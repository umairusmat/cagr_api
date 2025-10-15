"""
Enhanced CAGR API with Dynamic Ticker Management and Manual Scraping
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import json
import asyncio
from pydantic import BaseModel

from cagr_scraper_firefox import CAGRScraperFirefox, CAGRDatabase
from ticker_manager import ticker_manager
from scheduler_fixed import start_scheduler, stop_scheduler, trigger_manual_scrape

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return {
            "api": {"auth_token": "mysecretapitoken123"},
            "scraping": {"frequency_hours": 3, "enabled": True, "headless": True}
        }

config = load_config()
AUTH_TOKEN = config.get('api', {}).get('auth_token', 'mysecretapitoken123')

# Initialize database
db = CAGRDatabase()

# Pydantic models for API
class TickerRequest(BaseModel):
    ticker: str
    is_scheduled: bool = True
    group_name: str = "default"

class TickerListRequest(BaseModel):
    tickers: List[str]
    is_scheduled: bool = True
    group_name: str = "default"

class ManualScrapeRequest(BaseModel):
    tickers: List[str]
    wait_for_completion: bool = False

class TickerUpdateRequest(BaseModel):
    is_scheduled: bool

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Enhanced CAGR API application...")
    
    # Load initial tickers from CSV
    try:
        logger.info("Loading initial tickers from CSV...")
        ticker_manager.load_from_csv()
        scheduled_tickers = ticker_manager.get_scheduled_tickers()
        logger.info(f"Loaded {len(scheduled_tickers)} scheduled tickers: {scheduled_tickers}")
    except Exception as e:
        logger.error(f"Error loading initial tickers: {e}")
    
    # Run initial scrape for scheduled tickers
    try:
        logger.info("Running initial scrape for scheduled tickers...")
        scheduled_tickers = ticker_manager.get_scheduled_tickers()
        if scheduled_tickers:
            logger.info(f"Starting initial scrape for {len(scheduled_tickers)} scheduled tickers")
            
            scraper = CAGRScraperFirefox(headless=True)
            try:
                results = scraper.scrape_multiple(scheduled_tickers)
                successful = db.save_scraped_data(results)
                logger.info(f"Initial scrape completed: {successful} successful")
            finally:
                scraper.close()
        else:
            logger.warning("No scheduled tickers found for initial scrape")
    except Exception as e:
        logger.error(f"Error in initial scrape: {e}")
        logger.info("Continuing without initial scrape...")
    
    # Start background scheduler for scheduled tickers
    try:
        logger.info("Starting background scheduler for scheduled tickers...")
        await start_scheduler()
        logger.info("Background scheduler started successfully")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        logger.info("Continuing without background scheduler...")
    
    logger.info("Enhanced CAGR API ready to serve data")
    yield
    
    # Cleanup on shutdown
    try:
        logger.info("Stopping background scheduler...")
        await stop_scheduler()
        logger.info("Background scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
    
    logger.info("Enhanced CAGR API application stopped")

app = FastAPI(
    title="Enhanced CAGR Analyst Estimates API",
    description="API for CAGR data with dynamic ticker management and manual scraping",
    version="3.0.0",
    lifespan=lifespan
)

def verify_token(x_auth_token: str = Header(...)):
    """Verify authentication token"""
    if x_auth_token != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return x_auth_token

@app.get("/")
async def root():
    """API information and available endpoints"""
    return {
        "message": "Enhanced CAGR Analyst Estimates API",
        "version": "3.0.0",
        "description": "API for CAGR data with dynamic ticker management",
        "features": [
            "Scheduled scraping for predefined tickers",
            "Manual scraping for any tickers on-demand",
            "Dynamic ticker management (add/remove)",
            "SQLite-based ticker storage"
        ],
        "endpoints": {
            "health": "/health",
            "data": "/data",
            "data_by_ticker": "/data/{ticker}",
            "tickers": "/tickers",
            "ticker_management": "/tickers/manage",
            "manual_scrape": "/scrape/manual",
            "scheduled_tickers": "/tickers/scheduled"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        freshness = db.get_freshness_info()
        scheduled_tickers = ticker_manager.get_scheduled_tickers()
        
        return {
            "status": "healthy",
            "message": "Enhanced CAGR API is running",
            "version": "3.0.0",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "available": freshness['data_available'],
                "total_tickers": freshness['total_tickers'],
                "last_scrape": freshness['last_scrape']
            },
            "ticker_management": {
                "scheduled_tickers": len(scheduled_tickers),
                "total_tickers": len(ticker_manager.get_all_tickers())
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

# Data endpoints
@app.get("/data")
async def get_all_data(token: str = Depends(verify_token)):
    """Get all CAGR data"""
    try:
        data = db.get_all_data()
        return {
            "success": True,
            "data": data,
            "total_tickers": len(data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting all data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/{ticker}")
async def get_ticker_data(ticker: str, token: str = Depends(verify_token)):
    """Get data for specific ticker"""
    try:
        data = db.get_ticker_data(ticker.upper())
        if data:
            return {
                "success": True,
                "ticker": ticker.upper(),
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": f"No data found for ticker {ticker}",
                    "timestamp": datetime.now().isoformat()
                }
            )
    except Exception as e:
        logger.error(f"Error getting data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Ticker management endpoints
@app.get("/tickers")
async def get_all_tickers(token: str = Depends(verify_token)):
    """Get all tickers with their information"""
    try:
        ticker_info = ticker_manager.get_all_ticker_info()
        return {
            "success": True,
            "tickers": ticker_info,
            "total_count": len(ticker_info),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting tickers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickers/scheduled")
async def get_scheduled_tickers(token: str = Depends(verify_token)):
    """Get scheduled tickers"""
    try:
        scheduled_tickers = ticker_manager.get_scheduled_tickers()
        return {
            "success": True,
            "scheduled_tickers": scheduled_tickers,
            "count": len(scheduled_tickers),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting scheduled tickers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tickers/manage")
async def manage_ticker(request: TickerRequest, token: str = Depends(verify_token)):
    """Add or update a ticker"""
    try:
        success = ticker_manager.add_ticker(
            request.ticker, 
            request.is_scheduled, 
            request.group_name
        )
        
        if success:
            return {
                "success": True,
                "message": f"Ticker {request.ticker} added successfully",
                "ticker": request.ticker,
                "is_scheduled": request.is_scheduled,
                "group": request.group_name,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to add ticker {request.ticker}")
            
    except Exception as e:
        logger.error(f"Error managing ticker {request.ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tickers/manage/batch")
async def manage_tickers_batch(request: TickerListRequest, token: str = Depends(verify_token)):
    """Add multiple tickers"""
    try:
        results = []
        for ticker in request.tickers:
            success = ticker_manager.add_ticker(
                ticker, 
                request.is_scheduled, 
                request.group_name
            )
            results.append({
                "ticker": ticker,
                "success": success
            })
        
        successful_count = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "message": f"Processed {len(request.tickers)} tickers, {successful_count} successful",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error managing tickers batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tickers/manage/{ticker}")
async def remove_ticker(ticker: str, token: str = Depends(verify_token)):
    """Remove a ticker"""
    try:
        success = ticker_manager.remove_ticker(ticker.upper())
        
        if success:
            return {
                "success": True,
                "message": f"Ticker {ticker} removed successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to remove ticker {ticker}")
            
    except Exception as e:
        logger.error(f"Error removing ticker {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tickers/manage/{ticker}/schedule")
async def update_ticker_schedule(ticker: str, request: TickerUpdateRequest, token: str = Depends(verify_token)):
    """Update ticker schedule status"""
    try:
        success = ticker_manager.update_ticker_schedule(ticker.upper(), request.is_scheduled)
        
        if success:
            return {
                "success": True,
                "message": f"Ticker {ticker} schedule updated to {request.is_scheduled}",
                "ticker": ticker,
                "is_scheduled": request.is_scheduled,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to update ticker {ticker}")
            
    except Exception as e:
        logger.error(f"Error updating ticker {ticker} schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Manual scraping endpoint
@app.post("/scrape/manual")
async def manual_scrape(request: ManualScrapeRequest, token: str = Depends(verify_token)):
    """Trigger manual scrape for specific tickers"""
    try:
        logger.info(f"Manual scrape requested for tickers: {request.tickers}")
        
        # Initialize scraper
        scraper = CAGRScraperFirefox(headless=True)
        
        try:
            # Scrape the requested tickers
            results = scraper.scrape_multiple(request.tickers)
            
            # Save to database
            successful = db.save_scraped_data(results)
            
            if request.wait_for_completion:
                # Wait a bit for database operations to complete
                await asyncio.sleep(2)
            
            return {
                "success": True,
                "message": f"Manual scrape completed: {successful} successful",
                "requested_tickers": request.tickers,
                "successful_count": successful,
                "failed_count": len(request.tickers) - successful,
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            scraper.close()
            
    except Exception as e:
        logger.error(f"Error in manual scrape: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Get config
    config = load_config()
    api_config = config.get('api', {})
    
    host = api_config.get('host', '0.0.0.0')
    port = api_config.get('port', 8000)
    
    uvicorn.run(app, host=host, port=port)

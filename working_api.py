"""
Working FastAPI for CAGR Data with Firefox scraper
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import json

from cagr_scraper_firefox import CAGRScraperFirefox, CAGRDatabase, load_tickers
from scheduler_fixed import start_scheduler, stop_scheduler, trigger_manual_scrape

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, using defaults")
        return {
            "api": {
                "auth_token": "mysecretapitoken123",
                "host": "0.0.0.0",
                "port": 8000
            }
        }
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing config: {e}")
        return {"api": {"auth_token": "mysecretapitoken123"}}

config = load_config()
AUTH_TOKEN = config.get('api', {}).get('auth_token', 'mysecretapitoken123')

# Initialize database
db = CAGRDatabase()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting CAGR API application...")
    
    # Run initial scrape after deployment
    try:
        logger.info("Running initial scrape after deployment...")
        from cagr_scraper_firefox import CAGRScraperFirefox, load_tickers
        
        # Load tickers
        tickers = load_tickers()
        if tickers:
            logger.info(f"Starting initial scrape for {len(tickers)} tickers")
            
            # Initialize scraper
            scraper = CAGRScraperFirefox(headless=True)
            
            try:
                # Scrape data
                results = scraper.scrape_multiple(tickers)
                
                # Save to database
                successful = db.save_scraped_data(results)
                logger.info(f"Initial scrape completed: {successful} successful")
                
            finally:
                # Clean up scraper
                scraper.close()
        else:
            logger.warning("No tickers found for initial scrape")
            
    except Exception as e:
        logger.error(f"Error in initial scrape: {e}")
        logger.info("Continuing without initial scrape...")
    
    # Start background scheduler for automatic scraping
    try:
        logger.info("Starting background scheduler...")
        await start_scheduler()
        logger.info("Background scheduler started successfully")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        logger.info("Continuing without background scheduler...")
    
    logger.info("CAGR API ready to serve data")
    yield
    
    # Cleanup on shutdown
    try:
        logger.info("Stopping background scheduler...")
        await stop_scheduler()
        logger.info("Background scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
    
    logger.info("CAGR API application stopped")

app = FastAPI(
    title="CAGR Analyst Estimates API",
    description="API for serving CAGR analyst estimates data",
    version="2.0.0",
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
        "message": "CAGR Analyst Estimates API",
        "version": "2.0.0",
        "description": "API for CAGR data",
        "endpoints": {
            "health": "/health",
            "data": "/data",
            "data_by_ticker": "/data/{ticker}",
            "data_freshness": "/data/freshness",
            "data_statistics": "/data/statistics",
            "tickers": "/tickers",
            "scrape_manual": "/scrape/manual"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Get data freshness
        freshness = db.get_freshness_info()
        
        return {
            "status": "healthy",
            "message": "CAGR API is running",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "available": freshness['data_available'],
                "total_tickers": freshness['total_tickers'],
                "last_scrape": freshness['last_scrape']
            },
            "endpoints": {
                "health": "/health",
                "data": "/data",
                "data_by_ticker": "/data/{ticker}",
                "data_freshness": "/data/freshness",
                "data_statistics": "/data/statistics",
                "tickers": "/tickers",
                "scrape_manual": "/scrape/manual"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        # Return 200 even if database check fails, just indicate the issue
        return {
            "status": "healthy",
            "message": "CAGR API is running (database check failed)",
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "data": {
                "available": False,
                "total_tickers": 0,
                "last_scrape": None
            }
        }

@app.get("/data")
async def get_all_data(auth_token: str = Depends(verify_token)):
    """Get all CAGR data"""
    try:
        data = db.get_all_data()
        return {
            "success": True,
            "data": data,
            "count": len(data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting all data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/{ticker}")
async def get_ticker_data(ticker: str, auth_token: str = Depends(verify_token)):
    """Get CAGR data for specific ticker"""
    try:
        data = db.get_ticker_data(ticker.upper())
        if data is None:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        return {
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/freshness")
async def get_data_freshness(auth_token: str = Depends(verify_token)):
    """Get data freshness information"""
    try:
        freshness = db.get_freshness_info()
        return {
            "success": True,
            "freshness": freshness,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting data freshness: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/statistics")
async def get_data_statistics(auth_token: str = Depends(verify_token)):
    """Get data statistics"""
    try:
        all_data = db.get_all_data()
        freshness = db.get_freshness_info()
        
        # Calculate statistics
        total_tickers = len(all_data)
        tickers_with_data = len([d for d in all_data if d.get('data')])
        
        # Count years per ticker
        years_per_ticker = []
        for ticker_data in all_data:
            if ticker_data.get('data'):
                years_per_ticker.append(len(ticker_data['data']))
        
        avg_years = sum(years_per_ticker) / len(years_per_ticker) if years_per_ticker else 0
        
        return {
            "success": True,
            "statistics": {
                "total_tickers": total_tickers,
                "tickers_with_data": tickers_with_data,
                "tickers_without_data": total_tickers - tickers_with_data,
                "average_years_per_ticker": round(avg_years, 2),
                "data_availability_percentage": round((tickers_with_data / total_tickers * 100) if total_tickers > 0 else 0, 2),
                "last_scrape": freshness.get('last_scrape'),
                "first_scrape": freshness.get('first_scrape')
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting data statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickers")
async def get_tickers(auth_token: str = Depends(verify_token)):
    """Get list of available tickers"""
    try:
        all_data = db.get_all_data()
        tickers = [data['ticker'] for data in all_data]
        
        return {
            "success": True,
            "tickers": tickers,
            "count": len(tickers),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting tickers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape/manual")
async def run_manual_scrape(auth_token: str = Depends(verify_token)):
    """Trigger a manual scrape"""
    try:
        logger.info("Starting manual scrape...")
        
        # Use the scheduler for manual scrape
        await trigger_manual_scrape()
        
        return {
            "success": True,
            "message": "Manual scrape triggered successfully",
            "timestamp": datetime.now().isoformat()
        }
            
    except Exception as e:
        logger.error(f"Error in manual scrape: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Get config
    config = load_config()
    host = config.get('api', {}).get('host', '0.0.0.0')
    port = config.get('api', {}).get('port', 8000)
    
    logger.info(f"Starting CAGR API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)


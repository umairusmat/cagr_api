from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Optional
import logging

from models import load_config, test_connection
from data_service import DataService
from scheduler import scheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = load_config()
AUTH_TOKEN = config.get('api', {}).get('auth_token', 'mysecretapitoken123')

# Initialize data service
data_service = DataService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting CAGR API application...")
    
    # Test database connection
    if not test_connection():
        logger.error("Failed to connect to database")
        raise Exception("Database connection failed")
    
    # Start the scheduler
    scheduler.start_scheduler()
    logger.info("Scheduler started")
    
    yield
    
    # Cleanup
    logger.info("Shutting down CAGR API application...")
    scheduler.stop_scheduler()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="CAGR Analyst Estimates API",
    description="API for serving CAGR analyst estimates data scraped from StockUnlock",
    version="1.0.0",
    lifespan=lifespan
)

def verify_token(x_auth_token: str = Header(...)):
    """Verify API authentication token"""
    if x_auth_token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid auth token")
    return True

@app.get("/", dependencies=[Depends(verify_token)])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CAGR Analyst Estimates API",
        "version": "1.0.0",
        "endpoints": {
            "data": "/data",
            "ticker": "/data/{ticker}",
            "freshness": "/data/freshness",
            "statistics": "/data/statistics",
            "scrape": "/scrape/manual",
            "scheduler": "/scheduler/status",
            "sessions": "/sessions"
        }
    }

@app.get("/data", dependencies=[Depends(verify_token)])
async def get_all_data():
    """Get all CAGR data"""
    try:
        data = data_service.get_cagr_data_formatted()
        return JSONResponse(content=data)
    except Exception as e:
        logger.error(f"Error getting all data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/data/{ticker}", dependencies=[Depends(verify_token)])
async def get_ticker_data(ticker: str):
    """Get CAGR data for a specific ticker"""
    try:
        data = data_service.get_cagr_data_formatted(ticker.upper())
        if not data["data"]:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        return JSONResponse(content=data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/data/freshness", dependencies=[Depends(verify_token)])
async def get_data_freshness():
    """Get information about data freshness"""
    try:
        freshness = data_service.get_data_freshness()
        return JSONResponse(content=freshness)
    except Exception as e:
        logger.error(f"Error getting data freshness: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/data/statistics", dependencies=[Depends(verify_token)])
async def get_data_statistics():
    """Get statistics about stored data"""
    try:
        stats = data_service.get_data_statistics()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Error getting data statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/tickers", dependencies=[Depends(verify_token)])
async def get_tickers(search: Optional[str] = Query(None, description="Search for tickers")):
    """Get list of available tickers"""
    try:
        if search:
            tickers = data_service.search_tickers(search)
        else:
            tickers = data_service.get_ticker_list()
        return JSONResponse(content={"tickers": tickers})
    except Exception as e:
        logger.error(f"Error getting tickers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/scrape/manual", dependencies=[Depends(verify_token)])
async def trigger_manual_scrape():
    """Trigger a manual scraping session"""
    try:
        result = scheduler.run_manual_scrape()
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering manual scrape: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/scheduler/status", dependencies=[Depends(verify_token)])
async def get_scheduler_status():
    """Get scheduler status and configuration"""
    try:
        status = scheduler.get_scheduler_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/sessions", dependencies=[Depends(verify_token)])
async def get_recent_sessions(limit: int = Query(10, ge=1, le=50)):
    """Get recent scraping sessions"""
    try:
        sessions = scheduler.get_recent_sessions(limit)
        return JSONResponse(content={"sessions": sessions})
    except Exception as e:
        logger.error(f"Error getting recent sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health", dependencies=[Depends(verify_token)])
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_ok = test_connection()
        
        # Check scheduler status
        scheduler_status = scheduler.get_scheduler_status()
        
        # Check data freshness
        freshness = data_service.get_data_freshness()
        
        return JSONResponse(content={
            "status": "healthy" if db_ok else "unhealthy",
            "database": "connected" if db_ok else "disconnected",
            "scheduler": scheduler_status,
            "data": freshness
        })
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return JSONResponse(
            content={"status": "unhealthy", "error": str(e)},
            status_code=500
        )
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
import logging
import json
from datetime import datetime

from models import load_config, test_connection
from data_service import DataService

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
    
    logger.info("CAGR API ready to receive data from Streamlit")
    
    yield
    
    # Cleanup
    logger.info("Shutting down CAGR API application...")
    logger.info("Application shutdown complete")

app = FastAPI(
    title="CAGR Analyst Estimates API",
    description="API for serving CAGR analyst estimates data from Streamlit",
    version="1.0.0",
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
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "data": "/data",
            "data_by_ticker": "/data/{ticker}",
            "data_freshness": "/data/freshness",
            "data_statistics": "/data/statistics",
            "tickers": "/tickers",
            "upload_data": "/upload/data"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        if not test_connection():
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "message": "Database connection failed"}
            )
        
        return {
            "status": "healthy",
            "message": "CAGR API is running",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": str(e)}
        )

@app.get("/data")
async def get_all_data(auth_token: str = Depends(verify_token)):
    """Get all CAGR data"""
    try:
        data = data_service.get_all_data()
        return {"data": data}
    except Exception as e:
        logger.error(f"Error getting all data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/{ticker}")
async def get_ticker_data(ticker: str, auth_token: str = Depends(verify_token)):
    """Get CAGR data for specific ticker"""
    try:
        data = data_service.get_ticker_data(ticker.upper())
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        return {"data": {ticker.upper(): data}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/freshness")
async def get_data_freshness(auth_token: str = Depends(verify_token)):
    """Get data freshness information"""
    try:
        freshness = data_service.get_data_freshness()
        return freshness
    except Exception as e:
        logger.error(f"Error getting data freshness: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/statistics")
async def get_data_statistics(auth_token: str = Depends(verify_token)):
    """Get data statistics"""
    try:
        stats = data_service.get_data_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting data statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickers")
async def get_tickers(auth_token: str = Depends(verify_token)):
    """Get list of available tickers"""
    try:
        tickers = data_service.get_available_tickers()
        return {"tickers": tickers}
    except Exception as e:
        logger.error(f"Error getting tickers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/data")
async def upload_data(data: Dict[str, Any], auth_token: str = Depends(verify_token)):
    """Upload data from Streamlit app"""
    try:
        logger.info(f"Received data upload from Streamlit: {len(data.get('data', {}))} tickers")
        
        # Store the data
        result = data_service.store_data_from_streamlit(data)
        
        return {
            "message": "Data uploaded successfully",
            "tickers_processed": result.get("tickers_processed", 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error uploading data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

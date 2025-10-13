from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
import logging
import json
import requests
from datetime import datetime

from models import load_config, test_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = load_config()
AUTH_TOKEN = config.get('api', {}).get('auth_token', 'mysecretapitoken123')

# Streamlit data server URL (this should be your Streamlit Cloud URL)
STREAMLIT_DATA_SERVER_URL = "https://your-streamlit-app.streamlit.app"  # Update this with your actual Streamlit URL

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting CAGR API application...")
    
    # Test database connection (optional for this architecture)
    # if not test_connection():
    #     logger.error("Failed to connect to database")
    #     raise Exception("Database connection failed")
    
    logger.info("CAGR API ready to fetch data from Streamlit")
    
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

def fetch_from_streamlit(endpoint: str) -> Dict[str, Any]:
    """Fetch data from Streamlit data server"""
    try:
        url = f"{STREAMLIT_DATA_SERVER_URL}{endpoint}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Streamlit server returned {response.status_code}: {response.text}")
            raise HTTPException(status_code=503, detail="Streamlit data server unavailable")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching from Streamlit: {e}")
        raise HTTPException(status_code=503, detail="Cannot connect to Streamlit data server")
    except Exception as e:
        logger.error(f"Unexpected error fetching from Streamlit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """API information and available endpoints"""
    return {
        "message": "CAGR Analyst Estimates API",
        "version": "1.0.0",
        "description": "Fetches data from Streamlit data server",
        "streamlit_server": STREAMLIT_DATA_SERVER_URL,
        "endpoints": {
            "health": "/health",
            "data": "/data",
            "data_by_ticker": "/data/{ticker}",
            "data_freshness": "/data/freshness",
            "data_statistics": "/data/statistics",
            "tickers": "/tickers"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test connection to Streamlit data server
        response = requests.get(f"{STREAMLIT_DATA_SERVER_URL}/health", timeout=5)
        
        if response.status_code == 200:
            streamlit_health = response.json()
            return {
                "status": "healthy",
                "message": "CAGR API is running",
                "version": "1.0.0",
                "streamlit_server": {
                    "status": streamlit_health.get("status", "unknown"),
                    "data_available": streamlit_health.get("data_available", False),
                    "scraping_in_progress": streamlit_health.get("scraping_in_progress", False)
                }
            }
        else:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "message": "Streamlit data server unavailable"}
            )
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": str(e)}
        )

@app.get("/data")
async def get_all_data(auth_token: str = Depends(verify_token)):
    """Get all CAGR data from Streamlit"""
    try:
        data = fetch_from_streamlit("/data")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/{ticker}")
async def get_ticker_data(ticker: str, auth_token: str = Depends(verify_token)):
    """Get CAGR data for specific ticker from Streamlit"""
    try:
        data = fetch_from_streamlit(f"/data/{ticker}")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/freshness")
async def get_data_freshness(auth_token: str = Depends(verify_token)):
    """Get data freshness information from Streamlit"""
    try:
        freshness = fetch_from_streamlit("/data/freshness")
        return freshness
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data freshness: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/statistics")
async def get_data_statistics(auth_token: str = Depends(verify_token)):
    """Get data statistics from Streamlit"""
    try:
        stats = fetch_from_streamlit("/data/statistics")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickers")
async def get_tickers(auth_token: str = Depends(verify_token)):
    """Get list of available tickers from Streamlit"""
    try:
        tickers_data = fetch_from_streamlit("/tickers")
        return tickers_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tickers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
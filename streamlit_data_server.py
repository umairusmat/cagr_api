import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import time
import threading
from analyst_cagr import CAGRScraper
import os
from fastapi import FastAPI, HTTPException
import uvicorn
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global data storage
scraped_data = {}
scraping_in_progress = False
last_scrape_time = None

# FastAPI app for serving data
app = FastAPI(title="Streamlit Data Server", version="1.0.0")

@app.get("/data")
async def get_all_data():
    """Get all scraped data"""
    try:
        return {"data": scraped_data}
    except Exception as e:
        logger.error(f"Error getting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/{ticker}")
async def get_ticker_data(ticker: str):
    """Get data for specific ticker"""
    try:
        ticker_data = scraped_data.get(ticker.upper(), {})
        if not ticker_data:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        return {"data": {ticker.upper(): ticker_data}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/freshness")
async def get_data_freshness():
    """Get data freshness information"""
    try:
        if not scraped_data:
            return {
                "ticker_count": 0,
                "hours_since_update": 0,
                "is_fresh": False,
                "latest_update": None
            }
        
        hours_since_update = 0
        if last_scrape_time:
            hours_since_update = (datetime.now() - last_scrape_time).total_seconds() / 3600
        
        return {
            "ticker_count": len(scraped_data),
            "hours_since_update": hours_since_update,
            "is_fresh": hours_since_update < 6,  # Consider fresh if less than 6 hours old
            "latest_update": last_scrape_time.isoformat() if last_scrape_time else None
        }
    except Exception as e:
        logger.error(f"Error getting data freshness: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/statistics")
async def get_data_statistics():
    """Get data statistics"""
    try:
        if not scraped_data:
            return {
                "total_records": 0,
                "unique_tickers": 0,
                "unique_years": 0,
                "latest_update": None
            }
        
        total_records = sum(len(ticker_data.get("values", {})) for ticker_data in scraped_data.values())
        unique_tickers = len(scraped_data)
        
        # Get all years
        all_years = set()
        for ticker_data in scraped_data.values():
            all_years.update(ticker_data.get("values", {}).keys())
        
        return {
            "total_records": total_records,
            "unique_tickers": unique_tickers,
            "unique_years": len(all_years),
            "latest_update": last_scrape_time.isoformat() if last_scrape_time else None
        }
    except Exception as e:
        logger.error(f"Error getting data statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickers")
async def get_tickers():
    """Get list of available tickers"""
    try:
        tickers = list(scraped_data.keys())
        return {"tickers": tickers}
    except Exception as e:
        logger.error(f"Error getting tickers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Streamlit Data Server is running",
        "version": "1.0.0",
        "scraping_in_progress": scraping_in_progress,
        "data_available": len(scraped_data) > 0
    }

def scrape_data_periodically(tickers, frequency_hours=6):
    """Scrape data periodically in background"""
    global scraped_data, scraping_in_progress, last_scrape_time
    
    while True:
        try:
            logger.info(f"Starting periodic scrape for {len(tickers)} tickers")
            scraping_in_progress = True
            
            scraper = CAGRScraper()
            results = {}
            
            for ticker in tickers:
                try:
                    logger.info(f"Scraping {ticker}")
                    data = scraper.scrape_ticker_data(ticker)
                    if data:
                        results[ticker] = {
                            "values": data,
                            "last_updated": datetime.now().isoformat()
                        }
                        logger.info(f"Successfully scraped {ticker}")
                    else:
                        logger.warning(f"No data found for {ticker}")
                        
                except Exception as e:
                    logger.error(f"Error scraping {ticker}: {e}")
                    continue
            
            # Update global data
            scraped_data = results
            last_scrape_time = datetime.now()
            scraping_in_progress = False
            
            logger.info(f"Periodic scrape completed. Scraped {len(results)} tickers")
            
            # Wait for next scrape
            time.sleep(frequency_hours * 3600)  # Convert hours to seconds
            
        except Exception as e:
            logger.error(f"Error in periodic scraping: {e}")
            scraping_in_progress = False
            time.sleep(60)  # Wait 1 minute before retrying

# Streamlit UI
st.set_page_config(
    page_title="CAGR Scraper & Data Server",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CAGR Analyst Estimates Scraper & Data Server")

# Configuration
API_BASE_URL = st.secrets.get("api", {}).get("API_BASE_URL", "http://localhost:8000")
AUTH_TOKEN = st.secrets.get("api", {}).get("AUTH_TOKEN", "mysecretapitoken123")

# Initialize session state
if 'scraping_started' not in st.session_state:
    st.session_state.scraping_started = False

# Sidebar
st.sidebar.title("🔧 Scraper Controls")

# Ticker input
tickers_input = st.sidebar.text_area(
    "Enter tickers (one per line):",
    value="AAPL\nMSFT\nGOOGL\nTSLA\nNVDA",
    height=100
)

# Scraping frequency
frequency_hours = st.sidebar.slider("Scraping Frequency (hours)", 1, 24, 6)

# Start/Stop Scraping
col1, col2 = st.sidebar.columns(2)

if col1.button("🚀 Start Scraping", disabled=st.session_state.scraping_started):
    tickers = [ticker.strip().upper() for ticker in tickers_input.split('\n') if ticker.strip()]
    
    if tickers:
        st.session_state.scraping_started = True
        st.sidebar.success(f"Started scraping for {len(tickers)} tickers")
        
        # Start background scraping thread
        thread = threading.Thread(
            target=scrape_data_periodically,
            args=(tickers, frequency_hours),
            daemon=True
        )
        thread.start()
    else:
        st.sidebar.error("Please enter at least one ticker")

if col2.button("⏹️ Stop Scraping", disabled=not st.session_state.scraping_started):
    st.session_state.scraping_started = False
    st.sidebar.info("Scraping stopped")

# Status Display
st.sidebar.markdown("---")
st.sidebar.markdown("**Status**")
if scraping_in_progress:
    st.sidebar.warning("🔄 Scraping in progress...")
else:
    st.sidebar.success("✅ Ready")

if last_scrape_time:
    st.sidebar.info(f"Last scrape: {last_scrape_time.strftime('%H:%M:%S')}")

# Data Server Info
st.sidebar.markdown("---")
st.sidebar.markdown("**Data Server**")
st.sidebar.info("Data is served locally at: http://localhost:8501")
st.sidebar.info("Railway API fetches from this server")

# Main Content
col1, col2 = st.columns(2)

with col1:
    st.header("📈 Local Data Overview")
    
    if scraped_data:
        col1_1, col1_2, col1_3 = st.columns(3)
        with col1_1:
            st.metric("Ticker Count", len(scraped_data))
        with col1_2:
            hours_since = 0
            if last_scrape_time:
                hours_since = (datetime.now() - last_scrape_time).total_seconds() / 3600
            st.metric("Hours Since Update", f"{hours_since:.1f}")
        with col1_3:
            st.metric("Data Fresh", "✅" if hours_since < 6 else "❌")
            
        if last_scrape_time:
            st.info(f"Last updated: {last_scrape_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("No data available - start scraping to populate data")

with col2:
    st.header("📊 Data Statistics")
    
    if scraped_data:
        total_records = sum(len(ticker_data.get("values", {})) for ticker_data in scraped_data.values())
        all_years = set()
        for ticker_data in scraped_data.values():
            all_years.update(ticker_data.get("values", {}).keys())
        
        col2_1, col2_2, col2_3 = st.columns(3)
        with col2_1:
            st.metric("Total Records", total_records)
        with col2_2:
            st.metric("Unique Tickers", len(scraped_data))
        with col2_3:
            st.metric("Unique Years", len(all_years))
    else:
        st.info("No statistics available")

# Available Tickers
st.header("🏷️ Available Tickers")
if scraped_data:
    st.write(f"Found {len(scraped_data)} tickers:")
    
    # Display tickers in columns
    cols = st.columns(5)
    for i, ticker in enumerate(scraped_data.keys()):
        with cols[i % 5]:
            st.text(ticker)
else:
    st.info("No tickers found - start scraping to populate data")

# Sample Data Display
st.header("📊 Sample Data")
if scraped_data:
    ticker_to_display = st.selectbox("Select a ticker to view data:", ["Select a ticker..."] + list(scraped_data.keys()))
    
    if ticker_to_display and ticker_to_display != "Select a ticker...":
        ticker_data = scraped_data.get(ticker_to_display, {})
        
        if ticker_data:
            st.subheader(f"Data for {ticker_to_display}")
            
            # Display values in a nice format
            values = ticker_data.get("values", {})
            if values:
                df_values = pd.DataFrame(list(values.items()), columns=['Year', 'CAGR'])
                st.dataframe(df_values, use_container_width=True)
                
                st.info(f"Last updated: {ticker_data.get('last_updated', 'Unknown')}")
            else:
                st.warning("No data available for this ticker")
        else:
            st.warning("No data found for this ticker")
else:
    st.info("No data available - start scraping to populate data")

# Footer
st.markdown("---")
st.markdown("**CAGR Analyst Estimates Scraper & Data Server** - Built with Streamlit")
st.markdown("**Data Server**: http://localhost:8501")

# Auto-refresh
if scraping_in_progress:
    time.sleep(2)
    st.rerun()

if __name__ == "__main__":
    # Start FastAPI server in background
    import threading
    
    def run_fastapi():
        uvicorn.run(app, host="0.0.0.0", port=8501, log_level="info")
    
    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Run Streamlit
    st.run()

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import time
import threading
import os
import sys

# Add the current directory to Python path to import analyst_cagr
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import the scraper, but handle gracefully if it fails
try:
    from analyst_cagr import CAGRScraper
    SCRAPER_AVAILABLE = True
except ImportError as e:
    st.error(f"Scraper not available: {e}")
    SCRAPER_AVAILABLE = False

st.set_page_config(
    page_title="CAGR Scraper & Data Server",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CAGR Analyst Estimates Scraper & Data Server")

# Global data storage
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = {}
if 'scraping_in_progress' not in st.session_state:
    st.session_state.scraping_in_progress = False
if 'last_scrape_time' not in st.session_state:
    st.session_state.last_scrape_time = None

# Configuration
API_BASE_URL = st.secrets.get("api", {}).get("API_BASE_URL", "http://localhost:8000")
AUTH_TOKEN = st.secrets.get("api", {}).get("AUTH_TOKEN", "mysecretapitoken123")

# Sidebar
st.sidebar.title("🔧 Scraper Controls")

# Check if scraper is available
if not SCRAPER_AVAILABLE:
    st.sidebar.error("⚠️ Scraper not available - check dependencies")
    st.sidebar.info("This app will work in monitoring mode only")

# Ticker input
tickers_input = st.sidebar.text_area(
    "Enter tickers (one per line):",
    value="AAPL\nMSFT\nGOOGL\nTSLA\nNVDA",
    height=100
)

# Scraping frequency
frequency_hours = st.sidebar.slider("Scraping Frequency (hours)", 1, 24, 6)

# Manual Scrape Button
if st.sidebar.button("🔄 Start Manual Scrape", disabled=st.session_state.scraping_in_progress or not SCRAPER_AVAILABLE):
    if not st.session_state.scraping_in_progress and SCRAPER_AVAILABLE:
        st.session_state.scraping_in_progress = True
        st.session_state.last_scrape_time = datetime.now()
        
        # Parse tickers
        tickers = [ticker.strip().upper() for ticker in tickers_input.split('\n') if ticker.strip()]
        
        if tickers:
            st.sidebar.success(f"Starting scrape for {len(tickers)} tickers...")
            
            # Run scraping in background
            def scrape_data():
                try:
                    scraper = CAGRScraper()
                    results = {}
                    
                    for i, ticker in enumerate(tickers):
                        try:
                            st.sidebar.info(f"Scraping {ticker} ({i+1}/{len(tickers)})")
                            
                            # Scrape data for this ticker
                            data = scraper.scrape_ticker_data(ticker)
                            if data:
                                results[ticker] = {
                                    "values": data,
                                    "last_updated": datetime.now().isoformat()
                                }
                                st.sidebar.success(f"✅ {ticker} scraped successfully")
                            else:
                                st.sidebar.warning(f"⚠️ No data found for {ticker}")
                                
                        except Exception as e:
                            st.sidebar.error(f"❌ Error scraping {ticker}: {e}")
                            continue
                    
                    # Store results in session state
                    st.session_state.scraped_data = results
                    st.session_state.scraping_in_progress = False
                    
                    # Upload to Railway API
                    if results:
                        try:
                            upload_data = {"data": results}
                            response = requests.post(
                                f"{API_BASE_URL}/upload/data",
                                headers={"X-Auth-Token": AUTH_TOKEN},
                                json=upload_data,
                                timeout=30
                            )
                            
                            if response.status_code == 200:
                                st.sidebar.success("✅ Data uploaded to Railway API")
                            else:
                                st.sidebar.error(f"❌ Failed to upload data: {response.text}")
                                
                        except Exception as e:
                            st.sidebar.error(f"❌ Error uploading data: {e}")
                    
                except Exception as e:
                    st.sidebar.error(f"❌ Scraping failed: {e}")
                    st.session_state.scraping_in_progress = False
            
            # Start scraping thread
            thread = threading.Thread(target=scrape_data)
            thread.daemon = True
            thread.start()
        else:
            st.sidebar.error("Please enter at least one ticker")
            st.session_state.scraping_in_progress = False

# Stop Scraping Button
if st.sidebar.button("⏹️ Stop Scraping", disabled=not st.session_state.scraping_in_progress):
    st.session_state.scraping_in_progress = False
    st.sidebar.info("Scraping stopped")

# Status Display
st.sidebar.markdown("---")
st.sidebar.markdown("**Status**")
if st.session_state.scraping_in_progress:
    st.sidebar.warning("🔄 Scraping in progress...")
else:
    st.sidebar.success("✅ Ready")

if st.session_state.last_scrape_time:
    st.sidebar.info(f"Last scrape: {st.session_state.last_scrape_time.strftime('%H:%M:%S')}")

# Configuration Display
st.sidebar.markdown("---")
st.sidebar.markdown("**Configuration**")
st.sidebar.text(f"API URL: {API_BASE_URL}")
st.sidebar.text(f"Auth Token: {AUTH_TOKEN[:10]}...")

# Main Content
col1, col2 = st.columns(2)

with col1:
    st.header("📈 Data Overview")
    
    # Get data freshness from Railway API
    try:
        response = requests.get(f"{API_BASE_URL}/data/freshness", headers={"X-Auth-Token": AUTH_TOKEN}, timeout=10)
        if response.status_code == 200:
            freshness = response.json()
            
            col1_1, col1_2, col1_3 = st.columns(3)
            with col1_1:
                st.metric("Ticker Count", freshness.get("ticker_count", 0))
            with col1_2:
                st.metric("Hours Since Update", f"{freshness.get('hours_since_update', 0):.1f}")
            with col1_3:
                st.metric("Data Fresh", "✅" if freshness.get("is_fresh") else "❌")
                
            if freshness.get("latest_update"):
                st.info(f"Last updated: {freshness['latest_update']}")
        else:
            st.error("Failed to get data freshness")
    except Exception as e:
        st.error(f"Error: {e}")

with col2:
    st.header("📊 Data Statistics")
    try:
        response = requests.get(f"{API_BASE_URL}/data/statistics", headers={"X-Auth-Token": AUTH_TOKEN}, timeout=10)
        if response.status_code == 200:
            stats = response.json()
            
            col2_1, col2_2, col2_3, col2_4 = st.columns(4)
            with col2_1:
                st.metric("Total Records", stats.get("total_records", 0))
            with col2_2:
                st.metric("Unique Tickers", stats.get("unique_tickers", 0))
            with col2_3:
                st.metric("Unique Years", stats.get("unique_years", 0))
            with col2_4:
                if stats.get("latest_update"):
                    st.metric("Latest Update", stats["latest_update"][:10])
        else:
            st.error("Failed to get data statistics")
    except Exception as e:
        st.error(f"Error: {e}")

# Available Tickers
st.header("🏷️ Available Tickers")
try:
    response = requests.get(f"{API_BASE_URL}/tickers", headers={"X-Auth-Token": AUTH_TOKEN}, timeout=10)
    if response.status_code == 200:
        tickers_data = response.json()
        tickers = tickers_data.get("tickers", [])
        
        if tickers:
            st.write(f"Found {len(tickers)} tickers:")
            
            # Display tickers in columns
            cols = st.columns(5)
            for i, ticker in enumerate(tickers):
                with cols[i % 5]:
                    st.text(ticker)
        else:
            st.info("No tickers found - run a scrape to populate data")
    else:
        st.error("Failed to get tickers")
except Exception as e:
    st.error(f"Error: {e}")

# Sample Data Display
st.header("📊 Sample Data")
ticker_to_display = st.selectbox("Select a ticker to view data:", ["Select a ticker..."] + tickers if 'tickers' in locals() else ["Select a ticker..."])

if ticker_to_display and ticker_to_display != "Select a ticker...":
    try:
        response = requests.get(f"{API_BASE_URL}/data/{ticker_to_display}", headers={"X-Auth-Token": AUTH_TOKEN}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            ticker_data = data.get("data", {}).get(ticker_to_display, {})
            
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
            st.error(f"Failed to get data for {ticker_to_display}")
    except Exception as e:
        st.error(f"Error: {e}")

# Auto-refresh
if st.session_state.scraping_in_progress:
    time.sleep(2)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("**CAGR Analyst Estimates Scraper & Monitor** - Built with Streamlit")
st.markdown("**Railway API**: " + API_BASE_URL)

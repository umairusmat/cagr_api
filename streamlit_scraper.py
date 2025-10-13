import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import time
import threading
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the scraper
try:
    from analyst_cagr import CAGRScraper
    SCRAPER_AVAILABLE = True
except ImportError as e:
    st.error(f"❌ Scraper not available: {e}")
    SCRAPER_AVAILABLE = False

st.set_page_config(
    page_title="CAGR Data Scraper",
    page_icon="🕷️",
    layout="wide"
)

st.title("🕷️ CAGR Data Scraper - StockUnlock.com")

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
st.sidebar.title("🕷️ Scraper Controls")

# Check if scraper is available
if not SCRAPER_AVAILABLE:
    st.sidebar.error("⚠️ Scraper dependencies not available")
    st.sidebar.info("This app needs Selenium, Firefox-ESR, and WebDriver Manager")
    st.sidebar.info("Check your requirements.txt and packages.txt")
else:
    st.sidebar.success("✅ Scraper ready with Selenium + Firefox-ESR")

# Ticker input
st.sidebar.markdown("### 📝 Ticker Configuration")
tickers_input = st.sidebar.text_area(
    "Enter tickers to scrape (one per line):",
    value="AAPL\nMSFT\nGOOGL\nTSLA\nNVDA\nAMZN\nMETA\nNFLX",
    height=150,
    help="Enter stock tickers you want to scrape CAGR data for"
)

# Scraping frequency
st.sidebar.markdown("### ⏰ Scraping Schedule")
frequency_hours = st.sidebar.slider(
    "Auto-scrape every (hours):", 
    1, 24, 6,
    help="How often to automatically scrape data"
)

# Manual Scrape Button
st.sidebar.markdown("### 🚀 Manual Scraping")
if st.sidebar.button("🕷️ Start Scraping Now", disabled=st.session_state.scraping_in_progress or not SCRAPER_AVAILABLE):
    if not st.session_state.scraping_in_progress and SCRAPER_AVAILABLE:
        st.session_state.scraping_in_progress = True
        st.session_state.last_scrape_time = datetime.now()
        
        # Parse tickers
        tickers = [ticker.strip().upper() for ticker in tickers_input.split('\n') if ticker.strip()]
        
        if tickers:
            st.sidebar.success(f"🕷️ Starting scrape for {len(tickers)} tickers...")
            
            # Run scraping in background
            def scrape_data():
                try:
                    scraper = CAGRScraper()
                    results = {}
                    
                    progress_bar = st.sidebar.progress(0)
                    status_text = st.sidebar.empty()
                    
                    for i, ticker in enumerate(tickers):
                        try:
                            status_text.text(f"🕷️ Scraping {ticker} ({i+1}/{len(tickers)})")
                            
                            # Scrape data for this ticker using Selenium + Firefox-ESR
                            data = scraper.scrape_ticker_data(ticker)
                            if data:
                                results[ticker] = {
                                    "values": data,
                                    "last_updated": datetime.now().isoformat()
                                }
                                st.sidebar.success(f"✅ {ticker}: {len(data)} years scraped")
                            else:
                                st.sidebar.warning(f"⚠️ {ticker}: No data found")
                                
                        except Exception as e:
                            st.sidebar.error(f"❌ {ticker}: {str(e)[:50]}...")
                            continue
                        
                        # Update progress
                        progress_bar.progress((i + 1) / len(tickers))
                    
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
                                st.sidebar.error(f"❌ Upload failed: {response.text}")
                                
                        except Exception as e:
                            st.sidebar.error(f"❌ Upload error: {e}")
                    
                    # Clear progress
                    progress_bar.empty()
                    status_text.empty()
                    
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
st.sidebar.markdown("### 📊 Status")
if st.session_state.scraping_in_progress:
    st.sidebar.warning("🔄 Scraping in progress...")
else:
    st.sidebar.success("✅ Ready to scrape")

if st.session_state.last_scrape_time:
    st.sidebar.info(f"Last scrape: {st.session_state.last_scrape_time.strftime('%H:%M:%S')}")

# Configuration Display
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Configuration")
st.sidebar.text(f"API URL: {API_BASE_URL}")
st.sidebar.text(f"Auth Token: {AUTH_TOKEN[:10]}...")

# Main Content
col1, col2 = st.columns(2)

with col1:
    st.header("🕷️ Scraping Status")
    
    if st.session_state.scraped_data:
        col1_1, col1_2, col1_3 = st.columns(3)
        with col1_1:
            st.metric("Tickers Scraped", len(st.session_state.scraped_data))
        with col1_2:
            hours_since = 0
            if st.session_state.last_scrape_time:
                hours_since = (datetime.now() - st.session_state.last_scrape_time).total_seconds() / 3600
            st.metric("Hours Since Scrape", f"{hours_since:.1f}")
        with col1_3:
            st.metric("Data Fresh", "✅" if hours_since < 6 else "❌")
            
        if st.session_state.last_scrape_time:
            st.info(f"Last scraped: {st.session_state.last_scrape_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("No data scraped yet - click 'Start Scraping Now' to begin")

with col2:
    st.header("📊 Scraped Data Statistics")
    
    if st.session_state.scraped_data:
        total_records = sum(len(ticker_data.get("values", {})) for ticker_data in st.session_state.scraped_data.values())
        all_years = set()
        for ticker_data in st.session_state.scraped_data.values():
            all_years.update(ticker_data.get("values", {}).keys())
        
        col2_1, col2_2, col2_3 = st.columns(3)
        with col2_1:
            st.metric("Total Records", total_records)
        with col2_2:
            st.metric("Unique Tickers", len(st.session_state.scraped_data))
        with col2_3:
            st.metric("Unique Years", len(all_years))
    else:
        st.info("No statistics available")

# Scraped Data Display
st.header("🕷️ Scraped Data from StockUnlock.com")
if st.session_state.scraped_data:
    ticker_to_display = st.selectbox("Select a ticker to view scraped data:", ["Select a ticker..."] + list(st.session_state.scraped_data.keys()))
    
    if ticker_to_display and ticker_to_display != "Select a ticker...":
        ticker_data = st.session_state.scraped_data.get(ticker_to_display, {})
        
        if ticker_data:
            st.subheader(f"🕷️ Scraped Data for {ticker_to_display}")
            
            # Display values in a nice format
            values = ticker_data.get("values", {})
            if values:
                df_values = pd.DataFrame(list(values.items()), columns=['Year', 'CAGR'])
                st.dataframe(df_values, use_container_width=True)
                
                st.info(f"🕷️ Scraped from StockUnlock.com at: {ticker_data.get('last_updated', 'Unknown')}")
            else:
                st.warning("No data available for this ticker")
        else:
            st.warning("No data found for this ticker")
else:
    st.info("No data scraped yet - start scraping to see data from StockUnlock.com")

# Auto-refresh during scraping
if st.session_state.scraping_in_progress:
    time.sleep(2)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("**🕷️ CAGR Data Scraper** - Scrapes from StockUnlock.com using Selenium + Firefox-ESR")
st.markdown("**Railway API**: " + API_BASE_URL)

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="CAGR API Monitor",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CAGR Analyst Estimates API Monitor")

# Configuration
API_BASE_URL = st.secrets.get("api", {}).get("API_BASE_URL", "http://localhost:8000")
AUTH_TOKEN = st.secrets.get("api", {}).get("AUTH_TOKEN", "mysecretapitoken123")

headers = {"X-Auth-Token": AUTH_TOKEN}

# Sidebar
st.sidebar.title("🔧 API Controls")

# Health Check
if st.sidebar.button("🏥 Check Health"):
    try:
        response = requests.get(f"{API_BASE_URL}/health", headers=headers, timeout=10)
        if response.status_code == 200:
            st.sidebar.success("✅ API is healthy")
            health_data = response.json()
            st.sidebar.json(health_data)
        else:
            st.sidebar.error("❌ API is unhealthy")
    except Exception as e:
        st.sidebar.error(f"❌ Connection failed: {e}")

# Manual Scrape
if st.sidebar.button("🔄 Trigger Manual Scrape"):
    try:
        with st.spinner("Triggering scrape..."):
            response = requests.post(f"{API_BASE_URL}/scrape/manual", headers=headers, timeout=30)
        if response.status_code == 200:
            st.sidebar.success("✅ Scrape triggered")
            result = response.json()
            st.sidebar.json(result)
        else:
            st.sidebar.error("❌ Scrape failed")
    except Exception as e:
        st.sidebar.error(f"❌ Error: {e}")

# Configuration Display
st.sidebar.markdown("---")
st.sidebar.markdown("**Configuration**")
st.sidebar.text(f"API URL: {API_BASE_URL}")
st.sidebar.text(f"Auth Token: {AUTH_TOKEN[:10]}...")

# Main Content
col1, col2 = st.columns(2)

with col1:
    st.header("📈 Data Overview")
    
    # Get data freshness
    try:
        response = requests.get(f"{API_BASE_URL}/data/freshness", headers=headers, timeout=10)
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
    st.header("⚙️ Scheduler Status")
    
    # Get scheduler status
    try:
        response = requests.get(f"{API_BASE_URL}/scheduler/status", headers=headers, timeout=10)
        if response.status_code == 200:
            status = response.json()
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric("Scheduler Running", "✅" if status.get("is_running") else "❌")
            with col2_2:
                st.metric("Frequency (hours)", status.get("frequency_hours", 0))
                
            if status.get("next_run"):
                st.info(f"Next run: {status['next_run']}")
        else:
            st.error("Failed to get scheduler status")
    except Exception as e:
        st.error(f"Error: {e}")

# Data Statistics
st.header("📊 Data Statistics")
try:
    response = requests.get(f"{API_BASE_URL}/data/statistics", headers=headers, timeout=10)
    if response.status_code == 200:
        stats = response.json()
        
        col3_1, col3_2, col3_3, col3_4 = st.columns(4)
        with col3_1:
            st.metric("Total Records", stats.get("total_records", 0))
        with col3_2:
            st.metric("Unique Tickers", stats.get("unique_tickers", 0))
        with col3_3:
            st.metric("Unique Years", stats.get("unique_years", 0))
        with col3_4:
            if stats.get("latest_update"):
                st.metric("Latest Update", stats["latest_update"][:10])
    else:
        st.error("Failed to get data statistics")
except Exception as e:
    st.error(f"Error: {e}")

# Recent Sessions
st.header("📋 Recent Scraping Sessions")
try:
    response = requests.get(f"{API_BASE_URL}/sessions?limit=5", headers=headers, timeout=10)
    if response.status_code == 200:
        sessions_data = response.json()
        sessions = sessions_data.get("sessions", [])
        
        if sessions:
            # Create DataFrame for better display
            df = pd.DataFrame(sessions)
            df['started_at'] = pd.to_datetime(df['started_at']).dt.strftime('%Y-%m-%d %H:%M')
            df['completed_at'] = pd.to_datetime(df['completed_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            st.dataframe(
                df[['id', 'type', 'status', 'total_tickers', 'successful_tickers', 'failed_tickers', 'started_at']],
                use_container_width=True
            )
        else:
            st.info("No recent sessions found")
    else:
        st.error("Failed to get sessions")
except Exception as e:
    st.error(f"Error: {e}")

# Available Tickers
st.header("🏷️ Available Tickers")
try:
    response = requests.get(f"{API_BASE_URL}/tickers", headers=headers, timeout=10)
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
            st.info("No tickers found")
    else:
        st.error("Failed to get tickers")
except Exception as e:
    st.error(f"Error: {e}")

# Sample Data Display
st.header("📊 Sample Data")
ticker_to_display = st.selectbox("Select a ticker to view data:", ["Select a ticker..."] + tickers if 'tickers' in locals() else ["Select a ticker..."])

if ticker_to_display and ticker_to_display != "Select a ticker...":
    try:
        response = requests.get(f"{API_BASE_URL}/data/{ticker_to_display}", headers=headers, timeout=10)
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

# Footer
st.markdown("---")
st.markdown("**CAGR Analyst Estimates API Monitor** - Built with Streamlit")
st.markdown("For more information, see the [README.md](README.md) file.")
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

# Configuration Display
st.sidebar.markdown("---")
st.sidebar.markdown("**Configuration**")
st.sidebar.text(f"API URL: {API_BASE_URL}")
st.sidebar.text(f"Auth Token: {AUTH_TOKEN[:10]}...")

# Main Content
st.header("📈 API Status")

# Simple API test
try:
    response = requests.get(f"{API_BASE_URL}/health", headers=headers, timeout=10)
    if response.status_code == 200:
        st.success("✅ API is running and healthy")
        health_data = response.json()
        st.json(health_data)
    else:
        st.error(f"❌ API returned status code: {response.status_code}")
except Exception as e:
    st.error(f"❌ Cannot connect to API: {e}")
    st.info("Make sure your Railway API is deployed and running")

# Data Statistics
st.header("📊 Data Statistics")
try:
    response = requests.get(f"{API_BASE_URL}/data/statistics", headers=headers, timeout=10)
    if response.status_code == 200:
        stats = response.json()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", stats.get("total_records", 0))
        with col2:
            st.metric("Unique Tickers", stats.get("unique_tickers", 0))
        with col3:
            st.metric("Unique Years", stats.get("unique_years", 0))
        with col4:
            if stats.get("latest_update"):
                st.metric("Latest Update", stats["latest_update"][:10])
    else:
        st.error("Failed to get data statistics")
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
st.markdown("**Railway API**: " + API_BASE_URL)
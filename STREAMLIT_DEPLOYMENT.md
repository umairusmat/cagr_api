# CAGR API - Streamlit Deployment Guide

This guide will help you deploy the CAGR Analyst Estimates API on Streamlit Cloud.

## Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Browser Requirements**: Firefox or Chrome for web scraping

## Step 1: Prepare Your Repository

### 1.1 Repository Structure
Ensure your repository has this structure:
```
cagr_api/
├── main.py                 # FastAPI application
├── models.py              # Database models
├── data_service.py        # Data service layer
├── scheduler.py           # Scheduler for automatic scraping
├── analyst_cagr.py        # CAGR scraper
├── streamlit_app.py       # Streamlit monitoring interface
├── config.json            # Configuration file
├── requirements.txt       # Python dependencies
├── packages.txt           # System packages for Streamlit Cloud
├── setup.sh              # Setup script for Streamlit Cloud
├── input/
│   └── tickers.csv       # Ticker list
├── output/               # Output directory (auto-created)
└── README.md
```

### 1.2 Update Configuration for Streamlit
Your `config.json` should be optimized for Streamlit Cloud:

```json
{
  "scraping": {
    "frequency_hours": 6,
    "retry_attempts": 3,
    "retry_delay": 2,
    "scroll_pixels": 500,
    "row_type": "Avg"
  },
  "webdriver": {
    "browser": "firefox",
    "headless": true
  },
  "data": {
    "output": {
      "directory": "./output",
      "analyst_cagr_csv": "analyst_cagr_data.csv"
    }
  },
  "api": {
    "auth_token": "your_secure_token_here",
    "host": "0.0.0.0",
    "port": 8000
  },
  "database": {
    "url": "sqlite:///cagr_data.db"
  }
}
```

### 1.3 System Packages and Setup
Your `packages.txt` file contains the system packages needed for Streamlit Cloud:
```
firefox-esr
wget
tar
libxml2-dev
libxslt1-dev
```

Your `setup.sh` script handles the GeckoDriver installation:
- Downloads and installs GeckoDriver v0.34.0
- Sets up Firefox-ESR binary path
- Configures the environment for Python 3.13.1

### 1.4 Create Streamlit App (Optional)
Create a simple Streamlit interface for monitoring:

```python
# streamlit_app.py
import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="CAGR API Monitor",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CAGR Analyst Estimates API Monitor")

# Configuration
API_BASE_URL = "http://localhost:8000"
AUTH_TOKEN = st.secrets.get("AUTH_TOKEN", "your_token_here")

headers = {"X-Auth-Token": AUTH_TOKEN}

# Sidebar
st.sidebar.title("API Controls")

# Health Check
if st.sidebar.button("Check Health"):
    try:
        response = requests.get(f"{API_BASE_URL}/health", headers=headers)
        if response.status_code == 200:
            st.sidebar.success("✅ API is healthy")
            health_data = response.json()
            st.sidebar.json(health_data)
        else:
            st.sidebar.error("❌ API is unhealthy")
    except Exception as e:
        st.sidebar.error(f"❌ Connection failed: {e}")

# Manual Scrape
if st.sidebar.button("Trigger Manual Scrape"):
    try:
        response = requests.post(f"{API_BASE_URL}/scrape/manual", headers=headers)
        if response.status_code == 200:
            st.sidebar.success("✅ Scrape triggered")
            result = response.json()
            st.sidebar.json(result)
        else:
            st.sidebar.error("❌ Scrape failed")
    except Exception as e:
        st.sidebar.error(f"❌ Error: {e}")

# Main Content
col1, col2 = st.columns(2)

with col1:
    st.header("📈 Data Overview")
    
    # Get data freshness
    try:
        response = requests.get(f"{API_BASE_URL}/data/freshness", headers=headers)
        if response.status_code == 200:
            freshness = response.json()
            st.metric("Ticker Count", freshness.get("ticker_count", 0))
            st.metric("Hours Since Update", freshness.get("hours_since_update", 0))
            st.metric("Data Fresh", "✅" if freshness.get("is_fresh") else "❌")
        else:
            st.error("Failed to get data freshness")
    except Exception as e:
        st.error(f"Error: {e}")

with col2:
    st.header("⚙️ Scheduler Status")
    
    # Get scheduler status
    try:
        response = requests.get(f"{API_BASE_URL}/scheduler/status", headers=headers)
        if response.status_code == 200:
            status = response.json()
            st.metric("Scheduler Running", "✅" if status.get("is_running") else "❌")
            st.metric("Frequency (hours)", status.get("frequency_hours", 0))
            if status.get("next_run"):
                st.metric("Next Run", status["next_run"])
        else:
            st.error("Failed to get scheduler status")
    except Exception as e:
        st.error(f"Error: {e}")

# Recent Sessions
st.header("📋 Recent Scraping Sessions")
try:
    response = requests.get(f"{API_BASE_URL}/sessions?limit=5", headers=headers)
    if response.status_code == 200:
        sessions_data = response.json()
        sessions = sessions_data.get("sessions", [])
        
        if sessions:
            for session in sessions:
                with st.expander(f"Session {session['id']} - {session['type']} ({session['status']})"):
                    st.json(session)
        else:
            st.info("No recent sessions found")
    else:
        st.error("Failed to get sessions")
except Exception as e:
    st.error(f"Error: {e}")

# Available Tickers
st.header("🏷️ Available Tickers")
try:
    response = requests.get(f"{API_BASE_URL}/tickers", headers=headers)
    if response.status_code == 200:
        tickers_data = response.json()
        tickers = tickers_data.get("tickers", [])
        
        if tickers:
            st.write(f"Found {len(tickers)} tickers:")
            st.write(", ".join(tickers))
        else:
            st.info("No tickers found")
    else:
        st.error("Failed to get tickers")
except Exception as e:
    st.error(f"Error: {e}")
```

## Step 2: Deploy to Streamlit Cloud

### 2.1 Connect Repository
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Select the repository and branch

### 2.2 Configure App Settings
- **Main file path**: `streamlit_app.py` (if you created the monitoring interface)
- **App URL**: Choose a custom subdomain
- **Python version**: 3.13.1 (required - matches your setup.sh)
- **System packages**: Streamlit will automatically use your `packages.txt`
- **Setup script**: Streamlit will run your `setup.sh` during deployment

### 2.3 Set Secrets
In your Streamlit app settings, add these secrets:

```toml
# .streamlit/secrets.toml
AUTH_TOKEN = "your_secure_api_token_here"
```

### 2.4 Deploy
Click "Deploy!" and wait for the deployment to complete.

## Step 3: Deploy FastAPI Backend

### 3.1 Using Railway (Recommended)
Railway is excellent for FastAPI applications:

1. **Sign up**: Go to [railway.app](https://railway.app)
2. **Connect GitHub**: Link your repository
3. **Deploy**: Railway will auto-detect your FastAPI app
4. **Environment Variables**: Set `AUTH_TOKEN` in Railway dashboard
5. **Custom Domain**: Configure a custom domain if needed

### 3.2 Using Render
Alternative deployment option:

1. **Sign up**: Go to [render.com](https://render.com)
2. **New Web Service**: Connect your GitHub repository
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**: Set `AUTH_TOKEN`

### 3.3 Using Heroku
Traditional option:

1. **Install Heroku CLI**
2. **Create Heroku app**: `heroku create your-app-name`
3. **Set environment variables**: `heroku config:set AUTH_TOKEN=your_token`
4. **Deploy**: `git push heroku main`

## Step 4: Configuration for Production

### 4.1 Update Streamlit App
Update the `API_BASE_URL` in your Streamlit app to point to your deployed FastAPI backend:

```python
# In streamlit_app.py
API_BASE_URL = "https://your-fastapi-app.railway.app"  # or your domain
```

### 4.2 Environment Variables
Set these in your FastAPI deployment:

```bash
AUTH_TOKEN=your_secure_token_here
DATABASE_URL=sqlite:///cagr_data.db
```

### 4.3 CORS Configuration (if needed)
Add CORS middleware to your FastAPI app:

```python
# In main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-streamlit-app.streamlit.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Step 5: Monitoring and Maintenance

### 5.1 Health Monitoring
- Use the `/health` endpoint to monitor API status
- Set up uptime monitoring (UptimeRobot, Pingdom)
- Monitor logs in your deployment platform

### 5.2 Data Management
- The scheduler automatically runs every 6 hours (configurable)
- Data is stored in SQLite database
- Use the `/data/freshness` endpoint to check data age

### 5.3 Scaling Considerations
- For high traffic, consider PostgreSQL instead of SQLite
- Use Redis for caching if needed
- Implement rate limiting for API endpoints

## Step 6: Security Best Practices

### 6.1 Authentication
- Use a strong, random AUTH_TOKEN
- Rotate tokens regularly
- Consider implementing JWT tokens for better security

### 6.2 API Security
- Enable HTTPS only
- Implement rate limiting
- Add request logging
- Use environment variables for sensitive data

### 6.3 Database Security
- Regular backups
- Encrypt sensitive data
- Use connection pooling for production

## Troubleshooting

### Common Issues

1. **WebDriver Issues**: Ensure Firefox is available in the deployment environment
2. **Memory Issues**: Monitor memory usage, especially during scraping
3. **Rate Limiting**: Add delays between requests to avoid being blocked
4. **Database Locks**: Use connection pooling and proper session management

### Debug Commands

```bash
# Check API health
curl -H "X-Auth-Token: your_token" https://your-api.com/health

# Trigger manual scrape
curl -X POST -H "X-Auth-Token: your_token" https://your-api.com/scrape/manual

# Get data freshness
curl -H "X-Auth-Token: your_token" https://your-api.com/data/freshness
```

## Cost Optimization

### Streamlit Cloud
- Free tier: 1 app, limited resources
- Pro tier: $20/month for more resources

### FastAPI Hosting
- Railway: $5/month for hobby plan
- Render: Free tier available
- Heroku: $7/month for basic plan

### Total Estimated Cost
- **Free**: Streamlit free + Render free
- **Basic**: Streamlit free + Railway hobby ($5/month)
- **Pro**: Streamlit pro + Railway hobby ($25/month)

## Support and Updates

- Monitor your deployments regularly
- Keep dependencies updated
- Test scraping functionality periodically
- Backup your database regularly

For issues or questions, check the logs in your deployment platform and ensure all environment variables are set correctly.

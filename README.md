# CAGR Analyst Estimates API

A robust FastAPI application that automatically scrapes CAGR (Compound Annual Growth Rate) analyst estimates from StockUnlock and serves the data through a secure REST API.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Features

- **Automated Scraping**: Configurable scheduler (6h/12h intervals) for fresh data
- **Secure API**: Token-based authentication for all endpoints
- **Database Storage**: SQLite database with timestamps for data tracking
- **Real-time Monitoring**: Health checks and scraping session tracking
- **Streamlit Integration**: Optional web interface for monitoring
- **Robust Error Handling**: Retry mechanisms and comprehensive logging

## 📊 What is CAGR?

CAGR (Compound Annual Growth Rate) is a financial metric that shows the mean annual growth rate of an investment over a specified time period. This API scrapes analyst estimates for revenue CAGR from StockUnlock for various stock tickers.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Scheduler     │───▶│   CAGR Scraper   │───▶│   Database      │
│  (6h/12h)       │    │  (StockUnlock)   │    │   (SQLite)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │◀───│   Data Service   │◀───│   Fresh Data    │
│   Endpoints     │    │   Layer          │    │   Storage       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛠️ Installation

### Prerequisites

- **Python 3.13.1** (required for Streamlit Cloud deployment)
- Firefox-ESR or Chrome browser
- Git
- For Streamlit Cloud: `packages.txt` and `setup.sh` files included

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd cagr_api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**
   ```bash
   # Edit config.json with your settings
   cp config.json config.json.backup
   # Update AUTH_TOKEN and other settings
   ```

5. **Prepare ticker list**
   ```bash
   # Edit input/tickers.csv with your desired tickers
   # Format: One ticker per line in the 'Ticker' column
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 📋 Configuration

### config.json

```json
{
  "scraping": {
    "frequency_hours": 6,        // Scraping interval (6 or 12 hours)
    "retry_attempts": 3,         // Retry attempts for failed scrapes
    "retry_delay": 2,            // Delay between retries (seconds)
    "scroll_pixels": 500,        // Scroll amount for page loading
    "row_type": "Avg"            // Data row type: Low, Avg, High
  },
  "webdriver": {
    "browser": "firefox",        // Browser: firefox or chrome
    "headless": true            // Run browser in headless mode
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

### input/tickers.csv

```csv
Ticker
AAPL
MSFT
GOOGL
TSLA
NVDA
```

## 🔌 API Endpoints

All endpoints require authentication via `X-Auth-Token` header.

### Data Endpoints

- `GET /` - API information and available endpoints
- `GET /data` - Get all CAGR data
- `GET /data/{ticker}` - Get CAGR data for specific ticker
- `GET /data/freshness` - Get data freshness information
- `GET /data/statistics` - Get data statistics
- `GET /tickers` - Get list of available tickers
- `GET /tickers?search=query` - Search tickers

### Control Endpoints

- `POST /scrape/manual` - Trigger manual scraping session
- `GET /scheduler/status` - Get scheduler status
- `GET /sessions` - Get recent scraping sessions
- `GET /health` - Health check endpoint

### Example Usage

```bash
# Get all data
curl -H "X-Auth-Token: your_token" http://localhost:8000/data

# Get specific ticker data
curl -H "X-Auth-Token: your_token" http://localhost:8000/data/AAPL

# Trigger manual scrape
curl -X POST -H "X-Auth-Token: your_token" http://localhost:8000/scrape/manual

# Check health
curl -H "X-Auth-Token: your_token" http://localhost:8000/health
```

### Response Format

```json
{
  "tickers": ["AAPL", "MSFT"],
  "data": {
    "AAPL": {
      "values": {
        "2025": "5.2%",
        "2026": "4.8%",
        "2027": "4.5%"
      },
      "last_updated": "2024-01-15T10:30:00"
    }
  }
}
```

## 🚀 Deployment

### Streamlit Cloud Deployment

See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) for detailed deployment instructions.

### Quick Deployment Options

1. **Railway** (Recommended)
   ```bash
   # Connect GitHub repo to Railway
   # Set AUTH_TOKEN environment variable
   # Deploy automatically
   ```

2. **Render**
   ```bash
   # Connect GitHub repo to Render
   # Set build command: pip install -r requirements.txt
   # Set start command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Heroku**
   ```bash
   heroku create your-app-name
   heroku config:set AUTH_TOKEN=your_token
   git push heroku main
   ```

## 📊 Monitoring

### Health Check

The `/health` endpoint provides comprehensive system status:

```json
{
  "status": "healthy",
  "database": "connected",
  "scheduler": {
    "is_running": true,
    "frequency_hours": 6,
    "next_run": "2024-01-15T16:30:00"
  },
  "data": {
    "has_data": true,
    "latest_update": "2024-01-15T10:30:00",
    "hours_since_update": 2.5,
    "ticker_count": 5,
    "is_fresh": true
  }
}
```

### Logging

The application logs all activities:
- Scraping sessions
- API requests
- Database operations
- Error conditions

## 🔧 Development

### Running Tests

```bash
# Test database connection
python models.py

# Test scraper
python analyst_cagr.py

# Test API endpoints
curl -H "X-Auth-Token: your_token" http://localhost:8000/health
```

### Adding New Features

1. **New API Endpoints**: Add to `main.py`
2. **Database Changes**: Update `models.py`
3. **Scraping Logic**: Modify `analyst_cagr.py`
4. **Scheduling**: Update `scheduler.py`

### Code Structure

```
cagr_api/
├── main.py              # FastAPI application and endpoints
├── models.py            # Database models and configuration
├── data_service.py      # Data access layer
├── scheduler.py         # Automatic scraping scheduler
├── analyst_cagr.py      # Web scraping logic (Python 3.13.1 compatible)
├── streamlit_app.py     # Streamlit monitoring interface
├── config.json          # Application configuration
├── requirements.txt     # Python dependencies (Python 3.13.1 compatible)
├── packages.txt         # System packages for Streamlit Cloud
├── setup.sh            # Setup script for Streamlit Cloud
├── input/
│   └── tickers.csv     # Ticker list
├── output/             # Scraped data output
└── STREAMLIT_DEPLOYMENT.md  # Deployment guide
```

## 🛡️ Security

- **Authentication**: Token-based API authentication
- **Rate Limiting**: Built-in delays between scraping requests
- **Error Handling**: Comprehensive error handling and logging
- **Data Validation**: Input validation for all endpoints

## 📈 Performance

- **Efficient Scraping**: Optimized Selenium configuration
- **Database Indexing**: Indexed database queries
- **Caching**: In-memory data caching
- **Background Processing**: Non-blocking scraping operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the logs in your deployment platform
2. Verify all environment variables are set
3. Test the `/health` endpoint
4. Review the configuration in `config.json`

## 🔄 Updates

The application automatically:
- Scrapes fresh data at configured intervals
- Updates the database with new information
- Maintains data freshness tracking
- Logs all operations for monitoring

## 📊 Data Sources

- **StockUnlock**: Primary data source for CAGR analyst estimates
- **Ticker Management**: Uses `input/tickers.csv` for ticker list
- **Data Storage**: SQLite database with timestamp tracking

---

**Note**: This application is for educational and research purposes. Please respect the terms of service of StockUnlock and implement appropriate rate limiting for production use.
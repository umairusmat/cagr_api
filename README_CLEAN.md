# CAGR API - Clean Implementation

A clean, reliable application that scrapes CAGR (Compound Annual Growth Rate) data from StockUnlock and serves it through a REST API.

## Features

- ✅ **Python 3.13.5 Compatible**: Built specifically for Python 3.13.5
- ✅ **Automatic Scraping**: Scrapes data every 3-6 hours (configurable)
- ✅ **REST API**: Clean FastAPI with authentication
- ✅ **SQLite Database**: Local data storage
- ✅ **Railway Deployment**: Ready for Railway deployment
- ✅ **Background Scheduler**: Automatic data updates
- ✅ **Health Monitoring**: Built-in health checks and status endpoints

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

Edit `config.json` to set your preferences:

```json
{
  "scraping": {
    "frequency_hours": 6,
    "enabled": true,
    "headless": true
  },
  "api": {
    "auth_token": "mysecretapitoken123",
    "host": "0.0.0.0",
    "port": 8000
  }
}
```

### 3. Add Your Tickers

Edit `input/tickers.csv` with your stock tickers:

```csv
Ticker
AAPL
MSFT
GOOGL
AMZN
TSLA
```

### 4. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
All endpoints require the `X-Auth-Token` header with your configured token.

### Available Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /data` - Get all CAGR data
- `GET /data/{ticker}` - Get data for specific ticker
- `GET /data/freshness` - Get data freshness info
- `GET /data/statistics` - Get data statistics
- `GET /tickers` - Get list of available tickers
- `POST /scrape/manual` - Trigger manual scrape
- `GET /scheduler/status` - Get scheduler status

### Example Usage

```bash
# Get all data
curl -H "X-Auth-Token: mysecretapitoken123" http://localhost:8000/data

# Get specific ticker
curl -H "X-Auth-Token: mysecretapitoken123" http://localhost:8000/data/AAPL

# Health check
curl http://localhost:8000/health
```

## Configuration

### Scraping Settings

- `frequency_hours`: How often to scrape (default: 6 hours)
- `enabled`: Enable/disable automatic scraping
- `headless`: Run browser in headless mode

### API Settings

- `auth_token`: Authentication token for API access
- `host`: API host (default: 0.0.0.0)
- `port`: API port (default: 8000)

## Railway Deployment

### 1. Connect to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init
```

### 2. Deploy

```bash
railway up
```

### 3. Set Environment Variables (if needed)

```bash
railway variables set AUTH_TOKEN=your_secret_token
```

## File Structure

```
cagr_api/
├── app.py                 # Main application
├── api.py                 # FastAPI endpoints
├── cagr_scraper.py        # Scraping logic
├── scheduler.py           # Background scheduler
├── config.json           # Configuration
├── requirements.txt      # Dependencies
├── railway.json         # Railway config
├── Procfile             # Process file
├── runtime.txt          # Python version
├── input/
│   └── tickers.csv      # Stock tickers
└── output/              # Generated data
```

## How It Works

1. **Background Scheduler**: Automatically runs scraping every 6 hours
2. **Scraper**: Uses Selenium to scrape StockUnlock for CAGR data
3. **Database**: Stores data in SQLite database
4. **API**: Serves data through FastAPI with authentication
5. **Health Monitoring**: Provides status and health information

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**: The app uses webdriver-manager to automatically handle Chrome driver installation
2. **Memory Issues**: The scraper runs in headless mode to minimize resource usage
3. **Rate Limiting**: Built-in delays between requests to avoid being blocked

### Logs

Check the console output for detailed logging information.

### Manual Scraping

You can trigger manual scraping via the API:

```bash
curl -X POST -H "X-Auth-Token: mysecretapitoken123" http://localhost:8000/scrape/manual
```

## Development

### Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `config.json`
4. Add tickers to `input/tickers.csv`
5. Run: `python app.py`

### Testing

Test individual components:

```bash
# Test scraper
python cagr_scraper.py

# Test scheduler
python scheduler.py

# Test API
python api.py
```

## Support

This is a clean, simplified implementation designed to be reliable and easy to maintain. The code is well-documented and follows best practices for Python 3.13.5.

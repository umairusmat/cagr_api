# CAGR API Documentation

## Overview
The CAGR API provides access to analyst CAGR (Compound Annual Growth Rate) estimates scraped from StockUnlock. The API automatically scrapes data every 3-6 hours and serves it via REST endpoints.

**Base URL**: `https://cagrapi-production.up.railway.app`  
**Version**: `2.0.0`  
**Authentication**: Required for data endpoints

## Authentication
All data endpoints require authentication using the `X-Auth-Token` header:

```bash
curl -H "X-Auth-Token: mysecretapitoken123" https://cagrapi-production.up.railway.app/data
```

## Endpoints

### 1. Health Check
**GET** `/health`

Check API health and status.

**Response:**
```json
{
  "status": "healthy",
  "message": "CAGR API is running",
  "version": "2.0.0",
  "timestamp": "2025-10-14T09:48:59.667772",
  "data": {
    "available": true,
    "total_tickers": 4,
    "last_scrape": "2025-10-14T09:44:02.936861"
  },
  "endpoints": {
    "health": "/health",
    "data": "/data",
    "data_by_ticker": "/data/{ticker}",
    "data_freshness": "/data/freshness",
    "data_statistics": "/data/statistics",
    "tickers": "/tickers",
    "scrape_manual": "/scrape/manual"
  }
}
```

### 2. Get All Data
**GET** `/data`

Retrieve all CAGR data for all tickers.

**Headers:**
- `X-Auth-Token`: Your authentication token

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "ticker": "MELI",
      "data": {
        "2025": "Low",
        "2026": "Show All",
        "2027": "High",
        "2028": "Avg",
        "2029": "Low",
        "2030": "Net",
        "2031": "YoY",
        "2032": "CAGR"
      },
      "last_updated": "2025-10-14T09:43:10.204232"
    }
  ],
  "count": 4,
  "timestamp": "2025-10-14T09:49:22.678531"
}
```

### 3. Get Ticker Data
**GET** `/data/{ticker}`

Retrieve CAGR data for a specific ticker.

**Parameters:**
- `ticker` (string): Stock ticker symbol (e.g., "AAPL", "MSFT")

**Headers:**
- `X-Auth-Token`: Your authentication token

**Response:**
```json
{
  "success": true,
  "ticker": "MELI",
  "data": {
    "2025": "Low",
    "2026": "Show All",
    "2027": "High",
    "2028": "Avg",
    "2029": "Low",
    "2030": "Net",
    "2031": "YoY",
    "2032": "CAGR"
  },
  "last_updated": "2025-10-14T09:43:10.204232",
  "timestamp": "2025-10-14T09:49:22.678531"
}
```

### 4. Get Available Tickers
**GET** `/tickers`

Get list of all available tickers.

**Headers:**
- `X-Auth-Token`: Your authentication token

**Response:**
```json
{
  "success": true,
  "tickers": ["MELI", "SE", "FOUR", "HIMS"],
  "count": 4,
  "timestamp": "2025-10-14T09:49:22.678531"
}
```

### 5. Data Freshness
**GET** `/data/freshness`

Get information about data freshness and last update times.

**Headers:**
- `X-Auth-Token`: Your authentication token

**Response:**
```json
{
  "success": true,
  "freshness": {
    "last_scrape": "2025-10-14T09:44:02.936861",
    "total_tickers": 4,
    "data_available": true,
    "ticker_freshness": {
      "MELI": "2025-10-14T09:43:10.204232",
      "SE": "2025-10-14T09:43:27.876668",
      "FOUR": "2025-10-14T09:43:45.312054",
      "HIMS": "2025-10-14T09:44:02.936861"
    }
  },
  "timestamp": "2025-10-14T09:49:22.678531"
}
```

### 6. Data Statistics
**GET** `/data/statistics`

Get statistical information about the data.

**Headers:**
- `X-Auth-Token`: Your authentication token

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_tickers": 4,
    "total_records": 27,
    "year_range": {
      "min": "2025",
      "max": "2032"
    },
    "ticker_counts": {
      "MELI": 8,
      "SE": 8,
      "FOUR": 3,
      "HIMS": 8
    }
  },
  "timestamp": "2025-10-14T09:49:22.678531"
}
```

### 7. Manual Scrape
**POST** `/scrape/manual`

Trigger a manual scrape of all tickers.

**Headers:**
- `X-Auth-Token`: Your authentication token

**Response:**
```json
{
  "success": true,
  "message": "Manual scrape completed: 4 successful",
  "results": {
    "total_tickers": 4,
    "successful": 4,
    "failed": 0
  },
  "timestamp": "2025-10-14T09:49:22.678531"
}
```

## Usage Examples

### Python
```python
import requests

# Set up authentication
headers = {"X-Auth-Token": "mysecretapitoken123"}
base_url = "https://cagrapi-production.up.railway.app"

# Get all data
response = requests.get(f"{base_url}/data", headers=headers)
data = response.json()

# Get specific ticker
response = requests.get(f"{base_url}/data/MELI", headers=headers)
meli_data = response.json()

# Trigger manual scrape
response = requests.post(f"{base_url}/scrape/manual", headers=headers)
scrape_result = response.json()
```

### cURL
```bash
# Health check
curl https://cagrapi-production.up.railway.app/health

# Get all data
curl -H "X-Auth-Token: mysecretapitoken123" \
     https://cagrapi-production.up.railway.app/data

# Get specific ticker
curl -H "X-Auth-Token: mysecretapitoken123" \
     https://cagrapi-production.up.railway.app/data/MELI

# Manual scrape
curl -X POST -H "X-Auth-Token: mysecretapitoken123" \
     https://cagrapi-production.up.railway.app/scrape/manual
```

### JavaScript
```javascript
const baseUrl = 'https://cagrapi-production.up.railway.app';
const token = 'mysecretapitoken123';

// Get all data
fetch(`${baseUrl}/data`, {
  headers: { 'X-Auth-Token': token }
})
.then(response => response.json())
.then(data => console.log(data));

// Get specific ticker
fetch(`${baseUrl}/data/MELI`, {
  headers: { 'X-Auth-Token': token }
})
.then(response => response.json())
.then(data => console.log(data));
```

## Data Format

### CAGR Values
The API returns CAGR values in various formats:
- **Numeric values**: Direct CAGR percentages
- **Text values**: "Low", "High", "Avg", "Net", "YoY", "CAGR"
- **Action values**: "Go to DCF", "Go to Free Form", "Show All"

### Year Range
- **Minimum**: 2025
- **Maximum**: 2032 (varies by ticker)
- **Format**: YYYY string

### Timestamps
- **Format**: ISO 8601 (`YYYY-MM-DDTHH:MM:SS.ffffff`)
- **Timezone**: UTC

## Error Handling

### Common HTTP Status Codes
- **200**: Success
- **401**: Unauthorized (invalid token)
- **404**: Not Found (invalid ticker)
- **500**: Internal Server Error

### Error Response Format
```json
{
  "success": false,
  "error": "Error message",
  "timestamp": "2025-10-14T09:49:22.678531"
}
```

## Rate Limits
- **No rate limits** currently implemented
- **Scraping frequency**: Every 3-6 hours (configurable)
- **Manual scraping**: Available on demand

## Data Sources
- **Primary**: StockUnlock (https://stockunlock.com)
- **Scraping method**: Selenium with Firefox-ESR
- **Update frequency**: Automatic every 3-6 hours
- **Manual updates**: Available via API

## Support
For issues or questions:
1. Check the `/health` endpoint for API status
2. Verify authentication token
3. Check data freshness with `/data/freshness`
4. Trigger manual scrape if needed

## Changelog
- **v2.0.0**: Initial release with full CAGR data API
- **Features**: Health checks, data retrieval, manual scraping, statistics

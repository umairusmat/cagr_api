# Manual CAGR Scraping Guide

## Overview
This guide explains how to use the manual CAGR scraping functionality to get data for specific tickers (AAPL, MSFT, TSLA, META) and save results to `manual_cagr.csv`.

## Files Created

### 1. `manaul_requests.py` - Main Manual Scraping Script
- **Purpose**: Comprehensive manual scraping script
- **Features**: 
  - API health checking
  - Manual scrape triggering
  - Data retrieval and CSV export
  - Support for specific tickers

### 2. `update_tickers.py` - Ticker Update Script
- **Purpose**: Updates `input/tickers.csv` with new tickers
- **Usage**: `python api_calls/update_tickers.py`

### 3. `test_manual_scrape.py` - Simple Test Script
- **Purpose**: Simple script to test manual scraping
- **Usage**: `python api_calls/test_manual_scrape.py`

## Usage Options

### Option 1: Scrape Currently Available Tickers
```bash
python api_calls/manaul_requests.py available
```
- Gets data for currently available tickers (MELI, SE, FOUR, HIMS)
- Saves to `manual_cagr.csv`

### Option 2: Request New Tickers (AAPL, MSFT, TSLA, META)
```bash
python api_calls/manaul_requests.py custom
```
- Attempts to get data for AAPL, MSFT, TSLA, META
- If not available, provides instructions to update tickers

### Option 3: Update Tickers and Deploy
```bash
# 1. Update tickers file
python api_calls/update_tickers.py

# 2. Deploy to Railway
git add input/tickers.csv
git commit -m "Update tickers to AAPL, MSFT, TSLA, META"
git push origin main

# 3. Wait for Railway to redeploy and scrape new tickers
# 4. Then run the scraping script
python api_calls/manaul_requests.py custom
```

## Current Status

### Available Tickers (Currently on Railway)
- MELI (MercadoLibre)
- SE (Sea Ltd)
- FOUR (Shift4 Payments)
- HIMS (Hims & Hers Health)

### Requested Tickers (Need to be added)
- AAPL (Apple)
- MSFT (Microsoft)
- TSLA (Tesla)
- META (Meta)

## CSV Output Format

The `manual_cagr.csv` file will contain:
- **Ticker**: Stock symbol
- **Last_Updated**: When data was scraped
- **Year columns**: 2025, 2026, 2027, etc. with CAGR percentages

Example:
```csv
Ticker,Last_Updated,2025,2026,2027,2028,2029,2030,2031,2032
MELI,2025-10-15T08:55:09.760314,19.4%,22.8%,22.5%,21.3%,20.1%,18.1%,17.3%,16.6%
SE,2025-10-15T08:55:56.740588,16.5%,19.4%,18.3%,17.3%,16.5%,15.7%,14.9%,14.3%
```

## Next Steps

1. **For Current Data**: Use `python api_calls/manaul_requests.py available`
2. **For New Tickers**: Follow the deployment process above
3. **Check Results**: Look for `manual_cagr.csv` in the current directory

## Troubleshooting

- **API Timeout**: Railway scraping takes time, be patient
- **No Data**: Check if tickers are available in Railway
- **Connection Issues**: Verify Railway deployment is running
- **Missing Tickers**: Update `input/tickers.csv` and redeploy

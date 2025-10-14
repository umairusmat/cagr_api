"""
Example usage of the CAGR API
Demonstrates various ways to interact with the API
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://cagrapi-production.up.railway.app"
AUTH_TOKEN = "mysecretapitoken123"
HEADERS = {"X-Auth-Token": AUTH_TOKEN}

def example_health_check():
    """Example: Check API health"""
    print("🔍 Checking API health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        response.raise_for_status()
        health = response.json()
        
        print(f"✅ Status: {health['status']}")
        print(f"📊 Data Available: {health['data']['available']}")
        print(f"📈 Total Tickers: {health['data']['total_tickers']}")
        print(f"🕒 Last Scrape: {health['data']['last_scrape']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def example_get_all_data():
    """Example: Get all CAGR data"""
    print("\n📥 Fetching all CAGR data...")
    try:
        response = requests.get(f"{BASE_URL}/data", headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data['success']:
            print(f"✅ Fetched data for {len(data['data'])} tickers")
            for ticker_data in data['data']:
                ticker = ticker_data['ticker']
                years = len(ticker_data['data'])
                print(f"  📈 {ticker}: {years} years of data")
            return data
        else:
            print("❌ Failed to fetch data")
            return None
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def example_get_ticker_data(ticker):
    """Example: Get data for specific ticker"""
    print(f"\n📊 Fetching data for {ticker}...")
    try:
        response = requests.get(f"{BASE_URL}/data/{ticker}", headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data['success']:
            print(f"✅ {ticker} data:")
            for year, value in data['data'].items():
                print(f"  {year}: {value}")
            return data
        else:
            print(f"❌ Failed to fetch data for {ticker}")
            return None
    except Exception as e:
        print(f"❌ Error fetching {ticker}: {e}")
        return None

def example_get_tickers():
    """Example: Get available tickers"""
    print("\n📋 Fetching available tickers...")
    try:
        response = requests.get(f"{BASE_URL}/tickers", headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data['success']:
            print(f"✅ Available tickers: {', '.join(data['tickers'])}")
            return data['tickers']
        else:
            print("❌ Failed to fetch tickers")
            return None
    except Exception as e:
        print(f"❌ Error fetching tickers: {e}")
        return None

def example_manual_scrape():
    """Example: Trigger manual scrape"""
    print("\n🔄 Triggering manual scrape...")
    try:
        response = requests.post(f"{BASE_URL}/scrape/manual", headers=HEADERS, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        if data['success']:
            print(f"✅ Manual scrape completed: {data['message']}")
            print(f"📊 Results: {data['results']['successful']}/{data['results']['total_tickers']} successful")
            return data
        else:
            print("❌ Manual scrape failed")
            return None
    except Exception as e:
        print(f"❌ Error triggering scrape: {e}")
        return None

def example_data_analysis():
    """Example: Analyze the data"""
    print("\n📊 Analyzing CAGR data...")
    
    # Get all data
    all_data = example_get_all_data()
    if not all_data:
        return
    
    # Analyze data
    total_records = 0
    year_counts = {}
    ticker_counts = {}
    
    for ticker_data in all_data['data']:
        ticker = ticker_data['ticker']
        ticker_counts[ticker] = len(ticker_data['data'])
        total_records += len(ticker_data['data'])
        
        for year in ticker_data['data'].keys():
            year_counts[year] = year_counts.get(year, 0) + 1
    
    print(f"\n📈 Analysis Results:")
    print(f"  Total Records: {total_records}")
    print(f"  Total Tickers: {len(ticker_counts)}")
    print(f"  Year Range: {min(year_counts.keys())} - {max(year_counts.keys())}")
    print(f"  Records per Ticker:")
    for ticker, count in ticker_counts.items():
        print(f"    {ticker}: {count} years")

def main():
    """Run all examples"""
    print("🚀 CAGR API Examples")
    print("=" * 50)
    
    # Check health first
    if not example_health_check():
        print("❌ API is not healthy, stopping examples")
        return
    
    # Get available tickers
    tickers = example_get_tickers()
    if not tickers:
        print("❌ Could not get tickers, stopping examples")
        return
    
    # Get all data
    example_get_all_data()
    
    # Get specific ticker data
    if tickers:
        example_get_ticker_data(tickers[0])
    
    # Analyze data
    example_data_analysis()
    
    # Optional: Trigger manual scrape (uncomment if needed)
    # example_manual_scrape()
    
    print("\n🎉 Examples completed!")

if __name__ == "__main__":
    main()

"""
Test manual scraping with current available data
"""

import requests
import pandas as pd
from datetime import datetime

def test_manual_scrape():
    """Test manual scraping and save to CSV"""
    print("Testing Manual CAGR Scraping")
    print("=" * 50)
    
    # API configuration
    base_url = "https://cagrapi-production.up.railway.app"
    auth_token = "mysecretapitoken123"
    headers = {"X-Auth-Token": auth_token}
    
    try:
        # Check API health
        print("Checking API health...")
        response = requests.get(f"{base_url}/health", headers=headers, timeout=10)
        response.raise_for_status()
        health = response.json()
        print(f"SUCCESS: API Status: {health['status']}")
        print(f"Data Available: {health['data']['available']}")
        print(f"Total Tickers: {health['data']['total_tickers']}")
        print(f"Last Scrape: {health['data']['last_scrape']}")
        
        # Get current data
        print("\nFetching current data...")
        response = requests.get(f"{base_url}/data", headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data['success']:
            print(f"SUCCESS: Fetched data for {len(data['data'])} tickers")
            
            # Convert to wide format for CSV
            rows = []
            for ticker_data in data['data']:
                ticker = ticker_data['ticker']
                ticker_info = ticker_data['data']
                last_updated = ticker_data['last_updated']
                
                # Create a row for this ticker
                row = {'Ticker': ticker, 'Last_Updated': last_updated}
                
                # Add each year as a column
                for year, value in ticker_info.items():
                    row[year] = value
                
                rows.append(row)
            
            # Create DataFrame and save to CSV
            df = pd.DataFrame(rows)
            output_file = "manual_cagr.csv"
            df.to_csv(output_file, index=False)
            
            print(f"SUCCESS: Data saved to {output_file}")
            print(f"Total tickers: {len(df)}")
            print(f"Columns: {list(df.columns)}")
            
            # Show sample data
            print("\nSample Data:")
            print(df.to_string(index=False))
            
            return True
        else:
            print("ERROR: Failed to fetch data")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_manual_scrape()

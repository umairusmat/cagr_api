"""
Manual CAGR Scraping Script
Triggers manual scraping on Railway deployment for custom tickers
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

class ManualCAGRScraper:
    """Client for manual CAGR scraping on Railway"""
    
    def __init__(self, base_url="https://cagrapi-production.up.railway.app", auth_token="mysecretapitoken123"):
        self.base_url = base_url
        self.auth_token = auth_token
        self.headers = {"X-Auth-Token": auth_token}
    
    def check_api_health(self):
        """Check if API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            health = response.json()
            print(f"SUCCESS: API Status: {health['status']}")
            print(f"Data Available: {health['data']['available']}")
            print(f"Total Tickers: {health['data']['total_tickers']}")
            print(f"Last Scrape: {health['data']['last_scrape']}")
            return True
        except Exception as e:
            print(f"ERROR: API Health Check Failed: {e}")
            return False
    
    def trigger_manual_scrape(self):
        """Trigger manual scrape on Railway"""
        try:
            print("Triggering manual scrape on Railway...")
            response = requests.post(
                f"{self.base_url}/scrape/manual", 
                headers=self.headers, 
                timeout=120  # 2 minutes timeout for scraping
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"SUCCESS: Manual Scrape Result: {result['message']}")
            print(f"Timestamp: {result['timestamp']}")
            return result
            
        except Exception as e:
            print(f"ERROR: Manual Scrape Failed: {e}")
            return None
    
    def get_current_data(self):
        """Get current data from API"""
        try:
            print("Fetching current data...")
            response = requests.get(f"{self.base_url}/data", headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data['success']:
                print(f"SUCCESS: Fetched data for {len(data['data'])} tickers")
                return data['data']
            else:
                print("ERROR: Failed to fetch data")
                return None
                
        except Exception as e:
            print(f"ERROR: Error fetching data: {e}")
            return None
    
    def get_ticker_data(self, ticker: str):
        """Get data for specific ticker"""
        try:
            print(f"Fetching data for {ticker}...")
            response = requests.get(f"{self.base_url}/data/{ticker}", headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data['success']:
                print(f"SUCCESS: {ticker} data:")
                for year, value in data['data'].items():
                    print(f"  {year}: {value}")
                return data
            else:
                print(f"ERROR: Failed to fetch data for {ticker}")
                return None
                
        except Exception as e:
            print(f"ERROR: Error fetching {ticker}: {e}")
            return None
    
    def get_data_freshness(self):
        """Get data freshness information"""
        try:
            print("Checking data freshness...")
            response = requests.get(f"{self.base_url}/data/freshness", headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['success']:
                freshness = data['freshness']
                print(f"Last Scrape: {freshness['last_scrape']}")
                print(f"Total Tickers: {freshness['total_tickers']}")
                print(f"Data Available: {freshness['data_available']}")
                
                # Show ticker freshness
                if 'ticker_freshness' in freshness:
                    print("Ticker Freshness:")
                    for ticker, timestamp in freshness['ticker_freshness'].items():
                        print(f"  {ticker}: {timestamp}")
                
                return freshness
            else:
                print("ERROR: Failed to get freshness info")
                return None
                
        except Exception as e:
            print(f"ERROR: Error getting freshness: {e}")
            return None
    
    def wait_for_scrape_completion(self, timeout_minutes=5):
        """Wait for manual scrape to complete"""
        print(f"Waiting for scrape completion (timeout: {timeout_minutes} minutes)...")
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        while time.time() - start_time < timeout_seconds:
            try:
                # Check freshness to see if data was updated
                freshness = self.get_data_freshness()
                if freshness and freshness['data_available']:
                    print("SUCCESS: Scrape completed successfully!")
                    return True
                    
            except Exception as e:
                print(f"WARNING: Error checking completion: {e}")
            
            time.sleep(10)  # Wait 10 seconds before checking again
        
        print("TIMEOUT: Timeout reached, scrape may still be running")
        return False
    
    def scrape_specific_tickers(self, tickers: List[str], output_file: str = "manual_cagr.csv"):
        """Scrape specific tickers and save to CSV"""
        print(f"Requesting tickers: {', '.join(tickers)}")
        print("=" * 50)
        
        # Check API health first
        if not self.check_api_health():
            print("ERROR: API is not healthy, cannot proceed")
            return False
        
        # Get current data (no manual scrape needed for existing data)
        print("Fetching current data...")
        all_data = self.get_current_data()
        
        if not all_data:
            print("ERROR: No data available")
            return False
        
        # Show available tickers
        available_tickers = [ticker_data['ticker'] for ticker_data in all_data]
        print(f"Available tickers: {', '.join(available_tickers)}")
        
        # Filter for requested tickers
        filtered_data = []
        for ticker_data in all_data:
            if ticker_data['ticker'] in tickers:
                filtered_data.append(ticker_data)
        
        if not filtered_data:
            print(f"WARNING: No data found for requested tickers: {', '.join(tickers)}")
            print("Available tickers:")
            for ticker_data in all_data:
                print(f"  - {ticker_data['ticker']}")
            print("\nNOTE: To scrape new tickers (AAPL, MSFT, TSLA, META), you need to:")
            print("1. Update input/tickers.csv on Railway with the new tickers")
            print("2. Redeploy the application")
            print("3. Wait for automatic scraping or trigger manual scrape")
            return False
        
        # Convert to wide format for CSV
        rows = []
        for ticker_data in filtered_data:
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
        df.to_csv(output_file, index=False)
        
        print(f"SUCCESS: Data saved to {output_file}")
        print(f"Total tickers: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Show sample data
        print("\nSample Data:")
        print(df.to_string(index=False))
        
        return True

def main():
    """Main function to demonstrate manual scraping"""
    print("Manual CAGR Scraping Script")
    print("=" * 50)
    
    # Initialize client
    scraper = ManualCAGRScraper()
    
    # Check API health
    if not scraper.check_api_health():
        print("ERROR: API is not healthy, exiting...")
        return
    
    print("\n" + "=" * 50)
    
    # Get current data before scraping
    print("Current Data (Before Manual Scrape):")
    current_data = scraper.get_current_data()
    if current_data:
        for ticker_data in current_data:
            ticker = ticker_data['ticker']
            last_updated = ticker_data['last_updated']
            print(f"  {ticker}: Last updated {last_updated}")
    
    print("\n" + "=" * 50)
    
    # Trigger manual scrape
    print("Triggering Manual Scrape...")
    scrape_result = scraper.trigger_manual_scrape()
    
    if scrape_result:
        print("\nManual scrape triggered, waiting for completion...")
        
        # Wait for completion
        if scraper.wait_for_scrape_completion():
            print("\n" + "=" * 50)
            print("Updated Data (After Manual Scrape):")
            
            # Get updated data
            updated_data = scraper.get_current_data()
            if updated_data:
                for ticker_data in updated_data:
                    ticker = ticker_data['ticker']
                    last_updated = ticker_data['last_updated']
                    print(f"  {ticker}: Last updated {last_updated}")
                    
                    # Show sample data for first ticker
                    if ticker_data == updated_data[0]:
                        print(f"    Sample data for {ticker}:")
                        for year, value in list(ticker_data['data'].items())[:3]:
                            print(f"      {year}: {value}")
                        if len(ticker_data['data']) > 3:
                            print(f"      ... and {len(ticker_data['data']) - 3} more years")
    
    print("\nSUCCESS: Manual scraping demonstration completed!")

def test_specific_ticker(ticker: str):
    """Test getting data for a specific ticker"""
    print(f"Testing specific ticker: {ticker}")
    print("=" * 50)
    
    scraper = ManualCAGRScraper()
    
    # Check health
    if not scraper.check_api_health():
        return
    
    # Get ticker data
    data = scraper.get_ticker_data(ticker)
    
    if data:
        print(f"\nSUCCESS: Successfully retrieved data for {ticker}")
        print("CAGR Data:")
        for year, value in data['data'].items():
            print(f"  {year}: {value}")
    else:
        print(f"\nERROR: Failed to retrieve data for {ticker}")

def check_data_freshness():
    """Check data freshness"""
    print("Checking Data Freshness")
    print("=" * 50)
    
    scraper = ManualCAGRScraper()
    
    # Check health
    if not scraper.check_api_health():
        return
    
    # Get freshness info
    scraper.get_data_freshness()

def scrape_custom_tickers():
    """Scrape specific tickers and save to CSV"""
    print("Custom Ticker Scraping")
    print("=" * 50)
    
    # Define the tickers to scrape
    target_tickers = ["AAPL", "MSFT", "TSLA", "META"]
    output_file = "manual_cagr.csv"
    
    # Initialize scraper
    scraper = ManualCAGRScraper()
    
    # Scrape specific tickers
    success = scraper.scrape_specific_tickers(target_tickers, output_file)
    
    if success:
        print(f"\nSUCCESS: Scraping completed for {', '.join(target_tickers)}")
        print(f"Results saved to: {output_file}")
    else:
        print(f"\nERROR: Failed to scrape tickers: {', '.join(target_tickers)}")
        print("\nSOLUTION: To scrape new tickers (AAPL, MSFT, TSLA, META):")
        print("1. The tickers.csv file has been updated locally")
        print("2. Run: git add input/tickers.csv")
        print("3. Run: git commit -m 'Update tickers to AAPL, MSFT, TSLA, META'")
        print("4. Run: git push origin main")
        print("5. Wait for Railway to redeploy and scrape new tickers")
        print("6. Then run this script again")

def scrape_available_tickers():
    """Scrape currently available tickers and save to CSV"""
    print("Available Ticker Scraping")
    print("=" * 50)
    
    # Get currently available tickers from API
    scraper = ManualCAGRScraper()
    
    # Check API health first
    if not scraper.check_api_health():
        print("ERROR: API is not healthy, cannot proceed")
        return False
    
    # Get current data
    print("Fetching current data...")
    all_data = scraper.get_current_data()
    
    if not all_data:
        print("ERROR: No data available")
        return False
    
    # Show available tickers
    available_tickers = [ticker_data['ticker'] for ticker_data in all_data]
    print(f"Available tickers: {', '.join(available_tickers)}")
    
    # Convert to wide format for CSV
    rows = []
    for ticker_data in all_data:
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

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "ticker" and len(sys.argv) > 2:
            # Test specific ticker: python manaul_requests.py ticker MELI
            test_specific_ticker(sys.argv[2])
        elif command == "freshness":
            # Check freshness: python manaul_requests.py freshness
            check_data_freshness()
        elif command == "custom":
            # Scrape custom tickers: python manaul_requests.py custom
            scrape_custom_tickers()
        elif command == "available":
            # Scrape available tickers: python manaul_requests.py available
            scrape_available_tickers()
        else:
            print("Usage:")
            print("  python manaul_requests.py                    # Full demo")
            print("  python manaul_requests.py ticker MELI        # Test specific ticker")
            print("  python manaul_requests.py freshness          # Check data freshness")
            print("  python manaul_requests.py custom             # Scrape AAPL, MSFT, TSLA, META")
            print("  python manaul_requests.py available         # Scrape currently available tickers")
    else:
        # Full demonstration
        main()

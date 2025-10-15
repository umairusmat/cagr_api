"""
Enhanced Manual CAGR Scraping Script
Works with the new enhanced API that supports dynamic ticker management
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

class EnhancedManualCAGRScraper:
    """Client for enhanced manual CAGR scraping"""
    
    def __init__(self, base_url="https://cagrapi-production.up.railway.app", auth_token="mysecretapitoken123"):
        self.base_url = base_url
        self.auth_token = auth_token
        self.headers = {"X-Auth-Token": auth_token}
    
    def check_api_health(self):
        """Check if enhanced API is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            health = response.json()
            print(f"SUCCESS: API Status: {health['status']}")
            print(f"Version: {health['version']}")
            print(f"Data Available: {health['data']['available']}")
            print(f"Total Tickers: {health['data']['total_tickers']}")
            print(f"Scheduled Tickers: {health['ticker_management']['scheduled_tickers']}")
            print(f"Total Managed Tickers: {health['ticker_management']['total_tickers']}")
            return True
        except Exception as e:
            print(f"ERROR: API Health Check Failed: {e}")
            return False
    
    def get_all_tickers(self):
        """Get all managed tickers"""
        try:
            print("Fetching all managed tickers...")
            response = requests.get(f"{self.base_url}/tickers", headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data['success']:
                print(f"SUCCESS: Found {data['total_count']} managed tickers")
                for ticker_info in data['tickers']:
                    status = "Scheduled" if ticker_info['is_scheduled'] else "Manual"
                    groups = ", ".join(ticker_info['groups'])
                    print(f"  {ticker_info['ticker']}: {status} (Groups: {groups})")
                return data['tickers']
            else:
                print("ERROR: Failed to fetch tickers")
                return None
                
        except Exception as e:
            print(f"ERROR: Error fetching tickers: {e}")
            return None
    
    def add_tickers(self, tickers: List[str], is_scheduled: bool = True, group_name: str = "manual"):
        """Add new tickers to the system"""
        try:
            print(f"Adding tickers: {', '.join(tickers)}")
            response = requests.post(
                f"{self.base_url}/tickers/manage/batch",
                headers=self.headers,
                json={
                    "tickers": tickers,
                    "is_scheduled": is_scheduled,
                    "group_name": group_name
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data['success']:
                print(f"SUCCESS: {data['message']}")
                for result in data['results']:
                    status = "SUCCESS" if result['success'] else "FAILED"
                    print(f"  {result['ticker']}: {status}")
                return True
            else:
                print("ERROR: Failed to add tickers")
                return False
                
        except Exception as e:
            print(f"ERROR: Error adding tickers: {e}")
            return False
    
    def manual_scrape_tickers(self, tickers: List[str], wait_for_completion: bool = True):
        """Manually scrape specific tickers"""
        try:
            print(f"Triggering manual scrape for: {', '.join(tickers)}")
            response = requests.post(
                f"{self.base_url}/scrape/manual",
                headers=self.headers,
                json={
                    "tickers": tickers,
                    "wait_for_completion": wait_for_completion
                },
                timeout=300  # 5 minutes timeout for scraping
            )
            response.raise_for_status()
            data = response.json()
            
            if data['success']:
                print(f"SUCCESS: {data['message']}")
                print(f"Requested: {len(data['requested_tickers'])} tickers")
                print(f"Successful: {data['successful_count']}")
                print(f"Failed: {data['failed_count']}")
                return True
            else:
                print("ERROR: Manual scrape failed")
                return False
                
        except Exception as e:
            print(f"ERROR: Manual scrape failed: {e}")
            return False
    
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
    
    def get_all_data(self):
        """Get all CAGR data"""
        try:
            print("Fetching all CAGR data...")
            response = requests.get(f"{self.base_url}/data", headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data['success']:
                print(f"SUCCESS: Fetched data for {data['total_tickers']} tickers")
                return data['data']
            else:
                print("ERROR: Failed to fetch data")
                return None
                
        except Exception as e:
            print(f"ERROR: Error fetching data: {e}")
            return None
    
    def save_to_csv(self, data: List[Dict], output_file: str = "manual_cagr.csv"):
        """Save data to CSV file"""
        try:
            # Convert to wide format for CSV
            rows = []
            for ticker_data in data:
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
            
        except Exception as e:
            print(f"ERROR: Failed to save CSV: {e}")
            return False

def scrape_custom_tickers(tickers: List[str], output_file: str = "manual_cagr.csv"):
    """Scrape custom tickers and save to CSV"""
    print("Enhanced Manual CAGR Scraping")
    print("=" * 50)
    
    # Initialize scraper
    scraper = EnhancedManualCAGRScraper()
    
    # Check API health
    if not scraper.check_api_health():
        print("ERROR: API is not healthy, cannot proceed")
        return False
    
    print("\n" + "=" * 50)
    
    # Add tickers to the system (as manual tickers)
    print("Adding tickers to the system...")
    if not scraper.add_tickers(tickers, is_scheduled=False, group_name="manual_request"):
        print("ERROR: Failed to add tickers")
        return False
    
    print("\n" + "=" * 50)
    
    # Trigger manual scrape
    print("Triggering manual scrape...")
    if not scraper.manual_scrape_tickers(tickers, wait_for_completion=True):
        print("ERROR: Manual scrape failed")
        return False
    
    print("\n" + "=" * 50)
    
    # Get scraped data
    print("Fetching scraped data...")
    all_data = scraper.get_all_data()
    
    if not all_data:
        print("ERROR: No data available")
        return False
    
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
        return False
    
    # Save to CSV
    print("Saving data to CSV...")
    success = scraper.save_to_csv(filtered_data, output_file)
    
    if success:
        print(f"\nSUCCESS: Scraping completed for {', '.join(tickers)}")
        print(f"Results saved to: {output_file}")
        return True
    else:
        print(f"\nERROR: Failed to save data for {', '.join(tickers)}")
        return False

def get_current_data(output_file: str = "current_cagr.csv"):
    """Get current data and save to CSV"""
    print("Getting Current CAGR Data")
    print("=" * 50)
    
    # Initialize scraper
    scraper = EnhancedManualCAGRScraper()
    
    # Check API health
    if not scraper.check_api_health():
        print("ERROR: API is not healthy, cannot proceed")
        return False
    
    # Get all data
    all_data = scraper.get_all_data()
    
    if not all_data:
        print("ERROR: No data available")
        return False
    
    # Save to CSV
    success = scraper.save_to_csv(all_data, output_file)
    
    if success:
        print(f"\nSUCCESS: Current data saved to {output_file}")
        return True
    else:
        print(f"\nERROR: Failed to save current data")
        return False

def main():
    """Main function"""
    print("Enhanced Manual CAGR Scraping Script")
    print("=" * 50)
    
    # Define tickers to scrape
    target_tickers = ["AAPL", "MSFT", "TSLA", "META"]
    
    print(f"Target tickers: {', '.join(target_tickers)}")
    print("\nOptions:")
    print("1. Scrape custom tickers (AAPL, MSFT, TSLA, META)")
    print("2. Get current data")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        scrape_custom_tickers(target_tickers)
    elif choice == "2":
        get_current_data()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "custom":
            # Scrape custom tickers: python enhanced_manual_requests.py custom
            target_tickers = ["AAPL", "MSFT", "TSLA", "META"]
            scrape_custom_tickers(target_tickers)
        elif command == "current":
            # Get current data: python enhanced_manual_requests.py current
            get_current_data()
        else:
            print("Usage:")
            print("  python enhanced_manual_requests.py custom    # Scrape AAPL, MSFT, TSLA, META")
            print("  python enhanced_manual_requests.py current  # Get current data")
    else:
        # Interactive mode
        main()

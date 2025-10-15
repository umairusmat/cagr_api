"""
CAGR API Client Script
Fetches CAGR data from the deployed API and exports to CSV
"""

import requests
import pandas as pd
import json
from datetime import datetime
import os

class CAGRAPIClient:
    """Client for interacting with the CAGR API"""
    
    def __init__(self, base_url="https://cagrapi-production.up.railway.app", auth_token="mysecretapitoken123"):
        self.base_url = base_url
        self.auth_token = auth_token
        self.headers = {"X-Auth-Token": auth_token}
    
    def check_health(self):
        """Check API health status"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            return None
    
    def get_all_data(self):
        """Get all CAGR data from the API"""
        try:
            response = requests.get(f"{self.base_url}/data", headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data: {e}")
            return None
    
    def get_ticker_data(self, ticker):
        """Get data for a specific ticker"""
        try:
            response = requests.get(f"{self.base_url}/data/{ticker}", headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch data for {ticker}: {e}")
            return None
    
    def get_tickers(self):
        """Get list of available tickers"""
        try:
            response = requests.get(f"{self.base_url}/tickers", headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch tickers: {e}")
            return None
    
    def trigger_manual_scrape(self):
        """Trigger a manual scrape"""
        try:
            response = requests.post(f"{self.base_url}/scrape/manual", headers=self.headers, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to trigger manual scrape: {e}")
            return None
    
    def export_to_csv(self, filename=None):
        """Export all CAGR data to CSV"""
        print("Checking API health...")
        health = self.check_health()
        if not health:
            print("ERROR: API is not healthy")
            return False
        
        print(f"SUCCESS: API Status: {health['status']}")
        print(f"Data Available: {health['data']['available']}")
        print(f"Total Tickers: {health['data']['total_tickers']}")
        print(f"Last Scrape: {health['data']['last_scrape']}")
        
        print("\nFetching CAGR data...")
        data_response = self.get_all_data()
        if not data_response or not data_response.get('success'):
            print("ERROR: Failed to fetch data")
            return False
        
        data = data_response['data']
        print(f"SUCCESS: Fetched data for {len(data)} tickers")
        
        # Convert to wide format where each ticker is a row and years are columns
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
        
        df = pd.DataFrame(rows)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cagr_data_{timestamp}.csv"
        
        # Ensure we're saving in the api_calls directory
        if not os.path.dirname(filename):
            filename = os.path.join("api_calls", filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Save to CSV
        df.to_csv(filename, index=False)
        print(f"SUCCESS: Data exported to: {filename}")
        print(f"Total tickers: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        # Show year columns (excluding Ticker and Last_Updated)
        year_columns = [col for col in df.columns if col not in ['Ticker', 'Last_Updated']]
        if year_columns:
            print(f"Year range: {min(year_columns)} - {max(year_columns)}")
        
        return True

def main():
    """Main function to run the API client"""
    print("CAGR API Client")
    print("=" * 50)
    
    # Initialize client
    client = CAGRAPIClient()
    
    # Export data to CSV
    success = client.export_to_csv()
    
    if success:
        print("\nSUCCESS: Successfully exported CAGR data to CSV!")
        
        # Show sample data
        print("\nSample Data:")
        try:
            import glob
            csv_files = glob.glob("api_calls/cagr_data_*.csv")
            if csv_files:
                # Get the most recent CSV file
                latest_file = max(csv_files, key=os.path.getctime)
                df = pd.read_csv(latest_file)
                print(df.to_string(index=False))
        except Exception as e:
            print(f"Could not display sample data: {e}")
    else:
        print("\nERROR: Failed to export data")

if __name__ == "__main__":
    main()

"""
Test the fixed scraper with all tickers
"""

import sys
import os
import logging
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cagr_scraper_firefox import CAGRScraperFirefox

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_all_tickers():
    """Test the scraper with all tickers"""
    print("Testing CAGR Scraper with All Tickers")
    print("=" * 50)
    
    # Initialize scraper (headless=False for debugging)
    scraper = CAGRScraperFirefox(headless=False)
    
    try:
        # Test with all tickers
        tickers = ["MELI", "SE", "FOUR", "HIMS"]
        
        for ticker in tickers:
            print(f"\nTesting ticker: {ticker}")
            print("-" * 30)
            
            # Scrape the ticker
            result = scraper.scrape_ticker(ticker)
            
            print(f"Success: {result['success']}")
            print(f"Data: {result['data']}")
            
            if result['success']:
                # Check if we got percentage values
                has_percentages = any('%' in str(value) for value in result['data'].values())
                print(f"Contains percentage values: {has_percentages}")
                
                if has_percentages:
                    print("SUCCESS: Found percentage values!")
                    # Show the data in a nice format
                    print("CAGR Data:")
                    for year, value in result['data'].items():
                        print(f"  {year}: {value}")
                else:
                    print("WARNING: No percentage values found!")
            else:
                print("FAILED: Scraping failed")
            
            print()
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"ERROR: {e}")
    
    finally:
        # Clean up
        scraper.close()
        print("Scraper closed.")

if __name__ == "__main__":
    test_all_tickers()

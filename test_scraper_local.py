"""
Test CAGR scraper locally to debug and fix the scraping logic
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

def test_scraper():
    """Test the scraper locally"""
    print("Testing CAGR Scraper Locally")
    print("=" * 50)
    
    # Initialize scraper (headless=False for debugging)
    scraper = CAGRScraperFirefox(headless=False)
    
    try:
        # Test with a single ticker first
        test_ticker = "MELI"
        print(f"Testing with ticker: {test_ticker}")
        
        # Scrape the ticker
        result = scraper.scrape_ticker(test_ticker)
        
        print(f"\nScraping Result:")
        print(f"Success: {result['success']}")
        print(f"Ticker: {result['ticker']}")
        print(f"Data: {result['data']}")
        print(f"Scraped At: {result['scraped_at']}")
        
        if result['success']:
            print("\nData Analysis:")
            for year, value in result['data'].items():
                print(f"  {year}: {value}")
            
            # Check if we got percentage values
            has_percentages = any('%' in str(value) for value in result['data'].values())
            print(f"\nContains percentage values: {has_percentages}")
            
            if not has_percentages:
                print("WARNING: No percentage values found!")
                print("The scraper is likely getting button labels instead of actual CAGR values.")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"ERROR: {e}")
    
    finally:
        # Clean up
        scraper.close()
        print("\nScraper closed.")

if __name__ == "__main__":
    test_scraper()

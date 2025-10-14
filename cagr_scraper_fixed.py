"""
Fixed CAGR scraper that properly extracts percentage values
"""

import time
import logging
import pandas as pd
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager
import sqlite3
from datetime import datetime
import json
import platform
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CAGRScraperFixed:
    """Fixed CAGR scraper that properly extracts percentage values"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.base_url = "https://stockunlock.com/stockDetails/{}/analyst"
        
    def _init_driver(self):
        """Initialize Firefox driver"""
        try:
            options = FirefoxOptions()
            if self.headless:
                options.add_argument('--headless')
            
            # Essential options for stability
            options.set_preference("dom.webnotifications.enabled", False)
            options.set_preference("dom.push.enabled", False)
            options.set_preference("browser.cache.disk.enable", False)
            options.set_preference("browser.cache.memory.enable", True)
            
            # Use webdriver-manager for geckodriver
            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
            
            # Set reasonable timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            logger.info("Firefox driver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Firefox driver: {e}")
            return False
    
    def _wait_for_element(self, by: By, value: str, timeout: int = 10) -> Optional[Any]:
        """Wait for element with timeout"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            return None
    
    def scrape_ticker(self, ticker: str) -> Dict[str, Any]:
        """Scrape CAGR data for a single ticker with proper percentage extraction"""
        if not self.driver:
            if not self._init_driver():
                return self._empty_result(ticker)
        
        try:
            # Navigate to the ticker's analyst page
            url = self.base_url.format(ticker)
            logger.info(f"Scraping {ticker} from {url}")
            
            self.driver.get(url)
            time.sleep(5)  # Let page load
            
            # Scroll down to ensure content loads
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(3)
            
            # Click the CAGR button
            cagr_button = self._wait_for_element(
                By.CSS_SELECTOR, 
                "button[value='cagr']",
                timeout=15
            )
            
            if cagr_button:
                logger.info(f"CAGR button found for {ticker}, clicking...")
                self.driver.execute_script("arguments[0].click();", cagr_button)
                time.sleep(5)  # Wait for data to load
                logger.info(f"CAGR button clicked for {ticker}")
            else:
                logger.warning(f"CAGR button not found for {ticker}")
                return self._empty_result(ticker)
            
            # Wait for the CAGR table to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
                )
                logger.info(f"Table found for {ticker}")
            except TimeoutException:
                logger.warning(f"Table not found for {ticker}")
                return self._empty_result(ticker)
            
            # Find the CAGR table with percentage values
            # Look for table rows that contain percentage values
            table_rows = self.driver.find_elements(By.CSS_SELECTOR, "tr")
            
            cagr_data = {}
            years = []
            
            # First, find the year headers
            for row in table_rows:
                year_cells = row.find_elements(By.CSS_SELECTOR, "th")
                if year_cells:
                    for cell in year_cells:
                        text = cell.text.strip()
                        if text.isdigit() and len(text) == 4:
                            years.append(text)
                    if years:
                        break
            
            logger.info(f"Found years: {years}")
            
            # Now look for the row with percentage values
            for row in table_rows:
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                if len(cells) >= len(years):
                    # Check if this row contains percentage values
                    row_text = " ".join([cell.text.strip() for cell in cells])
                    if '%' in row_text:
                        logger.info(f"Found row with percentages: {row_text}")
                        
                        # Extract values for each year
                        for i, year in enumerate(years):
                            if i < len(cells):
                                value = cells[i].text.strip()
                                if value and value != '':
                                    cagr_data[year] = value
                                else:
                                    cagr_data[year] = 'N/A'
                            else:
                                cagr_data[year] = 'N/A'
                        break
            
            # If no percentage row found, try alternative approach
            if not cagr_data:
                logger.info("No percentage row found, trying alternative approach...")
                
                # Look for spans with percentage values
                percentage_spans = self.driver.find_elements(
                    By.XPATH, 
                    "//span[contains(text(), '%')]"
                )
                
                if percentage_spans:
                    logger.info(f"Found {len(percentage_spans)} percentage spans")
                    
                    # Try to map them to years
                    for i, year in enumerate(years):
                        if i < len(percentage_spans):
                            cagr_data[year] = percentage_spans[i].text.strip()
                        else:
                            cagr_data[year] = 'N/A'
            
            if not cagr_data:
                logger.warning(f"No CAGR data found for {ticker}")
                return self._empty_result(ticker)
            
            logger.info(f"Scraped CAGR data for {ticker}: {cagr_data}")
            
            return {
                'ticker': ticker,
                'data': cagr_data,
                'scraped_at': datetime.now().isoformat(),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error scraping {ticker}: {e}")
            return self._empty_result(ticker)
    
    def _empty_result(self, ticker: str) -> Dict[str, Any]:
        """Return empty result for failed scraping"""
        return {
            'ticker': ticker,
            'data': {},
            'scraped_at': datetime.now().isoformat(),
            'success': False
        }
    
    def scrape_multiple(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple tickers"""
        results = []
        
        for i, ticker in enumerate(tickers):
            logger.info(f"Scraping {ticker} ({i+1}/{len(tickers)})")
            result = self.scrape_ticker(ticker)
            results.append(result)
            
            # Small delay between requests
            time.sleep(2)
        
        return results
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Firefox driver closed successfully")

def test_scraper():
    """Test the fixed scraper"""
    print("Testing Fixed CAGR Scraper")
    print("=" * 50)
    
    # Initialize scraper (headless=False for debugging)
    scraper = CAGRScraperFixed(headless=False)
    
    try:
        # Test with a single ticker
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
            
            if has_percentages:
                print("SUCCESS: Found percentage values!")
            else:
                print("WARNING: No percentage values found!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"ERROR: {e}")
    
    finally:
        # Clean up
        scraper.close()
        print("\nScraper closed.")

if __name__ == "__main__":
    test_scraper()

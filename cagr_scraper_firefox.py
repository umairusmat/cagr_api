"""
CAGR Scraper using Firefox (more reliable on Windows)
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CAGRScraperFirefox:
    """CAGR scraper using Firefox (more reliable on Windows)"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.base_url = "https://stockunlock.com/stockDetails/{}/analyst"
        
    def _init_driver(self):
        """Initialize Firefox driver with Railway/Linux compatibility"""
        try:
            import platform
            import os
            
            options = FirefoxOptions()
            if self.headless:
                options.add_argument('--headless')
            
            # Essential options for stability
            options.set_preference("dom.webnotifications.enabled", False)
            options.set_preference("dom.push.enabled", False)
            options.set_preference("browser.cache.disk.enable", False)
            options.set_preference("browser.cache.memory.enable", True)
            options.set_preference("network.http.pipelining", True)
            options.set_preference("network.http.connection-timeout", 30)
            options.set_preference("network.http.connection-retry-timeout", 10)
            
            # Railway/Linux specific configuration
            if platform.system() == "Linux":
                # Railway/Linux environment - use firefox-esr (more stable)
                firefox_binary = os.environ.get('FIREFOX_BINARY_PATH', '/usr/bin/firefox-esr')
                options.binary_location = firefox_binary
                logger.info(f"Using Firefox-ESR at {firefox_binary} for Linux/Railway environment")
                
                # Additional Railway-specific options for stability
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-plugins')
                options.add_argument('--disable-images')
                options.add_argument('--disable-javascript')
                options.add_argument('--disable-web-security')
                options.add_argument('--allow-running-insecure-content')
                options.add_argument('--disable-features=VizDisplayCompositor')
                
                # Try to use system geckodriver first
                geckodriver_path = os.environ.get('GECKODRIVER_PATH')
                if not geckodriver_path:
                    geckodriver_paths = [
                        "/usr/local/bin/geckodriver",
                        "/usr/bin/geckodriver", 
                        "/opt/geckodriver/geckodriver"
                    ]
                    
                    for path in geckodriver_paths:
                        if os.path.exists(path):
                            geckodriver_path = path
                            break
                
                if geckodriver_path and os.path.exists(geckodriver_path):
                    service = FirefoxService(geckodriver_path)
                    logger.info(f"Using system geckodriver at {geckodriver_path}")
                else:
                    # Fallback to webdriver-manager
                    service = FirefoxService(GeckoDriverManager().install())
                    logger.info("Using webdriver-manager for geckodriver")
            else:
                # Windows/macOS - use webdriver-manager
                service = FirefoxService(GeckoDriverManager().install())
                logger.info("Using webdriver-manager for Windows/macOS")
            
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
            logger.warning(f"Element not found: {value}")
            return None
    
    def scrape_ticker(self, ticker: str) -> Dict[str, Any]:
        """Scrape CAGR data for a single ticker"""
        if not self.driver:
            if not self._init_driver():
                return self._empty_result(ticker)
        
        try:
            # Navigate to the ticker's analyst page
            url = self.base_url.format(ticker)
            logger.info(f"Scraping {ticker} from {url}")
            
            self.driver.get(url)
            time.sleep(5)  # Increased wait time for Railway
            
            # Log page title and URL for debugging
            logger.info(f"Page loaded: {self.driver.title}")
            logger.info(f"Current URL: {self.driver.current_url}")
            
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
                time.sleep(5)  # Increased wait time for data to load
                logger.info(f"CAGR button clicked for {ticker}")
            else:
                logger.warning(f"CAGR button not found for {ticker}")
                # Log page source for debugging
                try:
                    page_source = self.driver.page_source
                    logger.info(f"Page source length: {len(page_source)}")
                    if "cagr" in page_source.lower():
                        logger.info("CAGR text found in page source")
                    else:
                        logger.warning("CAGR text not found in page source")
                except Exception as e:
                    logger.error(f"Error checking page source: {e}")
                return self._empty_result(ticker)
            
            # Find year headers
            year_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "th.MuiTableCell-root.MuiTableCell-head span.MuiTypography-root"
            )
            
            years = []
            for element in year_elements:
                text = element.text.strip()
                if text.isdigit() and len(text) == 4:
                    years.append(text)
            
            if not years:
                logger.warning(f"No years found for {ticker}")
                return self._empty_result(ticker)
            
            # Find the first table (Revenue CAGR) - look for unique years
            unique_years = []
            seen_years = set()
            for year in years:
                if year not in seen_years:
                    unique_years.append(year)
                    seen_years.add(year)
                else:
                    break  # Stop at first duplicate (end of first table)
            
            logger.info(f"Found years for {ticker}: {unique_years}")
            
            # Find all value spans
            value_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                "span.MuiTypography-root.MuiTypography-body1"
            )
            
            values = [elem.text.strip() for elem in value_elements if elem.text.strip()]
            
            if not values:
                logger.warning(f"No values found for {ticker}")
                return self._empty_result(ticker)
            
            # Find the "Avg" row (usually the second row of values)
            avg_values = {}
            values_per_row = len(unique_years)
            
            # Look for the middle row (Avg) - typically at index values_per_row
            if len(values) >= values_per_row * 2:
                avg_start_idx = values_per_row  # Second row
                for i, year in enumerate(unique_years):
                    if avg_start_idx + i < len(values):
                        avg_values[year] = values[avg_start_idx + i]
                    else:
                        avg_values[year] = 'N/A'
            else:
                # Fallback: use first available values
                for i, year in enumerate(unique_years):
                    if i < len(values):
                        avg_values[year] = values[i]
                    else:
                        avg_values[year] = 'N/A'
            
            logger.info(f"Scraped data for {ticker}: {avg_values}")
            
            return {
                'ticker': ticker,
                'data': avg_values,
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
            try:
                self.driver.quit()
                logger.info("Firefox driver closed successfully")
            except Exception as e:
                logger.error(f"Error closing Firefox driver: {e}")

# Database class (same as before)
class CAGRDatabase:
    """Simple database operations for CAGR data"""
    
    def __init__(self, db_path: str = "cagr_data.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create CAGR data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cagr_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                year TEXT NOT NULL,
                value TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, year)
            )
        ''')
        
        # Check if scraped_at column exists, if not add it
        cursor.execute("PRAGMA table_info(cagr_data)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'scraped_at' not in columns:
            cursor.execute('ALTER TABLE cagr_data ADD COLUMN scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def save_scraped_data(self, results: List[Dict[str, Any]]) -> int:
        """Save scraped data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        successful = 0
        failed = 0
        
        for result in results:
            ticker = result['ticker']
            data = result.get('data', {})
            scraped_at = result.get('scraped_at', datetime.now().isoformat())
            
            if result.get('success', False) and data:
                # Delete existing data for this ticker
                cursor.execute('DELETE FROM cagr_data WHERE ticker = ?', (ticker,))
                
                # Insert new data
                for year, value in data.items():
                    cursor.execute('''
                        INSERT OR REPLACE INTO cagr_data (ticker, year, value, scraped_at)
                        VALUES (?, ?, ?, ?)
                    ''', (ticker, year, value, scraped_at))
                
                successful += 1
                logger.info(f"Saved data for {ticker}")
            else:
                failed += 1
                logger.warning(f"No data saved for {ticker}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Saved {successful} successful, {failed} failed tickers")
        return successful
    
    def get_all_data(self) -> List[Dict[str, Any]]:
        """Get all CAGR data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ticker, year, value, scraped_at 
            FROM cagr_data 
            ORDER BY ticker, year
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Group by ticker
        data_by_ticker = {}
        for row in rows:
            ticker, year, value, scraped_at = row
            if ticker not in data_by_ticker:
                data_by_ticker[ticker] = {
                    'ticker': ticker,
                    'data': {},
                    'last_updated': scraped_at
                }
            data_by_ticker[ticker]['data'][year] = value
        
        return list(data_by_ticker.values())
    
    def get_ticker_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get data for specific ticker"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT year, value, scraped_at 
            FROM cagr_data 
            WHERE ticker = ?
            ORDER BY year
        ''', (ticker,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return None
        
        data = {'ticker': ticker, 'data': {}, 'last_updated': rows[0][2]}
        for row in rows:
            year, value, scraped_at = row
            data['data'][year] = value
        
        return data
    
    def get_freshness_info(self) -> Dict[str, Any]:
        """Get data freshness information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT ticker) as total_tickers,
                MAX(scraped_at) as last_scrape,
                MIN(scraped_at) as first_scrape
            FROM cagr_data
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] > 0:
            return {
                'total_tickers': row[0],
                'last_scrape': row[1],
                'first_scrape': row[2],
                'data_available': True
            }
        else:
            return {
                'total_tickers': 0,
                'last_scrape': None,
                'first_scrape': None,
                'data_available': False
            }

def load_tickers(file_path: str = "input/tickers.csv") -> List[str]:
    """Load tickers from CSV file"""
    try:
        df = pd.read_csv(file_path)
        tickers = df['Ticker'].tolist()
        logger.info(f"Loaded {len(tickers)} tickers from {file_path}")
        return tickers
    except Exception as e:
        logger.error(f"Error loading tickers: {e}")
        return []

if __name__ == "__main__":
    # Test the scraper
    scraper = CAGRScraperFirefox(headless=True)
    db = CAGRDatabase()
    
    # Load tickers
    tickers = load_tickers()
    if not tickers:
        logger.error("No tickers found")
        exit(1)
    
    # Scrape data
    logger.info(f"Starting to scrape {len(tickers)} tickers")
    results = scraper.scrape_multiple(tickers)
    
    # Save to database
    successful = db.save_scraped_data(results)
    logger.info(f"Scraping completed: {successful} successful")
    
    # Close scraper
    scraper.close()

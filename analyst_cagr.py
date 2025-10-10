import json
import logging
import time
import pandas as pd
import streamlit as st
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, StaleElementReferenceException,
    WebDriverException, SessionNotCreatedException, ElementClickInterceptedException
)
import threading
import queue
import gc
import os

# Python version compatibility check (relaxed for development)
if sys.version_info < (3, 8):
    raise RuntimeError(f"This application requires Python 3.8 or higher. Current version: {sys.version}")

# Configure logging for Streamlit
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class StreamlitProgress:
    """Progress tracking for Streamlit"""
    def __init__(self, total_items: int, title: str = "Processing"):
        self.total_items = total_items
        self.current_item = 0
        self.title = title
        self.progress_bar = None
        self.status_text = None
        
    def start(self):
        """Initialize progress bar"""
        if st.session_state.get('progress_bar') is None:
            st.session_state.progress_bar = st.progress(0)
            st.session_state.status_text = st.empty()
    
    def update(self, current: int, status: str = ""):
        """Update progress"""
        if st.session_state.get('progress_bar') is not None:
            progress = current / self.total_items
            st.session_state.progress_bar.progress(progress)
            if st.session_state.get('status_text') is not None:
                st.session_state.status_text.text(f"{status} ({current}/{self.total_items})")
    
    def complete(self):
        """Mark as complete"""
        if st.session_state.get('progress_bar') is not None:
            st.session_state.progress_bar.progress(1.0)
            if st.session_state.get('status_text') is not None:
                st.session_state.status_text.text("✅ Processing complete!")

class RobustCAGRScraper:
    """Enhanced CAGR Scraper with robust error handling and Streamlit integration"""
    
    def __init__(self, config: Dict[str, Any], progress_callback=None):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.progress_callback = progress_callback
        self.driver = None
        self.wait = None
        self.base_url = "https://stockunlock.com/stockDetails/{}/analyst"
        self.session_attempts = 0
        self.max_session_attempts = 3
        self._initialize_driver()
        
    def _initialize_driver(self):
        """Initialize WebDriver with enhanced error handling"""
        browser = self.config['webdriver']['browser'].lower()
        headless = self.config['webdriver']['headless']
        
        try:
            if browser == 'firefox':
                options = FirefoxOptions()
                if headless:
                    options.add_argument('--headless')

                # Set Firefox binary path dynamically
                import platform
                if platform.system() == "Linux":
                    # Streamlit Cloud environment - use firefox-esr
                    options.binary_location = "/usr/bin/firefox-esr"
                    print("Using Firefox-ESR for Linux/Streamlit Cloud")
                elif platform.system() == "Windows":
                    # Windows environment - let Selenium find Firefox automatically
                    print("Using system Firefox for Windows")
                    pass
                else:
                    # macOS or other systems
                    print("Using system Firefox for macOS/other")
                    pass

                # Enhanced performance optimizations
                options.set_preference("dom.webnotifications.enabled", False)
                options.set_preference("dom.push.enabled", False)
                options.set_preference("browser.cache.disk.enable", False)
                options.set_preference("browser.cache.memory.enable", True)
                options.set_preference("browser.cache.offline.enable", False)
                options.set_preference("network.http.pipelining", True)
                options.set_preference("network.http.proxy.pipelining", True)
                
                # Network settings for stability
                options.set_preference("network.http.connection-timeout", 45)
                options.set_preference("network.http.connection-retry-timeout", 20)
                options.set_preference("network.http.max-connections", 128)
                options.set_preference("network.http.max-persistent-connections-per-server", 4)
                options.set_preference("network.http.max-connections-per-server", 16)
                
                # Additional connection stability
                options.set_preference("network.http.connection-retry-delay", 2)
                options.set_preference("network.http.connection-retry-timeout", 20)
                options.set_preference("network.http.max-pipelined-requests", 4)
                
                # Memory management for long sessions
                options.set_preference("browser.cache.memory.capacity", 65536)
                options.set_preference("browser.cache.memory.max_entry_size", 8192)
                options.set_preference("browser.cache.disk.capacity", 131072)
                options.set_preference("browser.cache.disk.max_entry_size", 16384)
                
                # Additional stability settings
                options.set_preference("browser.tabs.remote.autostart", False)
                options.set_preference("browser.tabs.remote.autostart.2", False)
                options.set_preference("browser.sessionstore.resume_from_crash", False)
                options.set_preference("browser.sessionstore.max_tabs_undo", 0)
                options.set_preference("browser.sessionhistory.max_entries", 5)
                
                # Memory management
                options.set_preference("browser.sessionstore.interval", 120000)
                options.set_preference("memory.free_dirty_pages", True)
                options.set_preference("javascript.options.mem.max", 1024 * 1024 * 1024)  # 1GB
                
                # Additional stability
                options.set_preference("browser.download.folderList", 2)
                options.set_preference("browser.download.manager.showWhenStarting", False)
                options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
                
                # Use GeckoDriver installed by setup.sh
                try:
                    # Try /usr/local/bin/geckodriver first (installed by setup.sh)
                    service = FirefoxService("/usr/local/bin/geckodriver")
                    self.driver = webdriver.Firefox(service=service, options=options)
                    print("Using GeckoDriver from /usr/local/bin/geckodriver")
                except:
                    try:
                        # Try system-installed geckodriver
                        service = FirefoxService("/usr/bin/geckodriver")
                        self.driver = webdriver.Firefox(service=service, options=options)
                        print("Using GeckoDriver from /usr/bin/geckodriver")
                    except:
                        try:
                            # Try local bin directory
                            service = FirefoxService("~/.local/bin/geckodriver")
                            self.driver = webdriver.Firefox(service=service, options=options)
                            print("Using GeckoDriver from ~/.local/bin/geckodriver")
                        except:
                            # Fallback to webdriver-manager
                            print("Falling back to webdriver-manager for GeckoDriver")
                            service = FirefoxService(GeckoDriverManager().install())
                            self.driver = webdriver.Firefox(service=service, options=options)
                
                # Set timeouts
                self.driver.set_page_load_timeout(60)
                self.driver.set_script_timeout(30)
                self.driver.implicitly_wait(10)
                
                # Set window size
                self.driver.set_window_size(1920, 1080)
                
                self.wait = WebDriverWait(self.driver, 10, poll_frequency=0.5)
                self.logger.info("Firefox WebDriver initialized with enhanced settings")
                
            elif browser == 'chrome':
                options = ChromeOptions()
                if headless:
                    options.add_argument('--headless=new')
                
                # Enhanced performance optimizations
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-notifications')
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-software-rasterizer')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-infobars')
                options.add_argument('--disable-popup-blocking')
                options.add_argument('--disable-background-timer-throttling')
                options.add_argument('--disable-backgrounding-occluded-windows')
                options.add_argument('--disable-renderer-backgrounding')
                
                # Memory and performance settings
                options.add_argument('--js-flags="--max-old-space-size=1024"')
                options.add_argument('--memory-pressure-off')
                options.add_argument('--disable-features=RendererCodeIntegrity')
                
                # Network settings
                options.add_argument('--dns-prefetch-disable')
                options.add_argument('--disable-features=NetworkService')
                options.add_argument('--disable-features=VizDisplayCompositor')
                
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                
                # Set timeouts and window size
                self.driver.set_page_load_timeout(120)
                self.driver.set_script_timeout(60)
                self.driver.implicitly_wait(15)
                self.driver.set_window_size(1920, 1080)
                
                self.wait = WebDriverWait(self.driver, 10, poll_frequency=0.5)
                return
                
            else:
                raise ValueError(f"Unsupported browser: {browser}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            raise

    def _retry_with_session_refresh(self, func, *args, **kwargs):
        """Retry function with session refresh on failure"""
        max_retries = self.config['scraping'].get('retry_attempts', 3)
        retry_delay = self.config['scraping'].get('retry_delay', 2)
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except (WebDriverException, SessionNotCreatedException) as e:
                self.logger.warning(f"Session error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    self._refresh_session()
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    raise
            except Exception as e:
                self.logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise

    def _refresh_session(self):
        """Refresh the browser session"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
        
        time.sleep(2)  # Allow time for cleanup
        self._initialize_driver()

    def wait_for_element(self, by, value, timeout=10, condition=EC.presence_of_element_located):
        """Enhanced wait for element with better error handling"""
        start_time = time.time()
        last_exception = None
        
        while time.time() - start_time < timeout:
            try:
                element = WebDriverWait(self.driver, timeout/4, poll_frequency=0.5).until(
                    condition((by, value))
                )
                if element and element.is_displayed():
                    return element
            except StaleElementReferenceException:
                continue  # Retry immediately for stale elements
            except TimeoutException as e:
                last_exception = e
                time.sleep(0.5)  # Shorter pause before retry
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Unexpected error waiting for element {value}: {str(e)}")
                time.sleep(0.5)
        
        if last_exception:
            self.logger.error(f"Timeout waiting for element: {value}")
        return None

    def get_data(self, ticker: str) -> Dict[str, Any]:
        """Get CAGR data for a given ticker with enhanced error handling"""
        start_time = time.time()
        
        if not ticker:
            self.logger.error("No ticker provided")
            return self._get_empty_result(ticker)

        try:
            # Navigate to analyst page
            url = self.base_url.format(ticker)
            self.logger.info(f"Accessing URL: {url}")
            
            # Use retry mechanism for page loading
            def load_page():
                self.driver.get(url)
                # Wait for page load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            
            self._retry_with_session_refresh(load_page)
            
            # Scroll down to load content
            scroll_pixels = self.config['scraping']['scroll_pixels']
            self.driver.execute_script(f"window.scrollBy(0, {scroll_pixels});")
            
            # Wait for content to load
            time.sleep(1)
            
            try:
                # Click CAGR button with explicit wait and retry
                def click_cagr_button():
                    cagr_button = self.wait_for_element(
                        By.CSS_SELECTOR, 
                        "button.MuiButtonBase-root.MuiToggleButtonGroup-grouped.MuiToggleButtonGroup-lastButton[value='cagr']",
                        timeout=10,
                        condition=EC.element_to_be_clickable
                    )
                    if cagr_button:
                        self.driver.execute_script("arguments[0].click();", cagr_button)
                        time.sleep(1)  # Reduced wait time
                    else:
                        raise Exception("CAGR button not found")
                
                self._retry_with_session_refresh(click_cagr_button)
                
                # Get all years from both tables
                year_cells = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "th.MuiTableCell-root.MuiTableCell-head.MuiTableCell-alignLeft span.MuiTypography-root.MuiTypography-body1"
                )
                all_years = [cell.text.strip() for cell in year_cells if cell.text.strip().isdigit()]
                self.logger.info(f"Found years: {all_years}")
                
                if not all_years:
                    self.logger.warning(f"No years found for {ticker}")
                    return self._get_empty_result(ticker)
                
                # Find where years start repeating to determine first table width
                table_width = 0
                for i, year in enumerate(all_years):
                    if year in all_years[:i]:
                        table_width = i
                        break
                
                # Get years from first table only (Revenue CAGR table)
                revenue_years = all_years[:table_width] if table_width > 0 else all_years
                self.logger.info(f"Revenue years: {revenue_years}")
                
                # Get all values with retry
                def get_values():
                    value_spans = self.driver.find_elements(
                        By.CSS_SELECTOR, 
                        "span.MuiTypography-root.MuiTypography-body1.css-1r92pvx"
                    )
                    return [span.text.strip() for span in value_spans]
                
                all_values = self._retry_with_session_refresh(get_values)
                self.logger.info(f"All values found: {all_values}")
                
                if not all_values:
                    self.logger.warning(f"No values found for {ticker}")
                    return self._get_empty_result(ticker)
                
                # Split values into rows based on number of years
                values_per_row = len(revenue_years)
                
                # Get row type from config
                row_type = self.config['scraping']['row_type']
                self.logger.info(f"Using row type: {row_type}")
                
                # Map row types to their indices
                row_indices = {'Low': 0, 'Avg': 1, 'High': 2}
                row_index = row_indices.get(row_type, 1)  # Default to Avg
                start_idx = row_index * values_per_row
                
                # Create result dictionary with years as keys and values
                avg_dict = {}
                for i, year in enumerate(revenue_years):
                    value_idx = start_idx + i
                    if value_idx < len(all_values):
                        avg_dict[year] = all_values[value_idx]
                    else:
                        avg_dict[year] = 'N/A'
                
                elapsed_time = time.time() - start_time
                self.logger.info(f"Scraping CAGR for {ticker} took {elapsed_time:.2f} seconds")
                
                return {
                    'ticker': ticker,
                    'avg_values': avg_dict,
                    'elapsed_time': elapsed_time
                }
                
            except Exception as e:
                self.logger.error(f"Error processing data for {ticker}: {str(e)}")
                return self._get_empty_result(ticker)
                
        except Exception as e:
            self.logger.error(f"Error fetching data for {ticker}: {str(e)}")
            return self._get_empty_result(ticker)

    def _get_empty_result(self, ticker: str) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            'ticker': ticker,
            'avg_values': {},
            'elapsed_time': 0
        }

    def save_data(self, results: List[Dict[str, Any]]) -> None:
        """Save the scraped data to CSV"""
        try:
            # Create output directory if it doesn't exist
            output_dir = Path(self.config['data']['output']['directory'])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Get output file path
            output_file = output_dir / self.config['data']['output']['analyst_cagr_csv']
            
            # Convert results to DataFrame with years as columns
            data = []
            for result in results:
                if result['avg_values']:  # Only include results with data
                    row = {'ticker': result['ticker']}
                    row.update(result['avg_values'])
                    data.append(row)
            
            if data:
                df = pd.DataFrame(data)
                
                # Sort columns in sequential order
                year_columns = [col for col in df.columns if col != 'ticker']
                sorted_years = sorted(year_columns, key=lambda x: int(x))
                column_order = ['ticker'] + sorted_years
                
                # Reorder columns and save to CSV
                df = df[column_order]
                df.to_csv(output_file, index=False)
                self.logger.info(f"Data saved to {output_file}")
            else:
                self.logger.warning("No data to save")
            
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")

    def safe_quit(self):
        """Safely quit the browser"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.error(f"Error closing browser: {str(e)}")

    def __del__(self):
        """Cleanup method"""
        self.safe_quit()

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file {config_path} not found")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing configuration file: {e}")
        raise

def process_tickers(tickers: List[str], config: Dict[str, Any], 
                   progress_callback=None) -> List[Dict[str, Any]]:
    """Process tickers without session refresh to avoid GitHub API rate limiting"""
    all_results = []
    
    # Create a single scraper instance for all tickers
    scraper = None
    try:
        scraper = RobustCAGRScraper(config, progress_callback)
        
        for i, ticker in enumerate(tickers):
            if progress_callback:
                progress_callback(i + 1, f"Processing {ticker}")
            
            try:
                result = scraper.get_data(ticker)
                all_results.append(result)
                
            except Exception as e:
                logging.error(f"Error processing {ticker}: {str(e)}")
                all_results.append({
                    'ticker': ticker,
                    'avg_values': {},
                    'elapsed_time': 0
                })
            
            # Add delay between requests
            time.sleep(0.8)
            
            # Force garbage collection periodically
            if (i + 1) % 50 == 0:
                gc.collect()
        
        logging.info(f"Successfully processed {len(tickers)} tickers")
        
    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
        # Add empty results for remaining tickers
        for ticker in tickers[len(all_results):]:
            all_results.append({
                'ticker': ticker,
                'avg_values': {},
                'elapsed_time': 0
            })
    finally:
        if scraper:
            try:
                scraper.safe_quit()
            except:
                pass
    
    return all_results

# Keep the old function for backward compatibility but mark as deprecated
def process_tickers_batch(tickers: List[str], config: Dict[str, Any], 
                          progress_callback=None, batch_size: int = 20) -> List[Dict[str, Any]]:
    """DEPRECATED: Use process_tickers instead to avoid GitHub API rate limiting"""
    logging.warning("process_tickers_batch is deprecated. Use process_tickers instead.")
    return process_tickers(tickers, config, progress_callback)

def main():
    """Main function to run the scraper"""
    try:
        # Load configuration
        config = load_config()
        
        # Read tickers from CSV file
        try:
            df = pd.read_csv('tickers.csv')
            tickers = df['Ticker'].tolist()
            print(f"Found {len(tickers)} tickers in tickers.csv")
        except Exception as e:
            print(f"Error reading tickers.csv: {e}")
            return

        # Process tickers
        results = process_tickers(tickers, config)
        
        # Save results
        scraper = RobustCAGRScraper(config)
        scraper.save_data(results)
        scraper.safe_quit()
        
        print(f"\nScraping completed. Processed {len(results)} tickers.")
        
    except Exception as e:
        logging.error(f"Error in main function: {str(e)}")
        raise

if __name__ == "__main__":
    main() 
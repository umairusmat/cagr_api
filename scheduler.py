"""
Background Scheduler for CAGR Scraping
Handles automatic scraping at configurable intervals
"""

import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import json

from cagr_scraper import CAGRScraper, CAGRDatabase, load_tickers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CAGRScrapingScheduler:
    """Background scheduler for CAGR scraping"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.scheduler = BackgroundScheduler()
        self.scraper = None
        self.db = CAGRDatabase()
        self.is_running = False
        self.last_scrape_time = None
        self.scraping_in_progress = False
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return {
                "scraping": {
                    "frequency_hours": 6,
                    "enabled": True,
                    "headless": True
                }
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config: {e}")
            return {"scraping": {"frequency_hours": 6, "enabled": True, "headless": True}}
    
    def _scrape_job(self):
        """Main scraping job"""
        if self.scraping_in_progress:
            logger.warning("Scraping already in progress, skipping this run")
            return
        
        self.scraping_in_progress = True
        start_time = datetime.now()
        
        try:
            logger.info("Starting scheduled CAGR scraping")
            
            # Load tickers
            tickers = load_tickers()
            if not tickers:
                logger.error("No tickers found, skipping scrape")
                return
            
            # Initialize scraper
            headless = self.config.get('scraping', {}).get('headless', True)
            self.scraper = CAGRScraper(headless=headless)
            
            # Scrape data
            results = self.scraper.scrape_multiple(tickers)
            
            # Save to database
            successful = self.db.save_scraped_data(results)
            
            # Update last scrape time
            self.last_scrape_time = datetime.now()
            
            elapsed = (self.last_scrape_time - start_time).total_seconds()
            logger.info(f"Scraping completed: {successful} successful in {elapsed:.1f}s")
            
        except Exception as e:
            logger.error(f"Error in scraping job: {e}")
        finally:
            # Clean up scraper
            if self.scraper:
                try:
                    self.scraper.close()
                except:
                    pass
                self.scraper = None
            
            self.scraping_in_progress = False
    
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        scraping_config = self.config.get('scraping', {})
        
        if not scraping_config.get('enabled', True):
            logger.info("Scraping is disabled in config")
            return
        
        frequency_hours = scraping_config.get('frequency_hours', 6)
        
        # Add the scraping job
        self.scheduler.add_job(
            func=self._scrape_job,
            trigger=IntervalTrigger(hours=frequency_hours),
            id='cagr_scraping',
            name='CAGR Scraping Job',
            replace_existing=True
        )
        
        # Start the scheduler
        self.scheduler.start()
        self.is_running = True
        
        logger.info(f"Scheduler started - scraping every {frequency_hours} hours")
        
        # Run initial scrape
        logger.info("Running initial scrape...")
        self._scrape_job()
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Scheduler stopped")
    
    def run_manual_scrape(self) -> Dict[str, Any]:
        """Run a manual scrape"""
        if self.scraping_in_progress:
            return {
                'success': False,
                'message': 'Scraping already in progress',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            logger.info("Starting manual scrape")
            self._scrape_job()
            
            return {
                'success': True,
                'message': 'Manual scrape completed',
                'timestamp': datetime.now().isoformat(),
                'last_scrape': self.last_scrape_time.isoformat() if self.last_scrape_time else None
            }
        except Exception as e:
            logger.error(f"Error in manual scrape: {e}")
            return {
                'success': False,
                'message': f'Manual scrape failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            'is_running': self.is_running,
            'scraping_in_progress': self.scraping_in_progress,
            'last_scrape_time': self.last_scrape_time.isoformat() if self.last_scrape_time else None,
            'next_scrape': self._get_next_scrape_time(),
            'config': self.config.get('scraping', {})
        }
    
    def _get_next_scrape_time(self) -> Optional[str]:
        """Get next scheduled scrape time"""
        if not self.is_running:
            return None
        
        try:
            job = self.scheduler.get_job('cagr_scraping')
            if job and job.next_run_time:
                return job.next_run_time.isoformat()
        except:
            pass
        
        return None
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration and restart scheduler if needed"""
        self.config.update(new_config)
        
        if self.is_running:
            logger.info("Restarting scheduler with new config")
            self.stop_scheduler()
            time.sleep(1)
            self.start_scheduler()

# Global scheduler instance
_scheduler_instance: Optional[CAGRScrapingScheduler] = None

def get_scheduler() -> CAGRScrapingScheduler:
    """Get global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = CAGRScrapingScheduler()
    return _scheduler_instance

def start_background_scheduler():
    """Start the background scheduler (for use in main app)"""
    scheduler = get_scheduler()
    scheduler.start_scheduler()
    return scheduler

def stop_background_scheduler():
    """Stop the background scheduler"""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop_scheduler()
        _scheduler_instance = None

if __name__ == "__main__":
    # Test the scheduler
    scheduler = CAGRScrapingScheduler()
    
    try:
        scheduler.start_scheduler()
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.stop_scheduler()
        logger.info("Scheduler stopped")
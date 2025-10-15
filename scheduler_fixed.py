"""
Background scheduler for automatic CAGR data scraping
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import json
import os
from pathlib import Path

from cagr_scraper_firefox import CAGRScraperFirefox, CAGRDatabase, load_tickers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CAGRBackgroundScheduler:
    """Background scheduler for automatic CAGR scraping"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db = CAGRDatabase()
        self.scraper = None
        self.is_running = False
        self.scrape_task = None
        
        # Get scraping configuration
        scraping_config = config.get('scraping', {})
        self.frequency_hours = scraping_config.get('frequency_hours', 6)
        self.enabled = scraping_config.get('enabled', True)
        self.headless = scraping_config.get('headless', True)
        
        logger.info(f"Scheduler initialized: frequency={self.frequency_hours}h, enabled={self.enabled}")
    
    async def start(self):
        """Start the background scheduler"""
        if not self.enabled:
            logger.info("Scheduler is disabled in configuration")
            return
        
        self.is_running = True
        logger.info(f"Starting background scheduler with {self.frequency_hours}h frequency")
        
        # Start the background task
        self.scrape_task = asyncio.create_task(self._scrape_loop())
        
    async def stop(self):
        """Stop the background scheduler"""
        self.is_running = False
        if self.scrape_task:
            self.scrape_task.cancel()
            try:
                await self.scrape_task
            except asyncio.CancelledError:
                pass
        
        if self.scraper:
            self.scraper.close()
        
        logger.info("Background scheduler stopped")
    
    async def _scrape_loop(self):
        """Main scraping loop"""
        while self.is_running:
            try:
                # Calculate next scrape time
                next_scrape = datetime.now() + timedelta(hours=self.frequency_hours)
                logger.info(f"Next scheduled scrape: {next_scrape}")
                
                # Wait for the scheduled time
                await asyncio.sleep(self.frequency_hours * 3600)  # Convert hours to seconds
                
                if not self.is_running:
                    break
                
                # Perform the scrape
                await self._perform_scrape()
                
            except asyncio.CancelledError:
                logger.info("Scrape loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in scrape loop: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(300)  # 5 minutes
    
    async def _perform_scrape(self):
        """Perform a scheduled scrape"""
        logger.info("Starting scheduled scrape...")
        
        try:
            # Load tickers
            tickers = load_tickers()
            if not tickers:
                logger.warning("No tickers found for scheduled scrape")
                return
            
            logger.info(f"Scraping {len(tickers)} tickers")
            
            # Initialize scraper
            self.scraper = CAGRScraperFirefox(headless=self.headless)
            
            try:
                # Scrape data
                results = self.scraper.scrape_multiple(tickers)
                
                # Save to database
                successful = self.db.save_scraped_data(results)
                logger.info(f"Scheduled scrape completed: {successful} successful")
                
            finally:
                # Clean up scraper
                if self.scraper:
                    self.scraper.close()
                    self.scraper = None
                    
        except Exception as e:
            logger.error(f"Error in scheduled scrape: {e}")
    
    async def trigger_manual_scrape(self):
        """Trigger a manual scrape immediately"""
        logger.info("Triggering manual scrape...")
        await self._perform_scrape()

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_path} not found, creating default")
        default_config = {
            "scraping": {
                "frequency_hours": 6,
                "enabled": True,
                "headless": True
            },
            "api": {
                "auth_token": "mysecretapitoken123",
                "host": "0.0.0.0",
                "port": 8000
            },
            "database": {
                "url": "sqlite:///cagr_data.db"
            }
        }
        
        # Save default config
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info(f"Created default config at {config_path}")
        return default_config
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing config: {e}")
        raise

# Global scheduler instance
scheduler = None

async def get_scheduler():
    """Get or create the global scheduler instance"""
    global scheduler
    if scheduler is None:
        config = load_config()
        scheduler = CAGRBackgroundScheduler(config)
    return scheduler

async def start_scheduler():
    """Start the background scheduler"""
    global scheduler
    if scheduler is None:
        config = load_config()
        scheduler = CAGRBackgroundScheduler(config)
    
    await scheduler.start()

async def stop_scheduler():
    """Stop the background scheduler"""
    global scheduler
    if scheduler:
        await scheduler.stop()

async def trigger_manual_scrape():
    """Trigger a manual scrape"""
    global scheduler
    if scheduler:
        await scheduler.trigger_manual_scrape()
    else:
        # Create temporary scheduler for manual scrape
        config = load_config()
        temp_scheduler = CAGRBackgroundScheduler(config)
        await temp_scheduler.trigger_manual_scrape()
        await temp_scheduler.stop()

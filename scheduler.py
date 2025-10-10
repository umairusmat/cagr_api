import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
from pathlib import Path

from models import get_session, CAGRData, ScrapeSession, ScrapeJob
from analyst_cagr import RobustCAGRScraper, load_config
from data_service import DataService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CAGRScrapingScheduler:
    """Scheduler for automatic CAGR data scraping"""
    
    def __init__(self):
        self.config = load_config()
        self.data_service = DataService()
        self.is_running = False
        self.scheduler_thread = None
        self.frequency_hours = self.config.get('scraping', {}).get('frequency_hours', 6)
        
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
            
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        logger.info(f"Scheduler started with {self.frequency_hours} hour intervals")
        
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Scheduler stopped")
        
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                # Calculate next run time
                next_run = datetime.now() + timedelta(hours=self.frequency_hours)
                logger.info(f"Next scheduled scrape at: {next_run}")
                
                # Wait until next run time
                while self.is_running and datetime.now() < next_run:
                    time.sleep(60)  # Check every minute
                    
                if self.is_running:
                    logger.info("Starting scheduled scrape...")
                    self.run_scheduled_scrape()
                    
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
                
    def run_scheduled_scrape(self):
        """Run a scheduled scraping session"""
        session_id = self._create_scrape_session("scheduled")
        
        try:
            # Get tickers from CSV
            tickers = self._load_tickers()
            if not tickers:
                logger.warning("No tickers found in input/tickers.csv")
                return
                
            logger.info(f"Starting scheduled scrape for {len(tickers)} tickers")
            
            # Update session with total tickers
            self._update_session(session_id, total_tickers=len(tickers))
            
            # Run scraping
            results = self._scrape_tickers(tickers, session_id)
            
            # Update session with results
            successful = len([r for r in results if r.get('avg_values')])
            failed = len(tickers) - successful
            self._update_session(session_id, 
                               successful_tickers=successful,
                               failed_tickers=failed,
                               status="completed")
            
            logger.info(f"Scheduled scrape completed: {successful} successful, {failed} failed")
            
        except Exception as e:
            logger.error(f"Error in scheduled scrape: {e}")
            self._update_session(session_id, status="failed")
            
    def run_manual_scrape(self) -> Dict[str, Any]:
        """Run a manual scraping session"""
        session_id = self._create_scrape_session("manual")
        
        try:
            # Get tickers from CSV
            tickers = self._load_tickers()
            if not tickers:
                return {"error": "No tickers found in input/tickers.csv"}
                
            logger.info(f"Starting manual scrape for {len(tickers)} tickers")
            
            # Update session with total tickers
            self._update_session(session_id, total_tickers=len(tickers))
            
            # Run scraping
            results = self._scrape_tickers(tickers, session_id)
            
            # Update session with results
            successful = len([r for r in results if r.get('avg_values')])
            failed = len(tickers) - successful
            self._update_session(session_id, 
                               successful_tickers=successful,
                               failed_tickers=failed,
                               status="completed")
            
            return {
                "session_id": session_id,
                "total_tickers": len(tickers),
                "successful": successful,
                "failed": failed,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in manual scrape: {e}")
            self._update_session(session_id, status="failed")
            return {"error": str(e), "session_id": session_id}
            
    def _load_tickers(self) -> List[str]:
        """Load tickers from CSV file"""
        try:
            ticker_file = Path("input/tickers.csv")
            if not ticker_file.exists():
                logger.error("input/tickers.csv not found")
                return []
                
            df = pd.read_csv(ticker_file)
            if 'Ticker' not in df.columns:
                logger.error("'Ticker' column not found in input/tickers.csv")
                return []
                
            tickers = df['Ticker'].dropna().astype(str).tolist()
            return [ticker.strip().upper() for ticker in tickers if ticker.strip()]
            
        except Exception as e:
            logger.error(f"Error loading tickers: {e}")
            return []
            
    def _scrape_tickers(self, tickers: List[str], session_id: int) -> List[Dict[str, Any]]:
        """Scrape CAGR data for given tickers"""
        scraper = None
        results = []
        
        try:
            scraper = RobustCAGRScraper(self.config)
            
            for i, ticker in enumerate(tickers):
                try:
                    logger.info(f"Scraping {ticker} ({i+1}/{len(tickers)})")
                    
                    # Create job record
                    job_id = self._create_scrape_job(ticker, session_id)
                    
                    # Scrape data
                    result = scraper.get_data(ticker)
                    results.append(result)
                    
                    # Save to database
                    if result.get('avg_values'):
                        self.data_service.save_cagr_data(ticker, result['avg_values'])
                        self._update_job(job_id, "completed", result)
                    else:
                        self._update_job(job_id, "failed", result, "No data found")
                        
                    # Add delay between requests
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error scraping {ticker}: {e}")
                    results.append({
                        'ticker': ticker,
                        'avg_values': {},
                        'elapsed_time': 0
                    })
                    self._update_job(job_id, "failed", {}, str(e))
                    
        finally:
            if scraper:
                scraper.safe_quit()
                
        return results
        
    def _create_scrape_session(self, session_type: str) -> int:
        """Create a new scraping session"""
        with get_session() as session:
            scrape_session = ScrapeSession(session_type=session_type)
            session.add(scrape_session)
            session.commit()
            return scrape_session.id
            
    def _update_session(self, session_id: int, **kwargs):
        """Update scraping session"""
        with get_session() as session:
            scrape_session = session.query(ScrapeSession).get(session_id)
            if scrape_session:
                for key, value in kwargs.items():
                    setattr(scrape_session, key, value)
                if kwargs.get('status') in ['completed', 'failed']:
                    scrape_session.completed_at = datetime.now()
                session.commit()
                
    def _create_scrape_job(self, ticker: str, session_id: int) -> int:
        """Create a new scraping job"""
        with get_session() as session:
            job = ScrapeJob(ticker=ticker, status="running")
            session.add(job)
            session.commit()
            return job.id
            
    def _update_job(self, job_id: int, status: str, result: Dict = None, error_message: str = None):
        """Update scraping job"""
        with get_session() as session:
            job = session.query(ScrapeJob).get(job_id)
            if job:
                job.status = status
                if result:
                    job.result = str(result)
                if error_message:
                    job.error_message = error_message
                if status in ['completed', 'failed']:
                    job.completed_at = datetime.now()
                session.commit()
                
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            "is_running": self.is_running,
            "frequency_hours": self.frequency_hours,
            "next_run": datetime.now() + timedelta(hours=self.frequency_hours) if self.is_running else None
        }
        
    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent scraping sessions"""
        with get_session() as session:
            sessions = session.query(ScrapeSession).order_by(ScrapeSession.started_at.desc()).limit(limit).all()
            return [
                {
                    "id": s.id,
                    "type": s.session_type,
                    "status": s.status,
                    "total_tickers": s.total_tickers,
                    "successful_tickers": s.successful_tickers,
                    "failed_tickers": s.failed_tickers,
                    "started_at": s.started_at.isoformat() if s.started_at else None,
                    "completed_at": s.completed_at.isoformat() if s.completed_at else None
                }
                for s in sessions
            ]

# Global scheduler instance
scheduler = CAGRScrapingScheduler()

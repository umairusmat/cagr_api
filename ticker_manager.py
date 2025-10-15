"""
Dynamic Ticker Management System
Manages tickers in SQLite database instead of CSV file
"""

import sqlite3
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TickerManager:
    """Manages tickers in SQLite database"""
    
    def __init__(self, db_path: str = "cagr_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize ticker management tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create tickers table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tickers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticker TEXT UNIQUE NOT NULL,
                        is_scheduled BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create ticker_groups table for categorization
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ticker_groups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_name TEXT NOT NULL,
                        ticker TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (ticker) REFERENCES tickers (ticker)
                    )
                """)
                
                conn.commit()
                logger.info("Ticker management database initialized")
                
        except Exception as e:
            logger.error(f"Error initializing ticker database: {e}")
            raise
    
    def add_ticker(self, ticker: str, is_scheduled: bool = True, group_name: str = "default") -> bool:
        """Add a new ticker to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert ticker
                cursor.execute("""
                    INSERT OR REPLACE INTO tickers (ticker, is_scheduled, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (ticker.upper(), is_scheduled))
                
                # Add to group
                cursor.execute("""
                    INSERT OR REPLACE INTO ticker_groups (group_name, ticker)
                    VALUES (?, ?)
                """, (group_name, ticker.upper()))
                
                conn.commit()
                logger.info(f"Added ticker {ticker} to group {group_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error adding ticker {ticker}: {e}")
            return False
    
    def remove_ticker(self, ticker: str) -> bool:
        """Remove a ticker from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Remove from groups first
                cursor.execute("DELETE FROM ticker_groups WHERE ticker = ?", (ticker.upper(),))
                
                # Remove ticker
                cursor.execute("DELETE FROM tickers WHERE ticker = ?", (ticker.upper(),))
                
                conn.commit()
                logger.info(f"Removed ticker {ticker}")
                return True
                
        except Exception as e:
            logger.error(f"Error removing ticker {ticker}: {e}")
            return False
    
    def get_scheduled_tickers(self) -> List[str]:
        """Get all tickers that are scheduled for scraping"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ticker FROM tickers WHERE is_scheduled = 1")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting scheduled tickers: {e}")
            return []
    
    def get_all_tickers(self) -> List[str]:
        """Get all tickers in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT ticker FROM tickers")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all tickers: {e}")
            return []
    
    def get_tickers_by_group(self, group_name: str) -> List[str]:
        """Get tickers by group"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT t.ticker FROM tickers t
                    JOIN ticker_groups tg ON t.ticker = tg.ticker
                    WHERE tg.group_name = ?
                """, (group_name,))
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting tickers by group {group_name}: {e}")
            return []
    
    def update_ticker_schedule(self, ticker: str, is_scheduled: bool) -> bool:
        """Update whether a ticker is scheduled for scraping"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tickers 
                    SET is_scheduled = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE ticker = ?
                """, (is_scheduled, ticker.upper()))
                
                conn.commit()
                logger.info(f"Updated ticker {ticker} schedule status to {is_scheduled}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating ticker {ticker} schedule: {e}")
            return False
    
    def get_ticker_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a ticker"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT ticker, is_scheduled, created_at, updated_at
                    FROM tickers WHERE ticker = ?
                """, (ticker.upper(),))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'ticker': row[0],
                        'is_scheduled': bool(row[1]),
                        'created_at': row[2],
                        'updated_at': row[3]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting ticker info for {ticker}: {e}")
            return None
    
    def get_all_ticker_info(self) -> List[Dict[str, Any]]:
        """Get information about all tickers"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT t.ticker, t.is_scheduled, t.created_at, t.updated_at,
                           GROUP_CONCAT(tg.group_name) as groups
                    FROM tickers t
                    LEFT JOIN ticker_groups tg ON t.ticker = tg.ticker
                    GROUP BY t.ticker, t.is_scheduled, t.created_at, t.updated_at
                    ORDER BY t.ticker
                """)
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'ticker': row[0],
                        'is_scheduled': bool(row[1]),
                        'created_at': row[2],
                        'updated_at': row[3],
                        'groups': row[4].split(',') if row[4] else []
                    })
                return results
                
        except Exception as e:
            logger.error(f"Error getting all ticker info: {e}")
            return []
    
    def load_from_csv(self, csv_path: str = "input/tickers.csv") -> bool:
        """Load initial tickers from CSV file"""
        try:
            import csv
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ticker = row['ticker'].strip()
                    if ticker:
                        self.add_ticker(ticker, is_scheduled=True, group_name="csv_import")
            
            logger.info(f"Loaded tickers from {csv_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading tickers from CSV: {e}")
            return False

# Global ticker manager instance
ticker_manager = TickerManager()

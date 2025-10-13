import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from models import get_session, CAGRData, ScrapeSession

logger = logging.getLogger(__name__)

class DataService:
    """Service for managing CAGR data operations"""
    
    def __init__(self):
        self.session_factory = get_session
        
    def save_cagr_data(self, ticker: str, avg_values: Dict[str, str]) -> bool:
        """Save CAGR data for a ticker"""
        try:
            with self.session_factory() as session:
                # Delete existing data for this ticker
                session.query(CAGRData).filter(CAGRData.ticker == ticker.upper()).delete()
                
                # Insert new data
                for year, value in avg_values.items():
                    cagr_data = CAGRData(
                        ticker=ticker.upper(),
                        year=str(year),
                        value=str(value) if value else None
                    )
                    session.add(cagr_data)
                
                session.commit()
                logger.info(f"Saved CAGR data for {ticker}: {len(avg_values)} years")
                return True
                
        except Exception as e:
            logger.error(f"Error saving CAGR data for {ticker}: {e}")
            return False
            
    def get_cagr_data(self, ticker: str = None) -> List[Dict[str, Any]]:
        """Get CAGR data for a specific ticker or all tickers"""
        try:
            with self.session_factory() as session:
                query = session.query(CAGRData)
                
                if ticker:
                    query = query.filter(CAGRData.ticker == ticker.upper())
                    
                # Get latest data for each ticker/year combination
                latest_data = query.order_by(
                    CAGRData.ticker, 
                    CAGRData.year, 
                    desc(CAGRData.updated_at)
                ).all()
                
                # Group by ticker
                result = {}
                for data in latest_data:
                    if data.ticker not in result:
                        result[data.ticker] = {
                            'ticker': data.ticker,
                            'data': {},
                            'last_updated': data.updated_at.isoformat()
                        }
                    result[data.ticker]['data'][data.year] = data.value
                
                return list(result.values())
                
        except Exception as e:
            logger.error(f"Error getting CAGR data: {e}")
            return []
            
    def get_cagr_data_formatted(self, ticker: str = None) -> Dict[str, Any]:
        """Get CAGR data in a formatted structure for API responses"""
        try:
            data = self.get_cagr_data(ticker)
            
            if not data:
                return {"tickers": [], "data": {}}
                
            # Convert to the format expected by the API
            result = {
                "tickers": [item['ticker'] for item in data],
                "data": {}
            }
            
            for item in data:
                result["data"][item['ticker']] = {
                    "values": item['data'],
                    "last_updated": item['last_updated']
                }
                
            return result
            
        except Exception as e:
            logger.error(f"Error formatting CAGR data: {e}")
            return {"tickers": [], "data": {}}
            
    def get_ticker_list(self) -> List[str]:
        """Get list of all available tickers"""
        try:
            with self.session_factory() as session:
                tickers = session.query(CAGRData.ticker).distinct().all()
                return [ticker[0] for ticker in tickers]
                
        except Exception as e:
            logger.error(f"Error getting ticker list: {e}")
            return []
            
    def get_data_freshness(self) -> Dict[str, Any]:
        """Get information about data freshness"""
        try:
            with self.session_factory() as session:
                # Get latest update time
                latest_update = session.query(CAGRData.updated_at).order_by(
                    desc(CAGRData.updated_at)
                ).first()
                
                if not latest_update:
                    return {
                        "has_data": False,
                        "latest_update": None,
                        "ticker_count": 0
                    }
                    
                latest_time = latest_update[0]
                now = datetime.now()
                hours_since_update = (now - latest_time).total_seconds() / 3600
                
                # Count unique tickers
                ticker_count = session.query(CAGRData.ticker).distinct().count()
                
                return {
                    "has_data": True,
                    "latest_update": latest_time.isoformat(),
                    "hours_since_update": round(hours_since_update, 2),
                    "ticker_count": ticker_count,
                    "is_fresh": hours_since_update < 12  # Consider fresh if less than 12 hours old
                }
                
        except Exception as e:
            logger.error(f"Error getting data freshness: {e}")
            return {
                "has_data": False,
                "latest_update": None,
                "ticker_count": 0
            }
            
    def delete_old_data(self, days_old: int = 30) -> int:
        """Delete data older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            with self.session_factory() as session:
                deleted_count = session.query(CAGRData).filter(
                    CAGRData.updated_at < cutoff_date
                ).delete()
                
                session.commit()
                logger.info(f"Deleted {deleted_count} old CAGR data records")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error deleting old data: {e}")
            return 0
            
    def get_data_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored data"""
        try:
            with self.session_factory() as session:
                # Total records
                total_records = session.query(CAGRData).count()
                
                # Unique tickers
                unique_tickers = session.query(CAGRData.ticker).distinct().count()
                
                # Years covered
                unique_years = session.query(CAGRData.year).distinct().count()
                
                # Latest and earliest data
                latest_data = session.query(CAGRData.updated_at).order_by(
                    desc(CAGRData.updated_at)
                ).first()
                
                earliest_data = session.query(CAGRData.updated_at).order_by(
                    CAGRData.updated_at
                ).first()
                
                return {
                    "total_records": total_records,
                    "unique_tickers": unique_tickers,
                    "unique_years": unique_years,
                    "latest_update": latest_data[0].isoformat() if latest_data else None,
                    "earliest_update": earliest_data[0].isoformat() if earliest_data else None
                }
                
        except Exception as e:
            logger.error(f"Error getting data statistics: {e}")
            return {}
            
    def search_tickers(self, query: str) -> List[str]:
        """Search for tickers matching the query"""
        try:
            with self.session_factory() as session:
                tickers = session.query(CAGRData.ticker).filter(
                    CAGRData.ticker.ilike(f"%{query.upper()}%")
                ).distinct().all()
                
                return [ticker[0] for ticker in tickers]
                
        except Exception as e:
            logger.error(f"Error searching tickers: {e}")
            return []
    
    def store_data_from_streamlit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store data uploaded from Streamlit app"""
        try:
            tickers_processed = 0
            
            with self.session_factory() as session:
                # Get the data from the request
                streamlit_data = data.get('data', {})
                
                for ticker, ticker_data in streamlit_data.items():
                    try:
                        # Delete existing data for this ticker
                        session.query(CAGRData).filter(CAGRData.ticker == ticker.upper()).delete()
                        
                        # Get values from the ticker data
                        values = ticker_data.get('values', {})
                        
                        # Insert new data
                        for year, value in values.items():
                            cagr_data = CAGRData(
                                ticker=ticker.upper(),
                                year=str(year),
                                value=str(value) if value else None
                            )
                            session.add(cagr_data)
                        
                        tickers_processed += 1
                        logger.info(f"Stored data for {ticker}: {len(values)} years")
                        
                    except Exception as e:
                        logger.error(f"Error storing data for {ticker}: {e}")
                        continue
                
                session.commit()
                logger.info(f"Successfully stored data for {tickers_processed} tickers")
                
                return {
                    "tickers_processed": tickers_processed,
                    "status": "success"
                }
                
        except Exception as e:
            logger.error(f"Error storing data from Streamlit: {e}")
            return {
                "tickers_processed": 0,
                "status": "error",
                "error": str(e)
            }
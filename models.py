import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()

class CAGRData(Base):
    """Model for storing CAGR analyst estimates data"""
    __tablename__ = "cagr_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False, index=True)
    year = Column(String(4), nullable=False)
    value = Column(String(20), nullable=True)  # Store as string to handle 'N/A' values
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<CAGRData(ticker='{self.ticker}', year='{self.year}', value='{self.value}')>"

class ScrapeJob(Base):
    """Model for tracking scraping jobs"""
    __tablename__ = "scrape_jobs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    result = Column(Text)  # JSON string of scraped data
    error_message = Column(Text)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<ScrapeJob(ticker='{self.ticker}', status='{self.status}')>"

class ScrapeSession(Base):
    """Model for tracking scraping sessions"""
    __tablename__ = "scrape_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_type = Column(String(20), nullable=False)  # scheduled, manual
    total_tickers = Column(Integer, default=0)
    successful_tickers = Column(Integer, default=0)
    failed_tickers = Column(Integer, default=0)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    status = Column(String(20), default="running")  # running, completed, failed
    
    def __repr__(self):
        return f"<ScrapeSession(type='{self.session_type}', status='{self.status}')>"

def load_config(config_path: str = "config.json"):
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file {config_path} not found, using defaults")
        return {
            "database": {"url": "sqlite:///cagr_data.db"},
            "api": {"auth_token": "mysecretapitoken123"}
        }
    except json.JSONDecodeError as e:
        print(f"Error parsing configuration file: {e}")
        raise

def get_database_url():
    """Get database URL from config"""
    config = load_config()
    return config.get("database", {}).get("url", "sqlite:///cagr_data.db")

# Initialize database
db_url = get_database_url()
engine = create_engine(db_url)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_session():
    """Get database session"""
    return Session()

def test_connection():
    """Test database connection"""
    try:
        with get_session() as session:
            session.query(CAGRData).first()
        print("Database connected successfully")
        return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    test_connection()
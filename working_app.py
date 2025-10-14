"""
Working CAGR Application with Firefox scraper
"""

import os
import sys
import logging
import signal
import time
from typing import Dict, Any
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

def create_directories():
    """Create necessary directories"""
    directories = ['input', 'output', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")

def check_tickers_file():
    """Check if tickers file exists and create if needed"""
    tickers_file = "input/tickers.csv"
    
    if not Path(tickers_file).exists():
        logger.warning(f"Tickers file {tickers_file} not found, creating sample")
        
        # Create sample tickers file
        sample_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        with open(tickers_file, 'w') as f:
            f.write("Ticker\n")
            for ticker in sample_tickers:
                f.write(f"{ticker}\n")
        
        logger.info(f"Created sample tickers file: {tickers_file}")
    else:
        logger.info(f"Tickers file found: {tickers_file}")

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main application entry point"""
    logger.info("Starting CAGR Application...")
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Create necessary directories
        create_directories()
        
        # Check tickers file
        check_tickers_file()
        
        # Setup signal handlers
        setup_signal_handlers()
        
        # Import and start the API
        from working_api import app
        import uvicorn
        
        # Get API configuration
        api_config = config.get('api', {})
        host = api_config.get('host', '0.0.0.0')
        # Use Railway's PORT environment variable if available
        port = int(os.environ.get('PORT', api_config.get('port', 8000)))
        
        logger.info(f"Starting CAGR API on {host}:{port}")
        logger.info("Application is ready!")
        logger.info("API endpoints available at:")
        logger.info(f"  - Health: http://{host}:{port}/health")
        logger.info(f"  - Data: http://{host}:{port}/data")
        logger.info(f"  - Docs: http://{host}:{port}/docs")
        
        # Start the API server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Error in main application: {e}")
        raise
    finally:
        logger.info("CAGR Application stopped")

if __name__ == "__main__":
    main()


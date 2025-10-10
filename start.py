#!/usr/bin/env python3
"""
Startup script for CAGR API
This script initializes the database and starts the FastAPI server
"""

import sys
import os
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import test_connection, Base, engine
from models import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main startup function"""
    logger.info("Starting CAGR API...")
    
    # Load configuration
    try:
        config = load_config()
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return 1
    
    # Test database connection
    if not test_connection():
        logger.error("Database connection failed")
        return 1
    
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    logger.info("Output directory ready")
    
    # Start the FastAPI server
    try:
        import uvicorn
        host = config.get('api', {}).get('host', '0.0.0.0')
        port = config.get('api', {}).get('port', 8000)
        
        logger.info(f"Starting server on {host}:{port}")
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

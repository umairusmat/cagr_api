"""
Simple health check for Railway deployment
"""

import os
import sys
import time
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_health():
    """Check if the application is healthy"""
    try:
        # Get the port from environment
        port = os.environ.get('PORT', '8000')
        host = '0.0.0.0'
        
        # Try to connect to the health endpoint
        url = f"http://{host}:{port}/health"
        logger.info(f"Checking health at: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            logger.info("Health check passed!")
            return True
        else:
            logger.error(f"Health check failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    # Wait a bit for the app to start
    time.sleep(5)
    
    # Check health
    if check_health():
        logger.info("Application is healthy!")
        sys.exit(0)
    else:
        logger.error("Application is not healthy!")
        sys.exit(1)

"""
Railway startup script with proper port handling
"""

import os
import sys
import logging
from working_app import main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main_startup():
    """Main startup function for Railway"""
    logger.info("Starting CAGR Application for Railway...")
    
    # Set Railway environment variables
    if 'PORT' in os.environ:
        logger.info(f"Railway PORT detected: {os.environ['PORT']}")
    else:
        logger.info("No Railway PORT detected, using default 8000")
    
    # Start virtual display for Firefox
    try:
        import subprocess
        logger.info("Starting virtual display for Firefox...")
        subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x24'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        logger.info("Virtual display started successfully")
    except Exception as e:
        logger.warning(f"Could not start virtual display: {e}")
        logger.info("Continuing without virtual display...")
    
    # Start the main application
    try:
        main()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main_startup()

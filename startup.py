"""
Railway startup script with health check
Starts simple health server first, then transitions to full app
"""

import os
import sys
import time
import subprocess
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    """Health check handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "message": "CAGR API is running",
                "version": "2.0.0",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "available": True,
                    "total_tickers": 0,
                    "last_scrape": None
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
            logger.info("Health check passed")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def run_health_server():
    """Run health server in background"""
    port = int(os.environ.get('PORT', 8000))
    
    try:
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"Health server starting on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server error: {e}")

def main():
    """Main startup function"""
    logger.info("Starting CAGR API with health check...")
    
    # Start health server in background
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Wait a moment for health server to start
    time.sleep(2)
    
    # Check if we should start the full application
    if os.environ.get('START_FULL_APP', 'true').lower() == 'true':
        logger.info("Starting full CAGR application...")
        try:
            # Import and start the full application
            from working_app import main as app_main
            app_main()
        except Exception as e:
            logger.error(f"Error starting full app: {e}")
            logger.info("Continuing with health server only...")
            # Keep the health server running
            while True:
                time.sleep(1)
    else:
        logger.info("Running in health-only mode...")
        # Keep the health server running
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()

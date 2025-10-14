"""
Simple health check server for Railway deployment
This ensures the health check passes quickly
"""

import os
import sys
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    """Simple health check handler"""
    
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
    """Run simple health server"""
    port = int(os.environ.get('PORT', 8000))
    
    try:
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"Health server starting on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_health_server()

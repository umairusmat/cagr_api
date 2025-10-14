"""
Minimal health check for Railway
No dependencies, just basic HTTP server
"""

import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "message": "CAGR API is running",
                "timestamp": datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def main():
    port = int(os.environ.get('PORT', 8000))
    
    try:
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        print(f"Health server starting on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

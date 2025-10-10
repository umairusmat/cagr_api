#!/usr/bin/env python3
"""
Railway startup script for CAGR API
Handles PORT environment variable and starts the FastAPI server
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Start the FastAPI server with Railway configuration"""
    
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"Starting CAGR API on {host}:{port}")
    print(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'development')}")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()

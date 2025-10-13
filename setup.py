"""
Setup script for CAGR API
Creates necessary directories and files
"""

import os
import sys
from pathlib import Path
import json

def create_directories():
    """Create necessary directories"""
    directories = ['input', 'output', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")

def create_sample_tickers():
    """Create sample tickers file if it doesn't exist"""
    tickers_file = "input/tickers.csv"
    
    if not Path(tickers_file).exists():
        sample_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        with open(tickers_file, 'w') as f:
            f.write("Ticker\n")
            for ticker in sample_tickers:
                f.write(f"{ticker}\n")
        print(f"Created sample tickers file: {tickers_file}")
    else:
        print(f"Tickers file already exists: {tickers_file}")

def create_config():
    """Create config file if it doesn't exist"""
    config_file = "config.json"
    
    if not Path(config_file).exists():
        config = {
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
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Created config file: {config_file}")
    else:
        print(f"Config file already exists: {config_file}")

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 13):
        print(f"Warning: Python 3.13+ recommended, current version: {sys.version}")
    else:
        print(f"Python version: {sys.version}")

def main():
    """Main setup function"""
    print("Setting up CAGR API...")
    print()
    
    # Check Python version
    check_python_version()
    print()
    
    # Create directories
    print("Creating directories...")
    create_directories()
    print()
    
    # Create sample files
    print("Creating sample files...")
    create_sample_tickers()
    create_config()
    print()
    
    print("Setup complete!")
    print()
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Edit input/tickers.csv with your stock tickers")
    print("3. Edit config.json if needed")
    print("4. Run the application: python app.py")
    print()
    print("API will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()

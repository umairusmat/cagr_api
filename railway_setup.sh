#!/bin/bash
# Railway setup script for CAGR API - Based on working Streamlit setup
echo "🚀 Setting up CAGR API for Railway deployment..."

# Update package list
apt-get update

# Install Python and pip
echo "Installing Python and pip..."
apt-get install -y python3 python3-pip

# Install Firefox-ESR (more stable on Linux)
echo "Installing Firefox-ESR..."
apt-get install -y firefox-esr

# Install wget, tar, and other dependencies
echo "Installing system dependencies..."
apt-get install -y wget tar libxml2-dev libxslt1-dev

# Install GeckoDriver manually (same as working Streamlit setup)
echo "📦 Installing GeckoDriver for Firefox-ESR..."
GECKODRIVER_VERSION="0.34.0"
GECKODRIVER_URL="https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz"

# Create directory for GeckoDriver
mkdir -p /usr/local/bin

# Download GeckoDriver
wget -O /tmp/geckodriver.tar.gz "$GECKODRIVER_URL"

# Extract and install
tar -xzf /tmp/geckodriver.tar.gz -C /tmp/
chmod +x /tmp/geckodriver
mv /tmp/geckodriver /usr/local/bin/

# Clean up
rm /tmp/geckodriver.tar.gz

# Set Firefox binary path
export FIREFOX_BIN=/usr/bin/firefox-esr

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Create necessary directories
mkdir -p /app/input
mkdir -p /app/output
mkdir -p /app/logs

# Verify installations
echo "✅ Setup completed successfully!"
echo "Firefox path: $(which firefox-esr)"
echo "GeckoDriver path: $(which geckodriver)"
echo "Python version: $(python3 --version)"
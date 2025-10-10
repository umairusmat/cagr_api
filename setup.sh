#!/bin/bash

# Setup script for Streamlit Cloud deployment with Python 3.13.1
echo "🚀 Setting up environment for Python 3.13.1..."

# Install GeckoDriver manually since the package doesn't exist
echo "📦 Installing GeckoDriver for Firefox-ESR..."

# Download and install GeckoDriver
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

echo "✅ Setup completed successfully!"
echo "Firefox path: $(which firefox-esr)"
echo "GeckoDriver path: $(which geckodriver)"
echo "Python version: $(python --version)"

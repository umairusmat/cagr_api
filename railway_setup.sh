#!/bin/bash

# Railway-specific setup script for Firefox and GeckoDriver
echo "🚀 Setting up Railway environment for web scraping..."

# Update package list
apt-get update

# Install Firefox ESR and dependencies
echo "📦 Installing Firefox ESR..."
apt-get install -y firefox-esr wget tar

# Download and install GeckoDriver
echo "📦 Installing GeckoDriver..."
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

# Set environment variables
export FIREFOX_BIN=/usr/bin/firefox-esr
export PATH="/usr/local/bin:$PATH"

echo "✅ Railway setup completed!"
echo "Firefox path: $(which firefox-esr)"
echo "GeckoDriver path: $(which geckodriver)"

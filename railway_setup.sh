#!/bin/bash
# Railway setup script for CAGR API
# Installs Firefox and geckodriver for Linux environment

echo "Setting up CAGR API for Railway deployment..."

# Update package list
apt-get update

# Install Firefox
echo "Installing Firefox..."
apt-get install -y firefox

# Install wget and unzip for geckodriver
apt-get install -y wget unzip

# Download and install geckodriver
echo "Installing geckodriver..."
GECKODRIVER_VERSION="0.34.0"
wget -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz"
tar -xzf /tmp/geckodriver.tar.gz -C /tmp/
mv /tmp/geckodriver /usr/local/bin/geckodriver
chmod +x /usr/local/bin/geckodriver

# Install additional dependencies for Firefox
apt-get install -y \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0

# Create necessary directories
mkdir -p /app/input
mkdir -p /app/output
mkdir -p /app/logs

echo "Railway setup completed successfully!"
echo "Firefox version: $(firefox --version)"
echo "Geckodriver version: $(geckodriver --version)"
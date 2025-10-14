# Use Ubuntu base image
FROM ubuntu:22.04

# Cache bust - force rebuild

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    tar \
    libxml2-dev \
    libxslt1-dev \
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
    libgdk-pixbuf2.0-0 \
    libxss1 \
    libgconf-2-4 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Firefox-ESR directly from Mozilla
RUN FIREFOX_VERSION="115.12.0esr" && \
    wget -O /tmp/firefox-esr.tar.bz2 "https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VERSION}/linux-x86_64/en-US/firefox-${FIREFOX_VERSION}.tar.bz2" && \
    tar -xjf /tmp/firefox-esr.tar.bz2 -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox-esr && \
    rm /tmp/firefox-esr.tar.bz2

# Install GeckoDriver
RUN GECKODRIVER_VERSION="0.34.0" && \
    wget -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz" && \
    tar -xzf /tmp/geckodriver.tar.gz -C /tmp/ && \
    mv /tmp/geckodriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/geckodriver && \
    rm /tmp/geckodriver.tar.gz

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p /app/input /app/output /app/logs

# Set environment variables
ENV FIREFOX_BINARY_PATH=/usr/bin/firefox-esr
ENV GECKODRIVER_PATH=/usr/local/bin/geckodriver
ENV DISPLAY=:99

# Expose port
EXPOSE 8080

# Start the application
CMD ["python3", "startup.py"]

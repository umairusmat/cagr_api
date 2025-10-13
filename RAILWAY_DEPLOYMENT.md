# Railway Deployment Guide for CAGR API

## 🚀 **Railway Deployment with Firefox-ESR**

This guide ensures your CAGR API works perfectly on Railway's Linux environment using Firefox-ESR instead of Chrome.

### 📋 **Prerequisites**

1. **Railway Account** - Sign up at [railway.app](https://railway.app)
2. **Railway CLI** - Install: `npm install -g @railway/cli`
3. **Git Repository** - Your code should be in a Git repo

### 🔧 **Railway Configuration**

The following files are configured for Railway deployment:

#### **1. `railway.json`** - Railway deployment config
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "chmod +x railway_setup.sh && ./railway_setup.sh && pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "python working_app.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### **2. `nixpacks.toml`** - Nixpacks configuration
```toml
[phases.setup]
nixPkgs = ["firefox-esr", "wget", "unzip", "libgtk-3-0", "libdbus-glib-1-2", "libxt6", "libxcomposite1", "libxdamage1", "libxrandr2", "libasound2", "libpangocairo-1.0-0", "libatk1.0-0", "libcairo-gobject2", "libgdk-pixbuf2.0-0"]

[phases.install]
cmds = [
  "chmod +x railway_setup.sh",
  "./railway_setup.sh",
  "pip install -r requirements.txt"
]

[start]
cmd = "python working_app.py"
```

#### **3. `railway_setup.sh`** - Firefox-ESR installation script
- Installs Firefox-ESR
- Downloads and installs geckodriver
- Sets up necessary dependencies

### 🚀 **Deployment Steps**

#### **Step 1: Connect to Railway**
```bash
# Login to Railway
railway login

# Initialize project
railway init
```

#### **Step 2: Set Environment Variables**
```bash
# Set your API token
railway variables set AUTH_TOKEN=your_secret_token_here

# Optional: Set other variables
railway variables set SCRAPING_FREQUENCY_HOURS=6
railway variables set SCRAPING_ENABLED=true
railway variables set SCRAPING_HEADLESS=true
```

#### **Step 3: Deploy**
```bash
# Deploy to Railway
railway up
```

### 🔍 **Railway-Specific Features**

#### **Firefox-ESR Configuration**
- **Binary Path**: `/usr/bin/firefox-esr`
- **Geckodriver Path**: `/usr/local/bin/geckodriver`
- **Headless Mode**: Enabled by default
- **Memory Optimization**: Configured for Railway's environment

#### **Environment Variables**
- `FIREFOX_BINARY_PATH` - Firefox-ESR binary location
- `GECKODRIVER_PATH` - Geckodriver location
- `AUTH_TOKEN` - API authentication token
- `SCRAPING_FREQUENCY_HOURS` - Scraping frequency
- `SCRAPING_ENABLED` - Enable/disable scraping
- `SCRAPING_HEADLESS` - Headless mode

### 📊 **Monitoring & Health Checks**

#### **Health Endpoint**
- **URL**: `https://your-app.railway.app/health`
- **Purpose**: Check API status and data availability

#### **Manual Scraping**
```bash
curl -X POST \
  -H "X-Auth-Token: your_secret_token" \
  https://your-app.railway.app/scrape/manual
```

#### **Get Data**
```bash
curl -H "X-Auth-Token: your_secret_token" \
  https://your-app.railway.app/data
```

### 🛠 **Troubleshooting**

#### **Common Issues**

1. **Firefox-ESR Not Found**
   - Check if `railway_setup.sh` ran successfully
   - Verify Firefox-ESR installation in build logs

2. **Geckodriver Issues**
   - Ensure geckodriver is in `/usr/local/bin/geckodriver`
   - Check file permissions: `chmod +x /usr/local/bin/geckodriver`

3. **Memory Issues**
   - Railway has memory limits
   - Firefox-ESR is more memory-efficient than Chrome
   - Headless mode reduces memory usage

#### **Debug Commands**
```bash
# Check Railway logs
railway logs

# Check environment variables
railway variables

# Restart service
railway redeploy
```

### 📈 **Performance Optimization**

#### **Railway-Specific Settings**
- **Headless Mode**: Always enabled
- **Memory Management**: Optimized for Railway's limits
- **Connection Timeouts**: Configured for Railway's network
- **Resource Cleanup**: Automatic driver cleanup

#### **Scraping Configuration**
- **Frequency**: 6 hours (configurable)
- **Timeout**: 30 seconds per page
- **Retry Logic**: Built-in error handling
- **Resource Management**: Automatic cleanup

### 🎯 **Production Checklist**

- [ ] **Environment Variables Set**
  - [ ] `AUTH_TOKEN` configured
  - [ ] `SCRAPING_FREQUENCY_HOURS` set
  - [ ] `SCRAPING_ENABLED=true`

- [ ] **Firefox-ESR Setup**
  - [ ] `railway_setup.sh` executed
  - [ ] Firefox-ESR installed
  - [ ] Geckodriver installed

- [ ] **API Testing**
  - [ ] Health endpoint working
  - [ ] Manual scraping working
  - [ ] Data retrieval working

- [ ] **Monitoring**
  - [ ] Health checks configured
  - [ ] Logs accessible
  - [ ] Error handling working

### 🚀 **Deployment Commands**

```bash
# Complete deployment workflow
railway login
railway init
railway variables set AUTH_TOKEN=your_secret_token
railway up

# Check deployment status
railway status

# View logs
railway logs

# Test API
curl https://your-app.railway.app/health
```

### 📝 **Notes**

- **Firefox-ESR** is more stable on Railway than Chrome
- **System geckodriver** is preferred over webdriver-manager
- **Headless mode** is required for Railway deployment
- **Memory optimization** is crucial for Railway's limits
- **Environment variables** provide flexibility for configuration

Your CAGR API is now ready for Railway deployment with Firefox-ESR! 🎉

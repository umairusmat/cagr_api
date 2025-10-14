# 🚀 Production Setup Guide

## ✅ **Deployment Successful!**

Your CAGR API is now live on Railway! Here's how to complete the production setup:

## 🔧 **Step 1: Set Environment Variables**

### **Using Railway CLI:**
```bash
# Install Railway CLI (if not already installed)
npm install -g @railway/cli

# Login to Railway
railway login

# Set your API authentication token
railway variables set AUTH_TOKEN=your_secret_token_here

# Set scraping configuration
railway variables set SCRAPING_FREQUENCY_HOURS=6
railway variables set SCRAPING_ENABLED=true
railway variables set SCRAPING_HEADLESS=true
```

### **Using Railway Dashboard:**
1. Go to [railway.app](https://railway.app)
2. Select your project
3. Go to "Variables" tab
4. Add these variables:
   - `AUTH_TOKEN` = `your_secret_token_here`
   - `SCRAPING_FREQUENCY_HOURS` = `6`
   - `SCRAPING_ENABLED` = `true`
   - `SCRAPING_HEADLESS` = `true`

## 🌐 **Step 2: Get Your API URL**

### **Find Your URL:**
```bash
# Get your deployment URL
railway domain
```

Your API will be available at: `https://your-app-name.railway.app`

## 🧪 **Step 3: Test Your API**

### **Health Check (No Auth Required):**
```bash
curl https://your-app-name.railway.app/health
```

### **API Endpoints (Auth Required):**
```bash
# Get all data
curl -H "X-Auth-Token: your_secret_token_here" \
  https://your-app-name.railway.app/data

# Get specific ticker data
curl -H "X-Auth-Token: your_secret_token_here" \
  https://your-app-name.railway.app/data/AAPL

# Manual scraping
curl -X POST -H "X-Auth-Token: your_secret_token_here" \
  https://your-app-name.railway.app/scrape/manual

# Get data freshness
curl -H "X-Auth-Token: your_secret_token_here" \
  https://your-app-name.railway.app/data/freshness

# Get data statistics
curl -H "X-Auth-Token: your_secret_token_here" \
  https://your-app-name.railway.app/data/statistics
```

## 🔄 **Step 4: Switch to Full Application**

### **Push Full Application:**
```bash
# Add the updated files
git add railway.json Procfile

# Commit the changes
git commit -m "Switch to full CAGR application

- Updated railway.json to use working_app.py
- Updated Procfile to use working_app.py
- Full CAGR API functionality now available"

# Push to deploy full application
git push origin main
```

## 📊 **Step 5: API Documentation**

### **Available Endpoints:**

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/health` | GET | No | Health check |
| `/data` | GET | Yes | All CAGR data |
| `/data/{ticker}` | GET | Yes | Specific ticker data |
| `/data/freshness` | GET | Yes | Data freshness info |
| `/data/statistics` | GET | Yes | Data statistics |
| `/tickers` | GET | Yes | Available tickers |
| `/scrape/manual` | POST | Yes | Trigger manual scrape |

### **Authentication:**
All endpoints (except `/health`) require the `X-Auth-Token` header:
```
X-Auth-Token: your_secret_token_here
```

## 🎯 **Step 6: Production Features**

### **Automatic Scraping:**
- Runs every 6 hours (configurable)
- Scrapes data from StockUnlock
- Stores data in SQLite database
- Updates automatically

### **Manual Scraping:**
- Trigger on-demand scraping
- Useful for immediate data updates
- Returns scraping results

### **Data Access:**
- Get all CAGR data
- Get specific ticker data
- Check data freshness
- View statistics

## 🔒 **Step 7: Security**

### **API Token:**
- Keep your `AUTH_TOKEN` secret
- Use strong, random tokens
- Don't commit tokens to Git

### **Rate Limiting:**
- Built-in delays between requests
- Prevents being blocked by StockUnlock
- Respectful scraping practices

## 🚀 **Step 8: Monitoring**

### **Health Monitoring:**
- Railway automatically monitors your app
- Health checks every 30 seconds
- Automatic restarts on failure

### **Logs:**
```bash
# View Railway logs
railway logs

# View specific service logs
railway logs --service your-service-name
```

## 🎉 **You're Ready!**

Your CAGR API is now:
- ✅ **Deployed on Railway**
- ✅ **Publicly accessible**
- ✅ **Automatically scraping**
- ✅ **Production ready**

**Your API URL:** `https://your-app-name.railway.app`
**Authentication:** `X-Auth-Token: your_secret_token_here`

Start using your API from anywhere! 🚀
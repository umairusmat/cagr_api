# Streamlit Cloud Deployment Guide

## 🚀 Quick Deployment Steps

### 1. Deploy FastAPI Backend First

Before deploying the Streamlit app, you need to deploy your FastAPI backend to a cloud service:

#### Option A: Railway (Recommended)
1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Set environment variables:
   - `AUTH_TOKEN=mysecretapitoken123`
4. Deploy automatically
5. Note the deployed URL (e.g., `https://your-app.railway.app`)

#### Option B: Render
1. Go to [Render.com](https://render.com)
2. Connect your GitHub repository
3. Set environment variables:
   - `AUTH_TOKEN=mysecretapitoken123`
4. Deploy automatically
5. Note the deployed URL (e.g., `https://your-app.onrender.com`)

### 2. Deploy Streamlit App

1. Go to [Streamlit Cloud](https://share.streamlit.io)
2. Connect your GitHub repository
3. Set the following secrets in Streamlit Cloud:

```toml
[api]
API_BASE_URL = "https://your-fastapi-url.railway.app"
AUTH_TOKEN = "mysecretapitoken123"
```

4. Deploy the app

## 🔧 Configuration

### Local Development
- FastAPI runs on `http://localhost:8000`
- Streamlit runs on `http://localhost:8501`
- Use the existing `.streamlit/secrets.toml` file

### Streamlit Cloud Deployment
- Update `API_BASE_URL` in Streamlit Cloud secrets to your deployed FastAPI URL
- Keep the same `AUTH_TOKEN` for consistency

## 📊 What Works

The following features are fully functional:
- ✅ API root endpoint (`/`)
- ✅ Tickers endpoint (`/tickers`)
- ✅ Data endpoints (`/data`, `/data/{ticker}`)
- ✅ Manual scraping (`/scrape/manual`)
- ✅ Scheduler status (`/scheduler/status`)
- ✅ Sessions endpoint (`/sessions`)

## ⚠️ Known Issues

- The `/health` endpoint returns a 500 error (but other endpoints work fine)
- The `/data/freshness` and `/data/statistics` endpoints may have issues with empty database

## 🛠️ Troubleshooting

### If Streamlit shows connection errors:
1. Verify your FastAPI backend is deployed and accessible
2. Check the `API_BASE_URL` in Streamlit Cloud secrets
3. Ensure the `AUTH_TOKEN` matches between FastAPI and Streamlit

### If API endpoints return errors:
1. Check that your FastAPI backend is running
2. Verify the authentication token is correct
3. Test the API endpoints directly using curl or Postman

## 📝 Environment Variables for FastAPI Deployment

When deploying FastAPI, set these environment variables:

```bash
AUTH_TOKEN=mysecretapitoken123
```

## 🔐 Security Notes

- Change the default `AUTH_TOKEN` to a secure random string for production
- Use HTTPS URLs for production deployments
- Consider implementing rate limiting for production use

## 📈 Monitoring

Once deployed, you can monitor:
- API health via the Streamlit interface
- Scraping sessions and data freshness
- Ticker data and statistics
- Manual scraping triggers

## 🆘 Support

If you encounter issues:
1. Check the deployment platform logs
2. Verify all environment variables are set
3. Test API endpoints directly
4. Review the configuration files

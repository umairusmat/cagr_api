# Railway Quick Start - CAGR API

## 🚀 5-Minute Deployment

### 1. Go to Railway
- Visit [railway.app](https://railway.app)
- Sign up with GitHub

### 2. Deploy from GitHub
- Click "Deploy from GitHub repo"
- Select: `umairusmat/cagr_api`
- Click "Deploy Now"

### 3. Set Environment Variable
- Go to Variables tab
- Add: `AUTH_TOKEN=your_secure_token_here`
- Save

### 4. Get Your URL
- Railway will give you: `https://your-app-name.railway.app`
- Test: `curl -H "X-Auth-Token: your_token" https://your-app-name.railway.app/`

### 5. Update Streamlit
- Go to Streamlit Cloud
- Set secrets:
  ```toml
  [api]
  API_BASE_URL = "https://your-app-name.railway.app"
  AUTH_TOKEN = "your_secure_token_here"
  ```

## ✅ Done!
Your FastAPI backend is now live on Railway! 🎉

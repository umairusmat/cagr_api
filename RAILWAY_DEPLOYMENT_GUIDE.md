# Railway.com Deployment Guide for CAGR API

## 🚀 Why Railway.com?

Railway is an excellent choice for deploying your FastAPI backend because:
- **Easy GitHub Integration** - Direct deployment from your repository
- **Automatic Deployments** - Updates when you push to GitHub
- **Built-in Database** - PostgreSQL support included
- **Environment Variables** - Easy configuration management
- **Free Tier Available** - $5/month hobby plan for production
- **Fast Setup** - Deploy in minutes

## 📋 Prerequisites

- ✅ GitHub repository: `https://github.com/umairusmat/cagr_api.git`
- ✅ Railway.com account (free to sign up)
- ✅ Your FastAPI code ready

## 🚀 Step-by-Step Deployment

### Step 1: Sign Up for Railway

1. Go to [Railway.app](https://railway.app)
2. Click **"Start a New Project"**
3. Sign up with your GitHub account (recommended)
4. Authorize Railway to access your repositories

### Step 2: Create New Project

1. Click **"Deploy from GitHub repo"**
2. Select your repository: `umairusmat/cagr_api`
3. Railway will automatically detect it's a Python project
4. Click **"Deploy Now"**

### Step 3: Configure Environment Variables

Railway will start building your project. While it's building:

1. Go to your project dashboard
2. Click on the **"Variables"** tab
3. Add these environment variables:

```
AUTH_TOKEN=mysecretapitoken123
```

**Important**: Change `mysecretapitoken123` to a secure random string for production!

### Step 4: Configure Database (Optional but Recommended)

Since your app uses SQLite locally, you might want to upgrade to PostgreSQL for production:

1. In your Railway project, click **"New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will create a PostgreSQL database
4. Add the database URL to your environment variables:

```
DATABASE_URL=postgresql://username:password@host:port/database
```

### Step 5: Update Configuration for Production

You'll need to update your `config.json` to use the Railway database:

```json
{
  "scraping": {
    "frequency_hours": 6,
    "retry_attempts": 3,
    "retry_delay": 2,
    "scroll_pixels": 500,
    "row_type": "Avg"
  },
  "webdriver": {
    "browser": "firefox",
    "headless": true
  },
  "api": {
    "auth_token": "your_secure_token_here",
    "host": "0.0.0.0",
    "port": 8000
  },
  "database": {
    "url": "postgresql://username:password@host:port/database"
  }
}
```

### Step 6: Configure Build Settings

Railway should auto-detect your Python project, but verify these settings:

1. **Build Command**: `pip install -r requirements.txt`
2. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Python Version**: 3.8+ (Railway will use the latest)

### Step 7: Deploy and Test

1. Railway will automatically build and deploy your app
2. You'll get a URL like: `https://your-app-name.railway.app`
3. Test your API endpoints:

```bash
# Test the root endpoint
curl -H "X-Auth-Token: your_secure_token" https://your-app-name.railway.app/

# Test health endpoint
curl -H "X-Auth-Token: your_secure_token" https://your-app-name.railway.app/health
```

## 🔧 Configuration Details

### Environment Variables to Set

| Variable | Value | Purpose |
|----------|-------|---------|
| `AUTH_TOKEN` | `your_secure_token_here` | API authentication |
| `DATABASE_URL` | `postgresql://...` | Database connection (if using PostgreSQL) |
| `PORT` | `8000` | Port (Railway sets this automatically) |

### Build Configuration

Railway will automatically detect:
- **Language**: Python
- **Framework**: FastAPI
- **Dependencies**: From `requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## 📊 Monitoring Your Deployment

### Railway Dashboard Features

1. **Deployments** - View deployment history
2. **Logs** - Real-time application logs
3. **Metrics** - CPU, memory, and network usage
4. **Variables** - Environment variable management
5. **Database** - Database management (if using Railway PostgreSQL)

### Health Check

Your API includes a health endpoint:
```
GET https://your-app-name.railway.app/health
```

## 🔄 Updating Your Deployment

### Automatic Updates

Railway automatically redeploys when you:
1. Push changes to your GitHub repository
2. Update environment variables
3. Modify configuration files

### Manual Updates

1. Go to your Railway project dashboard
2. Click **"Redeploy"** to force a new deployment
3. Check logs for any issues

## 🛠️ Troubleshooting

### Common Issues

#### 1. Build Failures
- Check that all dependencies are in `requirements.txt`
- Verify Python version compatibility
- Check build logs in Railway dashboard

#### 2. Runtime Errors
- Check application logs in Railway dashboard
- Verify environment variables are set correctly
- Test API endpoints manually

#### 3. Database Connection Issues
- Verify `DATABASE_URL` is correct
- Check database is running in Railway dashboard
- Test connection with a simple script

#### 4. Authentication Issues
- Verify `AUTH_TOKEN` is set correctly
- Test with curl commands
- Check token matches between FastAPI and Streamlit

### Debug Commands

```bash
# Test API connectivity
curl -v https://your-app-name.railway.app/

# Test with authentication
curl -H "X-Auth-Token: your_token" https://your-app-name.railway.app/health

# Check if app is running
curl -I https://your-app-name.railway.app/
```

## 💰 Pricing

### Free Tier
- **$0/month**
- 500 hours of usage
- 1GB RAM
- Perfect for development and testing

### Hobby Plan
- **$5/month**
- Unlimited usage
- 1GB RAM
- Custom domains
- Perfect for production

## 🔐 Security Best Practices

### 1. Secure Your Token
```bash
# Generate a secure token
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Environment Variables
- Never commit secrets to GitHub
- Use Railway's environment variables
- Rotate tokens regularly

### 3. Database Security
- Use strong database passwords
- Enable SSL connections
- Regular backups

## 📈 Next Steps After Railway Deployment

### 1. Update Streamlit Configuration

Once your FastAPI is deployed on Railway:

1. Go to [Streamlit Cloud](https://share.streamlit.io)
2. Connect your GitHub repository
3. Set these secrets:

```toml
[api]
API_BASE_URL = "https://your-app-name.railway.app"
AUTH_TOKEN = "your_secure_token_here"
```

### 2. Test Full Integration

1. Deploy Streamlit app
2. Test all features:
   - Health checks
   - Data endpoints
   - Manual scraping
   - Scheduler status

### 3. Monitor Performance

- Check Railway metrics
- Monitor API response times
- Set up alerts for downtime

## 🎯 Success Checklist

- [ ] Railway account created
- [ ] GitHub repository connected
- [ ] Environment variables set
- [ ] FastAPI deployed successfully
- [ ] API endpoints tested
- [ ] Database configured (if needed)
- [ ] Streamlit app updated with Railway URL
- [ ] Full integration tested

## 🆘 Support

If you encounter issues:

1. **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
2. **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
3. **Check Logs**: Railway dashboard → Logs tab
4. **Test Locally**: Ensure your app works locally first

---

**Your CAGR API will be live on Railway in minutes! 🚀**

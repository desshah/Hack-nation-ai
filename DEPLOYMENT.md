# 🚀 Deployment Guide - Ghana Medical Desert IDP Agent

## Deploy to Streamlit Community Cloud (FREE)

### Prerequisites
- GitHub account with this repository
- Groq API key (get free at https://console.groq.com/)

### Step-by-Step Deployment

#### 1. Prepare Repository
Ensure all changes are committed and pushed to GitHub:
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

#### 2. Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**: https://share.streamlit.io/

2. **Sign in with GitHub**

3. **Click "New app"**

4. **Configure your app**:
   - **Repository**: `desshah/Hack-nation-ai`
   - **Branch**: `main`
   - **Main file path**: `streamlit_demo.py`

5. **Add Secrets** (click "Advanced settings"):
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
   Replace with your actual Groq API key from https://console.groq.com/

6. **Click "Deploy"**

7. **Wait 2-5 minutes** for deployment to complete

#### 3. Your App is Live! 🎉

You'll get a public URL like:
```
https://desshah-hack-nation-ai-streamlit-demo-xxxxx.streamlit.app
```

Share this URL with anyone - no login required!

---

## Alternative Deployment Options

### Option 2: Hugging Face Spaces (FREE)
1. Create account at https://huggingface.co/
2. Create new Space → Select "Streamlit"
3. Upload files or connect GitHub
4. Add `GROQ_API_KEY` in Settings → Secrets
5. Space will auto-deploy at `https://huggingface.co/spaces/YOUR_USERNAME/APP_NAME`

### Option 3: Railway (FREE Tier)
1. Create account at https://railway.app/
2. New Project → Deploy from GitHub
3. Select this repository
4. Add environment variable: `GROQ_API_KEY`
5. Set start command: `streamlit run streamlit_demo.py --server.port=$PORT`

### Option 4: Render (FREE Tier)
1. Create account at https://render.com/
2. New → Web Service
3. Connect GitHub repository
4. Build command: `pip install -r requirements.txt`
5. Start command: `streamlit run streamlit_demo.py --server.port=$PORT --server.address=0.0.0.0`
6. Add environment variable: `GROQ_API_KEY`

---

## Troubleshooting

### App crashes on startup
- **Check logs** in Streamlit Cloud dashboard
- **Verify API key** is correctly set in Secrets
- **Ensure vector database** builds successfully (may take 1-2 minutes on first run)

### "Module not found" errors
- Check `requirements.txt` includes all dependencies
- Restart app from Streamlit Cloud dashboard

### API rate limits
- Groq free tier: 14,400 requests/day
- For production: Upgrade to Groq paid tier

### Memory issues
- Streamlit Cloud free tier: 1GB RAM
- Reduce batch sizes in config if needed
- Consider upgrading to Streamlit Cloud Team plan

---

## Security Notes

✅ **API keys** are stored securely in Streamlit Secrets (not in code)
✅ **No authentication required** - app is public by default
✅ **HTTPS enabled** automatically on all platforms

To add password protection, see: https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso

---

## Monitoring

After deployment:
- **Usage stats**: Streamlit Cloud dashboard
- **Error logs**: Click "Manage app" → "Logs"
- **Update app**: Push to GitHub → Auto-redeploys in 1-2 minutes

---

## Cost Comparison

| Platform | Free Tier | Paid Tier |
|----------|-----------|-----------|
| **Streamlit Cloud** | 1 private + unlimited public apps | $20/month |
| **Hugging Face** | Unlimited public spaces | $9/month for GPU |
| **Railway** | $5 credit/month | Pay as you go |
| **Render** | 750 hours/month | $7/month |

**Recommendation**: Start with **Streamlit Cloud** - it's built for Streamlit apps and easiest to set up!

---

## Need Help?

- Streamlit Docs: https://docs.streamlit.io/deploy
- Groq Support: https://console.groq.com/docs
- GitHub Issues: https://github.com/desshah/Hack-nation-ai/issues

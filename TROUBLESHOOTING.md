# 🔧 Streamlit Cloud Deployment Troubleshooting

## Common Installation Errors & Fixes

### ✅ **FIXED: Requirements Installation Error**

**Problem:** `torch>=2.0.0` was too large for Streamlit Cloud (1GB RAM limit)

**Solution Applied:**
- ✅ Pinned `torch==2.1.0` (CPU-only version)
- ✅ Added `--extra-index-url https://download.pytorch.org/whl/cpu`
- ✅ Added version upper bounds for stability
- ✅ Reduced total package size

**Status:** Fixed in commit `e2e90a4` - **Reboot your app now!**

---

## 🚀 Next Steps After Fix

### In Streamlit Cloud Dashboard:

1. **Wait 30 seconds** for GitHub sync
2. Click **"Manage app"** button (three dots ⋮)
3. Click **"Reboot app"**
4. Wait 2-3 minutes for fresh installation

### Check Logs:
1. Click **"Manage app"** → **"Logs"**
2. You should see:
   ```
   Installing requirements...
   Successfully installed torch-2.1.0+cpu
   Successfully installed sentence-transformers...
   ```

---

## 📋 Deployment Checklist

### Before Reboot, Verify:

✅ **Repository Settings:**
- Repository: `desshah/Hack-nation-ai` ✓
- Branch: `main` ✓
- File: `streamlit_demo.py` ✓

✅ **Secrets (Advanced Settings):**
```toml
GROQ_API_KEY = "your_actual_key_here"
```
⚠️ **Make sure this is YOUR key from console.groq.com!**

✅ **Python Version:**
- Should auto-detect Python 3.11 or 3.12 ✓

---

## 🐛 Still Having Issues?

### Error: "Module not found: lancedb"
**Fix:** Reboot app (packages installed but not loaded)

### Error: "Memory limit exceeded"
**Symptom:** App crashes during vector database build
**Fix:** This is rare. If it happens:
1. Temporarily comment out vector rebuild in `main.py`
2. Or reduce batch size in embeddings

### Error: "GROQ_API_KEY not found"
**Fix:**
1. Go to Streamlit Cloud → Settings → Secrets
2. Verify format (no extra spaces):
   ```toml
   GROQ_API_KEY = "gsk_..."
   ```
3. Click "Save"
4. Reboot app

### Error: "File not found: vf_ghana_enriched_final.csv"
**Check:** Run this locally:
```bash
git ls-files | grep vf_ghana_enriched_final.csv
```
Should show the file. If not, re-add it:
```bash
git add -f vf_ghana_enriched_final.csv
git commit -m "Add data file"
git push origin main
```

---

## ⏱️ Expected Deployment Timeline

| Phase | Duration | What's Happening |
|-------|----------|------------------|
| **Cloning repo** | 10 sec | Downloading code from GitHub |
| **Installing packages** | 2-3 min | Installing torch, transformers, etc. |
| **Starting app** | 30 sec | Launching Streamlit |
| **Building vector DB** | 1-2 min | First run only (987 facilities) |
| **Ready!** | ✅ | App accessible at your URL |

**Total first deployment: ~4-6 minutes**
**Subsequent reboots: ~3 minutes**

---

## 🎯 Success Indicators

When deployment succeeds, you'll see:

1. **In Logs:**
   ```
   ✅ IDP Agent initialized successfully!
   You can now view your Streamlit app
   ```

2. **In Browser:**
   - Purple gradient header
   - "Ghana Medical Desert IDP Agent" title
   - 4 tabs: Query Analysis, Medical Deserts, etc.

3. **Test Query:**
   - Enter: "Which regions have hospitals?"
   - Should return results with facility names

---

## 🔄 If It Still Fails

### Option 1: Minimal Requirements Test
Create this as `requirements-minimal.txt`:
```
streamlit==1.31.0
pandas==2.0.3
numpy==1.24.3
groq==0.4.2
sentence-transformers==2.3.1
lancedb==0.3.4
pyarrow==14.0.1
pydantic==2.5.0
python-dotenv==1.0.0
plotly==5.18.0
```

### Option 2: Use Hugging Face Spaces Instead
1. Go to https://huggingface.co/spaces
2. Create new Space → Streamlit
3. Upload files from GitHub
4. Tends to have better torch support

### Option 3: Deploy to Railway
Railway has more generous free tier memory:
```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Deploy
cd /Users/deshnashah/Downloads/hacknationai/Hack-nation-ai
railway login
railway init
railway up
```

---

## 📊 Resource Usage (Expected)

- **RAM:** 600-800 MB (within 1GB limit ✓)
- **Startup Time:** 4-6 minutes first time
- **Cold Start:** 30-60 seconds after inactivity
- **Query Response:** 2-5 seconds

---

## 💡 Pro Tips

1. **Monitor Logs:** Keep logs tab open during first boot
2. **Patient:** First deployment takes time (torch install)
3. **Check Secrets:** Most common issue is wrong/missing API key
4. **GitHub Auto-Deploy:** Every push triggers redeploy (wait 2 min)

---

## ✅ Verification Commands (Run Locally)

Test that requirements work:
```bash
cd /Users/deshnashah/Downloads/hacknationai/Hack-nation-ai
python3 -c "
import streamlit
import torch
import sentence_transformers
import lancedb
print('✅ All imports successful!')
print(f'Torch version: {torch.__version__}')
print(f'Streamlit version: {streamlit.__version__}')
"
```

---

## 🆘 Get Help

- **Streamlit Forum:** https://discuss.streamlit.io/
- **Check Status:** https://status.streamlit.io/
- **GitHub Issues:** https://github.com/desshah/Hack-nation-ai/issues

---

**Next Action:** Go to Streamlit Cloud and click "Reboot app" now! 🚀

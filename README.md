# 🌾 Project SAMARTH

**Intelligent Q&A System for Indian Agriculture & Climate Data**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

> Natural language Q&A system using real-time government data and AI

**Application Link** : https://agrorain-samarth.streamlit.app/  
**📹 Video Demo:** https://www.loom.com/share/a94f9c1dd1844c4bad38c1974d6d7a5d

---

## 🎯 What It Does

Ask questions about Indian agriculture in plain English, get intelligent answers backed by real-time government data:

- **"Compare rainfall in Punjab and Haryana for 2010-2014"**
- **"Which district in Punjab has highest wheat production?"**
- **"Why promote drip irrigation for cotton in Maharashtra?"**

---

## ✨ Features

- 🗣️ **Natural Language Processing** - Ask in plain English
- 📊 **Real-time Government Data** - Live from data.gov.in APIs
- 🤖 **AI-Powered Analysis** - Gemini 2.0 for intelligent answers
- 🔍 **Full Traceability** - All API sources visible & verifiable
- 💾 **Smart Caching** - Fast responses with 24-hour cache
- 🔄 **Auto-retry Logic** - Handles slow government servers
- 📱 **Responsive UI** - Works on desktop and mobile

---

## 🚀 Quick Start (Local Development)

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/project-samarth.git
cd project-samarth
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get API Keys

- **data.gov.in:** https://data.gov.in/ (free registration)
- **Gemini API:** https://makersuite.google.com/app/apikey (free tier)

### 4. Add Your Keys

Create `.streamlit/secrets.toml`:

```toml
API_KEY = "your_data_gov_in_key"
GEMINI_KEY = "your_gemini_key"
```

### 5. Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## 🌐 Deploy to Streamlit Cloud

### Prerequisites
- GitHub account
- Streamlit Cloud account (free)
- API keys (see above)

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Select your repo
   - Set main file: `app.py`

3. **Add Secrets**
   - In app Settings → Secrets
   - Add:
     ```toml
     API_KEY = "your_key"
     GEMINI_KEY = "your_key"
     ```

4. **Done!** App deploys in ~2 minutes

**📖 Detailed Guide:** See [STREAMLIT_CLOUD_GUIDE.md](STREAMLIT_CLOUD_GUIDE.md)

---

## 📊 Data Sources

All data from official Indian government sources:

1. **IMD Rainfall Data** (1901-2017)
   - Sub-divisional annual rainfall
   - India Meteorological Department

2. **Crop Production** (1997-2014)
   - District-wise, season-wise statistics
   - Ministry of Agriculture & Farmers Welfare

3. **Water Efficiency** (8 crops)
   - Traditional vs drip irrigation
   - ICAR (Indian Council of Agricultural Research)

---

## 🏗️ Architecture

```
User Question
    ↓
Gemini AI (Parse Query)
    ↓
Determine Required APIs
    ↓
Fetch Data (parallel, with retry)
    ↓
Gemini AI (Generate Answer)
    ↓
Display with Sources
```

---

## 💻 Tech Stack

- **Frontend:** Streamlit 1.40.1
- **AI:** Google Gemini 2.0 Flash Exp
- **APIs:** data.gov.in (3 datasets)
- **Language:** Python 3.11
- **Deployment:** Streamlit Cloud
- **Caching:** Built-in Streamlit cache

---

## 📁 Project Structure

```
project-samarth/
├── app.py                    # Main Streamlit app
├── config.py                 # Configuration (reads from secrets)
├── gemini_handler.py         # AI integration
├── data_fetcher.py           # API data fetching
├── metadata.py               # Data availability info
├── requirements.txt          # Python dependencies
├── .streamlit/
│   ├── config.toml          # Streamlit settings
│   └── secrets.toml         # API keys (local only, not in Git)
├── .gitignore               # Protects secrets
└── README.md                # This file
```

---

## 🧪 Testing

Try the 4 example questions from the sidebar:

1. **Q1: Multi-State Comparison** - Tests state comparison, rainfall, crop aggregation
2. **Q2: District Extremes** - Tests district-level data, extreme values
3. **Q3: Trend Analysis** - Tests time series, correlation analysis
4. **Q4: Policy Recommendation** - Tests water efficiency, AI reasoning

---

## 🐛 Common Issues

### "API Key Error"
→ Check secrets are added in `.streamlit/secrets.toml` (local) or Streamlit Cloud dashboard (deployed)

### "Request Timeout"
→ Normal - government servers can be slow. Wait 30s and retry.

### "Module not found"
→ Run `pip install -r requirements.txt`

### App works locally but not on Streamlit Cloud
→ Verify secrets are added in Streamlit Cloud dashboard (Settings → Secrets)

---

## 🔒 Security

- ✅ API keys stored in secrets (never in code)
- ✅ `.gitignore` protects `secrets.toml`
- ✅ `config.py` safe to commit (reads from secrets)
- ✅ No hardcoded credentials anywhere

---

## 📝 License

Educational project for demonstration purposes.

---

## 🤝 Credits

- **Data:** data.gov.in (Government of India)
- **AI:** Google Gemini 2.0
- **Framework:** Streamlit

---

## 📞 Support

For issues:
1. Check [STREAMLIT_CLOUD_GUIDE.md](STREAMLIT_CLOUD_GUIDE.md)
2. Review error logs in Streamlit Cloud dashboard
3. Verify API keys are valid

---

## 🎓 Built For

Challenge submission showcasing:
- Natural language processing
- Multi-source data integration
- Real-time API orchestration
- Production-ready error handling
- Modern web deployment

---

**Made with ❤️ for Indian Agriculture**



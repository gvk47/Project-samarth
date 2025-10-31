# 🌾 Project SAMARTH

**Intelligent Q&A System for Indian Agriculture & Climate Data**

## 🎯 Challenge Solution
This project answers complex natural language questions about Indian agriculture and climate by integrating real-time data from data.gov.in government portal.

## ✨ Features
- ✅ Real-time API integration with government datasets
- ✅ Natural language processing with Gemini AI
- ✅ Multi-source data synthesis across inconsistent formats
- ✅ Complete source traceability for every data point
- ✅ Covers 33 states, 100+ crops, 120 years of rainfall data

## 📊 Data Sources
1. **IMD Rainfall Data** (1901-2017) - Sub-divisional monthly rainfall
2. **Ministry of Agriculture** (1997-2014) - District-wise crop production
3. **ICAR Water Efficiency** - Traditional vs drip irrigation comparison

## 🏗️ System Architecture
```
User Question 
    → NLU Parser (Gemini AI)
    → API Selector (Intelligent routing)
    → Data Fetcher (Real-time APIs)
    → Answer Generator (Gemini AI)
    → Response with Citations
```

## 🎯 Sample Questions (All 4 Types Supported)

**Q1: Multi-State Comparison**
```
Compare the average annual rainfall in Punjab and Haryana for 2010-2014. 
Also list the top 3 most produced crops in each state during 2014.
```

**Q2: District Extremes**
```
Identify the district in Punjab with the highest wheat production in 2014 
and compare with the district with lowest wheat production in Haryana.
```

**Q3: Trend Analysis**
```
Analyze rice production trend in Punjab from 2010 to 2014. 
Correlate with rainfall pattern and provide impact summary.
```

**Q4: Policy Recommendation**
```
Why promote cotton cultivation with drip irrigation over traditional methods 
in Maharashtra? Give 3 data-backed arguments using 2010-2014 data.
```

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Configuration
For local testing, update `config.py` with your API keys:
- Gemini API key from Google AI Studio
- data.gov.in API key from the portal

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **AI/NLU:** Google Gemini 2.0 Flash
- **Data APIs:** data.gov.in REST APIs
- **Language:** Python 3.9+

## 📂 Project Structure
```
project-samarth/
├── app.py                 # Main Streamlit application
├── gemini_handler.py      # NLU parsing & answer generation
├── data_fetcher.py        # API integration & data fetching
├── metadata.py            # State/crop mappings & validation
├── config.py              # API keys & endpoints
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🎨 Key Design Decisions

1. **State Mapping Layer** - Handles inconsistent naming between datasets (e.g., "Orissa" vs "Odisha")
2. **Intelligent API Selection** - Automatically determines which APIs to call based on question intent
3. **Multi-stage Processing** - Parse → Validate → Fetch → Generate for robust error handling
4. **Source Traceability** - Every answer cites specific datasets, API endpoints, and record counts

## 📝 Evaluation Criteria Coverage

✅ **Problem Solving:** Navigated data.gov.in, identified relevant datasets, built working prototype  
✅ **System Architecture:** Modular design with clear separation of concerns  
✅ **Accuracy:** Real-time government data with validation  
✅ **Traceability:** Complete citation system for all claims  
✅ **Data Sovereignty:** Runs locally, secure deployment possible  

## 🎥 Demo Video
[Loom video link will be added here]

---

Built for the Government Data Integration Challenge
```

---

## 📤 Manual Upload Steps:

### **Step 2: Organize Your Files**

Your folder should look like this:
```
project-samarth/
├── app.py                    (use app_compact.py - rename it)
├── gemini_handler.py         (from document 3)
├── data_fetcher.py           (from document 5)
├── metadata.py               (from document 6)
├── config.py                 (NEW - use the one above)
├── requirements.txt          (NEW - use the one above)
├── .gitignore               (NEW - use the one above)
└── README.md                (NEW - use the one above)
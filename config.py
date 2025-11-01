# config.py
# Configuration file for Project SAMARTH - STREAMLIT CLOUD VERSION
# This file reads API keys from Streamlit secrets in production

import os

# ============================================================================
# API KEYS - Streamlit Cloud Compatible
# ============================================================================

try:
    # Try to import Streamlit (works in Streamlit Cloud)
    import streamlit as st
    
    # In Streamlit Cloud, read from secrets
    API_KEY = st.secrets.get("API_KEY", os.environ.get("API_KEY", ""))
    GEMINI_KEY = st.secrets.get("GEMINI_KEY", os.environ.get("GEMINI_KEY", ""))
    
except ImportError:
    # Running locally without Streamlit (for testing)
    API_KEY = os.environ.get("API_KEY", "")
    GEMINI_KEY = os.environ.get("GEMINI_KEY", "")

# Validation check
if not API_KEY or API_KEY == "":
    import warnings
    warnings.warn("⚠️ API_KEY not set! Add it to .streamlit/secrets.toml for local dev or Streamlit Cloud secrets for deployment")

if not GEMINI_KEY or GEMINI_KEY == "":
    import warnings
    warnings.warn("⚠️ GEMINI_KEY not set! Add it to .streamlit/secrets.toml for local dev or Streamlit Cloud secrets for deployment")

# ============================================================================
# DATA.GOV.IN API ENDPOINTS
# ============================================================================

RAINFALL_MONTHLY_API = "https://api.data.gov.in/resource/8e0bd482-4aba-4d99-9cb9-ff124f6f1c2f"
RAINFALL_ANNUAL_API = "https://api.data.gov.in/resource/294a162a-92fb-4939-af88-e69bd84049f1"
CROP_PRODUCTION_API = "https://api.data.gov.in/resource/35be999b-0208-4354-b557-f6ca9a5355de"
WATER_USAGE_API = "https://api.data.gov.in/resource/50bc5a96-d6d5-483e-92b1-2d8fe09f0a0d"

# ============================================================================
# API CONFIGURATION
# ============================================================================

API_TIMEOUT = 30
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY = 2
CACHE_TTL = 86400  # 24 hours

# ============================================================================
# GEMINI CONFIGURATION
# ============================================================================

GEMINI_MODEL = "gemini-2.0-flash-exp"
GEMINI_MAX_ATTEMPTS = 20
GEMINI_INITIAL_DELAY = 2

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

MAX_CONVERSATIONS = 20
MAX_MESSAGES_PER_CONV = 20
MAX_QUESTIONS_PER_SESSION = 100
RATE_LIMIT_WARNING_THRESHOLD = 80

# ============================================================================
# FEATURE FLAGS
# ============================================================================

ENABLE_CACHING = True
ENABLE_DEBUG_MODE = False
SHOW_API_URLS = True
ENABLE_PARALLEL_FETCHING = False


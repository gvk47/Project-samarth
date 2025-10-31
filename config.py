import os
import streamlit as st

# Get API keys from Streamlit secrets or environment
GEMINI_KEY = st.secrets.get("GEMINI_KEY", os.getenv("GEMINI_KEY", ""))
API_KEY = st.secrets.get("DATA_GOV_API_KEY", os.getenv("DATA_GOV_API_KEY", ""))

# API endpoints (URLs where we get data)
RAINFALL_MONTHLY_API = "https://api.data.gov.in/resource/8e0bd482-4aba-4d99-9cb9-ff124f6f1c2f"
RAINFALL_ANNUAL_API = "https://api.data.gov.in/resource/294a162a-92fb-4939-af88-e69bd84049f1"
CROP_PRODUCTION_API = "https://api.data.gov.in/resource/35be999b-0208-4354-b557-f6ca9a5355de"
WATER_USAGE_API = "https://api.data.gov.in/resource/50bc5a96-d6d5-483e-92b1-2d8fe09f0a0d"


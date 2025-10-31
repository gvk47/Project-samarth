# metadata.py
# This file contains all the information about what data is available

# All 36 meteorological subdivisions
SUBDIVISIONS = [
    "ANDAMAN & NICOBAR ISLANDS",
    "ARUNACHAL PRADESH",
    "ASSAM & MEGHALAYA",
    "NAGALAND, MANIPUR, MIZORAM,TRIPURA",
    "SUB-HIMALAYAN W BENGAL & SIKKIM",
    "GANGETIC WEST BENGAL",
    "ORISSA",
    "JHARKHAND",
    "BIHAR",
    "EAST UTTAR PRADESH",
    "WEST UTTAR PRADESH",
    "UTTARANCHAL",
    "HARYANA, DELHI & CHANDIGARH",
    "PUNJAB",
    "HIMACHAL PRADESH",
    "JAMMU & KASHMIR",
    "WEST RAJASTHAN",
    "EAST RAJASTHAN",
    "WEST MADHYA PRADESH",
    "EAST MADHYA PRADESH",
    "GUJARAT REGION, DADRA & NAGAR HAVELI",
    "SAURASHTRA KUTCH & DIU",
    "KOKAN & GOA",
    "MADHYA MAHARASHTRA",
    "MARATWADA",
    "VIDARBHA",
    "CHATTISGARH",
    "COSTAL ANDHRA PRADESH",
    "TELENGANA",
    "RAYALSEEMA",
    "TAMIL NADU & PONDICHERRY",
    "COASTAL KARNATAKA",
    "NORTH INTERIOR KARNATAKA",
    "SOUTH INTERIOR KARNATAKA",
    "KERALA",
    "LAKSHADWEEP"
]

# All available states in crop data
AVAILABLE_STATES = [
    "Andaman and Nicobar Islands",
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chandigarh",
    "Chhattisgarh",
    "Dadra and Nagar Haveli",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jammu and Kashmir",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Puducherry",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal"
]

# State aliases - common variations and abbreviations
STATE_ALIASES = {
    # Abbreviations
    "UP": "Uttar Pradesh",
    "MP": "Madhya Pradesh",
    "HP": "Himachal Pradesh",
    "AP": "Andhra Pradesh",
    "TN": "Tamil Nadu",
    "WB": "West Bengal",
    "J&K": "Jammu and Kashmir",
    "JK": "Jammu and Kashmir",
    
    # Alternative spellings
    "Orissa": "Odisha",
    "Pondicherry": "Puducherry",
    "Uttaranchal": "Uttarakhand",
    
    # Old names
    "Bombay": "Maharashtra",
    "Madras": "Tamil Nadu",
    "Calcutta": "West Bengal",
    "Bangalore": "Karnataka",
    
    # Common variations
    "Uttar pradesh": "Uttar Pradesh",
    "Tamil nadu": "Tamil Nadu",
    "West bengal": "West Bengal",
    "Himachal pradesh": "Himachal Pradesh",
    "Madhya pradesh": "Madhya Pradesh",
    "Andhra pradesh": "Andhra Pradesh",
    "Arunachal pradesh": "Arunachal Pradesh",
    "Jammu kashmir": "Jammu and Kashmir",
    
    # Lowercase versions
    "punjab": "Punjab",
    "haryana": "Haryana",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "bihar": "Bihar",
    "assam": "Assam",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "rajasthan": "Rajasthan",
    "maharashtra": "Maharashtra",
    "odisha": "Odisha",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "sikkim": "Sikkim",
    "jharkhand": "Jharkhand",
    "chhattisgarh": "Chhattisgarh",
    "uttarakhand": "Uttarakhand",
    "chandigarh": "Chandigarh",
    "puducherry": "Puducherry"
}

# Common crops (will be expanded with API data)
COMMON_CROPS = [
    "Wheat", "Rice", "Maize", "Bajra", "Jowar",
    "Arhar/Tur", "Gram", "Moong(Green Gram)", "Urad", "Masoor",
    "Cotton(lint)", "Sugarcane", "Groundnut", "Rapeseed &Mustard",
    "Sunflower", "Soyabean", "Sesamum", "Safflower"
]

# Crops available in water usage data (only 8)
WATER_USAGE_CROPS = [
    "Banana", "Grapes", "Citrus", "Tomato",
    "Brinjal", "Chilli", "Sugarcane", "Cotton"
]

# Year ranges
CROP_YEAR_MIN = 1997
CROP_YEAR_MAX = 2014
RAINFALL_YEAR_MIN = 1901
RAINFALL_YEAR_MAX = 2017

# Subdivision to State mapping
SUBDIVISION_TO_STATE = {
    "PUNJAB": ["Punjab"],
    "HARYANA, DELHI & CHANDIGARH": ["Haryana", "Delhi", "Chandigarh"],
    "UTTARANCHAL": ["Uttarakhand"],
    "EAST UTTAR PRADESH": ["Uttar Pradesh"],
    "WEST UTTAR PRADESH": ["Uttar Pradesh"],
    "ORISSA": ["Odisha"],
    "JHARKHAND": ["Jharkhand"],
    "BIHAR": ["Bihar"],
    "ASSAM & MEGHALAYA": ["Assam", "Meghalaya"],
    "NAGALAND, MANIPUR, MIZORAM,TRIPURA": ["Nagaland", "Manipur", "Mizoram", "Tripura"],
    "SUB-HIMALAYAN W BENGAL & SIKKIM": ["West Bengal", "Sikkim"],
    "GANGETIC WEST BENGAL": ["West Bengal"],
    "ANDAMAN & NICOBAR ISLANDS": ["Andaman and Nicobar Islands"],
    "ARUNACHAL PRADESH": ["Arunachal Pradesh"],
    "HIMACHAL PRADESH": ["Himachal Pradesh"],
    "JAMMU & KASHMIR": ["Jammu and Kashmir"],
    "WEST RAJASTHAN": ["Rajasthan"],
    "EAST RAJASTHAN": ["Rajasthan"],
    "WEST MADHYA PRADESH": ["Madhya Pradesh"],
    "EAST MADHYA PRADESH": ["Madhya Pradesh"],
    "GUJARAT REGION, DADRA & NAGAR HAVELI": ["Gujarat", "Dadra and Nagar Haveli"],
    "SAURASHTRA KUTCH & DIU": ["Gujarat", "Daman and Diu"],
    "KOKAN & GOA": ["Maharashtra", "Goa"],
    "MADHYA MAHARASHTRA": ["Maharashtra"],
    "MARATWADA": ["Maharashtra"],
    "VIDARBHA": ["Maharashtra"],
    "CHATTISGARH": ["Chhattisgarh"],
    "COSTAL ANDHRA PRADESH": ["Andhra Pradesh"],
    "TELENGANA": ["Telangana"],
    "RAYALSEEMA": ["Andhra Pradesh"],
    "TAMIL NADU & PONDICHERRY": ["Tamil Nadu", "Puducherry"],
    "COASTAL KARNATAKA": ["Karnataka"],
    "NORTH INTERIOR KARNATAKA": ["Karnataka"],
    "SOUTH INTERIOR KARNATAKA": ["Karnataka"],
    "KERALA": ["Kerala"],
    "LAKSHADWEEP": ["Lakshadweep"]
}

def normalize_state_name(state_name):
    """
    Normalize state name using aliases
    
    Args:
        state_name: State name (possibly an alias or variation)
    
    Returns:
        Normalized state name or original if no match
    """
    # Check if it's already a valid state
    if state_name in AVAILABLE_STATES:
        return state_name
    
    # Check aliases (case-insensitive)
    for alias, normalized in STATE_ALIASES.items():
        if state_name.lower() == alias.lower():
            return normalized
    
    # Try case-insensitive match against available states
    for state in AVAILABLE_STATES:
        if state_name.lower() == state.lower():
            return state
    
    # No match found, return original
    return state_name

def get_subdivision_for_state(state_name):
    """
    Given a state name, find its rainfall subdivision
    
    Example: get_subdivision_for_state("Punjab") returns "PUNJAB"
    """
    # First normalize the state name
    normalized_state = normalize_state_name(state_name)
    
    for subdivision, states in SUBDIVISION_TO_STATE.items():
        if normalized_state in states:
            return subdivision
    
    # If not found, return uppercased state name as fallback
    return normalized_state.upper()

def validate_state(state_name):
    """Check if a state exists in our data (with alias support)"""
    normalized_state = normalize_state_name(state_name)
    return normalized_state in AVAILABLE_STATES

def validate_crop(crop_name):
    """Check if a crop exists in our data"""
    # Will be expanded when we fetch actual crop list from API
    return True  # For now, accept any crop

def validate_year_for_crops(year):
    """Check if year is valid for crop data"""
    return CROP_YEAR_MIN <= year <= CROP_YEAR_MAX

def validate_year_for_rainfall(year):
    """Check if year is valid for rainfall data"""
    return RAINFALL_YEAR_MIN <= year <= RAINFALL_YEAR_MAX

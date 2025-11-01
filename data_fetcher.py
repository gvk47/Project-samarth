# data_fetcher.py
# This file handles all API calls to fetch data
# PRODUCTION VERSION with improved error handling and timeouts

import requests
import time
import random

# Try to import streamlit, use dummy cache if not available
try:
    import streamlit as st
    cache_decorator = st.cache_data(ttl=86400)  # 24 hours cache
except:
    # Dummy decorator for testing without Streamlit
    def cache_decorator(func):
        return func

from config import *
from metadata import get_subdivision_for_state

def retry_request(func, max_attempts=3, initial_delay=2):
    """
    Retry a function with exponential backoff and jitter
    
    Args:
        func: Function to retry
        max_attempts: Maximum number of attempts (default 3)
        initial_delay: Initial delay in seconds (default 2)
    
    Returns:
        Result of function or None if all attempts fail
    """
    for attempt in range(max_attempts):
        try:
            result = func()
            return result
        except requests.exceptions.Timeout:
            if attempt < max_attempts - 1:
                # Exponential backoff with jitter: 2s, 4s, 8s (+ random 0-1s)
                delay = min(initial_delay * (2 ** attempt) + random.uniform(0, 1), 15)
                print(f"⏱️ Request timeout, retrying in {delay:.1f}s... (Attempt {attempt + 1}/{max_attempts})")
                time.sleep(delay)
            else:
                print(f"❌ All {max_attempts} attempts failed due to timeout")
                return None
        except requests.exceptions.RequestException as e:
            if attempt < max_attempts - 1:
                delay = min(initial_delay * (2 ** attempt) + random.uniform(0, 1), 15)
                print(f"⚠️ Request failed: {str(e)[:100]}, retrying in {delay:.1f}s... (Attempt {attempt + 1}/{max_attempts})")
                time.sleep(delay)
            else:
                print(f"❌ All {max_attempts} attempts failed: {str(e)[:100]}")
                return None
    return None

# Cache decorator to store API responses (24 hour expiry)
@cache_decorator
def fetch_rainfall_annual(state_name, years):
    """
    Fetch annual rainfall data for a state
    
    Args:
        state_name: Name of the state (e.g., "Punjab")
        years: List of years (e.g., [2010, 2011, 2012])
    
    Returns:
        Dictionary with rainfall data and metadata
    """
    print(f"🌧️ Fetching rainfall data for {state_name}...")
    
    # Get the subdivision name for this state
    subdivision = get_subdivision_for_state(state_name)
    print(f"   Mapped to subdivision: {subdivision}")
    
    url = f"{RAINFALL_ANNUAL_API}"
    params = {
        'api-key': API_KEY,
        'format': 'json',
        'offset': 1800,  # Skip to recent years
        'limit': 500     # Fetch enough to cover 2000-2017
    }
    
    def make_request():
        # Reduced timeout from 60s to 30s for better UX
        response = requests.get(url, params=params, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response
    
    try:
        response = retry_request(make_request, max_attempts=API_RETRY_ATTEMPTS, initial_delay=API_RETRY_DELAY)
        
        if response is None:
            return {
                'success': False,
                'error': 'api_timeout',
                'message': '⏱️ Government servers are responding slowly. Please try again in a moment.',
                'user_friendly': True
            }
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            print(f"   ✅ Fetched {len(records)} total records")
            
            # Debug: Show year range
            if records:
                years_in_data = [int(float(r.get('year', 0))) for r in records if r.get('year')]
                if years_in_data:
                    print(f"   📅 Year range: {min(years_in_data)}-{max(years_in_data)}")
            
            # Filter for our subdivision and years
            filtered_records = []
            for r in records:
                record_subdivision = r.get('sd_name', '')
                record_year_str = r.get('year', '0')
                
                try:
                    record_year = int(float(record_year_str))
                except (ValueError, TypeError):
                    continue
                
                # Match subdivision (case-insensitive) and year
                if record_subdivision.upper() == subdivision.upper() and record_year in years:
                    filtered_records.append(r)
            
            print(f"   ✅ Matched {len(filtered_records)} records for {subdivision} ({years})")
            
            return {
                'success': True,
                'subdivision': subdivision,
                'state': state_name,
                'records': filtered_records,
                'api_url': response.url,
                'total_fetched': len(records),
                'total_matched': len(filtered_records)
            }
        else:
            return {
                'success': False,
                'error': 'api_status',
                'message': f'📡 Data service returned unexpected status: {response.status_code}',
                'user_friendly': True
            }
            
    except Exception as e:
        error_str = str(e)
        print(f"❌ Unexpected error: {error_str[:200]}")
        return {
            'success': False,
            'error': 'unexpected',
            'message': f'⚠️ Unexpected error while fetching rainfall data. Please try again.',
            'user_friendly': True,
            'technical_details': error_str[:200]
        }
    
@cache_decorator
def fetch_crop_production(state_name, crop_name=None, year=None):
    """
    Fetch crop production data for a state
    
    Args:
        state_name: Name of the state (e.g., "Punjab")
        crop_name: Optional - specific crop (e.g., "Wheat")
        year: Optional - specific year (e.g., 2014)
    
    Returns:
        Dictionary with crop production data and metadata
    """
    print(f"🌾 Fetching crop data for {state_name}, crop={crop_name}, year={year}...")
    
    url = f"{CROP_PRODUCTION_API}"
    params = {
        'api-key': API_KEY,
        'format': 'json',
        'filters[state_name]': state_name,
        'limit': 200  # Reasonable limit
    }
    
    # Add optional filters
    if crop_name:
        params['filters[crop]'] = crop_name
    if year:
        params['filters[crop_year]'] = year
    
    def make_request():
        response = requests.get(url, params=params, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response
    
    try:
        response = retry_request(make_request, max_attempts=API_RETRY_ATTEMPTS, initial_delay=API_RETRY_DELAY)
        
        if response is None:
            return {
                'success': False,
                'error': 'api_timeout',
                'message': '⏱️ Agriculture data service is slow right now. Please try again.',
                'user_friendly': True
            }
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            print(f"   ✅ Retrieved {len(records)} crop records")
            
            return {
                'success': True,
                'state': state_name,
                'crop': crop_name,
                'year': year,
                'records': records,
                'api_url': response.url,
                'total_records': len(records)
            }
        else:
            return {
                'success': False,
                'error': 'api_status',
                'message': f'📡 Crop data service returned unexpected status: {response.status_code}',
                'user_friendly': True
            }
            
    except Exception as e:
        error_str = str(e)
        print(f"❌ Unexpected error: {error_str[:200]}")
        return {
            'success': False,
            'error': 'unexpected',
            'message': f'⚠️ Error fetching crop production data. Please try again.',
            'user_friendly': True,
            'technical_details': error_str[:200]
        }
    
@cache_decorator
def fetch_water_usage(crop_name=None):
    """
    Fetch water usage comparison data
    
    Args:
        crop_name: Optional - specific crop (e.g., "Sugarcane")
    
    Returns:
        Dictionary with water usage data and metadata
    """
    print(f"💧 Fetching water usage data for crop={crop_name}...")
    
    url = f"{WATER_USAGE_API}"
    params = {
        'api-key': API_KEY,
        'format': 'json'
    }
    
    if crop_name:
        params['filters[crop]'] = crop_name
    
    def make_request():
        response = requests.get(url, params=params, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response
    
    try:
        response = retry_request(make_request, max_attempts=API_RETRY_ATTEMPTS, initial_delay=API_RETRY_DELAY)
        
        if response is None:
            return {
                'success': False,
                'error': 'api_timeout',
                'message': '⏱️ Water efficiency data service is slow. Please try again.',
                'user_friendly': True
            }
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            print(f"   ✅ Retrieved {len(records)} water usage records")
            
            return {
                'success': True,
                'crop': crop_name,
                'records': records,
                'api_url': response.url,
                'total_records': len(records)
            }
        else:
            return {
                'success': False,
                'error': 'api_status',
                'message': f'📡 Water data service returned unexpected status: {response.status_code}',
                'user_friendly': True
            }
            
    except Exception as e:
        error_str = str(e)
        print(f"❌ Unexpected error: {error_str[:200]}")
        return {
            'success': False,
            'error': 'unexpected',
            'message': f'⚠️ Error fetching water usage data. Please try again.',
            'user_friendly': True,
            'technical_details': error_str[:200]
        }
    
def calculate_average_rainfall(rainfall_data):
    """Calculate average annual rainfall from records"""
    records = rainfall_data.get('records', [])
    
    if not records:
        return 0
    
    # Handle potential non-numeric values
    valid_values = []
    for r in records:
        try:
            value = float(r.get('annual', 0))
            if value > 0:  # Ignore zero/negative values
                valid_values.append(value)
        except (ValueError, TypeError):
            continue
    
    if not valid_values:
        return 0
    
    return sum(valid_values) / len(valid_values)

def get_top_n_crops(crop_data, n=3):
    """Get top N crops by production volume"""
    records = crop_data.get('records', [])
    
    if not records:
        return []
    
    # Aggregate production by crop
    crop_totals = {}
    for record in records:
        crop = record.get('crop', 'Unknown')
        production_str = record.get('production_', '0')
        
        # Handle 'NA', empty strings, and other non-numeric values
        try:
            production = float(production_str)
            if production < 0:  # Skip negative values
                continue
        except (ValueError, TypeError):
            continue
        
        if crop in crop_totals:
            crop_totals[crop] += production
        else:
            crop_totals[crop] = production
    
    # Sort by production and get top N
    sorted_crops = sorted(crop_totals.items(), key=lambda x: x[1], reverse=True)
    return sorted_crops[:n]

def format_api_call_info(api_response):
    """Format API call information for display"""
    if not api_response.get('success'):
        return f"❌ Error: {api_response.get('message', 'Unknown error')}"
    
    info = f"✅ Success\n"
    info += f"   API URL: {api_response.get('api_url', 'N/A')}\n"
    info += f"   Records: {api_response.get('total_records', 0)}"
    
    return info

def check_all_apis_failed(fetched_data):
    """
    Check if all API calls failed (network issue vs no matching data)
    
    Returns:
        (all_failed: bool, network_issue: bool)
    """
    if not fetched_data:
        return True, False
    
    all_failed = all(not data.get('success') for data in fetched_data.values())
    
    if all_failed:
        # Check if failures were due to network/timeout
        network_errors = ['api_timeout', 'api_status', 'unexpected']
        has_network_issue = any(
            data.get('error') in network_errors 
            for data in fetched_data.values()
        )
        return True, has_network_issue
    
    return False, False

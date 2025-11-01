# gemini_handler.py
# This file handles all Gemini AI interactions
# PRODUCTION VERSION with improved rate limiting and error handling

import google.generativeai as genai
import json
import time
import random
from config import GEMINI_KEY, GEMINI_MODEL, GEMINI_MAX_ATTEMPTS, GEMINI_INITIAL_DELAY
from metadata import *

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

def check_if_agriculture_query(question):
    """
    Determine if a question is about agriculture/climate data that requires data fetching
    Returns True if agriculture-related and needs data, False for general questions
    """
    question_lower = question.lower()
    
    # Simple greetings and pleasantries - handle conversationally (one or two words only)
    if len(question.split()) <= 2:
        simple_phrases = ['hello', 'hi', 'hey', 'thanks', 'thank you', 'bye', 'goodbye', 
                         'ok', 'okay', 'cool', 'great', 'awesome', 'good', 'nice']
        if any(phrase == question_lower.strip() for phrase in simple_phrases):
            return False
    
    # Questions about the assistant itself (conversational)
    assistant_questions = ['who are you', 'what are you', 'what can you do', 'what is your name',
                          'how are you', 'tell me about yourself', 'what do you do']
    if any(q in question_lower for q in assistant_questions):
        return False
    
    # Agriculture/data keywords that indicate need for data fetching
    data_keywords = [
        'crop', 'rain', 'rainfall', 'production', 'wheat', 'rice', 'cotton',
        'irrigation', 'harvest', 'farming', 'cultivation', 'paddy', 'maize',
        'district', 'yield', 'drip', 'traditional', 'water usage',
        'punjab', 'haryana', 'maharashtra', 'karnataka', 'tamil nadu',
        'uttar pradesh', 'madhya pradesh', 'andhra pradesh', 'telangana',
        'annual', 'season', 'kharif', 'rabi', 'data', 'statistics',
        'area', 'productivity', 'hectare', 'tonne', 'sugarcane', 'bajra',
        'jowar', 'arhar', 'gram', 'moong', 'groundnut', 'soyabean',
        'compare', 'trend', 'highest', 'lowest', 'average', 'total',
        'state', 'india', 'government', 'ministry of agriculture'
    ]
    
    # If question has agriculture keywords, it's probably an agriculture query
    has_data_keyword = any(keyword in question_lower for keyword in data_keywords)
    
    # If it has data keywords, treat as agriculture query
    # Exception: questions about definitions without asking for specific data
    if has_data_keyword:
        # Check if it's just asking for a definition (general knowledge)
        definition_patterns = ['what is', 'what are', 'define', 'meaning of', 'explain']
        is_definition_only = any(pattern in question_lower for pattern in definition_patterns) and \
                           not any(word in question_lower for word in ['compare', 'show', 'list', 'find', 'get', 'analyze', 'data', 'statistics', 'production', 'in', 'for'])
        
        if is_definition_only:
            return False  # Handle as general query
        
        return True  # Has agriculture keywords and not just asking for definition
    
    return False  # No agriculture keywords, handle conversationally

def handle_general_query(question):
    """
    Handle non-agriculture queries with professionalism and respect
    Provides helpful, contextual responses for any question
    """
    
    # Pre-handle common questions with UNIQUE responses
    question_lower = question.lower().strip()
    
    # Greetings
    if question_lower in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'hi there']:
        return {
            'success': True,
            'answer': "Hello! 👋 I'm SAMARTH, specialized in Indian agriculture and climate data. I can help you analyze crop production, rainfall patterns, and irrigation efficiency across Indian states. What would you like to explore?"
        }
    
    # Thanks
    if 'thank' in question_lower:
        return {
            'success': True,
            'answer': "You're welcome! 😊 Feel free to ask about any agriculture or climate data for Indian states."
        }
    
    # About assistant
    if any(phrase in question_lower for phrase in ['who are you', 'what are you', 'what can you do', 'your name', 'tell me about yourself']):
        return {
            'success': True,
            'answer': "I'm **SAMARTH**, an AI assistant specializing in Indian agriculture and climate data analysis. I can:\n\n- 🌧️ Compare rainfall patterns across states\n- 🌾 Analyze crop production and trends\n- 💧 Evaluate water efficiency in irrigation\n- 📊 Find extremes (highest/lowest production)\n- 📈 Identify trends over multiple years\n\nAll my data comes from official government sources (data.gov.in). What would you like to analyze?"
        }
    
    # For other questions, use Gemini with concise, specific prompt
    prompt = f"""You are SAMARTH, specializing in Indian agriculture and climate data.

Question: "{question}"

Instructions:
1. Answer the question DIRECTLY if you can (give actual information, not just generic response)
2. Be specific and unique - this exact question deserves a unique answer
3. If you don't know, say so honestly
4. Then briefly mention your agriculture expertise
5. Keep it under 80 words
6. Be warm and professional

Answer:"""
    
    try:
        gemini_response = call_gemini_with_retry(prompt, max_attempts=2)
        
        if gemini_response['success']:
            return {
                'success': True,
                'answer': gemini_response['text']
            }
        else:
            # Context-aware fallbacks based on question content
            if 'budget' in question_lower:
                return {
                    'success': True,
                    'answer': "I specialize in agricultural data rather than general budget information. For comprehensive budget details, try the Ministry of Finance website. However, I can help you analyze agricultural allocations, crop production statistics, or irrigation investments across states!"
                }
            elif any(word in question_lower for word in ['capital', 'city', 'country', 'geography']):
                return {
                    'success': True,
                    'answer': "That's a geography question! While that's not my specialty, I'm excellent at analyzing agricultural geography - comparing crop yields across states, rainfall distributions, or regional farming patterns. Want to explore any of that?"
                }
            elif 'weather' in question_lower:
                return {
                    'success': True,
                    'answer': "For current weather, check weather apps or IMD. I specialize in historical climate data - rainfall patterns over years, seasonal trends, and how they correlate with crop production. I can show you rainfall trends for any Indian state!"
                }
            else:
                return {
                    'success': True,
                    'answer': "That's outside my expertise area. I'm SAMARTH, specializing in Indian agriculture and climate data - crop production, rainfall analysis, and irrigation efficiency. How can I help you explore agricultural data?"
                }
    except Exception as e:
        return {
            'success': True,
            'answer': "I'm here to help with Indian agriculture and climate data! Ask me about crop production, rainfall patterns, or water efficiency for any state."
        }

def call_gemini_with_retry(prompt, max_attempts=GEMINI_MAX_ATTEMPTS):
    """
    Call Gemini API with retry logic for rate limits and other errors
    Uses exponential backoff with jitter for better reliability
    
    Args:
        prompt: The prompt to send to Gemini
        max_attempts: Maximum number of attempts (default from config)
    
    Returns:
        Response dict with success flag and text/error
    """
    for attempt in range(max_attempts):
        try:
            response = model.generate_content(prompt)
            return {'success': True, 'text': response.text.strip()}
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Handle rate limiting (429 error)
            if '429' in error_str or 'quota' in error_str or 'rate limit' in error_str:
                if attempt < max_attempts - 1:
                    # Exponential backoff with jitter: 2s, 5s, 10s (+ random 0-2s)
                    wait_time = min(GEMINI_INITIAL_DELAY * (2 ** attempt) + random.uniform(0, 2), 15)
                    print(f"⏱️ Gemini rate limit hit, waiting {wait_time:.1f}s... (Attempt {attempt + 1}/{max_attempts})")
                    time.sleep(wait_time)
                else:
                    return {
                        'success': False,
                        'error': 'rate_limit',
                        'message': '⏱️ AI service is busy right now. Please wait a moment and try again.'
                    }
            
            # Handle timeout
            elif 'timeout' in error_str:
                if attempt < max_attempts - 1:
                    wait_time = GEMINI_INITIAL_DELAY * (attempt + 1) + random.uniform(0, 1)
                    print(f"⏱️ Gemini timeout, retrying in {wait_time:.1f}s... (Attempt {attempt + 1}/{max_attempts})")
                    time.sleep(wait_time)
                else:
                    return {
                        'success': False,
                        'error': 'timeout',
                        'message': '⏱️ AI service is taking too long. Please try again.'
                    }
            
            # Handle blocked content
            elif 'blocked' in error_str or 'safety' in error_str:
                return {
                    'success': False,
                    'error': 'blocked',
                    'message': '⚠️ Unable to process this query. Please rephrase your question.'
                }
            
            # Handle other API errors
            else:
                if attempt < max_attempts - 1:
                    wait_time = GEMINI_INITIAL_DELAY + random.uniform(0, 1)
                    print(f"⚠️ Gemini error: {str(e)[:100]}, retrying in {wait_time:.1f}s... (Attempt {attempt + 1}/{max_attempts})")
                    time.sleep(wait_time)
                else:
                    return {
                        'success': False,
                        'error': 'api_error',
                        'message': f'⚠️ AI service error. Please try again. (Details: {str(e)[:100]})'
                    }
    
    return {
        'success': False,
        'error': 'max_attempts',
        'message': '⚠️ Failed after multiple attempts. Please try again later.'
    }

def parse_user_question(user_question):
    """
    Stage 1: Use Gemini to understand the user's question
    and extract structured information
    
    Args:
        user_question: The natural language question from user
    
    Returns:
        Dictionary with parsed intent and validation
    """
    
    print(f"\n🤔 Parsing question: '{user_question}'")
    
    # Create prompt for Gemini
    prompt = f"""
You are a query parser for an agricultural data system.

AVAILABLE DATA:
- States: {', '.join(AVAILABLE_STATES[:15])}... (33 total)
- Years: Crops (1997-2014), Rainfall (1901-2017)
- Common Crops: {', '.join(COMMON_CROPS[:10])}... (100+ total)
- Metrics: rainfall, crop production, water usage

USER QUESTION: "{user_question}"

TASK: Extract structured information from this question.

Return ONLY valid JSON in this EXACT format (no markdown, no extra text):
{{
  "intent": "comparison | trend | extreme | policy | general",
  "entities": {{
    "states": ["State1", "State2"],
    "crops": ["Crop1"],
    "years": [2010, 2011, 2012],
    "metrics": ["rainfall", "production"]
  }},
  "question_type": "brief description of what user wants",
  "time_period": "description of time range"
}}

RULES:
- Only include states/crops that are clearly mentioned
- For "last 5 years", use [2010, 2011, 2012, 2013, 2014]
- For single year like "2014", use [2014]
- If comparing states, intent is "comparison"
- If asking about trends over time, intent is "trend"
- If asking for highest/lowest/best/worst, intent is "extreme"
- If asking for recommendations/reasons, intent is "policy"
- Normalize state names properly (e.g., "UP" → "Uttar Pradesh")
"""
    
    try:
        # Call Gemini with retry logic
        gemini_response = call_gemini_with_retry(prompt, max_attempts=GEMINI_MAX_ATTEMPTS)
        
        if not gemini_response['success']:
            return {
                'success': False,
                'error': gemini_response.get('message', 'Failed to parse question')
            }
        
        response_text = gemini_response['text']
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            # Extract JSON from markdown
            lines = response_text.split('\n')
            json_lines = []
            in_json = False
            for line in lines:
                if line.strip().startswith('```'):
                    in_json = not in_json
                    continue
                if in_json or (line.strip().startswith('{') or json_lines):
                    json_lines.append(line)
            response_text = '\n'.join(json_lines)
        
        # Parse JSON
        parsed = json.loads(response_text)
        
        print(f"✅ Parsed successfully!")
        print(f"   Intent: {parsed.get('intent')}")
        print(f"   States: {parsed.get('entities', {}).get('states')}")
        print(f"   Crops: {parsed.get('entities', {}).get('crops')}")
        print(f"   Years: {parsed.get('entities', {}).get('years')}")
        
        return {
            'success': True,
            'parsed': parsed,
            'original_question': user_question
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON from Gemini")
        return {
            'success': False,
            'error': 'Could not understand the question format. Please try rephrasing with clearer state names, crop types, and time periods.'
        }
    except Exception as e:
        print(f"❌ Error: {str(e)[:200]}")
        return {
            'success': False,
            'error': f'Unexpected error parsing question. Please try again.'
        }

def validate_parsed_query(parsed_data):
    """
    Stage 1.5: Validate that the parsed query can be answered
    with available data
    """
    
    if not parsed_data.get('success'):
        return {
            'valid': False,
            'reason': 'Failed to parse question',
            'type': 'parse_error'
        }
    
    parsed = parsed_data['parsed']
    entities = parsed.get('entities', {})
    
    # Check for meaningful entities
    has_states = entities.get('states') and len(entities.get('states', [])) > 0
    has_crops = entities.get('crops') and len(entities.get('crops', [])) > 0
    has_years = entities.get('years') and len(entities.get('years', [])) > 0
    has_metrics = entities.get('metrics') and len(entities.get('metrics', [])) > 0
    
    if not (has_states or has_crops or has_metrics):
        return {
            'valid': False,
            'reason': 'Your question is too vague. Please specify states, crops, or metrics.',
            'type': 'too_vague',
            'suggestion': 'Example: "Compare rainfall in Punjab and Haryana for 2010-2014"'
        }
    
    issues = []
    
    # Validate states
    for state in entities.get('states', []):
        if not validate_state(state):
            issues.append(f"State '{state}' not available. Check sidebar for available states.")
    
    # Validate years for crops
    if 'production' in entities.get('metrics', []) or entities.get('crops'):
        for year in entities.get('years', []):
            if year and not validate_year_for_crops(year):
                issues.append(f"Crop data only available for 1997-2014")
                break  # Only show once
    
    # Validate water usage crops
    if 'water' in str(entities.get('metrics', [])).lower():
        crops = entities.get('crops', [])
        if crops and not any(c in WATER_USAGE_CROPS for c in crops):
            issues.append(f"Water usage data only for: {', '.join(WATER_USAGE_CROPS)}")
    
    if issues:
        return {
            'valid': False,
            'reason': '; '.join(issues),
            'type': 'data_unavailable',
            'suggestions': 'Try: Punjab, Haryana (states); Wheat, Rice (crops); 2010-2014 (years)'
        }
    
    return {
        'valid': True,
        'parsed': parsed
    }

def determine_required_apis(parsed_data):
    """
    Stage 2: Determine which APIs need to be called
    based on the parsed query
    
    Args:
        parsed_data: Validated parsed query
    
    Returns:
        List of API calls needed
    """
    
    parsed = parsed_data.get('parsed', {})
    entities = parsed.get('entities', {})
    intent = parsed.get('intent')
    
    apis_needed = []
    
    # Check if rainfall data is needed
    metrics = entities.get('metrics', [])
    if 'rainfall' in metrics or intent in ['comparison', 'trend']:
        apis_needed.append({
            'api': 'rainfall',
            'states': entities.get('states', []),
            'years': entities.get('years', [])
        })
    
    # Check if crop production data is needed
    if 'production' in metrics or entities.get('crops') or intent in ['comparison', 'extreme', 'trend']:
        apis_needed.append({
            'api': 'crops',
            'states': entities.get('states', []),
            'crops': entities.get('crops', []),
            'years': entities.get('years', [])
        })
    
    # Check if water usage data is needed
    if 'water' in str(metrics).lower() or intent == 'policy':
        apis_needed.append({
            'api': 'water',
            'crops': entities.get('crops', [])
        })
    
    print(f"\n📊 APIs needed: {[api['api'] for api in apis_needed]}")
    
    return apis_needed

def generate_intelligent_answer(user_question, parsed_data, fetched_data):
    """
    Stage 3: Use Gemini to generate a natural language answer
    based on the fetched data
    
    Args:
        user_question: Original user question
        parsed_data: Parsed query structure
        fetched_data: Dictionary of fetched data from APIs
    
    Returns:
        Dictionary with generated answer and citations
    """
    
    print(f"\n✍️ Generating intelligent answer...")
    
    # Prepare data summary for Gemini
    data_summary = "AVAILABLE DATA:\n\n"
    
    for key, data in fetched_data.items():
        if not data.get('success'):
            continue
            
        if 'rainfall' in key:
            state = data['state']
            records = data.get('records', [])
            if records:
                data_summary += f"**{state} Rainfall Data:**\n"
                for record in records:
                    year = record.get('year')
                    rainfall = record.get('annual')
                    data_summary += f"  - Year {year}: {rainfall} mm\n"
                data_summary += "\n"
        
        elif 'crops' in key:
            state = data['state']
            records = data.get('records', [])
            if records:
                data_summary += f"**{state} Crop Production Data:**\n"
                # Aggregate by crop
                crop_totals = {}
                for record in records:
                    crop = record.get('crop', 'Unknown')
                    try:
                        production = float(record.get('production_', 0))
                        district = record.get('district_name', 'Unknown')
                        
                        if crop not in crop_totals:
                            crop_totals[crop] = {'total': 0, 'districts': {}}
                        crop_totals[crop]['total'] += production
                        crop_totals[crop]['districts'][district] = production
                    except:
                        continue
                
                # Show top crops
                sorted_crops = sorted(crop_totals.items(), key=lambda x: x[1]['total'], reverse=True)
                for crop, info in sorted_crops[:10]:
                    data_summary += f"  - {crop}: {info['total']:,.0f} tonnes\n"
                    # Show district breakdown if asking about districts
                    if 'district' in user_question.lower():
                        sorted_districts = sorted(info['districts'].items(), key=lambda x: x[1], reverse=True)
                        for district, prod in sorted_districts[:3]:
                            data_summary += f"    • {district}: {prod:,.0f} tonnes\n"
                data_summary += "\n"
        
        elif 'water' in key:
            records = data.get('records', [])
            if records:
                for record in records:
                    crop = record.get('crop')
                    trad_water = record.get('traditional_method___water')
                    drip_water = record.get('drip_irrigation_method___water')
                    savings = record.get('_saving_in_water_')
                    yield_increase = record.get('_increase_in_yield')
                    
                    data_summary += f"**{crop} Water Usage:**\n"
                    data_summary += f"  - Traditional: {trad_water} mm\n"
                    data_summary += f"  - Drip irrigation: {drip_water} mm\n"
                    data_summary += f"  - Water savings: {savings}%\n"
                    data_summary += f"  - Yield increase: {yield_increase}%\n\n"
    
    # Create prompt for Gemini
    prompt = f"""
You are an expert agricultural analyst. Answer the user's question based ONLY on the provided data.

USER QUESTION: "{user_question}"

{data_summary}

INSTRUCTIONS:
1. Answer the question directly and concisely
2. Use natural, professional language
3. Include specific numbers from the data
4. If comparing, clearly state the comparison
5. If asked for reasons/recommendations, provide 3 clear points
6. If asking about trends, describe the pattern
7. Do NOT mention "based on the data" - just answer naturally
8. Keep the answer focused and under 200 words
9. Format with markdown for readability (use bold, bullet points)
10. Be precise with numbers and units

Generate a clear, direct answer:
"""
    
    try:
        # Call Gemini with retry logic
        gemini_response = call_gemini_with_retry(prompt, max_attempts=GEMINI_MAX_ATTEMPTS)
        
        if not gemini_response['success']:
            return {
                'success': False,
                'error': gemini_response.get('message', 'Failed to generate answer')
            }
        
        answer = gemini_response['text']
        
        print(f"✅ Answer generated ({len(answer)} chars)")
        
        return {
            'success': True,
            'answer': answer,
            'data_used': data_summary
        }
        
    except Exception as e:
        print(f"❌ Error generating answer: {str(e)[:200]}")
        return {
            'success': False,
            'error': f'⚠️ Error generating answer. Please try again.'
        }

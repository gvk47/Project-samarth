# gemini_handler.py
# This file handles all Gemini AI interactions

import google.generativeai as genai
import json
from config import GEMINI_KEY
from metadata import *

# Configure Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('models/gemini-2.0-flash')

def is_greeting_or_simple_chat(question):
    """
    Check if the question is just a greeting or simple chat
    Uses word boundaries to avoid false matches like 'hi' in 'highest'
    """
    import re
    
    question_lower = question.lower().strip()
    
    # Greetings - use word boundaries to avoid false matches
    greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 
                 'good evening', 'namaste', 'greetings']
    
    # Check if the ENTIRE message is just a greeting (with optional punctuation)
    if question_lower in greetings:
        return 'greeting'
    
    # Check for greetings as complete words (not substrings)
    for greeting in greetings:
        # Use word boundaries \b to match complete words only
        pattern = r'\b' + re.escape(greeting) + r'\b'
        if re.search(pattern, question_lower):
            # Additional check: if it's only greeting + punctuation, it's a greeting
            if len(question_lower.split()) <= 3:  # "hi there" or "hello!"
                return 'greeting'
    
    # Simple questions about the system
    simple_questions = ['what can you do', 'what do you do', 'help me', 
                       'how does this work', 'what is this', 'tell me about yourself']
    
    for q in simple_questions:
        if q in question_lower:
            return 'help'
    
    return None

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
"""
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
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
        print(f"   Response was: {response_text[:200]}...")
        return {
            'success': False,
            'error': 'Could not parse Gemini response as JSON',
            'raw_response': response_text
        }
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
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
    original_question = parsed_data.get('original_question', '').lower()
    
    # Check if it's a greeting or simple chat
    chat_type = is_greeting_or_simple_chat(original_question)
    if chat_type == 'greeting':
        return {
            'valid': False,
            'reason': 'greeting',
            'type': 'greeting'
        }
    elif chat_type == 'help':
        return {
            'valid': False,
            'reason': 'help_request',
            'type': 'help'
        }
    
    # Check if agriculture-related
    agriculture_keywords = [
        'crop', 'rain', 'rainfall', 'production', 'agriculture', 'wheat', 'rice',
        'irrigation', 'harvest', 'farming', 'cultivation', 'paddy', 'maize',
        'district', 'state', 'cultivation', 'yield', 'water', 'climate',
        'punjab', 'haryana', 'maharashtra', 'karnataka', 'tamil nadu'
    ]
    
    if not any(keyword in original_question for keyword in agriculture_keywords):
        return {
            'valid': False,
            'reason': 'This question is not related to agriculture or climate data.',
            'type': 'out_of_scope',
            'suggestion': 'Please ask questions about crop production, rainfall patterns, or agricultural practices in Indian states.'
        }
    
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
            issues.append(f"State '{state}' not available")
    
    # Validate years for crops
    if 'production' in entities.get('metrics', []) or entities.get('crops'):
        for year in entities.get('years', []):
            if year and not validate_year_for_crops(year):
                issues.append(f"Crop data only available for 1997-2014")
    
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

Generate a clear, direct answer:
"""
    
    try:
        response = model.generate_content(prompt)
        answer = response.text.strip()
        
        print(f"✅ Answer generated!")
        
        return {
            'success': True,
            'answer': answer,
            'data_used': data_summary
        }
        
    except Exception as e:
        print(f"❌ Error generating answer: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
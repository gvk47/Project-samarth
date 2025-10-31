# app.py
# Main Streamlit application - Project SAMARTH

import streamlit as st
from metadata import *
from data_fetcher import *
from gemini_handler import *
import datetime
import sys
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Project SAMARTH - Agriculture Q&A",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - ULTRA COMPACT SIDEBAR
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* ULTRA COMPACT SIDEBAR */
    [data-testid="stSidebar"] {
        font-size: 0.8rem;
        padding-top: 0.5rem;
    }
    
    /* Reduce all internal spacing in sidebar */
    [data-testid="stSidebar"] > div {
        padding-top: 0.3rem;
    }
    
    /* Compact sidebar buttons with minimal spacing */
    [data-testid="stSidebar"] .stButton {
        margin-bottom: 0.15rem;
    }
    
    [data-testid="stSidebar"] .stButton button {
        padding: 0.25rem 0.4rem;
        font-size: 0.75rem;
        margin-bottom: 0;
    }
    
    /* Smaller sidebar headers with less spacing */
    [data-testid="stSidebar"] h2 {
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
        margin-top: 0.25rem;
        font-weight: 600;
    }
    
    /* Thinner separators with minimal margin */
    [data-testid="stSidebar"] hr {
        margin: 0.3rem 0;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Compact expanders in sidebar */
    [data-testid="stSidebar"] .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 3px;
        margin-top: 0.2rem;
        margin-bottom: 0.2rem;
    }
    
    [data-testid="stSidebar"] .stExpander summary {
        padding: 0.25rem 0.4rem;
        font-size: 0.72rem;
    }
    
    [data-testid="stSidebar"] .stExpander [data-testid="stExpanderDetails"] {
        padding: 0.3rem 0.4rem;
    }
    
    /* Compact captions in sidebar */
    [data-testid="stSidebar"] .stCaption {
        font-size: 0.68rem;
        line-height: 1.2;
        margin-bottom: 0.1rem;
    }
    
    /* Tooltip for buttons */
    [data-testid="stSidebar"] .stButton button[title]:hover::after {
        content: attr(title);
        position: absolute;
        left: 0;
        top: 100%;
        width: 95%;
        background-color: rgba(0, 0, 0, 0.85);
        color: #fff;
        padding: 5px;
        border-radius: 4px;
        font-size: 0.7rem;
        z-index: 1000;
        margin-top: 2px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        white-space: normal;
        line-height: 1.3;
    }
    
    .stChatMessage {
        background-color: transparent !important;
    }
    
    /* Cleaner expander in main area */
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        margin-top: 0.5rem;
    }
    
    /* Compact source item */
    .source-item {
        background-color: #f8f9fa;
        border-left: 3px solid #4CAF50;
        padding: 0.6rem;
        margin-bottom: 0.6rem;
        border-radius: 4px;
    }
    
    .source-title {
        font-weight: 600;
        font-size: 0.9rem;
        color: #2E7D32;
        margin-bottom: 0.3rem;
    }
    
    .source-detail {
        font-size: 0.8rem;
        color: #666;
        margin: 0.2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversations' not in st.session_state:
    st.session_state['conversations'] = []

if 'current_conversation_id' not in st.session_state:
    st.session_state['current_conversation_id'] = None

# Helper functions
def get_current_conversation():
    if st.session_state['current_conversation_id'] is None:
        return []
    
    for conv in st.session_state['conversations']:
        if conv['id'] == st.session_state['current_conversation_id']:
            return conv['messages']
    return []

def add_message(role, content, **kwargs):
    if st.session_state['current_conversation_id'] is None:
        conv_id = len(st.session_state['conversations'])
        title = content[:40] + "..." if len(content) > 40 else content
        st.session_state['conversations'].append({
            'id': conv_id,
            'title': title if role == 'user' else 'New Chat',
            'created': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            'messages': []
        })
        st.session_state['current_conversation_id'] = conv_id
    
    for conv in st.session_state['conversations']:
        if conv['id'] == st.session_state['current_conversation_id']:
            message = {
                'role': role,
                'content': content,
                'timestamp': datetime.datetime.now().strftime("%H:%M")
            }
            message.update(kwargs)
            conv['messages'].append(message)
            
            if role == 'user' and len(conv['messages']) == 1:
                conv['title'] = content[:40] + "..." if len(content) > 40 else content
            break

# Sidebar - COMPACT VERSION
with st.sidebar:
    st.markdown("## 💬 Chats")
    
    if st.button("➕ New", use_container_width=True):
        st.session_state['current_conversation_id'] = None
        st.rerun()
    
    st.markdown("---")
    
    # Conversation history
    if st.session_state['conversations']:
        for conv in reversed(st.session_state['conversations'][-5:]):
            is_current = conv['id'] == st.session_state['current_conversation_id']
            icon = "📌" if is_current else "💬"
            
            if st.button(f"{icon} {conv['title'][:35]}...", key=f"conv_{conv['id']}", 
                        use_container_width=True, help=conv['title']):
                st.session_state['current_conversation_id'] = conv['id']
                st.rerun()
    
    st.markdown("---")
    
    # SUGGESTED QUESTIONS - WITH TOOLTIPS
    st.markdown("## 💡 Examples")
    
    questions = [
        {
            'short': 'Q1: Multi-State Comparison',
            'full': 'Compare the average annual rainfall in Punjab and Haryana for 2010-2014. Also list the top 3 most produced crops (by volume) in each state during 2014.'
        },
        {
            'short': 'Q2: District Extremes',
            'full': 'Identify the district in Punjab with the highest wheat production in 2014 and compare that with the district with the lowest wheat production in Haryana in 2014.'
        },
        {
            'short': 'Q3: Trend Analysis',
            'full': 'Analyze the rice production trend in Punjab from 2010 to 2014. Correlate this trend with the rainfall pattern during the same period and provide a summary of the apparent impact.'
        },
        {
            'short': 'Q4: Policy Recommendation',
            'full': 'A policy advisor is proposing to promote cotton cultivation with drip irrigation over traditional methods in Maharashtra. Based on 2010-2014 data, what are the three most compelling data-backed arguments to support this policy?'
        }
    ]
    
    for i, q in enumerate(questions):
        if st.button(q['short'], key=f"sidebar_q_{i}", 
                    use_container_width=True, 
                    help=q['full']):
            st.session_state['selected_question'] = q['full']
            st.rerun()
    
    st.markdown("---")
    st.markdown("## 📊 Data")
    
    with st.expander("📍 States (33)", expanded=False):
        st.caption("Punjab, Haryana, UP, Maharashtra, Karnataka, Gujarat, TN, AP, Telangana, Bihar, WB, Odisha, Rajasthan + 20 more")
    
    with st.expander("🌾 Crops (100+)", expanded=False):
        st.caption("Wheat, Rice, Maize, Cotton, Sugarcane, Bajra, Jowar, Arhar, Gram, Moong, Groundnut + 90 more")
    
    with st.expander("📅 Coverage", expanded=False):
        st.caption("**Rainfall:** 1901-2017")
        st.caption("**Crops:** 1997-2014 (district-level)")
        st.caption("**Water:** 8 crops")

# Main header
st.markdown('<div class="main-header">🌾 Project SAMARTH</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent Q&A System for Agriculture & Climate Data</div>', unsafe_allow_html=True)

st.markdown("---")

# Display conversation
current_messages = get_current_conversation()

for msg in current_messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])
        
        # CLEANER DATA SOURCES SECTION
        if msg['role'] == 'assistant' and 'api_calls' in msg:
            with st.expander("📊 Data Sources & Traceability", expanded=False):
                total_records = sum(c['records'] for c in msg['api_calls'])
                
                st.markdown(f"**{len(msg['api_calls'])} data source(s) • {total_records} records processed**")
                st.markdown("")
                
                for i, call in enumerate(msg['api_calls'], 1):
                    # Compact, clean presentation
                    st.markdown(f"""
                    <div class="source-item">
                        <div class="source-title">Source {i}: {call['dataset']}</div>
                        <div class="source-detail">📍 {call['purpose']}</div>
                        <div class="source-detail">📊 {call['records']} records retrieved</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show API URL in collapsible section
                    with st.expander(f"🔗 View API endpoint", expanded=False):
                        st.code(call['url'], language='text')
                
                st.markdown("---")
                st.caption("💡 All data sourced in real-time from **data.gov.in** (Government of India Open Data Portal)")
                st.caption("🔍 API endpoints above can be used to independently verify all data points")

# Welcome message
if not current_messages:
    st.info("👋 **Welcome to SAMARTH!** Ask questions about Indian agriculture and climate data, or try the example questions in the sidebar.")

# User input
user_input = st.chat_input("Ask about agriculture and climate data...")

# Handle pre-built question
if 'selected_question' in st.session_state and st.session_state.get('selected_question'):
    user_input = st.session_state['selected_question']
    st.session_state['selected_question'] = None

# Process question
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    
    add_message('user', user_input)
    
    with st.chat_message("assistant"):
        # HIDE PRINT STATEMENTS - Redirect stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            with st.spinner("✨ Generating answer..."):
                
                # Check for greetings
                chat_type = is_greeting_or_simple_chat(user_input)
                
                if chat_type == 'greeting':
                    response = "Hello! 👋 I'm SAMARTH, your agriculture and climate data assistant.\n\nI can help you analyze:\n- 🌧️ Rainfall patterns across states\n- 🌾 Crop production trends\n- 📊 District-level comparisons\n- 💧 Water efficiency recommendations\n\nTry the example questions in the sidebar!"
                    
                    sys.stdout = old_stdout
                    st.markdown(response)
                    add_message('assistant', response)
                
                elif chat_type == 'help':
                    response = "I can help you with questions about Indian agriculture and climate data!\n\n**Available:**\n- 📍 33 states\n- 🌾 100+ crops\n- 📅 Rainfall: 1901-2017\n- 📅 Crops: 1997-2014\n\n**Check the sidebar for examples!**"
                    
                    sys.stdout = old_stdout
                    st.markdown(response)
                    add_message('assistant', response)
                
                # Parse and validate
                parsed = parse_user_question(user_input)
                
                if not parsed['success']:
                    error_msg = "❌ I couldn't understand your question.\n\n💡 Include:\n- State names (Punjab, Haryana, etc.)\n- Crop types (wheat, rice, etc.)\n- Time periods (2010-2014, etc.)\n\n📌 Check sidebar for examples!"
                    
                    sys.stdout = old_stdout
                    st.markdown(error_msg)
                    add_message('assistant', error_msg)
                
                validation = validate_parsed_query(parsed)
                
                if not validation['valid']:
                    if validation['type'] == 'out_of_scope':
                        error_msg = f"❌ {validation['reason']}\n\n💡 **Ask about agriculture/climate only:**\n- Crop production\n- Rainfall patterns\n- District data\n- Irrigation methods\n\n📌 Try sidebar examples!"
                    elif validation['type'] == 'too_vague':
                        error_msg = f"❌ {validation['reason']}\n\n💡 **Be specific:**\n- States: Punjab, Maharashtra, etc.\n- Crops: wheat, rice, cotton, etc.\n- Years: 2010-2014, etc.\n\n📌 Check sidebar!"
                    else:
                        error_msg = f"❌ {validation['reason']}"
                        if validation.get('suggestions'):
                            error_msg += f"\n\n💡 {validation['suggestions']}"
                    
                    sys.stdout = old_stdout
                    st.markdown(error_msg)
                    add_message('assistant', error_msg)
                
                # Fetch data
                apis_needed = determine_required_apis(parsed)
                
                fetched_data = {}
                api_calls_made = []
                
                for api_spec in apis_needed:
                    if api_spec['api'] == 'rainfall':
                        for state in api_spec['states']:
                            key = f"rainfall_{state}"
                            data = fetch_rainfall_annual(state, api_spec['years'])
                            if data.get('success'):
                                fetched_data[key] = data
                                api_calls_made.append({
                                    'purpose': f'Rainfall data for {state} ({min(api_spec["years"])}-{max(api_spec["years"])})',
                                    'url': data.get('api_url', 'N/A'),
                                    'records': data.get('total_matched', 0),
                                    'dataset': 'IMD Rainfall Data'
                                })
                    
                    elif api_spec['api'] == 'crops':
                        for state in api_spec['states']:
                            key = f"crops_{state}"
                            year = max(api_spec['years']) if api_spec['years'] else 2014
                            crop = api_spec['crops'][0] if api_spec['crops'] else None
                            data = fetch_crop_production(state, crop_name=crop, year=year)
                            if data.get('success'):
                                fetched_data[key] = data
                                api_calls_made.append({
                                    'purpose': f'Crop production for {state} in {year}',
                                    'url': data.get('api_url', 'N/A'),
                                    'records': data.get('total_records', 0),
                                    'dataset': 'Ministry of Agriculture - Crop Production'
                                })
                    
                    elif api_spec['api'] == 'water':
                        crops_to_check = api_spec['crops'] if api_spec['crops'] else ['Cotton']
                        for crop in crops_to_check:
                            if crop in WATER_USAGE_CROPS:
                                key = f"water_{crop}"
                                data = fetch_water_usage(crop)
                                if data.get('success'):
                                    fetched_data[key] = data
                                    api_calls_made.append({
                                        'purpose': f'Water efficiency data for {crop}',
                                        'url': data.get('api_url', 'N/A'),
                                        'records': data.get('total_records', 0),
                                        'dataset': 'ICAR Water Efficiency Comparison'
                                    })
                
                if not fetched_data:
                    error_msg = "❌ No data found.\n\n**Try:**\n- States: Punjab, Haryana, Maharashtra\n- Years: 2010-2014\n- Crops: wheat, rice, cotton\n\n📌 Check sidebar for availability!"
                    
                    sys.stdout = old_stdout
                    st.markdown(error_msg)
                    add_message('assistant', error_msg)
                
                # Generate answer
                answer_result = generate_intelligent_answer(user_input, parsed, fetched_data)
                
                # Restore stdout
                sys.stdout = old_stdout
                
                if answer_result['success']:
                    st.markdown(answer_result['answer'])
                    add_message('assistant', answer_result['answer'], api_calls=api_calls_made)
                else:
                    error_msg = f"❌ Error: {answer_result.get('error')}"
                    st.markdown(error_msg)
                    add_message('assistant', error_msg)
        
        except Exception as e:
            # Restore stdout in case of error
            sys.stdout = old_stdout
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8rem; padding: 0.8rem;'>
    <p><strong>🌾 Project SAMARTH</strong> - Agriculture & Climate Data Intelligence</p>
    <p style='font-size: 0.7rem;'>Powered by Gemini AI • Real-time data from data.gov.in</p>
</div>
""", unsafe_allow_html=True)

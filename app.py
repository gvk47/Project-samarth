# app.py
# Main Streamlit application - Project SAMARTH
# Production-ready version with full optimization

import streamlit as st
from metadata import *
from data_fetcher import *
from gemini_handler import *
import datetime
import sys
from io import StringIO
import gc  # Garbage collection for memory management

# Page configuration
st.set_page_config(
    page_title="Project SAMARTH - Agriculture Q&A",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - PRODUCTION OPTIMIZED
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
    
    [data-testid="stSidebar"] > div {
        padding-top: 0.3rem;
    }
    
    [data-testid="stSidebar"] .stButton {
        margin-bottom: 0.15rem;
    }
    
    [data-testid="stSidebar"] .stButton button {
        padding: 0.25rem 0.4rem;
        font-size: 0.75rem;
        margin-bottom: 0;
    }
    
    [data-testid="stSidebar"] h2 {
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
        margin-top: 0.25rem;
        font-weight: 600;
    }
    
    [data-testid="stSidebar"] hr {
        margin: 0.3rem 0;
        border-top: 1px solid #e0e0e0;
    }
    
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
        font-size: 0.7rem;
        line-height: 1.3;
    }
    
    [data-testid="stSidebar"] .stCaption {
        font-size: 0.68rem;
        line-height: 1.2;
        margin-bottom: 0.1rem;
    }
    
    /* Question text in expander */
    .example-question-text {
        font-size: 0.7rem;
        line-height: 1.4;
        color: #ccc;
    }
    
    .stChatMessage {
        background-color: transparent !important;
    }
    
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        margin-top: 0.5rem;
    }
    
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
    
    .api-url-box {
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 3px;
        padding: 0.5rem;
        margin-top: 0.3rem;
        font-size: 0.7rem;
        font-family: monospace;
        word-break: break-all;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with limits
if 'conversations' not in st.session_state:
    st.session_state['conversations'] = []

if 'current_conversation_id' not in st.session_state:
    st.session_state['current_conversation_id'] = None

if 'pending_question' not in st.session_state:
    st.session_state['pending_question'] = None

if 'question_count' not in st.session_state:
    st.session_state['question_count'] = 0

# MEMORY MANAGEMENT: Limit conversation history
MAX_CONVERSATIONS = 10
MAX_MESSAGES_PER_CONV = 20

def cleanup_old_conversations():
    """Remove old conversations to prevent memory buildup"""
    if len(st.session_state['conversations']) > MAX_CONVERSATIONS:
        # Keep only the most recent conversations
        st.session_state['conversations'] = st.session_state['conversations'][-MAX_CONVERSATIONS:]
        
        # If current conversation was deleted, reset
        current_id = st.session_state.get('current_conversation_id')
        if current_id is not None:
            conv_ids = [c['id'] for c in st.session_state['conversations']]
            if current_id not in conv_ids:
                st.session_state['current_conversation_id'] = None

def get_current_conversation():
    if st.session_state['current_conversation_id'] is None:
        return []
    
    for conv in st.session_state['conversations']:
        if conv['id'] == st.session_state['current_conversation_id']:
            # Limit messages per conversation
            return conv['messages'][-MAX_MESSAGES_PER_CONV:]
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
            
            # Limit messages per conversation
            if len(conv['messages']) > MAX_MESSAGES_PER_CONV:
                conv['messages'] = conv['messages'][-MAX_MESSAGES_PER_CONV:]
            
            if role == 'user' and len(conv['messages']) == 1:
                conv['title'] = content[:40] + "..." if len(content) > 40 else content
            break
    
    # Cleanup after adding message
    cleanup_old_conversations()

# Sidebar
with st.sidebar:
    st.markdown("## 💬 Chats")
    
    if st.button("➕ New", use_container_width=True):
        st.session_state['current_conversation_id'] = None
        st.session_state['question_count'] = 0
        gc.collect()  # Force garbage collection
        st.rerun()
    
    st.markdown("---")
    
    # Conversation history - show last 5 only
    if st.session_state['conversations']:
        for conv in reversed(st.session_state['conversations'][-5:]):
            is_current = conv['id'] == st.session_state['current_conversation_id']
            icon = "📌" if is_current else "💬"
            
            if st.button(f"{icon} {conv['title'][:30]}...", key=f"conv_{conv['id']}", 
                        use_container_width=True):
                st.session_state['current_conversation_id'] = conv['id']
                st.session_state['question_count'] = len(conv['messages']) // 2
                st.rerun()
    
    st.markdown("---")
    
    # FIXED: Example questions as EXPANDERS (not tooltips)
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
        with st.expander(q['short'], expanded=False):
            st.markdown(f"<div class='example-question-text'>{q['full']}</div>", unsafe_allow_html=True)
            if st.button("Ask this question", key=f"ask_q_{i}", use_container_width=True):
                st.session_state['pending_question'] = q['full']
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
        
        # Only show data sources when api_calls exist AND have data
        if msg['role'] == 'assistant' and 'api_calls' in msg and len(msg.get('api_calls', [])) > 0:
            with st.expander("📊 Data Sources & Traceability", expanded=False):
                total_records = sum(c.get('records', 0) for c in msg['api_calls'])
                
                st.markdown(f"**{len(msg['api_calls'])} data source(s) • {total_records} records processed**")
                st.markdown("")
                
                for i, call in enumerate(msg['api_calls'], 1):
                    st.markdown(f"""
                    <div class="source-item">
                        <div class="source-title">Source {i}: {call.get('dataset', 'Unknown')}</div>
                        <div class="source-detail">📍 {call.get('purpose', 'N/A')}</div>
                        <div class="source-detail">📊 {call.get('records', 0)} records retrieved</div>
                        <div class="api-url-box">🔗 API: {call.get('url', 'N/A')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.caption("💡 All data sourced in real-time from **data.gov.in** (Government of India Open Data Portal)")
                st.caption("🔍 API endpoints above can be used to independently verify all data points")

# Welcome message
if not current_messages:
    st.info("👋 **Welcome to SAMARTH!** Ask questions about Indian agriculture and climate data, or try the example questions in the sidebar.")

# User input
user_input = st.chat_input("Ask about agriculture and climate data...")

# Handle pre-built question from sidebar
if st.session_state.get('pending_question'):
    user_input = st.session_state['pending_question']
    st.session_state['pending_question'] = None

# Process question
if user_input:
    # Increment question count
    st.session_state['question_count'] += 1
    
    # Display user message IMMEDIATELY
    with st.chat_message("user"):
        st.markdown(user_input)
    
    add_message('user', user_input)
    
    with st.chat_message("assistant"):
        # Redirect stdout to hide print statements
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            with st.spinner("✨ Generating answer..."):
                
                # Check if agriculture-related
                is_agriculture_query = check_if_agriculture_query(user_input)
                
                if not is_agriculture_query:
                    # Handle general queries naturally
                    response_result = handle_general_query(user_input)
                    
                    sys.stdout = old_stdout
                    st.markdown(response_result['answer'])
                    add_message('assistant', response_result['answer'])
                
                else:
                    # Parse agriculture query
                    parsed = parse_user_question(user_input)
                    
                    if not parsed['success']:
                        error_msg = f"❌ I couldn't understand your question.\n\n{parsed.get('error', '')}\n\n💡 **Try:**\n- State names (Punjab, Haryana)\n- Crop types (wheat, rice)\n- Time periods (2010-2014)\n\n📌 Check sidebar for examples!"
                        
                        sys.stdout = old_stdout
                        st.markdown(error_msg)
                        add_message('assistant', error_msg)
                    else:
                        validation = validate_parsed_query(parsed)
                        
                        if not validation['valid']:
                            if validation['type'] == 'too_vague':
                                error_msg = f"❌ {validation['reason']}\n\n💡 **Be specific:**\n- States: Punjab, Maharashtra\n- Crops: wheat, rice, cotton\n- Years: 2010-2014\n\n📌 Check sidebar!"
                            else:
                                error_msg = f"❌ {validation['reason']}"
                                if validation.get('suggestions'):
                                    error_msg += f"\n\n💡 {validation['suggestions']}"
                            
                            sys.stdout = old_stdout
                            st.markdown(error_msg)
                            add_message('assistant', error_msg)
                        else:
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
                            else:
                                # Generate answer
                                answer_result = generate_intelligent_answer(user_input, parsed, fetched_data)
                                
                                sys.stdout = old_stdout
                                
                                if answer_result['success']:
                                    st.markdown(answer_result['answer'])
                                    add_message('assistant', answer_result['answer'], api_calls=api_calls_made)
                                else:
                                    error_msg = f"❌ Error: {answer_result.get('error')}"
                                    st.markdown(error_msg)
                                    add_message('assistant', error_msg)
            
            # Force garbage collection after each question
            gc.collect()
        
        except Exception as e:
            sys.stdout = old_stdout
            error_msg = f"❌ An error occurred. Please try again or use a different question."
            st.error(error_msg)
            add_message('assistant', error_msg)
            gc.collect()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8rem; padding: 0.8rem;'>
    <p><strong>🌾 Project SAMARTH</strong> - Agriculture & Climate Data Intelligence</p>
    <p style='font-size: 0.7rem;'>Powered by Gemini AI • Real-time data from data.gov.in</p>
</div>
""", unsafe_allow_html=True)

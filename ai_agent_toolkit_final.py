#!/usr/bin/env python3
"""
🤖 AI AGENT TOOLKIT - FINAL ENHANCED STREAMLIT APPLICATION
A comprehensive Streamlit application featuring specialized AI business assistants
with OpenAI API integration, Supabase authentication, custom bot creation, 
personalization features, and modern UI.
"""

import streamlit as st
from openai import OpenAI
import tiktoken
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Tuple, Optional, Any
import logging
import hashlib
import os
import pandas as pd
import io
import base64
import requests
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================================================
# 🎨 STREAMLIT CONFIGURATION & STYLING
# ======================================================

# Hide Streamlit settings and menu
st.set_page_config(
    page_title="🤖 AI Agent Toolkit",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Enhanced styling for the AI Agent Toolkit
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
.stDecoration {display:none;}

/* Custom styling for AI Agent Toolkit */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.agent-card {
    background: #ff6b6b;
    color: black;
    padding: 20px;
    border-radius: 15px;
    margin: 10px 0;
    border-left: 4px solid #667eea;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.agent-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
}

.custom-bot-card {
    background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
    color: black;
    padding: 20px;
    border-radius: 15px;
    margin: 10px 0;
    border-left: 4px solid #e17055;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.custom-bot-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(225, 112, 85, 0.2);
}

.chat-container {
    max-width: 100%;
    margin: 0 auto;
}

.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px 20px;
    border-radius: 20px 20px 5px 20px;
    margin: 10px 0 10px 50px;
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.assistant-message {
    background: #ff6b6b;
    color: black;
    padding: 15px 20px;
    border-radius: 20px 20px 20px 5px;
    margin: 10px 50px 10px 0;
    border-left: 4px solid #667eea;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.feature-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.9em;
    cursor: pointer;
    margin: 5px;
    transition: all 0.3s ease;
}

.feature-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.stButton > button {
    border-radius: 25px;
    border: none;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 10px 20px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.sidebar-section {
    background: rgba(102, 126, 234, 0.05);
    padding: 15px;
    border-radius: 15px;
    margin: 15px 0;
    border-left: 4px solid #667eea;
}

.metric-display {
    background: #ff6b6b;
    color: black;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin: 10px 0;
}

/* Logo styling */
.logo-container {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
}

.logo-image {
    max-width: 100px;
    height: auto;
    margin-right: 15px;
}

/* Page navigation styling */
.page-nav {
    background: rgba(102, 126, 234, 0.1);
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 20px;
}

/* User preferences styling */
.preference-card {
    background: #ff6b6b;
    color: black;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #667eea;
}

/* Responsive design */
@media (max-width: 768px) {
    .user-message, .assistant-message {
        margin-left: 10px;
        margin-right: 10px;
    }
}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ======================================================
# 🔑 API CONFIGURATION
# ======================================================

def initialize_openai():
    """Initialize OpenAI client with API key from secrets or environment"""
    try:
        # Try Streamlit secrets first
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            api_key = st.secrets['OPENAI_API_KEY']
            return OpenAI(api_key=api_key), api_key
        
        # Fallback to environment variable
        elif 'OPENAI_API_KEY' in os.environ:
            api_key = os.environ['OPENAI_API_KEY']
            return OpenAI(api_key=api_key), api_key
        
        # No API key found
        return None, None
        
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI: {str(e)}")
        return None, None

# ======================================================
# 🤖 AI AGENT PERSONALITIES (PREDEFINED)
# ======================================================

BOT_PERSONALITIES = {
    # ENTREPRENEURSHIP & STARTUPS
    "Startup Strategist": {
        "description": "I specialize in helping new businesses with planning and execution. From MVP development to scaling strategies, I guide entrepreneurs through every stage of their startup journey.",
        "emoji": "🚀",
        "category": "Entrepreneurship & Startups",
        "temperature": 0.7,
        "specialties": ["Business Planning", "MVP Development", "Product-Market Fit", "Growth Hacking"],
        "quick_actions": ["Create Business Plan", "Validate Idea", "Find Co-founder", "Pitch Deck Help"],
        "is_custom": False
    },
    "Business Plan Writer": {
        "description": "I create comprehensive, investor-ready business plans. I help entrepreneurs articulate their vision, analyze markets, and present financial projections.",
        "emoji": "📝",
        "category": "Entrepreneurship & Startups",
        "temperature": 0.6,
        "specialties": ["Business Plans", "Market Analysis", "Financial Projections", "Investor Presentations"],
        "quick_actions": ["Write Executive Summary", "Market Research", "Financial Model", "Competitive Analysis"],
        "is_custom": False
    },
    "Venture Capital Advisor": {
        "description": "I guide startups through fundraising and investment landscapes. I specialize in pitch deck creation, investor relations, and valuation strategies.",
        "emoji": "💼",
        "category": "Entrepreneurship & Startups",
        "temperature": 0.6,
        "specialties": ["Fundraising", "Pitch Decks", "Investor Relations", "Valuation"],
        "quick_actions": ["Create Pitch Deck", "Find Investors", "Prepare Due Diligence", "Valuation Help"],
        "is_custom": False
    },

    # SALES & MARKETING
    "Sales Performance Coach": {
        "description": "I help individuals and teams maximize sales potential through proven methodologies. I specialize in sales funnel optimization and conversion improvement.",
        "emoji": "💼",
        "category": "Sales & Marketing",
        "temperature": 0.8,
        "specialties": ["Sales Funnels", "Conversion Optimization", "Objection Handling", "Closing Techniques"],
        "quick_actions": ["Sales Script", "Objection Handling", "Pipeline Review", "Closing Tips"],
        "is_custom": False
    },
    "Marketing Strategy Expert": {
        "description": "I have deep expertise in digital marketing, brand positioning, and customer acquisition. I help businesses build compelling campaigns.",
        "emoji": "📱",
        "category": "Sales & Marketing",
        "temperature": 0.8,
        "specialties": ["Digital Marketing", "Brand Positioning", "Customer Acquisition", "Campaign Strategy"],
        "quick_actions": ["Marketing Plan", "Brand Strategy", "Campaign Ideas", "Target Audience"],
        "is_custom": False
    },
    "Content Marketing Strategist": {
        "description": "I create engaging content that attracts and converts audiences. I develop content strategies, editorial calendars, and storytelling frameworks.",
        "emoji": "✍️",
        "category": "Sales & Marketing",
        "temperature": 0.8,
        "specialties": ["Content Strategy", "Editorial Calendars", "Storytelling", "Brand Authority"],
        "quick_actions": ["Content Calendar", "Blog Ideas", "Social Posts", "Video Scripts"],
        "is_custom": False
    },

    # FINANCE & ACCOUNTING
    "Financial Controller": {
        "description": "I specialize in business financial management, budgeting, and financial planning. I help optimize financial operations and manage cash flow.",
        "emoji": "💰",
        "category": "Finance & Accounting",
        "temperature": 0.5,
        "specialties": ["Financial Planning", "Budget Management", "Cash Flow", "Cost Control"],
        "quick_actions": ["Budget Planning", "Cash Flow Analysis", "Cost Reduction", "Financial Reports"],
        "is_custom": False
    },
    "Investment Banking Advisor": {
        "description": "I provide expertise in corporate finance, M&A, and capital raising. I help evaluate opportunities, structure deals, and conduct valuations.",
        "emoji": "🏦",
        "category": "Finance & Accounting",
        "temperature": 0.5,
        "specialties": ["Corporate Finance", "M&A", "Capital Raising", "Valuations"],
        "quick_actions": ["Deal Analysis", "Valuation Model", "M&A Strategy", "Capital Structure"],
        "is_custom": False
    },

    # TECHNOLOGY & INNOVATION
    "Digital Transformation Consultant": {
        "description": "I help organizations leverage technology to transform business models and operations. I specialize in digital strategy and change management.",
        "emoji": "🔄",
        "category": "Technology & Innovation",
        "temperature": 0.7,
        "specialties": ["Digital Strategy", "Technology Adoption", "Change Management", "Innovation"],
        "quick_actions": ["Digital Roadmap", "Tech Assessment", "Change Plan", "Innovation Strategy"],
        "is_custom": False
    },
    "AI Strategy Consultant": {
        "description": "I help businesses leverage artificial intelligence for competitive advantage. I specialize in AI implementation and automation strategies.",
        "emoji": "🤖",
        "category": "Technology & Innovation",
        "temperature": 0.7,
        "specialties": ["AI Implementation", "Machine Learning", "Automation", "AI Strategy"],
        "quick_actions": ["AI Roadmap", "Use Case Analysis", "Automation Plan", "ML Strategy"],
        "is_custom": False
    },

    # OPERATIONS & MANAGEMENT
    "Operations Excellence Manager": {
        "description": "I focus on streamlining processes and maximizing efficiency. I specialize in process improvement, supply chain optimization, and lean methodologies.",
        "emoji": "⚙️",
        "category": "Operations & Management",
        "temperature": 0.6,
        "specialties": ["Process Improvement", "Supply Chain", "Lean Methodologies", "Efficiency"],
        "quick_actions": ["Process Map", "Efficiency Audit", "Workflow Design", "Cost Optimization"],
        "is_custom": False
    },
    "Project Management Expert": {
        "description": "I help organizations deliver projects on time and within budget. I specialize in planning, resource allocation, and risk management.",
        "emoji": "📋",
        "category": "Operations & Management",
        "temperature": 0.6,
        "specialties": ["Project Planning", "Resource Management", "Risk Management", "Stakeholder Communication"],
        "quick_actions": ["Project Plan", "Risk Assessment", "Team Structure", "Timeline Creation"],
        "is_custom": False
    },

    # HUMAN RESOURCES
    "Human Resources Director": {
        "description": "I provide strategic HR guidance for organizational development. I specialize in talent management, culture building, and performance optimization.",
        "emoji": "👥",
        "category": "Human Resources",
        "temperature": 0.7,
        "specialties": ["Talent Management", "Culture Building", "Performance Management", "Employee Engagement"],
        "quick_actions": ["Hiring Strategy", "Performance Review", "Culture Assessment", "Team Building"],
        "is_custom": False
    },
    "Talent Acquisition Specialist": {
        "description": "I help organizations attract and hire top talent. I specialize in recruitment strategies, candidate assessment, and employer branding.",
        "emoji": "🎯",
        "category": "Human Resources",
        "temperature": 0.7,
        "specialties": ["Recruitment Strategy", "Candidate Assessment", "Employer Branding", "Interview Process"],
        "quick_actions": ["Job Description", "Interview Questions", "Candidate Screening", "Offer Strategy"],
        "is_custom": False
    }
}

# ======================================================
# 🗄️ ENHANCED DATA MANAGEMENT WITH SUPABASE INTEGRATION
# ======================================================

# Import enhanced Supabase integration
try:
    from supabase_integration import enhanced_auth
except ImportError:
    # Fallback to basic auth if enhanced integration is not available
    from auth import auth as enhanced_auth

def load_custom_bots(user_id: str) -> Dict[str, Dict]:
    """Load custom bots for a specific user"""
    try:
        return enhanced_auth.load_custom_bots(user_id)
    except AttributeError:
        # Fallback to session state if enhanced auth doesn't have this method
        if 'custom_bots' not in st.session_state:
            st.session_state.custom_bots = {}
        return st.session_state.custom_bots.get(user_id, {})

def save_custom_bot(user_id: str, bot_name: str, bot_data: Dict) -> bool:
    """Save a custom bot for a specific user"""
    try:
        return enhanced_auth.save_custom_bot(user_id, bot_name, bot_data)
    except AttributeError:
        # Fallback to session state
        try:
            if 'custom_bots' not in st.session_state:
                st.session_state.custom_bots = {}
            
            if user_id not in st.session_state.custom_bots:
                st.session_state.custom_bots[user_id] = {}
            
            bot_data['is_custom'] = True
            bot_data['created_at'] = datetime.now().isoformat()
            bot_data['updated_at'] = datetime.now().isoformat()
            
            st.session_state.custom_bots[user_id][bot_name] = bot_data
            return True
        except Exception as e:
            logger.error(f"Error saving custom bot: {str(e)}")
            return False

def delete_custom_bot(user_id: str, bot_name: str) -> bool:
    """Delete a custom bot for a specific user"""
    try:
        return enhanced_auth.delete_custom_bot(user_id, bot_name)
    except AttributeError:
        # Fallback to session state
        try:
            if ('custom_bots' in st.session_state and 
                user_id in st.session_state.custom_bots and 
                bot_name in st.session_state.custom_bots[user_id]):
                del st.session_state.custom_bots[user_id][bot_name]
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting custom bot: {str(e)}")
            return False

def get_all_bots(user_id: str) -> Dict[str, Dict]:
    """Get all bots (predefined + custom) for a user"""
    all_bots = BOT_PERSONALITIES.copy()
    custom_bots = load_custom_bots(user_id)
    all_bots.update(custom_bots)
    return all_bots

def load_user_preferences(user_id: str) -> Dict[str, Any]:
    """Load user preferences"""
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {}
    
    if user_id not in st.session_state.user_preferences:
        # Default preferences
        st.session_state.user_preferences[user_id] = {
            'default_model': 'gpt-4',
            'default_temperature': 0.7,
            'chat_history_limit': 50,
            'auto_save_chats': True,
            'theme': 'default'
        }
    
    return st.session_state.user_preferences[user_id]

def save_user_preferences(user_id: str, preferences: Dict[str, Any]) -> bool:
    """Save user preferences"""
    try:
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = {}
        
        st.session_state.user_preferences[user_id] = preferences
        return True
    except Exception as e:
        logger.error(f"Error saving user preferences: {str(e)}")
        return False

def load_persistent_chat_history(user_id: str) -> List[Dict]:
    """Load persistent chat history"""
    try:
        return enhanced_auth.load_chat_history(user_id)
    except AttributeError:
        # Fallback - return empty list, session state manages this
        return []

def save_chat_message(user_id: str, agent_name: str, user_message: str, agent_response: str) -> bool:
    """Save a chat message persistently"""
    try:
        return enhanced_auth.save_chat_message(user_id, agent_name, user_message, agent_response)
    except AttributeError:
        # Fallback - return True, session state manages this
        return True

# ======================================================
# 🧠 ENHANCED AGENT PROMPT GENERATION
# ======================================================

def get_agent_prompt(agent_name: str, user_id: str = None) -> str:
    """Generate system prompt for an agent (predefined or custom)"""
    all_bots = get_all_bots(user_id) if user_id else BOT_PERSONALITIES
    agent = all_bots.get(agent_name)
    
    if not agent:
        return "You are a helpful AI assistant."
    
    # For custom bots, use their system_prompt if available
    if agent.get('is_custom', False) and 'system_prompt' in agent:
        return agent['system_prompt']
    
    # For predefined bots, generate prompt from description and specialties
    prompt = f"""You are {agent_name}, {agent['description']}

Your specialties include: {', '.join(agent.get('specialties', []))}

You should respond in a professional, helpful manner while staying true to your role and expertise. 
Provide actionable advice and insights based on your specialization.
Keep your responses concise but comprehensive, and always aim to provide practical value.
"""
    return prompt

# ======================================================
# 💬 ENHANCED CHAT FUNCTIONALITY
# ======================================================

def chat_with_agent(user_message: str, agent_name: str, user_id: str = None) -> str:
    """Chat with an AI agent using OpenAI API with enhanced personalization"""
    client, api_key = initialize_openai()
    
    if not client:
        return "⚠️ OpenAI API key not configured. Please add your API key to continue."
    
    try:
        all_bots = get_all_bots(user_id) if user_id else BOT_PERSONALITIES
        agent = all_bots.get(agent_name, all_bots.get("Startup Strategist"))
        
        # Get user preferences for model and temperature
        user_prefs = load_user_preferences(user_id) if user_id else {}
        model = user_prefs.get('default_model', 'gpt-4')
        temperature = agent.get('temperature', user_prefs.get('default_temperature', 0.7))
        
        messages = [
            {"role": "system", "content": get_agent_prompt(agent_name, user_id)},
            {"role": "user", "content": user_message}
        ]
        
        # Add recent chat history for context
        if st.session_state.chat_history:
            recent_history = st.session_state.chat_history[-6:]  # Last 3 exchanges
            for msg in recent_history:
                if msg['agent'] == agent_name:
                    messages.insert(-1, {"role": "assistant", "content": msg['response']})
                    messages.insert(-1, {"role": "user", "content": msg['message']})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=1000
        )
        
        agent_response = response.choices[0].message.content
        
        # Save to persistent storage if available
        if user_id:
            save_chat_message(user_id, agent_name, user_message, agent_response)
        
        return agent_response
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return f"❌ Error: {str(e)}"

# ======================================================
# 🔐 AUTHENTICATION FUNCTIONS
# ======================================================

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'selected_agent' not in st.session_state:
        st.session_state.selected_agent = "Startup Strategist"
    if 'auth_mode' not in st.session_state:
        st.session_state.auth_mode = "login"
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Chat"
    if 'custom_bots' not in st.session_state:
        st.session_state.custom_bots = {}
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {}

def login_form():
    """Display login/signup form with Supabase integration"""
    # Display logo and banner
    col1, col2 = st.columns([1, 2])
    with col1:
        display_logo()
    with col2:
        st.markdown("""
        <div class="main-header">
            <h1>🤖 AI Agent Toolkit</h1>
            <p>Your comprehensive suite of AI business assistants</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display banner image if available
    try:
        if os.path.exists("ai_agent_toolkit_banner.png"):
            banner = Image.open("ai_agent_toolkit_banner.png")
            st.image(banner, use_column_width=True)
    except:
        pass
    
    # Authentication mode selector
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_mode = st.radio(
            "Choose an option:",
            ["Login", "Sign Up", "Reset Password"],
            horizontal=True,
            key="auth_mode_selector"
        )
        
        st.session_state.auth_mode = auth_mode.lower().replace(" ", "_")
    
    # Authentication forms
    if st.session_state.auth_mode == "login":
        login_section()
    elif st.session_state.auth_mode == "sign_up":
        signup_section()
    elif st.session_state.auth_mode == "reset_password":
        reset_password_section()
    
    # Demo mode notice
    if not enhanced_auth.is_configured():
        st.info("🔧 **Demo Mode**: Supabase not configured. You can use any email/password to login.")

def login_section():
    """Login form section"""
    with st.form("login_form"):
        st.subheader("🔑 Login to Your Account")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        
        login_submitted = st.form_submit_button("Login", type="primary")
        
        if login_submitted:
            if email and password:
                with st.spinner("Signing in..."):
                    result = enhanced_auth.sign_in(email, password)
                    
                if result['success']:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_id = result['user'].get('id', 'demo-user')
                    
                    # Load persistent chat history if available
                    persistent_history = load_persistent_chat_history(st.session_state.user_id)
                    if persistent_history:
                        st.session_state.chat_history = persistent_history
                    
                    st.success(result['message'])
                    st.rerun()
                else:
                    st.error(result['error'])
            else:
                st.error("Please enter both email and password")

def signup_section():
    """Signup form section"""
    with st.form("signup_form"):
        st.subheader("📝 Create New Account")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        signup_submitted = st.form_submit_button("Create Account", type="primary")
        
        if signup_submitted:
            if email and password and confirm_password:
                if password == confirm_password:
                    with st.spinner("Creating account..."):
                        result = enhanced_auth.sign_up(email, password)
                        
                    if result['success']:
                        st.success(result['message'])
                    else:
                        st.error(result['error'])
                else:
                    st.error("Passwords do not match")
            else:
                st.error("Please fill in all fields")

def reset_password_section():
    """Reset password form section"""
    with st.form("reset_form"):
        st.subheader("🔄 Reset Password")
        email = st.text_input("Email Address")
        
        reset_submitted = st.form_submit_button("Send Reset Link", type="primary")
        
        if reset_submitted:
            if email:
                with st.spinner("Sending reset link..."):
                    result = enhanced_auth.reset_password(email)
                    
                if result['success']:
                    st.success(result['message'])
                else:
                    st.error(result['error'])
            else:
                st.error("Please enter your email address")

# ======================================================
# 🎨 ENHANCED UI COMPONENTS
# ======================================================

def display_logo():
    """Display the AI Agent Toolkit logo"""
    try:
        # Try to load the logo image
        if os.path.exists("ai_agent_toolkit_logo.png"):
            logo = Image.open("ai_agent_toolkit_logo.png")
            st.image(logo, width=150)
        else:
            st.markdown("🤖")
    except:
        st.markdown("🤖")

def display_page_navigation():
    """Display page navigation in sidebar"""
    st.markdown("""
    <div class="sidebar-section">
        <h3>📄 Navigation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    pages = ["Chat", "Manage Custom Bots", "User Profile", "Analytics"]
    selected_page = st.selectbox(
        "Select Page:",
        pages,
        index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0
    )
    
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()

def display_agent_selector():
    """Display agent selection interface"""
    st.markdown("""
    <div class="sidebar-section">
        <h3>🤖 Select Your AI Assistant</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Get all bots for current user
    all_bots = get_all_bots(st.session_state.user_id)
    
    # Group agents by category
    categories = {}
    for agent_name, agent_info in all_bots.items():
        category = agent_info.get('category', 'Other')
        if category not in categories:
            categories[category] = []
        categories[category].append(agent_name)
    
    # Category selector
    selected_category = st.selectbox(
        "Choose Category:",
        list(categories.keys()),
        index=0
    )
    
    # Agent selector within category
    agents_in_category = categories[selected_category]
    selected_agent = st.selectbox(
        "Choose Agent:",
        agents_in_category,
        index=0
    )
    
    # Update session state
    st.session_state.selected_agent = selected_agent
    
    # Display agent info
    agent_info = all_bots[selected_agent]
    card_class = "custom-bot-card" if agent_info.get('is_custom', False) else "agent-card"
    
    st.markdown(f"""
    <div class="{card_class}">
        <h4>{agent_info.get('emoji', '🤖')} {selected_agent}</h4>
        <p>{agent_info['description']}</p>
        <p><strong>Specialties:</strong> {', '.join(agent_info.get('specialties', []))}</p>
        {f"<p><strong>Custom Bot</strong> ✨</p>" if agent_info.get('is_custom', False) else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # Quick actions
    if agent_info.get('quick_actions'):
        st.markdown("**Quick Actions:**")
        for action in agent_info['quick_actions']:
            if st.button(action, key=f"action_{action}"):
                st.session_state.chat_input = f"Help me with: {action}"

# ======================================================
# 📄 ENHANCED PAGE FUNCTIONS
# ======================================================

def display_chat_page():
    """Display the main chat interface"""
    # Header with logo
    col1, col2 = st.columns([1, 4])
    with col1:
        display_logo()
    with col2:
        st.markdown("""
        <div class="main-header">
            <h1>AI Agent Toolkit - Chat</h1>
            <p>Your comprehensive suite of AI business assistants</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat history
    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation History")
        
        # Show recent messages with pagination
        user_prefs = load_user_preferences(st.session_state.user_id)
        history_limit = user_prefs.get('chat_history_limit', 10)
        
        for msg in st.session_state.chat_history[-history_limit:]:
            st.markdown(f"""
            <div class="user-message">
                <strong>You:</strong> {msg['message']}
                <div style="font-size: 0.8em; opacity: 0.7; margin-top: 5px;">
                    Agent: {msg['agent']} | {msg['timestamp']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="assistant-message">
                <strong>{msg['agent']}:</strong> {msg['response']}
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("### 💭 Ask Your AI Assistant")
    
    # Use session state for input if set by quick actions
    default_input = st.session_state.get('chat_input', '')
    if default_input:
        st.session_state.chat_input = ''  # Clear after use
    
    user_input = st.text_area(
        f"Message {st.session_state.selected_agent}:",
        value=default_input,
        height=100,
        placeholder=f"Ask {st.session_state.selected_agent} for business advice..."
    )
    
    if st.button("Send Message", type="primary"):
        if user_input.strip():
            with st.spinner(f"{st.session_state.selected_agent} is thinking..."):
                response = chat_with_agent(user_input, st.session_state.selected_agent, st.session_state.user_id)
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'message': user_input,
                    'response': response,
                    'agent': st.session_state.selected_agent,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                st.rerun()
        else:
            st.warning("Please enter a message")

def display_custom_bots_page():
    """Display the custom bots management page"""
    st.markdown("""
    <div class="main-header">
        <h1>🛠️ Manage Custom Bots</h1>
        <p>Create and manage your personalized AI assistants</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["Create New Bot", "My Custom Bots", "Bot Templates"])
    
    with tab1:
        st.subheader("✨ Create a New Custom Bot")
        
        with st.form("create_bot_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                bot_name = st.text_input("Bot Name*", placeholder="e.g., My Marketing Expert")
                bot_emoji = st.text_input("Emoji", value="🤖", max_chars=2)
                bot_category = st.text_input("Category", value="My Custom Bots")
                bot_temperature = st.slider("Creativity Level", 0.0, 1.0, 0.7, 0.1,
                                           help="Lower values = more focused, Higher values = more creative")
            
            with col2:
                bot_description = st.text_area("Description*", 
                                             placeholder="Describe what your bot specializes in...",
                                             height=100)
                specialties_input = st.text_input("Specialties (comma-separated)",
                                                placeholder="e.g., SEO, Content Marketing, Social Media")
                quick_actions_input = st.text_input("Quick Actions (comma-separated)",
                                                  placeholder="e.g., Create Campaign, Analyze Metrics")
            
            system_prompt = st.text_area("System Prompt*",
                                       placeholder="You are an expert in... Your role is to help users with...",
                                       height=150,
                                       help="This defines how your bot will behave and respond")
            
            create_submitted = st.form_submit_button("Create Custom Bot", type="primary")
            
            if create_submitted:
                if bot_name and bot_description and system_prompt:
                    # Process specialties and quick actions
                    specialties = [s.strip() for s in specialties_input.split(',') if s.strip()]
                    quick_actions = [a.strip() for a in quick_actions_input.split(',') if a.strip()]
                    
                    bot_data = {
                        'description': bot_description,
                        'emoji': bot_emoji,
                        'category': bot_category,
                        'temperature': bot_temperature,
                        'specialties': specialties,
                        'quick_actions': quick_actions,
                        'system_prompt': system_prompt
                    }
                    
                    if save_custom_bot(st.session_state.user_id, bot_name, bot_data):
                        st.success(f"✅ Custom bot '{bot_name}' created successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create custom bot. Please try again.")
                else:
                    st.error("Please fill in all required fields (marked with *)")
    
    with tab2:
        st.subheader("🤖 My Custom Bots")
        
        custom_bots = load_custom_bots(st.session_state.user_id)
        
        if not custom_bots:
            st.info("You haven't created any custom bots yet. Use the 'Create New Bot' tab to get started!")
        else:
            for bot_name, bot_data in custom_bots.items():
                with st.expander(f"{bot_data.get('emoji', '🤖')} {bot_name}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Description:** {bot_data['description']}")
                        st.write(f"**Category:** {bot_data.get('category', 'My Custom Bots')}")
                        st.write(f"**Specialties:** {', '.join(bot_data.get('specialties', []))}")
                        st.write(f"**Quick Actions:** {', '.join(bot_data.get('quick_actions', []))}")
                        st.write(f"**Temperature:** {bot_data.get('temperature', 0.7)}")
                        st.write(f"**Created:** {bot_data.get('created_at', 'Unknown')}")
                    
                    with col2:
                        if st.button(f"Delete", key=f"delete_{bot_name}", type="secondary"):
                            if delete_custom_bot(st.session_state.user_id, bot_name):
                                st.success(f"Deleted '{bot_name}'")
                                st.rerun()
                            else:
                                st.error("Failed to delete bot")
    
    with tab3:
        st.subheader("📋 Bot Templates")
        st.info("Coming soon! Pre-built bot templates for common use cases.")
        
        # Sample templates (could be expanded)
        templates = [
            {
                "name": "Personal Productivity Coach",
                "description": "Helps with time management, goal setting, and productivity optimization",
                "emoji": "⚡",
                "category": "Personal Development"
            },
            {
                "name": "Social Media Manager",
                "description": "Creates content strategies and manages social media campaigns",
                "emoji": "📱",
                "category": "Marketing"
            },
            {
                "name": "Code Review Assistant",
                "description": "Reviews code for best practices, bugs, and optimization opportunities",
                "emoji": "💻",
                "category": "Development"
            }
        ]
        
        for template in templates:
            st.markdown(f"""
            <div class="preference-card">
                <h4>{template['emoji']} {template['name']}</h4>
                <p>{template['description']}</p>
                <p><strong>Category:</strong> {template['category']}</p>
            </div>
            """, unsafe_allow_html=True)

def display_user_profile_page():
    """Display user profile and settings page"""
    st.markdown("""
    <div class="main-header">
        <h1>👤 User Profile</h1>
        <p>Manage your account settings and preferences</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Account Info", "Preferences", "Data Management"])
    
    with tab1:
        st.subheader("📋 Account Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Email:** {st.session_state.user_email}")
            st.info(f"**User ID:** {st.session_state.user_id}")
        
        with col2:
            total_custom_bots = len(load_custom_bots(st.session_state.user_id))
            total_messages = len(st.session_state.chat_history)
            st.metric("Custom Bots Created", total_custom_bots)
            st.metric("Messages Sent", total_messages)
    
    with tab2:
        st.subheader("⚙️ User Preferences")
        
        user_prefs = load_user_preferences(st.session_state.user_id)
        
        with st.form("preferences_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                default_model = st.selectbox(
                    "Default AI Model",
                    ["gpt-4", "gpt-3.5-turbo"],
                    index=0 if user_prefs.get('default_model', 'gpt-4') == 'gpt-4' else 1
                )
                
                default_temperature = st.slider(
                    "Default Creativity Level",
                    0.0, 1.0,
                    user_prefs.get('default_temperature', 0.7),
                    0.1
                )
            
            with col2:
                chat_history_limit = st.number_input(
                    "Chat History Display Limit",
                    min_value=5,
                    max_value=100,
                    value=user_prefs.get('chat_history_limit', 50)
                )
                
                auto_save_chats = st.checkbox(
                    "Auto-save Chat History",
                    value=user_prefs.get('auto_save_chats', True)
                )
            
            if st.form_submit_button("Save Preferences", type="primary"):
                new_prefs = {
                    'default_model': default_model,
                    'default_temperature': default_temperature,
                    'chat_history_limit': chat_history_limit,
                    'auto_save_chats': auto_save_chats,
                    'theme': user_prefs.get('theme', 'default')
                }
                
                if save_user_preferences(st.session_state.user_id, new_prefs):
                    st.success("Preferences saved successfully!")
                    st.rerun()
                else:
                    st.error("Failed to save preferences")
    
    with tab3:
        st.subheader("🗄️ Data Management")
        
        # Clear data options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat History", type="secondary"):
                st.session_state.chat_history = []
                # Also clear from persistent storage if available
                try:
                    enhanced_auth.clear_chat_history(st.session_state.user_id)
                except AttributeError:
                    pass
                st.success("Chat history cleared!")
                st.rerun()
        
        with col2:
            if st.button("⚠️ Delete All Custom Bots", type="secondary"):
                if st.session_state.user_id in st.session_state.get('custom_bots', {}):
                    st.session_state.custom_bots[st.session_state.user_id] = {}
                    st.success("All custom bots deleted!")
                    st.rerun()
        
        # Export data option
        st.subheader("📤 Export Data")
        if st.button("Export My Data", type="primary"):
            export_data = {
                'user_id': st.session_state.user_id,
                'custom_bots': load_custom_bots(st.session_state.user_id),
                'chat_history': st.session_state.chat_history,
                'preferences': load_user_preferences(st.session_state.user_id),
                'export_date': datetime.now().isoformat()
            }
            
            st.download_button(
                label="Download Data (JSON)",
                data=json.dumps(export_data, indent=2),
                file_name=f"ai_agent_toolkit_data_{st.session_state.user_id}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

def display_analytics_page():
    """Display analytics and insights page"""
    st.markdown("""
    <div class="main-header">
        <h1>📊 Analytics & Insights</h1>
        <p>Analyze your AI assistant usage and performance</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.chat_history:
        st.info("No chat data available yet. Start chatting with your AI assistants to see analytics!")
        return
    
    # Basic analytics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_messages = len(st.session_state.chat_history)
        st.metric("Total Messages", total_messages)
    
    with col2:
        unique_agents = len(set(msg['agent'] for msg in st.session_state.chat_history))
        st.metric("Agents Used", unique_agents)
    
    with col3:
        custom_bots_count = len(load_custom_bots(st.session_state.user_id))
        st.metric("Custom Bots", custom_bots_count)
    
    with col4:
        if st.session_state.chat_history:
            avg_msg_length = sum(len(msg['message']) for msg in st.session_state.chat_history) / len(st.session_state.chat_history)
            st.metric("Avg Message Length", f"{avg_msg_length:.0f} chars")
    
    # Agent usage chart
    st.subheader("🤖 Agent Usage Distribution")
    agent_usage = {}
    for msg in st.session_state.chat_history:
        agent = msg['agent']
        agent_usage[agent] = agent_usage.get(agent, 0) + 1
    
    if agent_usage:
        fig = px.pie(
            values=list(agent_usage.values()),
            names=list(agent_usage.keys()),
            title="Messages by Agent"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Activity over time
    st.subheader("📈 Activity Over Time")
    if len(st.session_state.chat_history) > 1:
        # Group messages by date
        daily_activity = {}
        for msg in st.session_state.chat_history:
            try:
                date = datetime.fromisoformat(msg['timestamp']).date()
                daily_activity[date] = daily_activity.get(date, 0) + 1
            except:
                # Handle different timestamp formats
                continue
        
        if daily_activity:
            dates = list(daily_activity.keys())
            counts = list(daily_activity.values())
            
            fig = px.line(
                x=dates,
                y=counts,
                title="Daily Message Count",
                labels={'x': 'Date', 'y': 'Messages'}
            )
            st.plotly_chart(fig, use_container_width=True)

def display_sidebar():
    """Display the sidebar with navigation and agent selection"""
    with st.sidebar:
        # User info
        st.markdown(f"""
        <div class="sidebar-section">
            <h3>👤 Welcome!</h3>
            <p>Email: {st.session_state.user_email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Page navigation
        display_page_navigation()
        
        # Agent selector (only show on chat page)
        if st.session_state.current_page == "Chat":
            display_agent_selector()
        
        # Quick stats
        st.markdown("""
        <div class="sidebar-section">
            <h3>📊 Quick Stats</h3>
        </div>
        """, unsafe_allow_html=True)
        
        total_messages = len(st.session_state.chat_history)
        st.metric("Total Messages", total_messages)
        
        total_custom_bots = len(load_custom_bots(st.session_state.user_id))
        st.metric("Custom Bots", total_custom_bots)
        
        if st.session_state.chat_history:
            agents_used = len(set(msg['agent'] for msg in st.session_state.chat_history))
            st.metric("Agents Consulted", agents_used)
        
        # Logout button
        if st.button("🚪 Logout"):
            result = enhanced_auth.sign_out()
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_id = None
            st.session_state.chat_history = []
            st.session_state.current_page = "Chat"
            if result['success']:
                st.success(result['message'])
            st.rerun()

# ======================================================
# 🚀 MAIN APPLICATION
# ======================================================

def main():
    """Main application function"""
    init_session_state()
    
    if not st.session_state.authenticated:
        login_form()
    else:
        display_sidebar()
        
        # Route to appropriate page
        if st.session_state.current_page == "Chat":
            display_chat_page()
        elif st.session_state.current_page == "Manage Custom Bots":
            display_custom_bots_page()
        elif st.session_state.current_page == "User Profile":
            display_user_profile_page()
        elif st.session_state.current_page == "Analytics":
            display_analytics_page()
        else:
            display_chat_page()  # Default fallback

if __name__ == "__main__":
    main()


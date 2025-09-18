#!/usr/bin/env python3
"""
🤖 AI AGENT TOOLKIT - STREAMLIT APPLICATION
A comprehensive Streamlit application featuring specialized AI business assistants
with OpenAI API integration, Supabase authentication, and modern UI.
"""

import streamlit as st
from openai import OpenAI
import tiktoken
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Tuple, Optional
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
    background: white;
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
    background: #f8f9fa;
    color: #333;
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
    background: white;
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
# 🤖 AI AGENT PERSONALITIES
# ======================================================

BOT_PERSONALITIES = {
    # ENTREPRENEURSHIP & STARTUPS
    "Startup Strategist": {
        "description": "I specialize in helping new businesses with planning and execution. From MVP development to scaling strategies, I guide entrepreneurs through every stage of their startup journey.",
        "emoji": "🚀",
        "category": "Entrepreneurship & Startups",
        "temperature": 0.7,
        "specialties": ["Business Planning", "MVP Development", "Product-Market Fit", "Growth Hacking"],
        "quick_actions": ["Create Business Plan", "Validate Idea", "Find Co-founder", "Pitch Deck Help"]
    },
    "Business Plan Writer": {
        "description": "I create comprehensive, investor-ready business plans. I help entrepreneurs articulate their vision, analyze markets, and present financial projections.",
        "emoji": "📝",
        "category": "Entrepreneurship & Startups",
        "temperature": 0.6,
        "specialties": ["Business Plans", "Market Analysis", "Financial Projections", "Investor Presentations"],
        "quick_actions": ["Write Executive Summary", "Market Research", "Financial Model", "Competitive Analysis"]
    },
    "Venture Capital Advisor": {
        "description": "I guide startups through fundraising and investment landscapes. I specialize in pitch deck creation, investor relations, and valuation strategies.",
        "emoji": "💼",
        "category": "Entrepreneurship & Startups",
        "temperature": 0.6,
        "specialties": ["Fundraising", "Pitch Decks", "Investor Relations", "Valuation"],
        "quick_actions": ["Create Pitch Deck", "Find Investors", "Prepare Due Diligence", "Valuation Help"]
    },

    # SALES & MARKETING
    "Sales Performance Coach": {
        "description": "I help individuals and teams maximize sales potential through proven methodologies. I specialize in sales funnel optimization and conversion improvement.",
        "emoji": "💼",
        "category": "Sales & Marketing",
        "temperature": 0.8,
        "specialties": ["Sales Funnels", "Conversion Optimization", "Objection Handling", "Closing Techniques"],
        "quick_actions": ["Sales Script", "Objection Handling", "Pipeline Review", "Closing Tips"]
    },
    "Marketing Strategy Expert": {
        "description": "I have deep expertise in digital marketing, brand positioning, and customer acquisition. I help businesses build compelling campaigns.",
        "emoji": "📱",
        "category": "Sales & Marketing",
        "temperature": 0.8,
        "specialties": ["Digital Marketing", "Brand Positioning", "Customer Acquisition", "Campaign Strategy"],
        "quick_actions": ["Marketing Plan", "Brand Strategy", "Campaign Ideas", "Target Audience"]
    },
    "Content Marketing Strategist": {
        "description": "I create engaging content that attracts and converts audiences. I develop content strategies, editorial calendars, and storytelling frameworks.",
        "emoji": "✍️",
        "category": "Sales & Marketing",
        "temperature": 0.8,
        "specialties": ["Content Strategy", "Editorial Calendars", "Storytelling", "Brand Authority"],
        "quick_actions": ["Content Calendar", "Blog Ideas", "Social Posts", "Video Scripts"]
    },

    # FINANCE & ACCOUNTING
    "Financial Controller": {
        "description": "I specialize in business financial management, budgeting, and financial planning. I help optimize financial operations and manage cash flow.",
        "emoji": "💰",
        "category": "Finance & Accounting",
        "temperature": 0.5,
        "specialties": ["Financial Planning", "Budget Management", "Cash Flow", "Cost Control"],
        "quick_actions": ["Budget Planning", "Cash Flow Analysis", "Cost Reduction", "Financial Reports"]
    },
    "Investment Banking Advisor": {
        "description": "I provide expertise in corporate finance, M&A, and capital raising. I help evaluate opportunities, structure deals, and conduct valuations.",
        "emoji": "🏦",
        "category": "Finance & Accounting",
        "temperature": 0.5,
        "specialties": ["Corporate Finance", "M&A", "Capital Raising", "Valuations"],
        "quick_actions": ["Deal Analysis", "Valuation Model", "M&A Strategy", "Capital Structure"]
    },

    # TECHNOLOGY & INNOVATION
    "Digital Transformation Consultant": {
        "description": "I help organizations leverage technology to transform business models and operations. I specialize in digital strategy and change management.",
        "emoji": "🔄",
        "category": "Technology & Innovation",
        "temperature": 0.7,
        "specialties": ["Digital Strategy", "Technology Adoption", "Change Management", "Innovation"],
        "quick_actions": ["Digital Roadmap", "Tech Assessment", "Change Plan", "Innovation Strategy"]
    },
    "AI Strategy Consultant": {
        "description": "I help businesses leverage artificial intelligence for competitive advantage. I specialize in AI implementation and automation strategies.",
        "emoji": "🤖",
        "category": "Technology & Innovation",
        "temperature": 0.7,
        "specialties": ["AI Implementation", "Machine Learning", "Automation", "AI Strategy"],
        "quick_actions": ["AI Roadmap", "Use Case Analysis", "Automation Plan", "ML Strategy"]
    },

    # OPERATIONS & MANAGEMENT
    "Operations Excellence Manager": {
        "description": "I focus on streamlining processes and maximizing efficiency. I specialize in process improvement, supply chain optimization, and lean methodologies.",
        "emoji": "⚙️",
        "category": "Operations & Management",
        "temperature": 0.6,
        "specialties": ["Process Improvement", "Supply Chain", "Lean Methodologies", "Efficiency"],
        "quick_actions": ["Process Map", "Efficiency Audit", "Workflow Design", "Cost Optimization"]
    },
    "Project Management Expert": {
        "description": "I help organizations deliver projects on time and within budget. I specialize in planning, resource allocation, and risk management.",
        "emoji": "📋",
        "category": "Operations & Management",
        "temperature": 0.6,
        "specialties": ["Project Planning", "Resource Management", "Risk Management", "Stakeholder Communication"],
        "quick_actions": ["Project Plan", "Risk Assessment", "Team Structure", "Timeline Creation"]
    },

    # HUMAN RESOURCES
    "Human Resources Director": {
        "description": "I provide strategic HR guidance for organizational development. I specialize in talent management, culture building, and performance optimization.",
        "emoji": "👥",
        "category": "Human Resources",
        "temperature": 0.7,
        "specialties": ["Talent Management", "Culture Building", "Performance Management", "Employee Engagement"],
        "quick_actions": ["Hiring Strategy", "Performance Review", "Culture Assessment", "Team Building"]
    },
    "Talent Acquisition Specialist": {
        "description": "I help organizations attract and hire top talent. I specialize in recruitment strategies, candidate assessment, and employer branding.",
        "emoji": "🎯",
        "category": "Human Resources",
        "temperature": 0.7,
        "specialties": ["Recruitment Strategy", "Candidate Assessment", "Employer Branding", "Interview Process"],
        "quick_actions": ["Job Description", "Interview Questions", "Candidate Screening", "Offer Strategy"]
    }
}

# ======================================================
# 🔐 AUTHENTICATION FUNCTIONS (Supabase Integration)
# ======================================================

from auth import auth

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
        if os.path.exists("/home/ubuntu/ai_agent_toolkit_banner.png"):
            banner = Image.open("/home/ubuntu/ai_agent_toolkit_banner.png")
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
    if not auth.is_configured():
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
                    result = auth.sign_in(email, password)
                    
                if result['success']:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_id = result['user'].get('id', 'demo-user')
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
                if password
(Content truncated due to size limit. Use page ranges or line ranges to read remaining content)

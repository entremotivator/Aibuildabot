#!/usr/bin/env python3
"""
🤖 AI AGENT TOOLKIT - ENHANCED STREAMLIT APPLICATION
A comprehensive Streamlit application featuring specialized AI business assistants
with OpenAI API integration, user authentication, custom bot creation, and modern UI.
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

.custom-bot-card {
    background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
    color: #2d3436;
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

/* Page navigation styling */
.page-nav {
    background: rgba(102, 126, 234, 0.1);
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 20px;
}

/* Auth form styling */
.auth-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 20px;
    background: white;
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

/* Responsive design */
@media (max-width: 768px) {
    .user-message, .assistant-message {
        margin-left: 10px;
        margin-right: 10px;
    }
    
    .main-header {
        padding: 15px;
    }
    
    .sidebar-section {
        padding: 10px;
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
        "emoji": "📈",
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
# 🗄️ CUSTOM BOT DATA MANAGEMENT
# ======================================================

def load_custom_bots(user_id: str) -> Dict[str, Dict]:
    """Load custom bots for a specific user"""
    if 'custom_bots' not in st.session_state:
        st.session_state.custom_bots = {}
    
    return st.session_state.custom_bots.get(user_id, {})

def save_custom_bot(user_id: str, bot_name: str, bot_data: Dict) -> bool:
    """Save a custom bot for a specific user"""
    try:
        if 'custom_bots' not in st.session_state:
            st.session_state.custom_bots = {}
        
        if user_id not in st.session_state.custom_bots:
            st.session_state.custom_bots[user_id] = {}
        
        # Add metadata
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

# ======================================================
# 🧠 AGENT PROMPT GENERATION
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
Be specific, practical, and focus on delivering value to business users.
"""
    return prompt

# ======================================================
# 💬 CHAT FUNCTIONALITY
# ======================================================

def chat_with_agent(user_message: str, agent_name: str, user_id: str = None) -> str:
    """Chat with an AI agent using OpenAI API"""
    client, api_key = initialize_openai()
    
    if not client:
        return "⚠️ OpenAI API key not configured. Please add your API key to Streamlit secrets or environment variables to continue."
    
    try:
        all_bots = get_all_bots(user_id) if user_id else BOT_PERSONALITIES
        agent = all_bots.get(agent_name, all_bots.get("Startup Strategist"))
        
        messages = [
            {"role": "system", "content": get_agent_prompt(agent_name, user_id)},
        ]
        
        # Add recent chat history for context (only for same agent)
        if st.session_state.chat_history:
            recent_history = [msg for msg in st.session_state.chat_history[-6:] if msg['agent'] == agent_name]
            for msg in recent_history:
                messages.append({"role": "user", "content": msg['message']})
                messages.append({"role": "assistant", "content": msg['response']})
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=agent.get('temperature', 0.7),
            max_tokens=1500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return f"❌ Error: {str(e)}"

# ======================================================
# 🔐 SIMPLE AUTHENTICATION SYSTEM
# ======================================================

def simple_auth():
    """Simple authentication system for demo purposes"""
    return {
        'sign_in': lambda email, password: {'success': True, 'message': 'Signed in successfully!', 'user': {'id': f"user_{hash(email)}", 'email': email}},
        'sign_up': lambda email, password: {'success': True, 'message': 'Account created successfully! You can now sign in.'},
        'sign_out': lambda: {'success': True, 'message': 'Signed out successfully!'},
        'reset_password': lambda email: {'success': True, 'message': 'Password reset link sent to your email!'},
        'is_configured': lambda: True
    }

auth = simple_auth()

# ======================================================
# 📱 SESSION STATE MANAGEMENT
# ======================================================

def init_session_state():
    """Initialize session state variables"""
    defaults = {
        'authenticated': False,
        'user_email': None,
        'user_id': None,
        'chat_history': [],
        'selected_agent': "Startup Strategist",
        'auth_mode': "login",
        'current_page': "Chat",
        'custom_bots': {},
        'chat_input': ''
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# ======================================================
# 🎨 UI COMPONENTS
# ======================================================

def display_logo():
    """Display the AI Agent Toolkit logo"""
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <div style="font-size: 2.5em;">🤖</div>
        <div style="font-size: 0.9em; color: #667eea; font-weight: bold;">AI Agent Toolkit</div>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display the sidebar with navigation and agent selection"""
    with st.sidebar:
        # Logo at top of sidebar
        display_logo()
        
        # User info section
        st.markdown(f"""
        <div class="sidebar-section">
            <h3 style="margin: 0; color: #667eea;">👤 Welcome!</h3>
            <p style="margin: 5px 0;"><strong>Email:</strong> {st.session_state.user_email}</p>
            <p style="margin: 5px 0; color: #28a745;"><strong>Status:</strong> ✅ Online</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Page navigation
        display_page_navigation()
        
        st.divider()
        
        # Agent selector (only show on chat page)
        if st.session_state.current_page == "Chat":
            display_agent_selector()
            st.divider()
        
        # Session statistics
        st.markdown("""
        <div class="sidebar-section">
            <h3 style="margin: 0; color: #667eea;">📊 Session Stats</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Create metrics in columns for better layout
        col1, col2 = st.columns(2)
        with col1:
            total_messages = len(st.session_state.chat_history)
            st.metric("Messages", total_messages)
        
        with col2:
            total_custom_bots = len(load_custom_bots(st.session_state.user_id))
            st.metric("Custom Bots", total_custom_bots)
        
        if st.session_state.chat_history:
            agents_used = len(set(msg['agent'] for msg in st.session_state.chat_history))
            st.metric("Agents Used", agents_used)
        
        st.divider()
        
        # Logout button at bottom
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            # Clear authentication state
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_id = None
            st.session_state.chat_history = []
            st.session_state.current_page = "Chat"
            st.session_state.selected_agent = "Startup Strategist"
            
            st.success("Logged out successfully!")
            time.sleep(1)
            st.rerun()

def display_page_navigation():
    """Display page navigation in sidebar"""
    st.markdown("**📄 Navigation**")
    
    pages = ["Chat", "Manage Custom Bots", "User Profile"]
    
    # Use radio buttons for better UX
    selected_page = st.radio(
        "Select Page:",
        pages,
        index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0,
        label_visibility="collapsed"
    )
    
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()

def display_agent_selector():
    """Display agent selection interface"""
    st.markdown("**🤖 AI Assistant**")
    
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
        "Category:",
        list(categories.keys()),
        index=0 if categories else None
    )
    
    if selected_category:
        # Agent selector within category
        agents_in_category = categories[selected_category]
        
        # Find current agent's index
        current_index = 0
        if st.session_state.selected_agent in agents_in_category:
            current_index = agents_in_category.index(st.session_state.selected_agent)
        
        selected_agent = st.selectbox(
            "Agent:",
            agents_in_category,
            index=current_index
        )
        
        # Update session state if changed
        if selected_agent != st.session_state.selected_agent:
            st.session_state.selected_agent = selected_agent
            st.rerun()
        
        # Display compact agent info
        if selected_agent in all_bots:
            agent_info = all_bots[selected_agent]
            
            # Compact agent info card
            is_custom = agent_info.get('is_custom', False)
            emoji = agent_info.get('emoji', '🤖')
            
            st.markdown(f"""
            <div style="background: {'linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%)' if is_custom else 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}; 
                        color: {'#2d3436' if is_custom else 'white'}; 
                        padding: 15px; 
                        border-radius: 10px; 
                        margin: 10px 0; 
                        font-size: 0.9em;
                        text-align: center;">
                <div style="font-size: 1.8em; margin-bottom: 8px;">{emoji}</div>
                <div style="font-weight: bold; margin-bottom: 5px;">{selected_agent}</div>
                {f'<div style="font-size: 0.8em; opacity: 0.9;">✨ Custom Bot</div>' if is_custom else ''}
                <div style="font-size: 0.8em; margin-top: 8px; opacity: 0.9;">
                    {', '.join(agent_info.get('specialties', [])[:2])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Quick actions as small buttons
            if agent_info.get('quick_actions'):
                st.markdown("**⚡ Quick Actions:**")
                for i, action in enumerate(agent_info['quick_actions'][:3]):  # Limit to 3 for space
                    if st.button(action, key=f"sidebar_action_{action}_{i}", use_container_width=True):
                        st.session_state.chat_input = f"Help me with: {action}"
                        if st.session_state.current_page != "Chat":
                            st.session_state.current_page = "Chat"
                        st.rerun()

# ======================================================
# 🔐 AUTHENTICATION UI
# ======================================================

def login_form():
    """Display login/signup form"""
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Display logo and banner
        display_logo()
        
        st.markdown("""
        <div class="main-header">
            <h1>🤖 AI Agent Toolkit</h1>
            <p>Your comprehensive suite of AI business assistants</p>
            <p style="font-size: 0.9em; margin-top: 15px;">
                Transform your business with specialized AI agents for every department
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Authentication mode selector
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
        st.info("🔧 **Demo Mode**: Use any email/password combination to login and explore the AI Agent Toolkit!")

def login_section():
    """Login form section"""
    with st.form("login_form"):
        st.subheader("🔑 Login to Your Account")
        email = st.text_input("Email Address", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Your password")
        
        login_submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
        
        if login_submitted:
            if email and password:
                with st.spinner("Signing in..."):
                    result = auth['sign_in'](email, password)
                    
                if result['success']:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_id = result['user'].get('id', f"user_{hash(email)}")
                    st.success(result['message'])
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(result['error'])
            else:
                st.error("Please enter both email and password")

def signup_section():
    """Signup form section"""
    with st.form("signup_form"):
        st.subheader("📝 Create New Account")
        email = st.text_input("Email Address", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Choose a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        signup_submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        
        if signup_submitted:
            if email and password and confirm_password:
                if password == confirm_password:
                    with st.spinner("Creating account..."):
                        result = auth['sign_up'](email, password)
                        
                    if result['success']:
                        st.success(result['message'])
                        st.info("Please switch to Login tab to sign in.")
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
        email = st.text_input("Email Address", placeholder="your@email.com")
        
        reset_submitted = st.form_submit_button("Send Reset Link", type="primary", use_container_width=True)
        
        if reset_submitted:
            if email:
                with st.spinner("Sending reset link..."):
                    result = auth['reset_password'](email)
                    
                if result['success']:
                    st.success(result['message'])
                else:
                    st.error(result['error'])
            else:
                st.error("Please enter your email address")

# ======================================================
# 📄 PAGE FUNCTIONS
# ======================================================

def display_chat_page():
    """Display the main chat interface"""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💬 Chat with AI Agents</h1>
        <p>Get expert business advice from specialized AI assistants</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Current agent info
    all_bots = get_all_bots(st.session_state.user_id)
    current_agent = all_bots.get(st.session_state.selected_agent)
    
    if current_agent:
        is_custom = current_agent.get('is_custom', False)
        card_class = "custom-bot-card" if is_custom else "agent-card"
        
        st.markdown(f"""
        <div class="{card_class}">
            <h3>{current_agent.get('emoji', '🤖')} Currently chatting with: {st.session_state.selected_agent}</h3>
            <p>{current_agent['description']}</p>
            <p><strong>Specialties:</strong> {', '.join(current_agent.get('specialties', []))}</p>
            {f"<p><strong>✨ This is a custom bot you created</strong></p>" if is_custom else ""}
        </div>
        """, unsafe_allow_html=True)
    
    # Chat history display
    if st.session_state.chat_history:
        st.markdown("### 📜 Conversation History")
        
        # Show recent messages (last 10)
        recent_messages = st.session_state.chat_history[-10:]
        
        for i, msg in enumerate(recent_messages):
            # User message
            st.markdown(f"""
            <div class="user-message">
                <strong>You:</strong> {msg['message']}
                <div style="font-size: 0.8em; opacity: 0.7; margin-top: 8px;">
                    💬 To: {msg['agent']} | 🕐 {msg['timestamp']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Agent response
            st.markdown(f"""
            <div class="assistant-message">
                <strong>{msg['agent']} {all_bots.get(msg['agent'], {}).get('emoji', '🤖')}:</strong><br/>
                {msg['response']}
            </div>
            """, unsafe_allow_html=True)
        
        # Clear history button
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("🗑️ Clear History", type="secondary"):
                st.session_state.chat_history = []
                st.success("Chat history cleared!")
                st.rerun()
    
    # Chat input section
    st.markdown("### 💭 Send a Message")
    
    # Use session state for input if set by quick actions
    default_input = st.session_state.get('chat_input', '')
    if default_input:
        st.session_state.chat_input = ''  # Clear after use
    
    # Create columns for input and send button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_area(
            f"Message {st.session_state.selected_agent}:",
            value=default_input,
            height=120,
            placeholder=f"Ask {st.session_state.selected_agent} for business advice, strategy, or specific help...",
            key="chat_text_input"
        )
    
    with col2:
        st.markdown("<br/>", unsafe_allow_html=True)  # Add some spacing
        send_button = st.button("📤 Send", type="primary", use_container_width=True)
    
    # Handle message sending
    if send_button or (user_input and st.session_state.get('send_message', False)):
        if user_input.strip():
            with st.spinner(f"🤔 {st.session_state.selected_agent} is thinking..."):
                # Add a small delay for better UX
                time.sleep(0.5)
                response = chat_with_agent(user_input, st.session_state.selected_agent, st.session_state.user_id)
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'message': user_input,
                    'response': response,
                    'agent': st.session_state.selected_agent,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Clear the input and rerun
                st.session_state.send_message = False
                st.rerun()
        else:
            st.warning("⚠️ Please enter a message before sending")

def display_custom_bots_page():
    """Display the custom bots management page"""
    st.markdown("""
    <div class="main-header">
        <h1>🛠️ Manage Custom Bots</h1>
        <p>Create and manage your personalized AI assistants</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different actions
    tab1, tab2 = st.tabs(["✨ Create New Bot", "🤖 My Custom Bots"])
    
    with tab1:
        create_custom_bot_form()
    
    with tab2:
        display_existing_custom_bots()

def create_custom_bot_form():
    """Display form to create a new custom bot"""
    st.subheader("✨ Create a New Custom AI Assistant")
    st.markdown("Design your own specialized AI agent tailored to your specific business needs.")
    
    with st.form("create_bot_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            bot_name = st.text_input(
                "Bot Name*", 
                placeholder="e.g., My E-commerce Expert",
                help="Choose a descriptive name for your AI assistant"
            )
            bot_emoji = st.text_input(
                "Emoji", 
                value="🤖", 
                max_chars=2,
                help="Choose an emoji to represent your bot"
            )
            bot_category = st.text_input(
                "Category", 
                value="My Custom Bots",
                placeholder="e.g., Marketing, Sales, Operations",
                help="Categorize your bot for easy organization"
            )
            bot_temperature = st.slider(
                "Creativity Level", 
                0.0, 1.0, 0.7, 0.1,
                help="Lower = more focused responses, Higher = more creative responses"
            )
        
        with col2:
            bot_description = st.text_area(
                "Description*", 
                placeholder="Describe what your bot specializes in and how it helps users...",
                height=100,
                help="This description will be shown when users select your bot"
            )
            specialties_input = st.text_input(
                "Specialties (comma-separated)",
                placeholder="e.g., SEO, Content Marketing, Social Media Analytics",
                help="List the key areas your bot specializes in"
            )
            quick_actions_input = st.text_input(
                "Quick Actions (comma-separated)",
                placeholder="e.g., Create Campaign Plan, Analyze Performance, Generate Content Ideas",
                help="Quick action buttons users can click for common tasks"
            )
        
        system_prompt = st.text_area(
            "System Prompt*",
            placeholder="You are an expert in e-commerce and digital marketing. Your role is to help users optimize their online stores, improve conversion rates, and develop effective marketing strategies. Always provide specific, actionable advice based on current best practices...",
            height=150,
            help="This defines your bot's personality, expertise, and how it responds to users"
        )
        
        st.markdown("---")
        create_submitted = st.form_submit_button("🚀 Create Custom Bot", type="primary", use_container_width=True)
        
        if create_submitted:
            if bot_name and bot_description and system_prompt:
                # Check if bot name already exists
                existing_bots = get_all_bots(st.session_state.user_id)
                if bot_name in existing_bots:
                    st.error("❌ A bot with this name already exists. Please choose a different name.")
                    return
                
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
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Failed to create custom bot. Please try again.")
            else:
                st.error("⚠️ Please fill in all required fields (marked with *)")

def display_existing_custom_bots():
    """Display existing custom bots"""
    st.subheader("🤖 Your Custom AI Assistants")
    
    custom_bots = load_custom_bots(st.session_state.user_id)
    
    if not custom_bots:
        st.info("🎯 You haven't created any custom bots yet. Use the 'Create New Bot' tab to build your first AI assistant!")
        
        # Show some inspiration
        st.markdown("### 💡 Custom Bot Ideas")
        ideas = [
            "**E-commerce Specialist** - Help with online store optimization, product descriptions, and conversion strategies",
            "**Social Media Manager** - Create content calendars, write posts, and analyze engagement metrics",
            "**Customer Service Expert** - Handle customer inquiries, write responses, and improve satisfaction",
            "**Industry Expert** - Specialize in your specific industry (healthcare, finance, manufacturing, etc.)",
            "**Personal Business Coach** - Tailored to your specific business goals and challenges"
        ]
        
        for idea in ideas:
            st.markdown(f"• {idea}")
        
    else:
        st.success(f"🎉 You have {len(custom_bots)} custom bot(s) created!")
        
        for bot_name, bot_data in custom_bots.items():
            with st.expander(f"{bot_data.get('emoji', '🤖')} {bot_name}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**📝 Description:** {bot_data['description']}")
                    st.markdown(f"**📂 Category:** {bot_data.get('category', 'My Custom Bots')}")
                    if bot_data.get('specialties'):
                        st.markdown(f"**🎯 Specialties:** {', '.join(bot_data.get('specialties', []))}")
                    if bot_data.get('quick_actions'):
                        st.markdown(f"**⚡ Quick Actions:** {', '.join(bot_data.get('quick_actions', []))}")
                    st.markdown(f"**🌡️ Creativity Level:** {bot_data.get('temperature', 0.7)}")
                    st.markdown(f"**📅 Created:** {bot_data.get('created_at', 'Unknown')[:19]}")
                
                with col2:
                    st.markdown("**Actions:**")
                    
                    # Test bot button
                    if st.button(f"💬 Chat", key=f"test_{bot_name}", use_container_width=True):
                        st.session_state.selected_agent = bot_name
                        st.session_state.current_page = "Chat"
                        st.success(f"Switched to {bot_name}!")
                        time.sleep(1)
                        st.rerun()
                    
                    # Delete bot button
                    if st.button(f"🗑️ Delete", key=f"delete_{bot_name}", type="secondary", use_container_width=True):
                        if delete_custom_bot(st.session_state.user_id, bot_name):
                            st.success(f"✅ Deleted '{bot_name}'")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete bot")
                
                # Show system prompt in expandable section
                with st.expander("🧠 View System Prompt"):
                    st.code(bot_data.get('system_prompt', 'No system prompt defined'), language='text')

def display_user_profile_page():
    """Display user profile and settings page"""
    st.markdown("""
    <div class="main-header">
        <h1>👤 User Profile & Settings</h1>
        <p>Manage your account and preferences</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Account information section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Account Information")
        
        st.markdown(f"""
        <div class="agent-card">
            <h4>👤 User Details</h4>
            <p><strong>Email:</strong> {st.session_state.user_email}</p>
            <p><strong>User ID:</strong> {st.session_state.user_id}</p>
            <p><strong>Account Type:</strong> Demo User</p>
            <p><strong>Joined:</strong> {datetime.now().strftime("%Y-%m-%d")}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("📊 Usage Statistics")
        
        total_custom_bots = len(load_custom_bots(st.session_state.user_id))
        total_messages = len(st.session_state.chat_history)
        agents_used = len(set(msg['agent'] for msg in st.session_state.chat_history)) if st.session_state.chat_history else 0
        
        # Display metrics in a nice card
        st.markdown(f"""
        <div class="agent-card">
            <h4>📈 Your Activity</h4>
            <div style="display: flex; justify-content: space-between; margin: 15px 0;">
                <div style="text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #667eea;">{total_messages}</div>
                    <div style="font-size: 0.9em;">Messages Sent</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #667eea;">{total_custom_bots}</div>
                    <div style="font-size: 0.9em;">Custom Bots</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #667eea;">{agents_used}</div>
                    <div style="font-size: 0.9em;">Agents Used</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Settings and actions
    st.subheader("⚙️ Account Settings & Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**💬 Chat Management**")
        if st.button("🗑️ Clear Chat History", type="secondary", use_container_width=True):
            st.session_state.chat_history = []
            st.success("✅ Chat history cleared!")
            st.rerun()
    
    with col2:
        st.markdown("**🤖 Bot Management**")
        if st.button("⚠️ Delete All Custom Bots", type="secondary", use_container_width=True):
            if st.session_state.user_id in st.session_state.get('custom_bots', {}):
                st.session_state.custom_bots[st.session_state.user_id] = {}
                st.success("✅ All custom bots deleted!")
                st.rerun()
            else:
                st.info("No custom bots to delete.")
    
    with col3:
        st.markdown("**📊 Export Data**")
        if st.button("💾 Export Chat History", type="secondary", use_container_width=True):
            if st.session_state.chat_history:
                # Convert chat history to DataFrame
                df = pd.DataFrame(st.session_state.chat_history)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No chat history to export.")
    
    # Quick stats visualization
    if st.session_state.chat_history:
        st.markdown("---")
        st.subheader("📈 Activity Overview")
        
        # Agent usage chart
        agent_counts = {}
        for msg in st.session_state.chat_history:
            agent = msg['agent']
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        if agent_counts:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    values=list(agent_counts.values()), 
                    names=list(agent_counts.keys()),
                    title="Messages by Agent"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Messages over time (by day)
                df_history = pd.DataFrame(st.session_state.chat_history)
                df_history['date'] = pd.to_datetime(df_history['timestamp']).dt.date
                daily_counts = df_history.groupby('date').size().reset_index(name='messages')
                
                fig = px.bar(daily_counts, x='date', y='messages', title="Messages per Day")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

# ======================================================
# 🚀 MAIN APPLICATION
# ======================================================

def main():
    """Main application function"""
    init_session_state()
    
    if not st.session_state.authenticated:
        login_form()
    else:
        # Display sidebar
        display_sidebar()
        
        # Route to appropriate page based on current_page state
        if st.session_state.current_page == "Chat":
            display_chat_page()
        elif st.session_state.current_page == "Manage Custom Bots":
            display_custom_bots_page()
        elif st.session_state.current_page == "User Profile":
            display_user_profile_page()
        else:
            # Default fallback to chat
            st.session_state.current_page = "Chat"
            display_chat_page()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
🤖 AI AGENT TOOLKIT - SIMPLIFIED WORKING VERSION
A comprehensive Streamlit application featuring specialized AI business assistants
with OpenAI API integration, custom bot creation, and personalization features.
"""

import streamlit as st
from openai import OpenAI
from datetime import datetime
import json
import os
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================================================
# 🎨 STREAMLIT CONFIGURATION & STYLING
# ======================================================

st.set_page_config(
    page_title="🤖 AI Agent Toolkit",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced styling
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}

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

.custom-bot-card {
    background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
    color: black;
    padding: 20px;
    border-radius: 15px;
    margin: 10px 0;
    border-left: 4px solid #e17055;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
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

.sidebar-section {
    background: rgba(102, 126, 234, 0.05);
    padding: 15px;
    border-radius: 15px;
    margin: 15px 0;
    border-left: 4px solid #667eea;
}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ======================================================
# 🔑 API CONFIGURATION
# ======================================================

def initialize_openai():
    """Initialize OpenAI client with API key from environment"""
    try:
        if 'OPENAI_API_KEY' in os.environ:
            api_key = os.environ['OPENAI_API_KEY']
            return OpenAI(api_key=api_key), api_key
        return None, None
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI: {str(e)}")
        return None, None

# ======================================================
# 🤖 AI AGENT PERSONALITIES
# ======================================================

BOT_PERSONALITIES = {
    "Startup Strategist": {
        "description": "I specialize in helping new businesses with planning and execution. From MVP development to scaling strategies, I guide entrepreneurs through every stage of their startup journey.",
        "emoji": "🚀",
        "category": "Entrepreneurship & Startups",
        "temperature": 0.7,
        "specialties": ["Business Planning", "MVP Development", "Product-Market Fit", "Growth Hacking"],
        "quick_actions": ["Create Business Plan", "Validate Idea", "Find Co-founder", "Pitch Deck Help"],
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
    "AI Strategy Consultant": {
        "description": "I help businesses leverage artificial intelligence for competitive advantage. I specialize in AI implementation and automation strategies.",
        "emoji": "🤖",
        "category": "Technology & Innovation",
        "temperature": 0.7,
        "specialties": ["AI Implementation", "Machine Learning", "Automation", "AI Strategy"],
        "quick_actions": ["AI Roadmap", "Use Case Analysis", "Automation Plan", "ML Strategy"],
        "is_custom": False
    }
}

# ======================================================
# 🗄️ DATA MANAGEMENT
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
        
        bot_data['is_custom'] = True
        bot_data['created_at'] = datetime.now().isoformat()
        
        st.session_state.custom_bots[user_id][bot_name] = bot_data
        return True
    except Exception as e:
        logger.error(f"Error saving custom bot: {str(e)}")
        return False

def get_all_bots(user_id: str) -> Dict[str, Dict]:
    """Get all bots (predefined + custom) for a user"""
    all_bots = BOT_PERSONALITIES.copy()
    custom_bots = load_custom_bots(user_id)
    all_bots.update(custom_bots)
    return all_bots

# ======================================================
# 💬 CHAT FUNCTIONALITY
# ======================================================

def get_agent_prompt(agent_name: str, user_id: str = None) -> str:
    """Generate system prompt for an agent"""
    all_bots = get_all_bots(user_id) if user_id else BOT_PERSONALITIES
    agent = all_bots.get(agent_name)
    
    if not agent:
        return "You are a helpful AI assistant."
    
    if agent.get('is_custom', False) and 'system_prompt' in agent:
        return agent['system_prompt']
    
    prompt = f"""You are {agent_name}, {agent['description']}

Your specialties include: {', '.join(agent.get('specialties', []))}

You should respond in a professional, helpful manner while staying true to your role and expertise. 
Provide actionable advice and insights based on your specialization.
"""
    return prompt

def chat_with_agent(user_message: str, agent_name: str, user_id: str = None) -> str:
    """Chat with an AI agent using OpenAI API"""
    client, api_key = initialize_openai()
    
    if not client:
        return "⚠️ OpenAI API key not configured. Please add your API key to continue."
    
    try:
        all_bots = get_all_bots(user_id) if user_id else BOT_PERSONALITIES
        agent = all_bots.get(agent_name, all_bots.get("Startup Strategist"))
        
        messages = [
            {"role": "system", "content": get_agent_prompt(agent_name, user_id)},
            {"role": "user", "content": user_message}
        ]
        
        # Add recent chat history for context
        if st.session_state.chat_history:
            recent_history = st.session_state.chat_history[-4:]  # Last 2 exchanges
            for msg in recent_history:
                if msg['agent'] == agent_name:
                    messages.insert(-1, {"role": "assistant", "content": msg['response']})
                    messages.insert(-1, {"role": "user", "content": msg['message']})
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=agent.get('temperature', 0.7),
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return f"❌ Error: {str(e)}"

# ======================================================
# 🔐 SESSION STATE INITIALIZATION
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
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Chat"
    if 'custom_bots' not in st.session_state:
        st.session_state.custom_bots = {}

# ======================================================
# 🎨 UI COMPONENTS
# ======================================================

def login_form():
    """Display simple login form"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Agent Toolkit</h1>
        <p>Your comprehensive suite of AI business assistants</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.subheader("🔑 Demo Login")
        email = st.text_input("Email Address", value="demo@example.com")
        password = st.text_input("Password", type="password", value="demo123")
        
        login_submitted = st.form_submit_button("Login", type="primary")
        
        if login_submitted:
            if email and password:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.session_state.user_id = "demo-user"
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Please enter both email and password")

def display_page_navigation():
    """Display page navigation in sidebar"""
    st.markdown("""
    <div class="sidebar-section">
        <h3>📄 Navigation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    pages = ["Chat", "Manage Custom Bots", "User Profile"]
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
# 📄 PAGE FUNCTIONS
# ======================================================

def display_chat_page():
    """Display the main chat interface"""
    st.markdown("""
    <div class="main-header">
        <h1>AI Agent Toolkit - Chat</h1>
        <p>Your comprehensive suite of AI business assistants</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat history
    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation History")
        for msg in st.session_state.chat_history[-10:]:
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
    
    default_input = st.session_state.get('chat_input', '')
    if default_input:
        st.session_state.chat_input = ''
    
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
    
    tab1, tab2 = st.tabs(["Create New Bot", "My Custom Bots"])
    
    with tab1:
        st.subheader("✨ Create a New Custom Bot")
        
        with st.form("create_bot_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                bot_name = st.text_input("Bot Name*", placeholder="e.g., My Marketing Expert")
                bot_emoji = st.text_input("Emoji", value="🤖", max_chars=2)
                bot_category = st.text_input("Category", value="My Custom Bots")
                bot_temperature = st.slider("Creativity Level", 0.0, 1.0, 0.7, 0.1)
            
            with col2:
                bot_description = st.text_area("Description*", 
                                             placeholder="Describe what your bot specializes in...",
                                             height=100)
                specialties_input = st.text_input("Specialties (comma-separated)",
                                                placeholder="e.g., SEO, Content Marketing")
                quick_actions_input = st.text_input("Quick Actions (comma-separated)",
                                                  placeholder="e.g., Create Campaign, Analyze Metrics")
            
            system_prompt = st.text_area("System Prompt*",
                                       placeholder="You are an expert in... Your role is to help users with...",
                                       height=150)
            
            create_submitted = st.form_submit_button("Create Custom Bot", type="primary")
            
            if create_submitted:
                if bot_name and bot_description and system_prompt:
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
                    st.write(f"**Description:** {bot_data['description']}")
                    st.write(f"**Category:** {bot_data.get('category', 'My Custom Bots')}")
                    st.write(f"**Specialties:** {', '.join(bot_data.get('specialties', []))}")
                    st.write(f"**Created:** {bot_data.get('created_at', 'Unknown')}")

def display_user_profile_page():
    """Display user profile page"""
    st.markdown("""
    <div class="main-header">
        <h1>👤 User Profile</h1>
        <p>Manage your account and view statistics</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**Email:** {st.session_state.user_email}")
        st.info(f"**User ID:** {st.session_state.user_id}")
    
    with col2:
        total_custom_bots = len(load_custom_bots(st.session_state.user_id))
        total_messages = len(st.session_state.chat_history)
        st.metric("Custom Bots Created", total_custom_bots)
        st.metric("Messages Sent", total_messages)
    
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")
        st.rerun()

def display_sidebar():
    """Display the sidebar"""
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-section">
            <h3>👤 Welcome!</h3>
            <p>Email: {st.session_state.user_email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        display_page_navigation()
        
        if st.session_state.current_page == "Chat":
            display_agent_selector()
        
        st.markdown("""
        <div class="sidebar-section">
            <h3>📊 Quick Stats</h3>
        </div>
        """, unsafe_allow_html=True)
        
        total_messages = len(st.session_state.chat_history)
        st.metric("Total Messages", total_messages)
        
        total_custom_bots = len(load_custom_bots(st.session_state.user_id))
        st.metric("Custom Bots", total_custom_bots)
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_id = None
            st.session_state.chat_history = []
            st.session_state.current_page = "Chat"
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
        
        if st.session_state.current_page == "Chat":
            display_chat_page()
        elif st.session_state.current_page == "Manage Custom Bots":
            display_custom_bots_page()
        elif st.session_state.current_page == "User Profile":
            display_user_profile_page()
        else:
            display_chat_page()

if __name__ == "__main__":
    main()


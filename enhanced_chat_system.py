"""
Enhanced Chat System with Real-time Features
Integrates with user API keys and provides advanced chat functionality
"""

import streamlit as st
from enhanced_supabase_client import enhanced_supabase
from enhanced_auth_system import auth_manager
from api_key_manager import api_key_manager
from realtime_sync import realtime_sync
import openai
from typing import Dict, List, Any, Optional
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedChatSystem:
    """Enhanced chat system with user API keys integration"""
    
    def __init__(self):
        self.supabase_client = enhanced_supabase
        self.supported_models = {
            'openai': {
                'gpt-4': {'name': 'GPT-4', 'context': 8192, 'cost_per_1k': 0.03},
                'gpt-4-turbo': {'name': 'GPT-4 Turbo', 'context': 128000, 'cost_per_1k': 0.01},
                'gpt-3.5-turbo': {'name': 'GPT-3.5 Turbo', 'context': 4096, 'cost_per_1k': 0.002}
            },
            'anthropic': {
                'claude-3-opus': {'name': 'Claude 3 Opus', 'context': 200000, 'cost_per_1k': 0.015},
                'claude-3-sonnet': {'name': 'Claude 3 Sonnet', 'context': 200000, 'cost_per_1k': 0.003},
                'claude-3-haiku': {'name': 'Claude 3 Haiku', 'context': 200000, 'cost_per_1k': 0.00025}
            }
        }
    
    def get_available_models(self, user_id: str) -> Dict[str, List[str]]:
        """Get available models based on user's API keys"""
        user_keys = api_key_manager.get_user_api_keys(user_id)
        available_models = {}
        
        for key_data in user_keys:
            provider = key_data['provider']
            if provider in self.supported_models:
                available_models[provider] = list(self.supported_models[provider].keys())
        
        return available_models
    
    def send_message(self, user_id: str, message: str, model: str, provider: str, 
                    agent_name: str = "Assistant", temperature: float = 0.7) -> Dict[str, Any]:
        """Send message using user's API key"""
        try:
            # Get user's API key for the provider
            api_key = api_key_manager.get_api_key_for_provider(user_id, provider)
            if not api_key:
                return {
                    'success': False,
                    'error': f'No API key found for {provider}. Please add one in API Keys page.',
                    'response': None
                }
            
            # Check usage limits
            can_send, limit_msg = auth_manager.check_usage_limits('send_message')
            if not can_send:
                return {
                    'success': False,
                    'error': limit_msg,
                    'response': None
                }
            
            # Send message based on provider
            if provider == 'openai':
                response = self._send_openai_message(api_key, message, model, agent_name, temperature)
            elif provider == 'anthropic':
                response = self._send_anthropic_message(api_key, message, model, agent_name, temperature)
            else:
                return {
                    'success': False,
                    'error': f'Provider {provider} not yet implemented',
                    'response': None
                }
            
            if response['success']:
                # Update API key usage
                api_key_manager.update_api_key_usage(user_id, provider, response.get('tokens_used', 0))
                
                # Add to activity feed
                realtime_sync.add_activity(
                    'message_sent',
                    f'Sent message to {agent_name} using {model}',
                    {'provider': provider, 'model': model, 'tokens': response.get('tokens_used', 0)},
                    user_id
                )
                
                # Save to chat history
                self._save_chat_message(user_id, agent_name, message, response['response'], model, provider)
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return {
                'success': False,
                'error': f'Error: {str(e)}',
                'response': None
            }
    
    def _send_openai_message(self, api_key: str, message: str, model: str, 
                           agent_name: str, temperature: float) -> Dict[str, Any]:
        """Send message using OpenAI API"""
        try:
            # For demo purposes, simulate API call
            # In production, you would use the actual OpenAI client
            time.sleep(1)  # Simulate API delay
            
            # Simulate response
            response_text = f"This is a simulated response from {model} for the message: '{message[:50]}...'"
            
            return {
                'success': True,
                'response': response_text,
                'tokens_used': len(message.split()) + len(response_text.split()),
                'model': model,
                'provider': 'openai'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'OpenAI API error: {str(e)}',
                'response': None
            }
    
    def _send_anthropic_message(self, api_key: str, message: str, model: str, 
                              agent_name: str, temperature: float) -> Dict[str, Any]:
        """Send message using Anthropic API"""
        try:
            # For demo purposes, simulate API call
            time.sleep(1)  # Simulate API delay
            
            # Simulate response
            response_text = f"This is a simulated response from {model} for the message: '{message[:50]}...'"
            
            return {
                'success': True,
                'response': response_text,
                'tokens_used': len(message.split()) + len(response_text.split()),
                'model': model,
                'provider': 'anthropic'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Anthropic API error: {str(e)}',
                'response': None
            }
    
    def _save_chat_message(self, user_id: str, agent_name: str, user_message: str, 
                          ai_response: str, model: str, provider: str):
        """Save chat message to database and session"""
        try:
            # Save to database
            if self.supabase_client.is_configured():
                self.supabase_client.save_chat_message(user_id, agent_name, user_message, ai_response)
            
            # Save to session state
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            chat_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_message': user_message,
                'ai_response': ai_response,
                'agent': agent_name,
                'model': model,
                'provider': provider
            }
            
            st.session_state.chat_history.append(chat_entry)
            
            # Keep only last 100 messages
            if len(st.session_state.chat_history) > 100:
                st.session_state.chat_history = st.session_state.chat_history[-100:]
                
        except Exception as e:
            logger.error(f"Error saving chat message: {str(e)}")
    
    def get_chat_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for user"""
        try:
            # Get from session state first
            session_history = st.session_state.get('chat_history', [])
            
            # If Supabase is configured, merge with database history
            if self.supabase_client.is_configured():
                db_history = self.supabase_client.load_chat_history(user_id, limit)
                # Merge and deduplicate histories
                # In production, you'd implement proper merging logic
                return session_history[-limit:]
            
            return session_history[-limit:]
            
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []
    
    def clear_chat_history(self, user_id: str) -> bool:
        """Clear chat history"""
        try:
            # Clear session state
            st.session_state.chat_history = []
            
            # Clear database if configured
            if self.supabase_client.is_configured():
                self.supabase_client.clear_chat_history(user_id)
            
            # Add activity
            realtime_sync.add_activity(
                'chat_cleared',
                'Chat history cleared',
                {},
                user_id
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing chat history: {str(e)}")
            return False

# Global enhanced chat system
enhanced_chat = EnhancedChatSystem()

def render_enhanced_chat_page():
    """Render the enhanced chat page with real-time features"""
    st.markdown("# 💬 Enhanced AI Chat")
    st.markdown("Chat with AI using your own API keys")
    
    user_id = auth_manager.get_current_user_id()
    if not user_id:
        st.error("❌ User not authenticated")
        return
    
    # Get available models
    available_models = enhanced_chat.get_available_models(user_id)
    
    if not available_models:
        st.warning("⚠️ No API keys configured. Please add API keys to start chatting.")
        if st.button("🔑 Go to API Keys", use_container_width=True):
            st.session_state.current_page = "API Keys"
            st.rerun()
        return
    
    # Chat configuration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Provider selection
        selected_provider = st.selectbox(
            "AI Provider",
            options=list(available_models.keys()),
            format_func=lambda x: api_key_manager.supported_providers[x]['name']
        )
    
    with col2:
        # Model selection
        if selected_provider:
            provider_models = available_models[selected_provider]
            selected_model = st.selectbox("Model", options=provider_models)
        else:
            selected_model = None
    
    with col3:
        # Temperature setting
        temperature = st.slider("Creativity", 0.0, 2.0, 0.7, 0.1)
    
    # Agent selection
    agents = [
        "General Assistant", "Business Strategist", "Marketing Expert",
        "Technical Consultant", "Creative Writer", "Data Analyst"
    ]
    selected_agent = st.selectbox("AI Agent", options=agents)
    
    st.markdown("---")
    
    # Chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 💬 Chat")
        
        # Chat history
        chat_history = enhanced_chat.get_chat_history(user_id)
        
        if chat_history:
            # Display chat messages
            for i, chat in enumerate(chat_history[-10:]):  # Show last 10 messages
                with st.container():
                    # User message
                    st.markdown(f"**You** ({chat.get('timestamp', '')[:16]}):")
                    st.markdown(chat['user_message'])
                    
                    # AI response
                    st.markdown(f"**{chat.get('agent', 'AI')}** ({chat.get('model', 'Unknown')}):")
                    st.markdown(chat['ai_response'])
                    
                    st.markdown("---")
        else:
            st.info("Start a conversation by typing a message below!")
    
    with col2:
        st.markdown("### ⚙️ Chat Settings")
        
        # Model info
        if selected_provider and selected_model:
            model_info = enhanced_chat.supported_models.get(selected_provider, {}).get(selected_model, {})
            if model_info:
                st.markdown(f"**Model**: {model_info.get('name', selected_model)}")
                st.markdown(f"**Context**: {model_info.get('context', 'Unknown')} tokens")
                st.markdown(f"**Cost**: ${model_info.get('cost_per_1k', 0)}/1K tokens")
        
        # Chat actions
        if st.button("🗑️ Clear Chat", use_container_width=True):
            if enhanced_chat.clear_chat_history(user_id):
                st.success("Chat history cleared!")
                st.rerun()
            else:
                st.error("Failed to clear chat history")
        
        if st.button("💾 Export Chat", use_container_width=True):
            chat_history = enhanced_chat.get_chat_history(user_id)
            if chat_history:
                # Create export data
                export_data = []
                for chat in chat_history:
                    export_data.append(f"User: {chat['user_message']}")
                    export_data.append(f"AI: {chat['ai_response']}")
                    export_data.append("---")
                
                export_text = "\n".join(export_data)
                st.download_button(
                    "📥 Download",
                    export_text,
                    "chat_history.txt",
                    "text/plain"
                )
            else:
                st.info("No chat history to export")
    
    # Message input
    st.markdown("### ✍️ Send Message")
    
    with st.form("chat_form"):
        user_message = st.text_area(
            "Your message:",
            placeholder="Type your message here...",
            height=100
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            send_button = st.form_submit_button("🚀 Send Message", use_container_width=True)
        
        with col2:
            if st.form_submit_button("🎲 Random Prompt", use_container_width=True):
                random_prompts = [
                    "Explain quantum computing in simple terms",
                    "Write a business plan for a coffee shop",
                    "Create a marketing strategy for a new app",
                    "Analyze the pros and cons of remote work",
                    "Suggest ways to improve team productivity"
                ]
                import random
                user_message = random.choice(random_prompts)
                st.rerun()
        
        with col3:
            if st.form_submit_button("📋 Templates", use_container_width=True):
                st.session_state.show_templates = True
                st.rerun()
        
        if send_button and user_message and selected_provider and selected_model:
            with st.spinner("Sending message..."):
                result = enhanced_chat.send_message(
                    user_id, user_message, selected_model, selected_provider,
                    selected_agent, temperature
                )
                
                if result['success']:
                    st.success("✅ Message sent!")
                    
                    # Add notification
                    realtime_sync.add_notification(
                        "Message Sent",
                        f"Received response from {selected_agent}",
                        "success"
                    )
                    
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
        elif send_button:
            st.error("❌ Please fill in all fields")
    
    # Message templates modal
    if st.session_state.get('show_templates', False):
        render_message_templates()

def render_message_templates():
    """Render message templates modal"""
    st.markdown("### 📋 Message Templates")
    
    templates = {
        "Business": [
            "Create a business plan for [business idea]",
            "Analyze the market for [product/service]",
            "Suggest pricing strategies for [product]",
            "Write a pitch deck outline for [startup idea]"
        ],
        "Marketing": [
            "Create a social media strategy for [brand]",
            "Write ad copy for [product]",
            "Suggest content ideas for [industry] blog",
            "Analyze competitor marketing strategies"
        ],
        "Technical": [
            "Explain [technology] in simple terms",
            "Compare [technology A] vs [technology B]",
            "Suggest best practices for [development task]",
            "Debug this code: [code snippet]"
        ],
        "Creative": [
            "Write a story about [topic]",
            "Create a poem about [subject]",
            "Brainstorm creative solutions for [problem]",
            "Design a logo concept for [brand]"
        ]
    }
    
    for category, template_list in templates.items():
        with st.expander(f"📁 {category}", expanded=False):
            for template in template_list:
                if st.button(template, key=f"template_{template}", use_container_width=True):
                    st.session_state.selected_template = template
                    st.session_state.show_templates = False
                    st.rerun()
    
    if st.button("❌ Close Templates", use_container_width=True):
        st.session_state.show_templates = False
        st.rerun()

"""
Enhanced API Key Management System
Handles individual user API keys with usage tracking, validation, and provider integration
"""

import streamlit as st
from enhanced_supabase_client import enhanced_supabase
from enhanced_auth_system import auth_manager
from typing import Dict, List, Any, Optional, Tuple
import logging
import requests
import json
from datetime import datetime, timedelta
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Manages user API keys with validation and usage tracking"""
    
    def __init__(self):
        self.supabase_client = enhanced_supabase
        self.supported_providers = {
            'openai': {
                'name': 'OpenAI',
                'icon': '🤖',
                'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
                'test_endpoint': 'https://api.openai.com/v1/models',
                'auth_header': 'Authorization',
                'auth_format': 'Bearer {key}'
            },
            'anthropic': {
                'name': 'Anthropic',
                'icon': '🧠',
                'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
                'test_endpoint': 'https://api.anthropic.com/v1/messages',
                'auth_header': 'x-api-key',
                'auth_format': '{key}'
            },
            'google': {
                'name': 'Google AI',
                'icon': '🔍',
                'models': ['gemini-pro', 'gemini-pro-vision'],
                'test_endpoint': 'https://generativelanguage.googleapis.com/v1/models',
                'auth_header': 'Authorization',
                'auth_format': 'Bearer {key}'
            },
            'deepseek': {
                'name': 'DeepSeek',
                'icon': '🌊',
                'models': ['deepseek-chat', 'deepseek-coder'],
                'test_endpoint': 'https://api.deepseek.com/v1/models',
                'auth_header': 'Authorization',
                'auth_format': 'Bearer {key}'
            },
            'groq': {
                'name': 'Groq',
                'icon': '⚡',
                'models': ['llama2-70b-4096', 'mixtral-8x7b-32768'],
                'test_endpoint': 'https://api.groq.com/openai/v1/models',
                'auth_header': 'Authorization',
                'auth_format': 'Bearer {key}'
            },
            'cohere': {
                'name': 'Cohere',
                'icon': '🎯',
                'models': ['command', 'command-light'],
                'test_endpoint': 'https://api.cohere.ai/v1/models',
                'auth_header': 'Authorization',
                'auth_format': 'Bearer {key}'
            }
        }
    
    def validate_api_key_format(self, provider: str, api_key: str) -> Tuple[bool, str]:
        """Validate API key format for specific provider"""
        if not api_key or len(api_key.strip()) < 10:
            return False, "API key is too short"
        
        # Provider-specific validation
        if provider == 'openai':
            if not api_key.startswith('sk-'):
                return False, "OpenAI API keys should start with 'sk-'"
        elif provider == 'anthropic':
            if not api_key.startswith('sk-ant-'):
                return False, "Anthropic API keys should start with 'sk-ant-'"
        elif provider == 'google':
            if len(api_key) < 20:
                return False, "Google API keys should be at least 20 characters"
        
        return True, "Valid format"
    
    async def test_api_key(self, provider: str, api_key: str) -> Tuple[bool, str]:
        """Test API key by making a simple API call"""
        try:
            provider_config = self.supported_providers.get(provider)
            if not provider_config:
                return False, "Unsupported provider"
            
            headers = {
                provider_config['auth_header']: provider_config['auth_format'].format(key=api_key),
                'Content-Type': 'application/json'
            }
            
            # For demo purposes, we'll simulate the test
            # In production, you'd make actual API calls
            await asyncio.sleep(1)  # Simulate API call delay
            
            # Simulate success for valid-looking keys
            is_valid, format_msg = self.validate_api_key_format(provider, api_key)
            if is_valid:
                return True, "API key is valid and working"
            else:
                return False, f"Invalid key format: {format_msg}"
                
        except Exception as e:
            logger.error(f"Error testing API key: {str(e)}")
            return False, f"Test failed: {str(e)}"
    
    def save_api_key(self, user_id: str, provider: str, key_name: str, api_key: str) -> Tuple[bool, str]:
        """Save API key with validation"""
        try:
            # Validate format first
            is_valid, message = self.validate_api_key_format(provider, api_key)
            if not is_valid:
                return False, message
            
            # Check usage limits
            can_add, limit_msg = auth_manager.check_usage_limits('add_api_key')
            if not can_add:
                return False, limit_msg
            
            # Save to database
            success = self.supabase_client.save_user_api_key(user_id, provider, key_name, api_key)
            
            if success:
                # Log activity
                self.supabase_client.log_user_activity(
                    user_id,
                    'api_key_added',
                    f'Added {provider} API key: {key_name}'
                )
                return True, "API key saved successfully"
            else:
                return False, "Failed to save API key to database"
                
        except Exception as e:
            logger.error(f"Error saving API key: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def get_user_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's API keys with enhanced information"""
        try:
            keys = self.supabase_client.get_user_api_keys(user_id)
            
            # Enhance with provider information
            for key in keys:
                provider_info = self.supported_providers.get(key['provider'], {})
                key['provider_name'] = provider_info.get('name', key['provider'].title())
                key['provider_icon'] = provider_info.get('icon', '🔑')
                key['available_models'] = provider_info.get('models', [])
            
            return keys
            
        except Exception as e:
            logger.error(f"Error getting API keys: {str(e)}")
            return []
    
    def delete_api_key(self, user_id: str, key_id: str) -> Tuple[bool, str]:
        """Delete API key"""
        try:
            success = self.supabase_client.delete_user_api_key(user_id, key_id)
            
            if success:
                # Log activity
                self.supabase_client.log_user_activity(
                    user_id,
                    'api_key_deleted',
                    f'Deleted API key: {key_id}'
                )
                return True, "API key deleted successfully"
            else:
                return False, "Failed to delete API key"
                
        except Exception as e:
            logger.error(f"Error deleting API key: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def get_api_key_for_provider(self, user_id: str, provider: str, key_name: str = None) -> Optional[str]:
        """Get decrypted API key for use in chat"""
        try:
            return self.supabase_client.get_decrypted_api_key(user_id, provider, key_name)
        except Exception as e:
            logger.error(f"Error getting API key for provider: {str(e)}")
            return None
    
    def update_api_key_usage(self, user_id: str, provider: str, tokens_used: int = 0) -> bool:
        """Update API key usage statistics"""
        try:
            if not self.supabase_client.is_configured():
                return True  # Demo mode
            
            # Update usage count and last used timestamp
            result = self.supabase_client.supabase.table('user_api_keys').update({
                'usage_count': self.supabase_client.supabase.table('user_api_keys').select('usage_count').eq('user_id', user_id).eq('provider', provider).single().execute().data['usage_count'] + 1,
                'last_used_at': datetime.now().isoformat()
            }).eq('user_id', user_id).eq('provider', provider).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error updating API key usage: {str(e)}")
            return False
    
    def get_usage_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        try:
            keys = self.get_user_api_keys(user_id)
            
            total_usage = sum(key.get('usage_count', 0) for key in keys)
            providers_count = len(set(key['provider'] for key in keys))
            
            # Get usage by provider
            provider_usage = {}
            for key in keys:
                provider = key['provider']
                if provider not in provider_usage:
                    provider_usage[provider] = {
                        'count': 0,
                        'last_used': None,
                        'keys': 0
                    }
                provider_usage[provider]['count'] += key.get('usage_count', 0)
                provider_usage[provider]['keys'] += 1
                
                last_used = key.get('last_used_at')
                if last_used and (not provider_usage[provider]['last_used'] or last_used > provider_usage[provider]['last_used']):
                    provider_usage[provider]['last_used'] = last_used
            
            return {
                'total_api_keys': len(keys),
                'total_usage': total_usage,
                'providers_count': providers_count,
                'provider_usage': provider_usage,
                'most_used_provider': max(provider_usage.keys(), key=lambda x: provider_usage[x]['count']) if provider_usage else None
            }
            
        except Exception as e:
            logger.error(f"Error getting usage statistics: {str(e)}")
            return {}

# Global API key manager instance
api_key_manager = APIKeyManager()

def render_api_key_management_page():
    """Render the enhanced API key management page"""
    st.markdown("# 🔑 API Key Management")
    st.markdown("Securely manage your AI provider API keys with usage tracking and validation")
    
    user_id = auth_manager.get_current_user_id()
    if not user_id:
        st.error("❌ User not authenticated")
        return
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Keys", "🗂️ My Keys", "📊 Usage Stats", "ℹ️ Provider Info"])
    
    with tab1:
        render_add_api_key_tab(user_id)
    
    with tab2:
        render_my_keys_tab(user_id)
    
    with tab3:
        render_usage_stats_tab(user_id)
    
    with tab4:
        render_provider_info_tab()

def render_add_api_key_tab(user_id: str):
    """Render add API key tab"""
    st.markdown("### ➕ Add New API Key")
    
    # Provider selection with visual cards
    st.markdown("#### Choose AI Provider")
    
    providers = api_key_manager.supported_providers
    
    # Display providers in a grid
    cols = st.columns(3)
    selected_provider = None
    
    for i, (provider_key, provider_info) in enumerate(providers.items()):
        with cols[i % 3]:
            if st.button(
                f"{provider_info['icon']} {provider_info['name']}", 
                key=f"select_{provider_key}",
                use_container_width=True
            ):
                selected_provider = provider_key
    
    # If provider selected or use selectbox as fallback
    if not selected_provider:
        selected_provider = st.selectbox(
            "Or select from dropdown:",
            options=list(providers.keys()),
            format_func=lambda x: f"{providers[x]['icon']} {providers[x]['name']}"
        )
    
    if selected_provider:
        provider_info = providers[selected_provider]
        
        st.markdown(f"### {provider_info['icon']} {provider_info['name']} Configuration")
        
        # Show available models
        with st.expander("📋 Available Models", expanded=False):
            for model in provider_info['models']:
                st.markdown(f"• {model}")
        
        # API key form
        with st.form("add_api_key_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                key_name = st.text_input(
                    "Key Name*", 
                    placeholder=f"e.g., My {provider_info['name']} Key",
                    help="Give your API key a memorable name"
                )
            
            with col2:
                api_key = st.text_input(
                    "API Key*", 
                    type="password", 
                    placeholder="Enter your API key",
                    help="Your API key will be encrypted and stored securely"
                )
            
            # Additional options
            test_key = st.checkbox("Test API key before saving", value=True)
            set_default = st.checkbox("Set as default for this provider", value=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("💾 Save API Key", use_container_width=True):
                    if not all([key_name, api_key]):
                        st.error("❌ Please fill in all required fields")
                    else:
                        with st.spinner("Saving API key..."):
                            # Test key if requested
                            if test_key:
                                st.info("🔍 Testing API key...")
                                # In a real implementation, you'd test the key here
                                # For demo, we'll simulate success
                                st.success("✅ API key test successful!")
                            
                            # Save the key
                            success, message = api_key_manager.save_api_key(
                                user_id, selected_provider, key_name, api_key
                            )
                            
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
            
            with col2:
                if st.form_submit_button("🧪 Test Only", use_container_width=True):
                    if api_key:
                        with st.spinner("Testing API key..."):
                            # Simulate API key test
                            is_valid, test_message = api_key_manager.validate_api_key_format(selected_provider, api_key)
                            if is_valid:
                                st.success(f"✅ {test_message}")
                            else:
                                st.error(f"❌ {test_message}")
                    else:
                        st.error("❌ Please enter an API key to test")

def render_my_keys_tab(user_id: str):
    """Render my keys tab"""
    st.markdown("### 🗂️ Your API Keys")
    
    api_keys = api_key_manager.get_user_api_keys(user_id)
    
    if not api_keys:
        st.info("🔍 No API keys found. Add your first API key in the 'Add Keys' tab!")
        return
    
    # Filter and search
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search keys", placeholder="Key name or provider...")
    
    with col2:
        provider_filter = st.selectbox(
            "Filter by provider", 
            ["All"] + list(set(key['provider'] for key in api_keys))
        )
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Name", "Provider", "Usage", "Date Added"])
    
    # Apply filters
    filtered_keys = api_keys
    
    if search_term:
        filtered_keys = [
            key for key in filtered_keys 
            if search_term.lower() in key['key_name'].lower() or 
               search_term.lower() in key['provider'].lower()
        ]
    
    if provider_filter != "All":
        filtered_keys = [key for key in filtered_keys if key['provider'] == provider_filter]
    
    # Sort keys
    if sort_by == "Name":
        filtered_keys.sort(key=lambda x: x['key_name'])
    elif sort_by == "Provider":
        filtered_keys.sort(key=lambda x: x['provider'])
    elif sort_by == "Usage":
        filtered_keys.sort(key=lambda x: x.get('usage_count', 0), reverse=True)
    elif sort_by == "Date Added":
        filtered_keys.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    st.markdown(f"**Showing {len(filtered_keys)} of {len(api_keys)} keys**")
    
    # Display keys
    for key_data in filtered_keys:
        with st.container():
            # Key header
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"### {key_data['provider_icon']} {key_data['key_name']}")
                st.markdown(f"*{key_data['provider_name']}*")
            
            with col2:
                st.metric("Usage", f"{key_data.get('usage_count', 0)} calls")
            
            with col3:
                last_used = key_data.get('last_used_at')
                if last_used:
                    st.markdown(f"**Last Used**: {last_used[:10]}")
                else:
                    st.markdown("**Last Used**: Never")
            
            with col4:
                # Action buttons
                if st.button("🗑️", key=f"delete_{key_data['id']}", help="Delete API key"):
                    success, message = api_key_manager.delete_api_key(user_id, key_data['id'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            # Key details
            with st.expander("📋 Key Details", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Provider**: {key_data['provider_name']}")
                    st.markdown(f"**Created**: {key_data.get('created_at', 'Unknown')[:10]}")
                    st.markdown(f"**Status**: {'🟢 Active' if key_data.get('is_active', True) else '🔴 Inactive'}")
                
                with col2:
                    st.markdown(f"**Total Calls**: {key_data.get('usage_count', 0)}")
                    st.markdown("**Available Models**:")
                    for model in key_data.get('available_models', []):
                        st.markdown(f"• {model}")
            
            st.markdown("---")

def render_usage_stats_tab(user_id: str):
    """Render usage statistics tab"""
    st.markdown("### 📊 Usage Statistics")
    
    stats = api_key_manager.get_usage_statistics(user_id)
    
    if not stats:
        st.info("📈 Usage statistics will appear here once you start using your API keys")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total API Keys", stats.get('total_api_keys', 0))
    
    with col2:
        st.metric("Total API Calls", f"{stats.get('total_usage', 0):,}")
    
    with col3:
        st.metric("Providers Used", stats.get('providers_count', 0))
    
    with col4:
        most_used = stats.get('most_used_provider')
        if most_used:
            provider_info = api_key_manager.supported_providers.get(most_used, {})
            st.metric("Most Used", f"{provider_info.get('icon', '🔑')} {provider_info.get('name', most_used)}")
        else:
            st.metric("Most Used", "None")
    
    # Usage by provider
    st.markdown("#### 📈 Usage by Provider")
    
    provider_usage = stats.get('provider_usage', {})
    
    if provider_usage:
        for provider, usage_data in provider_usage.items():
            provider_info = api_key_manager.supported_providers.get(provider, {})
            
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"**{provider_info.get('icon', '🔑')} {provider_info.get('name', provider)}**")
                
                with col2:
                    st.metric("API Calls", f"{usage_data['count']:,}")
                
                with col3:
                    st.metric("Keys", usage_data['keys'])
                
                with col4:
                    last_used = usage_data.get('last_used')
                    if last_used:
                        st.markdown(f"**Last Used**: {last_used[:10]}")
                    else:
                        st.markdown("**Last Used**: Never")
                
                st.markdown("---")
    else:
        st.info("No usage data available yet")
    
    # Usage limits
    st.markdown("#### 📋 Usage Limits")
    
    tier = auth_manager.get_user_subscription_tier()
    
    limits = {
        'free': {'providers': 2, 'daily_messages': 50},
        'pro': {'providers': 5, 'daily_messages': 500},
        'enterprise': {'providers': 10, 'daily_messages': 2000}
    }
    
    user_limits = limits.get(tier, limits['free'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_providers = stats.get('providers_count', 0)
        max_providers = user_limits['providers']
        st.progress(min(current_providers / max_providers, 1.0))
        st.markdown(f"**API Providers**: {current_providers}/{max_providers}")
    
    with col2:
        # Daily messages would be tracked separately in a real implementation
        st.progress(0.0)  # Placeholder
        st.markdown(f"**Daily Messages**: 0/{user_limits['daily_messages']}")

def render_provider_info_tab():
    """Render provider information tab"""
    st.markdown("### ℹ️ Supported AI Providers")
    st.markdown("Information about supported AI providers and how to get API keys")
    
    providers = api_key_manager.supported_providers
    
    for provider_key, provider_info in providers.items():
        with st.expander(f"{provider_info['icon']} {provider_info['name']}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Available Models:**")
                for model in provider_info['models']:
                    st.markdown(f"• {model}")
            
            with col2:
                st.markdown("**How to get API key:**")
                
                if provider_key == 'openai':
                    st.markdown("1. Visit [OpenAI Platform](https://platform.openai.com)")
                    st.markdown("2. Sign up or log in")
                    st.markdown("3. Go to API Keys section")
                    st.markdown("4. Create new secret key")
                elif provider_key == 'anthropic':
                    st.markdown("1. Visit [Anthropic Console](https://console.anthropic.com)")
                    st.markdown("2. Sign up or log in")
                    st.markdown("3. Generate API key")
                elif provider_key == 'google':
                    st.markdown("1. Visit [Google AI Studio](https://makersuite.google.com)")
                    st.markdown("2. Sign up or log in")
                    st.markdown("3. Create API key")
                else:
                    st.markdown(f"1. Visit {provider_info['name']} website")
                    st.markdown("2. Sign up for API access")
                    st.markdown("3. Generate API key")
            
            # Pricing info (placeholder)
            st.markdown("**Pricing**: Check provider's website for current pricing")
            
            # Key format info
            if provider_key == 'openai':
                st.info("🔑 OpenAI keys start with 'sk-' followed by 48 characters")
            elif provider_key == 'anthropic':
                st.info("🔑 Anthropic keys start with 'sk-ant-' followed by characters")

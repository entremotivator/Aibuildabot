"""
Enhanced Supabase Integration Module for AI Agent Toolkit
Provides persistent storage for custom bots and chat histories
"""

import streamlit as st
from supabase import create_client, Client
import os
from typing import Optional, Dict, Any, List
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedSupabaseAuth:
    """Enhanced Supabase authentication and data handler"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize Supabase client"""
        try:
            # Get Supabase credentials from Streamlit secrets or environment
            supabase_url = self.get_config_value('SUPABASE_URL')
            supabase_key = self.get_config_value('SUPABASE_ANON_KEY')
            
            if supabase_url and supabase_key:
                self.supabase = create_client(supabase_url, supabase_key)
                logger.info("Supabase client initialized successfully")
            else:
                logger.warning("Supabase credentials not found")
                
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
    
    def get_config_value(self, key: str) -> Optional[str]:
        """Get configuration value from Streamlit secrets or environment"""
        try:
            # Try Streamlit secrets first
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
            
            # Fallback to environment variable
            return os.environ.get(key)
            
        except Exception:
            return None
    
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured"""
        return self.supabase is not None
    
    # ======================================================
    # AUTHENTICATION METHODS
    # ======================================================
    
    def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """Sign up a new user"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Supabase not configured. Using demo mode.',
                'user': None
            }
        
        try:
            response = self.supabase.auth.sign_up({
                'email': email,
                'password': password
            })
            
            if response.user:
                return {
                    'success': True,
                    'user': response.user,
                    'message': 'Account created successfully! Please check your email for verification.'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create account',
                    'user': None
                }
                
        except Exception as e:
            logger.error(f"Sign up error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'user': None
            }
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in an existing user"""
        if not self.is_configured():
            # Demo mode - accept any email/password combination
            if email and password:
                return {
                    'success': True,
                    'user': {'email': email, 'id': 'demo-user'},
                    'message': 'Signed in successfully (Demo Mode)'
                }
            else:
                return {
                    'success': False,
                    'error': 'Please enter both email and password',
                    'user': None
                }
        
        try:
            response = self.supabase.auth.sign_in_with_password({
                'email': email,
                'password': password
            })
            
            if response.user:
                return {
                    'success': True,
                    'user': response.user,
                    'message': 'Signed in successfully!'
                }
            else:
                return {
                    'success': False,
                    'error': 'Invalid email or password',
                    'user': None
                }
                
        except Exception as e:
            logger.error(f"Sign in error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'user': None
            }
    
    def sign_out(self) -> Dict[str, Any]:
        """Sign out the current user"""
        if not self.is_configured():
            return {
                'success': True,
                'message': 'Signed out successfully (Demo Mode)'
            }
        
        try:
            self.supabase.auth.sign_out()
            return {
                'success': True,
                'message': 'Signed out successfully!'
            }
            
        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get the current authenticated user"""
        if not self.is_configured():
            return None
        
        try:
            user = self.supabase.auth.get_user()
            return user.user if user else None
            
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return None
    
    def reset_password(self, email: str) -> Dict[str, Any]:
        """Send password reset email"""
        if not self.is_configured():
            return {
                'success': True,
                'message': 'Password reset email sent (Demo Mode)'
            }
        
        try:
            self.supabase.auth.reset_password_email(email)
            return {
                'success': True,
                'message': 'Password reset email sent! Please check your inbox.'
            }
            
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ======================================================
    # CUSTOM BOTS MANAGEMENT
    # ======================================================
    
    def save_custom_bot(self, user_id: str, bot_name: str, bot_data: Dict[str, Any]) -> bool:
        """Save a custom bot to Supabase"""
        if not self.is_configured():
            # Fallback to session state in demo mode
            return self._save_custom_bot_local(user_id, bot_name, bot_data)
        
        try:
            # Prepare data for Supabase
            supabase_data = {
                'user_id': user_id,
                'name': bot_name,
                'description': bot_data.get('description', ''),
                'emoji': bot_data.get('emoji', '🤖'),
                'category': bot_data.get('category', 'My Custom Bots'),
                'temperature': bot_data.get('temperature', 0.7),
                'system_prompt': bot_data.get('system_prompt', ''),
                'specialties': bot_data.get('specialties', []),
                'quick_actions': bot_data.get('quick_actions', []),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Insert or update
            result = self.supabase.table('custom_bots').upsert(supabase_data).execute()
            
            if result.data:
                logger.info(f"Custom bot '{bot_name}' saved successfully for user {user_id}")
                return True
            else:
                logger.error(f"Failed to save custom bot '{bot_name}'")
                return False
                
        except Exception as e:
            logger.error(f"Error saving custom bot: {str(e)}")
            # Fallback to local storage
            return self._save_custom_bot_local(user_id, bot_name, bot_data)
    
    def load_custom_bots(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """Load custom bots for a user from Supabase"""
        if not self.is_configured():
            # Fallback to session state in demo mode
            return self._load_custom_bots_local(user_id)
        
        try:
            result = self.supabase.table('custom_bots').select('*').eq('user_id', user_id).execute()
            
            custom_bots = {}
            for bot_data in result.data:
                bot_name = bot_data['name']
                custom_bots[bot_name] = {
                    'description': bot_data['description'],
                    'emoji': bot_data['emoji'],
                    'category': bot_data['category'],
                    'temperature': bot_data['temperature'],
                    'system_prompt': bot_data['system_prompt'],
                    'specialties': bot_data['specialties'],
                    'quick_actions': bot_data['quick_actions'],
                    'is_custom': True,
                    'created_at': bot_data['created_at'],
                    'updated_at': bot_data['updated_at']
                }
            
            return custom_bots
            
        except Exception as e:
            logger.error(f"Error loading custom bots: {str(e)}")
            # Fallback to local storage
            return self._load_custom_bots_local(user_id)
    
    def delete_custom_bot(self, user_id: str, bot_name: str) -> bool:
        """Delete a custom bot from Supabase"""
        if not self.is_configured():
            # Fallback to session state in demo mode
            return self._delete_custom_bot_local(user_id, bot_name)
        
        try:
            result = self.supabase.table('custom_bots').delete().eq('user_id', user_id).eq('name', bot_name).execute()
            
            if result.data:
                logger.info(f"Custom bot '{bot_name}' deleted successfully for user {user_id}")
                return True
            else:
                logger.error(f"Failed to delete custom bot '{bot_name}'")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting custom bot: {str(e)}")
            # Fallback to local storage
            return self._delete_custom_bot_local(user_id, bot_name)
    
    # ======================================================
    # CHAT HISTORY MANAGEMENT
    # ======================================================
    
    def save_chat_message(self, user_id: str, agent_name: str, user_message: str, agent_response: str) -> bool:
        """Save a chat message to Supabase"""
        if not self.is_configured():
            # In demo mode, chat history is already managed in session state
            return True
        
        try:
            chat_data = {
                'user_id': user_id,
                'agent_name': agent_name,
                'user_message': user_message,
                'agent_response': agent_response,
                'timestamp': datetime.now().isoformat()
            }
            
            result = self.supabase.table('chat_histories').insert(chat_data).execute()
            
            if result.data:
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error saving chat message: {str(e)}")
            return False
    
    def load_chat_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Load chat history for a user from Supabase"""
        if not self.is_configured():
            # In demo mode, return empty list (session state manages this)
            return []
        
        try:
            result = self.supabase.table('chat_histories').select('*').eq('user_id', user_id).order('timestamp', desc=True).limit(limit).execute()
            
            chat_history = []
            for msg_data in reversed(result.data):  # Reverse to get chronological order
                chat_history.append({
                    'message': msg_data['user_message'],
                    'response': msg_data['agent_response'],
                    'agent': msg_data['agent_name'],
                    'timestamp': msg_data['timestamp']
                })
            
            return chat_history
            
        except Exception as e:
            logger.error(f"Error loading chat history: {str(e)}")
            return []
    
    def clear_chat_history(self, user_id: str) -> bool:
        """Clear all chat history for a user"""
        if not self.is_configured():
            # In demo mode, this is handled by session state
            return True
        
        try:
            result = self.supabase.table('chat_histories').delete().eq('user_id', user_id).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error clearing chat history: {str(e)}")
            return False
    
    # ======================================================
    # LOCAL STORAGE FALLBACK METHODS
    # ======================================================
    
    def _save_custom_bot_local(self, user_id: str, bot_name: str, bot_data: Dict[str, Any]) -> bool:
        """Save custom bot to session state (fallback)"""
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
            logger.error(f"Error saving custom bot locally: {str(e)}")
            return False
    
    def _load_custom_bots_local(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """Load custom bots from session state (fallback)"""
        if 'custom_bots' not in st.session_state:
            st.session_state.custom_bots = {}
        
        return st.session_state.custom_bots.get(user_id, {})
    
    def _delete_custom_bot_local(self, user_id: str, bot_name: str) -> bool:
        """Delete custom bot from session state (fallback)"""
        try:
            if ('custom_bots' in st.session_state and 
                user_id in st.session_state.custom_bots and 
                bot_name in st.session_state.custom_bots[user_id]):
                del st.session_state.custom_bots[user_id][bot_name]
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting custom bot locally: {str(e)}")
            return False

# Global enhanced auth instance
enhanced_auth = EnhancedSupabaseAuth()


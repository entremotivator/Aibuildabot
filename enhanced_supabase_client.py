"""
Enhanced Supabase Client with Real Authentication and Advanced Features
Provides comprehensive user management, API key handling, and real-time sync
"""

import streamlit as st
from supabase import create_client, Client
import os
from typing import Optional, Dict, Any, List, Tuple
import logging
import json
from datetime import datetime, timedelta
import hashlib
import secrets
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

class EnhancedSupabaseClient:
    """Enhanced Supabase client with real authentication and advanced features"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.encryption_key = None
        self.initialize_client()
        self.setup_encryption()
    
    def initialize_client(self):
        """Initialize Supabase client with proper configuration"""
        try:
            # Get Supabase credentials
            supabase_url = self.get_config_value('SUPABASE_URL')
            supabase_key = self.get_config_value('SUPABASE_ANON_KEY')
            
            if supabase_url and supabase_key:
                self.supabase = create_client(supabase_url, supabase_key)
                logger.info("Enhanced Supabase client initialized successfully")
                return True
            else:
                logger.warning("Supabase credentials not found - running in demo mode")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            return False
    
    def setup_encryption(self):
        """Setup encryption for API keys"""
        try:
            # Get or generate encryption key
            encryption_key = self.get_config_value('ENCRYPTION_KEY')
            if not encryption_key:
                # Generate a new key (in production, store this securely)
                encryption_key = Fernet.generate_key().decode()
                logger.warning("Generated new encryption key - store this securely!")
            
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode()
            
            self.encryption_key = Fernet(encryption_key)
            
        except Exception as e:
            logger.error(f"Failed to setup encryption: {str(e)}")
            # Fallback to base64 encoding
            self.encryption_key = None
    
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
    # ENCRYPTION UTILITIES
    # ======================================================
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt an API key for secure storage"""
        try:
            if self.encryption_key:
                encrypted = self.encryption_key.encrypt(api_key.encode())
                return base64.b64encode(encrypted).decode()
            else:
                # Fallback to base64 encoding (not secure, for demo only)
                return base64.b64encode(api_key.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            return api_key  # Return original if encryption fails
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt an API key for use"""
        try:
            if self.encryption_key:
                encrypted_data = base64.b64decode(encrypted_key.encode())
                decrypted = self.encryption_key.decrypt(encrypted_data)
                return decrypted.decode()
            else:
                # Fallback from base64 encoding
                return base64.b64decode(encrypted_key.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            return encrypted_key  # Return original if decryption fails
    
    # ======================================================
    # USER AUTHENTICATION
    # ======================================================
    
    def sign_up_user(self, email: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """Register a new user with Supabase Auth"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Supabase not configured',
                'user': None
            }
        
        try:
            # Sign up with Supabase Auth
            response = self.supabase.auth.sign_up({
                'email': email,
                'password': password,
                'options': {
                    'data': {
                        'full_name': full_name or email.split('@')[0]
                    }
                }
            })
            
            if response.user:
                # Create user profile
                self.create_user_profile(response.user.id, {
                    'full_name': full_name or email.split('@')[0],
                    'email': email
                })
                
                # Log activity
                self.log_user_activity(
                    response.user.id,
                    'user_registered',
                    f'New user registered: {email}'
                )
                
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
    
    def sign_in_user(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in user with Supabase Auth"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Supabase not configured',
                'user': None
            }
        
        try:
            response = self.supabase.auth.sign_in_with_password({
                'email': email,
                'password': password
            })
            
            if response.user:
                # Update last login
                self.supabase.table('users').update({
                    'last_login_at': datetime.now().isoformat()
                }).eq('id', response.user.id).execute()
                
                # Log activity
                self.log_user_activity(
                    response.user.id,
                    'user_login',
                    f'User logged in: {email}'
                )
                
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
    
    def sign_out_user(self) -> Dict[str, Any]:
        """Sign out current user"""
        if not self.is_configured():
            return {
                'success': True,
                'message': 'Signed out successfully'
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
        """Get current authenticated user"""
        if not self.is_configured():
            return None
        
        try:
            user = self.supabase.auth.get_user()
            return user.user if user else None
            
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return None
    
    # ======================================================
    # USER PROFILE MANAGEMENT
    # ======================================================
    
    def create_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Create user profile"""
        if not self.is_configured():
            return False
        
        try:
            # Insert into users table
            user_data = {
                'id': user_id,
                'email': profile_data.get('email'),
                'full_name': profile_data.get('full_name'),
                'role': 'user',
                'subscription_tier': 'free',
                'is_active': True,
                'email_verified': False
            }
            
            self.supabase.table('users').upsert(user_data).execute()
            
            # Insert into user_profiles table
            profile_data = {
                'user_id': user_id,
                'company_name': profile_data.get('company_name'),
                'job_title': profile_data.get('job_title'),
                'industry': profile_data.get('industry'),
                'preferences': profile_data.get('preferences', {})
            }
            
            self.supabase.table('user_profiles').upsert(profile_data).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get complete user profile"""
        if not self.is_configured():
            return None
        
        try:
            # Get user data with profile
            result = self.supabase.table('users').select(
                '*, user_profiles(*)'
            ).eq('id', user_id).single().execute()
            
            return result.data if result.data else None
            
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return None
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile"""
        if not self.is_configured():
            return False
        
        try:
            # Update users table
            user_updates = {k: v for k, v in updates.items() 
                          if k in ['full_name', 'avatar_url']}
            if user_updates:
                self.supabase.table('users').update(user_updates).eq('id', user_id).execute()
            
            # Update user_profiles table
            profile_updates = {k: v for k, v in updates.items() 
                             if k in ['company_name', 'job_title', 'industry', 'preferences']}
            if profile_updates:
                self.supabase.table('user_profiles').update(profile_updates).eq('user_id', user_id).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return False
    
    # ======================================================
    # API KEY MANAGEMENT
    # ======================================================
    
    def save_user_api_key(self, user_id: str, provider: str, key_name: str, api_key: str) -> bool:
        """Save encrypted API key for user"""
        if not self.is_configured():
            return False
        
        try:
            encrypted_key = self.encrypt_api_key(api_key)
            
            key_data = {
                'user_id': user_id,
                'provider': provider,
                'key_name': key_name,
                'encrypted_api_key': encrypted_key,
                'is_active': True
            }
            
            self.supabase.table('user_api_keys').upsert(key_data).execute()
            
            # Log activity
            self.log_user_activity(
                user_id,
                'api_key_saved',
                f'API key saved for {provider}'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving API key: {str(e)}")
            return False
    
    def get_user_api_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all API keys for user (without decrypting)"""
        if not self.is_configured():
            return []
        
        try:
            result = self.supabase.table('user_api_keys').select(
                'id, provider, key_name, is_active, usage_count, last_used_at, created_at'
            ).eq('user_id', user_id).eq('is_active', True).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting API keys: {str(e)}")
            return []
    
    def get_decrypted_api_key(self, user_id: str, provider: str, key_name: str = None) -> Optional[str]:
        """Get decrypted API key for use"""
        if not self.is_configured():
            return None
        
        try:
            query = self.supabase.table('user_api_keys').select('encrypted_api_key').eq('user_id', user_id).eq('provider', provider).eq('is_active', True)
            
            if key_name:
                query = query.eq('key_name', key_name)
            
            result = query.limit(1).execute()
            
            if result.data:
                encrypted_key = result.data[0]['encrypted_api_key']
                return self.decrypt_api_key(encrypted_key)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting decrypted API key: {str(e)}")
            return None
    
    def delete_user_api_key(self, user_id: str, key_id: str) -> bool:
        """Delete user API key"""
        if not self.is_configured():
            return False
        
        try:
            self.supabase.table('user_api_keys').update({
                'is_active': False
            }).eq('id', key_id).eq('user_id', user_id).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting API key: {str(e)}")
            return False
    
    # ======================================================
    # ACTIVITY LOGGING
    # ======================================================
    
    def log_user_activity(self, user_id: str, activity_type: str, description: str = None, metadata: Dict = None) -> bool:
        """Log user activity"""
        if not self.is_configured():
            return False
        
        try:
            activity_data = {
                'user_id': user_id,
                'activity_type': activity_type,
                'description': description,
                'metadata': metadata or {}
            }
            
            self.supabase.table('user_activity_log').insert(activity_data).execute()
            return True
            
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")
            return False
    
    def get_user_activity(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user activity log"""
        if not self.is_configured():
            return []
        
        try:
            result = self.supabase.table('user_activity_log').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting user activity: {str(e)}")
            return []
    
    # ======================================================
    # ADMIN FUNCTIONS
    # ======================================================
    
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users (admin only)"""
        if not self.is_configured():
            return []
        
        try:
            result = self.supabase.table('users').select(
                '*, user_profiles(*)'
            ).range(offset, offset + limit - 1).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return []
    
    def update_user_role(self, user_id: str, new_role: str) -> bool:
        """Update user role (admin only)"""
        if not self.is_configured():
            return False
        
        try:
            self.supabase.table('users').update({
                'role': new_role
            }).eq('id', user_id).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user role: {str(e)}")
            return False
    
    def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide analytics (admin only)"""
        if not self.is_configured():
            return {}
        
        try:
            # Get user counts
            users_result = self.supabase.table('users').select('role', count='exact').execute()
            
            # Get usage analytics
            usage_result = self.supabase.table('usage_analytics').select(
                'messages_sent, tokens_used, api_calls'
            ).execute()
            
            # Calculate totals
            total_messages = sum(row['messages_sent'] for row in usage_result.data) if usage_result.data else 0
            total_tokens = sum(row['tokens_used'] for row in usage_result.data) if usage_result.data else 0
            total_api_calls = sum(row['api_calls'] for row in usage_result.data) if usage_result.data else 0
            
            return {
                'total_users': users_result.count,
                'total_messages': total_messages,
                'total_tokens': total_tokens,
                'total_api_calls': total_api_calls
            }
            
        except Exception as e:
            logger.error(f"Error getting system analytics: {str(e)}")
            return {}

# Global enhanced client instance
enhanced_supabase = EnhancedSupabaseClient()

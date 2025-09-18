"""
Supabase Authentication Module for AI Agent Toolkit
"""

import streamlit as st
from supabase import create_client, Client
import os
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SupabaseAuth:
    """Supabase authentication handler"""
    
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

# Global auth instance
auth = SupabaseAuth()

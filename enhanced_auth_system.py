import streamlit as st
from enhanced_supabase_client import enhanced_supabase
from typing import Dict, Any, Optional
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class AuthenticationManager:
    """Manages user authentication and session state"""

    def __init__(self):
        self.supabase_client = enhanced_supabase

    # -------------------------
    # Session State Management
    # -------------------------
    def initialize_session_state(self):
        """Initialize authentication-related session state"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = None
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0
        if 'session_start_time' not in st.session_state:
            st.session_state.session_start_time = None

    # -------------------------
    # Validators
    # -------------------------
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            return False, "Password must contain at least one special character"
        return True, "Password is valid"

    # -------------------------
    # User Management
    # -------------------------
    def sign_up_user(
        self, email: str, password: str, full_name: str,
        company_name: str = None, job_title: str = None
    ) -> Dict[str, Any]:
        """Register a new user"""
        try:
            if not self.validate_email(email):
                return {'success': False, 'error': 'Invalid email format'}

            valid_password, password_message = self.validate_password(password)
            if not valid_password:
                return {'success': False, 'error': password_message}

            # Attempt registration
            result = self.supabase_client.sign_up_user(email, password, full_name)

            if result['success'] and result.get('user'):
                profile_updates = {}
                if company_name:
                    profile_updates['company_name'] = company_name
                if job_title:
                    profile_updates['job_title'] = job_title

                if profile_updates:
                    self.supabase_client.update_user_profile(
                        result['user'].id, profile_updates
                    )

            return result

        except Exception as e:
            logger.error(f"Sign up error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def sign_in_user(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in an existing user"""
        try:
            if not self.validate_email(email):
                return {'success': False, 'error': 'Invalid email format'}

            result = self.supabase_client.sign_in_user(email, password)

            if result['success'] and result.get('user'):
                profile = self.supabase_client.get_user_profile(result['user'].id)

                st.session_state.authenticated = True
                st.session_state.user_data = result['user']
                st.session_state.user_profile = profile
                st.session_state.login_attempts = 0
                st.session_state.session_start_time = datetime.now()

                if 'chat_history' not in st.session_state:
                    st.session_state.chat_history = []
                if 'current_agent' not in st.session_state:
                    st.session_state.current_agent = "Startup Strategist"
                if 'current_page' not in st.session_state:
                    st.session_state.current_page = "Chat"

            return result

        except Exception as e:
            logger.error(f"Sign in error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def sign_out_user(self) -> Dict[str, Any]:
        """Sign out current user"""
        try:
            result = self.supabase_client.sign_out_user()

            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.session_state.user_profile = None
            st.session_state.chat_history = []
            st.session_state.session_start_time = None

            for key in list(st.session_state.keys()):
                if key.startswith('custom_bots') or key.startswith('api_keys'):
                    del st.session_state[key]

            return result

        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def reset_password(self, email: str) -> Dict[str, Any]:
        """Send password reset email (Supabase stub)"""
        try:
            if not self.validate_email(email):
                return {'success': False, 'error': 'Invalid email format'}

            # Supabase client should expose a password reset function
            result = self.supabase_client.reset_password(email)
            return result

        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return {'success': False, 'error': str(e)}

    # -------------------------
    # Helpers
    # -------------------------
    def get_current_user_id(self) -> Optional[str]:
        """Get current user ID"""
        if st.session_state.authenticated and st.session_state.user_data:
            return st.session_state.user_data.id
        return None

    def is_admin(self) -> bool:
        """Check if current user is admin"""
        if not st.session_state.authenticated or not st.session_state.user_profile:
            return False
        return st.session_state.user_profile.get('role') == 'admin'

    def get_user_subscription_tier(self) -> str:
        """Get user's subscription tier"""
        if not st.session_state.authenticated or not st.session_state.user_profile:
            return 'free'
        return st.session_state.user_profile.get('subscription_tier', 'free')

    def check_usage_limits(self, action: str) -> tuple[bool, str]:
        """Check if user can perform action based on subscription limits"""
        if not st.session_state.authenticated:
            return False, "Please sign in to continue"

        tier = self.get_user_subscription_tier()

        limits = {
            'free': {'daily_messages': 50, 'custom_bots': 5, 'api_providers': 2},
            'pro': {'daily_messages': 500, 'custom_bots': 25, 'api_providers': 5},
            'enterprise': {'daily_messages': 2000, 'custom_bots': 100, 'api_providers': 10}
        }

        user_limits = limits.get(tier, limits['free'])

        if action == 'send_message':
            return True, "OK"
        elif action == 'create_custom_bot':
            custom_bots = st.session_state.get('custom_bots', {}).get(self.get_current_user_id(), {})
            if len(custom_bots) >= user_limits['custom_bots']:
                return False, f"Custom bot limit reached ({user_limits['custom_bots']} for {tier} tier)"
            return True, "OK"


# -------------------------
# Exports
# -------------------------
auth_manager = AuthenticationManager()

# Alias for compatibility with ai_agent_toolkit_final.py
EnhancedAuthSystem = AuthenticationManager

__all__ = ["AuthenticationManager", "EnhancedAuthSystem", "auth_manager"]


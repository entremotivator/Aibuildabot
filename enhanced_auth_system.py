import streamlit as st
from enhanced_supabase_client import enhanced_supabase
from typing import Dict, Any, Optional
import logging
import re
from datetime import datetime
from enhanced_auth_system import AuthSystem as EnhancedAuthSystem

logger = logging.getLogger(__name__)


class AuthenticationManager:
    """Manages user authentication and session state"""

    def __init__(self):
        self.supabase_client = enhanced_supabase

    def initialize_session_state(self):
        """Initialize authentication-related session state"""
        defaults = {
            "authenticated": False,
            "user_data": None,
            "user_profile": None,
            "login_attempts": 0,
            "session_start_time": None
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

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

    def sign_up_user(self, email: str, password: str, full_name: str,
                     company_name: str = None, job_title: str = None) -> Dict[str, Any]:
        """Register a new user"""
        try:
            if not self.validate_email(email):
                return {'success': False, 'error': 'Invalid email format'}

            valid_password, password_message = self.validate_password(password)
            if not valid_password:
                return {'success': False, 'error': password_message}

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

                st.session_state.setdefault("chat_history", [])
                st.session_state.setdefault("current_agent", "Startup Strategist")
                st.session_state.setdefault("current_page", "Chat")

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
                if key.startswith(('custom_bots', 'api_keys')):
                    del st.session_state[key]

            return result

        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            return {'success': False, 'error': str(e)}

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

        return True, "OK"


# Global instance
auth_manager = AuthenticationManager()


def render_authentication_ui():
    """Render the authentication UI"""
    auth_manager.initialize_session_state()

    st.markdown("""
    <style>
    .auth-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        color: white;
        text-align: center;
    }
    .auth-header { font-size: 3rem; margin-bottom: 1rem; }
    .auth-title { font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem; }
    .auth-subtitle { font-size: 1rem; opacity: 0.9; margin-bottom: 2rem; }
    .security-badge {
        background: rgba(40, 167, 69, 0.1);
        border: 1px solid #28a745;
        border-radius: 8px;
        padding: 0.5rem;
        margin: 1rem 0;
        color: #28a745;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-container">
        <div class="auth-header">🧠</div>
        <div class="auth-title">AI Agent Toolkit</div>
        <div class="auth-subtitle">Professional Multi-LLM Platform with Real User Management</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="security-badge">
        🔒 Enterprise-grade security with encrypted API key storage
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])
    with tab1:
        render_sign_in_form()
    with tab2:
        render_sign_up_form()

    st.markdown("### ✨ Platform Features")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **🤖 Multi-LLM Support**
        - OpenAI GPT-4/3.5
        - Anthropic Claude
        - Google Gemini
        - DeepSeek & Groq
        - Bring your own API keys
        """)
    with col2:
        st.markdown("""
        **🛠️ Custom AI Agents**
        - Create specialized bots
        - Business templates
        - Advanced prompt engineering
        - Share with team
        """)
    with col3:
        st.markdown("""
        **👥 User Management**
        - Individual API keys
        - Usage analytics
        - Admin dashboard
        - Real-time sync
        """)


def render_sign_in_form():
    """Render sign in form"""
    st.subheader("Welcome Back!")
    with st.form("sign_in_form"):
        email = st.text_input("📧 Email Address", placeholder="Enter your email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")

        col1, col2 = st.columns(2)
        with col1:
            remember_me = st.checkbox("Remember me")
        with col2:
            forgot_password = st.form_submit_button("Forgot Password?")

        sign_in_button = st.form_submit_button("🚀 Sign In", use_container_width=True)

        if forgot_password:
            st.info("Password reset will be handled with Supabase Auth")

        if sign_in_button:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                with st.spinner("Signing in..."):
                    result = auth_manager.sign_in_user(email, password)
                    if result['success']:
                        st.success(result['message'])
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        st.error(f"❌ {result['error']}")
                        if st.session_state.login_attempts >= 5:
                            st.warning("Too many failed attempts. Try again later.")


def render_sign_up_form():
    """Render sign up form"""
    st.subheader("Create Your Account")
    with st.form("sign_up_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("👤 Full Name*", placeholder="Enter your full name")
            email = st.text_input("📧 Email Address*", placeholder="Enter your email")
            password = st.text_input("🔒 Password*", type="password", placeholder="Create a strong password")
        with col2:
            company_name = st.text_input("🏢 Company Name", placeholder="Your company (optional)")
            job_title = st.text_input("💼 Job Title", placeholder="Your role (optional)")
            confirm_password = st.text_input("🔒 Confirm Password*", type="password", placeholder="Confirm password")

        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy*")
        newsletter = st.checkbox("Subscribe to product updates and tips")

        sign_up_button = st.form_submit_button("✨ Create Account", use_container_width=True)

        if sign_up_button:
            if not all([full_name, email, password, confirm_password]):
                st.error("Please fill in all required fields (*)")
            elif not auth_manager.validate_email(email):
                st.error("Invalid email format")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif not agree_terms:
                st.error("You must agree to the Terms of Service")
            else:
                with st.spinner("Creating your account..."):
                    result = auth_manager.sign_up_user(
                        email, password, full_name, company_name, job_title
                    )
                    if result['success']:
                        st.success("🎉 " + result['message'])
                        st.info("You can now sign in with your credentials!")
                    else:
                        st.error(f"❌ {result['error']}")


def render_user_header():
    """Render header for authenticated users"""
    if not st.session_state.authenticated:
        return

    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        user_name = st.session_state.user_profile.get('full_name', 'User') if st.session_state.user_profile else 'User'
        st.markdown(f"### 👋 Welcome back, {user_name}!")

    with col2:
        tier = auth_manager.get_user_subscription_tier()
        tier_icon = {'free': '🆓', 'pro': '⭐', 'enterprise': '💎'}
        st.metric("Plan", f"{tier_icon.get(tier, '🆓')} {tier.title()}")

    with col3:
        st.metric("Role", "👑 Admin" if auth_manager.is_admin() else "👤 User")

    with col4:
        if st.button("🚪 Sign Out", use_container_width=True):
            result = auth_manager.sign_out_user()
            if result['success']:
                st.success(result['message'])
                st.rerun()
            else:
                st.error(result['error'])

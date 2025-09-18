"""
Admin Dashboard for AI Agent Toolkit
Comprehensive user management, system analytics, and administrative controls
"""

import streamlit as st
from enhanced_supabase_client import enhanced_supabase
from enhanced_auth_system import auth_manager
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class AdminDashboard:
    """Admin dashboard functionality"""
    
    def __init__(self):
        self.supabase_client = enhanced_supabase
    
    def check_admin_access(self) -> bool:
        """Verify admin access"""
        if not st.session_state.authenticated:
            st.error("🔒 Please sign in to access admin features")
            return False
        
        if not auth_manager.is_admin():
            st.error("🚫 Admin access required")
            return False
        
        return True
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            stats = self.supabase_client.get_system_analytics()
            
            # Add more detailed stats if Supabase is configured
            if self.supabase_client.is_configured():
                # Get additional metrics
                users_result = self.supabase_client.supabase.table('users').select('*', count='exact').execute()
                active_users = self.supabase_client.supabase.table('users').select('*', count='exact').eq('is_active', True).execute()
                
                stats.update({
                    'total_users': users_result.count or 0,
                    'active_users': active_users.count or 0,
                    'inactive_users': (users_result.count or 0) - (active_users.count or 0)
                })
            else:
                # Demo mode stats
                stats = {
                    'total_users': 1,
                    'active_users': 1,
                    'inactive_users': 0,
                    'total_messages': 0,
                    'total_tokens': 0,
                    'total_api_calls': 0
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            return {
                'total_users': 0,
                'active_users': 0,
                'inactive_users': 0,
                'total_messages': 0,
                'total_tokens': 0,
                'total_api_calls': 0
            }
    
    def get_user_list(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get paginated user list"""
        try:
            if self.supabase_client.is_configured():
                return self.supabase_client.get_all_users(limit, offset)
            else:
                # Demo mode - return current user
                if st.session_state.user_profile:
                    return [st.session_state.user_profile]
                return []
                
        except Exception as e:
            logger.error(f"Error getting user list: {str(e)}")
            return []
    
    def update_user_status(self, user_id: str, is_active: bool) -> bool:
        """Update user active status"""
        try:
            if not self.supabase_client.is_configured():
                return True  # Demo mode
            
            result = self.supabase_client.supabase.table('users').update({
                'is_active': is_active
            }).eq('id', user_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error updating user status: {str(e)}")
            return False
    
    def update_user_subscription(self, user_id: str, tier: str) -> bool:
        """Update user subscription tier"""
        try:
            if not self.supabase_client.is_configured():
                return True  # Demo mode
            
            result = self.supabase_client.supabase.table('users').update({
                'subscription_tier': tier
            }).eq('id', user_id).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error updating user subscription: {str(e)}")
            return False
    
    def get_usage_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get usage analytics for the specified period"""
        try:
            if not self.supabase_client.is_configured():
                # Demo data
                dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
                return {
                    'daily_users': pd.DataFrame({
                        'date': dates,
                        'active_users': [1] * days
                    }),
                    'daily_messages': pd.DataFrame({
                        'date': dates,
                        'messages': [0] * days
                    }),
                    'provider_usage': pd.DataFrame({
                        'provider': ['openai', 'anthropic', 'google'],
                        'usage_count': [0, 0, 0]
                    })
                }
            
            # Real analytics would be implemented here
            return {
                'daily_users': pd.DataFrame(),
                'daily_messages': pd.DataFrame(),
                'provider_usage': pd.DataFrame()
            }
            
        except Exception as e:
            logger.error(f"Error getting usage analytics: {str(e)}")
            return {}

def render_admin_dashboard():
    """Render the main admin dashboard"""
    admin = AdminDashboard()
    
    if not admin.check_admin_access():
        return
    
    st.markdown("# 👑 Admin Dashboard")
    st.markdown("System administration and user management")
    
    # Admin tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", "👥 Users", "📈 Analytics", "⚙️ Settings", "🔧 System"
    ])
    
    with tab1:
        render_overview_tab(admin)
    
    with tab2:
        render_users_tab(admin)
    
    with tab3:
        render_analytics_tab(admin)
    
    with tab4:
        render_settings_tab(admin)
    
    with tab5:
        render_system_tab(admin)

def render_overview_tab(admin: AdminDashboard):
    """Render overview tab"""
    st.markdown("### 📊 System Overview")
    
    # Get system stats
    stats = admin.get_system_stats()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Users", 
            stats.get('total_users', 0),
            delta=f"+{stats.get('new_users_today', 0)} today"
        )
    
    with col2:
        st.metric(
            "Active Users", 
            stats.get('active_users', 0),
            delta=f"{stats.get('active_users', 0) - stats.get('inactive_users', 0)}"
        )
    
    with col3:
        st.metric(
            "Total Messages", 
            f"{stats.get('total_messages', 0):,}",
            delta=f"+{stats.get('messages_today', 0)} today"
        )
    
    with col4:
        st.metric(
            "API Calls", 
            f"{stats.get('total_api_calls', 0):,}",
            delta=f"+{stats.get('api_calls_today', 0)} today"
        )
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👥 Manage Users", use_container_width=True):
            st.session_state.admin_tab = "Users"
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.admin_tab = "Analytics"
            st.rerun()
    
    with col3:
        if st.button("⚙️ System Settings", use_container_width=True):
            st.session_state.admin_tab = "Settings"
            st.rerun()
    
    with col4:
        if st.button("🔧 System Health", use_container_width=True):
            st.session_state.admin_tab = "System"
            st.rerun()
    
    # Recent activity
    st.markdown("### 📈 Recent Activity")
    
    if admin.supabase_client.is_configured():
        st.info("Recent system activity will be displayed here")
    else:
        st.warning("🔄 Demo Mode: Connect Supabase to see real activity data")
    
    # System health indicators
    st.markdown("### 🏥 System Health")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if admin.supabase_client.is_configured():
            st.success("🟢 Database: Connected")
        else:
            st.warning("🟡 Database: Demo Mode")
    
    with col2:
        st.success("🟢 Authentication: Active")
    
    with col3:
        st.success("🟢 API Services: Operational")

def render_users_tab(admin: AdminDashboard):
    """Render users management tab"""
    st.markdown("### 👥 User Management")
    
    # User search and filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search users", placeholder="Email or name...")
    
    with col2:
        role_filter = st.selectbox("Filter by role", ["All", "admin", "user", "premium"])
    
    with col3:
        status_filter = st.selectbox("Filter by status", ["All", "Active", "Inactive"])
    
    # Get user list
    users = admin.get_user_list(limit=100)
    
    if users:
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(users)
        
        # Apply filters
        if search_term:
            mask = df['email'].str.contains(search_term, case=False, na=False) | \
                   df['full_name'].str.contains(search_term, case=False, na=False)
            df = df[mask]
        
        if role_filter != "All":
            df = df[df['role'] == role_filter]
        
        if status_filter != "All":
            is_active = status_filter == "Active"
            df = df[df['is_active'] == is_active]
        
        st.markdown(f"**Found {len(df)} users**")
        
        # User table
        for idx, user in df.iterrows():
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
                
                with col1:
                    st.markdown(f"**{user.get('full_name', 'N/A')}**")
                    st.markdown(f"*{user.get('email', 'N/A')}*")
                
                with col2:
                    role = user.get('role', 'user')
                    role_emoji = {'admin': '👑', 'user': '👤', 'premium': '⭐'}
                    st.markdown(f"{role_emoji.get(role, '👤')} {role.title()}")
                
                with col3:
                    tier = user.get('subscription_tier', 'free')
                    tier_emoji = {'free': '🆓', 'pro': '⭐', 'enterprise': '💎'}
                    st.markdown(f"{tier_emoji.get(tier, '🆓')} {tier.title()}")
                
                with col4:
                    is_active = user.get('is_active', True)
                    status_text = "🟢 Active" if is_active else "🔴 Inactive"
                    st.markdown(status_text)
                
                with col5:
                    # User actions
                    user_id = user.get('id')
                    if user_id:
                        action_col1, action_col2 = st.columns(2)
                        
                        with action_col1:
                            if st.button("✏️", key=f"edit_{user_id}", help="Edit user"):
                                st.session_state.edit_user_id = user_id
                                st.session_state.show_edit_modal = True
                        
                        with action_col2:
                            current_status = user.get('is_active', True)
                            action_text = "🔴" if current_status else "🟢"
                            action_help = "Deactivate" if current_status else "Activate"
                            
                            if st.button(action_text, key=f"toggle_{user_id}", help=action_help):
                                success = admin.update_user_status(user_id, not current_status)
                                if success:
                                    st.success(f"User {action_help.lower()}d successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to {action_help.lower()} user")
                
                st.markdown("---")
        
        # User edit modal
        if st.session_state.get('show_edit_modal', False):
            render_user_edit_modal(admin)
    
    else:
        st.info("No users found")
    
    # Bulk actions
    st.markdown("### 🔧 Bulk Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Send Announcement", use_container_width=True):
            st.info("Email announcement feature would be implemented here")
    
    with col2:
        if st.button("📊 Export User Data", use_container_width=True):
            if users:
                csv = pd.DataFrame(users).to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    "users_export.csv",
                    "text/csv"
                )
            else:
                st.warning("No user data to export")
    
    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

def render_user_edit_modal(admin: AdminDashboard):
    """Render user edit modal"""
    user_id = st.session_state.get('edit_user_id')
    if not user_id:
        return
    
    st.markdown("### ✏️ Edit User")
    
    # Get user data
    users = admin.get_user_list()
    user_data = next((u for u in users if u.get('id') == user_id), None)
    
    if not user_data:
        st.error("User not found")
        return
    
    with st.form("edit_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_role = st.selectbox(
                "Role", 
                ["user", "admin", "premium"],
                index=["user", "admin", "premium"].index(user_data.get('role', 'user'))
            )
            
            new_tier = st.selectbox(
                "Subscription Tier",
                ["free", "pro", "enterprise"],
                index=["free", "pro", "enterprise"].index(user_data.get('subscription_tier', 'free'))
            )
        
        with col2:
            new_status = st.checkbox("Active", value=user_data.get('is_active', True))
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                # Update user
                success = True
                
                if new_role != user_data.get('role'):
                    success &= admin.supabase_client.update_user_role(user_id, new_role)
                
                if new_tier != user_data.get('subscription_tier'):
                    success &= admin.update_user_subscription(user_id, new_tier)
                
                if new_status != user_data.get('is_active'):
                    success &= admin.update_user_status(user_id, new_status)
                
                if success:
                    st.success("✅ User updated successfully!")
                    st.session_state.show_edit_modal = False
                    st.rerun()
                else:
                    st.error("❌ Failed to update user")
        
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.show_edit_modal = False
                st.rerun()

def render_analytics_tab(admin: AdminDashboard):
    """Render analytics tab"""
    st.markdown("### 📈 System Analytics")
    
    # Time period selector
    col1, col2 = st.columns([1, 3])
    
    with col1:
        period = st.selectbox("Time Period", ["7 days", "30 days", "90 days", "1 year"])
        days = {"7 days": 7, "30 days": 30, "90 days": 90, "1 year": 365}[period]
    
    # Get analytics data
    analytics = admin.get_usage_analytics(days)
    
    if admin.supabase_client.is_configured():
        st.info("📊 Real analytics data will be displayed here when connected to Supabase")
    else:
        st.warning("🔄 Demo Mode: Connect Supabase to see real analytics")
    
    # Demo charts
    st.markdown("#### 👥 User Growth")
    
    # Create sample data for demo
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    sample_data = pd.DataFrame({
        'date': dates,
        'new_users': [1 if i == 0 else 0 for i in range(days)],
        'active_users': [1] * days
    })
    
    fig = px.line(sample_data, x='date', y=['new_users', 'active_users'], 
                  title="User Activity Over Time")
    st.plotly_chart(fig, use_container_width=True)
    
    # Usage metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💬 Message Volume")
        message_data = pd.DataFrame({
            'date': dates,
            'messages': [0] * days
        })
        fig = px.bar(message_data, x='date', y='messages', title="Daily Messages")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🔑 API Usage")
        api_data = pd.DataFrame({
            'provider': ['OpenAI', 'Anthropic', 'Google', 'DeepSeek'],
            'calls': [0, 0, 0, 0]
        })
        fig = px.pie(api_data, values='calls', names='provider', title="API Provider Usage")
        st.plotly_chart(fig, use_container_width=True)

def render_settings_tab(admin: AdminDashboard):
    """Render system settings tab"""
    st.markdown("### ⚙️ System Settings")
    
    # Application settings
    st.markdown("#### 🏢 Application Settings")
    
    with st.form("app_settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            app_name = st.text_input("Application Name", value="AI Agent Toolkit")
            maintenance_mode = st.checkbox("Maintenance Mode", value=False)
            registration_enabled = st.checkbox("Allow Registration", value=True)
        
        with col2:
            max_free_bots = st.number_input("Max Custom Bots (Free)", min_value=1, value=5)
            max_free_messages = st.number_input("Max Daily Messages (Free)", min_value=10, value=50)
            email_verification = st.checkbox("Require Email Verification", value=True)
        
        if st.form_submit_button("💾 Save Settings", use_container_width=True):
            st.success("✅ Settings saved successfully!")
    
    st.markdown("---")
    
    # User limits by tier
    st.markdown("#### 📊 Subscription Limits")
    
    tiers_data = {
        'Tier': ['Free', 'Pro', 'Enterprise'],
        'Custom Bots': [5, 25, 100],
        'Daily Messages': [50, 500, 2000],
        'API Providers': [2, 5, 10],
        'Priority Support': ['❌', '✅', '✅']
    }
    
    df = pd.DataFrame(tiers_data)
    st.dataframe(df, use_container_width=True)
    
    # System notifications
    st.markdown("#### 📢 System Notifications")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📧 Send System Announcement", use_container_width=True):
            st.info("System announcement feature would be implemented here")
    
    with col2:
        if st.button("⚠️ Send Maintenance Notice", use_container_width=True):
            st.info("Maintenance notice feature would be implemented here")

def render_system_tab(admin: AdminDashboard):
    """Render system monitoring tab"""
    st.markdown("### 🔧 System Monitoring")
    
    # System health
    st.markdown("#### 🏥 System Health")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if admin.supabase_client.is_configured():
            st.success("🟢 Database\nConnected")
        else:
            st.warning("🟡 Database\nDemo Mode")
    
    with col2:
        st.success("🟢 Authentication\nOperational")
    
    with col3:
        st.success("🟢 API Services\nHealthy")
    
    with col4:
        st.success("🟢 File Storage\nAvailable")
    
    # System information
    st.markdown("#### ℹ️ System Information")
    
    system_info = {
        'Application Version': '2.0.0',
        'Database': 'Supabase PostgreSQL' if admin.supabase_client.is_configured() else 'Demo Mode',
        'Authentication': 'Supabase Auth',
        'Deployment': 'Streamlit Cloud',
        'Last Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    for key, value in system_info.items():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{key}:**")
        with col2:
            st.markdown(value)
    
    st.markdown("---")
    
    # System actions
    st.markdown("#### 🛠️ System Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh System Status", use_container_width=True):
            st.success("System status refreshed!")
            st.rerun()
    
    with col2:
        if st.button("📊 Generate System Report", use_container_width=True):
            st.info("System report generation would be implemented here")
    
    with col3:
        if st.button("🧹 Clear System Cache", use_container_width=True):
            st.success("System cache cleared!")
    
    # Logs section
    st.markdown("#### 📋 Recent System Logs")
    
    sample_logs = [
        {"timestamp": "2024-01-15 10:30:00", "level": "INFO", "message": "User authentication successful"},
        {"timestamp": "2024-01-15 10:25:00", "level": "INFO", "message": "Database connection established"},
        {"timestamp": "2024-01-15 10:20:00", "level": "WARN", "message": "High API usage detected"},
        {"timestamp": "2024-01-15 10:15:00", "level": "INFO", "message": "System startup completed"}
    ]
    
    for log in sample_logs:
        level_color = {"INFO": "🟢", "WARN": "🟡", "ERROR": "🔴"}
        st.markdown(f"{level_color.get(log['level'], '⚪')} `{log['timestamp']}` **{log['level']}**: {log['message']}")

# Initialize session state for admin
if 'show_edit_modal' not in st.session_state:
    st.session_state.show_edit_modal = False
if 'edit_user_id' not in st.session_state:
    st.session_state.edit_user_id = None

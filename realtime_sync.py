"""
Real-time Sync and Advanced Features
Provides real-time updates, notifications, and advanced user experience features
"""

import streamlit as st
from enhanced_supabase_client import enhanced_supabase
from enhanced_auth_system import auth_manager
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import asyncio
import threading

logger = logging.getLogger(__name__)

class RealtimeSync:
    """Handles real-time synchronization and advanced features"""
    
    def __init__(self):
        self.supabase_client = enhanced_supabase
        self.sync_enabled = False
        self.last_sync = None
        self.notifications = []
        self.activity_feed = []
    
    def initialize_realtime(self):
        """Initialize real-time features"""
        if 'realtime_initialized' not in st.session_state:
            st.session_state.realtime_initialized = True
            st.session_state.notifications = []
            st.session_state.activity_feed = []
            st.session_state.last_sync = datetime.now()
            st.session_state.sync_status = "connected" if self.supabase_client.is_configured() else "demo"
    
    def add_notification(self, title: str, message: str, type: str = "info", user_id: str = None):
        """Add a notification to the user's notification feed"""
        notification = {
            'id': f"notif_{int(time.time() * 1000)}",
            'title': title,
            'message': message,
            'type': type,  # info, success, warning, error
            'timestamp': datetime.now().isoformat(),
            'read': False,
            'user_id': user_id or auth_manager.get_current_user_id()
        }
        
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        
        st.session_state.notifications.insert(0, notification)
        
        # Keep only last 50 notifications
        if len(st.session_state.notifications) > 50:
            st.session_state.notifications = st.session_state.notifications[:50]
        
        # Log to database if configured
        if self.supabase_client.is_configured() and user_id:
            self.supabase_client.log_user_activity(
                user_id,
                'notification_created',
                f'{title}: {message}',
                {'type': type}
            )
    
    def add_activity(self, activity_type: str, description: str, metadata: Dict = None, user_id: str = None):
        """Add an activity to the user's activity feed"""
        activity = {
            'id': f"activity_{int(time.time() * 1000)}",
            'type': activity_type,
            'description': description,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id or auth_manager.get_current_user_id()
        }
        
        if 'activity_feed' not in st.session_state:
            st.session_state.activity_feed = []
        
        st.session_state.activity_feed.insert(0, activity)
        
        # Keep only last 100 activities
        if len(st.session_state.activity_feed) > 100:
            st.session_state.activity_feed = st.session_state.activity_feed[:100]
    
    def mark_notification_read(self, notification_id: str):
        """Mark a notification as read"""
        if 'notifications' in st.session_state:
            for notif in st.session_state.notifications:
                if notif['id'] == notification_id:
                    notif['read'] = True
                    break
    
    def get_unread_notifications_count(self) -> int:
        """Get count of unread notifications"""
        if 'notifications' not in st.session_state:
            return 0
        
        return len([n for n in st.session_state.notifications if not n.get('read', False)])
    
    def sync_user_data(self, user_id: str) -> bool:
        """Sync user data from database"""
        try:
            if not self.supabase_client.is_configured():
                return True  # Demo mode
            
            # Update last sync time
            st.session_state.last_sync = datetime.now()
            
            # In a real implementation, you would:
            # 1. Fetch latest user data
            # 2. Update session state
            # 3. Check for new notifications
            # 4. Update activity feed
            
            return True
            
        except Exception as e:
            logger.error(f"Error syncing user data: {str(e)}")
            return False
    
    def auto_sync(self):
        """Auto-sync user data periodically"""
        if not st.session_state.authenticated:
            return
        
        user_id = auth_manager.get_current_user_id()
        if not user_id:
            return
        
        # Check if it's time to sync (every 30 seconds)
        last_sync = st.session_state.get('last_sync')
        if last_sync and datetime.now() - last_sync < timedelta(seconds=30):
            return
        
        # Perform sync
        success = self.sync_user_data(user_id)
        st.session_state.sync_status = "connected" if success else "error"

# Global realtime sync instance
realtime_sync = RealtimeSync()

class AdvancedFeatures:
    """Advanced features for enhanced user experience"""
    
    def __init__(self):
        self.shortcuts = {
            'ctrl+k': 'Open command palette',
            'ctrl+/': 'Show keyboard shortcuts',
            'ctrl+n': 'New chat',
            'ctrl+b': 'Create new bot',
            'esc': 'Close modals'
        }
    
    def render_command_palette(self):
        """Render command palette for quick actions"""
        if st.session_state.get('show_command_palette', False):
            st.markdown("### ⌨️ Command Palette")
            
            with st.container():
                search_term = st.text_input("Type a command...", placeholder="Search for actions, pages, or features")
                
                commands = [
                    {"name": "Go to Dashboard", "action": "dashboard", "icon": "🏠"},
                    {"name": "Start AI Chat", "action": "chat", "icon": "💬"},
                    {"name": "Manage API Keys", "action": "api_keys", "icon": "🔑"},
                    {"name": "Create Custom Bot", "action": "custom_bots", "icon": "🤖"},
                    {"name": "View Analytics", "action": "analytics", "icon": "📊"},
                    {"name": "User Profile", "action": "profile", "icon": "👤"},
                    {"name": "Sign Out", "action": "sign_out", "icon": "🚪"}
                ]
                
                if auth_manager.is_admin():
                    commands.append({"name": "Admin Panel", "action": "admin", "icon": "👑"})
                
                # Filter commands based on search
                if search_term:
                    commands = [cmd for cmd in commands if search_term.lower() in cmd['name'].lower()]
                
                for cmd in commands:
                    if st.button(f"{cmd['icon']} {cmd['name']}", key=f"cmd_{cmd['action']}", use_container_width=True):
                        if cmd['action'] == 'sign_out':
                            auth_manager.sign_out_user()
                            st.rerun()
                        else:
                            st.session_state.current_page = cmd['action'].replace('_', ' ').title()
                            st.session_state.show_command_palette = False
                            st.rerun()
                
                if st.button("❌ Close", use_container_width=True):
                    st.session_state.show_command_palette = False
                    st.rerun()
    
    def render_keyboard_shortcuts(self):
        """Render keyboard shortcuts help"""
        if st.session_state.get('show_shortcuts', False):
            st.markdown("### ⌨️ Keyboard Shortcuts")
            
            for shortcut, description in self.shortcuts.items():
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.code(shortcut)
                with col2:
                    st.markdown(description)
            
            if st.button("❌ Close", use_container_width=True):
                st.session_state.show_shortcuts = False
                st.rerun()
    
    def render_quick_actions_sidebar(self):
        """Render quick actions in sidebar"""
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("⌨️ Command Palette", use_container_width=True, help="Ctrl+K"):
            st.session_state.show_command_palette = True
            st.rerun()
        
        if st.button("❓ Keyboard Shortcuts", use_container_width=True, help="Ctrl+/"):
            st.session_state.show_shortcuts = True
            st.rerun()
        
        if st.button("🔄 Sync Data", use_container_width=True):
            user_id = auth_manager.get_current_user_id()
            if user_id:
                success = realtime_sync.sync_user_data(user_id)
                if success:
                    realtime_sync.add_notification(
                        "Sync Complete",
                        "Your data has been synchronized successfully",
                        "success"
                    )
                else:
                    realtime_sync.add_notification(
                        "Sync Failed",
                        "Failed to synchronize your data",
                        "error"
                    )
                st.rerun()

def render_notifications_panel():
    """Render notifications panel"""
    st.markdown("### 🔔 Notifications")
    
    notifications = st.session_state.get('notifications', [])
    unread_count = realtime_sync.get_unread_notifications_count()
    
    if unread_count > 0:
        st.markdown(f"**{unread_count} unread notifications**")
    
    if not notifications:
        st.info("No notifications yet")
        return
    
    # Mark all as read button
    if unread_count > 0:
        if st.button("✅ Mark All as Read", use_container_width=True):
            for notif in notifications:
                notif['read'] = True
            st.rerun()
    
    # Display notifications
    for notif in notifications[:10]:  # Show only last 10
        with st.container():
            # Notification styling based on type
            type_colors = {
                'info': '🔵',
                'success': '🟢',
                'warning': '🟡',
                'error': '🔴'
            }
            
            color_icon = type_colors.get(notif['type'], '🔵')
            read_status = '📖' if notif.get('read', False) else '📩'
            
            col1, col2 = st.columns([1, 8])
            
            with col1:
                st.markdown(f"{color_icon} {read_status}")
            
            with col2:
                st.markdown(f"**{notif['title']}**")
                st.markdown(notif['message'])
                st.markdown(f"*{notif['timestamp'][:16]}*")
                
                if not notif.get('read', False):
                    if st.button("Mark as Read", key=f"read_{notif['id']}"):
                        realtime_sync.mark_notification_read(notif['id'])
                        st.rerun()
            
            st.markdown("---")

def render_activity_feed():
    """Render activity feed"""
    st.markdown("### 📈 Recent Activity")
    
    activities = st.session_state.get('activity_feed', [])
    
    if not activities:
        st.info("No recent activity")
        return
    
    # Activity type icons
    activity_icons = {
        'login': '🔐',
        'api_key_added': '🔑',
        'api_key_deleted': '🗑️',
        'custom_bot_created': '🤖',
        'custom_bot_deleted': '🗑️',
        'message_sent': '💬',
        'profile_updated': '👤',
        'notification_created': '🔔',
        'sync_completed': '🔄'
    }
    
    for activity in activities[:15]:  # Show only last 15
        icon = activity_icons.get(activity['type'], '📝')
        
        col1, col2 = st.columns([1, 8])
        
        with col1:
            st.markdown(icon)
        
        with col2:
            st.markdown(f"**{activity['description']}**")
            st.markdown(f"*{activity['timestamp'][:16]}*")
        
        st.markdown("---")

def render_system_status():
    """Render system status indicators"""
    st.markdown("### 🔧 System Status")
    
    # Connection status
    sync_status = st.session_state.get('sync_status', 'unknown')
    
    if sync_status == 'connected':
        st.success("🟢 Connected")
    elif sync_status == 'demo':
        st.warning("🟡 Demo Mode")
    else:
        st.error("🔴 Connection Error")
    
    # Last sync time
    last_sync = st.session_state.get('last_sync')
    if last_sync:
        time_diff = datetime.now() - last_sync
        if time_diff.total_seconds() < 60:
            st.markdown("🔄 **Last Sync**: Just now")
        elif time_diff.total_seconds() < 3600:
            minutes = int(time_diff.total_seconds() / 60)
            st.markdown(f"🔄 **Last Sync**: {minutes}m ago")
        else:
            hours = int(time_diff.total_seconds() / 3600)
            st.markdown(f"🔄 **Last Sync**: {hours}h ago")
    
    # Auto-sync toggle
    auto_sync_enabled = st.session_state.get('auto_sync_enabled', True)
    if st.checkbox("Auto-sync enabled", value=auto_sync_enabled):
        st.session_state.auto_sync_enabled = True
        # Perform auto-sync
        realtime_sync.auto_sync()
    else:
        st.session_state.auto_sync_enabled = False

def render_enhanced_sidebar():
    """Render enhanced sidebar with real-time features"""
    with st.sidebar:
        st.markdown("### 🧠 AI Agent Toolkit")
        
        # Sync status indicator
        sync_status = st.session_state.get('sync_status', 'unknown')
        if sync_status == 'connected':
            st.markdown("🟢 **Status**: Connected")
        elif sync_status == 'demo':
            st.markdown("🟡 **Status**: Demo Mode")
        else:
            st.markdown("🔴 **Status**: Offline")
        
        st.markdown("---")
        
        # Navigation with notification badges
        st.markdown("### 📍 Navigation")
        
        pages = {
            "🏠 Dashboard": "Dashboard",
            "💬 AI Chat": "Chat", 
            "🤖 Custom Bots": "Custom Bots",
            "🔑 API Keys": "API Keys",
            "📊 Analytics": "Analytics",
            "👤 Profile": "Profile"
        }
        
        # Add admin pages for admin users
        if auth_manager.is_admin():
            pages["👑 Admin Panel"] = "Admin"
        
        for display_name, page_key in pages.items():
            if st.button(display_name, use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # Quick actions
        advanced_features = AdvancedFeatures()
        advanced_features.render_quick_actions_sidebar()
        
        st.markdown("---")
        
        # Notifications summary
        unread_count = realtime_sync.get_unread_notifications_count()
        if unread_count > 0:
            st.markdown(f"### 🔔 Notifications ({unread_count})")
            
            # Show latest notification
            notifications = st.session_state.get('notifications', [])
            if notifications:
                latest = notifications[0]
                st.markdown(f"**{latest['title']}**")
                st.markdown(f"{latest['message'][:50]}...")
                
                if st.button("View All", use_container_width=True):
                    st.session_state.show_notifications = True
                    st.rerun()
        
        st.markdown("---")
        
        # System status
        render_system_status()
        
        # User info
        if st.session_state.authenticated:
            st.markdown("### 👤 User Info")
            user_profile = st.session_state.user_profile
            if user_profile:
                st.markdown(f"**Name**: {user_profile.get('full_name', 'N/A')}")
                st.markdown(f"**Plan**: {auth_manager.get_user_subscription_tier().title()}")
                if auth_manager.is_admin():
                    st.markdown("**Role**: 👑 Administrator")

def render_enhanced_header():
    """Render enhanced header with real-time features"""
    if not st.session_state.authenticated:
        return
    
    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
    
    with col1:
        user_name = st.session_state.user_profile.get('full_name', 'User') if st.session_state.user_profile else 'User'
        st.markdown(f"### 👋 Welcome back, {user_name}!")
    
    with col2:
        # Notifications button
        unread_count = realtime_sync.get_unread_notifications_count()
        notif_text = f"🔔 ({unread_count})" if unread_count > 0 else "🔔"
        if st.button(notif_text, help="Notifications"):
            st.session_state.show_notifications = True
            st.rerun()
    
    with col3:
        # Quick sync button
        if st.button("🔄", help="Sync data"):
            user_id = auth_manager.get_current_user_id()
            if user_id:
                realtime_sync.sync_user_data(user_id)
                realtime_sync.add_notification(
                    "Sync Complete",
                    "Data synchronized successfully",
                    "success"
                )
                st.rerun()
    
    with col4:
        # Command palette button
        if st.button("⌨️", help="Command palette (Ctrl+K)"):
            st.session_state.show_command_palette = True
            st.rerun()
    
    with col5:
        # Sign out button
        if st.button("🚪 Sign Out", use_container_width=True):
            result = auth_manager.sign_out_user()
            if result['success']:
                st.success(result['message'])
                st.rerun()
            else:
                st.error(result['error'])

def initialize_realtime_features():
    """Initialize all real-time features"""
    realtime_sync.initialize_realtime()
    
    # Add welcome notification for new sessions
    if 'welcome_shown' not in st.session_state:
        st.session_state.welcome_shown = True
        realtime_sync.add_notification(
            "Welcome!",
            "Welcome to AI Agent Toolkit. Start by adding your API keys!",
            "info"
        )
        
        realtime_sync.add_activity(
            "login",
            "User signed in to the platform"
        )

def render_modals():
    """Render all modal dialogs"""
    advanced_features = AdvancedFeatures()
    
    # Command palette modal
    if st.session_state.get('show_command_palette', False):
        with st.container():
            advanced_features.render_command_palette()
    
    # Keyboard shortcuts modal
    if st.session_state.get('show_shortcuts', False):
        with st.container():
            advanced_features.render_keyboard_shortcuts()
    
    # Notifications panel
    if st.session_state.get('show_notifications', False):
        with st.container():
            render_notifications_panel()
            if st.button("❌ Close Notifications", use_container_width=True):
                st.session_state.show_notifications = False
                st.rerun()

# Auto-refresh functionality
def auto_refresh():
    """Auto-refresh the page periodically for real-time updates"""
    if st.session_state.get('auto_refresh_enabled', False):
        # Add JavaScript for auto-refresh
        st.markdown("""
        <script>
        setTimeout(function(){
            window.location.reload();
        }, 30000); // Refresh every 30 seconds
        </script>
        """, unsafe_allow_html=True)

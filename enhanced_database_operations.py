import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional
import plotly.express as px
import plotly.graph_objects as go
from enhanced_supabase_client import EnhancedSupabaseClient

class DatabaseOperationsManager:
    def __init__(self, supabase_client: EnhancedSupabaseClient):
        self.supabase = supabase_client
        
    def render_database_operations(self, user_id: str, is_admin: bool = False):
        """Render comprehensive database operations interface"""
        st.header("🗄️ Database Operations")
        
        # Create tabs for different operations
        if is_admin:
            tabs = st.tabs(["Query Builder", "Data Analytics", "Backup & Export", "System Monitoring", "Advanced SQL"])
        else:
            tabs = st.tabs(["Query Builder", "My Data Analytics", "Export My Data"])
            
        with tabs[0]:
            self._render_query_builder(user_id, is_admin)
            
        with tabs[1]:
            self._render_data_analytics(user_id, is_admin)
            
        with tabs[2]:
            self._render_backup_export(user_id, is_admin)
            
        if is_admin:
            with tabs[3]:
                self._render_system_monitoring()
                
            with tabs[4]:
                self._render_advanced_sql()
    
    def _render_query_builder(self, user_id: str, is_admin: bool):
        """Visual query builder interface"""
        st.subheader("Visual Query Builder")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Table selection
            if is_admin:
                available_tables = ["users", "user_profiles", "api_keys", "chat_sessions", 
                                  "messages", "user_activity", "system_settings", "notifications"]
            else:
                available_tables = ["chat_sessions", "messages", "user_activity"]
                
            selected_table = st.selectbox("Select Table", available_tables)
            
            # Column selection
            if selected_table:
                columns = self._get_table_columns(selected_table)
                selected_columns = st.multiselect("Select Columns", columns, default=columns[:3])
                
            # Filters
            st.subheader("Filters")
            filter_column = st.selectbox("Filter Column", columns if selected_table else [])
            filter_operator = st.selectbox("Operator", ["=", "!=", ">", "<", ">=", "<=", "LIKE", "IN"])
            filter_value = st.text_input("Filter Value")
            
            # Sorting
            sort_column = st.selectbox("Sort By", columns if selected_table else [])
            sort_order = st.selectbox("Sort Order", ["ASC", "DESC"])
            
            # Limit
            limit = st.number_input("Limit Results", min_value=1, max_value=1000, value=50)
            
        with col2:
            # Query preview
            st.subheader("Generated Query")
            if selected_table and selected_columns:
                query = self._build_query(selected_table, selected_columns, filter_column, 
                                        filter_operator, filter_value, sort_column, sort_order, limit, user_id, is_admin)
                st.code(query, language="sql")
                
                if st.button("Execute Query", type="primary"):
                    try:
                        result = self._execute_safe_query(query, user_id, is_admin)
                        if result:
                            st.success(f"Query executed successfully! {len(result)} rows returned.")
                            df = pd.DataFrame(result)
                            st.dataframe(df, use_container_width=True)
                            
                            # Download option
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Download as CSV",
                                data=csv,
                                file_name=f"{selected_table}_query_result.csv",
                                mime="text/csv"
                            )
                        else:
                            st.info("Query executed but returned no results.")
                    except Exception as e:
                        st.error(f"Query execution failed: {str(e)}")
    
    def _render_data_analytics(self, user_id: str, is_admin: bool):
        """Data analytics and visualization"""
        st.subheader("Data Analytics Dashboard")
        
        if is_admin:
            # System-wide analytics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_users = self.supabase.get_total_users()
                st.metric("Total Users", total_users)
                
            with col2:
                active_users = self.supabase.get_active_users_count()
                st.metric("Active Users (30d)", active_users)
                
            with col3:
                total_sessions = self.supabase.get_total_chat_sessions()
                st.metric("Total Chat Sessions", total_sessions)
                
            with col4:
                total_messages = self.supabase.get_total_messages()
                st.metric("Total Messages", total_messages)
            
            # Charts
            st.subheader("System Analytics")
            
            # User registration over time
            user_data = self.supabase.get_user_registration_data()
            if user_data:
                df_users = pd.DataFrame(user_data)
                fig_users = px.line(df_users, x='date', y='count', title='User Registrations Over Time')
                st.plotly_chart(fig_users, use_container_width=True)
            
            # Activity heatmap
            activity_data = self.supabase.get_activity_heatmap_data()
            if activity_data:
                df_activity = pd.DataFrame(activity_data)
                fig_heatmap = px.density_heatmap(df_activity, x='hour', y='day', z='activity_count',
                                               title='User Activity Heatmap')
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
        else:
            # User-specific analytics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                user_sessions = self.supabase.get_user_chat_sessions_count(user_id)
                st.metric("My Chat Sessions", user_sessions)
                
            with col2:
                user_messages = self.supabase.get_user_messages_count(user_id)
                st.metric("My Messages", user_messages)
                
            with col3:
                api_usage = self.supabase.get_user_api_usage(user_id)
                st.metric("API Calls This Month", api_usage)
            
            # User activity chart
            st.subheader("My Activity")
            user_activity = self.supabase.get_user_activity_data(user_id)
            if user_activity:
                df_activity = pd.DataFrame(user_activity)
                fig_activity = px.bar(df_activity, x='date', y='activity_count', 
                                    title='My Daily Activity')
                st.plotly_chart(fig_activity, use_container_width=True)
    
    def _render_backup_export(self, user_id: str, is_admin: bool):
        """Backup and export functionality"""
        st.subheader("Data Export & Backup")
        
        if is_admin:
            st.warning("⚠️ Admin Export - Handle with care!")
            
            export_options = st.multiselect(
                "Select tables to export",
                ["users", "user_profiles", "api_keys", "chat_sessions", "messages", "user_activity"],
                default=["users", "user_profiles"]
            )
            
            export_format = st.selectbox("Export Format", ["CSV", "JSON", "SQL"])
            include_sensitive = st.checkbox("Include sensitive data (encrypted)")
            
            if st.button("Generate System Backup", type="primary"):
                try:
                    backup_data = self.supabase.create_system_backup(export_options, include_sensitive)
                    
                    if export_format == "JSON":
                        backup_json = json.dumps(backup_data, indent=2, default=str)
                        st.download_button(
                            label="Download System Backup (JSON)",
                            data=backup_json,
                            file_name=f"system_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    elif export_format == "CSV":
                        # Create ZIP with multiple CSV files
                        st.info("CSV export will create multiple files - one per table")
                        
                except Exception as e:
                    st.error(f"Backup failed: {str(e)}")
        else:
            # User data export
            st.info("Export your personal data")
            
            export_options = st.multiselect(
                "Select data to export",
                ["Chat Sessions", "Messages", "Activity Log", "Profile Data"],
                default=["Chat Sessions", "Messages"]
            )
            
            export_format = st.selectbox("Export Format", ["JSON", "CSV"])
            
            if st.button("Export My Data", type="primary"):
                try:
                    user_data = self.supabase.export_user_data(user_id, export_options)
                    
                    if export_format == "JSON":
                        data_json = json.dumps(user_data, indent=2, default=str)
                        st.download_button(
                            label="Download My Data (JSON)",
                            data=data_json,
                            file_name=f"my_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    else:
                        # Convert to CSV
                        if user_data.get('chat_sessions'):
                            df = pd.DataFrame(user_data['chat_sessions'])
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Download My Data (CSV)",
                                data=csv,
                                file_name=f"my_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                            
                    st.success("Data exported successfully!")
                    
                except Exception as e:
                    st.error(f"Export failed: {str(e)}")
    
    def _render_system_monitoring(self):
        """System monitoring for admins"""
        st.subheader("System Monitoring")
        
        # Real-time metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            db_size = self.supabase.get_database_size()
            st.metric("Database Size", f"{db_size:.2f} MB")
            
        with col2:
            active_connections = self.supabase.get_active_connections()
            st.metric("Active Connections", active_connections)
            
        with col3:
            query_performance = self.supabase.get_avg_query_time()
            st.metric("Avg Query Time", f"{query_performance:.2f}ms")
        
        # Performance charts
        st.subheader("Performance Metrics")
        
        # Query performance over time
        perf_data = self.supabase.get_performance_data()
        if perf_data:
            df_perf = pd.DataFrame(perf_data)
            fig_perf = px.line(df_perf, x='timestamp', y='query_time', 
                             title='Query Performance Over Time')
            st.plotly_chart(fig_perf, use_container_width=True)
        
        # Error monitoring
        st.subheader("Error Monitoring")
        error_data = self.supabase.get_error_logs()
        if error_data:
            df_errors = pd.DataFrame(error_data)
            st.dataframe(df_errors, use_container_width=True)
        else:
            st.success("No recent errors detected!")
    
    def _render_advanced_sql(self):
        """Advanced SQL interface for admins"""
        st.subheader("Advanced SQL Console")
        st.warning("⚠️ Direct SQL access - Use with extreme caution!")
        
        # SQL editor
        sql_query = st.text_area(
            "SQL Query",
            height=200,
            placeholder="Enter your SQL query here...\n\nExample:\nSELECT * FROM users WHERE created_at > NOW() - INTERVAL '7 days';"
        )
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            query_type = st.selectbox("Query Type", ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER"])
            dry_run = st.checkbox("Dry Run (Explain Only)", value=True)
            
        with col2:
            if st.button("Execute SQL", type="primary"):
                if not sql_query.strip():
                    st.error("Please enter a SQL query")
                    return
                    
                try:
                    if dry_run:
                        # Explain query
                        explain_result = self.supabase.explain_query(sql_query)
                        st.subheader("Query Execution Plan")
                        st.json(explain_result)
                    else:
                        # Execute query
                        result = self.supabase.execute_raw_sql(sql_query)
                        st.success("Query executed successfully!")
                        
                        if result and isinstance(result, list):
                            df = pd.DataFrame(result)
                            st.dataframe(df, use_container_width=True)
                            
                            # Download option
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Download Results",
                                data=csv,
                                file_name=f"sql_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        
                except Exception as e:
                    st.error(f"SQL execution failed: {str(e)}")
        
        # Query history
        st.subheader("Query History")
        query_history = self.supabase.get_query_history()
        if query_history:
            df_history = pd.DataFrame(query_history)
            st.dataframe(df_history, use_container_width=True)
    
    def _get_table_columns(self, table_name: str) -> List[str]:
        """Get columns for a specific table"""
        column_mapping = {
            "users": ["id", "email", "created_at", "last_sign_in_at", "is_admin"],
            "user_profiles": ["user_id", "full_name", "subscription_tier", "preferences"],
            "api_keys": ["id", "user_id", "provider", "key_name", "created_at", "last_used"],
            "chat_sessions": ["id", "user_id", "title", "created_at", "updated_at"],
            "messages": ["id", "session_id", "role", "content", "created_at"],
            "user_activity": ["id", "user_id", "activity_type", "details", "created_at"],
            "system_settings": ["key", "value", "updated_at", "updated_by"],
            "notifications": ["id", "user_id", "title", "message", "read", "created_at"]
        }
        return column_mapping.get(table_name, [])
    
    def _build_query(self, table: str, columns: List[str], filter_col: str, 
                     filter_op: str, filter_val: str, sort_col: str, sort_order: str, 
                     limit: int, user_id: str, is_admin: bool) -> str:
        """Build SQL query from visual builder inputs"""
        query = f"SELECT {', '.join(columns)} FROM {table}"
        
        # Add user filtering for non-admin users
        conditions = []
        if not is_admin and table in ["chat_sessions", "messages", "user_activity"]:
            if table == "messages":
                conditions.append("session_id IN (SELECT id FROM chat_sessions WHERE user_id = %s)")
            else:
                conditions.append("user_id = %s")
        
        # Add custom filter
        if filter_col and filter_val:
            if filter_op == "LIKE":
                conditions.append(f"{filter_col} LIKE '%{filter_val}%'")
            elif filter_op == "IN":
                conditions.append(f"{filter_col} IN ({filter_val})")
            else:
                conditions.append(f"{filter_col} {filter_op} '{filter_val}'")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        if sort_col:
            query += f" ORDER BY {sort_col} {sort_order}"
        
        query += f" LIMIT {limit}"
        
        return query
    
    def _execute_safe_query(self, query: str, user_id: str, is_admin: bool) -> List[Dict]:
        """Execute query with safety checks"""
        # Basic safety checks
        query_upper = query.upper().strip()
        
        if not query_upper.startswith("SELECT"):
            raise Exception("Only SELECT queries are allowed in the query builder")
        
        dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise Exception(f"Dangerous keyword '{keyword}' not allowed in query builder")
        
        # Execute query
        return self.supabase.execute_safe_query(query, user_id, is_admin)

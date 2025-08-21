#!/usr/bin/env python3
"""
VC Conversational AI Agent - Streamlit Interface
===============================================
A conversational interface for the VC AI Agent that can understand natural language
and automate VC tasks through chat interactions.
"""

import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
import os
from pathlib import Path
import re

# Import the conversational agent (RAG disabled due to Keras/Transformers conflicts)
try:
    from vc_conversational_agent import VCConversationalAgent
    print("✅ VCConversationalAgent imported successfully")
except ImportError as e:
    print(f"⚠️ VCConversationalAgent not available: {e}")
    VCConversationalAgent = None

try:
    from config_manager import config_manager
    print("✅ config_manager imported successfully")
except ImportError as e:
    print(f"⚠️ config_manager not available: {e}")
    # Create a minimal config manager stub
    class ConfigManagerStub:
        def __init__(self):
            self.excel_path = None
            
        def get_excel_path(self):
            return self.excel_path or "data/CC_Growth_EIS_Fund_Data.xlsx"
            
        def set_excel_path(self, path):
            self.excel_path = path
            
        def validate_excel_file(self, path):
            return {"valid": True, "errors": []}
    
    config_manager = ConfigManagerStub()

# RAG integration disabled to prevent Keras/Transformers crashes
EnhancedVCAgent = None
StreamlitRAGIntegration = None

# Page configuration
st.set_page_config(
    page_title="Committed Capital Agentic Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)
if 'preauth_ok' not in st.session_state:
    st.session_state.preauth_ok = False

if not st.session_state.preauth_ok:
    st.title("🔐 Committed Capital Agentic Assistant")
    st.markdown("### Microsoft sign-in required to continue")
    
    from microsoft_graph_auth_manager import get_auth_manager
    from microsoft_graph_mail import MicrosoftGraphMailService
    
    col1, col2 = st.columns([1,2])
    with col1:
        if st.button("Sign in with Microsoft", type="primary"):
            try:
                manager = get_auth_manager()
                token = manager.get_access_token(force_refresh=False)
                if not token:
                    st.error("❌ Authentication failed. Please try again.")
                else:
                    svc = MicrosoftGraphMailService()
                    check = svc.verify_permissions()
                    if check.get('ok'):
                        # Persist user info for later display
                        try:
                            st.session_state.user_info = manager.get_user_info() or {}
                        except Exception:
                            st.session_state.user_info = {}
                        st.session_state.preauth_ok = True
                        st.success("✅ Permissions verified for investors@committedcapital.co.uk")
                        st.rerun()
                    else:
                        st.error("❌ You do not have the required permissions to use investors@committedcapital.co.uk")
                        st.caption(f"Status: {check.get('status')} | {check.get('error')}")
            except Exception as e:
                st.error(f"❌ Sign-in error: {e}")
    with col2:
        try:
            u = get_auth_manager().get_user_info() or {}
            if u:
                st.info(f"Signed in as: {u.get('displayName','Unknown')} ({u.get('mail') or u.get('userPrincipalName','no email')})")
        except Exception:
            pass
    st.stop()

# Password protection (runs only after preauth_ok)
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("### Please enter the password to access the application")
    password = st.text_input("Password", type="password", key="password_input")
    if st.button("Login", type="primary"):
        if password == "136c17c6":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect password. Please try again.")
            st.stop()
    if password == "":
        st.info("💡 Enter the password to access the application")
    st.stop()

# Enhanced CSS for professional VC interface
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Navigation Bar */
    .nav-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.75rem 1.25rem;
        border-radius: 14px;
        margin: 0 0 1.25rem 0;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.18);
    }
    
    .nav-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
    }
    
    .nav-title {
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.1;
    }
    
    .nav-subtitle {
        font-size: 0.9rem;
        opacity: 0.85;
        margin: 0.1rem 0 0 0;
    }
    
    .nav-actions {
        display: flex;
        gap: 0.75rem;
        align-items: center;
    }
    
    .nav-breadcrumb {
        background: rgba(255,255,255,0.22);
        padding: 0.4rem 0.8rem;
        border-radius: 999px;
        font-size: 0.9rem;
        font-weight: 500;
        line-height: 1;
    }
    
    /* Header Styling */
    .main-header {
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 0.25rem 0 0.5rem 0;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 1.2rem;
        margin: 0 0 2rem 0;
        font-weight: 400;
    }
    
    /* Chat Message Styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 1rem 0;
        margin-left: 20%;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .agent-message {
        background: #f8fafc;
        color: #1f2937;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 1rem 0;
        margin-right: 20%;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .agent-message h4 {
        margin-top: 0;
        color: #374151;
        font-weight: 600;
    }
    
    .action-taken {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2);
    }
    
    .action-taken h5 {
        color: #065f46;
        margin: 0 0 0.5rem 0;
        font-weight: 600;
    }
    
    /* Input Area Styling */
    .chat-input {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 1rem;
        border-top: 1px solid #e5e7eb;
        box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
        z-index: 1000;
    }
    
    /* Agent Status */
    .agent-status {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border: 2px solid #3b82f6;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .agent-status h4 {
        color: #1e40af;
        margin-top: 0;
    }
    
    /* Metrics */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    /* Quick Actions */
    .quick-action {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #0ea5e9;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        font-weight: 500;
    }
    
    .quick-action:hover {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

def render_navigation():
    """Render the main navigation bar"""
    current_interface = st.session_state.get('current_interface', 'main_selection')
    
    # Navigation breadcrumb mapping
    breadcrumbs = {
        'main_selection': 'Dashboard',
        'fee_generation': 'Fee Letter Generation',
        'chat': 'AI Chat Assistant', 
        'analytics': 'Analytics & Reports',
        'research': 'Company Research',
        'settings': 'System Settings',
        'docs': 'Documentation'
    }
    
    current_breadcrumb = breadcrumbs.get(current_interface, 'Dashboard')
    
    # Signed-in user info (for right side display)
    user_display = ""
    try:
        from microsoft_graph_auth_manager import get_auth_manager as _get_auth_manager
        uinfo = _get_auth_manager().get_user_info() or {}
        if uinfo:
            _name = uinfo.get('displayName') or uinfo.get('givenName') or 'Unknown'
            _mail = uinfo.get('mail') or uinfo.get('userPrincipalName') or ''
            user_display = f"Signed in: {_name}{' (' + _mail + ')' if _mail else ''}"
    except Exception:
        pass
    
    st.markdown(f"""
    <div class="nav-container">
        <div class="nav-content">
            <div>
                <div class="nav-title">Committed Capital Agentic Assistant</div>
                <div class="nav-subtitle">Investment Operations Platform</div>
            </div>
            <div class="nav-actions">
                <div class="nav-breadcrumb">{current_breadcrumb}</div>
                {('<div class="nav-breadcrumb" style="margin-left:16px;white-space:nowrap;">' + user_display + '</div>') if user_display else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add navigation buttons if not on main page
    if current_interface != 'main_selection':
        col1, col2, col3 = st.columns([2, 6, 2])
        
        with col1:
            if st.button("Back to Dashboard", key="nav_back", use_container_width=True):
                st.session_state.current_interface = 'main_selection'
                st.rerun()
        
        with col3:
            # Quick access menu
            with st.popover("Quick Access"):
                if st.button("Dashboard", use_container_width=True):
                    st.session_state.current_interface = 'main_selection'
                    st.rerun()
                if st.button("Fee Letters", use_container_width=True):
                    st.session_state.current_interface = 'fee_generation'
                    st.rerun()
                if st.button("AI Chat", use_container_width=True):
                    st.session_state.current_interface = 'chat'
                    st.rerun()
                if st.button("Analytics", use_container_width=True):
                    st.session_state.current_interface = 'analytics'
                    st.rerun()

def initialize_session_state():
    """Initialize session state for the conversational agent"""
    
    # Ensure we have an interface value early so we can conditionally init the chat agent
    if 'current_interface' not in st.session_state:
        st.session_state.current_interface = 'main_selection'

    if 'vc_agent' not in st.session_state:
        # Only initialize the chat agent when entering the chat interface to avoid crashes/reruns
        if st.session_state.current_interface == 'chat':
            with st.spinner("🤖 Initializing your VC AI Assistant..."):
                # Initialize enhanced agent with RAG capabilities (if available)
                if EnhancedVCAgent:
                    enable_rag = st.session_state.get('enable_rag', False)
                    st.session_state.vc_agent = EnhancedVCAgent(
                        enable_rag=enable_rag, 
                        fast_mode=not enable_rag
                    )
                else:
                    # Fallback to basic conversational agent when RAG is disabled
                    st.session_state.vc_agent = VCConversationalAgent(fast_mode=True)
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'user_context' not in st.session_state:
        st.session_state.user_context = {
            'firm_name': 'Committed Capital Agentic Assistant',
            'user_role': 'Partner',
            'preferences': {
                'analysis_depth': 'comprehensive',
                'sectors_of_interest': ['fintech', 'healthtech', 'cleantech']
            }
        }
    
    # New UI state management (already set above)
    
    # Fee generation form inputs now use direct key-based session state
    # No need for nested fee_generation_data structure

def render_chat_message(message: Dict[str, Any], is_user: bool = False):
    """Render a chat message with appropriate styling and RAG information"""
    
    if is_user:
        st.markdown(f"""
        <div class="user-message">
            <strong>You:</strong> {message['content']}
        </div>
        """, unsafe_allow_html=True)
    else:
        response_content = message.get('response', message.get('message', ''))
        
        # Determine method icon and description
        method = message.get('method', 'unknown')
        method_icon = "🔍" if method == 'rag' else "🤖" if method == 'base_agent' else "⚙️"
        method_desc = {
            'rag': 'RAG (Document Retrieval)',
            'base_agent': 'Conversational AI',
            'error': 'Error Response'
        }.get(method, 'AI Response')
        
        # Check if this was an actionable response
        if message.get('action_taken'):
            st.markdown(f"""
            <div class="agent-message">
                <h4>{method_icon} VC Assistant</h4>
                <div class="action-taken">
                    <h5>✅ Action Completed: {message.get('task_type', '').replace('_', ' ').title()}</h5>
                    {response_content}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show next steps if available
            if message.get('next_steps'):
                with st.expander("📋 Suggested Next Steps"):
                    for i, step in enumerate(message['next_steps'], 1):
                        st.write(f"{i}. {step}")
        else:
            st.markdown(f"""
            <div class="agent-message">
                <h4>{method_icon} VC Assistant</h4>
                <small style="color: #666;">Response via {method_desc}</small>
                <div style="margin-top: 10px;">
                    {response_content}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display RAG source information if available
            if method == 'rag' and message.get('retrieved_docs', 0) > 0:
                with st.expander(f"📚 Sources ({message['retrieved_docs']} documents retrieved)"):
                    sources = message.get('sources', [])
                    if sources:
                        for i, source in enumerate(sources, 1):
                            st.write(f"**Source {i}:** {source.get('source_file', 'Unknown file')}")
                            st.write(f"**Type:** {source.get('document_type', 'General')}")
                            if 'start_index' in source:
                                st.write(f"**Location:** Character {source['start_index']}")
                            st.markdown("---")
                    else:
                        st.write("Source metadata not available")
            elif method == 'rag':
                st.caption("🔍 RAG search performed but no relevant documents found")

def render_quick_actions():
    """Render quick action buttons for common tasks"""
    
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Create Fee Letter", use_container_width=True):
            return "I need to create a fee letter"
    
    with col2:
        if st.button("📊 Analyze Company", use_container_width=True):
            return "I want to analyze an investment opportunity"
    
    with col3:
        if st.button("📋 EIS Assessment", use_container_width=True):
            return "Can you help me assess EIS qualification?"
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("📈 Market Research", use_container_width=True):
            return "I need market intelligence for a sector"
    
    with col5:
        if st.button("🏢 Portfolio Review", use_container_width=True):
            return "Help me with portfolio management tasks"
    
    with col6:
        if st.button("❓ Ask Question", use_container_width=True):
            return "I have a question about VC regulations"
    
    return None

def render_agent_status():
    """Render current agent status and capabilities"""
    
    # Handle both EnhancedVCAgent and VCConversationalAgent
    if hasattr(st.session_state.vc_agent, 'get_system_status'):
        status = st.session_state.vc_agent.get_system_status()
    elif hasattr(st.session_state.vc_agent, 'get_agent_status'):
        status = st.session_state.vc_agent.get_agent_status()
    else:
        status = {"status": "unknown", "model": "unknown"}
    
    # Display status based on agent type
    if 'base_agent' in status:
        # EnhancedVCAgent status
        st.markdown(f"""
        <div class="agent-status">
            <h4>🤖 Enhanced Agent Status</h4>
            <p><strong>Base Agent:</strong> {status.get('base_agent', 'unknown')}</p>
            <p><strong>Fast Mode:</strong> {'✅' if status.get('fast_mode') else '❌'}</p>
            <p><strong>RAG Enabled:</strong> {'✅' if status.get('rag_enabled') else '❌'}</p>
            <p><strong>RAG System:</strong> {status.get('rag_system', 'not available')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show vector store stats if available
        if 'vector_store_stats' in status:
            stats = status['vector_store_stats']
            with st.expander("📚 Vector Store Details"):
                st.write(f"**Documents:** {stats.get('total_documents', 0)}")
                st.write(f"**Model:** {stats.get('model', 'unknown')}")
                st.write(f"**Path:** {stats.get('vector_store_path', 'unknown')}")
    else:
        # Original VCConversationalAgent status
        st.markdown(f"""
        <div class="agent-status">
            <h4>🤖 Agent Status</h4>
            <p><strong>Model:</strong> {status.get('model', 'unknown')}</p>
            <p><strong>Conversations:</strong> {status.get('conversations_count', 0)}</p>
            <p><strong>Session:</strong> {status.get('session_id', 'unknown')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show capabilities if available
        if 'capabilities' in status:
            with st.expander("🎯 Agent Capabilities"):
                for capability in status['capabilities']:
                    st.write(f"✅ {capability}")

def render_conversation_analytics():
    """Render conversation analytics and insights"""
    
    if not st.session_state.conversation_history:
        st.info("Start a conversation to see analytics")
        return
    
    # Basic analytics
    total_conversations = len(st.session_state.conversation_history)
    actions_taken = sum(1 for msg in st.session_state.conversation_history if msg.get('action_taken'))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Messages", total_conversations)
    
    with col2:
        st.metric("Actions Completed", actions_taken)
    
    # Task type breakdown
    if actions_taken > 0:
        task_types = [msg.get('task_type', 'unknown') for msg in st.session_state.conversation_history if msg.get('action_taken')]
        task_df = pd.DataFrame(task_types, columns=['Task Type'])
        
        if not task_df.empty:
            task_counts = task_df['Task Type'].value_counts()
            st.bar_chart(task_counts)

async def process_user_input(user_input: str):
    """Process user input through the enhanced conversational agent"""
    
    with st.spinner("🤖 Processing your request..."):
        try:
            # Get response from enhanced agent
            if hasattr(st.session_state.vc_agent, 'enhanced_chat'):
                response = await st.session_state.vc_agent.enhanced_chat(user_input)
            else:
                # Fall back to basic chat if enhanced not available
                response = await st.session_state.vc_agent.chat(
                    user_input=user_input,
                    user_context=st.session_state.user_context
                )
            
            # Add to conversation history
            st.session_state.conversation_history.append({
                'timestamp': datetime.now(),
                'user_input': user_input,
                'content': user_input,
                'is_user': True
            })
            
            # Ensure timestamp is datetime object and add enhanced metadata
            response_with_timestamp = response.copy()
            response_with_timestamp['timestamp'] = datetime.now()
            response_with_timestamp['is_user'] = False
            
            # Add RAG-specific metadata if available
            if 'method' in response:
                response_with_timestamp['method'] = response['method']
            if 'sources' in response:
                response_with_timestamp['sources'] = response['sources']
            if 'retrieved_docs' in response:
                response_with_timestamp['retrieved_docs'] = response['retrieved_docs']
            
            st.session_state.conversation_history.append(response_with_timestamp)
            
            return response
            
        except Exception as e:
            st.error(f"Error processing request: {str(e)}")
            return None

def main():
    """Main Streamlit application for the VC conversational agent"""
    
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">VC AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Your intelligent partner for UK venture capital operations</div>', unsafe_allow_html=True)
    # Signed-in indicator now shown in navigation; remove duplicate here for cleaner layout
    
    # Sidebar
    with st.sidebar:
        st.header("🤖 Agent Dashboard")
        
        # Performance and RAG mode indicator
        agent = st.session_state.vc_agent
        
        if hasattr(agent, 'enable_rag') and not agent.enable_rag:
            st.info("⚡ **Fast Mode Active**\nBasic features enabled. RAG document retrieval disabled for faster performance.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Enable RAG", help="Enable document retrieval and advanced knowledge"):
                    st.session_state.enable_rag = True
                    if 'vc_agent' in st.session_state:
                        del st.session_state.vc_agent
                    st.rerun()
            
            with col2:
                if st.button("🚀 Enable All Features", help="Enable all advanced features"):
                    st.session_state.enable_rag = True
                    if 'vc_agent' in st.session_state:
                        del st.session_state.vc_agent
                    with st.spinner("🔄 Initializing full feature set..."):
                        st.session_state.vc_agent = EnhancedVCAgent(enable_rag=True, fast_mode=False)
                    st.success("✅ All advanced features enabled!")
                    st.rerun()
        
        elif hasattr(agent, 'enable_rag') and agent.enable_rag:
            st.success("🔍 **RAG Mode Active**\nDocument retrieval and advanced knowledge features enabled.")
            if st.button("⚡ Switch to Fast Mode", help="Disable RAG for faster performance"):
                st.session_state.enable_rag = False
                if 'vc_agent' in st.session_state:
                    del st.session_state.vc_agent
                st.rerun()
        
        # Agent status
        render_agent_status()
        
        st.markdown("---")
        
        # Show current Excel path and warn if it's a temporary upload copy
        try:
            current_excel_path = config_manager.get_excel_path()
            if current_excel_path:
                st.caption(f"Using Excel file: `{current_excel_path}`")
                try:
                    import os, datetime
                    mtime = os.path.getmtime(current_excel_path)
                    st.caption(f"Last modified: {datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}")
                    col_open1, col_open2 = st.columns(2)
                    with col_open1:
                        if st.button("Reveal in Finder"):
                            os.system(f"open -R '{current_excel_path}'")
                    with col_open2:
                        if st.button("Open in Excel"):
                            os.system(f"open '{current_excel_path}'")
                except Exception:
                    pass
                if ".streamlit_temp" in current_excel_path:
                    st.warning("You're using a temporary uploaded copy. Refresh will re-read this temp file only. To reflect live edits to your original workbook, go to Settings and set the Excel path to the original file.")
        except Exception:
            pass

        # Quick-change / Maintain single-source-of-truth file (no temp switching by default)
        with st.expander("📂 Maintain Excel File", expanded=False):
            st.caption("Recommended: keep one shared Excel file. Uploading will replace that file in-place (path unchanged).")
            uploaded = render_file_uploader("quick_change")
            if uploaded and current_excel_path:
                col_rep, col_switch = st.columns(2)
                with col_rep:
                    if st.button("⬆️ Replace current file in-place", key="replace_current_file"):
                        try:
                            import shutil
                            shutil.copyfile(uploaded, current_excel_path)
                            fee_agent.refresh_excel_cache()
                            st.success("Replaced configured Excel file in-place. Cache cleared.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to replace file: {e}")
                with col_switch:
                    if st.button("🔁 Switch to uploaded copy (not recommended)", key="switch_to_uploaded"):
                        if config_manager.set_excel_path(uploaded):
                            fee_agent.refresh_excel_cache()
                            st.success("Excel path updated to uploaded file. Cache cleared.")
                            st.rerun()
                        else:
                            st.error("Failed to update Excel path")

            st.markdown("**Or enter path manually:**")
            manual_new = st.text_input("New Excel File Path", value=current_excel_path or "", key="quick_change_path")
            if st.button("💾 Use This Path", key="quick_change_save"):
                if manual_new:
                    if config_manager.set_excel_path(manual_new):
                        fee_agent.refresh_excel_cache()
                        st.success("Excel path updated. Cache cleared.")
                        st.rerun()
                    else:
                        st.error("Failed to update Excel path")
        
        # Conversation analytics
        st.header("📊 Analytics")
        render_conversation_analytics()
        
        st.markdown("---")
        
        # Settings
        st.header("⚙️ Settings")
        
        # User context settings
        firm_name = st.text_input("Firm Name", value=st.session_state.user_context['firm_name'])
        user_role = st.selectbox("Your Role", ["Partner", "Principal", "Associate", "Analyst"])
        
        if st.button("Update Profile"):
            st.session_state.user_context.update({
                'firm_name': firm_name,
                'user_role': user_role
            })
            st.success("Profile updated!")
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation"):
            st.session_state.conversation_history = []
            # Clear agent memory if method exists
            if hasattr(st.session_state.vc_agent, 'clear_conversation_history'):
                st.session_state.vc_agent.clear_conversation_history()
            elif hasattr(st.session_state.vc_agent, 'base_agent') and hasattr(st.session_state.vc_agent.base_agent, 'clear_conversation_history'):
                st.session_state.vc_agent.base_agent.clear_conversation_history()
            st.success("Conversation cleared!")
            st.rerun()
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("💬 Chat with Your VC Assistant")
        
        # Chat history container
        chat_container = st.container()
        
        with chat_container:
            # Display conversation history
            for message in st.session_state.conversation_history:
                render_chat_message(message, message.get('is_user', False))
        
        # Input area
        st.markdown("---")
        
        # Quick actions
        quick_action = render_quick_actions()
        if quick_action:
            # Process quick action
            response = asyncio.run(process_user_input(quick_action))
            if response:
                st.rerun()
        
        st.markdown("---")
        
        # Enhanced text input with Enter key support
        st.markdown("""
        <style>
        .stTextArea > div > div > textarea {
            font-family: 'Inter', sans-serif;
        }
        .input-help {
            font-size: 0.8rem;
            color: #666;
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="input-help">💡 Tip: Press Ctrl+Enter to send your message</div>', unsafe_allow_html=True)
        
        # Create a form to handle Enter key submission
        with st.form(key="message_form", clear_on_submit=True):
            user_input = st.text_area(
                "Type your message:",
                placeholder="e.g., 'Create a fee letter for John Smith investing £50,000 into TechCorp Ltd'",
                height=100,
                key="user_input_form"
            )
            
            # Always-clickable send button (form submit handles the logic)
            col_send, col_clear = st.columns([3, 1])
            
            with col_send:
                send_clicked = st.form_submit_button(
                    "💬 Send Message", 
                    type="primary", 
                    use_container_width=True
                )
            
            with col_clear:
                if st.form_submit_button("🗑️ Clear Input", use_container_width=True):
                    st.rerun()
        
        # Process message if sent (either via button or Enter)
        if send_clicked and user_input and user_input.strip():
            with st.spinner("🤖 Processing your message..."):
                response = asyncio.run(process_user_input(user_input))
                if response:
                    st.rerun()
        elif send_clicked and (not user_input or not user_input.strip()):
            st.warning("⚠️ Please enter a message before sending.")
    
    with col2:
        st.header("📋 Recent Activity")
        
        # Add Fee Letter Dashboard link
        if st.button("🔍 Fee Letter Dashboard", use_container_width=True):
            st.session_state.show_dashboard = True
            st.rerun()
        
        # Show recent actions taken
        recent_actions = [
            msg for msg in st.session_state.conversation_history[-5:]
            if msg.get('action_taken')
        ]
        
        if recent_actions:
            for action in recent_actions:
                with st.expander(f"✅ {action.get('task_type', 'Action').replace('_', ' ').title()}"):
                    try:
                        from datetime import datetime
                        timestamp = action.get('timestamp')
                        if timestamp:
                            if isinstance(timestamp, str):
                                # Handle various timestamp formats
                                if 'T' in timestamp:
                                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                else:
                                    timestamp = datetime.now()
                            elif hasattr(timestamp, 'strftime'):
                                # Already a datetime object
                                pass
                            else:
                                timestamp = datetime.now()
                            st.write(f"**Time:** {timestamp.strftime('%H:%M:%S')}")
                        else:
                            st.write("**Time:** Just now")
                    except Exception:
                        st.write("**Time:** Just now")
                    st.write(f"**Success:** {'✅' if action.get('success') else '❌'}")
                    if action.get('task_result'):
                        st.json(action['task_result'])
        else:
            st.info("No recent actions. Start by asking me to help with a task!")
        
        st.markdown("---")
        
        # Help section
        st.header("❓ Need Help?")
        
        with st.expander("💡 Example Requests"):
            st.write("**Fee Letter Generation:**")
            st.code("Create a fee letter for Sarah Jones investing £25,000 into GreenTech Ltd")
            
            st.write("**Investment Analysis:**")
            st.code("Analyze TechStart AI Ltd as an investment opportunity")
            
            st.write("**EIS Assessment:**")
            st.code("Can you assess if FinanceFlow Ltd qualifies for EIS?")
            
            st.write("**Market Research:**")
            st.code("I need market intelligence for the UK fintech sector")
        
        with st.expander("🎯 Available Tasks"):
            tasks = [
                "Fee letter generation",
                "Investment opportunity analysis",
                "EIS qualification assessment",
                "KIC status evaluation",
                "Market research and intelligence",
                "Portfolio management tasks",
                "Regulatory compliance guidance",
                "General VC questions and advice"
            ]
            
            for task in tasks:
                st.write(f"• {task}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8rem;'>"
        "VC AI Assistant | Specialized for UK Venture Capital Operations"
        "</div>", 
        unsafe_allow_html=True
    )

def render_fee_letter_dashboard():
    """Render the comprehensive fee letter dashboard"""
    st.title("🔍 Fee Letter Dashboard")
    
    # Back button
    if st.button("← Back to Chat"):
        st.session_state.show_dashboard = False
        st.rerun()
    
    st.markdown("---")
    
    # Import enhanced utilities
    try:
        # Import utilities with error handling
        try:
            from vc_enhanced_utils import ActivityLogger, PolicyGate, FeeCalculator, FuzzyMatcher
            activity_logger = ActivityLogger()
        except ImportError as e:
            st.error(f"❌ Enhanced utilities not available: {e}")
            return
            
        try:
            from agents.fee_letter_agent import FeeLetterAgent
            fee_agent = FeeLetterAgent()
        except ImportError as e:
            st.error(f"❌ Fee Letter Agent not available: {e}")
            st.info("💡 This usually means some dependencies are missing. Please check the installation.")
            return
        
        # Dashboard tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Generate Fee Letter", "📊 Activity Log", "🔍 Preview & Validate", "📈 Analytics"])
        
        with tab1:
            st.header("📝 Generate Fee Letter")
            
            # Excel Data Management
            col_refresh, col_debug = st.columns(2)
            with col_refresh:
                if st.button("🔄 Refresh Excel Data", help="Clear cache and reload Excel data"):
                    try:
                        fee_agent.refresh_excel_cache()
                        st.success("✅ Excel data cache refreshed!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error refreshing cache: {str(e)}")
            
            with col_debug:
                if st.button("🔍 Debug Company Search", help="Show available companies in Excel"):
                    try:
                        debug_info = fee_agent.debug_company_search()
                        st.info(f"📊 Found {debug_info['total_companies']} companies in Excel")
                        
                        # Show Dingus/Pingus status
                        if debug_info.get('contains_dingus'):
                            st.success("✅ 'Dingus Ltd' found in Excel")
                        else:
                            st.warning("⚠️ 'Dingus Ltd' NOT found in Excel")
                        
                        if debug_info.get('contains_pingus'):
                            st.info("ℹ️ 'Pingus Ltd' found in Excel")
                        
                        with st.expander("📋 All Available Companies"):
                            for company in debug_info['company_names']:  # Show ALL companies
                                if "dingus" in company.lower():
                                    st.write(f"🎯 **{company}** (Target - Dingus)")
                                elif "pingus" in company.lower():
                                    st.write(f"🔍 **{company}** (Contains 'Pingus')")
                                else:
                                    st.write(f"• {company}")
                        
                        st.caption(f"Excel file: {debug_info.get('excel_file', 'Unknown')}")
                    except Exception as e:
                        st.error(f"❌ Error debugging companies: {str(e)}")
            
            st.markdown("---")
            
            # Initialize form widget keys in session state if not present
            if 'input_investor_name' not in st.session_state:
                st.session_state.input_investor_name = ""
            if 'input_company_name' not in st.session_state:
                st.session_state.input_company_name = ""
            if 'input_investment_amount' not in st.session_state:
                st.session_state.input_investment_amount = 50000
            if 'input_investment_type' not in st.session_state:
                st.session_state.input_investment_type = "Gross"
            if 'input_preview_only' not in st.session_state:
                st.session_state.input_preview_only = True

            with st.form("fee_letter_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    investor_name = st.text_input(
                        "Investor Name", 
                        placeholder="e.g., Jacob Pedersen",
                        key="input_investor_name"
                    )
                    investment_amount = st.number_input(
                        "Investment Amount (£)", 
                        min_value=1000, 
                        max_value=1000000, 
                        key="input_investment_amount"
                    )
                    investment_type = st.selectbox(
                        "Investment Type", 
                        ["Gross", "Net"],
                        key="input_investment_type"
                    )
                
                with col2:
                    company_name = st.text_input(
                        "Company Name", 
                        placeholder="e.g., Harper Concierge",
                        key="input_company_name"
                    )
                    preview_only = st.checkbox(
                        "Preview Only (Don't Send)", 
                        key="input_preview_only"
                    )
                
                col_submit, col_clear = st.columns([3, 1])
                with col_submit:
                    generate_clicked = st.form_submit_button("🚀 Generate Fee Letter", type="primary", use_container_width=True)
                with col_clear:
                    clear_clicked = st.form_submit_button("🗑️ Clear", use_container_width=True)
            
            # Handle clear button
            if clear_clicked:
                # Reset all widget values directly
                st.session_state.input_investor_name = ""
                st.session_state.input_company_name = ""
                st.session_state.input_investment_amount = 50000
                st.session_state.input_investment_type = "Gross"
                st.session_state.input_preview_only = True
                # Clear any previous preview
                if 'last_fee_preview' in st.session_state:
                    del st.session_state['last_fee_preview']
                st.rerun()
            
            if generate_clicked and investor_name and company_name:
                # Update session state with current form values to persist them
                st.session_state.input_investor_name = investor_name
                st.session_state.input_company_name = company_name
                st.session_state.input_investment_amount = investment_amount
                st.session_state.input_investment_type = investment_type
                st.session_state.input_preview_only = preview_only
                
                prompt = f"create a fee letter for {investor_name} for {investment_amount} {investment_type.lower()} into {company_name}"
                
                with st.spinner("🔄 Generating fee letter..."):
                    # Use enhanced generation
                    result = fee_agent.execute_enhanced(prompt)
                    
                    if result["success"]:
                        st.success(result["message"])
                        
                        # Check if default rates were used (indicated by warning message)
                        if "Using default rates" in result.get("message", ""):
                            st.warning("⚠️ No fee data found in Excel for this investor. Using default rates (1.5% setup, 2.0% AMC, 20% carry). Please update the FeeSheet if different rates should be applied.")
                        
                        # Show preview
                        preview_data = result["preview_data"]
                        
                        st.subheader("📄 Fee Letter Preview")
                        
                        preview_col1, preview_col2 = st.columns(2)
                        
                        with preview_col1:
                            st.markdown(f"""
                            **Investor:** {preview_data['investor_name']}  
                            **Company:** {preview_data['company_name']}  
                            **Investment Type:** {preview_data['investment_type']}  
                            **Gross Investment:** £{preview_data['gross_investment']:,.2f}  
                            **Total Fees:** £{preview_data['total_fees']:,.2f}  
                            **Total Transfer:** £{preview_data['total_transfer']:,.2f}  
                            **Share Quantity:** {preview_data['share_quantity']:,.2f}  
                            """)
                        
                        with preview_col2:
                            st.markdown(f"""
                            **Calculation Note:**  
                            {preview_data['calculation_note']}
                            """)
                            
                            # Validation warnings suppressed per user preference
                        
                        # Show fee breakdown if available
                        if "fee_calculation" in result and result["fee_calculation"]:
                            fee_calc = result["fee_calculation"]
                            
                            st.subheader("💰 Fee Breakdown")
                            breakdown_col1, breakdown_col2 = st.columns(2)
                            
                            with breakdown_col1:
                                st.metric("Management Fee", f"£{fee_calc.management_fee:,.2f}")
                                st.metric("Admin Fee", f"£{fee_calc.admin_fee:,.2f}")
                            
                            with breakdown_col2:
                                st.metric("Fee Rate", f"{fee_calc.fee_rate:.2%}")
                                st.metric("Calculation Method", fee_calc.calculation_method.upper())
                    
                    else:
                        st.error(result["message"])
                        if "missing_fields" in result:
                            st.write("**Missing Required Fields:**")
                            for field in result["missing_fields"]:
                                st.write(f"• {field}")
        
        with tab2:
            st.header("📊 Activity Log")
            
            # Activity stats
            stats = activity_logger.get_activity_stats()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Activities", stats.get("total_activities", 0))
            with col2:
                st.metric("Activity Types", len(stats.get("activity_types", {})))
            with col3:
                if stats.get("recent_activity"):
                    st.metric("Last Activity", stats["recent_activity"][:10])
            
            # Recent activities
            st.subheader("🕒 Recent Activities")
            recent_activities = activity_logger.get_recent_activities(limit=20)
            
            for activity in recent_activities:
                with st.expander(f"{activity['type']} - {activity['timestamp'][:19]}"):
                    st.json(activity['details'])
        
        with tab3:
            st.header("🔍 Preview & Validate")
            
            st.info("💡 Use this tab to validate fee letter requests before generation")
            
            with st.form("validation_form"):
                val_investor = st.text_input("Investor Name (for validation)")
                val_company = st.text_input("Company Name (for validation)")
                val_amount = st.number_input("Investment Amount", min_value=0.0)
                
                validate_clicked = st.form_submit_button("🔍 Validate Request")
            
            if validate_clicked and val_investor and val_company:
                # Mock validation (would need actual data)
                investor_data = {"name": val_investor, "email": "test@example.com", "address": "Test Address"}
                company_data = {"name": val_company, "share_price": 1.0, "company_number": "12345"}
                investment_data = {"amount": val_amount, "investment_type": "gross"}
                
                validation_result = PolicyGate.validate_fee_letter_request(
                    investor_data, company_data, investment_data
                )
                
                if validation_result.is_valid:
                    st.success(f"✅ {validation_result.message}")
                else:
                    st.error(f"❌ {validation_result.message}")
                    for field in validation_result.missing_fields:
                        st.write(f"• Missing: {field}")
                
                # Suppress non-critical warnings in the UI
        
        with tab4:
            st.header("📈 Analytics")
            
            # Activity type breakdown
            if stats.get("activity_types"):
                st.subheader("📊 Activity Types")
                
                activity_types = stats["activity_types"]
                type_names = list(activity_types.keys())
                type_counts = list(activity_types.values())
                
                # Create a simple bar chart
                import pandas as pd
                df = pd.DataFrame({
                    "Activity Type": type_names,
                    "Count": type_counts
                })
                
                st.bar_chart(df.set_index("Activity Type"))
            
            # Fee calculation examples
            st.subheader("💰 Fee Calculation Examples")
            
            example_amounts = [10000, 25000, 50000, 100000]
            example_data = []
            
            for amount in example_amounts:
                gross_calc = FeeCalculator.calculate_fees(amount, is_net_investment=False)
                net_calc = FeeCalculator.calculate_fees(amount, is_net_investment=True)
                
                example_data.append({
                    "Amount": f"£{amount:,}",
                    "Gross Investment": f"£{gross_calc.net_investment:,.2f}",
                    "Gross Total Fees": f"£{gross_calc.total_fees:,.2f}",
                    "Net Investment": f"£{net_calc.net_investment:,.2f}",
                    "Net Total Fees": f"£{net_calc.total_fees:,.2f}"
                })
            
            st.table(example_data)
    
    except ImportError as e:
        st.error(f"❌ Enhanced utilities not available: {e}")
        st.info("💡 Make sure vc_enhanced_utils.py is in the project directory")

def render_minimal_fallback():
    """Render a minimal fallback interface when dependencies are missing"""
    st.error("🚫 **Application Dependencies Missing**")
    st.markdown("""
    ### ❌ Some required components are not available
    
    This usually happens when:
    - The application is running in a restricted environment
    - Some Python packages failed to install
    - There are import conflicts
    
    ### 🔧 Troubleshooting Steps:
    1. **Check Installation**: Ensure all dependencies are installed
    2. **Restart Application**: Sometimes a restart resolves import issues  
    3. **Check Environment**: Verify Python environment is correct
    4. **Contact Support**: If issues persist, contact technical support
    
    ### 📋 Required Dependencies:
    - streamlit >= 1.28.0
    - pandas >= 2.0.0
    - openpyxl >= 3.1.0
    - rapidfuzz >= 3.5.0
    - jinja2 >= 3.1.0
    - msal >= 1.24.0
    - requests >= 2.31.0
    - python-dotenv >= 1.0.0
    """)
    
    if st.button("🧪 Run Diagnostic Test"):
        st.rerun()

def render_main_selection():
    """Render the professional VC dashboard interface"""
    
    # Welcome section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
        <h1 style="color: #2c3e50; font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;">
            Welcome to Your VC Operations Center
        </h1>
        <p style="color: #7f8c8d; font-size: 1.1rem; margin-bottom: 0;">
            Select the AI assistant you need for your current task
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Primary VC Operations - Featured Cards
    st.markdown("### 🎯 Primary Operations")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        with st.container():
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 2rem; border-radius: 15px; color: white; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 3rem; margin-right: 1rem;">📄</div>
                    <div>
                        <h3 style="margin: 0; font-size: 1.4rem;">Fee Letter Generation</h3>
                        <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Professional Documentation</p>
                    </div>
                </div>
                <p style="opacity: 0.8; margin-bottom: 1.5rem; line-height: 1.5;">
                    Generate professional fee letters with customizable AMC rates, upfront fees, 
                    and performance charges. Fully compliant with EIS regulations.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Generate Fee Letters", key="fee_gen_btn", use_container_width=True, type="primary"):
                st.session_state.current_interface = 'fee_generation'
                st.rerun()
    
    with col2:
        with st.container():
            st.markdown("""
            <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                        padding: 2rem; border-radius: 15px; color: white; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 3rem; margin-right: 1rem;">💬</div>
                    <div>
                        <h3 style="margin: 0; font-size: 1.4rem;">AI Investment Assistant</h3>
                        <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Intelligent Analysis</p>
                    </div>
                </div>
                <p style="opacity: 0.8; margin-bottom: 1.5rem; line-height: 1.5;">
                    Advanced AI assistant for investment analysis, market research, due diligence, 
                    and strategic VC operations support.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💬 Launch AI Assistant", key="chat_btn", use_container_width=True):
                st.session_state.current_interface = 'chat'
                st.rerun()
    
    st.markdown("---")
    
    # Secondary Operations
    st.markdown("### 📊 Analytics & Research")
    
    col3, col4, col5 = st.columns(3, gap="medium")
    
    with col3:
        if st.button("📊 Analytics Dashboard\n*Activity logs & reports*", key="analytics_btn", use_container_width=True, help="View comprehensive analytics and reports"):
            st.session_state.current_interface = 'analytics'
            st.rerun()
    
    with col4:
        if st.button("🔍 Company Research\n*Deep dive analysis*", key="research_btn", use_container_width=True, help="Conduct detailed company research and analysis"):
            st.session_state.current_interface = 'research'
            st.rerun()
    
    with col5:
        if st.button("⚙️ System Settings\n*Configuration & setup*", key="settings_btn", use_container_width=True, help="Configure system settings and preferences"):
            st.session_state.current_interface = 'settings'
            st.rerun()
    
    # Quick Statistics Overview
    st.markdown("### 📈 Today's Activity")
    
    try:
        from vc_enhanced_utils import ActivityLogger
        activity_logger = ActivityLogger()
        stats = activity_logger.get_activity_stats()
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric(
                "Total Operations", 
                stats.get("total_activities", 0),
                help="Total number of operations performed"
            )
        
        with col_stat2:
            st.metric(
                "Fee Letters", 
                stats.get("activity_types", {}).get("fee_letter_generated", 0),
                help="Fee letters generated today"
            )
        
        with col_stat3:
            st.metric(
                "Validations", 
                stats.get("activity_types", {}).get("validation_check", 0),
                help="Validation checks performed"
            )
        
        with col_stat4:
            last_activity = stats.get("recent_activity", "None")[:10] if stats.get("recent_activity") else "None"
            st.metric(
                "Last Activity", 
                last_activity,
                help="Most recent system activity"
            )
                
    except ImportError:
        st.info("💡 Activity tracking will be available once enhanced utilities are loaded")

def render_file_uploader(key_suffix=""):
    """Render file uploader for Excel files."""
    st.markdown("### 📂 Select Your Excel File")
    st.info("Click 'Browse files' below to select your Excel data file from anywhere on your computer.")
    
    uploaded_file = st.file_uploader(
        "Choose Excel File",
        type=['xlsx', 'xls'],
        help="Select your Excel file containing FeeSheet, InvestorSheet, and CompanySheet",
        key=f"file_uploader_{key_suffix}"
    )
    
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        temp_dir = Path.home() / ".streamlit_temp"
        temp_dir.mkdir(exist_ok=True)
        
        temp_file_path = temp_dir / uploaded_file.name
        
        # Write the uploaded file to temporary location
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"📄 File uploaded: **{uploaded_file.name}**")
        st.info(f"📍 Temporary location: `{temp_file_path}`")
        
        # Show file details
        file_size = len(uploaded_file.getbuffer()) / 1024  # Size in KB
        st.caption(f"File size: {file_size:.1f} KB")
        
        # Confirmation step
        st.markdown("---")
        st.markdown("### ✅ Confirm File Selection")
        st.write(f"**Selected file:** {uploaded_file.name}")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✅ Use This File", type="primary", key=f"confirm_{key_suffix}"):
                return str(temp_file_path)
        
        with col2:
            if st.button("🔄 Choose Different File", type="secondary", key=f"cancel_{key_suffix}"):
                # Clear the uploader by rerunning
                st.rerun()
        
        return None  # Don't return path until confirmed
    
    return None

def render_first_run_setup():
    """Render first-run Excel file selection screen."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1>🚀 Welcome to Committed Capital Agentic Assistant</h1>
        <p style="font-size: 1.2rem; color: #666; margin-bottom: 2rem;">
            To get started, please select your Excel data file containing investor and fee information.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📁 Select Excel Data File")
    st.info("**Required:** Your Excel file must contain three sheets: `FeeSheet`, `InvestorSheet`, and `CompanySheet` with the required columns.")
    
    # Initialize session state for selected file
    if 'selected_excel_path' not in st.session_state:
        st.session_state.selected_excel_path = ""
    
    # Display current selection
    if st.session_state.selected_excel_path:
        st.success(f"📄 Selected: `{os.path.basename(st.session_state.selected_excel_path)}`")
        st.caption(f"Full path: {st.session_state.selected_excel_path}")
    
    # File uploader section
    selected_file = render_file_uploader("first_run")
    if selected_file:
        st.session_state.selected_excel_path = selected_file
        st.rerun()
    
    # Manual path input (alternative)
    st.markdown("**✏️ Or enter path manually:**")
    manual_path = st.text_input(
        "Excel File Path",
        value=st.session_state.selected_excel_path,
        placeholder="/path/to/your/Fee input extract - copy.xlsx",
        help="Enter the full path to your Excel file"
    )
    
    if manual_path != st.session_state.selected_excel_path:
        st.session_state.selected_excel_path = manual_path
        st.rerun()
    
    # Alternative: show current environment variable if set
    env_path = os.environ.get("EXCEL_PATH")
    if env_path:
        st.info(f"💡 Found Excel path in environment: `{env_path}`")
        if st.button("📋 Use Environment Path"):
            st.session_state.selected_excel_path = env_path
            st.rerun()
    
    excel_path = st.session_state.selected_excel_path
    
    # Validation and save
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if excel_path:
            with st.spinner("🔍 Validating Excel file..."):
                is_valid, message = config_manager.validate_excel_file(excel_path)
                
                if is_valid:
                    st.success(f"✅ {message}")
                    st.markdown("**File Details:**")
                    file_path = Path(excel_path)
                    st.write(f"• **Location:** {file_path.parent}")
                    st.write(f"• **Filename:** {file_path.name}")
                    st.write(f"• **Size:** {file_path.stat().st_size / 1024:.1f} KB")
                else:
                    st.error(f"❌ {message}")
    
    with col2:
        if excel_path:
            is_valid, _ = config_manager.validate_excel_file(excel_path)
            if is_valid:
                if st.button("💾 Save & Continue", type="primary"):
                    if config_manager.set_excel_path(excel_path):
                        st.success("Configuration saved successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to save configuration")
    
    st.markdown("---")
    st.markdown("### 📋 Requirements")
    st.markdown("""
    **Your Excel file must contain these sheets and columns:**
    
    **FeeSheet:**
    - Custodian Client Ref, Subscription code, Fund, Gross/Net
    - CC Set up fee %, CC AMC %, CC Carry %
    
    **InvestorSheet:**
    - Custodian Client Ref, Account Name, Salutation
    - First Name, Last Name, Contact email
    
    **CompanySheet:**
    - Company Name, Current Share Price, Share Class
    """)

def render_settings_panel():
    """Render settings management panel."""
    st.header("⚙️ Application Settings")
    
    # Data Source Settings
    st.subheader("📁 Data Source Configuration")
    
    current_path = config_manager.get_excel_path()
    if current_path:
        st.success(f"**Current Excel File:** `{current_path}`")
        
        # Validate current file
        is_valid, message = config_manager.validate_excel_file(current_path)
        if is_valid:
            st.info(f"✅ File is valid: {message}")
        else:
            st.error(f"❌ Current file has issues: {message}")
            st.warning("⚠️ Please update your Excel file path to continue using the application.")
    else:
        st.warning("❌ No Excel file configured")
    
    st.markdown("---")
    
    # Change Excel file
    with st.expander("🔄 Change Excel File"):
        # Initialize session state for settings file selection
        if 'settings_selected_path' not in st.session_state:
            st.session_state.settings_selected_path = current_path or ""
        
        # Display current selection
        if st.session_state.settings_selected_path:
            st.info(f"📄 Selected: `{os.path.basename(st.session_state.settings_selected_path)}`")
            st.caption(f"Full path: {st.session_state.settings_selected_path}")
        
        # File uploader section
        selected_file = render_file_uploader("settings")
        if selected_file:
            st.session_state.settings_selected_path = selected_file
            st.rerun()
        
        # Manual path input (alternative)
        st.markdown("**✏️ Or enter path manually:**")
        manual_path = st.text_input(
            "New Excel File Path",
            value=st.session_state.settings_selected_path,
            placeholder="/path/to/your/Excel file.xlsx",
            key="settings_manual_path"
        )
        
        if manual_path != st.session_state.settings_selected_path:
            st.session_state.settings_selected_path = manual_path
            st.rerun()
        
        new_path = st.session_state.settings_selected_path
        
        if new_path and new_path != current_path:
            is_valid, message = config_manager.validate_excel_file(new_path)
            
            if is_valid:
                st.success(f"✅ {message}")
                if st.button("💾 Update Excel Path"):
                    if config_manager.set_excel_path(new_path):
                        st.success("Excel path updated successfully!")
                        # Reset session state
                        st.session_state.settings_selected_path = new_path
                        st.rerun()
                    else:
                        st.error("Failed to update Excel path")
            else:
                st.error(f"❌ {message}")
    
    # Configuration Info
    st.markdown("---")
    st.subheader("📊 Configuration Information")
    
    config_data = config_manager.get_all_settings()
    if config_data:
        st.json(config_data)
    else:
        st.info("No configuration data available")
    
    # Reset Configuration
    st.markdown("---")
    with st.expander("🗑️ Reset Configuration", expanded=False):
        st.warning("⚠️ This will reset all application settings to defaults.")
        if st.button("Reset All Settings", type="secondary"):
            if config_manager.reset_config():
                st.success("Configuration reset successfully!")
                st.rerun()
            else:
                st.error("Failed to reset configuration")

def check_excel_configuration():
    """Check if Excel configuration is valid and show warnings if not."""
    excel_path = config_manager.get_excel_path()
    
    if not excel_path:
        return False, "No Excel file configured"
    
    is_valid, message = config_manager.validate_excel_file(excel_path)
    if not is_valid:
        return False, message
    
    return True, "Configuration is valid"

def render_specialized_fee_generation():
    """Render the specialized fee letter generation interface"""
    
    # Check Excel configuration first
    config_valid, config_message = check_excel_configuration()
    
    if not config_valid:
        st.error(f"❌ Configuration Error: {config_message}")
        st.info("Please go to Settings to configure your Excel data source.")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⚙️ Go to Settings", type="primary"):
                st.session_state.current_interface = 'settings'
                st.rerun()
        with col2:
            if st.button("🔄 Refresh", type="secondary"):
                st.rerun()
        return
    
    # Page header
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
        <h1 style="color: #2c3e50; font-size: 2.2rem; font-weight: 700; margin-bottom: 0.5rem;">
            Fee Letter Generation
        </h1>
        <p style="color: #7f8c8d; font-size: 1rem; margin-bottom: 0;">
            Create professional fee letters with customizable rates and terms
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Excel Data Management
    try:
        from agents.fee_letter_agent import FeeLetterAgent
        fee_agent = FeeLetterAgent()
        
        # Toolbar with wider search for balance
        col_refresh, col_companies, col_investors = st.columns([1,1,3])
        with col_refresh:
            if st.button("🔄 Refresh Excel Data", help="Clear cache and reload Excel data"):
                try:
                    fee_agent.refresh_excel_cache()
                    st.success("✅ Excel data cache refreshed!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error refreshing cache: {str(e)}")

        with col_companies:
            if st.button("🏢 View Companies", help="List companies and key details"):
                try:
                    data = fee_agent.list_companies()
                    st.info(f"📊 Companies: {data.get('total', 0)}")
                    if data.get('excel_file'):
                        st.caption(f"Excel file: {data.get('excel_file')}")
                    with st.expander("📋 Company list"):
                        rows = data.get('rows', [])
                        if rows:
                            import pandas as _pd
                            st.dataframe(_pd.DataFrame(rows))
                        else:
                            st.caption("No companies found.")
                except Exception as e:
                    st.error(f"❌ Error listing companies: {str(e)}")

        with col_investors:
            # Investor search UI (debounced/live) – wider field, collapsed label
            st.text_input(
                "Investor search",
                key="investor_search_box",
                placeholder="🔎 Search investors (2+ chars)",
                label_visibility="collapsed",
                on_change=lambda: None
            )
            q = (st.session_state.investor_search_box if 'investor_search_box' in st.session_state else '').strip()
            if len(q) < 2:
                st.caption("Type at least 2 characters to search investors")
            else:
                try:
                    with st.spinner("Searching investors..."):
                        data = fee_agent.list_investors(query=q)
                    total = int(data.get('total', 0))
                    st.info(f"👤 Investors: {total}")
                    if data.get('excel_file'):
                        st.caption(f"Excel file: {data.get('excel_file')}")
                    with st.expander("📋 Investor list", expanded=True):
                        rows = data.get('rows', [])
                        if rows:
                            import pandas as _pd
                            df = _pd.DataFrame(rows)
                            limit = 200
                            if len(df) > limit:
                                st.caption(f"Showing first {limit} of {len(df)} matches")
                                df = df.head(limit)
                            st.dataframe(df, use_container_width=True, height=360)
                        else:
                            st.caption("No investors found.")
                except Exception as e:
                    st.error(f"❌ Error listing investors: {str(e)}")
        
        st.divider()
        
        # Show current Excel path and last-modified for visibility
        try:
            # Re-read config fresh from disk to avoid stale in-memory values
            from config_manager import ConfigManager as _CMDisp
            current_excel_path = _CMDisp().get_excel_path()
            if current_excel_path:
                st.caption(f"Using Excel file: `{current_excel_path}`")
                import os, datetime
                try:
                    mtime = os.path.getmtime(current_excel_path)
                    st.caption(f"Last modified: {datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}")
                except Exception:
                    pass
        except Exception:
            pass

        # Maintain Excel File controls (placed on Fee Letter Generation page)
        try:
            if current_excel_path:
                with st.expander("📂 Maintain Excel File", expanded=False):
                    st.caption("Recommended: keep one shared Excel file. Uploading will replace that file in-place (path unchanged).")
                    # Direct uploader that does NOT auto-change path
                    import os
                    from pathlib import Path
                    up = st.file_uploader(
                        "Choose Excel File",
                        type=["xlsx", "xls"],
                        key="maintain_excel_uploader",
                        help="Upload a new version to replace the current shared file"
                    )
                    temp_upload_path = None
                    if up is not None:
                        temp_dir = Path.home() / ".streamlit_temp"
                        temp_dir.mkdir(exist_ok=True)
                        temp_upload_path = str(temp_dir / up.name)
                        try:
                            with open(temp_upload_path, "wb") as f:
                                f.write(up.getbuffer())
                            st.success(f"Uploaded: {up.name}")
                            st.caption(f"Temporary upload: {temp_upload_path}")
                        except Exception as e:
                            st.error(f"Failed to save upload: {e}")

                    if temp_upload_path:
                        col_rep_fp, col_switch_fp = st.columns(2)
                        with col_rep_fp:
                            if st.button("⬆️ Replace current file in-place", key="replace_current_file_fp"):
                                try:
                                    import shutil
                                    shutil.copyfile(temp_upload_path, current_excel_path)
                                    fee_agent.refresh_excel_cache()
                                    st.success("Replaced configured Excel file in-place. Cache cleared.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to replace file: {e}")
                        with col_switch_fp:
                            if st.button("🔁 Switch to uploaded copy (not recommended)", key="switch_to_uploaded_fp"):
                                if config_manager.set_excel_path(temp_upload_path):
                                    fee_agent.refresh_excel_cache()
                                    st.success("Excel path updated to uploaded file. Cache cleared.")
                                    st.rerun()
                                else:
                                    st.error("Failed to update Excel path")

                    st.markdown("**Or enter path manually:**")
                    manual_new_fp = st.text_input("New Excel File Path", value=current_excel_path or "", key="quick_change_path_fp")
                    if st.button("💾 Use This Path", key="quick_change_save_fp"):
                        if manual_new_fp:
                            if config_manager.set_excel_path(manual_new_fp):
                                fee_agent.refresh_excel_cache()
                                st.success("Excel path updated. Cache cleared.")
                                st.rerun()
                            else:
                                st.error("Failed to update Excel path")
        except Exception:
            pass

        st.markdown("---")
    except Exception as e:
        st.warning(f"⚠️ Could not initialize Excel data management: {str(e)}")
    
    # Main form
    with st.form("specialized_fee_form", clear_on_submit=False):
        
        # Basic Information Section
        st.markdown("### Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            investor_name = st.text_input(
                "Investor Name *", 
                placeholder="e.g., Jacob Pedersen",
                help="Full name of the investor",
                key="specialized_investor_name"
            )
            
            investment_amount = st.number_input(
                "Investment Amount (£) *", 
                min_value=1000, 
                max_value=5000000, 
                value=50000,
                step=1000,
                help="Total investment amount in British Pounds",
                key="specialized_investment_amount"
            )
        
        with col2:
            company_name = st.text_input(
                "Company Name *", 
                placeholder="e.g., Harper Concierge Ltd",
                help="Full legal name of the company",
                key="specialized_company_name"
            )
        
        st.markdown("---")
        
        # Excel-driven configuration
        st.caption("Fees, investor classification (Professional/Retail), and investment type (Gross/Net) are pulled from Excel (FeeSheet/InvestorSheet). Share price and class come from CompanySheet.")
        
        st.markdown("---")
        
        # Overrides section (take precedence over Excel)
        overrides = {}
        with st.expander("⚙️ Override variables (optional)", expanded=False):
            st.caption("These values will override Excel for this letter only.")
            col_ov1, col_ov2, col_ov3 = st.columns(3)
            with col_ov1:
                ov_upfront = st.number_input("Setup Fee %", min_value=0.0, max_value=10.0, 
                                           value=st.session_state.get('ov_upfront', 0.0), step=0.1, key='ov_upfront')
                ov_vat = st.number_input("VAT %", min_value=0.0, max_value=25.0, 
                                       value=st.session_state.get('ov_vat', 0.0), step=0.5, key='ov_vat')
            with col_ov2:
                ov_amc13 = st.number_input("AMC 1–3 % (per year)", min_value=0.0, max_value=10.0, 
                                          value=st.session_state.get('ov_amc13', 0.0), step=0.1, key='ov_amc13')
                ov_share = st.number_input("Share Price (£)", min_value=0.0, max_value=1000.0, 
                                         value=st.session_state.get('ov_share', 0.0), step=0.01, key='ov_share')
            with col_ov3:
                ov_amc45 = st.number_input("AMC 4–5 % (per year)", min_value=0.0, max_value=10.0, 
                                          value=st.session_state.get('ov_amc45', 0.0), step=0.1, key='ov_amc45')
                ov_type = st.selectbox("Investment Type", ["No override", "Gross", "Net"], 
                                     index=st.session_state.get('ov_type_index', 0), key='ov_type')
            
            # Additional overrides (investor type and share class)
            col_ov4, col_ov5 = st.columns(2)
            with col_ov4:
                ov_investor_type = st.selectbox(
                    "Investor Type", ["No override", "Professional", "Retail"], 
                    index=st.session_state.get('ov_investor_type_index', 0), key='ov_investor_type',
                    help="Override investor classification"
                )
            with col_ov5:
                ov_share_class = st.text_input(
                    "Share Class Override", 
                    value=st.session_state.get('ov_share_class', ''), 
                    placeholder="e.g., A Ordinary", key='ov_share_class',
                    help="Override share class name"
                )
            
            # Number of shares override
            col_ov6, col_ov7 = st.columns(2)
            with col_ov6:
                ov_shares_override = st.number_input(
                    "Number of Shares Override",
                    min_value=0,
                    value=st.session_state.get('ov_shares_override', 0),
                    key='ov_shares_override',
                    help="Override calculated number of shares"
                )
            with col_ov7:
                st.caption("Leave as 0 to use calculated value")
        
        # Build overrides dictionary from session state values
        if st.session_state.get('ov_upfront', 0.0) > 0:
            overrides['upfront_fee_pct'] = float(st.session_state.get('ov_upfront', 0.0))
        if st.session_state.get('ov_amc13', 0.0) > 0:
            overrides['amc_1_3_pct'] = float(st.session_state.get('ov_amc13', 0.0))
        if st.session_state.get('ov_amc45', 0.0) > 0:
            overrides['amc_4_5_pct'] = float(st.session_state.get('ov_amc45', 0.0))
        if st.session_state.get('ov_vat', 0.0) > 0:
            overrides['vat_rate'] = float(st.session_state.get('ov_vat', 0.0))
        if st.session_state.get('ov_share', 0.0) > 0:
            overrides['share_price_override'] = float(st.session_state.get('ov_share', 0.0))
        if st.session_state.get('ov_type', 'No override') != "No override":
            overrides['investment_type_override'] = st.session_state.get('ov_type', 'No override').lower()
        if st.session_state.get('ov_investor_type', 'No override') != "No override":
            overrides['investor_type_override'] = st.session_state.get('ov_investor_type', 'No override').lower()
        if st.session_state.get('ov_share_class', '').strip():
            overrides['share_class_override'] = st.session_state.get('ov_share_class', '').strip()
        
        # Add shares override if specified
        if st.session_state.get('ov_shares_override', 0) > 0:
            overrides['shares_override'] = int(st.session_state.get('ov_shares_override', 0))
        
        # Form submission
        st.markdown("---")
        
        col_submit, col_clear = st.columns([3, 1])
        
        with col_submit:
            # Only allow preview first - no direct send option
            preview_clicked = st.form_submit_button(
                "Preview Fee Letter", 
                type="primary",
                use_container_width=True
            )
        
        with col_clear:
            clear_clicked = st.form_submit_button(
                "🗑️ Clear", 
                use_container_width=True
            )
        
        # Remove direct send option - must preview first
        generate_clicked = False
    
    # Handle clear button
    if clear_clicked:
        # Clear all input fields by deleting their session state keys
        keys_to_clear = [
            "specialized_investor_name",
            "specialized_company_name", 
            "specialized_investment_amount",
            # Clear override variables
            "ov_upfront",
            "ov_vat", 
            "ov_amc13",
            "ov_amc45",
            "ov_share",
            "ov_type",
            "ov_investor_type",
            "ov_share_class",
            "ov_shares_override"
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Clear any previous preview
        if 'last_fee_preview' in st.session_state:
            del st.session_state['last_fee_preview']
        
        st.rerun()
    
    # Handle form submissions
    if preview_clicked or generate_clicked:
        # Validate required fields
        if not investor_name or not company_name or investment_amount <= 0:
            st.error("❌ Please fill in all required fields (marked with *)")
            return
        
        # Process the request
        with st.spinner("Processing fee letter request..."):
            try:
                from vc_enhanced_utils import PolicyGate, FeeCalculator
                from agents.fee_letter_agent import FeeLetterAgent
                
                # Create prompt (investment type will be determined from Excel)
                prompt = f"create a fee letter for {investor_name} for {investment_amount} into {company_name}"
                
                # Use enhanced agent with configured Excel path
                fee_agent = FeeLetterAgent()
                
                # Set Excel path from configuration
                excel_path = config_manager.get_excel_path()
                if excel_path:
                    os.environ["EXCEL_PATH"] = excel_path
                
                custom_fees = overrides if overrides else None
                result = fee_agent.execute_enhanced(prompt, custom_fees=custom_fees)
                
                if result["success"]:
                    st.success(result['message'].replace("✅ ", ""))
                    # Persist preview so it stays after reruns
                    st.session_state['last_fee_preview'] = result
                    
                    # Show detailed preview
                    render_fee_letter_preview(result, preview_only=preview_clicked)

                    # Send is handled within the preview section now (single-button flow)
                    
                else:
                    st.error(f"❌ {result['message']}")
                    if "missing_fields" in result:
                        st.write("**Missing Required Fields:**")
                        for field in result["missing_fields"]:
                            st.write(f"• {field}")
                            
            except ImportError:
                st.error("❌ Enhanced utilities not available. Please ensure all required modules are installed.")
            except Exception as e:
                st.error(f"❌ Error processing request: {str(e)}")

    # If not submitting this run, render the last successful preview if present
    if not (preview_clicked or generate_clicked) and st.session_state.get('last_fee_preview'):
        render_fee_letter_preview(st.session_state['last_fee_preview'], preview_only=True)

def render_fee_letter_preview(result: Dict[str, Any], preview_only: bool = True):
    """Render detailed fee letter preview"""
    
    st.markdown("---")
    st.markdown("## Fee Letter Preview")

    # Persisted debug info (shown after reruns)
    if st.session_state.get('fee_letter_debug_last_approved'):
        dbg = st.session_state['fee_letter_debug_last_approved']
        st.info(f"Approved payload – to_email='{dbg.get('to_email','')}', company='{dbg.get('company_name','')}', content_length={dbg.get('content_len',0)}")

    # Persisted send result (shown after reruns)
    if st.session_state.get('fee_letter_debug_last_send'):
        send_dbg = st.session_state['fee_letter_debug_last_send']
        if send_dbg.get('success'):
            st.success(f"Last send succeeded to {send_dbg.get('to_email','')}")
        else:
            detail = send_dbg.get('error_detail') or 'Unknown error'
            st.error(f"Last send failed to {send_dbg.get('to_email','')}. Details: {detail}")
    
    if preview_only:
        st.info("Preview Mode - No fee letter will be sent")
    else:
        st.success("Generation Mode - Fee letter will be processed")
    
    preview_data = result.get("preview_data", {})
    fee_calculation = result.get("fee_calculation")
    validation_result = result.get("validation_result")
    
    # Main preview content
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("### Fee Letter Details")
        
        # Show summary first
        investor_type = result.get('investor_data', {}).get('Investor Type', 'N/A')
        if not investor_type or investor_type == 'N/A':
            # Try to get from fee_calculation breakdown
            fee_calc = result.get("fee_calculation")
            if fee_calc and hasattr(fee_calc, 'breakdown'):
                investor_type = fee_calc.breakdown.get('investor_type', 'N/A').title()
        
        # Get share price from company data
        share_price = result.get('company_data', {}).get('Current Share Price', 'N/A')
        if share_price != 'N/A':
            share_price_display = f"£{share_price:.2f}"
        else:
            share_price_display = "N/A"
        
        # Proper capitalization for display
        investor_type_display = investor_type.title() if investor_type != 'N/A' else 'N/A'
        investment_type_display = preview_data.get('investment_type', 'N/A').title() if preview_data.get('investment_type', 'N/A') != 'N/A' else 'N/A'
        
        st.markdown(f"""
        **Investor:** {preview_data.get('investor_name', 'N/A')}  
        **Investor Type:** {investor_type_display}  
        **Investment Type:** {investment_type_display}  
        **Company:** {preview_data.get('company_name', 'N/A')}  
        **Gross Investment:** £{preview_data.get('gross_investment', 0):,.2f}  
        **Total Fees:** £{preview_data.get('total_fees', 0):,.2f}  
        **Total Transfer Required:** £{preview_data.get('total_transfer', 0):,.2f}  
        **Share Price:** {share_price_display}  
        **Share Quantity:** {preview_data.get('share_quantity', 0):,.2f}  
        **Recipient Email:** {result.get('to_email', 'N/A')}  
        """)
        if preview_data.get('reference'):
            st.markdown(f"**Reference:** {preview_data['reference']}")
        
        # Remove redundant calculation note as method is already displayed in Fee Breakdown
        
        # Show actual fee letter text
        st.markdown("### Actual Fee Letter Text")
        if result.get('email_content'):
            # Convert HTML to readable text for preview
            email_content = result['email_content']
            
            # Remove HTML tags and convert to readable text
            readable_content = re.sub(r'<[^>]+>', '', email_content)
            readable_content = re.sub(r'&pound;', '£', readable_content)
            readable_content = re.sub(r'&nbsp;', ' ', readable_content)
            readable_content = re.sub(r'\s+', ' ', readable_content).strip()
            
            # Add share quantity information if available
            preview_data = result.get('preview_data', {})
            if preview_data.get('shares_have_decimals'):
                shares_info = f"\n\nNote: Share quantity {preview_data.get('share_quantity_exact', 0):,.2f} has been rounded to {preview_data.get('share_quantity_rounded', 0):,} for ease of allocation."
                readable_content += shares_info
            
            st.text_area(
                "Fee Letter Content (as it will appear):",
                value=readable_content,
                height=400,
                disabled=True,
                help="This is the exact text that will be sent in the fee letter"
            )
        else:
            st.warning("Fee letter content not available for preview")
    
    with col_right:
        st.markdown("### Fee Breakdown")
        
        if fee_calculation:
            # Get breakdown data for percentages
            breakdown = getattr(fee_calculation, 'breakdown', {}) or {}
            applied_rates = breakdown.get('applied_rates', {})

            
            # Get AMC rates
            amc_1_3_rate = applied_rates.get('amc_1_3_pct', fee_calculation.fee_rate)
            amc_4_5_rate = applied_rates.get('amc_4_5_pct', 1.5)  # Default fallback
            upfront_rate = applied_rates.get('upfront_pct', 1.5)  # Default fallback
            
            # Format method display
            method_display = "Net" if "net" in fee_calculation.calculation_method.lower() else "Gross"
            
            # Use totals including VAT for display
            fee_bd = breakdown.get('fee_breakdown', {})
            upfront_tot = fee_bd.get('upfront_total', fee_bd.get('upfront', 0.0)) or 0.0
            amc_1_3_tot = fee_bd.get('amc_1_3_total', fee_bd.get('amc_1_3', 0.0)) or 0.0
            amc_4_5_tot = fee_bd.get('amc_4_5_total', fee_bd.get('amc_4_5', 0.0)) or 0.0
            management_fee_incl_vat = (amc_1_3_tot or 0.0) + (amc_4_5_tot or 0.0)

            st.metric("Management Fee (incl. VAT)", f"£{management_fee_incl_vat:,.2f}", 
                     help=f"AMC 1-3: {amc_1_3_rate:.1f}% | AMC 4-5: {amc_4_5_rate:.1f}%")
            st.metric("Admin Fee (incl. VAT)", f"{upfront_rate:.1f}% - £{upfront_tot:,.2f}", 
                     help="CC Set Up Costs")
            st.metric("AMC 1–3 (incl. VAT)", f"{amc_1_3_rate:.1f}% - £{amc_1_3_tot:,.2f}", 
                     help="Annual Management Charges for years 1-3")
            st.metric("AMC 4–5 (future, incl. VAT)", f"{amc_4_5_rate:.1f}% - £{amc_4_5_tot:,.2f}", 
                     help="Annual Management Charges for years 4-5")
            st.metric("Method", method_display)


            # Show investor-type specific inputs used by the calculator
            try:
                breakdown = getattr(fee_calculation, 'breakdown', {}) or {}
                applied_rates = breakdown.get('applied_rates', {})
                fee_bd = breakdown.get('fee_breakdown', {})
                investor_type_used = breakdown.get('investor_type', 'n/a').title()
                amc_base = applied_rates.get('amc_base')
                upfront_total = fee_bd.get('upfront_total', fee_bd.get('upfront'))
                amc_1_3_total = fee_bd.get('amc_1_3_total', fee_bd.get('amc_1_3'))
                with st.expander("Calculation inputs used"):
                    st.write(f"Investor type: {investor_type_used}")
                    if amc_base is not None:
                        st.write(f"AMC base: £{amc_base:,.2f}")
                    if upfront_total is not None:
                        st.write(f"Upfront total (incl. VAT): £{upfront_total:,.2f}")
                    if amc_1_3_total is not None:
                        st.write(f"AMC 1–3 total (incl. VAT): £{amc_1_3_total:,.2f}")
                    # Show applied percentage rates (from Excel when available)
                    try:
                        up = applied_rates.get('upfront_pct')
                        a13 = applied_rates.get('amc_1_3_pct')
                        a45 = applied_rates.get('amc_4_5_pct')
                        perf = applied_rates.get('performance_pct')
                        if any(v is not None for v in [up, a13, a45, perf]):
                            st.write("Applied rates:")
                            if up is not None:
                                st.write(f"- Upfront: {up:.2f}%")
                            if a13 is not None:
                                st.write(f"- AMC 1–3: {a13:.2f}%")
                            if a45 is not None:
                                st.write(f"- AMC 4–5: {a45:.2f}%")
                            if perf is not None:
                                st.write(f"- Performance carry: {perf:.2f}%")
                    except Exception:
                        pass
            except Exception:
                pass
    
    # Validation warnings suppressed globally
    
    # Email sending options with clear descriptions
    st.markdown("### Email Options")
    st.info("📋 **Choose how to send the fee letter:**\n"
            "• **Send to Team First** - Send to CC employees for review before investor delivery\n"
            "• **Send to Investor Direct** - Send directly to the investor (use only when approved)")
    
    # Team email configuration section
    with st.expander("⚙️ Configure Team Email Recipients", expanded=False):
        st.markdown("**Primary Recipients (TO):**")
        
        # Initialize team email widget keys in session state if not present
        if 'team_primary_emails_input' not in st.session_state:
            st.session_state.team_primary_emails_input = "Jamie.Harris@committedcapital.co.uk\nlilie.chouchou@committedcapital.co.uk"
        
        if 'team_cc_email_input' not in st.session_state:
            st.session_state.team_cc_email_input = "Joshua.Spence@committedcapital.co.uk"
        
        # Dynamic primary recipients
        primary_emails_text = st.text_area(
            "Primary Recipients (one per line)",
            height=100,
            help="Enter email addresses, one per line. These will be the main recipients (TO field).",
            key="team_primary_emails_input"
        )
        
        # CC recipient
        cc_email_text = st.text_input(
            "CC Recipient (optional)",
            help="Optional CC recipient email address",
            key="team_cc_email_input"
        )
        
        # Parse current values for display and usage
        team_primary_emails = [email.strip() for email in primary_emails_text.split('\n') if email.strip()]
        team_cc_email = cc_email_text.strip()
        
        # Show current configuration
        st.markdown("**Current Configuration:**")
        st.write(f"• **TO:** {', '.join(team_primary_emails)}")
        if team_cc_email:
            st.write(f"• **CC:** {team_cc_email}")
        
        # Reset to defaults button
        if st.button("🔄 Reset to Defaults"):
            # Delete the existing keys so they can be reinitialized with default values
            if "team_primary_emails_input" in st.session_state:
                del st.session_state["team_primary_emails_input"]
            if "team_cc_email_input" in st.session_state:
                del st.session_state["team_cc_email_input"]
            st.rerun()
    
    col_draft, col_team, col_investor = st.columns(3)

    with col_draft:
        to_email = result.get('to_email', '')
        company_name = result.get('company_data', {}).get('Company Name', 'Unknown Company')
        email_content = result.get('email_content', '')
        
        if st.button("📝 Create as Draft", use_container_width=True):
            try:
                from agents.fee_letter_agent import FeeLetterAgent
                # Force draft mode for this action
                fee_agent = FeeLetterAgent()
                fee_agent.email_mode = "draft"  # Override to draft mode
                if hasattr(fee_agent.mail_service, 'set_send_mode'):
                    fee_agent.mail_service.set_send_mode("draft")  # Update mail service mode
                
                if to_email and email_content:
                    ok = fee_agent.send_fee_letter_email(to_email, company_name, email_content)
                    if ok:
                        st.success(f"📝 Fee letter draft created successfully for {to_email}")
                        st.info("💡 Draft saved to investors@committedcapital.co.uk drafts folder")
                    else:
                        err = getattr(fee_agent, 'last_email_error', None)
                        st.error(f"❌ Failed to create draft for {to_email}. Details: {err or 'Unknown error'}")
                else:
                    st.error("❌ Missing recipient email or content.")
            except Exception as e:
                st.error(f"❌ Error creating draft: {e}")

    with col_team:
        company_name = result.get('company_data', {}).get('Company Name', 'Unknown Company')
        email_content = result.get('email_content', '')
        investor_name = result.get('investor_data', {}).get('First Name', 'Investor')
        
        if st.button("📋 Send to Team", type="secondary", use_container_width=True):
            try:
                from agents.fee_letter_agent import FeeLetterAgent
                # Force send mode for team emails
                fee_agent = FeeLetterAgent()
                fee_agent.email_mode = "send"  # Override to send mode
                if hasattr(fee_agent.mail_service, 'set_send_mode'):
                    fee_agent.mail_service.set_send_mode("send")  # Update mail service mode
                
                # Use dynamic email addresses from current form values
                primary_recipients = team_primary_emails
                cc_recipient = team_cc_email
                
                # Validate email addresses
                if not primary_recipients:
                    st.error("❌ No primary recipients configured. Please add at least one email address.")
                    return
                
                if email_content:
                    # Add header to email for team review
                    team_email_content = f"""TEAM REVIEW - Fee Letter for {investor_name}
Company: {company_name}
Final Recipient: {result.get('to_email', 'N/A')}

Please review the fee letter below before sending to the investor.

---

{email_content}"""
                    
                    # Send to team with CC (handle case where CC might be empty)
                    if cc_recipient:
                        ok = fee_agent.send_team_review_email(primary_recipients, cc_recipient, company_name, team_email_content, investor_name)
                        success_msg = f"📧 Fee letter sent to team for review: {', '.join(primary_recipients)} (CC: {cc_recipient})"
                    else:
                        # Send without CC if no CC recipient specified
                        ok = fee_agent.send_team_review_email_no_cc(primary_recipients, company_name, team_email_content, investor_name)
                        success_msg = f"📧 Fee letter sent to team for review: {', '.join(primary_recipients)}"
                    
                    if ok:
                        st.success(success_msg)
                    else:
                        err = getattr(fee_agent, 'last_email_error', None)
                        st.error(f"❌ Failed to send team email. Details: {err or 'Unknown error'}")
                else:
                    st.error("❌ Missing email content.")
            except Exception as e:
                st.error(f"❌ Error sending team email: {e}")

    with col_investor:
        to_email = result.get('to_email', '')
        if st.button("📧 Send to Investor Direct", type="primary", use_container_width=True):
            try:
                from agents.fee_letter_agent import FeeLetterAgent
                # Force send mode for direct investor emails
                fee_agent = FeeLetterAgent()
                fee_agent.email_mode = "send"  # Override to send mode
                if hasattr(fee_agent.mail_service, 'set_send_mode'):
                    fee_agent.mail_service.set_send_mode("send")  # Update mail service mode
                
                if to_email and email_content:
                    ok = fee_agent.send_fee_letter_email(to_email, company_name, email_content)
                    if ok:
                        st.success(f"📧 Fee letter email sent successfully to {to_email}")
                        st.info("💡 Email sent directly from investors@committedcapital.co.uk")
                    else:
                        err = getattr(fee_agent, 'last_email_error', None)
                        st.error(f"❌ Failed to send email to {to_email}. Details: {err or 'Unknown error'}")
                else:
                    st.error("❌ Missing recipient email or content.")
            except Exception as e:
                st.error(f"❌ Error sending email: {e}")

    # Email healthcheck (optional, for debugging)
    if st.button("🩺 Email Healthcheck", use_container_width=True):
        try:
            from agents.fee_letter_agent import FeeLetterAgent
            fee_agent = FeeLetterAgent()
            diag = fee_agent.email_healthcheck()
            if diag.get('ok'):
                st.success(f"Email OK via {diag.get('method')}. Details: {' | '.join(diag.get('details', []))}")
            else:
                st.error(f"Email FAILED. Details: {' | '.join(diag.get('details', []))}")
        except Exception as e:
            st.error(f"Healthcheck error: {e}")

def render_research_interface():
    """Render company research interface"""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
        <h1 style="color: #2c3e50; font-size: 2.2rem; font-weight: 700; margin-bottom: 0.5rem;">
            Company Research
        </h1>
        <p style="color: #7f8c8d; font-size: 1rem; margin-bottom: 0;">
            Deep dive analysis and due diligence tools
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("🚧 Company Research interface coming soon. Use the AI Chat Assistant for company analysis in the meantime.")

def render_settings_interface():
    """Render system settings interface"""
    render_settings_panel()
    
    # Email diagnostics
    st.subheader("Email Diagnostics")
    st.caption("Use these tools to verify email connectivity and send a test email.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Email Healthcheck", use_container_width=True):
            try:
                from agents.fee_letter_agent import FeeLetterAgent
                fee_agent = FeeLetterAgent()
                diag = fee_agent.email_healthcheck()
                details = ' | '.join(diag.get('details', []))
                if diag.get('ok'):
                    st.success(f"Email OK via {diag.get('method')}. {details}")
                else:
                    st.error(f"Email FAILED. {details}")
            except Exception as e:
                st.error(f"Healthcheck error: {e}")

    with col2:
        with st.form("email_test_form"):
            to_email = st.text_input("To email", placeholder="you@example.com")
            subject = st.text_input("Subject", value="Test Email from Fee Automation")
            body = st.text_area("Body", value="This is a test email.")
            send_test = st.form_submit_button("Send Test Email")
        if send_test:
            try:
                from agents.fee_letter_agent import FeeLetterAgent
                fee_agent = FeeLetterAgent()
                ok = fee_agent._send_email(to_email, subject, body)
                if ok:
                    st.success(f"Test email sent to {to_email}")
                else:
                    err = getattr(fee_agent, 'last_email_error', 'Unknown error')
                    st.error(f"Failed to send test email to {to_email}. Details: {err}")
            except Exception as e:
                st.error(f"Test send error: {e}")

if __name__ == "__main__":
    try:
        # Check for first-run setup (Excel configuration) before proceeding
        if config_manager.is_first_run():
            render_first_run_setup()
            st.stop()
        
        initialize_session_state()
        
        # Always render navigation (shows signed-in indicator on all pages)
        current_interface = st.session_state.get('current_interface', 'main_selection')
        render_navigation()
        
        # Router based on current interface
        if current_interface == 'main_selection':
            render_main_selection()
        elif current_interface == 'fee_generation':
            render_specialized_fee_generation()
        elif current_interface == 'chat':
            main()  # Use existing chat interface
        elif current_interface == 'analytics':
            render_fee_letter_dashboard()  # Use existing dashboard
        elif current_interface == 'research':
            render_research_interface()
        elif current_interface == 'settings':
            render_settings_interface()
        else:
            # Fallback to main selection
            st.session_state.current_interface = 'main_selection'
            st.rerun()
            
    except Exception as e:
        st.error("🚫 **Application Error**")
        st.markdown(f"""
        ### ❌ The application encountered an error:
        
        ```
        {str(e)}
        ```
        
        This is likely due to missing dependencies or configuration issues.
        """)
        
        if st.button("🧪 Show Diagnostic Information"):
            import traceback
            st.code(traceback.format_exc())
            
        render_minimal_fallback()

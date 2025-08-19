#!/usr/bin/env python3
"""
Minimal Test - Fee Letter Agent
================================
A minimal test to verify core functionality works without optional dependencies.
"""

import streamlit as st
import sys
import traceback

# Page configuration
st.set_page_config(
    page_title="Fee Letter Agent - Test",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Minimal Test - Fee Letter Agent")

# Test core imports
st.subheader("📦 Testing Core Dependencies")

tests = [
    ("Streamlit", "streamlit", None),
    ("Pandas", "pandas", None),
    ("OpenPyXL", "openpyxl", None),
    ("RapidFuzz", "rapidfuzz", None),
    ("Jinja2", "jinja2", None),
    ("MSAL", "msal", None),
    ("Requests", "requests", None),
    ("Python-dotenv", "dotenv", None),
]

optional_tests = [
    ("LangChain", "langchain", "AI Chat features"),
    ("LangChain Community", "langchain_community", "AI Chat features"),
    ("Config Manager", "config_manager", "Configuration management"),
    ("VC Conversational Agent", "vc_conversational_agent", "AI Chat interface"),
    ("Fee Letter Agent", "agents.fee_letter_agent", "Fee letter generation"),
    ("VC Enhanced Utils", "vc_enhanced_utils", "Enhanced features"),
]

# Test core dependencies
st.markdown("### ✅ Core Dependencies")
all_core_passed = True

for name, module, note in tests:
    try:
        __import__(module)
        st.success(f"✅ {name}")
    except ImportError as e:
        st.error(f"❌ {name}: {e}")
        all_core_passed = False

# Test optional dependencies
st.markdown("### 🔧 Optional Dependencies")
optional_available = []

for name, module, note in optional_tests:
    try:
        __import__(module)
        st.success(f"✅ {name} - {note}")
        optional_available.append(name)
    except ImportError as e:
        st.warning(f"⚠️ {name} - {note}: Not available")

# Summary
st.markdown("---")
st.subheader("📊 Test Summary")

if all_core_passed:
    st.success("🎉 **All core dependencies are available!**")
    st.info("✅ The application should run with basic functionality.")
else:
    st.error("❌ **Some core dependencies are missing.**")
    st.error("🚫 The application may not work correctly.")

if optional_available:
    st.info(f"🔧 **Optional features available:** {', '.join(optional_available)}")
else:
    st.warning("⚠️ **No optional features available** - only core functionality will work.")

# Test simple functionality
st.markdown("---")
st.subheader("🧪 Basic Functionality Test")

if st.button("Test Basic Operations"):
    try:
        import pandas as pd
        import json
        from datetime import datetime
        
        # Create test data
        test_data = {
            "timestamp": datetime.now().isoformat(),
            "test_value": 42,
            "status": "success"
        }
        
        # Test pandas
        df = pd.DataFrame([test_data])
        st.success("✅ Pandas DataFrame creation works")
        st.dataframe(df)
        
        # Test JSON
        json_str = json.dumps(test_data, indent=2)
        st.success("✅ JSON serialization works")
        
        st.success("🎉 **Basic operations test passed!**")
        
    except Exception as e:
        st.error(f"❌ Basic operations test failed: {e}")
        st.code(traceback.format_exc())

# Environment info
with st.expander("🔍 Environment Information"):
    st.code(f"""
Python Version: {sys.version}
Platform: {sys.platform}
Python Path: {sys.executable}
Working Directory: {sys.path[0] if sys.path else 'Unknown'}
""")

st.markdown("---")
st.caption("💡 This test helps diagnose dependency issues in Pinokio or other deployment environments.")

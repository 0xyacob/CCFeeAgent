#!/usr/bin/env python3
"""
Simple Fee Letter Agent - Minimal Dependencies Version
======================================================
A simplified version that works with minimal dependencies for deployment testing.
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="CC Fee Letter Agent - Simple",
    page_icon="🚀",
    layout="wide"
)

# Password protection
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 CC Fee Letter Agent - Simple Version")
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

# Main application
st.title("🚀 CC Fee Letter Agent - Simple Version")

st.success("✅ **Application is running successfully!**")

st.info("""
🎉 **Congratulations!** The simplified version is working correctly.

This proves that:
- ✅ Streamlit is working
- ✅ Core Python dependencies are available  
- ✅ The Pinokio environment is functional
- ✅ Authentication system works
""")

# Basic functionality test
st.markdown("---")
st.subheader("🧪 Basic Functionality Test")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Data Processing Test")
    
    if st.button("Test Pandas Operations"):
        try:
            # Create sample data
            data = {
                'Investor': ['Alice Johnson', 'Bob Smith', 'Carol Davis'],
                'Amount': [50000, 75000, 100000],
                'Fee_Rate': [0.015, 0.015, 0.015],
                'Fee_Amount': [750, 1125, 1500]
            }
            
            df = pd.DataFrame(data)
            st.success("✅ Pandas DataFrame created successfully!")
            st.dataframe(df)
            
        except Exception as e:
            st.error(f"❌ Pandas test failed: {e}")

with col2:
    st.markdown("### 📁 File System Test")
    
    if st.button("Test File Operations"):
        try:
            # Test file operations
            test_file = Path("test_output.json")
            test_data = {
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "message": "File operations working"
            }
            
            # Write test file
            with open(test_file, 'w') as f:
                json.dump(test_data, f, indent=2)
            
            # Read test file
            with open(test_file, 'r') as f:
                loaded_data = json.load(f)
            
            st.success("✅ File operations working!")
            st.json(loaded_data)
            
            # Clean up
            if test_file.exists():
                test_file.unlink()
            
        except Exception as e:
            st.error(f"❌ File operations test failed: {e}")

# Environment information
st.markdown("---")
st.subheader("🔍 Environment Information")

with st.expander("View Environment Details"):
    import sys
    
    env_info = {
        "Python Version": sys.version,
        "Platform": sys.platform,
        "Executable": sys.executable,
        "Working Directory": os.getcwd(),
        "Streamlit Version": st.__version__,
        "Pandas Version": pd.__version__
    }
    
    for key, value in env_info.items():
        st.text(f"{key}: {value}")

# Next steps
st.markdown("---")
st.subheader("🎯 Next Steps")

st.markdown("""
Since this simplified version is working, the issue with the full application is likely:

1. **Missing Dependencies**: Some Python packages (like `langchain`, `msal`, etc.) may not be installed
2. **Import Errors**: Specific modules may be failing to import
3. **Configuration Issues**: Config files or data files may be missing

**Recommended Actions:**
- ✅ Run the diagnostic test from the Pinokio menu
- ✅ Check the installation logs for any failed packages
- ✅ Try the full application after ensuring all dependencies are installed
""")

if st.button("🔄 Switch to Full Application"):
    st.info("To switch to the full application, restart Pinokio and select 'Start Fee Letter Agent' from the menu.")

st.markdown("---")
st.caption("💡 This is a simplified version for testing deployment environments.")

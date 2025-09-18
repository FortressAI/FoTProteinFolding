#!/usr/bin/env python3
"""
Main entry point for Streamlit Cloud deployment
Redirects to the optimized dashboard in the streamlit_dashboard folder
"""

import sys
import os
from pathlib import Path

# Add streamlit_dashboard to path
dashboard_dir = Path(__file__).parent / "streamlit_dashboard"
sys.path.insert(0, str(dashboard_dir))

# Import and run the optimized dashboard
try:
    # Change working directory to streamlit_dashboard for proper data loading
    os.chdir(dashboard_dir)
    
    # Import the main dashboard
    from streamlit_cloud_optimized import main
    
    # Run the dashboard
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    import streamlit as st
    st.error(f"❌ Import Error: {e}")
    st.error("Please ensure all dependencies are installed correctly.")
    st.stop()
except Exception as e:
    import streamlit as st
    st.error(f"❌ Application Error: {e}")
    st.error("Please check the application configuration.")
    st.stop()

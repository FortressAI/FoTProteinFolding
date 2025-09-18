#!/usr/bin/env python3
"""
FoT Protein Discovery Dashboard - Streamlit Cloud Entry Point
Optimized for 251K protein dataset with static data loading
"""

import streamlit as st
import pandas as pd
import json
import gzip
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="FoT Protein Discovery Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .priority-high { color: #ff6b6b; font-weight: bold; }
    .priority-medium { color: #ffa726; font-weight: bold; }
    .priority-low { color: #66bb6a; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load protein discovery data from static files"""
    
    # Try to load from streamlit_dashboard/data first
    data_paths = [
        "streamlit_dashboard/data",
        "data", 
        "."
    ]
    
    for data_dir in data_paths:
        # Try compressed JSON first
        json_path = Path(data_dir) / "protein_discovery_data.json.gz"
        if json_path.exists():
            try:
                with gzip.open(json_path, 'rt') as f:
                    data = json.load(f)
                
                proteins_df = pd.DataFrame(data['proteins'])
                summary_stats = data['summary_stats']
                
                st.sidebar.success(f"🔗 Loaded {len(proteins_df):,} proteins from compressed data")
                return proteins_df, summary_stats
                
            except Exception as e:
                st.sidebar.error(f"Error loading compressed data: {e}")
        
        # Try CSV fallback
        csv_path = Path(data_dir) / "proteins.csv"
        if csv_path.exists():
            try:
                proteins_df = pd.read_csv(csv_path)
                summary_stats = {
                    "total_proteins": len(proteins_df),
                    "druggable_proteins": len(proteins_df[proteins_df.get('druggable', False) == True]),
                    "high_priority": len(proteins_df[proteins_df.get('priority', '') == 'HIGH']),
                    "avg_druglikeness": proteins_df.get('druglikeness_score', pd.Series([0])).mean()
                }
                
                st.sidebar.warning(f"📊 Loaded {len(proteins_df):,} proteins from CSV")
                return proteins_df, summary_stats
                
            except Exception as e:
                st.sidebar.error(f"Error loading CSV: {e}")
    
    # No data found - create demo message
    st.sidebar.error("❌ No protein data files found")
    return pd.DataFrame(), {"total_proteins": 0, "druggable_proteins": 0, "high_priority": 0, "avg_druglikeness": 0}

def create_overview_metrics(summary_stats):
    """Create overview metrics cards"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{summary_stats.get('total_proteins', 0):,}</h3>
            <p>Total Proteins</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{summary_stats.get('druggable_proteins', 0):,}</h3>
            <p>Druggable Candidates</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{summary_stats.get('high_priority', 0):,}</h3>
            <p>High Priority</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{summary_stats.get('avg_druglikeness', 0):.3f}</h3>
            <p>Avg Druglikeness</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main dashboard application"""
    
    # Header
    st.title("🧬 Field of Truth Protein Discovery Dashboard")
    st.markdown("**Quantum-Enhanced Protein Discovery Analytics**")
    
    # Load data
    with st.spinner("Loading protein discovery data..."):
        proteins_df, summary_stats = load_data()
    
    if len(proteins_df) == 0:
        st.error("❌ No data available. Please ensure data files are present.")
        st.info("Expected files: `streamlit_dashboard/data/protein_discovery_data.json.gz` or `proteins.csv`")
        st.stop()
    
    # Overview metrics
    create_overview_metrics(summary_stats)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔬 Protein Analysis", "📥 Export"])
    
    with tab1:
        st.header("Discovery Overview")
        
        # Priority distribution
        if 'priority' in proteins_df.columns:
            priority_counts = proteins_df['priority'].value_counts()
            fig = px.pie(
                values=priority_counts.values,
                names=priority_counts.index,
                title="Priority Distribution",
                color_discrete_map={'HIGH': '#ff6b6b', 'MEDIUM': '#ffa726', 'LOW': '#66bb6a'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Druglikeness distribution
        if 'druglikeness_score' in proteins_df.columns:
            fig = px.histogram(
                proteins_df,
                x='druglikeness_score',
                nbins=50,
                title="Druglikeness Score Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Protein Analysis")
        
        # Show sample proteins
        if len(proteins_df) > 0:
            st.write(f"**Showing top proteins from {len(proteins_df):,} total discoveries**")
            
            # Display top proteins
            display_cols = ['sequence', 'length', 'druglikeness_score', 'priority']
            available_cols = [col for col in display_cols if col in proteins_df.columns]
            
            if available_cols:
                st.dataframe(proteins_df[available_cols].head(20))
            else:
                st.dataframe(proteins_df.head(20))
    
    with tab3:
        st.header("Data Export")
        
        if len(proteins_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                # Export high priority
                if 'priority' in proteins_df.columns:
                    high_priority = proteins_df[proteins_df['priority'] == 'HIGH']
                    if len(high_priority) > 0:
                        csv_data = high_priority.to_csv(index=False)
                        st.download_button(
                            label=f"Download High Priority ({len(high_priority):,} proteins)",
                            data=csv_data,
                            file_name=f"high_priority_proteins_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
            
            with col2:
                # Export druggable
                if 'druggable' in proteins_df.columns:
                    druggable = proteins_df[proteins_df['druggable'] == True]
                    if len(druggable) > 0:
                        csv_data = druggable.to_csv(index=False)
                        st.download_button(
                            label=f"Download Druggable ({len(druggable):,} proteins)",
                            data=csv_data,
                            file_name=f"druggable_proteins_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
    
    # Footer
    st.markdown("---")
    st.markdown("**Powered by Field of Truth (FoT) Quantum Protein Discovery System**")

if __name__ == "__main__":
    main()

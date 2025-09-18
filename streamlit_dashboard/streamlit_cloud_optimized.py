#!/usr/bin/env python3
"""
Streamlit Cloud Dashboard - Optimized for Static Data Loading
Field of Truth Protein Discovery Analytics
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
    .druggable-yes { color: #4caf50; font-weight: bold; }
    .druggable-no { color: #f44336; }
    .sidebar .stRadio > div { background-color: #f0f2f6; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_optimized_data():
    """Load the optimized exported data"""
    
    data_dir = Path("data")
    
    # Try to load compressed JSON first (most complete data)
    json_path = data_dir / "protein_discovery_data.json.gz"
    if json_path.exists():
        try:
            with gzip.open(json_path, 'rt') as f:
                data = json.load(f)
            
            proteins_df = pd.DataFrame(data['proteins'])
            summary_stats = data['summary_stats']
            export_metadata = data['export_metadata']
            
            st.sidebar.success("🔗 Loaded Compressed Full Dataset")
            return proteins_df, summary_stats, export_metadata
            
        except Exception as e:
            st.sidebar.error(f"Error loading compressed data: {e}")
    
    # Fallback to CSV
    csv_path = data_dir / "proteins.csv"
    if csv_path.exists():
        try:
            proteins_df = pd.read_csv(csv_path)
            
            # Calculate basic summary stats
            summary_stats = {
                "total_proteins": len(proteins_df),
                "druggable_proteins": len(proteins_df[proteins_df['druggable'] == True]),
                "high_priority": len(proteins_df[proteins_df['priority'] == 'HIGH']),
                "avg_druglikeness": proteins_df['druglikeness_score'].mean(),
                "therapeutic_classes": proteins_df['therapeutic_class'].unique().tolist(),
                "target_diseases": proteins_df['target_disease'].unique().tolist()
            }
            
            export_metadata = {
                "export_date": datetime.now().isoformat(),
                "source": "CSV Fallback",
                "processed_proteins": len(proteins_df)
            }
            
            st.sidebar.warning("📊 Loaded CSV Fallback Data")
            return proteins_df, summary_stats, export_metadata
            
        except Exception as e:
            st.sidebar.error(f"Error loading CSV data: {e}")
    
    # Last resort - load summary only
    summary_path = data_dir / "summary.json"
    if summary_path.exists():
        try:
            with open(summary_path, 'r') as f:
                data = json.load(f)
            
            proteins_df = pd.DataFrame(data['sample_proteins'])
            summary_stats = data['summary_stats']
            export_metadata = data['export_metadata']
            
            st.sidebar.warning("⚠️ Limited to Summary Data Only")
            return proteins_df, summary_stats, export_metadata
            
        except Exception as e:
            st.sidebar.error(f"Error loading summary data: {e}")
    
    # No data available
    st.sidebar.error("❌ No Data Files Found")
    return None, None, None

def create_overview_metrics(summary_stats):
    """Create overview metrics cards"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{summary_stats['total_proteins']:,}</h3>
            <p>Total Proteins</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{summary_stats['druggable_proteins']:,}</h3>
            <p>Druggable Candidates</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{summary_stats['high_priority']:,}</h3>
            <p>High Priority</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{summary_stats['avg_druglikeness']:.3f}</h3>
            <p>Avg Druglikeness</p>
        </div>
        """, unsafe_allow_html=True)

def create_priority_distribution_chart(df):
    """Create priority distribution chart"""
    
    priority_counts = df['priority'].value_counts()
    
    fig = px.pie(
        values=priority_counts.values,
        names=priority_counts.index,
        title="Discovery Priority Distribution",
        color_discrete_map={
            'HIGH': '#ff6b6b',
            'MEDIUM': '#ffa726', 
            'LOW': '#66bb6a'
        }
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    return fig

def create_druglikeness_histogram(df):
    """Create druglikeness score distribution"""
    
    fig = px.histogram(
        df,
        x='druglikeness_score',
        nbins=50,
        title="Druglikeness Score Distribution",
        labels={'druglikeness_score': 'Druglikeness Score', 'count': 'Number of Proteins'},
        color_discrete_sequence=['#667eea']
    )
    
    fig.add_vline(x=0.7, line_dash="dash", line_color="red", 
                  annotation_text="High Priority Threshold")
    fig.add_vline(x=0.5, line_dash="dash", line_color="orange",
                  annotation_text="Medium Priority Threshold")
    
    fig.update_layout(height=400)
    
    return fig

def create_therapeutic_class_chart(df):
    """Create therapeutic class distribution"""
    
    class_counts = df['therapeutic_class'].value_counts().head(10)
    
    fig = px.bar(
        x=class_counts.values,
        y=class_counts.index,
        orientation='h',
        title="Top 10 Therapeutic Classes",
        labels={'x': 'Number of Proteins', 'y': 'Therapeutic Class'},
        color=class_counts.values,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=500)
    
    return fig

def create_molecular_weight_vs_druglikeness(df):
    """Create scatter plot of molecular weight vs druglikeness"""
    
    # Sample for performance if dataset is large
    if len(df) > 10000:
        df_sample = df.sample(n=10000, random_state=42)
    else:
        df_sample = df
    
    fig = px.scatter(
        df_sample,
        x='molecular_weight',
        y='druglikeness_score',
        color='priority',
        size='validation_score',
        hover_data=['therapeutic_class', 'target_disease'],
        title="Molecular Weight vs Druglikeness Score",
        color_discrete_map={
            'HIGH': '#ff6b6b',
            'MEDIUM': '#ffa726', 
            'LOW': '#66bb6a'
        }
    )
    
    fig.update_layout(height=500)
    
    return fig

def create_quantum_coherence_analysis(df):
    """Create quantum coherence analysis"""
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Quantum Coherence Distribution", "Coherence vs Validation Score"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Histogram of quantum coherence
    fig.add_trace(
        go.Histogram(x=df['quantum_coherence'], name="Quantum Coherence", nbinsx=30),
        row=1, col=1
    )
    
    # Scatter plot of coherence vs validation
    df_sample = df.sample(n=min(5000, len(df)), random_state=42)
    fig.add_trace(
        go.Scatter(
            x=df_sample['quantum_coherence'],
            y=df_sample['validation_score'],
            mode='markers',
            name="Coherence vs Validation",
            marker=dict(
                size=4,
                color=df_sample['druglikeness_score'],
                colorscale='Viridis',
                showscale=True
            )
        ),
        row=1, col=2
    )
    
    fig.update_layout(height=400, title_text="Quantum Analysis Dashboard")
    
    return fig

def show_detailed_protein_view(df):
    """Show detailed protein information"""
    
    st.subheader("🔬 Detailed Protein Analysis")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        priority_filter = st.multiselect(
            "Priority Level:",
            options=['HIGH', 'MEDIUM', 'LOW'],
            default=['HIGH']
        )
    
    with col2:
        therapeutic_classes = df['therapeutic_class'].unique()
        class_filter = st.multiselect(
            "Therapeutic Class:",
            options=therapeutic_classes,
            default=therapeutic_classes[:3] if len(therapeutic_classes) > 3 else therapeutic_classes
        )
    
    with col3:
        min_druglikeness = st.slider(
            "Minimum Druglikeness:",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1
        )
    
    # Apply filters
    filtered_df = df[
        (df['priority'].isin(priority_filter)) &
        (df['therapeutic_class'].isin(class_filter)) &
        (df['druglikeness_score'] >= min_druglikeness)
    ]
    
    st.write(f"**Showing {len(filtered_df):,} proteins matching criteria**")
    
    # Display proteins with enhanced information
    for idx, protein in filtered_df.head(20).iterrows():
        with st.expander(f"🧬 {protein['protein_id']} - {protein['therapeutic_class']} (Priority: {protein['priority']})"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Basic Properties:**")
                st.write(f"- Length: {protein['length']} amino acids")
                st.write(f"- Molecular Weight: {protein['molecular_weight']:.1f} Da")
                st.write(f"- Druglikeness: {protein['druglikeness_score']:.3f}")
                st.write(f"- Validation Score: {protein['validation_score']:.3f}")
                
                st.write("**Therapeutic Information:**")
                st.write(f"- Class: {protein['therapeutic_class']}")
                st.write(f"- Target Disease: {protein['target_disease']}")
                st.write(f"- Binding Affinity: {protein['binding_affinity']}")
                st.write(f"- Selectivity: {protein['selectivity']}")
                st.write(f"- Stability: {protein['stability']}")
            
            with col2:
                st.write("**Quantum Properties:**")
                st.write(f"- Quantum Coherence: {protein['quantum_coherence']:.3f}")
                st.write(f"- Energy: {protein['energy_kcal_mol']:.2f} kcal/mol")
                
                st.write("**Structural Features:**")
                st.write(f"- Hydrophobic Fraction: {protein['hydrophobic_fraction']:.3f}")
                st.write(f"- Charged Residues: {protein['charged_residues']}")
                st.write(f"- Aromatic Residues: {protein['aromatic_residues']}")
                st.write(f"- Cysteine Bridges: {protein['cysteine_bridges']}")
            
            # Show sequence (truncated for display)
            sequence = protein['sequence']
            if len(sequence) > 100:
                st.write(f"**Sequence:** {sequence[:100]}... ({len(sequence)} total)")
            else:
                st.write(f"**Sequence:** {sequence}")
            
            # Simple 2D visualization of amino acid composition
            if len(sequence) > 0:
                aa_counts = {}
                for aa in sequence:
                    aa_counts[aa] = aa_counts.get(aa, 0) + 1
                
                if aa_counts:
                    fig = px.bar(
                        x=list(aa_counts.keys()),
                        y=list(aa_counts.values()),
                        title=f"Amino Acid Composition - {protein['protein_id']}",
                        labels={'x': 'Amino Acid', 'y': 'Count'}
                    )
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)

def create_export_section(df, summary_stats):
    """Create data export section"""
    
    st.subheader("📥 Data Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # High priority proteins
        high_priority = df[df['priority'] == 'HIGH']
        if len(high_priority) > 0:
            csv_data = high_priority.to_csv(index=False)
            st.download_button(
                label="Download High Priority Proteins",
                data=csv_data,
                file_name=f"high_priority_proteins_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        # Druggable proteins
        druggable = df[df['druggable'] == True]
        if len(druggable) > 0:
            csv_data = druggable.to_csv(index=False)
            st.download_button(
                label="Download Druggable Proteins",
                data=csv_data,
                file_name=f"druggable_proteins_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col3:
        # Summary report
        summary_json = json.dumps(summary_stats, indent=2)
        st.download_button(
            label="Download Summary Report",
            data=summary_json,
            file_name=f"discovery_summary_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

def main():
    """Main dashboard application"""
    
    # Header
    st.title("🧬 Field of Truth Protein Discovery Dashboard")
    st.markdown("**Optimized Analytics for Quantum-Enhanced Protein Discoveries**")
    
    # Load data
    with st.spinner("Loading optimized protein discovery data..."):
        proteins_df, summary_stats, export_metadata = load_optimized_data()
    
    if proteins_df is None:
        st.error("❌ No data available. Please ensure data files are present in the 'data' directory.")
        st.stop()
    
    # Sidebar information
    st.sidebar.markdown("### 📊 Dataset Information")
    st.sidebar.write(f"**Export Date:** {export_metadata.get('export_date', 'Unknown')[:10]}")
    st.sidebar.write(f"**Records:** {len(proteins_df):,}")
    st.sidebar.write(f"**Source:** {export_metadata.get('source', 'FoT System')}")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔬 Detailed Analysis", "📈 Advanced Analytics", "📥 Export"])
    
    with tab1:
        st.header("Discovery Overview")
        
        # Metrics
        create_overview_metrics(summary_stats)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_priority_distribution_chart(proteins_df), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_druglikeness_histogram(proteins_df), use_container_width=True)
        
        # Therapeutic class distribution
        st.plotly_chart(create_therapeutic_class_chart(proteins_df), use_container_width=True)
    
    with tab2:
        show_detailed_protein_view(proteins_df)
    
    with tab3:
        st.header("Advanced Analytics")
        
        # Molecular weight vs druglikeness
        st.plotly_chart(create_molecular_weight_vs_druglikeness(proteins_df), use_container_width=True)
        
        # Quantum analysis
        st.plotly_chart(create_quantum_coherence_analysis(proteins_df), use_container_width=True)
        
        # Statistical summary
        st.subheader("📈 Statistical Summary")
        st.dataframe(proteins_df.describe())
    
    with tab4:
        create_export_section(proteins_df, summary_stats)
    
    # Footer
    st.markdown("---")
    st.markdown("**Powered by Field of Truth (FoT) Quantum Protein Discovery System**")

if __name__ == "__main__":
    main()

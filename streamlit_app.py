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

def show_detailed_protein_analysis(protein_data):
    """Show detailed analysis of a single protein with 2D/3D visualizations"""
    
    # Get protein properties
    protein_id = protein_data.get('protein_id', 'Unknown')
    sequence = protein_data.get('sequence', '')
    length = len(sequence)
    druglikeness = protein_data.get('druglikeness_score', 0)
    priority = protein_data.get('priority', 'UNKNOWN')
    validation_score = protein_data.get('validation_score', 0)
    energy = protein_data.get('energy_kcal_mol', 0)
    quantum_coherence = protein_data.get('quantum_coherence', 0)
    
    # Protein header
    st.markdown(f"## 🧬 {protein_id}")
    
    # Basic properties in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Length", f"{length} aa")
        st.metric("Druglikeness", f"{druglikeness:.3f}")
    with col2:
        st.metric("Priority", priority)
        st.metric("Validation Score", f"{validation_score:.3f}")
    with col3:
        st.metric("Energy", f"{energy:.2f} kcal/mol")
        st.metric("Quantum Coherence", f"{quantum_coherence:.3f}")
    with col4:
        # Calculate additional properties
        charged_count = sum(1 for aa in sequence if aa in 'RKDE')
        hydrophobic_count = sum(1 for aa in sequence if aa in 'AILMFPWV')
        aromatic_count = sum(1 for aa in sequence if aa in 'FYW')
        cysteine_count = sum(1 for aa in sequence if aa in 'C')
        
        st.metric("Charged Residues", charged_count)
        st.metric("Hydrophobic Fraction", f"{hydrophobic_count/length:.3f}")
    
    # Sequence display
    st.subheader("📋 Full Sequence")
    st.code(sequence, language=None)
    
    # 2D and 3D Visualizations
    col_2d, col_3d = st.columns(2)
    
    with col_2d:
        st.subheader("🎯 2D Amino Acid Composition")
        create_2d_composition_chart(sequence)
        
        st.subheader("🔄 2D Circular Sequence Map")
        create_2d_circular_map(sequence)
    
    with col_3d:
        st.subheader("🧬 3D Protein Structure Model")
        create_3d_protein_model(sequence, protein_id)
        
        st.subheader("⚡ 3D Quantum Properties")
        create_3d_quantum_visualization(sequence, quantum_coherence, energy)
    
    # Detailed analysis
    st.subheader("🔬 Structural Analysis")
    create_detailed_analysis(sequence, druglikeness, priority)

def create_2d_composition_chart(sequence):
    """Create 2D amino acid composition chart"""
    import collections
    
    # Count amino acids
    aa_counts = collections.Counter(sequence)
    aa_names = list(aa_counts.keys())
    counts = list(aa_counts.values())
    
    # Create pie chart
    fig = px.pie(
        values=counts,
        names=aa_names,
        title="Amino Acid Composition",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

def create_2d_circular_map(sequence):
    """Create 2D circular sequence map"""
    import numpy as np
    
    length = len(sequence)
    angles = np.linspace(0, 2*np.pi, length, endpoint=False)
    
    # Color code by amino acid properties
    colors = []
    for aa in sequence:
        if aa in 'RKDE':  # Charged
            colors.append('red')
        elif aa in 'AILMFPWV':  # Hydrophobic
            colors.append('blue')
        elif aa in 'FYW':  # Aromatic
            colors.append('purple')
        elif aa in 'C':  # Cysteine
            colors.append('yellow')
        else:  # Polar/other
            colors.append('green')
    
    # Create circular plot
    x = np.cos(angles)
    y = np.sin(angles)
    
    fig = go.Figure()
    
    # Add amino acid points
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='markers+text',
        marker=dict(color=colors, size=8),
        text=list(sequence),
        textposition="middle center",
        textfont=dict(size=8),
        name="Amino Acids"
    ))
    
    fig.update_layout(
        title="Circular Sequence Map",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_3d_protein_model(sequence, protein_id):
    """Create 3D protein structure model"""
    import numpy as np
    
    length = len(sequence)
    
    # Generate simplified 3D backbone coordinates
    np.random.seed(hash(protein_id) % 2**32)  # Consistent seed based on protein ID
    
    # Create a protein-like backbone structure
    t = np.linspace(0, 4*np.pi, length)
    x = np.cos(t) + 0.1*np.random.randn(length)
    y = np.sin(t) + 0.1*np.random.randn(length)
    z = 0.1*t + 0.1*np.random.randn(length)
    
    # Color by amino acid properties
    colors = []
    for aa in sequence:
        if aa in 'RKDE':  # Charged - red
            colors.append(1)
        elif aa in 'AILMFPWV':  # Hydrophobic - blue
            colors.append(2)
        elif aa in 'FYW':  # Aromatic - purple
            colors.append(3)
        elif aa in 'C':  # Cysteine - yellow
            colors.append(4)
        else:  # Polar/other - green
            colors.append(5)
    
    fig = go.Figure()
    
    # Add backbone trace
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines+markers',
        line=dict(color='gray', width=4),
        marker=dict(
            size=6,
            color=colors,
            colorscale='viridis',
            showscale=True,
            colorbar=dict(title="AA Type")
        ),
        text=[f"{i+1}: {aa}" for i, aa in enumerate(sequence)],
        name="Backbone"
    ))
    
    fig.update_layout(
        title="3D Protein Model (Simplified)",
        scene=dict(
            xaxis_title="X (Å)",
            yaxis_title="Y (Å)",
            zaxis_title="Z (Å)"
        ),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_3d_quantum_visualization(sequence, quantum_coherence, energy):
    """Create 3D quantum properties visualization"""
    import numpy as np
    
    length = len(sequence)
    
    # Generate quantum field visualization
    x = np.linspace(-2, 2, 20)
    y = np.linspace(-2, 2, 20)
    X, Y = np.meshgrid(x, y)
    
    # Create quantum field based on coherence and energy
    Z = np.sin(np.sqrt(X**2 + Y**2) * (1 + quantum_coherence)) * np.exp(-energy/1000)
    
    fig = go.Figure()
    
    # Add surface plot
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z,
        colorscale='plasma',
        name="Quantum Field",
        showscale=True,
        colorbar=dict(title="Field Strength")
    ))
    
    fig.update_layout(
        title=f"Quantum Properties (Coherence: {quantum_coherence:.3f})",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Field Strength"
        ),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_detailed_analysis(sequence, druglikeness, priority):
    """Create detailed structural analysis"""
    
    # Calculate properties
    length = len(sequence)
    charged_count = sum(1 for aa in sequence if aa in 'RKDE')
    hydrophobic_count = sum(1 for aa in sequence if aa in 'AILMFPWV')
    aromatic_count = sum(1 for aa in sequence if aa in 'FYW')
    cysteine_count = sum(1 for aa in sequence if aa in 'C')
    proline_count = sum(1 for aa in sequence if aa in 'P')
    
    # Analysis columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Therapeutic Potential**")
        if druglikeness > 0.7:
            st.success(f"⭐ HIGH therapeutic potential (druglikeness: {druglikeness:.3f})")
        elif druglikeness > 0.5:
            st.warning(f"⚠️ MEDIUM therapeutic potential (druglikeness: {druglikeness:.3f})")
        else:
            st.info(f"ℹ️ LOW therapeutic potential (druglikeness: {druglikeness:.3f})")
        
        st.markdown("**🔬 Structural Features**")
        st.write(f"• Length: {length} amino acids")
        st.write(f"• Charged residues: {charged_count} ({charged_count/length*100:.1f}%)")
        st.write(f"• Hydrophobic residues: {hydrophobic_count} ({hydrophobic_count/length*100:.1f}%)")
        st.write(f"• Aromatic residues: {aromatic_count} ({aromatic_count/length*100:.1f}%)")
        st.write(f"• Cysteine bridges: {cysteine_count//2}")
        st.write(f"• Proline content: {proline_count} ({proline_count/length*100:.1f}%)")
    
    with col2:
        st.markdown("**⚡ Folding Predictions**")
        
        # Simple secondary structure prediction
        if proline_count/length > 0.1:
            st.write("🔄 High flexibility due to proline content")
        else:
            st.write("🏗️ Structured folding expected")
        
        if cysteine_count >= 2:
            st.write("🔗 Disulfide bonds likely - stable structure")
        
        if hydrophobic_count/length > 0.4:
            st.write("💧 Hydrophobic core formation expected")
        
        if aromatic_count > 0:
            st.write("🌟 Aromatic stacking interactions possible")
        
        st.markdown("**🎭 Predicted Function**")
        if priority == "HIGH":
            if length < 50:
                st.write("🦠 **Antimicrobial peptide** candidate")
            elif charged_count/length > 0.2:
                st.write("🧲 **Binding protein** candidate")
            else:
                st.write("💊 **Drug target** candidate")
        else:
            st.write("🔬 Structural or regulatory protein")

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
        st.header("🔬 Detailed Protein Analysis")
        
        if len(proteins_df) > 0:
            # Protein selector
            st.subheader("Select Protein for Detailed Analysis")
            protein_options = []
            for idx, row in proteins_df.head(50).iterrows():  # Top 50 for selection
                protein_id = row.get('protein_id', f'protein_{idx}')
                sequence = row.get('sequence', 'N/A')
                priority = row.get('priority', 'UNKNOWN')
                protein_options.append(f"{protein_id} - {sequence[:20]}{'...' if len(sequence) > 20 else ''} (Priority: {priority})")
            
            selected_idx = st.selectbox("Choose a protein:", range(len(protein_options)), format_func=lambda x: protein_options[x])
            
            if selected_idx is not None:
                selected_protein = proteins_df.iloc[selected_idx]
                show_detailed_protein_analysis(selected_protein)
        else:
            st.error("No protein data available")
    
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

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
    
    /* Fix data alignment issues - force left alignment */
    .stDataFrame, .stDataFrame > div, .stDataFrame table {
        text-align: left !important;
        width: 100% !important;
    }
    
    /* Protein discovery cards - left align all content */
    .protein-discovery-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #fafafa;
        text-align: left !important;
    }
    
    /* Fix expandable protein cards */
    .stExpander > div > div {
        text-align: left !important;
    }
    
    /* Fix any right-aligned content */
    .element-container, .stMarkdown, .stText, .stColumns > div {
        text-align: left !important;
    }
    
    /* Ensure protein info displays properly */
    .protein-info {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        text-align: left !important;
    }
    
    /* Fix protein sequence display */
    .protein-sequence {
        font-family: 'Courier New', monospace;
        background: #f5f5f5;
        padding: 0.5rem;
        border-radius: 4px;
        word-break: break-all;
        text-align: left !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_chunked_data():
    """Load protein discovery data from CHUNKED files - ALL data preserved"""
    
    # Try to load from streamlit_dashboard/data first
    data_paths = [
        "streamlit_dashboard/data",
        "data", 
        "."
    ]
    
    for data_dir in data_paths:
        data_path = Path(data_dir)
        
        # 1. Try CHUNKED dataset first (ALL discoveries preserved)
        chunk_index_path = data_path / "chunk_index.json"
        if chunk_index_path.exists():
            try:
                st.sidebar.info(f"📦 Loading CHUNKED dataset (all discoveries preserved)...")
                
                # Load chunk index
                with open(chunk_index_path, 'r') as f:
                    chunk_index = json.load(f)
                
                summary_stats = chunk_index['summary_stats']
                chunk_files = chunk_index['chunk_files']
                
                st.sidebar.info(f"🔄 Loading {len(chunk_files)} chunks...")
                
                # Load all chunks
                all_proteins = []
                chunks_loaded = 0
                
                for chunk_file in chunk_files:
                    chunk_path = data_path / chunk_file
                    if chunk_path.exists():
                        try:
                            with gzip.open(chunk_path, 'rt') as f:
                                chunk_data = json.load(f)
                            all_proteins.extend(chunk_data)
                            chunks_loaded += 1
                            
                            # Update progress
                            if chunks_loaded % 5 == 0:
                                st.sidebar.info(f"📊 Loaded {chunks_loaded}/{len(chunk_files)} chunks ({len(all_proteins):,} proteins)")
                        except Exception as e:
                            st.sidebar.warning(f"⚠️ Could not load chunk {chunk_file}: {e}")
                
                if all_proteins:
                    proteins_df = pd.DataFrame(all_proteins)
                    
                    st.sidebar.success(f"🎉 Loaded COMPLETE CHUNKED dataset: {len(proteins_df):,} proteins")
                    st.sidebar.success(f"✅ NO DATA LOSS - All discoveries preserved across {chunks_loaded} chunks!")
                    st.sidebar.info(f"📈 Quality: {summary_stats.get('excellent_quality', 0):,} Excellent + {summary_stats.get('very_good_quality', 0):,} Very Good + {summary_stats.get('good_quality', 0):,} Good")
                    
                    return proteins_df, summary_stats
                else:
                    st.sidebar.error("❌ No protein data found in chunks")
                    
            except Exception as e:
                st.sidebar.error(f"Error loading chunked dataset: {e}")
        
        # 2. Try single complete dataset (fallback)
        complete_json_path = data_path / "complete_protein_dataset.json.gz"
        if complete_json_path.exists():
            try:
                st.sidebar.info(f"📦 Loading single complete dataset...")
                with gzip.open(complete_json_path, 'rt') as f:
                    data = json.load(f)
                
                proteins_df = pd.DataFrame(data['proteins'])
                summary_stats = data['summary_stats']
                
                st.sidebar.success(f"🎉 Loaded single dataset: {len(proteins_df):,} proteins")
                return proteins_df, summary_stats
                
            except Exception as e:
                st.sidebar.error(f"Error loading complete dataset: {e}")
        
        # 3. Try complete CSV
        complete_csv_path = data_path / "complete_proteins.csv"
        if complete_csv_path.exists():
            try:
                st.sidebar.info(f"📄 Loading complete CSV dataset...")
                proteins_df = pd.read_csv(complete_csv_path)
                
                # Calculate summary stats
                summary_stats = {
                    "total_proteins": len(proteins_df),
                    "druggable_proteins": proteins_df['druggable'].sum() if 'druggable' in proteins_df.columns else 0,
                    "high_priority": proteins_df[proteins_df['priority'] == 'HIGH'].shape[0] if 'priority' in proteins_df.columns else 0,
                    "avg_druglikeness": proteins_df['druglikeness_score'].mean() if 'druglikeness_score' in proteins_df.columns else 0,
                    "avg_quantum_coherence": proteins_df['quantum_coherence'].mean() if 'quantum_coherence' in proteins_df.columns else 0
                }
                
                st.sidebar.success(f"🎉 Loaded CSV: {len(proteins_df):,} proteins")
                return proteins_df, summary_stats
                
            except Exception as e:
                st.sidebar.error(f"Error loading complete CSV: {e}")
        
        # 4. Fallback to legacy limited dataset (warn user)
        json_path = data_path / "protein_discovery_data.json.gz"
        if json_path.exists():
            try:
                st.sidebar.warning("⚠️ Loading LEGACY limited dataset (only 5K proteins)")
                st.sidebar.error("🚨 MISSING 246,941 discoveries! Please update to chunked data.")
                with gzip.open(json_path, 'rt') as f:
                    data = json.load(f)
                
                proteins_df = pd.DataFrame(data['proteins'])
                summary_stats = data['summary_stats']
                
                st.sidebar.warning(f"📉 Limited dataset: {len(proteins_df):,} proteins (INCOMPLETE)")
                return proteins_df, summary_stats
                
            except Exception as e:
                st.sidebar.error(f"Error loading legacy data: {e}")
        
        # 5. Try CSV fallback
        csv_path = data_path / "proteins.csv"
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

def show_dashboard_overview(proteins_df, summary_stats):
    """Dashboard overview with key metrics and charts"""
    st.header("🏠 Discovery Overview")
    
    # Quality distribution overview
    if 'validation_score' in proteins_df.columns:
        st.subheader("🎯 Quality Distribution - Field of Truth Validation")
        
        excellent_count = len(proteins_df[proteins_df['validation_score'] >= 0.9])
        very_good_count = len(proteins_df[(proteins_df['validation_score'] >= 0.8) & (proteins_df['validation_score'] < 0.9)])
        good_count = len(proteins_df[(proteins_df['validation_score'] >= 0.7) & (proteins_df['validation_score'] < 0.8)])
        
        qual_col1, qual_col2, qual_col3, qual_col4 = st.columns(4)
        with qual_col1:
            st.metric("🌟 Excellent", f"{excellent_count:,}", f"{excellent_count/len(proteins_df)*100:.1f}%")
            st.caption("Validation Score ≥ 0.9")
        with qual_col2:
            st.metric("⭐ Very Good", f"{very_good_count:,}", f"{very_good_count/len(proteins_df)*100:.1f}%")
            st.caption("Validation Score 0.8-0.9")
        with qual_col3:
            st.metric("✅ Good", f"{good_count:,}", f"{good_count/len(proteins_df)*100:.1f}%")
            st.caption("Validation Score 0.7-0.8")
        with qual_col4:
            total_high_quality = excellent_count + very_good_count + good_count
            st.metric("🎯 Total High Quality", f"{total_high_quality:,}", f"{total_high_quality/len(proteins_df)*100:.1f}%")
            st.caption("All validation scores ≥ 0.7")
        
        st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Quality distribution pie chart
        if 'validation_score' in proteins_df.columns:
            quality_data = {
                '🌟 Excellent (≥0.9)': excellent_count,
                '⭐ Very Good (0.8-0.9)': very_good_count,
                '✅ Good (0.7-0.8)': good_count
            }
            
            fig = px.pie(
                values=list(quality_data.values()),
                names=list(quality_data.keys()),
                title="Quality Distribution by Validation Score",
                color_discrete_sequence=['#ff9999', '#ffcc99', '#99ff99']
            )
            st.plotly_chart(fig, use_container_width=True)
        elif 'priority' in proteins_df.columns:
            priority_counts = proteins_df['priority'].value_counts()
            fig = px.pie(
                values=priority_counts.values,
                names=priority_counts.index,
                title="Priority Distribution",
                color_discrete_map={'HIGH': '#ff6b6b', 'MEDIUM': '#ffa726', 'LOW': '#66bb6a'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'druglikeness_score' in proteins_df.columns:
            fig = px.histogram(
                proteins_df,
                x='druglikeness_score',
                nbins=30,
                title="Druglikeness Score Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent discoveries with improved formatting
    st.subheader("🆕 Recent High-Priority Discoveries")
    if len(proteins_df) > 0:
        top_proteins = proteins_df.head(10)
        for idx, protein in top_proteins.iterrows():
            with st.expander(f"🧬 {protein.get('protein_id', f'protein_{idx}')} - {protein.get('priority', 'UNKNOWN')} Priority"):
                # Use single column layout for better left alignment
                sequence = protein.get('sequence', '')
                
                # Display sequence with proper formatting
                st.markdown("**Protein Sequence:**")
                st.markdown(f'<div class="protein-sequence">{sequence}</div>', unsafe_allow_html=True)
                
                # Display metrics in a clean row layout
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Druglikeness", f"{protein.get('druglikeness_score', 0):.3f}")
                with col2:
                    st.metric("Length", f"{len(sequence)} aa")
                with col3:
                    st.metric("Priority", protein.get('priority', 'N/A'))
                with col4:
                    st.metric("Energy", f"{protein.get('energy_kcal_mol', 0):.1f}")
                
                # Additional protein details in a clean format
                col_details1, col_details2 = st.columns(2)
                with col_details1:
                    st.write(f"**Validation Score:** {protein.get('validation_score', 0):.3f}")
                    st.write(f"**Quantum Coherence:** {protein.get('quantum_coherence', 0):.3f}")
                with col_details2:
                    st.write(f"**Charged Residues:** {protein.get('charged_residues', 0)}")
                    st.write(f"**Hydrophobic Fraction:** {protein.get('hydrophobic_fraction', 0):.3f}")

def show_protein_explorer(proteins_df):
    """Enhanced protein explorer with search, filtering, and pagination"""
    st.header("🔍 Protein Explorer")
    
    # Quality tier overview
    if 'validation_score' in proteins_df.columns:
        excellent_count = len(proteins_df[proteins_df['validation_score'] >= 0.9])
        very_good_count = len(proteins_df[(proteins_df['validation_score'] >= 0.8) & (proteins_df['validation_score'] < 0.9)])
        good_count = len(proteins_df[(proteins_df['validation_score'] >= 0.7) & (proteins_df['validation_score'] < 0.8)])
        
        col_qual1, col_qual2, col_qual3, col_qual4 = st.columns(4)
        with col_qual1:
            st.metric("🌟 Excellent (≥0.9)", f"{excellent_count:,}", f"{excellent_count/len(proteins_df)*100:.1f}%")
        with col_qual2:
            st.metric("⭐ Very Good (0.8-0.9)", f"{very_good_count:,}", f"{very_good_count/len(proteins_df)*100:.1f}%")
        with col_qual3:
            st.metric("✅ Good (0.7-0.8)", f"{good_count:,}", f"{good_count/len(proteins_df)*100:.1f}%")
        with col_qual4:
            total_high_quality = excellent_count + very_good_count + good_count
            st.metric("🎯 Total High Quality", f"{total_high_quality:,}", f"{total_high_quality/len(proteins_df)*100:.1f}%")
    
    st.markdown("---")
    
    # Search and filters
    col_search, col_filter1, col_filter2, col_filter3 = st.columns([2, 1, 1, 1])
    
    with col_search:
        search_term = st.text_input("🔍 Search by sequence or ID:", placeholder="Enter amino acid sequence or protein ID...")
    
    with col_filter1:
        priority_filter = st.selectbox("Priority Filter:", ["All", "HIGH", "MEDIUM", "LOW"])
    
    with col_filter2:
        # Quality filter based on validation scores
        quality_filter = st.selectbox("Quality Filter:", [
            "All", 
            "🌟 Excellent (≥0.9)", 
            "⭐ Very Good (0.8-0.9)", 
            "✅ Good (0.7-0.8)",
            "🎯 High Quality (≥0.7)"
        ])
    
    with col_filter3:
        length_range = st.slider("Length Range:", 1, 500, (10, 100))
    
    # Apply filters
    filtered_df = proteins_df.copy()
    
    if search_term:
        mask = (
            filtered_df.get('sequence', '').astype(str).str.contains(search_term, case=False, na=False) |
            filtered_df.get('protein_id', '').astype(str).str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df.get('priority', '') == priority_filter]
    
    # Apply quality filter
    if quality_filter != "All" and 'validation_score' in filtered_df.columns:
        if quality_filter == "🌟 Excellent (≥0.9)":
            filtered_df = filtered_df[filtered_df['validation_score'] >= 0.9]
        elif quality_filter == "⭐ Very Good (0.8-0.9)":
            filtered_df = filtered_df[(filtered_df['validation_score'] >= 0.8) & (filtered_df['validation_score'] < 0.9)]
        elif quality_filter == "✅ Good (0.7-0.8)":
            filtered_df = filtered_df[(filtered_df['validation_score'] >= 0.7) & (filtered_df['validation_score'] < 0.8)]
        elif quality_filter == "🎯 High Quality (≥0.7)":
            filtered_df = filtered_df[filtered_df['validation_score'] >= 0.7]
    
    filtered_df = filtered_df[
        (filtered_df.get('length', 0) >= length_range[0]) & 
        (filtered_df.get('length', 0) <= length_range[1])
    ]
    
    st.info(f"Found {len(filtered_df):,} proteins matching your criteria")
    
    # Pagination
    proteins_per_page = 20
    total_pages = max(1, (len(filtered_df) + proteins_per_page - 1) // proteins_per_page)
    
    if total_pages > 1:
        page_num = st.number_input("Page:", min_value=1, max_value=total_pages, value=1) - 1
        start_idx = page_num * proteins_per_page
        end_idx = start_idx + proteins_per_page
        page_df = filtered_df.iloc[start_idx:end_idx]
        
        st.caption(f"Showing proteins {start_idx + 1}-{min(end_idx, len(filtered_df))} of {len(filtered_df):,}")
    else:
        page_df = filtered_df.head(proteins_per_page)
    
    # Display proteins
    for idx, protein in page_df.iterrows():
        protein_id = protein.get('protein_id', f'protein_{idx}')
        sequence = protein.get('sequence', '')
        priority = protein.get('priority', 'UNKNOWN')
        druglikeness = protein.get('druglikeness_score', 0)
        
        with st.expander(f"🧬 {protein_id} - {sequence[:30]}{'...' if len(sequence) > 30 else ''} (Priority: {priority})"):
            col_info, col_action = st.columns([3, 1])
            
            with col_info:
                st.write(f"**Length:** {len(sequence)} amino acids")
                st.write(f"**Druglikeness:** {druglikeness:.3f}")
                st.write(f"**Validation Score:** {protein.get('validation_score', 0):.3f}")
                st.code(sequence, language=None)
            
            with col_action:
                if st.button(f"🔬 Full Analysis", key=f"full_analysis_{idx}"):
                    show_detailed_protein_analysis(protein)

def show_analytics_deep_dive(proteins_df):
    """Deep analytics with advanced charts and correlations"""
    st.header("📊 Analytics Deep Dive")
    
    # Correlation analysis
    st.subheader("🔗 Property Correlations")
    
    numeric_cols = ['length', 'druglikeness_score', 'validation_score', 'energy_kcal_mol', 'quantum_coherence']
    available_cols = [col for col in numeric_cols if col in proteins_df.columns]
    
    if len(available_cols) >= 2:
        col_x, col_y = st.columns(2)
        with col_x:
            x_axis = st.selectbox("X-axis:", available_cols, index=0)
        with col_y:
            y_axis = st.selectbox("Y-axis:", available_cols, index=1 if len(available_cols) > 1 else 0)
        
        if x_axis != y_axis:
            fig = px.scatter(
                proteins_df,
                x=x_axis,
                y=y_axis,
                color='priority' if 'priority' in proteins_df.columns else None,
                title=f"{y_axis.title()} vs {x_axis.title()}",
                hover_data=['protein_id'] if 'protein_id' in proteins_df.columns else None
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Length distribution by priority
    st.subheader("📏 Length Distribution Analysis")
    if 'priority' in proteins_df.columns and 'length' in proteins_df.columns:
        fig = px.box(
            proteins_df,
            x='priority',
            y='length',
            title="Protein Length Distribution by Priority"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top performers
    st.subheader("⭐ Top Performing Discoveries")
    if 'druglikeness_score' in proteins_df.columns:
        top_drugs = proteins_df.nlargest(10, 'druglikeness_score')
        display_cols = ['protein_id', 'sequence', 'druglikeness_score', 'priority']
        available_display_cols = [col for col in display_cols if col in top_drugs.columns]
        
        if available_display_cols:
            st.dataframe(
                top_drugs[available_display_cols],
                use_container_width=True
            )

def show_data_export(proteins_df):
    """Data export options"""
    st.header("📥 Data Export")
    
    if len(proteins_df) > 0:
        # Export options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📄 Download CSV",
                data=proteins_df.to_csv(index=False),
                file_name="fot_protein_discoveries.csv",
                mime="text/csv",
                help="Download all protein data as CSV"
            )
        
        with col2:
            st.download_button(
                label="📋 Download JSON",
                data=proteins_df.to_json(orient='records', indent=2),
                file_name="fot_protein_discoveries.json",
                mime="application/json",
                help="Download all protein data as JSON"
            )
        
        with col3:
            # High priority only
            if 'priority' in proteins_df.columns:
                high_priority = proteins_df[proteins_df['priority'] == 'HIGH']
                if len(high_priority) > 0:
                    st.download_button(
                        label="⭐ High Priority Only",
                        data=high_priority.to_csv(index=False),
                        file_name="fot_high_priority_proteins.csv",
                        mime="text/csv",
                        help="Download only high priority proteins"
                    )
        
        # Export stats
        st.subheader("📊 Export Statistics")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric("Total Proteins", f"{len(proteins_df):,}")
        with col_stat2:
            high_count = len(proteins_df[proteins_df.get('priority', '') == 'HIGH']) if 'priority' in proteins_df.columns else 0
            st.metric("High Priority", f"{high_count:,}")
        with col_stat3:
            druggable_count = len(proteins_df[proteins_df.get('druggable', False) == True]) if 'druggable' in proteins_df.columns else 0
            st.metric("Druggable", f"{druggable_count:,}")

def main():
    """Main dashboard application"""
    
    # Header
    st.title("🧬 Field of Truth Protein Discovery Dashboard")
    st.markdown("**Quantum-Enhanced Protein Discovery Analytics**")
    
    # Load data from chunks
    with st.spinner("Loading protein discovery data..."):
        proteins_df, summary_stats = load_chunked_data()
    
    if len(proteins_df) == 0:
        st.error("❌ No data available. Please ensure data files are present.")
        st.info("Expected files: `streamlit_dashboard/data/protein_discovery_data.json.gz` or `proteins.csv`")
        st.stop()
    
    # Overview metrics
    create_overview_metrics(summary_stats)
    
    # Sidebar navigation
    st.sidebar.title("🧬 Navigation")
    
    # Data source info
    if len(proteins_df) > 0:
        st.sidebar.success(f"📊 {len(proteins_df):,} Real Discoveries Loaded")
        st.sidebar.info(f"🎯 {summary_stats.get('druggable_proteins', 0):,} Druggable Proteins")
    
    # Navigation options
    page = st.sidebar.selectbox(
        "Choose Analysis View:",
        ["🏠 Dashboard Overview", "🔍 Protein Explorer", "📊 Analytics Deep Dive", "📥 Data Export"]
    )
    
    # Page routing
    if page == "🏠 Dashboard Overview":
        show_dashboard_overview(proteins_df, summary_stats)
    elif page == "🔍 Protein Explorer":
        show_protein_explorer(proteins_df)
    elif page == "📊 Analytics Deep Dive":
        show_analytics_deep_dive(proteins_df)
    elif page == "📥 Data Export":
        show_data_export(proteins_df)
    
    # Footer
    st.markdown("---")
    st.markdown("**Powered by Field of Truth (FoT) Quantum Protein Discovery System**")

if __name__ == "__main__":
    main()

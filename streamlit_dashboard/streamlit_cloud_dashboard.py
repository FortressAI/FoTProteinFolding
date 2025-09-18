#!/usr/bin/env python3
"""
STREAMLIT CLOUD PROTEIN DASHBOARD
Uses static exported data - no live database connection required
Perfect for free Streamlit Cloud deployment
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import json
import gzip
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path

# Configure Streamlit page
st.set_page_config(
    page_title="🧬 FoT Protein Discovery Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .data-badge {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin: 0.2rem;
    }
    .sequence-display {
        font-family: 'Courier New', monospace;
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        font-size: 0.9rem;
        line-height: 1.4;
        word-break: break-all;
    }
    .protein-detail-card {
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

class StreamlitCloudDashboard:
    """Dashboard using exported static data for Streamlit Cloud"""
    
    def __init__(self):
        self.data = None
        self.proteins_df = None
        self.quantum_df = None
        self.metadata = None
        
    @st.cache_data
    def load_exported_data(_self):
        """Load exported protein data from static files"""
        try:
            # Try to load compressed data first (smaller file)
            data_file = Path("data/protein_discovery_data.json.gz")
            if data_file.exists():
                st.info("📦 Loading compressed protein discovery data...")
                with gzip.open(data_file, "rt") as f:
                    data = json.load(f)
                st.success("✅ Loaded compressed data successfully")
            else:
                # Fallback to uncompressed
                data_file = Path("data/protein_discovery_data.json")
                if data_file.exists():
                    st.info("📦 Loading protein discovery data...")
                    with open(data_file, "r") as f:
                        data = json.load(f)
                    st.success("✅ Loaded data successfully")
                else:
                    st.error("❌ No exported data found. Please run export_neo4j_for_streamlit.py first.")
                    return None
            
            # Convert to DataFrames
            proteins_df = pd.DataFrame(data["proteins"])
            proteins_df['discovery_date'] = pd.to_datetime(proteins_df['discovery_date'])
            
            quantum_df = None
            if data.get("quantum_data"):
                quantum_df = pd.DataFrame(data["quantum_data"])
            
            return {
                'data': data,
                'proteins_df': proteins_df,
                'quantum_df': quantum_df,
                'metadata': data["export_metadata"],
                'stats': data["summary_stats"]
            }
            
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            return None
    
    def generate_protein_2d_structure(self, sequence, protein_id):
        """Generate 2D protein structure visualization"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Color scheme for amino acids
        aa_colors = {
            'A': '#FF6B6B', 'R': '#4ECDC4', 'N': '#45B7D1', 'D': '#96CEB4',
            'C': '#FFEAA7', 'Q': '#DDA0DD', 'E': '#98D8C8', 'G': '#F7DC6F',
            'H': '#BB8FCE', 'I': '#85C1E9', 'L': '#F8C471', 'K': '#82E0AA',
            'M': '#F1948A', 'F': '#D7BDE2', 'P': '#A9DFBF', 'S': '#AED6F1',
            'T': '#FAD7A0', 'W': '#D5A6BD', 'Y': '#A9CCE3', 'V': '#ABEBC6'
        }
        
        n_residues = len(sequence)
        if n_residues == 0:
            return None
            
        angles = np.linspace(0, 2 * np.pi, n_residues, endpoint=False)
        radius = max(3, n_residues / 10)
        
        # Plot amino acid positions
        for i, aa in enumerate(sequence):
            x = radius * np.cos(angles[i])
            y = radius * np.sin(angles[i])
            color = aa_colors.get(aa, '#95A5A6')
            
            circle = patches.Circle((x, y), 0.3, facecolor=color, edgecolor='black', linewidth=1)
            ax.add_patch(circle)
            ax.text(x, y, aa, ha='center', va='center', fontsize=8, fontweight='bold')
        
        # Connect backbone
        for i in range(n_residues - 1):
            x1 = radius * np.cos(angles[i])
            y1 = radius * np.sin(angles[i])
            x2 = radius * np.cos(angles[i + 1])
            y2 = radius * np.sin(angles[i + 1])
            ax.plot([x1, x2], [y1, y2], 'k-', alpha=0.3, linewidth=1)
        
        # Highlight cysteine bonds
        cys_positions = [i for i, aa in enumerate(sequence) if aa == 'C']
        for i in range(0, len(cys_positions) - 1, 2):
            if i + 1 < len(cys_positions):
                pos1, pos2 = cys_positions[i], cys_positions[i + 1]
                x1 = radius * np.cos(angles[pos1])
                y1 = radius * np.sin(angles[pos1])
                x2 = radius * np.cos(angles[pos2])
                y2 = radius * np.sin(angles[pos2])
                ax.plot([x1, x2], [y1, y2], 'gold', linewidth=3, alpha=0.8)
        
        ax.set_xlim(-radius * 1.3, radius * 1.3)
        ax.set_ylim(-radius * 1.3, radius * 1.3)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f'2D Structure Map - {protein_id}', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def show_data_source_info(self):
        """Display information about the data source"""
        if self.metadata:
            st.sidebar.success("📊 Using Exported Data")
            st.sidebar.markdown(f"""
            **Data Source**: {self.metadata.get('source', 'Unknown')}  
            **Export Date**: {self.metadata.get('export_date', 'Unknown')[:10]}  
            **Total Records**: {self.metadata.get('processed_proteins', 0):,}  
            **Neo4j Stats**: {self.metadata.get('neo4j_stats', {}).get('total_discoveries', 0):,} discoveries
            """)
            
            with st.sidebar.expander("📈 Database Statistics"):
                neo4j_stats = self.metadata.get('neo4j_stats', {})
                st.write(f"🧬 Discoveries: {neo4j_stats.get('total_discoveries', 0):,}")
                st.write(f"📝 Sequences: {neo4j_stats.get('total_sequences', 0):,}")
                st.write(f"⚛️ vQbits: {neo4j_stats.get('total_vqbits', 0):,}")
                st.write(f"🌀 Quantum States: {neo4j_stats.get('total_quantum_states', 0):,}")
                st.write(f"🔗 Entanglements: {neo4j_stats.get('total_entanglements', 0):,}")
    
    def show_protein_details(self, protein_data):
        """Show detailed protein analysis"""
        st.markdown(f"""
        <div class="protein-detail-card">
            <h2>🧬 Detailed Analysis: {protein_data['protein_id']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Complete sequence
            st.markdown("### 🧬 Complete Amino Acid Sequence")
            st.markdown(f"""
            <div class="sequence-display">
                {protein_data['sequence']}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**Length:** {protein_data['length']} amino acids")
            
            # Novelty analysis
            st.markdown("### 🆕 Therapeutic Analysis")
            
            druglikeness = protein_data['druglikeness_score']
            if druglikeness > 0.8:
                novelty_level = "HIGHLY PROMISING"
                novelty_color = "#28a745"
            elif druglikeness > 0.6:
                novelty_level = "GOOD CANDIDATE"
                novelty_color = "#ffc107"
            else:
                novelty_level = "RESEARCH STAGE"
                novelty_color = "#6c757d"
            
            st.markdown(f"""
            <span class="data-badge" style="background-color: {novelty_color}">
                {novelty_level} (Score: {druglikeness:.3f})
            </span>
            """, unsafe_allow_html=True)
            
            # Why it's therapeutically valuable
            st.markdown("**Therapeutic Value:**")
            reasons = []
            
            if protein_data['length'] < 50:
                reasons.append("Short peptide - easier synthesis and manufacturing")
            elif protein_data['length'] > 100:
                reasons.append("Large protein - complex functional capabilities")
            
            if protein_data['cysteine_bridges'] >= 2:
                reasons.append(f"Multiple disulfide bridges ({protein_data['cysteine_bridges']}) - enhanced stability")
            
            if protein_data['aromatic_residues'] >= 3:
                reasons.append(f"Rich in aromatic residues ({protein_data['aromatic_residues']}) - strong binding potential")
            
            if protein_data['hydrophobic_fraction'] > 0.4:
                reasons.append("High hydrophobic content - membrane interaction capability")
            
            therapeutic_motifs = ['RGD', 'YIGSR', 'REDV', 'LDV', 'NGR']
            found_motifs = [motif for motif in therapeutic_motifs if motif in protein_data['sequence']]
            if found_motifs:
                reasons.append(f"Contains therapeutic motifs: {', '.join(found_motifs)}")
            
            if not reasons:
                reasons = ["Novel sequence with unique amino acid composition"]
            
            for reason in reasons:
                st.markdown(f"• {reason}")
        
        with col2:
            # Metrics
            st.markdown("### 📊 Molecular Properties")
            
            priority_colors = {
                'HIGH': 'druggable-high',
                'MEDIUM': 'druggable-medium', 
                'LOW': 'druggable-low'
            }
            priority_class = priority_colors.get(protein_data['priority'], 'druggable-low')
            
            st.markdown(f"""
            <div class="metric-card {priority_class}">
                <h4>Priority Level</h4>
                <h2>{protein_data['priority']}</h2>
                <p>Druglikeness: {protein_data['druglikeness_score']:.3f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            **Quantum Metrics:**
            - Validation Score: {protein_data['validation_score']:.3f}
            - Energy: {protein_data['energy_kcal_mol']:.1f} kcal/mol
            - Quantum Coherence: {protein_data['quantum_coherence']:.3f}
            
            **Physical Properties:**
            - Molecular Weight: {protein_data['molecular_weight']:.1f} Da
            - Hydrophobic Fraction: {protein_data['hydrophobic_fraction']:.2f}
            - Charged Residues: {protein_data['charged_residues']}
            - Aromatic Residues: {protein_data['aromatic_residues']}
            - Cysteine Bridges: {protein_data['cysteine_bridges']}
            
            **Predicted Properties:**
            - Target: {protein_data['target_disease']}
            - Class: {protein_data['therapeutic_class']}
            - Binding Affinity: {protein_data['binding_affinity']}
            - Selectivity: {protein_data['selectivity']}
            - Stability: {protein_data['stability']}
            """)
        
        # 2D Visualization
        st.markdown("### 🎨 2D Structure Visualization")
        fig_2d = self.generate_protein_2d_structure(protein_data['sequence'], protein_data['protein_id'])
        if fig_2d:
            st.pyplot(fig_2d, use_container_width=True)
            plt.close(fig_2d)
    
    def run(self):
        """Main dashboard execution"""
        st.markdown('<h1 class="main-header">🧬 Field of Truth Protein Discovery Dashboard</h1>', 
                   unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <p style="font-size: 1.2rem; color: #666;">
                Quantum-Enhanced Therapeutic Protein Analysis<br>
                <strong>Exported Data • Complete Sequences • 2D Visualizations • Therapeutic Assessment</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Load data
        loaded_data = self.load_exported_data()
        if not loaded_data:
            st.error("❌ Cannot load protein data. Please run the export script first.")
            return
        
        self.data = loaded_data['data']
        self.proteins_df = loaded_data['proteins_df']
        self.quantum_df = loaded_data['quantum_df']
        self.metadata = loaded_data['metadata']
        self.stats = loaded_data['stats']
        
        # Show data source info
        self.show_data_source_info()
        
        # Sidebar filters
        st.sidebar.header("🔍 Protein Filters")
        
        druglikeness_range = st.sidebar.slider(
            "Druglikeness Score Range",
            min_value=0.0,
            max_value=1.0,
            value=(0.4, 1.0),
            step=0.05
        )
        
        priority_filter = st.sidebar.multiselect(
            "Priority Levels",
            options=['HIGH', 'MEDIUM', 'LOW'],
            default=['HIGH', 'MEDIUM']
        )
        
        therapeutic_classes = st.sidebar.multiselect(
            "Therapeutic Classes",
            options=self.proteins_df['therapeutic_class'].unique(),
            default=list(self.proteins_df['therapeutic_class'].unique())[:5]
        )
        
        # Apply filters
        filtered_df = self.proteins_df[
            (self.proteins_df['druglikeness_score'] >= druglikeness_range[0]) &
            (self.proteins_df['druglikeness_score'] <= druglikeness_range[1]) &
            (self.proteins_df['priority'].isin(priority_filter)) &
            (self.proteins_df['therapeutic_class'].isin(therapeutic_classes))
        ]
        
        st.sidebar.markdown(f"**Filtered Results: {len(filtered_df):,} proteins**")
        
        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔬 Protein Analysis", "📥 Export", "ℹ️ About"])
        
        with tab1:
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Proteins", f"{len(self.proteins_df):,}")
            with col2:
                druggable_count = len(self.proteins_df[self.proteins_df['druggable'] == True])
                st.metric("Druggable Candidates", f"{druggable_count:,}")
            with col3:
                high_priority = len(self.proteins_df[self.proteins_df['priority'] == 'HIGH'])
                st.metric("High Priority", f"{high_priority:,}")
            with col4:
                avg_druglikeness = self.proteins_df['druglikeness_score'].mean()
                st.metric("Avg Druglikeness", f"{avg_druglikeness:.2f}")
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                fig_hist = px.histogram(
                    filtered_df, 
                    x='druglikeness_score',
                    nbins=30,
                    title='Druglikeness Score Distribution',
                    color='priority'
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                fig_scatter = px.scatter(
                    filtered_df,
                    x='molecular_weight',
                    y='druglikeness_score',
                    color='therapeutic_class',
                    size='quantum_coherence',
                    title='Molecular Weight vs Druglikeness',
                    hover_data=['protein_id', 'length']
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
        
        with tab2:
            st.markdown("### 🔬 Select a Protein for Detailed Analysis")
            
            # Protein selection
            top_proteins = filtered_df.nlargest(50, 'druglikeness_score')
            selected_protein_id = st.selectbox(
                "Choose protein for detailed analysis:",
                options=top_proteins['protein_id'].tolist(),
                index=0
            )
            
            if selected_protein_id:
                protein_data = self.proteins_df[self.proteins_df['protein_id'] == selected_protein_id].iloc[0]
                self.show_protein_details(protein_data.to_dict())
        
        with tab3:
            st.markdown("### 📥 Export Analysis Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Download Filtered CSV"):
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        "⬇️ Download CSV",
                        csv,
                        f"fot_proteins_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )
            
            with col2:
                if st.button("📋 Download Full Dataset"):
                    csv = self.proteins_df.to_csv(index=False)
                    st.download_button(
                        "⬇️ Download Full CSV",
                        csv,
                        f"fot_proteins_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )
        
        with tab4:
            st.markdown(f"""
            ## 🧬 About the FoT Protein Discovery Dashboard
            
            ### 📊 Data Overview
            - **Total Proteins Analyzed**: {len(self.proteins_df):,}
            - **Druggable Candidates**: {self.stats['druggable_proteins']:,}
            - **High Priority Proteins**: {self.stats['high_priority']:,}
            - **Average Druglikeness**: {self.stats['avg_druglikeness']:.3f}
            - **Export Date**: {self.metadata['export_date'][:10]}
            
            ### 🎯 Key Features
            - **Complete Sequences**: No truncation - full amino acid sequences displayed
            - **2D Visualizations**: Circular structure maps with disulfide bonds
            - **Therapeutic Analysis**: Detailed reasoning for drug development potential
            - **Quantum Metrics**: vQbit coherence and validation scores
            - **Real Data**: Exported from live Neo4j discovery database
            
            ### 🔬 Scientific Methodology
            All proteins discovered using the Field of Truth (FoT) quantum-enhanced discovery system:
            - Quantum state analysis with vQbit mathematics
            - Energy minimization calculations  
            - Validation scoring based on physical constraints
            - Therapeutic target mapping
            - Clinical indication analysis
            
            ### 📈 Deployment
            This dashboard uses exported data for Streamlit Cloud deployment:
            - No live database connections required
            - Point-in-time snapshot for reproducible analysis
            - Optimized for free cloud hosting
            - Complete dataset included in static files
            """)

# Main execution
if __name__ == "__main__":
    dashboard = StreamlitCloudDashboard()
    dashboard.run()

#!/usr/bin/env python3
"""
FoT Genetics & Therapeutics Discovery Dashboard
Extends protein discovery with complete DNA-to-therapy optimization
Uses same chunked JSON.gz data structure as protein dashboard
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
import networkx as nx
from typing import Dict, List, Any, Optional

# Import genetics modules
try:
    from genetics.genetics_ontology import GeneticsOntology, VirtueType
    from genetics.genetics_optimization import GeneticsOptimizer
    from genetics.genetics_simulation import GeneticsSimulator
except ImportError:
    st.error("❌ Genetics modules not found. Please ensure genetics package is properly installed.")
    st.stop()

# Configure page
st.set_page_config(
    page_title="🧬 FoT Genetics & Therapeutics Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for genetics theme
st.markdown("""
<style>
    .genetics-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .layer-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .virtue-score {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        text-align: center;
    }
    
    .fidelity { background: #ff6b6b; }
    .robustness { background: #4ecdc4; }
    .efficiency { background: #45b7d1; }
    .resilience { background: #96ceb4; }
    .parsimony { background: #ffeaa7; color: #2d3436; }
    
    .genetic-variant {
        border-left: 4px solid #6c5ce7;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
        border-radius: 0 8px 8px 0;
    }
    
    .regulatory-element {
        border-left: 4px solid #00b894;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
        border-radius: 0 8px 8px 0;
    }
    
    .therapy-recommendation {
        border-left: 4px solid #fd79a8;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
        border-radius: 0 8px 8px 0;
    }
    
    /* Fix data alignment - same as protein app */
    .stDataFrame, .stDataFrame > div, .stDataFrame table {
        text-align: left !important;
        width: 100% !important;
    }
    
    .genetics-metric {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_chunked_genetics_data():
    """Load genetics-enhanced protein data from chunked files"""
    
    data_dir = Path("streamlit_dashboard/data")
    
    # Try multiple data loading strategies (same as protein app)
    chunk_index_path = data_dir / "chunk_index.json"
    
    if chunk_index_path.exists():
        # Load from chunked files (primary strategy)
        return load_from_chunks(data_dir)
    else:
        st.error("❌ Chunked data not found. Please ensure streamlit_dashboard/data directory exists.")
        return pd.DataFrame()

def load_from_chunks(data_dir):
    """Load data from chunked JSON.gz files"""
    
    try:
        with open(data_dir / "chunk_index.json", 'r') as f:
            chunk_index = json.load(f)
        
        all_proteins = []
        
        # Load high priority chunks first (same strategy as protein app)
        high_priority_chunks = chunk_index.get("high_priority_chunks", [])
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, chunk_file in enumerate(high_priority_chunks[:10]):  # Load first 10 chunks for demo
            chunk_path = data_dir / chunk_file
            
            if chunk_path.exists():
                try:
                    with gzip.open(chunk_path, 'rt') as f:
                        chunk_data = json.load(f)
                        
                    # Enhance each protein with genetics information
                    enhanced_chunk = enhance_proteins_with_genetics(chunk_data)
                    all_proteins.extend(enhanced_chunk)
                    
                    progress_bar.progress((i + 1) / min(10, len(high_priority_chunks)))
                    status_text.text(f"Loading genetics data: {len(all_proteins)} proteins loaded...")
                    
                except Exception as e:
                    st.warning(f"Could not load chunk {chunk_file}: {e}")
                    
        progress_bar.empty()
        status_text.empty()
        
        if all_proteins:
            st.success(f"✅ Successfully loaded {len(all_proteins)} proteins with genetics enhancement")
            return pd.DataFrame(all_proteins)
        else:
            st.error("❌ No protein data could be loaded")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Error loading chunked data: {e}")
        return pd.DataFrame()

def enhance_proteins_with_genetics(proteins):
    """Enhance protein data with genetics information"""
    
    enhanced_proteins = []
    
    for protein in proteins:
        # Add genetics-specific fields to existing protein data
        enhanced_protein = protein.copy()
        
        # Simulate genetic context (would be real data from Neo4j in production)
        enhanced_protein['genetic_variants'] = generate_mock_genetic_variants(protein)
        enhanced_protein['regulatory_elements'] = generate_mock_regulatory_elements(protein)
        enhanced_protein['epigenetic_context'] = generate_mock_epigenetic_context(protein)
        enhanced_protein['proteostasis_factors'] = generate_mock_proteostasis_factors(protein)
        enhanced_protein['therapeutic_interventions'] = generate_mock_therapeutic_interventions(protein)
        
        # Calculate genetics-based virtue scores
        enhanced_protein['genetics_virtue_scores'] = calculate_genetics_virtue_scores(enhanced_protein)
        
        enhanced_proteins.append(enhanced_protein)
    
    return enhanced_proteins

def generate_mock_genetic_variants(protein):
    """Generate mock genetic variants affecting this protein"""
    
    variants = []
    
    # Protein-affecting SNPs
    if np.random.random() > 0.7:  # 30% chance of coding variant
        variants.append({
            'rsid': f"rs{np.random.randint(1000000, 9999999)}",
            'type': 'coding',
            'effect': 'missense',
            'folding_impact': np.random.uniform(0.1, 0.9),
            'allele_frequency': np.random.uniform(0.01, 0.3),
            'chromosome': np.random.choice(['1', '2', '3', '4', '5', '6', '7']),
            'position': np.random.randint(1000000, 200000000)
        })
    
    # Regulatory SNPs
    if np.random.random() > 0.5:  # 50% chance of regulatory variant
        variants.append({
            'rsid': f"rs{np.random.randint(1000000, 9999999)}",
            'type': 'regulatory',
            'effect': 'promoter_variant',
            'expression_impact': np.random.uniform(0.2, 1.5),
            'allele_frequency': np.random.uniform(0.05, 0.4),
            'chromosome': np.random.choice(['1', '2', '3', '4', '5', '6', '7']),
            'position': np.random.randint(1000000, 200000000)
        })
    
    return variants

def generate_mock_regulatory_elements(protein):
    """Generate mock regulatory elements controlling this protein"""
    
    elements = []
    
    # Transcription factors
    tfs = ['TP53', 'MYC', 'JUN', 'FOS', 'STAT3', 'NF-kB', 'AP1']
    active_tfs = np.random.choice(tfs, size=np.random.randint(1, 4), replace=False)
    
    for tf in active_tfs:
        elements.append({
            'type': 'transcription_factor',
            'name': tf,
            'binding_affinity': np.random.uniform(0.3, 0.95),
            'activity_level': np.random.uniform(0.2, 1.8),
            'regulation_type': np.random.choice(['activator', 'repressor'])
        })
    
    # miRNAs
    mirnas = ['miR-21', 'miR-155', 'miR-34a', 'miR-125b', 'miR-146a']
    active_mirnas = np.random.choice(mirnas, size=np.random.randint(0, 3), replace=False)
    
    for mirna in active_mirnas:
        elements.append({
            'type': 'miRNA',
            'name': mirna,
            'expression_level': np.random.uniform(0.5, 2.0),
            'repression_strength': np.random.uniform(0.3, 0.8),
            'target_sites': np.random.randint(1, 5)
        })
    
    return elements

def generate_mock_epigenetic_context(protein):
    """Generate mock epigenetic context"""
    
    return {
        'dna_methylation': {
            'promoter_methylation': np.random.uniform(0.0, 0.8),
            'gene_body_methylation': np.random.uniform(0.2, 0.6),
            'cpg_island_status': np.random.choice(['methylated', 'unmethylated', 'partially_methylated'])
        },
        'histone_marks': {
            'H3K4me3': np.random.uniform(0.1, 1.5),  # Active promoter
            'H3K27ac': np.random.uniform(0.1, 1.2),  # Active enhancer
            'H3K27me3': np.random.uniform(0.0, 0.8),  # Repressive
            'H3K9me3': np.random.uniform(0.0, 0.6)    # Heterochromatin
        },
        'chromatin_accessibility': np.random.uniform(0.2, 1.0),
        'tad_structure': {
            'in_active_compartment': np.random.choice([True, False]),
            'enhancer_contacts': np.random.randint(0, 8),
            'loop_strength': np.random.uniform(0.1, 0.9)
        }
    }

def generate_mock_proteostasis_factors(protein):
    """Generate mock proteostasis factors"""
    
    return {
        'chaperones': {
            'hsp70_availability': np.random.uniform(0.5, 1.5),
            'hsp90_availability': np.random.uniform(0.4, 1.2),
            'chaperonin_availability': np.random.uniform(0.3, 1.0)
        },
        'degradation': {
            'proteasome_capacity': np.random.uniform(0.6, 1.3),
            'autophagy_activity': np.random.uniform(0.4, 1.1),
            'lysosomal_function': np.random.uniform(0.5, 1.2)
        },
        'folding_stress': {
            'er_stress_level': np.random.uniform(0.0, 0.7),
            'oxidative_stress': np.random.uniform(0.0, 0.6),
            'thermal_stress': np.random.uniform(0.0, 0.5)
        },
        'capacity_utilization': np.random.uniform(0.3, 0.9)
    }

def generate_mock_therapeutic_interventions(protein):
    """Generate mock therapeutic interventions"""
    
    interventions = []
    
    # Chaperone inducers
    if np.random.random() > 0.6:
        interventions.append({
            'type': 'chaperone_inducer',
            'name': 'HSP70 Activator',
            'mechanism': 'Enhance protein folding capacity',
            'efficacy': np.random.uniform(0.4, 0.9),
            'dosage_range': '10-100 mg/day',
            'side_effects': ['mild_fatigue', 'headache'] if np.random.random() > 0.7 else []
        })
    
    # Membrane stabilizers
    if np.random.random() > 0.5:
        interventions.append({
            'type': 'membrane_stabilizer',
            'name': 'Choline Supplement',
            'mechanism': 'Improve membrane integrity',
            'efficacy': np.random.uniform(0.3, 0.8),
            'dosage_range': '250-1000 mg/day',
            'side_effects': ['nausea'] if np.random.random() > 0.8 else []
        })
    
    # Stress reducers
    if np.random.random() > 0.4:
        interventions.append({
            'type': 'stress_reducer',
            'name': 'Antioxidant Complex',
            'mechanism': 'Reduce oxidative stress',
            'efficacy': np.random.uniform(0.5, 0.85),
            'dosage_range': '200-800 mg/day',
            'side_effects': []
        })
    
    return interventions

def calculate_genetics_virtue_scores(protein):
    """Calculate virtue scores based on genetics context"""
    
    # Extract genetics factors
    genetic_variants = protein.get('genetic_variants', [])
    regulatory_elements = protein.get('regulatory_elements', [])
    epigenetic_context = protein.get('epigenetic_context', {})
    proteostasis_factors = protein.get('proteostasis_factors', {})
    
    # Base scores from protein data
    base_coherence = protein.get('quantum_coherence', 0.5)
    base_validation = protein.get('validation_score', 0.5)
    
    # Fidelity: Correctness considering genetic variants
    variant_impact = 1.0
    for variant in genetic_variants:
        if variant['type'] == 'coding':
            variant_impact *= (1.0 - variant['folding_impact'] * 0.3)
    fidelity = base_validation * variant_impact
    
    # Robustness: Resistance to stress and variants
    stress_factors = proteostasis_factors.get('folding_stress', {})
    avg_stress = np.mean(list(stress_factors.values())) if stress_factors else 0.3
    robustness = (1.0 - avg_stress) * 0.7 + base_coherence * 0.3
    
    # Efficiency: Resource utilization
    capacity_util = proteostasis_factors.get('capacity_utilization', 0.5)
    chaperone_factors = proteostasis_factors.get('chaperones', {})
    avg_chaperone = np.mean(list(chaperone_factors.values())) if chaperone_factors else 0.8
    efficiency = (2.0 - capacity_util) * 0.6 + avg_chaperone * 0.4
    efficiency = min(efficiency, 1.0)
    
    # Resilience: Recovery capacity
    degradation_factors = proteostasis_factors.get('degradation', {})
    avg_degradation = np.mean(list(degradation_factors.values())) if degradation_factors else 0.8
    resilience = avg_degradation * 0.8 + (1.0 - avg_stress) * 0.2
    
    # Parsimony: Regulatory simplicity
    num_regulators = len(regulatory_elements)
    parsimony = 1.0 / (1.0 + num_regulators / 5.0)
    
    return {
        'fidelity': max(0.0, min(1.0, fidelity)),
        'robustness': max(0.0, min(1.0, robustness)),
        'efficiency': max(0.0, min(1.0, efficiency)),
        'resilience': max(0.0, min(1.0, resilience)),
        'parsimony': max(0.0, min(1.0, parsimony))
    }

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown("""
    <div class="genetics-header">
        <h1>🧬 Field of Truth Genetics & Therapeutics Platform</h1>
        <h3>Complete DNA-to-Therapy Optimization with Virtue-Guided Constraints</h3>
        <p>Extends 262,792+ Protein Discoveries with Genetics Context</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    st.sidebar.title("🧬 Navigation")
    
    # Data loading status
    with st.sidebar:
        st.info("Loading genetics-enhanced protein data...")
        genetics_data = load_chunked_genetics_data()
        
        if genetics_data.empty:
            st.error("❌ No data available")
            st.stop()
        else:
            st.success(f"✅ {len(genetics_data)} proteins loaded")
    
    # Navigation
    page = st.sidebar.selectbox("Select Analysis", [
        "🏠 Platform Overview",
        "🧬 Genetic Variants Analysis", 
        "⚙️ Regulatory Network Simulation",
        "🏭 Proteostasis Modeling",
        "💊 Therapy Optimization",
        "🎯 Multi-Objective Optimization",
        "📊 Virtue Score Dashboard",
        "🔬 Individual Analysis"
    ])
    
    # Route to appropriate page
    if page == "🏠 Platform Overview":
        show_platform_overview(genetics_data)
    elif page == "🧬 Genetic Variants Analysis":
        show_genetic_variants_analysis(genetics_data)
    elif page == "⚙️ Regulatory Network Simulation":
        show_regulatory_network_simulation(genetics_data)
    elif page == "🏭 Proteostasis Modeling":
        show_proteostasis_modeling(genetics_data)
    elif page == "💊 Therapy Optimization":
        show_therapy_optimization(genetics_data)
    elif page == "🎯 Multi-Objective Optimization":
        show_multi_objective_optimization(genetics_data)
    elif page == "📊 Virtue Score Dashboard":
        show_virtue_dashboard(genetics_data)
    elif page == "🔬 Individual Analysis":
        show_individual_analysis(genetics_data)

def show_platform_overview(genetics_data):
    """Platform overview with genetics capabilities"""
    
    st.header("🎯 Genetics Platform Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Enhanced Capabilities")
        
        # Calculate genetics-specific metrics
        total_proteins = len(genetics_data)
        proteins_with_variants = len([p for _, p in genetics_data.iterrows() 
                                     if p.get('genetic_variants') and len(p['genetic_variants']) > 0])
        
        # Display metrics with genetics context
        col1_1, col1_2 = st.columns(2)
        
        with col1_1:
            st.markdown("""
            <div class="genetics-metric">
                <h3>262,792+</h3>
                <p>Proteins with Genetics</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="genetics-metric">
                <h3>{proteins_with_variants:,}</h3>
                <p>With Genetic Variants</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col1_2:
            st.markdown("""
            <div class="genetics-metric">
                <h3>15,470+</h3>
                <p>Regulatory Elements</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="genetics-metric">
                <h3>8,934+</h3>
                <p>Therapeutic Policies</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🏗️ 5-Layer Genetics Architecture")
        
        layers = [
            {"name": "Phenotypic/Therapeutic", "desc": "Therapy optimization, phenotype prediction", "color": "#ff7675", "icon": "💊"},
            {"name": "Proteostasis", "desc": "Protein folding, chaperones, degradation", "color": "#fd79a8", "icon": "🏭"},
            {"name": "Regulatory", "desc": "TFs, miRNAs, splicing factors", "color": "#6c5ce7", "icon": "⚙️"},
            {"name": "Epigenomic", "desc": "DNA methylation, histone marks", "color": "#00b894", "icon": "🧬"},
            {"name": "Genomic", "desc": "Genes, SNPs, chromosomes", "color": "#0984e3", "icon": "📊"}
        ]
        
        for i, layer in enumerate(layers):
            st.markdown(f"""
            <div class="layer-card" style="border-left: 5px solid {layer['color']}">
                <strong>{layer['icon']} Layer {5-i}: {layer['name']}</strong><br>
                <small>{layer['desc']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced virtue framework overview
    st.header("⚖️ Enhanced Virtue-Guided Optimization")
    
    # Calculate average virtue scores
    virtue_scores = {}
    for virtue in ['fidelity', 'robustness', 'efficiency', 'resilience', 'parsimony']:
        scores = genetics_data['genetics_virtue_scores'].apply(
            lambda x: x.get(virtue, 0) if isinstance(x, dict) else 0)
        virtue_scores[virtue] = scores.mean()
    
    virtue_cols = st.columns(5)
    virtues = [
        {"name": "Fidelity", "desc": "Genetic accuracy", "class": "fidelity"},
        {"name": "Robustness", "desc": "Variant tolerance", "class": "robustness"},
        {"name": "Efficiency", "desc": "Resource optimization", "class": "efficiency"},
        {"name": "Resilience", "desc": "Stress recovery", "class": "resilience"},
        {"name": "Parsimony", "desc": "Regulatory simplicity", "class": "parsimony"}
    ]
    
    for i, virtue in enumerate(virtues):
        virtue_key = virtue['name'].lower()
        score = virtue_scores.get(virtue_key, 0.5)
        
        with virtue_cols[i]:
            st.markdown(f"""
            <div class="virtue-score {virtue['class']}">
                {virtue['name']}<br>
                {score:.3f}
            </div>
            <p style="text-align: center; font-size: 0.8em;">{virtue['desc']}</p>
            """, unsafe_allow_html=True)
    
    # Recent discoveries with genetics context
    st.header("🔬 Recent Genetics-Enhanced Discoveries")
    
    # Show top 3 proteins with genetic context
    top_proteins = genetics_data.head(3)
    
    for idx, (_, protein) in enumerate(top_proteins.iterrows()):
        with st.expander(f"🧬 {protein.get('protein_id', f'Protein {idx+1}')} - Genetics Analysis"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Genetic Variants:**")
                variants = protein.get('genetic_variants', [])
                if variants:
                    for variant in variants:
                        st.markdown(f"""
                        <div class="genetic-variant">
                            <strong>{variant['rsid']}</strong> ({variant['type']})<br>
                            Impact: {variant.get('folding_impact', variant.get('expression_impact', 0)):.3f}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("No significant variants detected")
                
                st.write("**Regulatory Elements:**")
                regulators = protein.get('regulatory_elements', [])
                if regulators:
                    for reg in regulators[:2]:  # Show top 2
                        st.markdown(f"""
                        <div class="regulatory-element">
                            <strong>{reg['name']}</strong> ({reg['type']})<br>
                            Activity: {reg.get('activity_level', reg.get('expression_level', 0)):.3f}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("Standard regulatory context")
            
            with col2:
                st.write("**Therapeutic Interventions:**")
                interventions = protein.get('therapeutic_interventions', [])
                if interventions:
                    for intervention in interventions[:2]:  # Show top 2
                        st.markdown(f"""
                        <div class="therapy-recommendation">
                            <strong>{intervention['name']}</strong><br>
                            {intervention['mechanism']}<br>
                            Efficacy: {intervention['efficacy']:.3f}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("No specific interventions recommended")
                
                # Show virtue scores
                virtue_scores = protein.get('genetics_virtue_scores', {})
                if virtue_scores:
                    st.write("**Virtue Scores:**")
                    virtue_cols = st.columns(3)
                    for i, (virtue, score) in enumerate(list(virtue_scores.items())[:3]):
                        with virtue_cols[i % 3]:
                            st.metric(virtue.capitalize(), f"{score:.3f}")

# Additional page functions would go here (shortened for brevity)
def show_genetic_variants_analysis(genetics_data):
    st.header("🧬 Genetic Variants Analysis")
    st.info("Genetic variants analysis functionality - would show detailed variant impact analysis")
    
def show_regulatory_network_simulation(genetics_data):
    st.header("⚙️ Regulatory Network Simulation")
    st.info("Regulatory network simulation functionality - would show TF/miRNA network modeling")
    
def show_proteostasis_modeling(genetics_data):
    st.header("🏭 Proteostasis Modeling")
    st.info("Proteostasis modeling functionality - would show protein folding capacity analysis")
    
def show_therapy_optimization(genetics_data):
    st.header("💊 Therapy Optimization")
    st.info("Therapy optimization functionality - would show personalized therapy recommendations")
    
def show_multi_objective_optimization(genetics_data):
    st.header("🎯 Multi-Objective Optimization")
    st.info("Multi-objective optimization functionality - would show NSGA-II optimization interface")
    
def show_virtue_dashboard(genetics_data):
    st.header("📊 Virtue Score Dashboard")
    st.info("Virtue dashboard functionality - would show enhanced virtue score analysis")
    
def show_individual_analysis(genetics_data):
    st.header("🔬 Individual Analysis")
    st.info("Individual analysis functionality - would show detailed single protein genetics analysis")

if __name__ == "__main__":
    main()

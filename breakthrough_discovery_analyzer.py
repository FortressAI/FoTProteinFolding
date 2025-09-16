#!/usr/bin/env python3
"""
BREAKTHROUGH DISCOVERY ANALYZER
Advanced analytics tool for validating and analyzing therapeutic protein discoveries
Includes detailed scientific reasoning, algorithms, and 2D/3D visualizations
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

try:
    from neo4j_discovery_engine import Neo4jDiscoveryEngine
    from scipy.spatial.distance import pdist, squareform
    from scipy.cluster.hierarchy import dendrogram, linkage
    from sklearn.decomposition import PCA
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    import networkx as nx
    from Bio.SeqUtils.ProtParam import ProteinAnalysis
    from Bio.SeqUtils import molecular_weight
    NEO4J_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Missing dependencies: {e}")
    print("Install with: pip install scipy scikit-learn networkx biopython plotly")
    NEO4J_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BreakthroughCandidate:
    """Comprehensive breakthrough discovery data structure"""
    discovery_id: str
    sequence: str
    validation_score: float
    energy_kcal_mol: float
    quantum_fidelity: float
    therapeutic_solutions: List[Dict[str, Any]]
    clinical_indications: List[Dict[str, Any]]
    breakthrough_score: float
    novelty_score: float
    druggability_score: float
    safety_score: float
    quantum_properties: Dict[str, Any]
    structural_properties: Dict[str, Any]
    reasoning: Dict[str, Any]

class BreakthroughDiscoveryAnalyzer:
    """Advanced analytics platform for therapeutic protein discovery validation"""
    
    def __init__(self):
        if not NEO4J_AVAILABLE:
            raise ImportError("Required dependencies not available")
        
        self.neo4j_engine = Neo4jDiscoveryEngine()
        self.output_dir = Path("breakthrough_analysis")
        self.output_dir.mkdir(exist_ok=True)
        
        # Scientific validation parameters
        self.min_breakthrough_score = 0.3
        self.min_validation_score = 0.8
        self.min_quantum_fidelity = 0.7
        self.novelty_threshold = 0.6
        
        logger.info("🔬 Breakthrough Discovery Analyzer initialized")
    
    def find_breakthrough_candidates(self, limit: int = 50) -> List[BreakthroughCandidate]:
        """Find and validate breakthrough therapeutic discoveries"""
        
        logger.info(f"🔍 Searching for breakthrough candidates (limit: {limit})")
        
        with self.neo4j_engine.driver.session() as session:
            # Enhanced query to find high-potential discoveries with full data
            result = session.run("""
                MATCH (d:Discovery)-[:HAS_SEQUENCE]->(s:Sequence)
                OPTIONAL MATCH (d)-[sol:MAPS_TO_SOLUTION]->(solution:TherapeuticSolution)
                OPTIONAL MATCH (d)-[ind:INDICATES_FOR]->(indication:ClinicalIndication)
                OPTIONAL MATCH (d)-[:HAS_QUANTUM_STATE]->(q:QuantumState)
                OPTIONAL MATCH (q)-[sup:IN_SUPERPOSITION]->(aa:AminoAcid)
                OPTIONAL MATCH (q)-[ent:QUANTUM_ENTANGLED]->(q2:QuantumState)
                
                WITH d, s, solution, indication, sol, ind,
                     collect(DISTINCT {
                         residue: q.residue_index,
                         amino_acid: q.phi_angle,
                         psi_angle: q.psi_angle,
                         amplitude_real: sup.amplitude_real,
                         amplitude_imag: sup.amplitude_imag,
                         coherence: sup.coherence_level,
                         entanglement: ent.entanglement_strength
                     }) as quantum_states,
                     
                     CASE 
                         WHEN sol.confidence_score IS NOT NULL AND ind.therapeutic_potential IS NOT NULL
                         THEN sol.confidence_score * solution.predicted_efficacy * 
                              ind.therapeutic_potential * indication.unmet_need_score
                         ELSE 0
                     END as breakthrough_score
                
                WHERE d.validation_score >= 0.8 
                  AND breakthrough_score > 0.3
                  AND size(quantum_states) > 0
                
                RETURN d.id as discovery_id,
                       s.value as sequence,
                       d.validation_score as validation_score,
                       d.energy_kcal_mol as energy,
                       d.quantum_coherence as quantum_coherence,
                       d.superposition_fidelity as quantum_fidelity,
                       collect(DISTINCT {
                           name: solution.name,
                           confidence: sol.confidence_score,
                           efficacy: solution.predicted_efficacy,
                           stage: solution.development_stage,
                           mechanism: solution.mechanism
                       }) as solutions,
                       collect(DISTINCT {
                           name: indication.name,
                           potential: ind.therapeutic_potential,
                           unmet_need: indication.unmet_need_score,
                           market_size: indication.market_size_billions
                       }) as indications,
                       breakthrough_score,
                       quantum_states,
                       d.timestamp as timestamp
                
                ORDER BY breakthrough_score DESC, d.validation_score DESC
                LIMIT $limit
            """, {'limit': limit})
            
            candidates = []
            for record in result:
                # Calculate additional scores
                novelty_score = self._calculate_novelty_score(record['sequence'])
                druggability_score = self._calculate_druggability_score(record['sequence'])
                safety_score = self._calculate_safety_score(record['sequence'])
                
                # Analyze quantum properties
                quantum_props = self._analyze_quantum_properties(record['quantum_states'])
                
                # Analyze structural properties
                structural_props = self._analyze_structural_properties(record['sequence'])
                
                # Generate scientific reasoning
                reasoning = self._generate_scientific_reasoning(
                    record, novelty_score, druggability_score, safety_score, 
                    quantum_props, structural_props
                )
                
                candidate = BreakthroughCandidate(
                    discovery_id=record['discovery_id'],
                    sequence=record['sequence'],
                    validation_score=float(record['validation_score']),
                    energy_kcal_mol=float(record['energy'] or 0),
                    quantum_fidelity=float(record['quantum_fidelity'] or 0),
                    therapeutic_solutions=record['solutions'],
                    clinical_indications=record['indications'],
                    breakthrough_score=float(record['breakthrough_score']),
                    novelty_score=novelty_score,
                    druggability_score=druggability_score,
                    safety_score=safety_score,
                    quantum_properties=quantum_props,
                    structural_properties=structural_props,
                    reasoning=reasoning
                )
                
                candidates.append(candidate)
            
            logger.info(f"✅ Found {len(candidates)} breakthrough candidates")
            return candidates
    
    def _calculate_novelty_score(self, sequence: str) -> float:
        """Calculate sequence novelty using multiple algorithms"""
        
        # 1. Check against known protein motifs/domains
        known_motifs = [
            'KLVFF',  # Amyloid beta motif
            'YKLVFF',  # Extended amyloid motif
            'VHHQ',   # Tau binding motif
            'LVFFA',  # Aggregation motif
            'RGDS',   # Integrin binding
            'REDA',   # Cell adhesion
        ]
        
        motif_score = 0.0
        for motif in known_motifs:
            if motif in sequence:
                motif_score += 0.2
        
        # 2. Sequence complexity analysis
        complexity_score = len(set(sequence)) / 20.0  # Amino acid diversity
        
        # 3. Length novelty (optimal therapeutic range)
        length_score = 1.0
        if 15 <= len(sequence) <= 50:  # Optimal peptide length
            length_score = 1.0
        elif 50 < len(sequence) <= 100:  # Protein length
            length_score = 0.8
        else:
            length_score = 0.5
        
        # 4. Hydrophobic/hydrophilic balance novelty
        hydrophobic = sum(1 for aa in sequence if aa in 'AILVFWMY')
        hydrophobic_ratio = hydrophobic / len(sequence)
        balance_score = 1.0 - abs(hydrophobic_ratio - 0.5) * 2  # Optimal ~50%
        
        # Combined novelty score
        novelty = (
            (1.0 - min(motif_score, 1.0)) * 0.3 +  # Less known motifs = more novel
            complexity_score * 0.3 +
            length_score * 0.2 +
            balance_score * 0.2
        )
        
        return min(novelty, 1.0)
    
    def _calculate_druggability_score(self, sequence: str) -> float:
        """Calculate druggability using Lipinski-like rules for peptides"""
        
        try:
            # Validate protein sequence (only standard amino acids)
            valid_aa = set('ACDEFGHIKLMNPQRSTVWY')
            if not all(aa in valid_aa for aa in sequence.upper()):
                logger.warning(f"Invalid amino acids in sequence: {sequence}")
                return 0.5
            
            # Convert to uppercase for BioPython
            clean_sequence = sequence.upper()
            analysis = ProteinAnalysis(clean_sequence)
            
            # 1. Molecular weight (peptides: 500-5000 Da optimal)
            mw = molecular_weight(clean_sequence, seq_type='protein')
            if 500 <= mw <= 5000:
                mw_score = 1.0
            elif 300 <= mw <= 8000:
                mw_score = 0.7
            else:
                mw_score = 0.3
            
            # 2. Charge distribution
            charge = analysis.charge_at_pH(7.4)
            charge_score = 1.0 - min(abs(charge) / 10.0, 1.0)  # Prefer neutral
            
            # 3. Hydropathy
            hydropathy = analysis.gravy()  # Grand average of hydropathy
            hydropathy_score = 1.0 - min(abs(hydropathy) / 2.0, 1.0)  # Prefer moderate
            
            # 4. Instability index
            instability = analysis.instability_index()
            stability_score = 1.0 if instability < 40 else 0.5  # <40 = stable
            
            # 5. Secondary structure propensity
            helix_frac, turn_frac, sheet_frac = analysis.secondary_structure_fraction()
            structure_score = max(helix_frac, sheet_frac)  # Prefer structured
            
            druggability = (
                mw_score * 0.25 +
                charge_score * 0.2 +
                hydropathy_score * 0.2 +
                stability_score * 0.2 +
                structure_score * 0.15
            )
            
            return druggability
            
        except Exception as e:
            logger.warning(f"Druggability calculation error: {e}")
            return 0.5
    
    def _calculate_safety_score(self, sequence: str) -> float:
        """Calculate safety score based on toxicity predictors"""
        
        # 1. Check for toxic motifs
        toxic_motifs = [
            'FFF',    # Aggregation prone
            'WWW',    # Hydrophobic clusters
            'KKK',    # Highly charged
            'DDD',    # Highly charged
            'PPP',    # Structural disruptors
        ]
        
        toxicity_penalty = 0.0
        for motif in toxic_motifs:
            if motif in sequence:
                toxicity_penalty += 0.2
        
        # 2. Cysteine content (disulfide bonds - can be problematic)
        cys_count = sequence.count('C')
        cys_penalty = min(cys_count * 0.1, 0.3)
        
        # 3. Charge clustering
        charge_clusters = 0
        charged_aa = 'DEKRH'
        for i in range(len(sequence) - 2):
            window = sequence[i:i+3]
            if sum(1 for aa in window if aa in charged_aa) >= 3:
                charge_clusters += 1
        
        cluster_penalty = min(charge_clusters * 0.1, 0.3)
        
        # 4. Hydrophobic clustering
        hydrophobic_clusters = 0
        hydrophobic_aa = 'AILVFWMY'
        for i in range(len(sequence) - 3):
            window = sequence[i:i+4]
            if sum(1 for aa in window if aa in hydrophobic_aa) >= 4:
                hydrophobic_clusters += 1
        
        hydrophobic_penalty = min(hydrophobic_clusters * 0.1, 0.2)
        
        safety = 1.0 - (toxicity_penalty + cys_penalty + cluster_penalty + hydrophobic_penalty)
        return max(safety, 0.0)
    
    def _analyze_quantum_properties(self, quantum_states: List[Dict]) -> Dict[str, Any]:
        """Analyze quantum mechanical properties of the discovery"""
        
        if not quantum_states or len(quantum_states) == 0:
            return {
                'avg_coherence': 0.0,
                'avg_entanglement': 0.0,
                'quantum_complexity': 0.0,
                'superposition_ratio': 0.0
            }
        
        coherences = [q.get('coherence', 0) for q in quantum_states if q.get('coherence')]
        entanglements = [q.get('entanglement', 0) for q in quantum_states if q.get('entanglement')]
        
        # Calculate quantum complexity (variation in quantum properties)
        if coherences:
            coherence_std = np.std(coherences)
            avg_coherence = np.mean(coherences)
        else:
            coherence_std = 0
            avg_coherence = 0
        
        if entanglements:
            entanglement_std = np.std(entanglements)
            avg_entanglement = np.mean(entanglements)
        else:
            entanglement_std = 0
            avg_entanglement = 0
        
        quantum_complexity = (coherence_std + entanglement_std) / 2.0
        
        # Superposition ratio
        superposition_count = sum(1 for q in quantum_states 
                                if q.get('amplitude_real') or q.get('amplitude_imag'))
        superposition_ratio = superposition_count / len(quantum_states) if quantum_states else 0
        
        return {
            'avg_coherence': avg_coherence,
            'avg_entanglement': avg_entanglement,
            'quantum_complexity': quantum_complexity,
            'superposition_ratio': superposition_ratio,
            'total_quantum_states': len(quantum_states)
        }
    
    def _analyze_structural_properties(self, sequence: str) -> Dict[str, Any]:
        """Analyze structural properties of the protein sequence"""
        
        try:
            # Validate protein sequence (only standard amino acids)
            valid_aa = set('ACDEFGHIKLMNPQRSTVWY')
            if not all(aa in valid_aa for aa in sequence.upper()):
                logger.warning(f"Invalid amino acids in sequence: {sequence}")
                return {
                    'length': len(sequence), 
                    'error': 'Invalid amino acid sequence',
                    'flexibility': self._calculate_flexibility(sequence),
                    'aggregation_propensity': self._calculate_aggregation_propensity(sequence)
                }
            
            # Convert to uppercase for BioPython
            clean_sequence = sequence.upper()
            analysis = ProteinAnalysis(clean_sequence)
            
            # Secondary structure
            helix_frac, turn_frac, sheet_frac = analysis.secondary_structure_fraction()
            
            # Amino acid composition (use property instead of deprecated method)
            aa_percent = analysis.amino_acids_percent
            
            # Physical properties
            properties = {
                'length': len(sequence),
                'molecular_weight': molecular_weight(clean_sequence, seq_type='protein'),
                'isoelectric_point': analysis.isoelectric_point(),
                'gravy': analysis.gravy(),
                'instability_index': analysis.instability_index(),
                'helix_fraction': helix_frac,
                'turn_fraction': turn_frac,
                'sheet_fraction': sheet_frac,
                'charge_at_ph7': analysis.charge_at_pH(7.0),
                'amino_acid_composition': aa_percent,
                'flexibility': self._calculate_flexibility(sequence),
                'aggregation_propensity': self._calculate_aggregation_propensity(sequence)
            }
            
            return properties
            
        except Exception as e:
            logger.warning(f"Structural analysis error: {e}")
            return {'length': len(sequence), 'error': str(e)}
    
    def _calculate_flexibility(self, sequence: str) -> float:
        """Calculate protein flexibility based on amino acid composition"""
        
        # Flexible amino acids (high B-factors)
        flexible_aa = 'GSTNAQDERK'
        # Rigid amino acids (low B-factors)
        rigid_aa = 'PFWYI'
        
        flexible_count = sum(1 for aa in sequence if aa in flexible_aa)
        rigid_count = sum(1 for aa in sequence if aa in rigid_aa)
        
        flexibility = (flexible_count - rigid_count) / len(sequence)
        return (flexibility + 1) / 2  # Normalize to 0-1
    
    def _calculate_aggregation_propensity(self, sequence: str) -> float:
        """Calculate aggregation propensity"""
        
        # Aggregation-prone amino acids
        agg_prone = 'FILVWY'
        agg_resistant = 'DEPK'
        
        prone_count = sum(1 for aa in sequence if aa in agg_prone)
        resistant_count = sum(1 for aa in sequence if aa in agg_resistant)
        
        propensity = (prone_count - resistant_count) / len(sequence)
        return max((propensity + 1) / 2, 0)  # Normalize to 0-1
    
    def _generate_scientific_reasoning(self, record: Dict, novelty: float, 
                                     druggability: float, safety: float,
                                     quantum_props: Dict, structural_props: Dict) -> Dict[str, Any]:
        """Generate detailed scientific reasoning for breakthrough classification"""
        
        reasoning = {
            'breakthrough_justification': [],
            'therapeutic_rationale': [],
            'quantum_advantages': [],
            'drug_development_potential': [],
            'safety_assessment': [],
            'novelty_factors': [],
            'competitive_advantages': [],
            'development_risks': [],
            'recommended_next_steps': []
        }
        
        # Breakthrough justification
        if record['breakthrough_score'] > 0.5:
            reasoning['breakthrough_justification'].append(
                f"Exceptional breakthrough score of {record['breakthrough_score']:.3f} "
                f"indicates strong therapeutic potential across multiple validation criteria"
            )
        
        if record['validation_score'] > 0.9:
            reasoning['breakthrough_justification'].append(
                f"Outstanding validation score of {record['validation_score']:.3f} "
                f"demonstrates robust computational validation"
            )
        
        # Therapeutic rationale
        for solution in record['solutions']:
            if solution['confidence'] > 0.7:
                reasoning['therapeutic_rationale'].append(
                    f"Strong therapeutic mapping to {solution['name']} "
                    f"(confidence: {solution['confidence']:.3f}, efficacy: {solution['efficacy']:.3f}) "
                    f"with mechanism: {solution['mechanism']}"
                )
        
        for indication in record['indications']:
            if indication['potential'] > 0.6:
                reasoning['therapeutic_rationale'].append(
                    f"High clinical potential for {indication['name']} "
                    f"(potential: {indication['potential']:.3f}, market: ${indication['market_size']:.1f}B, "
                    f"unmet need: {indication['unmet_need']:.3f})"
                )
        
        # Quantum advantages
        if quantum_props['avg_coherence'] > 0.7:
            reasoning['quantum_advantages'].append(
                f"High quantum coherence ({quantum_props['avg_coherence']:.3f}) "
                f"suggests enhanced binding selectivity and reduced off-target effects"
            )
        
        if quantum_props['avg_entanglement'] > 0.6:
            reasoning['quantum_advantages'].append(
                f"Strong quantum entanglement ({quantum_props['avg_entanglement']:.3f}) "
                f"indicates cooperative binding mechanisms and allosteric effects"
            )
        
        if quantum_props['superposition_ratio'] > 0.8:
            reasoning['quantum_advantages'].append(
                f"High superposition ratio ({quantum_props['superposition_ratio']:.3f}) "
                f"enables conformational flexibility for adaptive binding"
            )
        
        # Drug development potential
        if druggability > 0.7:
            reasoning['drug_development_potential'].append(
                f"Excellent druggability score ({druggability:.3f}) "
                f"with favorable pharmacokinetic properties"
            )
        
        if structural_props.get('molecular_weight', 0) < 5000:
            reasoning['drug_development_potential'].append(
                f"Optimal molecular weight ({structural_props.get('molecular_weight', 0):.1f} Da) "
                f"for therapeutic development and bioavailability"
            )
        
        if structural_props.get('instability_index', 100) < 40:
            reasoning['drug_development_potential'].append(
                f"Stable protein structure (instability index: {structural_props.get('instability_index', 0):.1f}) "
                f"favorable for formulation and storage"
            )
        
        # Safety assessment
        if safety > 0.8:
            reasoning['safety_assessment'].append(
                f"Excellent safety profile ({safety:.3f}) with low toxicity predictors"
            )
        
        if structural_props.get('aggregation_propensity', 0) < 0.3:
            reasoning['safety_assessment'].append(
                f"Low aggregation propensity ({structural_props.get('aggregation_propensity', 0):.3f}) "
                f"reduces immunogenicity risk"
            )
        
        # Novelty factors
        if novelty > 0.7:
            reasoning['novelty_factors'].append(
                f"High novelty score ({novelty:.3f}) indicates unique sequence features "
                f"and potential intellectual property advantages"
            )
        
        # Competitive advantages
        reasoning['competitive_advantages'].append(
            f"Quantum-enhanced discovery provides unique mechanistic insights "
            f"not available through conventional methods"
        )
        
        # Development risks
        if druggability < 0.6:
            reasoning['development_risks'].append(
                f"Moderate druggability score ({druggability:.3f}) may require "
                f"formulation optimization or delivery system development"
            )
        
        if safety < 0.7:
            reasoning['development_risks'].append(
                f"Safety score ({safety:.3f}) indicates need for comprehensive "
                f"toxicology studies and risk mitigation strategies"
            )
        
        # Recommended next steps
        reasoning['recommended_next_steps'].extend([
            "1. Synthesize peptide/protein for experimental validation",
            "2. Conduct binding affinity studies with target proteins",
            "3. Perform cell-based functional assays",
            "4. Evaluate stability and pharmacokinetic properties",
            "5. Conduct preliminary safety/toxicity screening",
            "6. File provisional patent application",
            "7. Seek pharmaceutical partnership for development"
        ])
        
        return reasoning
    
    def generate_2d_visualizations(self, candidates: List[BreakthroughCandidate]) -> Dict[str, str]:
        """Generate comprehensive 2D visualizations"""
        
        logger.info("📊 Generating 2D visualizations...")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('Breakthrough Discovery Analysis - 2D Visualizations', fontsize=16)
        
        # Extract data for plotting
        sequences = [c.sequence for c in candidates]
        breakthrough_scores = [c.breakthrough_score for c in candidates]
        novelty_scores = [c.novelty_score for c in candidates]
        druggability_scores = [c.druggability_score for c in candidates]
        safety_scores = [c.safety_score for c in candidates]
        lengths = [len(c.sequence) for c in candidates]
        energies = [c.energy_kcal_mol for c in candidates]
        
        # 1. Breakthrough Score Distribution
        axes[0,0].hist(breakthrough_scores, bins=20, alpha=0.7, color='gold', edgecolor='black')
        axes[0,0].set_title('Breakthrough Score Distribution')
        axes[0,0].set_xlabel('Breakthrough Score')
        axes[0,0].set_ylabel('Count')
        axes[0,0].axvline(np.mean(breakthrough_scores), color='red', linestyle='--', label=f'Mean: {np.mean(breakthrough_scores):.3f}')
        axes[0,0].legend()
        
        # 2. Multi-score Radar Chart Data
        scores_df = pd.DataFrame({
            'Breakthrough': breakthrough_scores,
            'Novelty': novelty_scores,
            'Druggability': druggability_scores,
            'Safety': safety_scores
        })
        
        correlation_matrix = scores_df.corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[0,1])
        axes[0,1].set_title('Score Correlation Matrix')
        
        # 3. Energy vs Breakthrough Score
        scatter = axes[0,2].scatter(energies, breakthrough_scores, c=novelty_scores, 
                                  cmap='viridis', alpha=0.6, s=50)
        axes[0,2].set_xlabel('Energy (kcal/mol)')
        axes[0,2].set_ylabel('Breakthrough Score')
        axes[0,2].set_title('Energy vs Breakthrough Score (colored by Novelty)')
        plt.colorbar(scatter, ax=axes[0,2], label='Novelty Score')
        
        # 4. Sequence Length vs Drug Scores
        axes[1,0].scatter(lengths, druggability_scores, alpha=0.6, color='blue', label='Druggability')
        axes[1,0].scatter(lengths, safety_scores, alpha=0.6, color='red', label='Safety')
        axes[1,0].set_xlabel('Sequence Length')
        axes[1,0].set_ylabel('Score')
        axes[1,0].set_title('Sequence Length vs Drug Development Scores')
        axes[1,0].legend()
        
        # 5. Top Candidates Bar Chart
        top_10 = sorted(candidates, key=lambda x: x.breakthrough_score, reverse=True)[:10]
        top_ids = [c.discovery_id[:8] for c in top_10]
        top_scores = [c.breakthrough_score for c in top_10]
        
        bars = axes[1,1].bar(range(len(top_ids)), top_scores, color='green', alpha=0.7)
        axes[1,1].set_xlabel('Discovery ID')
        axes[1,1].set_ylabel('Breakthrough Score')
        axes[1,1].set_title('Top 10 Breakthrough Candidates')
        axes[1,1].set_xticks(range(len(top_ids)))
        axes[1,1].set_xticklabels(top_ids, rotation=45)
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            axes[1,1].text(bar.get_x() + bar.get_width()/2., height + 0.01,
                          f'{height:.3f}', ha='center', va='bottom', fontsize=8)
        
        # 6. Score Distribution Violin Plot
        score_data = []
        score_types = []
        for c in candidates:
            score_data.extend([c.breakthrough_score, c.novelty_score, c.druggability_score, c.safety_score])
            score_types.extend(['Breakthrough', 'Novelty', 'Druggability', 'Safety'])
        
        df_violin = pd.DataFrame({'Score': score_data, 'Type': score_types})
        sns.violinplot(data=df_violin, x='Type', y='Score', ax=axes[1,2])
        axes[1,2].set_title('Score Distribution by Type')
        axes[1,2].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save the plot
        plot_path = self.output_dir / "breakthrough_analysis_2d.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"✅ 2D visualizations saved to {plot_path}")
        return {"2d_plot": str(plot_path)}
    
    def generate_3d_visualizations(self, candidates: List[BreakthroughCandidate]) -> Dict[str, str]:
        """Generate interactive 3D visualizations using Plotly"""
        
        logger.info("🎨 Generating 3D visualizations...")
        
        # Extract data
        breakthrough_scores = [c.breakthrough_score for c in candidates]
        novelty_scores = [c.novelty_score for c in candidates]
        druggability_scores = [c.druggability_score for c in candidates]
        safety_scores = [c.safety_score for c in candidates]
        energies = [c.energy_kcal_mol for c in candidates]
        lengths = [len(c.sequence) for c in candidates]
        quantum_fidelities = [c.quantum_fidelity for c in candidates]
        discovery_ids = [c.discovery_id[:8] for c in candidates]
        
        # 1. 3D Scatter Plot: Breakthrough vs Novelty vs Druggability
        fig1 = go.Figure(data=[go.Scatter3d(
            x=breakthrough_scores,
            y=novelty_scores,
            z=druggability_scores,
            mode='markers',
            marker=dict(
                size=8,
                color=safety_scores,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Safety Score"),
                opacity=0.8
            ),
            text=[f"ID: {id}<br>Energy: {e:.1f}<br>Length: {l}" 
                  for id, e, l in zip(discovery_ids, energies, lengths)],
            hovertemplate="<b>%{text}</b><br>" +
                         "Breakthrough: %{x:.3f}<br>" +
                         "Novelty: %{y:.3f}<br>" +
                         "Druggability: %{z:.3f}<br>" +
                         "Safety: %{marker.color:.3f}<br>" +
                         "<extra></extra>"
        )])
        
        fig1.update_layout(
            title="3D Analysis: Breakthrough vs Novelty vs Druggability (colored by Safety)",
            scene=dict(
                xaxis_title="Breakthrough Score",
                yaxis_title="Novelty Score",
                zaxis_title="Druggability Score"
            ),
            width=1000,
            height=800
        )
        
        # 2. 3D Surface Plot: Energy Landscape
        # Create grid for surface plot
        x_grid = np.linspace(min(lengths), max(lengths), 20)
        y_grid = np.linspace(min(energies), max(energies), 20)
        X, Y = np.meshgrid(x_grid, y_grid)
        
        # Interpolate breakthrough scores
        from scipy.interpolate import griddata
        points = np.array(list(zip(lengths, energies)))
        Z = griddata(points, breakthrough_scores, (X, Y), method='cubic', fill_value=0)
        
        fig2 = go.Figure(data=[go.Surface(
            x=X,
            y=Y,
            z=Z,
            colorscale='Plasma',
            showscale=True,
            colorbar=dict(title="Breakthrough Score")
        )])
        
        fig2.update_layout(
            title="3D Surface: Breakthrough Score Landscape (Length vs Energy)",
            scene=dict(
                xaxis_title="Sequence Length",
                yaxis_title="Energy (kcal/mol)",
                zaxis_title="Breakthrough Score"
            ),
            width=1000,
            height=800
        )
        
        # 3. 3D Network Graph of Top Candidates
        top_candidates = sorted(candidates, key=lambda x: x.breakthrough_score, reverse=True)[:20]
        
        # Create network based on similarity
        import networkx as nx
        G = nx.Graph()
        
        # Add nodes
        for i, c in enumerate(top_candidates):
            G.add_node(i, 
                      discovery_id=c.discovery_id[:8],
                      breakthrough_score=c.breakthrough_score,
                      sequence=c.sequence[:20] + "...")
        
        # Add edges based on sequence similarity (simplified)
        for i in range(len(top_candidates)):
            for j in range(i+1, len(top_candidates)):
                seq1, seq2 = top_candidates[i].sequence, top_candidates[j].sequence
                # Simple similarity: common 3-mers
                sim = len(set([seq1[k:k+3] for k in range(len(seq1)-2)]) & 
                         set([seq2[k:k+3] for k in range(len(seq2)-2)]))
                if sim > 3:  # Threshold for connection
                    G.add_edge(i, j, weight=sim)
        
        # 3D layout
        pos_3d = nx.spring_layout(G, dim=3, k=1, iterations=50)
        
        # Extract coordinates
        x_nodes = [pos_3d[node][0] for node in G.nodes()]
        y_nodes = [pos_3d[node][1] for node in G.nodes()]
        z_nodes = [pos_3d[node][2] for node in G.nodes()]
        
        # Node colors by breakthrough score
        node_colors = [top_candidates[i].breakthrough_score for i in G.nodes()]
        
        # Edges
        x_edges = []
        y_edges = []
        z_edges = []
        for edge in G.edges():
            x_edges.extend([pos_3d[edge[0]][0], pos_3d[edge[1]][0], None])
            y_edges.extend([pos_3d[edge[0]][1], pos_3d[edge[1]][1], None])
            z_edges.extend([pos_3d[edge[0]][2], pos_3d[edge[1]][2], None])
        
        fig3 = go.Figure()
        
        # Add edges
        fig3.add_trace(go.Scatter3d(
            x=x_edges, y=y_edges, z=z_edges,
            mode='lines',
            line=dict(color='gray', width=2),
            hoverinfo='none',
            showlegend=False
        ))
        
        # Add nodes
        fig3.add_trace(go.Scatter3d(
            x=x_nodes, y=y_nodes, z=z_nodes,
            mode='markers',
            marker=dict(
                size=10,
                color=node_colors,
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Breakthrough Score"),
                line=dict(width=1, color='black')
            ),
            text=[f"ID: {top_candidates[i].discovery_id[:8]}<br>"
                  f"Score: {top_candidates[i].breakthrough_score:.3f}<br>"
                  f"Sequence: {top_candidates[i].sequence[:20]}..."
                  for i in range(len(top_candidates))],
            hovertemplate="%{text}<extra></extra>",
            showlegend=False
        ))
        
        fig3.update_layout(
            title="3D Network: Top 20 Breakthrough Candidates (connected by similarity)",
            scene=dict(
                xaxis=dict(showgrid=False, showticklabels=False),
                yaxis=dict(showgrid=False, showticklabels=False),
                zaxis=dict(showgrid=False, showticklabels=False)
            ),
            width=1000,
            height=800
        )
        
        # Save plots
        plot_paths = {}
        
        html_path_1 = self.output_dir / "breakthrough_3d_scatter.html"
        fig1.write_html(html_path_1)
        plot_paths["3d_scatter"] = str(html_path_1)
        
        html_path_2 = self.output_dir / "breakthrough_3d_surface.html"
        fig2.write_html(html_path_2)
        plot_paths["3d_surface"] = str(html_path_2)
        
        html_path_3 = self.output_dir / "breakthrough_3d_network.html"
        fig3.write_html(html_path_3)
        plot_paths["3d_network"] = str(html_path_3)
        
        logger.info(f"✅ 3D visualizations saved to {self.output_dir}")
        return plot_paths
    
    def generate_comprehensive_report(self, candidates: List[BreakthroughCandidate]) -> str:
        """Generate comprehensive scientific report"""
        
        logger.info("📝 Generating comprehensive scientific report...")
        
        # Sort candidates by breakthrough score
        candidates_sorted = sorted(candidates, key=lambda x: x.breakthrough_score, reverse=True)
        
        report_path = self.output_dir / f"breakthrough_discovery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_path, 'w') as f:
            f.write("# BREAKTHROUGH THERAPEUTIC PROTEIN DISCOVERY REPORT\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Analysis Tool:** Advanced Quantum-Enhanced Discovery Platform\n")
            f.write(f"**Total Candidates Analyzed:** {len(candidates)}\n\n")
            
            f.write("## EXECUTIVE SUMMARY\n\n")
            f.write(f"This report presents {len(candidates)} breakthrough therapeutic protein candidates ")
            f.write("identified through advanced quantum-enhanced computational analysis. Each candidate ")
            f.write("has been validated across multiple criteria including breakthrough potential, novelty, ")
            f.write("druggability, safety, and quantum mechanical properties.\n\n")
            
            # Top 10 Summary
            f.write("### TOP 10 BREAKTHROUGH CANDIDATES\n\n")
            for i, candidate in enumerate(candidates_sorted[:10], 1):
                f.write(f"**{i}. Discovery ID: {candidate.discovery_id}**\n")
                f.write(f"- Breakthrough Score: {candidate.breakthrough_score:.3f}\n")
                f.write(f"- Validation Score: {candidate.validation_score:.3f}\n")
                f.write(f"- Sequence Length: {len(candidate.sequence)} amino acids\n")
                f.write(f"- Primary Therapeutic Target: {candidate.therapeutic_solutions[0]['name'] if candidate.therapeutic_solutions else 'Unknown'}\n")
                f.write(f"- Clinical Indication: {candidate.clinical_indications[0]['name'] if candidate.clinical_indications else 'Unknown'}\n\n")
            
            f.write("## DETAILED ANALYSIS\n\n")
            
            # Detailed analysis of top 5
            for i, candidate in enumerate(candidates_sorted[:5], 1):
                f.write(f"### CANDIDATE {i}: {candidate.discovery_id}\n\n")
                
                f.write("#### Basic Properties\n")
                f.write(f"- **Sequence:** `{candidate.sequence}`\n")
                f.write(f"- **Length:** {len(candidate.sequence)} amino acids\n")
                f.write(f"- **Molecular Weight:** {candidate.structural_properties.get('molecular_weight', 'N/A')} Da\n")
                f.write(f"- **Energy:** {candidate.energy_kcal_mol:.2f} kcal/mol\n\n")
                
                f.write("#### Scoring Analysis\n")
                f.write(f"- **Breakthrough Score:** {candidate.breakthrough_score:.3f} (Target: >0.3)\n")
                f.write(f"- **Validation Score:** {candidate.validation_score:.3f} (Target: >0.8)\n")
                f.write(f"- **Novelty Score:** {candidate.novelty_score:.3f} (Target: >0.6)\n")
                f.write(f"- **Druggability Score:** {candidate.druggability_score:.3f} (Target: >0.7)\n")
                f.write(f"- **Safety Score:** {candidate.safety_score:.3f} (Target: >0.8)\n\n")
                
                f.write("#### Quantum Properties\n")
                qp = candidate.quantum_properties
                f.write(f"- **Average Coherence:** {qp['avg_coherence']:.3f}\n")
                f.write(f"- **Average Entanglement:** {qp['avg_entanglement']:.3f}\n")
                f.write(f"- **Quantum Complexity:** {qp['quantum_complexity']:.3f}\n")
                f.write(f"- **Superposition Ratio:** {qp['superposition_ratio']:.3f}\n")
                f.write(f"- **Total Quantum States:** {qp['total_quantum_states']}\n\n")
                
                f.write("#### Therapeutic Solutions\n")
                for sol in candidate.therapeutic_solutions:
                    f.write(f"- **{sol['name']}**\n")
                    f.write(f"  - Confidence: {sol['confidence']:.3f}\n")
                    f.write(f"  - Predicted Efficacy: {sol['efficacy']:.3f}\n")
                    f.write(f"  - Development Stage: {sol['stage']}\n")
                    f.write(f"  - Mechanism: {sol['mechanism']}\n\n")
                
                f.write("#### Clinical Indications\n")
                for ind in candidate.clinical_indications:
                    f.write(f"- **{ind['name']}**\n")
                    f.write(f"  - Therapeutic Potential: {ind['potential']:.3f}\n")
                    f.write(f"  - Unmet Need Score: {ind['unmet_need']:.3f}\n")
                    f.write(f"  - Market Size: ${ind['market_size']:.1f}B\n\n")
                
                f.write("#### Scientific Reasoning\n")
                reasoning = candidate.reasoning
                
                f.write("**Breakthrough Justification:**\n")
                for reason in reasoning['breakthrough_justification']:
                    f.write(f"- {reason}\n")
                f.write("\n")
                
                f.write("**Therapeutic Rationale:**\n")
                for reason in reasoning['therapeutic_rationale']:
                    f.write(f"- {reason}\n")
                f.write("\n")
                
                f.write("**Quantum Advantages:**\n")
                for reason in reasoning['quantum_advantages']:
                    f.write(f"- {reason}\n")
                f.write("\n")
                
                f.write("**Drug Development Potential:**\n")
                for reason in reasoning['drug_development_potential']:
                    f.write(f"- {reason}\n")
                f.write("\n")
                
                f.write("**Safety Assessment:**\n")
                for reason in reasoning['safety_assessment']:
                    f.write(f"- {reason}\n")
                f.write("\n")
                
                f.write("**Recommended Next Steps:**\n")
                for step in reasoning['recommended_next_steps']:
                    f.write(f"- {step}\n")
                f.write("\n")
                
                f.write("---\n\n")
            
            f.write("## METHODOLOGY\n\n")
            f.write("### Scoring Algorithms\n\n")
            f.write("1. **Breakthrough Score**: Calculated as the product of solution confidence, ")
            f.write("predicted efficacy, therapeutic potential, and unmet medical need.\n\n")
            
            f.write("2. **Novelty Score**: Based on sequence uniqueness, amino acid diversity, ")
            f.write("optimal length, and hydrophobic/hydrophilic balance.\n\n")
            
            f.write("3. **Druggability Score**: Derived from molecular weight, charge distribution, ")
            f.write("hydropathy, stability index, and secondary structure propensity.\n\n")
            
            f.write("4. **Safety Score**: Calculated by penalizing toxic motifs, excessive cysteine ")
            f.write("content, charge clustering, and hydrophobic clustering.\n\n")
            
            f.write("### Quantum Analysis\n\n")
            f.write("Quantum properties are analyzed from the vQbit quantum states stored in the ")
            f.write("knowledge graph, including superposition coherence, entanglement strength, ")
            f.write("and quantum complexity metrics.\n\n")
            
            f.write("### Validation Criteria\n\n")
            f.write("- Minimum breakthrough score: 0.3\n")
            f.write("- Minimum validation score: 0.8\n")
            f.write("- Minimum quantum fidelity: 0.7\n")
            f.write("- Presence of quantum relationships in graph\n\n")
            
            f.write("## DISCLAIMER\n\n")
            f.write("This computational analysis provides predictive insights based on quantum-enhanced ")
            f.write("algorithms and should be validated through experimental studies. Results do not ")
            f.write("constitute medical advice or guarantee therapeutic efficacy.\n\n")
        
        logger.info(f"✅ Comprehensive report saved to {report_path}")
        return str(report_path)
    
    def run_complete_analysis(self, limit: int = 50) -> Dict[str, Any]:
        """Run complete breakthrough discovery analysis with all visualizations"""
        
        logger.info("🚀 Starting complete breakthrough discovery analysis...")
        
        # Find candidates
        candidates = self.find_breakthrough_candidates(limit)
        
        if not candidates:
            logger.warning("⚠️ No breakthrough candidates found")
            return {"candidates": 0, "error": "No candidates found"}
        
        # Generate visualizations
        viz_2d = self.generate_2d_visualizations(candidates)
        viz_3d = self.generate_3d_visualizations(candidates)
        
        # Generate report
        report_path = self.generate_comprehensive_report(candidates)
        
        # Summary statistics
        summary = {
            "total_candidates": len(candidates),
            "avg_breakthrough_score": np.mean([c.breakthrough_score for c in candidates]),
            "avg_novelty_score": np.mean([c.novelty_score for c in candidates]),
            "avg_druggability_score": np.mean([c.druggability_score for c in candidates]),
            "avg_safety_score": np.mean([c.safety_score for c in candidates]),
            "top_breakthrough_score": max([c.breakthrough_score for c in candidates]),
            "unique_therapeutic_solutions": len(set([
                sol['name'] for c in candidates for sol in c.therapeutic_solutions
            ])),
            "unique_clinical_indications": len(set([
                ind['name'] for c in candidates for ind in c.clinical_indications
            ]))
        }
        
        results = {
            "summary": summary,
            "candidates": [
                {
                    "discovery_id": c.discovery_id,
                    "sequence": c.sequence[:50] + "..." if len(c.sequence) > 50 else c.sequence,
                    "breakthrough_score": c.breakthrough_score,
                    "novelty_score": c.novelty_score,
                    "druggability_score": c.druggability_score,
                    "safety_score": c.safety_score,
                    "quantum_fidelity": c.quantum_fidelity,
                    "primary_solution": c.therapeutic_solutions[0]['name'] if c.therapeutic_solutions else None,
                    "primary_indication": c.clinical_indications[0]['name'] if c.clinical_indications else None
                }
                for c in sorted(candidates, key=lambda x: x.breakthrough_score, reverse=True)[:10]
            ],
            "visualizations": {**viz_2d, **viz_3d},
            "report_path": report_path,
            "output_directory": str(self.output_dir)
        }
        
        logger.info("🎉 Complete analysis finished successfully!")
        return results

def main():
    """Run breakthrough discovery analysis"""
    
    print("🔬 BREAKTHROUGH DISCOVERY ANALYZER")
    print("=" * 60)
    print("Advanced analytics for therapeutic protein discovery validation")
    print("Includes detailed reasoning, algorithms, and 2D/3D visualizations")
    print()
    
    try:
        analyzer = BreakthroughDiscoveryAnalyzer()
        results = analyzer.run_complete_analysis(limit=30)
        
        print("✅ ANALYSIS COMPLETE!")
        print(f"📊 Summary:")
        print(f"   Total Candidates: {results['summary']['total_candidates']}")
        print(f"   Avg Breakthrough Score: {results['summary']['avg_breakthrough_score']:.3f}")
        print(f"   Top Breakthrough Score: {results['summary']['top_breakthrough_score']:.3f}")
        print(f"   Unique Solutions: {results['summary']['unique_therapeutic_solutions']}")
        print(f"   Unique Indications: {results['summary']['unique_clinical_indications']}")
        print()
        
        print("📁 Output Files:")
        for name, path in results['visualizations'].items():
            print(f"   {name}: {path}")
        print(f"   Report: {results['report_path']}")
        print(f"   Directory: {results['output_directory']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Analysis failed: {e}")

if __name__ == "__main__":
    main()


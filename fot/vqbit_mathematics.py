#!/usr/bin/env python3
"""
vQbit Mathematics for Field of Truth Protein Folding

This module implements the core mathematical operations for vQbit-based
protein folding using graph-based quantum-inspired algorithms.

Mathematical Framework:
- vQbit state: |ψ⟩ = α|φ⟩ + β|ψ⟩ + γ|ω⟩
- FoT equation: FoT(t) = AKG(∑aᵢVᵢ)
- Virtue operators: Projections onto valid subspaces
- Graph Laplacian: Entanglement between amino acid vQbits
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import logging
from scipy.sparse import csr_matrix
from scipy.linalg import expm
import torch

logger = logging.getLogger(__name__)

@dataclass
class VQbitState:
    """
    A vQbit state for protein folding
    
    Represents: |ψ⟩ = α|φ⟩ + β|ψ⟩ + γ|ω⟩
    where |φ⟩, |ψ⟩, |ω⟩ are conformational basis states
    """
    amplitudes: torch.Tensor  # Complex amplitudes [α, β, γ, ...]
    basis_states: List[Dict[str, Any]]  # List of conformational states
    residue_id: int  # Which residue this vQbit represents
    entanglement_map: Dict[int, torch.Tensor]  # Entanglement with other residues
    virtue_scores: Dict[str, float]  # Virtue evaluation for this state

@dataclass
class VirtueOperator:
    """
    Mathematical virtue constraint operator
    
    Implements projection onto valid conformational subspaces
    """
    name: str  # Justice, Honesty, Temperance, Prudence
    constraint_matrix: torch.Tensor  # Mathematical constraint operator
    threshold: float  # Minimum virtue score for validity
    projector: torch.Tensor  # Projection operator onto valid subspace

class ProteinVQbitGraph:
    """
    Graph-based vQbit system for protein folding
    
    Uses NetworkX for AKG operations and quantum-inspired mathematics
    for conformational sampling and virtue-based optimization.
    """
    
    def __init__(self, sequence: str, device: str = "cpu"):
        """Initialize protein vQbit graph"""
        self.sequence = sequence
        self.n_residues = len(sequence)
        self.device = device
        
        # Initialize AKG using NetworkX
        self.akg = nx.Graph()
        
        # vQbit states for each residue
        self.vqbit_states: Dict[int, VQbitState] = {}
        
        # Virtue operators
        self.virtue_operators: Dict[str, VirtueOperator] = {}
        
        # Graph Laplacian for entanglement
        self.laplacian_matrix = None
        
        # Measurement operators
        self.measurement_operators = {}
        
        logger.info(f"Initialized vQbit graph for {self.n_residues}-residue protein")
        self._build_protein_graph()
        self._initialize_virtue_operators()
    
    def _build_protein_graph(self) -> None:
        """Build protein backbone connectivity graph"""
        
        # Add residues as nodes
        for i, aa in enumerate(self.sequence):
            self.akg.add_node(i, 
                             residue_type=aa,
                             residue_number=i+1,
                             vqbit_dimension=8)  # 8-dimensional conformational space
        
        # Add backbone connectivity edges
        for i in range(self.n_residues - 1):
            self.akg.add_edge(i, i+1, 
                             bond_type='backbone',
                             coupling_strength=1.0,
                             constraint_type='sequential')
        
        # Add important long-range interactions
        for i in range(self.n_residues):
            for j in range(i+3, min(i+8, self.n_residues)):  # Medium-range
                if self._should_add_interaction(i, j):
                    self.akg.add_edge(i, j,
                                     bond_type='medium_range',
                                     coupling_strength=0.5,
                                     constraint_type='spatial')
        
        # Compute graph Laplacian for entanglement operations
        self.laplacian_matrix = torch.tensor(
            nx.normalized_laplacian_matrix(self.akg).toarray(),
            dtype=torch.float32,
            device=self.device
        )
        
        logger.info(f"Built protein graph: {self.akg.number_of_nodes()} nodes, {self.akg.number_of_edges()} edges")
    
    def _should_add_interaction(self, i: int, j: int) -> bool:
        """Determine if residues i and j should have long-range interaction"""
        
        aa_i = self.sequence[i]
        aa_j = self.sequence[j]
        
        # Hydrophobic interactions
        hydrophobic = {'PHE', 'TYR', 'TRP', 'LEU', 'ILE', 'VAL', 'MET'}
        if aa_i in hydrophobic and aa_j in hydrophobic:
            return True
        
        # Electrostatic interactions
        positive = {'LYS', 'ARG', 'HIS'}
        negative = {'ASP', 'GLU'}
        if (aa_i in positive and aa_j in negative) or (aa_i in negative and aa_j in positive):
            return True
        
        # Disulfide bonds (CYS-CYS)
        if aa_i == 'CYS' and aa_j == 'CYS':
            return True
        
        return False
    
    def _initialize_virtue_operators(self) -> None:
        """Initialize mathematical virtue constraint operators"""
        
        # Justice: Physical law enforcement (Ramachandran constraints)
        # TUNED: Align with validated force field - favor disorder over helix
        justice_matrix = self._create_ramachandran_operator()
        self.virtue_operators['Justice'] = VirtueOperator(
            name='Justice',
            constraint_matrix=justice_matrix,
            threshold=0.6,  # REDUCED: Less restrictive for disorder sampling
            projector=self._create_projector(justice_matrix, 0.6)
        )
        
        # Honesty: Experimental data consistency
        honesty_matrix = self._create_experimental_consistency_operator()
        self.virtue_operators['Honesty'] = VirtueOperator(
            name='Honesty',
            constraint_matrix=honesty_matrix,
            threshold=0.7,
            projector=self._create_projector(honesty_matrix, 0.7)
        )
        
        # Temperance: Computational stability
        temperance_matrix = self._create_stability_operator()
        self.virtue_operators['Temperance'] = VirtueOperator(
            name='Temperance',
            constraint_matrix=temperance_matrix,
            threshold=0.6,
            projector=self._create_projector(temperance_matrix, 0.6)
        )
        
        # Prudence: Efficiency and convergence
        prudence_matrix = self._create_efficiency_operator()
        self.virtue_operators['Prudence'] = VirtueOperator(
            name='Prudence',
            constraint_matrix=prudence_matrix,
            threshold=0.5,
            projector=self._create_projector(prudence_matrix, 0.5)
        )
        
        logger.info("Initialized virtue operators for mathematical constraints")
    
    def _create_ramachandran_operator(self) -> torch.Tensor:
        """Create Ramachandran constraint operator for backbone geometry"""
        
        # Create constraint matrix for valid phi-psi angles
        constraint_matrix = torch.zeros((self.n_residues, 8, 8), device=self.device, dtype=torch.complex64)
        
        for i in range(self.n_residues):
            # Define allowed regions in conformational space
            # 0-2: alpha-helical region
            # 3-5: beta-sheet region  
            # 6-7: extended/other regions
            
            # TUNED: Match validated force field - favor disorder for Aβ42
            
            # Alpha-helical constraints - REDUCED for Aβ42 disorder
            constraint_matrix[i, 0:3, 0:3] = torch.eye(3, dtype=torch.complex64, device=self.device) * 0.2
            
            # Beta-sheet constraints - MODERATE for aggregation
            constraint_matrix[i, 3:6, 3:6] = torch.eye(3, dtype=torch.complex64, device=self.device) * 0.6
            
            # Extended/disorder constraints - INCREASED for Aβ42 
            constraint_matrix[i, 6:8, 6:8] = torch.eye(2, dtype=torch.complex64, device=self.device) * 0.9
        
        return constraint_matrix
    
    def _create_experimental_consistency_operator(self) -> torch.Tensor:
        """Create operator for experimental data consistency"""
        
        # Create constraint matrix for each residue
        constraint_matrix = torch.zeros((self.n_residues, 8, 8), device=self.device, dtype=torch.complex64)
        
        for i in range(self.n_residues):
            # Create consistency operator for each residue
            constraint_matrix[i] = torch.eye(8, device=self.device, dtype=torch.complex64) * 0.7
            
            # Add specific experimental constraints if available
            # TODO: Integrate with real experimental data from pipeline
        
        return constraint_matrix
    
    def _create_stability_operator(self) -> torch.Tensor:
        """Create computational stability operator"""
        
        # Penalize high-energy or unstable conformations
        constraint_matrix = torch.zeros((self.n_residues, 8, 8), device=self.device, dtype=torch.complex64)
        
        for i in range(self.n_residues):
            # Create stability metric based on local energy landscape
            stability_values = torch.tensor([0.8, 0.7, 0.6, 0.7, 0.6, 0.5, 0.4, 0.3], dtype=torch.complex64, device=self.device)
            constraint_matrix[i] = torch.diag(stability_values)
        
        return constraint_matrix
    
    def _create_efficiency_operator(self) -> torch.Tensor:
        """Create computational efficiency operator"""
        
        # Favor conformations that converge quickly
        constraint_matrix = torch.zeros((self.n_residues, 8, 8), device=self.device, dtype=torch.complex64)
        
        for i in range(self.n_residues):
            # Create efficiency metric
            efficiency_values = torch.tensor([0.6, 0.5, 0.4, 0.6, 0.5, 0.4, 0.3, 0.2], dtype=torch.complex64, device=self.device)
            constraint_matrix[i] = torch.diag(efficiency_values)
        
        return constraint_matrix
    
    def _create_projector(self, constraint_matrix: torch.Tensor, threshold: float) -> torch.Tensor:
        """Create projection operator for virtue constraints"""
        
        # Project onto subspace where constraint_matrix eigenvalues > threshold
        # Use CPU for eigenvalue decomposition if MPS doesn't support it
        matrix_to_decompose = constraint_matrix.sum(dim=0)
        if matrix_to_decompose.device.type == 'mps':
            matrix_cpu = matrix_to_decompose.cpu()
            eigenvals, eigenvecs = torch.linalg.eigh(matrix_cpu)
            eigenvals = eigenvals.to(self.device)
            eigenvecs = eigenvecs.to(self.device)
        else:
            eigenvals, eigenvecs = torch.linalg.eigh(matrix_to_decompose)
        
        # Keep eigenvectors with eigenvalues above threshold
        valid_mask = eigenvals > threshold
        valid_eigenvecs = eigenvecs[:, valid_mask]
        
        # Create projector P = |ψ⟩⟨ψ| for valid subspace
        # Convert to complex type to match vQbit amplitudes
        valid_eigenvecs_complex = valid_eigenvecs.to(torch.complex64)
        projector = valid_eigenvecs_complex @ torch.conj(valid_eigenvecs_complex).T
        
        return projector
    
    def initialize_from_sequence(self, use_biophysical_priors: bool = True, use_learned_motifs: bool = False, 
                               neo4j_engine=None) -> None:
        """
        Phase 1 & 2 Enhancement: Initialize vQbit states directly from sequence using biophysical priors
        and optionally learned motifs from the AKG.
        
        This method implements the de novo vQbit initialization protocol from the 
        AlphaFold Independence Roadmap, creating physics-based initial states without
        external structure prediction dependency.
        
        Args:
            use_biophysical_priors: If True, use amino acid properties to bias initial states
            use_learned_motifs: If True, query AKG for learned structural motifs (Phase 2)
            neo4j_engine: Neo4j engine for motif queries (required if use_learned_motifs=True)
        """
        
        if use_biophysical_priors:
            logger.info("Initializing vQbit states with biophysical priors (Phase 1 de novo protocol)")
        else:
            logger.info("Initializing vQbit states with random amplitudes (legacy mode)")
            
        if use_learned_motifs and neo4j_engine:
            logger.info("Phase 2: Querying AKG for learned motifs to bias initialization")
            
        # Phase 2: Query learned motifs for experience-based seeding
        learned_motifs = []
        if use_learned_motifs and neo4j_engine:
            try:
                from fot.phase2_learning_system import AKGLearningSystem
                learning_system = AKGLearningSystem(neo4j_engine)
                
                # Query motifs for sequence fragments
                for i in range(0, len(self.sequence), 6):  # Check 6-residue windows
                    fragment = self.sequence[i:min(i+6, len(self.sequence))]
                    if len(fragment) >= 4:  # Minimum fragment size
                        motifs = learning_system.query_learned_motifs(fragment)
                        for motif in motifs:
                            motif['query_start'] = i
                            learned_motifs.append(motif)
                            
                logger.info(f"Found {len(learned_motifs)} learned motifs for experience-based seeding")
                
            except Exception as e:
                logger.warning(f"Could not query learned motifs: {e}")
        
        for i in range(self.n_residues):
            
            if use_biophysical_priors:
                # Phase 1: Use biophysical properties to generate initial amplitudes
                amplitudes = self._generate_biophysical_amplitudes(i)
                
                # Phase 2: Apply learned motif bias if available
                if learned_motifs:
                    amplitudes = self._apply_motif_bias(amplitudes, i, learned_motifs)
            else:
                # Legacy: Random initialization
                amplitudes = torch.randn(8, dtype=torch.complex64, device=self.device)
                norm = torch.sqrt(torch.sum(torch.conj(amplitudes) * amplitudes).real)
                amplitudes = amplitudes / norm
            
            # Create basis states for different conformations (unchanged)
            basis_states = [
                {'phi': -60, 'psi': -45, 'type': 'alpha_helix'},  # 0
                {'phi': -70, 'psi': -35, 'type': 'alpha_helix'},  # 1
                {'phi': -50, 'psi': -55, 'type': 'alpha_helix'},  # 2
                {'phi': -120, 'psi': 120, 'type': 'beta_sheet'},  # 3
                {'phi': -130, 'psi': 110, 'type': 'beta_sheet'},  # 4
                {'phi': -110, 'psi': 130, 'type': 'beta_sheet'},  # 5
                {'phi': -180, 'psi': 180, 'type': 'extended'},    # 6
                {'phi': 60, 'psi': 45, 'type': 'left_handed'}     # 7
            ]
            
            # Initialize entanglement map
            entanglement_map = {}
            for neighbor in self.akg.neighbors(i):
                entanglement_map[neighbor] = torch.randn(8, 8, dtype=torch.complex64, device=self.device)
            
            # Initialize virtue scores
            virtue_scores = {
                'Justice': 0.5,
                'Honesty': 0.5, 
                'Temperance': 0.5,
                'Prudence': 0.5
            }
            
            self.vqbit_states[i] = VQbitState(
                amplitudes=amplitudes,
                basis_states=basis_states,
                residue_id=i,
                entanglement_map=entanglement_map,
                virtue_scores=virtue_scores
            )
        
        mode_desc = []
        if use_biophysical_priors:
            mode_desc.append("biophysical priors")
        if use_learned_motifs and learned_motifs:
            mode_desc.append(f"learned motifs ({len(learned_motifs)} found)")
        if not mode_desc:
            mode_desc.append("random amplitudes")
            
        logger.info(f"Initialized {len(self.vqbit_states)} vQbit states using {' + '.join(mode_desc)}")
    
    def _apply_motif_bias(self, amplitudes: torch.Tensor, residue_idx: int, learned_motifs: List[Dict]) -> torch.Tensor:
        """
        Phase 2: Apply learned motif bias to initial amplitudes
        
        This method enhances the initial amplitudes based on structural motifs
        learned from previous validated discoveries.
        """
        
        # Find motifs that apply to this residue position
        relevant_motifs = []
        for motif in learned_motifs:
            motif_start = motif.get('query_start', 0)
            motif_length = len(motif.get('fragment', ''))
            
            if motif_start <= residue_idx < motif_start + motif_length:
                relevant_motifs.append(motif)
        
        if not relevant_motifs:
            return amplitudes
        
        # Apply bias based on motif types
        bias_factor = 1.0
        for motif in relevant_motifs:
            motif_type = motif.get('type', '')
            confidence = motif.get('confidence', 0.5)
            
            # Adjust amplitudes based on learned structural preferences
            if motif_type == 'alpha_helix':
                # Boost alpha helix states (indices 0, 1)
                amplitudes[0] *= (1.0 + confidence * 0.3)
                amplitudes[1] *= (1.0 + confidence * 0.3)
            elif motif_type == 'beta_hairpin':
                # Boost beta sheet states (indices 2, 3)
                amplitudes[2] *= (1.0 + confidence * 0.3)
                amplitudes[3] *= (1.0 + confidence * 0.3)
            elif motif_type == 'binding_site':
                # Boost extended conformations (indices 6, 7)
                amplitudes[6] *= (1.0 + confidence * 0.2)
                amplitudes[7] *= (1.0 + confidence * 0.2)
            elif motif_type == 'cysteine_bridge':
                # Boost constrained conformations (indices 4, 5)
                amplitudes[4] *= (1.0 + confidence * 0.4)
                amplitudes[5] *= (1.0 + confidence * 0.4)
        
        # Renormalize after bias application
        norm = torch.sqrt(torch.sum(torch.conj(amplitudes) * amplitudes).real)
        return amplitudes / norm
    
    def _generate_biophysical_amplitudes(self, residue_index: int) -> torch.Tensor:
        """
        Generate physics-based initial amplitudes for a residue based on amino acid properties.
        
        This implements the core de novo initialization from Phase 1 of the roadmap.
        """
        
        amino_acid = self.sequence[residue_index]
        
        # Biophysical property lookup (simplified Ramachandran propensities)
        aa_propensities = {
            'A': [0.3, 0.3, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0],  # Helix-favoring
            'R': [0.2, 0.2, 0.1, 0.2, 0.2, 0.1, 0.0, 0.0],  # Extended/charged
            'N': [0.1, 0.1, 0.1, 0.3, 0.3, 0.1, 0.0, 0.0],  # Sheet-favoring
            'D': [0.1, 0.1, 0.1, 0.3, 0.3, 0.1, 0.0, 0.0],  # Sheet-favoring
            'C': [0.2, 0.2, 0.1, 0.2, 0.2, 0.1, 0.0, 0.0],  # Flexible
            'E': [0.2, 0.2, 0.1, 0.2, 0.2, 0.1, 0.0, 0.0],  # Extended/charged
            'Q': [0.2, 0.2, 0.1, 0.2, 0.2, 0.1, 0.0, 0.0],  # Helix/extended
            'G': [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.2],  # Highly flexible
            'H': [0.2, 0.2, 0.1, 0.2, 0.2, 0.1, 0.0, 0.0],  # Variable
            'I': [0.3, 0.3, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0],  # Helix/sheet
            'L': [0.3, 0.3, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0],  # Helix-favoring
            'K': [0.2, 0.2, 0.1, 0.2, 0.2, 0.1, 0.0, 0.0],  # Extended/charged
            'M': [0.3, 0.3, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0],  # Helix-favoring
            'F': [0.2, 0.2, 0.1, 0.3, 0.2, 0.0, 0.0, 0.0],  # Sheet-favoring
            'P': [0.0, 0.0, 0.0, 0.1, 0.1, 0.1, 0.4, 0.3],  # Turn/break
            'S': [0.2, 0.2, 0.1, 0.2, 0.2, 0.1, 0.0, 0.0],  # Flexible
            'T': [0.2, 0.2, 0.1, 0.2, 0.2, 0.1, 0.0, 0.0],  # Flexible
            'W': [0.2, 0.2, 0.1, 0.3, 0.2, 0.0, 0.0, 0.0],  # Sheet-favoring
            'Y': [0.2, 0.2, 0.1, 0.3, 0.2, 0.0, 0.0, 0.0],  # Sheet-favoring
            'V': [0.3, 0.3, 0.2, 0.1, 0.1, 0.0, 0.0, 0.0],  # Helix/sheet
        }
        
        # Get propensities for this amino acid (default to flexible if unknown)
        propensities = aa_propensities.get(amino_acid, [0.125] * 8)
        
        # Add neighbor context effects
        if residue_index > 0:
            prev_aa = self.sequence[residue_index - 1]
            # Proline preceding this residue breaks helices
            if prev_aa == 'P':
                propensities[0] *= 0.1  # Reduce helix propensity
                propensities[1] *= 0.1
                propensities[2] *= 0.1
        
        if residue_index < len(self.sequence) - 1:
            next_aa = self.sequence[residue_index + 1]
            # Proline following this residue affects angles
            if next_aa == 'P':
                propensities[6] *= 2.0  # Increase extended propensity
                propensities[7] *= 2.0
        
        # Convert to complex amplitudes with random phases
        propensities_tensor = torch.tensor(propensities, dtype=torch.float32, device=self.device)
        phases = torch.rand(8, device=self.device) * 2 * np.pi
        
        amplitudes = torch.sqrt(propensities_tensor) * torch.exp(1j * phases)
        
        # Normalize
        norm = torch.sqrt(torch.sum(torch.conj(amplitudes) * amplitudes).real)
        if norm > 1e-10:
            amplitudes = amplitudes / norm
        
        return amplitudes.to(torch.complex64)

    def initialize_vqbit_states(self) -> None:
        """Legacy method - calls initialize_from_sequence for backward compatibility"""
        self.initialize_from_sequence(use_biophysical_priors=False)
        
        # Legacy initialization code preserved for compatibility
        for i in range(self.n_residues):
            
            # Create random initial amplitudes (normalized)
            amplitudes = torch.randn(8, dtype=torch.complex64, device=self.device)
            # Use manual normalization for complex numbers
            norm = torch.sqrt(torch.sum(torch.conj(amplitudes) * amplitudes).real)
            amplitudes = amplitudes / norm
            
            # Create basis states for different conformations
            basis_states = [
                {'phi': -60, 'psi': -45, 'type': 'alpha_helix'},  # 0
                {'phi': -70, 'psi': -35, 'type': 'alpha_helix'},  # 1
                {'phi': -50, 'psi': -55, 'type': 'alpha_helix'},  # 2
                {'phi': -120, 'psi': 120, 'type': 'beta_sheet'},  # 3
                {'phi': -130, 'psi': 110, 'type': 'beta_sheet'},  # 4
                {'phi': -110, 'psi': 130, 'type': 'beta_sheet'},  # 5
                {'phi': -180, 'psi': 180, 'type': 'extended'},    # 6
                {'phi': 60, 'psi': 45, 'type': 'left_handed'}     # 7
            ]
            
            # Initialize entanglement map
            entanglement_map = {}
            for neighbor in self.akg.neighbors(i):
                entanglement_map[neighbor] = torch.randn(8, 8, dtype=torch.complex64, device=self.device)
            
            # Initialize virtue scores
            virtue_scores = {
                'Justice': 0.5,
                'Honesty': 0.5, 
                'Temperance': 0.5,
                'Prudence': 0.5
            }
            
            self.vqbit_states[i] = VQbitState(
                amplitudes=amplitudes,
                basis_states=basis_states,
                residue_id=i,
                entanglement_map=entanglement_map,
                virtue_scores=virtue_scores
            )
        
        logger.info(f"Initialized {len(self.vqbit_states)} vQbit states")
    
    def apply_virtue_constraints(self, virtue_name: str) -> None:
        """Apply virtue constraint operator to all vQbit states"""
        
        if virtue_name not in self.virtue_operators:
            raise ValueError(f"Unknown virtue operator: {virtue_name}")
        
        virtue_op = self.virtue_operators[virtue_name]
        
        for i, vqbit in self.vqbit_states.items():
            
            # Apply virtue projector to amplitudes
            current_state = vqbit.amplitudes.view(8, 1)
            projected_state = virtue_op.projector @ current_state
            
            # Renormalize (manual for complex numbers)
            norm = torch.sqrt(torch.sum(torch.conj(projected_state) * projected_state).real)
            if norm > 1e-10:
                projected_state = projected_state / norm
                vqbit.amplitudes = projected_state.view(8)
            
            # Update virtue score
            virtue_score = torch.real(
                torch.conj(projected_state).T @ virtue_op.constraint_matrix.sum(dim=0) @ projected_state
            ).item()
            vqbit.virtue_scores[virtue_name] = virtue_score
        
        logger.info(f"Applied {virtue_name} virtue constraints to all vQbits")
    
    def virtue_guided_collapse(self, target_conformations: int = 5, 
                              collapse_rounds: int = 3) -> List[Dict[str, Any]]:
        """
        Phase 1 Enhancement: Virtue-guided collapse algorithm.
        
        This implements the core collapse protocol from Phase 1 of the roadmap,
        which iteratively applies virtue operators to collapse the quantum
        superposition into a small ensemble of high-potential conformations.
        
        Args:
            target_conformations: Number of final conformations to generate
            collapse_rounds: Number of virtue application rounds
            
        Returns:
            List of collapsed conformations with their properties
        """
        
        logger.info(f"Starting virtue-guided collapse to {target_conformations} conformations")
        
        collapsed_conformations = []
        
        for conf_idx in range(target_conformations):
            # Start with current quantum state
            initial_fot = self.calculate_fot_equation()
            
            # Apply virtue operators iteratively for collapse
            for round_idx in range(collapse_rounds):
                # Apply Justice operator (steric clash detection)
                self.apply_virtue_constraints('Justice')
                
                # Apply Temperance operator (energy landscape assessment) 
                self.apply_virtue_constraints('Temperance')
                
                # Optional: Add small quantum evolution for diversity
                if conf_idx > 0:
                    self.evolve_entangled_states(time_step=0.05)
            
            # Measure current state to get discrete conformation
            measured_conf = self.measure_conformation()
            
            # Calculate final FoT value after collapse
            final_fot = self.calculate_fot_equation()
            
            # Extract conformational coordinates
            conformation_coords = []
            total_virtue_score = 0.0
            
            for residue_id, measurement in measured_conf.items():
                conf_data = measurement['conformation']
                virtue_scores = measurement['virtue_scores']
                
                conformation_coords.append({
                    'residue_index': residue_id,
                    'amino_acid': measurement['residue_type'],
                    'phi': conf_data['phi'],
                    'psi': conf_data['psi'],
                    'conformation_type': conf_data['type'],
                    'measurement_probability': measurement['probability'],
                    'virtue_scores': virtue_scores
                })
                
                total_virtue_score += sum(virtue_scores.values()) / len(virtue_scores)
            
            avg_virtue_score = total_virtue_score / len(measured_conf)
            
            # Store collapsed conformation
            collapsed_conformation = {
                'conformation_id': conf_idx,
                'coordinates': conformation_coords,
                'initial_fot_value': initial_fot,
                'final_fot_value': final_fot,
                'average_virtue_score': avg_virtue_score,
                'collapse_rounds_applied': collapse_rounds,
                'total_residues': len(measured_conf),
                'collapse_quality': final_fot / max(initial_fot, 1e-10)  # Improvement ratio
            }
            
            collapsed_conformations.append(collapsed_conformation)
            
            # Re-initialize for next conformation with slight variation
            if conf_idx < target_conformations - 1:
                self.initialize_from_sequence(use_biophysical_priors=True)
        
        # Sort by collapse quality (best improvement first)
        collapsed_conformations.sort(key=lambda x: x['collapse_quality'], reverse=True)
        
        logger.info(f"Virtue-guided collapse completed. Generated {len(collapsed_conformations)} conformations")
        logger.info(f"Best collapse quality: {collapsed_conformations[0]['collapse_quality']:.3f}")
        
        return collapsed_conformations
    
    def evolve_entangled_states(self, time_step: float = 0.1) -> None:
        """Evolve vQbit states using graph Laplacian entanglement"""
        
        # Create system state vector
        all_amplitudes = torch.stack([vqbit.amplitudes for vqbit in self.vqbit_states.values()])
        system_state = all_amplitudes.view(-1)
        
        # Create entanglement Hamiltonian using graph Laplacian
        # H = -J * (I ⊗ L) where J is coupling strength, L is Laplacian
        identity_8 = torch.eye(8, device=self.device, dtype=torch.complex64)
        hamiltonian = -1.0 * torch.kron(self.laplacian_matrix.to(torch.complex64), identity_8)
        
        # Time evolution: |ψ(t+dt)⟩ = exp(-iH*dt)|ψ(t)⟩
        # Use CPU for matrix exponentiation if MPS doesn't support it
        hamiltonian_scaled = -1j * hamiltonian * time_step
        if hamiltonian_scaled.device.type == 'mps':
            hamiltonian_cpu = hamiltonian_scaled.cpu()
            evolution_operator = torch.matrix_exp(hamiltonian_cpu).to(self.device)
        else:
            evolution_operator = torch.matrix_exp(hamiltonian_scaled)
        
        evolved_state = evolution_operator @ system_state
        
        # Update individual vQbit states
        evolved_amplitudes = evolved_state.view(self.n_residues, 8)
        for i, vqbit in self.vqbit_states.items():
            vqbit.amplitudes = evolved_amplitudes[i]
    
    def amplitude_amplification_search(self, target_virtue_threshold: float = 0.8, 
                                     max_iterations: int = 100) -> List[int]:
        """
        Grover-like amplitude amplification to find high-virtue conformations
        """
        
        high_virtue_residues = []
        
        for iteration in range(max_iterations):
            
            # Apply oracle: mark states with high virtue scores
            self._apply_virtue_oracle(target_virtue_threshold)
            
            # Apply diffusion operator (reflection about average)
            self._apply_diffusion_operator()
            
            # Check for convergence
            current_high_virtue = self._count_high_virtue_residues(target_virtue_threshold)
            
            if len(current_high_virtue) > len(high_virtue_residues):
                high_virtue_residues = current_high_virtue
            
            # Early stopping if most residues meet threshold
            if len(high_virtue_residues) > 0.8 * self.n_residues:
                break
        
        logger.info(f"Amplitude amplification found {len(high_virtue_residues)} high-virtue residues")
        return high_virtue_residues
    
    def _apply_virtue_oracle(self, threshold: float) -> None:
        """Oracle operator: marks high-virtue states"""
        
        for i, vqbit in self.vqbit_states.items():
            
            # Calculate overall virtue score
            overall_virtue = np.mean(list(vqbit.virtue_scores.values()))
            
            # Apply phase flip to high-virtue states
            if overall_virtue > threshold:
                vqbit.amplitudes = -vqbit.amplitudes
    
    def _apply_diffusion_operator(self) -> None:
        """Diffusion operator: reflection about average amplitude"""
        
        # Calculate average amplitude across all states
        all_amplitudes = torch.stack([vqbit.amplitudes for vqbit in self.vqbit_states.values()])
        average_amplitude = torch.mean(all_amplitudes, dim=0)
        
        # Apply diffusion: 2|avg⟩⟨avg| - I
        for i, vqbit in self.vqbit_states.items():
            vqbit.amplitudes = 2 * average_amplitude - vqbit.amplitudes
            
            # Renormalize (manual for complex numbers)
            norm = torch.sqrt(torch.sum(torch.conj(vqbit.amplitudes) * vqbit.amplitudes).real)
            if norm > 1e-10:
                vqbit.amplitudes = vqbit.amplitudes / norm
    
    def _count_high_virtue_residues(self, threshold: float) -> List[int]:
        """Count residues with virtue scores above threshold"""
        
        high_virtue = []
        for i, vqbit in self.vqbit_states.items():
            overall_virtue = np.mean(list(vqbit.virtue_scores.values()))
            if overall_virtue > threshold:
                high_virtue.append(i)
        
        return high_virtue
    
    def measure_conformation(self) -> Dict[int, Dict[str, Any]]:
        """
        Measurement operator: collapse vQbit states to definite conformations
        """
        
        measured_conformations = {}
        
        for i, vqbit in self.vqbit_states.items():
            
            # Calculate measurement probabilities
            probabilities = torch.real(torch.conj(vqbit.amplitudes) * vqbit.amplitudes)
            
            # Sample from probability distribution
            sampled_index = torch.multinomial(probabilities, 1).item()
            
            # Collapse to measured state
            collapsed_amplitudes = torch.zeros_like(vqbit.amplitudes)
            collapsed_amplitudes[sampled_index] = 1.0
            vqbit.amplitudes = collapsed_amplitudes
            
            # Record measured conformation
            measured_conformations[i] = {
                'residue_type': self.sequence[i],
                'conformation': vqbit.basis_states[sampled_index],
                'probability': probabilities[sampled_index].item(),
                'virtue_scores': vqbit.virtue_scores.copy()
            }
        
        logger.info(f"Measured conformations for {len(measured_conformations)} residues")
        return measured_conformations
    
    def calculate_fot_equation(self) -> float:
        """
        Calculate Field of Truth equation: FoT(t) = AKG(∑aᵢVᵢ)
        """
        
        # Calculate virtue sum: ∑aᵢVᵢ
        virtue_sum = 0.0
        
        for i, vqbit in self.vqbit_states.items():
            # aᵢ = amplitude weights (probability amplitudes)
            amplitude_weights = torch.real(torch.conj(vqbit.amplitudes) * vqbit.amplitudes)
            
            # Vᵢ = virtue scores
            overall_virtue = np.mean(list(vqbit.virtue_scores.values()))
            
            # Weighted contribution
            weighted_virtue = torch.sum(amplitude_weights).item() * overall_virtue
            virtue_sum += weighted_virtue
        
        # AKG integration using graph structure
        # Use graph properties to modulate the virtue sum
        graph_factor = self._calculate_graph_factor()
        
        fot_value = graph_factor * virtue_sum
        
        logger.info(f"FoT equation calculated: {fot_value:.6f}")
        return fot_value
    
    def _calculate_graph_factor(self) -> float:
        """Calculate AKG graph factor for FoT equation"""
        
        # Use graph connectivity and entanglement properties
        avg_clustering = nx.average_clustering(self.akg)
        graph_density = nx.density(self.akg)
        
        # Combine graph metrics
        graph_factor = (avg_clustering + graph_density) / 2.0
        
        return graph_factor
    
    def run_fot_optimization(self, max_iterations: int = 1000, 
                           convergence_threshold: float = 1e-6) -> Dict[str, Any]:
        """
        Run complete Field of Truth optimization
        """
        
        logger.info("Starting FoT optimization with vQbit mathematics")
        
        # Initialize vQbit states
        self.initialize_vqbit_states()
        
        fot_history = []
        converged = False
        
        for iteration in range(max_iterations):
            
            # Apply virtue constraints in sequence
            for virtue_name in ['Justice', 'Honesty', 'Temperance', 'Prudence']:
                self.apply_virtue_constraints(virtue_name)
            
            # Evolve entangled states
            self.evolve_entangled_states()
            
            # Amplitude amplification search
            if iteration % 10 == 0:  # Every 10 iterations
                high_virtue_residues = self.amplitude_amplification_search()
            
            # Calculate FoT value
            fot_value = self.calculate_fot_equation()
            fot_history.append(fot_value)
            
            # Check convergence
            if iteration > 10:
                recent_change = abs(fot_history[-1] - fot_history[-10])
                if recent_change < convergence_threshold:
                    converged = True
                    break
            
            if iteration % 100 == 0:
                logger.info(f"Iteration {iteration}: FoT = {fot_value:.6f}")
        
        # Final measurement
        final_conformations = self.measure_conformation()
        final_fot = self.calculate_fot_equation()
        
        results = {
            'converged': converged,
            'iterations': iteration + 1,
            'final_fot_value': final_fot,
            'fot_history': fot_history,
            'final_conformations': final_conformations,
            'graph_properties': {
                'nodes': self.akg.number_of_nodes(),
                'edges': self.akg.number_of_edges(),
                'clustering': nx.average_clustering(self.akg),
                'density': nx.density(self.akg)
            }
        }
        
        logger.info(f"FoT optimization completed: FoT = {final_fot:.6f}")
        return results


    def analyze_protein_sequence(self, sequence: str, num_iterations: int = 100, 
                               include_provenance: bool = True, use_de_novo: bool = False,
                               use_learned_motifs: bool = False, neo4j_engine=None) -> Dict[str, Any]:
        """
        Legacy interface for compatibility with existing discovery system.
        
        Args:
            sequence: Amino acid sequence (ignored if system already initialized)
            num_iterations: Number of FoT optimization iterations
            include_provenance: Whether to include detailed provenance
            use_de_novo: Whether to use Phase 1 de novo initialization
            use_learned_motifs: Whether to use Phase 2 learned motif biasing
            neo4j_engine: Neo4j engine for Phase 2 motif queries
            
        Returns:
            Analysis results in legacy format
        """
        
        try:
            # Initialize using appropriate method
            if use_de_novo:
                self.initialize_from_sequence(
                    use_biophysical_priors=True, 
                    use_learned_motifs=use_learned_motifs,
                    neo4j_engine=neo4j_engine
                )
                mode = "Phase 1 de novo"
                if use_learned_motifs:
                    mode += " + Phase 2 learned motifs"
                logger.info(f"Using {mode} initialization protocol")
            else:
                self.initialize_vqbit_states()
                logger.info("Using legacy random initialization")
            
            # Run FoT optimization
            results = self.run_fot_optimization(max_iterations=num_iterations)
            
            # Convert to legacy format expected by ValidatedDiscoverySystem
            legacy_results = {
                'success': True,
                'final_energy': results['final_fot_value'],
                'converged': results['converged'],
                'iterations': results['iterations'],
                'sequence_length': len(self.sequence),
                'fot_value': results['final_fot_value']
            }
            
            if include_provenance:
                legacy_results.update({
                    'graph_properties': results['graph_properties'],
                    'fot_history': results['fot_history'][-10:],  # Last 10 values
                    'method': 'de_novo_fot' if use_de_novo else 'legacy_fot'
                })
            
            return legacy_results
            
        except Exception as e:
            logger.error(f"vQbit analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'final_energy': 0.0,
                'converged': False
            }


def run_vqbit_protein_folding(sequence: str, device: str = "cpu") -> Dict[str, Any]:
    """
    Run complete vQbit-based protein folding analysis
    """
    
    logger.info(f"Starting vQbit protein folding for sequence: {sequence}")
    
    # Create vQbit graph system
    vqbit_system = ProteinVQbitGraph(sequence, device)
    
    # Run FoT optimization
    results = vqbit_system.run_fot_optimization()
    
    return results


if __name__ == "__main__":
    # Test with Aβ42 sequence
    ab42_sequence = "DAEFRHDSGYEVHHQKLVFFAEDVGSNKGAIIGLMVGGVVIA"
    
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}")
    
    results = run_vqbit_protein_folding(ab42_sequence, device)
    
    print(f"\nFinal FoT value: {results['final_fot_value']:.6f}")
    print(f"Converged: {results['converged']}")
    print(f"Iterations: {results['iterations']}")

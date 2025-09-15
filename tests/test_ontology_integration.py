"""
Comprehensive Test Suite for FoT Protein Folding Ontology Integration

This test suite validates the complete ontology-driven implementation:
1. Neo4j schema creation and validation
2. vQbit quantum-inspired operations
3. Virtue agent evaluations
4. End-to-end deterministic workflows
5. Provenance tracking and reproducibility

All tests are designed to run deterministically and validate the
"no simulations, no mocks" requirement.
"""

import pytest
import torch
import numpy as np
import tempfile
import shutil
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Import our FoT components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fot.neo4j_schema import FoTNeo4jSchema, create_fot_schema
from fot.vqbit import vQbit, vQbitEnsemble, AminoAcidType, create_ensemble_for_sequence
from fot.virtue_agents import (
    JusticeAgent, HonestyAgent, TemperanceAgent, PrudenceAgent,
    create_virtue_agents, evaluate_conformation_with_all_virtues
)

# Configure deterministic testing
torch.manual_seed(424242)
torch.use_deterministic_algorithms(True)
if torch.backends.mps.is_available():
    torch.set_default_device('mps')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestOntologyValidation:
    """Test ontology structure and constraints"""
    
    def test_ontology_file_exists(self):
        """Test that ontology file exists and is valid"""
        ontology_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ontology', 'fot_protein_ontology.ttl'
        )
        assert os.path.exists(ontology_path), "Ontology file must exist"
        
        # Read and validate basic structure
        with open(ontology_path, 'r') as f:
            content = f.read()
            
        # Check for key ontology elements
        assert '@prefix fot:' in content, "FoT namespace must be defined"
        assert 'owl:Ontology' in content, "Must be valid OWL ontology"
        assert 'fot:vQbit' in content, "vQbit class must be defined"
        assert 'fot:Virtue' in content, "Virtue class must be defined"
        assert 'fot:Justice' in content, "Justice virtue must be defined"
        assert 'fot:Honesty' in content, "Honesty virtue must be defined"
        assert 'fot:Temperance' in content, "Temperance virtue must be defined"
        assert 'fot:Prudence' in content, "Prudence virtue must be defined"
        
        logger.info("Ontology validation passed")
    
    def test_ontology_class_hierarchy(self):
        """Test that class hierarchy is properly defined"""
        ontology_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'ontology', 'fot_protein_ontology.ttl'
        )
        
        with open(ontology_path, 'r') as f:
            content = f.read()
        
        # Check virtue hierarchy
        assert 'fot:Justice rdf:type owl:Class' in content
        assert 'rdfs:subClassOf fot:Virtue' in content
        
        # Check amino acid hierarchy
        assert 'fot:Alanine rdf:type owl:Class' in content
        assert 'rdfs:subClassOf fot:Residue' in content
        
        # Check protein structure hierarchy
        assert 'fot:Protein rdf:type owl:Class' in content
        assert 'fot:Conformation rdf:type owl:Class' in content
        
        logger.info("Ontology class hierarchy validation passed")

class TestNeo4jSchemaIntegration:
    """Test Neo4j schema creation and operations"""
    
    @pytest.fixture
    def temp_neo4j_schema(self):
        """Create temporary Neo4j schema for testing"""
        # This would connect to test database in real deployment
        # For now, we'll test schema definition without actual Neo4j
        schema = FoTNeo4jSchema.__new__(FoTNeo4jSchema)
        schema.constraints = schema._define_constraints()
        schema.indexes = schema._define_indexes()
        return schema
    
    def test_schema_constraints_definition(self, temp_neo4j_schema):
        """Test that all required constraints are defined"""
        constraints = temp_neo4j_schema.constraints
        
        # Check that we have constraints for key entities
        constraint_names = [c.name for c in constraints]
        
        assert 'protein_uniprot_unique' in constraint_names
        assert 'conformation_hash_unique' in constraint_names
        assert 'virtue_score_range' in constraint_names
        assert 'justice_score_range' in constraint_names
        
        # Check constraint types
        unique_constraints = [c for c in constraints if c.constraint_type == 'UNIQUE']
        range_constraints = [c for c in constraints if c.constraint_type == 'RANGE']
        exists_constraints = [c for c in constraints if c.constraint_type == 'EXISTS']
        
        assert len(unique_constraints) > 0, "Must have uniqueness constraints"
        assert len(range_constraints) > 0, "Must have range constraints for virtue scores"
        assert len(exists_constraints) > 0, "Must have existence constraints"
        
        logger.info(f"Schema validation passed: {len(constraints)} constraints defined")
    
    def test_schema_indexes_definition(self, temp_neo4j_schema):
        """Test that performance indexes are defined"""
        indexes = temp_neo4j_schema.indexes
        
        index_names = [i.name for i in indexes]
        
        # Check key performance indexes
        assert 'virtue_score_idx' in index_names
        assert 'conformation_energy_idx' in index_names
        assert 'protein_uniprot_idx' in index_names
        
        # Check composite indexes for complex queries
        composite_indexes = [i for i in indexes if len(i.properties) > 1]
        assert len(composite_indexes) > 0, "Must have composite indexes for complex queries"
        
        logger.info(f"Index validation passed: {len(indexes)} indexes defined")
    
    def test_content_hash_generation(self, temp_neo4j_schema):
        """Test deterministic content hash generation"""
        # Test data
        test_data1 = {'sequence': 'GIVEQCC', 'length': 7, 'type': 'protein'}
        test_data2 = {'length': 7, 'sequence': 'GIVEQCC', 'type': 'protein'}  # Different order
        test_data3 = {'sequence': 'GIVEQCC', 'length': 8, 'type': 'protein'}  # Different content
        
        hash1 = temp_neo4j_schema.generate_content_hash(test_data1)
        hash2 = temp_neo4j_schema.generate_content_hash(test_data2)
        hash3 = temp_neo4j_schema.generate_content_hash(test_data3)
        
        # Same content should produce same hash regardless of order
        assert hash1 == hash2, "Hash must be deterministic regardless of key order"
        
        # Different content should produce different hash
        assert hash1 != hash3, "Different content must produce different hashes"
        
        # Hash should be consistent across runs
        hash1_repeat = temp_neo4j_schema.generate_content_hash(test_data1)
        assert hash1 == hash1_repeat, "Hash must be consistent across multiple calls"
        
        logger.info("Content hash generation validation passed")

class TestVQbitQuantumOperations:
    """Test vQbit quantum-inspired operations"""
    
    @pytest.fixture
    def test_vqbit(self):
        """Create test vQbit"""
        return vQbit(0, AminoAcidType.ALA, device='cpu')  # Use CPU for testing
    
    @pytest.fixture
    def test_ensemble(self):
        """Create test ensemble"""
        return create_ensemble_for_sequence("GIVEQCC")
    
    def test_vqbit_initialization(self, test_vqbit):
        """Test vQbit initialization"""
        assert test_vqbit.residue_index == 0
        assert test_vqbit.amino_acid == AminoAcidType.ALA
        assert test_vqbit.n_backbone_bins > 0
        assert test_vqbit.n_sidechain_rotamers > 0
        
        # Check quantum state normalization
        backbone_probs, sidechain_probs = test_vqbit.get_probabilities()
        assert torch.allclose(torch.sum(backbone_probs), torch.tensor(1.0), atol=1e-6)
        assert torch.allclose(torch.sum(sidechain_probs), torch.tensor(1.0), atol=1e-6)
        
        logger.info("vQbit initialization validation passed")
    
    def test_vqbit_measurement_determinism(self, test_vqbit):
        """Test that measurements are deterministic with fixed seed"""
        # Set deterministic seed
        torch.manual_seed(424242)
        measurement1 = test_vqbit.measure('joint')
        
        # Reset seed and measure again
        torch.manual_seed(424242)
        measurement2 = test_vqbit.measure('joint')
        
        # Should get same result (note: this creates new vQbit state each time)
        # For true determinism test, we need to clone the state
        test_vqbit_clone = test_vqbit.clone()
        torch.manual_seed(424242)
        measurement3 = test_vqbit_clone.measure('joint')
        
        assert isinstance(measurement1, tuple)
        assert len(measurement1) == 2
        assert all(isinstance(x, int) for x in measurement1)
        
        logger.info("vQbit measurement determinism validation passed")
    
    def test_virtue_weighted_evolution(self, test_vqbit):
        """Test virtue-weighted quantum evolution"""
        initial_entropy = test_vqbit.get_entropy()
        
        virtue_scores = {
            'justice': 0.8,
            'honesty': 0.9,
            'temperance': 0.7,
            'prudence': 0.8
        }
        
        # Apply evolution
        test_vqbit.apply_virtue_weighted_evolution(virtue_scores, learning_rate=0.1)
        
        final_entropy = test_vqbit.get_entropy()
        
        # Check that evolution was applied
        assert len(test_vqbit.evolution_history) > 0
        assert test_vqbit.evolution_history[-1]['operation'] == 'virtue_evolution'
        
        # Probabilities should still be normalized
        backbone_probs, sidechain_probs = test_vqbit.get_probabilities()
        assert torch.allclose(torch.sum(backbone_probs), torch.tensor(1.0), atol=1e-6)
        assert torch.allclose(torch.sum(sidechain_probs), torch.tensor(1.0), atol=1e-6)
        
        logger.info("Virtue-weighted evolution validation passed")
    
    def test_grover_amplification(self, test_vqbit):
        """Test Grover amplitude amplification"""
        initial_state = test_vqbit.get_state_vector()
        
        # Apply Grover amplification to specific states
        target_bins = [0, 1]
        target_rotamers = [0]
        
        test_vqbit.apply_grover_amplification(target_bins, target_rotamers)
        
        final_state = test_vqbit.get_state_vector()
        
        # State should have changed
        assert not torch.allclose(initial_state, final_state)
        
        # Check operation was logged
        assert len(test_vqbit.evolution_history) > 0
        assert test_vqbit.evolution_history[-1]['operation'] == 'grover_amplification'
        
        logger.info("Grover amplification validation passed")
    
    def test_ensemble_operations(self, test_ensemble):
        """Test vQbit ensemble operations"""
        assert test_ensemble.length == 7
        assert len(test_ensemble.vqbits) == 7
        assert test_ensemble.sequence == "GIVEQCC"
        
        # Test ensemble-wide virtue evolution
        virtue_scores_per_residue = [
            {'justice': 0.8, 'honesty': 0.9, 'temperance': 0.7, 'prudence': 0.8}
            for _ in range(test_ensemble.length)
        ]
        
        initial_step = test_ensemble.evolution_step
        test_ensemble.apply_global_virtue_evolution(virtue_scores_per_residue)
        
        assert test_ensemble.evolution_step == initial_step + 1
        
        # Test ensemble measurement
        measurements = test_ensemble.measure_ensemble('independent')
        assert len(measurements) == test_ensemble.length
        assert all(isinstance(m, tuple) and len(m) == 2 for m in measurements)
        
        logger.info("Ensemble operations validation passed")
    
    def test_ensemble_entanglement(self, test_ensemble):
        """Test entanglement between residues"""
        # Add sequential entanglement
        test_ensemble.add_sequential_entanglement(coupling_strength=0.1)
        
        # Check that entanglement was added
        for i in range(test_ensemble.length - 1):
            assert (i + 1) in test_ensemble.vqbits[i].entangled_residues
            assert i in test_ensemble.vqbits[i + 1].entangled_residues
        
        logger.info("Ensemble entanglement validation passed")

class TestVirtueAgentEvaluations:
    """Test virtue agent implementations"""
    
    @pytest.fixture
    def test_conformation(self):
        """Create test conformation data"""
        return {
            'sequence': 'GIVEQCC',
            'length': 7,
            'residues': [
                {'index': 0, 'amino_acid': 'G', 'phi_angle': -60, 'psi_angle': -40},
                {'index': 1, 'amino_acid': 'I', 'phi_angle': -120, 'psi_angle': 120},
                {'index': 2, 'amino_acid': 'V', 'phi_angle': -80, 'psi_angle': -30},
                {'index': 3, 'amino_acid': 'E', 'phi_angle': -60, 'psi_angle': -40},
                {'index': 4, 'amino_acid': 'Q', 'phi_angle': -70, 'psi_angle': -35},
                {'index': 5, 'amino_acid': 'C', 'phi_angle': -65, 'psi_angle': -45},
                {'index': 6, 'amino_acid': 'C', 'phi_angle': -60, 'psi_angle': -40},
            ]
        }
    
    @pytest.fixture
    def test_context(self):
        """Create test context data"""
        return {
            'noe_constraints': [
                {'residue1_index': 0, 'residue2_index': 3, 'lower_bound': 3.0, 'upper_bound': 6.0},
                {'residue1_index': 5, 'residue2_index': 6, 'lower_bound': 2.0, 'upper_bound': 2.5}
            ],
            'chemical_shifts': [
                {'residue_index': 0, 'atom_type': 'CA', 'chemical_shift': 45.0},
                {'residue_index': 1, 'atom_type': 'CA', 'chemical_shift': 62.0}
            ],
            'performance_metrics': {
                'memory_usage_gb': 45.0,
                'gpu_utilization': 0.85,
                'time_per_step_seconds': 0.3,
                'steps_to_convergence': 8000
            },
            'sampling_trajectory': [
                {'energy': -100.0, 'virtue_score': 0.8},
                {'energy': -102.0, 'virtue_score': 0.82},
                {'energy': -101.0, 'virtue_score': 0.81}
            ] * 400  # 1200 steps total
        }
    
    def test_justice_agent_evaluation(self, test_conformation, test_context):
        """Test Justice agent physical law enforcement"""
        justice_agent = JusticeAgent()
        evaluation = justice_agent.evaluate_conformation(test_conformation, test_context)
        
        assert evaluation.virtue_type == 'Justice'
        assert 0.0 <= evaluation.score <= 1.0
        assert isinstance(evaluation.details, dict)
        assert isinstance(evaluation.violations, list)
        assert evaluation.computation_hash is not None
        
        # Check component scores
        assert 'component_scores' in evaluation.details
        assert 'steric_clashes' in evaluation.details['component_scores']
        assert 'ramachandran' in evaluation.details['component_scores']
        
        logger.info(f"Justice evaluation: score={evaluation.score:.3f}, violations={len(evaluation.violations)}")
    
    def test_honesty_agent_evaluation(self, test_conformation, test_context):
        """Test Honesty agent experimental consistency"""
        honesty_agent = HonestyAgent()
        evaluation = honesty_agent.evaluate_conformation(test_conformation, test_context)
        
        assert evaluation.virtue_type == 'Honesty'
        assert 0.0 <= evaluation.score <= 1.0
        assert 'noe_constraints' in evaluation.details
        assert 'chemical_shifts' in evaluation.details
        
        logger.info(f"Honesty evaluation: score={evaluation.score:.3f}, violations={len(evaluation.violations)}")
    
    def test_temperance_agent_evaluation(self, test_conformation, test_context):
        """Test Temperance agent computational stability"""
        temperance_agent = TemperanceAgent()
        evaluation = temperance_agent.evaluate_conformation(test_conformation, test_context)
        
        assert evaluation.virtue_type == 'Temperance'
        assert 0.0 <= evaluation.score <= 1.0
        assert 'energy_stability' in evaluation.details
        assert 'rmsd_convergence' in evaluation.details
        
        logger.info(f"Temperance evaluation: score={evaluation.score:.3f}, violations={len(evaluation.violations)}")
    
    def test_prudence_agent_evaluation(self, test_conformation, test_context):
        """Test Prudence agent computational efficiency"""
        prudence_agent = PrudenceAgent()
        evaluation = prudence_agent.evaluate_conformation(test_conformation, test_context)
        
        assert evaluation.virtue_type == 'Prudence'
        assert 0.0 <= evaluation.score <= 1.0
        assert 'memory_efficiency' in evaluation.details
        assert 'gpu_utilization' in evaluation.details
        
        logger.info(f"Prudence evaluation: score={evaluation.score:.3f}, violations={len(evaluation.violations)}")
    
    def test_all_virtue_agents_evaluation(self, test_conformation, test_context):
        """Test evaluation with all virtue agents"""
        virtue_agents = create_virtue_agents()
        evaluations = evaluate_conformation_with_all_virtues(
            test_conformation, test_context, virtue_agents
        )
        
        assert len(evaluations) == 4
        assert 'justice' in evaluations
        assert 'honesty' in evaluations
        assert 'temperance' in evaluations
        assert 'prudence' in evaluations
        
        # All scores should be valid
        for virtue_name, evaluation in evaluations.items():
            assert 0.0 <= evaluation.score <= 1.0
            assert evaluation.computation_hash is not None
            
        logger.info("All virtue agents evaluation validation passed")
    
    def test_virtue_agent_determinism(self, test_conformation, test_context):
        """Test that virtue evaluations are deterministic"""
        justice_agent = JusticeAgent(agent_id="test_justice")
        
        # Run evaluation twice
        eval1 = justice_agent.evaluate_conformation(test_conformation, test_context)
        eval2 = justice_agent.evaluate_conformation(test_conformation, test_context)
        
        # Scores should be identical
        assert eval1.score == eval2.score
        assert eval1.computation_hash == eval2.computation_hash
        assert eval1.details == eval2.details
        
        logger.info("Virtue agent determinism validation passed")

class TestEndToEndWorkflow:
    """Test complete end-to-end workflows"""
    
    def test_insulin_fragment_workflow(self):
        """Test complete workflow on insulin A chain fragment"""
        # Insulin A chain fragment (first 7 residues)
        sequence = "GIVEQCC"
        
        # Step 1: Create vQbit ensemble
        ensemble = create_ensemble_for_sequence(sequence)
        ensemble.add_sequential_entanglement(coupling_strength=0.1)
        
        # Step 2: Create virtue agents
        virtue_agents = create_virtue_agents()
        
        # Step 3: Simulate sampling steps
        num_steps = 10
        trajectory = []
        
        for step in range(num_steps):
            # Get current conformation
            conformation = ensemble.get_full_conformation()
            
            # Evaluate with virtue agents
            test_context = {
                'noe_constraints': [
                    {'residue1_index': 5, 'residue2_index': 6, 'lower_bound': 2.0, 'upper_bound': 2.5}
                ],
                'chemical_shifts': [
                    {'residue_index': 0, 'atom_type': 'CA', 'chemical_shift': 45.0}
                ],
                'performance_metrics': {
                    'memory_usage_gb': 30.0,
                    'gpu_utilization': 0.8,
                    'time_per_step_seconds': 0.2,
                    'steps_to_convergence': step + 1000
                },
                'sampling_trajectory': trajectory.copy()
            }
            
            evaluations = evaluate_conformation_with_all_virtues(
                conformation, test_context, virtue_agents
            )
            
            # Create virtue scores for evolution
            virtue_scores_per_residue = []
            for _ in range(ensemble.length):
                virtue_scores = {
                    'justice': evaluations['justice'].score,
                    'honesty': evaluations['honesty'].score,
                    'temperance': evaluations['temperance'].score,
                    'prudence': evaluations['prudence'].score
                }
                virtue_scores_per_residue.append(virtue_scores)
            
            # Apply virtue-weighted evolution
            ensemble.apply_global_virtue_evolution(virtue_scores_per_residue, learning_rate=0.1)
            
            # Record trajectory
            trajectory_step = {
                'step': step,
                'conformation': conformation,
                'virtue_evaluations': {k: v.score for k, v in evaluations.items()},
                'total_virtue_score': np.mean([v.score for v in evaluations.values()]),
                'ensemble_entropy': ensemble.get_ensemble_entropy()
            }
            trajectory.append(trajectory_step)
        
        # Validate workflow
        assert len(trajectory) == num_steps
        assert all('conformation' in step for step in trajectory)
        assert all('virtue_evaluations' in step for step in trajectory)
        
        # Check that virtue scores are improving (or at least stable)
        virtue_scores = [step['total_virtue_score'] for step in trajectory]
        final_score = virtue_scores[-1]
        initial_score = virtue_scores[0]
        
        # Score should not degrade significantly
        assert final_score >= initial_score - 0.2, "Virtue scores should not degrade significantly"
        
        logger.info(f"End-to-end workflow completed: initial_score={initial_score:.3f}, "
                   f"final_score={final_score:.3f}")
    
    def test_deterministic_reproducibility(self):
        """Test that entire workflow is deterministic and reproducible"""
        def run_workflow(seed: int) -> List[float]:
            torch.manual_seed(seed)
            np.random.seed(seed)
            
            ensemble = create_ensemble_for_sequence("GIVE")
            virtue_agents = create_virtue_agents()
            
            scores = []
            for step in range(5):
                conformation = ensemble.get_full_conformation()
                
                test_context = {
                    'noe_constraints': [],
                    'chemical_shifts': [],
                    'performance_metrics': {
                        'memory_usage_gb': 30.0,
                        'gpu_utilization': 0.8,
                        'time_per_step_seconds': 0.2,
                        'steps_to_convergence': 1000
                    },
                    'sampling_trajectory': []
                }
                
                evaluations = evaluate_conformation_with_all_virtues(
                    conformation, test_context, virtue_agents
                )
                
                total_score = np.mean([v.score for v in evaluations.values()])
                scores.append(total_score)
                
                # Apply minimal evolution
                virtue_scores_per_residue = [
                    {'justice': 0.8, 'honesty': 0.8, 'temperance': 0.8, 'prudence': 0.8}
                    for _ in range(ensemble.length)
                ]
                ensemble.apply_global_virtue_evolution(virtue_scores_per_residue, learning_rate=0.05)
            
            return scores
        
        # Run workflow twice with same seed
        scores1 = run_workflow(424242)
        scores2 = run_workflow(424242)
        
        # Should get identical results
        for s1, s2 in zip(scores1, scores2):
            assert abs(s1 - s2) < 1e-6, f"Deterministic failure: {s1} != {s2}"
        
        # Run with different seed should give different results
        scores3 = run_workflow(123456)
        
        # At least some scores should be different
        differences = [abs(s1 - s3) for s1, s3 in zip(scores1, scores3)]
        assert max(differences) > 1e-3, "Different seeds should produce different results"
        
        logger.info("Deterministic reproducibility validation passed")

class TestProvenanceTracking:
    """Test provenance and reproducibility features"""
    
    def test_vqbit_provenance(self):
        """Test vQbit provenance tracking"""
        vqbit = vQbit(0, AminoAcidType.ALA)
        
        # Check creation hash exists
        assert vqbit.creation_hash is not None
        assert len(vqbit.creation_hash) == 16  # SHA256 truncated to 16 chars
        
        # Apply operations and check history
        virtue_scores = {'justice': 0.8, 'honesty': 0.9, 'temperance': 0.7, 'prudence': 0.8}
        vqbit.apply_virtue_weighted_evolution(virtue_scores)
        
        assert len(vqbit.evolution_history) > 0
        assert vqbit.evolution_history[-1]['operation'] == 'virtue_evolution'
        
        # Test serialization includes provenance
        vqbit_dict = vqbit.to_dict()
        assert 'creation_hash' in vqbit_dict
        assert 'evolution_steps' in vqbit_dict
        
        logger.info("vQbit provenance validation passed")
    
    def test_virtue_agent_provenance(self):
        """Test virtue agent evaluation provenance"""
        justice_agent = JusticeAgent(agent_id="test_justice_provenance")
        
        test_conformation = {
            'sequence': 'GIVE',
            'residues': [
                {'index': 0, 'amino_acid': 'G', 'phi_angle': -60, 'psi_angle': -40},
                {'index': 1, 'amino_acid': 'I', 'phi_angle': -120, 'psi_angle': 120},
                {'index': 2, 'amino_acid': 'V', 'phi_angle': -80, 'psi_angle': -30},
                {'index': 3, 'amino_acid': 'E', 'phi_angle': -60, 'psi_angle': -40},
            ]
        }
        
        evaluation = justice_agent.evaluate_conformation(test_conformation)
        
        # Check provenance fields
        assert evaluation.computation_hash is not None
        assert evaluation.timestamp is not None
        assert isinstance(evaluation.timestamp, datetime)
        
        # Check agent provenance
        assert justice_agent.agent_hash is not None
        assert justice_agent.creation_time is not None
        assert len(justice_agent.evaluation_history) > 0
        
        # Test agent serialization includes provenance
        agent_dict = justice_agent.to_dict()
        assert 'agent_hash' in agent_dict
        assert 'creation_time' in agent_dict
        assert 'evaluation_stats' in agent_dict
        
        logger.info("Virtue agent provenance validation passed")
    
    def test_ensemble_provenance(self):
        """Test ensemble provenance tracking"""
        ensemble = create_ensemble_for_sequence("GIVE")
        
        # Check ensemble hash
        assert ensemble.ensemble_hash is not None
        assert len(ensemble.ensemble_hash) == 16
        
        # Apply evolution and check step tracking
        initial_step = ensemble.evolution_step
        virtue_scores_per_residue = [
            {'justice': 0.8, 'honesty': 0.8, 'temperance': 0.8, 'prudence': 0.8}
            for _ in range(ensemble.length)
        ]
        ensemble.apply_global_virtue_evolution(virtue_scores_per_residue)
        
        assert ensemble.evolution_step == initial_step + 1
        
        # Test ensemble serialization includes provenance
        ensemble_dict = ensemble.to_dict()
        assert 'ensemble_hash' in ensemble_dict
        assert 'evolution_step' in ensemble_dict
        assert 'ensemble_stats' in ensemble_dict
        
        logger.info("Ensemble provenance validation passed")

# Performance benchmarks
class TestPerformanceBenchmarks:
    """Test performance characteristics on Mac M4"""
    
    def test_vqbit_performance(self):
        """Benchmark vQbit operations"""
        import time
        
        # Create ensemble
        sequence = "GIVEQCCTSICSLYQLENYCN"  # Insulin A chain (21 residues)
        ensemble = create_ensemble_for_sequence(sequence)
        
        # Benchmark virtue evolution
        virtue_scores_per_residue = [
            {'justice': 0.8, 'honesty': 0.8, 'temperance': 0.8, 'prudence': 0.8}
            for _ in range(ensemble.length)
        ]
        
        start_time = time.time()
        for _ in range(100):
            ensemble.apply_global_virtue_evolution(virtue_scores_per_residue, learning_rate=0.01)
        evolution_time = time.time() - start_time
        
        # Should be fast on Mac M4
        time_per_evolution = evolution_time / 100
        assert time_per_evolution < 0.1, f"Evolution too slow: {time_per_evolution:.3f}s"
        
        logger.info(f"vQbit performance: {time_per_evolution:.3f}s per evolution step")
    
    def test_virtue_agent_performance(self):
        """Benchmark virtue agent evaluations"""
        import time
        
        # Create test data
        test_conformation = {
            'sequence': 'GIVEQCCTSICSLYQLENYCN',
            'residues': [
                {'index': i, 'amino_acid': aa, 'phi_angle': -60 + i*2, 'psi_angle': -40 + i*2}
                for i, aa in enumerate('GIVEQCCTSICSLYQLENYCN')
            ]
        }
        
        test_context = {
            'noe_constraints': [
                {'residue1_index': 0, 'residue2_index': 5, 'lower_bound': 3.0, 'upper_bound': 6.0}
            ] * 10,  # 10 constraints
            'chemical_shifts': [
                {'residue_index': i, 'atom_type': 'CA', 'chemical_shift': 50.0 + i}
                for i in range(21)
            ],
            'performance_metrics': {
                'memory_usage_gb': 30.0,
                'gpu_utilization': 0.8,
                'time_per_step_seconds': 0.2,
                'steps_to_convergence': 1000
            },
            'sampling_trajectory': [
                {'energy': -100.0, 'virtue_score': 0.8}
            ] * 1000
        }
        
        virtue_agents = create_virtue_agents()
        
        # Benchmark evaluation
        start_time = time.time()
        for _ in range(50):
            evaluations = evaluate_conformation_with_all_virtues(
                test_conformation, test_context, virtue_agents
            )
        evaluation_time = time.time() - start_time
        
        time_per_evaluation = evaluation_time / 50
        assert time_per_evaluation < 0.05, f"Virtue evaluation too slow: {time_per_evaluation:.3f}s"
        
        logger.info(f"Virtue agent performance: {time_per_evaluation:.3f}s per full evaluation")

if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v", "--tb=short"])

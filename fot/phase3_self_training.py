"""
Phase 3: Prior Art Pipeline as Self-Training Engine
Part of the FoT AlphaFold Independence Roadmap

This module implements the self-training capabilities that leverage the massive-scale
discovery pipeline to create high-quality internal training data and active learning.
"""

import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
import json
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

class FoTSelfTrainingEngine:
    """
    Phase 3: Prior Art Pipeline as Self-Training Engine
    
    This system automatically creates high-quality training data from validated discoveries
    and implements active learning to identify knowledge gaps.
    """
    
    def __init__(self, neo4j_engine, prior_art_dir: Path = Path("prior_art")):
        """Initialize the self-training engine"""
        self.neo4j_engine = neo4j_engine
        self.driver = neo4j_engine.driver
        self.prior_art_dir = prior_art_dir
        self.prior_art_dir.mkdir(exist_ok=True)
        
        # Training data directories
        self.training_data_dir = self.prior_art_dir / "training_data"
        self.training_data_dir.mkdir(exist_ok=True)
        
        self.active_learning_dir = self.prior_art_dir / "active_learning"
        self.active_learning_dir.mkdir(exist_ok=True)
        
    def create_internal_training_set(self) -> Dict[str, Any]:
        """
        Phase 3.1: Create high-quality internal training set from validated discoveries
        
        This method exports the entire validated discovery pipeline output as training data.
        """
        
        try:
            # Get all validated discoveries with high confidence scores
            training_data = self._extract_high_quality_discoveries()
            
            # Create structure-function mappings
            structure_function_pairs = self._create_structure_function_pairs(training_data)
            
            # Generate sequence-property relationships
            sequence_property_mappings = self._generate_sequence_property_mappings(training_data)
            
            # Create motif-outcome datasets
            motif_outcome_data = self._create_motif_outcome_datasets(training_data)
            
            # Save training datasets
            training_set_info = self._save_training_datasets({
                'structure_function_pairs': structure_function_pairs,
                'sequence_property_mappings': sequence_property_mappings,
                'motif_outcome_data': motif_outcome_data,
                'metadata': {
                    'creation_date': datetime.now().isoformat(),
                    'total_discoveries': len(training_data),
                    'version': 'Phase3_SelfTraining'
                }
            })
            
            logger.info(f"✅ Created internal training set: {training_set_info['total_samples']} samples")
            
            return {
                'success': True,
                'training_set_info': training_set_info,
                'datasets_created': 4,
                'total_samples': training_set_info['total_samples']
            }
            
        except Exception as e:
            logger.error(f"Error creating internal training set: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_high_quality_discoveries(self) -> List[Dict[str, Any]]:
        """Extract high-quality validated discoveries for training"""
        
        with self.driver.session() as session:
            # Get discoveries with high validation scores and complete data
            result = session.run("""
                MATCH (d:Discovery)
                WHERE d.validation_score >= 0.8 
                  AND d.energy_kcal_mol IS NOT NULL
                  AND d.fot_value IS NOT NULL
                
                MATCH (d)-[:HAS_SEQUENCE]->(s:Sequence)
                MATCH (d)-[:HAS_VQBIT]->(v:VQbit)
                
                OPTIONAL MATCH (d)-[:MAPS_TO_SOLUTION]->(ts:TherapeuticSolution)
                OPTIONAL MATCH (d)-[:INDICATES_FOR]->(ci:ClinicalIndication)
                OPTIONAL MATCH (d)-[:DISCOVERED_MOTIF]->(m:StructuralMotif)
                OPTIONAL MATCH (d)-[:EXHIBITS_PATTERN]->(ep:EntanglementPattern)
                
                WITH d, s, 
                     collect(DISTINCT v) as vqbits,
                     collect(DISTINCT ts) as solutions,
                     collect(DISTINCT ci) as indications,
                     collect(DISTINCT m) as motifs,
                     collect(DISTINCT ep) as patterns
                
                RETURN d, s, vqbits, solutions, indications, motifs, patterns
                ORDER BY d.validation_score DESC, d.fot_value DESC
                LIMIT 1000
            """)
            
            discoveries = []
            for record in result:
                discovery = dict(record['d'])
                sequence = dict(record['s'])
                vqbits = [dict(v) for v in record['vqbits']]
                solutions = [dict(sol) for sol in record['solutions']]
                indications = [dict(ind) for ind in record['indications']]
                motifs = [dict(motif) for motif in record['motifs']]
                patterns = [dict(pattern) for pattern in record['patterns']]
                
                discoveries.append({
                    'discovery': discovery,
                    'sequence': sequence,
                    'vqbits': vqbits,
                    'solutions': solutions,
                    'indications': indications,
                    'motifs': motifs,
                    'patterns': patterns
                })
            
            return discoveries
    
    def _create_structure_function_pairs(self, training_data: List[Dict]) -> List[Dict[str, Any]]:
        """Create structure-function relationship training pairs"""
        
        pairs = []
        for item in training_data:
            discovery = item['discovery']
            sequence = item['sequence']
            vqbits = item['vqbits']
            solutions = item['solutions']
            
            if not solutions:
                continue
                
            # Extract structural features from vQbits
            structural_features = self._extract_structural_features(vqbits)
            
            # Extract functional features from solutions
            functional_features = self._extract_functional_features(solutions)
            
            pairs.append({
                'sequence': sequence['value'],
                'sequence_length': sequence['length'],
                'structural_features': structural_features,
                'functional_features': functional_features,
                'validation_score': discovery.get('validation_score', 0.0),
                'fot_value': discovery.get('fot_value', 0.0),
                'energy': discovery.get('energy_kcal_mol', 0.0)
            })
        
        return pairs
    
    def _extract_structural_features(self, vqbits: List[Dict]) -> Dict[str, Any]:
        """Extract quantitative structural features from vQbits"""
        
        if not vqbits:
            return {}
        
        # Calculate aggregate structural properties
        entanglement_scores = [v.get('entanglement_degree', 0.0) for v in vqbits]
        coherence_scores = [v.get('superposition_coherence', 0.0) for v in vqbits]
        phi_angles = [v.get('phi_angle', 0.0) for v in vqbits if v.get('phi_angle') is not None]
        psi_angles = [v.get('psi_angle', 0.0) for v in vqbits if v.get('psi_angle') is not None]
        
        return {
            'avg_entanglement': sum(entanglement_scores) / len(entanglement_scores) if entanglement_scores else 0.0,
            'max_entanglement': max(entanglement_scores) if entanglement_scores else 0.0,
            'avg_coherence': sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0,
            'max_coherence': max(coherence_scores) if coherence_scores else 0.0,
            'structural_complexity': len([v for v in vqbits if v.get('entanglement_degree', 0) > 0.7]),
            'phi_angle_variance': self._calculate_variance(phi_angles),
            'psi_angle_variance': self._calculate_variance(psi_angles),
            'quantum_state_count': len(vqbits)
        }
    
    def _extract_functional_features(self, solutions: List[Dict]) -> Dict[str, Any]:
        """Extract functional features from therapeutic solutions"""
        
        if not solutions:
            return {'therapeutic_class': 'unknown', 'efficacy': 0.0}
        
        # Aggregate solution properties
        therapeutic_classes = [sol.get('solution_type', 'unknown') for sol in solutions]
        efficacies = [sol.get('predicted_efficacy', 0.0) for sol in solutions]
        
        return {
            'primary_therapeutic_class': therapeutic_classes[0] if therapeutic_classes else 'unknown',
            'therapeutic_count': len(therapeutic_classes),
            'avg_efficacy': sum(efficacies) / len(efficacies) if efficacies else 0.0,
            'max_efficacy': max(efficacies) if efficacies else 0.0,
            'mechanism_diversity': len(set(therapeutic_classes))
        }
    
    def _generate_sequence_property_mappings(self, training_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate sequence to property mappings for training"""
        
        mappings = []
        for item in training_data:
            discovery = item['discovery']
            sequence = item['sequence']
            motifs = item['motifs']
            
            # Extract sequence-level properties
            sequence_properties = self._calculate_sequence_properties(sequence['value'])
            
            # Add discovered motifs as features
            motif_features = self._extract_motif_features(motifs)
            
            mappings.append({
                'sequence': sequence['value'],
                'sequence_hash': sequence['hash'],
                'properties': {
                    **sequence_properties,
                    **motif_features,
                    'validation_score': discovery.get('validation_score', 0.0),
                    'therapeutic_potential': discovery.get('therapeutic_potential', 0.0)
                }
            })
        
        return mappings
    
    def _calculate_sequence_properties(self, sequence: str) -> Dict[str, Any]:
        """Calculate basic sequence properties"""
        
        amino_acid_counts = {}
        for aa in sequence:
            amino_acid_counts[aa] = amino_acid_counts.get(aa, 0) + 1
        
        # Calculate composition features
        hydrophobic_count = sum(1 for aa in sequence if aa in 'FILVWYAM')
        charged_count = sum(1 for aa in sequence if aa in 'EDRK')
        polar_count = sum(1 for aa in sequence if aa in 'STNQ')
        
        return {
            'length': len(sequence),
            'hydrophobic_fraction': hydrophobic_count / len(sequence),
            'charged_fraction': charged_count / len(sequence),
            'polar_fraction': polar_count / len(sequence),
            'cysteine_count': sequence.count('C'),
            'proline_count': sequence.count('P'),
            'glycine_count': sequence.count('G'),
            'unique_amino_acids': len(set(sequence))
        }
    
    def _extract_motif_features(self, motifs: List[Dict]) -> Dict[str, Any]:
        """Extract features from discovered motifs"""
        
        if not motifs:
            return {'motif_count': 0, 'dominant_motif_type': 'none'}
        
        motif_types = [m.get('motif_type', 'unknown') for m in motifs]
        motif_confidences = [m.get('confidence', 0.0) for m in motifs]
        
        return {
            'motif_count': len(motifs),
            'dominant_motif_type': max(set(motif_types), key=motif_types.count) if motif_types else 'none',
            'avg_motif_confidence': sum(motif_confidences) / len(motif_confidences) if motif_confidences else 0.0,
            'max_motif_confidence': max(motif_confidences) if motif_confidences else 0.0
        }
    
    def _create_motif_outcome_datasets(self, training_data: List[Dict]) -> List[Dict[str, Any]]:
        """Create motif to outcome prediction datasets"""
        
        datasets = []
        for item in training_data:
            discovery = item['discovery']
            motifs = item['motifs']
            solutions = item['solutions']
            indications = item['indications']
            
            if not motifs:
                continue
                
            for motif in motifs:
                # Create motif-outcome pairs
                outcomes = []
                
                # Add therapeutic outcomes
                for solution in solutions:
                    outcomes.append({
                        'type': 'therapeutic',
                        'category': solution.get('solution_type', 'unknown'),
                        'efficacy': solution.get('predicted_efficacy', 0.0)
                    })
                
                # Add clinical outcomes
                for indication in indications:
                    outcomes.append({
                        'type': 'clinical',
                        'category': indication.get('name', 'unknown'),
                        'priority': indication.get('priority_score', 0.0)
                    })
                
                if outcomes:
                    datasets.append({
                        'motif': {
                            'type': motif.get('motif_type', 'unknown'),
                            'sequence': motif.get('sequence_fragment', ''),
                            'confidence': motif.get('confidence', 0.0),
                            'length': motif.get('length', 0)
                        },
                        'outcomes': outcomes,
                        'discovery_quality': discovery.get('validation_score', 0.0)
                    })
        
        return datasets
    
    def _save_training_datasets(self, datasets: Dict[str, Any]) -> Dict[str, Any]:
        """Save training datasets to files"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save each dataset type
        files_created = []
        total_samples = 0
        
        for dataset_name, dataset in datasets.items():
            if dataset_name == 'metadata':
                continue
                
            filename = f"{dataset_name}_{timestamp}.json"
            filepath = self.training_data_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(dataset, f, indent=2)
            
            files_created.append(filename)
            total_samples += len(dataset) if isinstance(dataset, list) else 1
        
        # Save metadata
        metadata_file = self.training_data_dir / f"training_metadata_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(datasets['metadata'], f, indent=2)
        
        return {
            'files_created': files_created,
            'total_samples': total_samples,
            'timestamp': timestamp,
            'training_data_dir': str(self.training_data_dir)
        }
    
    def implement_active_learning(self) -> Dict[str, Any]:
        """
        Phase 3.2: Implement active learning to identify knowledge gaps
        
        This method analyzes the current knowledge state and identifies areas
        where the system is most uncertain, prioritizing them for discovery.
        """
        
        try:
            # Analyze convergence patterns
            convergence_analysis = self._analyze_convergence_patterns()
            
            # Identify knowledge gaps
            knowledge_gaps = self._identify_knowledge_gaps()
            
            # Generate targeted sequences for uncertain areas
            targeted_sequences = self._generate_targeted_sequences(knowledge_gaps)
            
            # Create active learning priorities
            learning_priorities = self._create_learning_priorities(convergence_analysis, knowledge_gaps)
            
            # Save active learning data
            active_learning_info = self._save_active_learning_data({
                'convergence_analysis': convergence_analysis,
                'knowledge_gaps': knowledge_gaps,
                'targeted_sequences': targeted_sequences,
                'learning_priorities': learning_priorities,
                'metadata': {
                    'creation_date': datetime.now().isoformat(),
                    'version': 'Phase3_ActiveLearning'
                }
            })
            
            logger.info(f"✅ Active learning analysis complete: {len(knowledge_gaps)} gaps identified")
            
            return {
                'success': True,
                'knowledge_gaps': len(knowledge_gaps),
                'targeted_sequences': len(targeted_sequences),
                'priority_areas': len(learning_priorities),
                'active_learning_info': active_learning_info
            }
            
        except Exception as e:
            logger.error(f"Error implementing active learning: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_convergence_patterns(self) -> Dict[str, Any]:
        """Analyze FoT convergence patterns to identify difficult cases"""
        
        with self.driver.session() as session:
            # Get convergence statistics
            result = session.run("""
                MATCH (d:Discovery)
                WHERE d.fot_history IS NOT NULL
                RETURN d.id as discovery_id,
                       d.sequence_length as length,
                       d.fot_value as final_fot,
                       d.fot_history as history,
                       d.validation_score as score
                ORDER BY d.validation_score DESC
                LIMIT 500
            """)
            
            convergence_data = []
            for record in result:
                history = record['history']
                if history and len(history) > 1:
                    convergence_rate = abs(history[-1] - history[0]) / len(history)
                    stability = self._calculate_stability(history)
                    
                    convergence_data.append({
                        'discovery_id': record['discovery_id'],
                        'sequence_length': record['length'],
                        'final_fot': record['final_fot'],
                        'convergence_rate': convergence_rate,
                        'stability': stability,
                        'validation_score': record['score']
                    })
            
            # Analyze patterns
            slow_converging = [d for d in convergence_data if d['convergence_rate'] < 0.01]
            unstable_systems = [d for d in convergence_data if d['stability'] < 0.5]
            
            return {
                'total_analyzed': len(convergence_data),
                'slow_converging_count': len(slow_converging),
                'unstable_systems_count': len(unstable_systems),
                'avg_convergence_rate': sum(d['convergence_rate'] for d in convergence_data) / len(convergence_data) if convergence_data else 0,
                'challenging_lengths': self._identify_challenging_lengths(convergence_data)
            }
    
    def _identify_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """Identify areas where the system lacks knowledge"""
        
        gaps = []
        
        with self.driver.session() as session:
            # Find under-represented sequence patterns
            result = session.run("""
                MATCH (s:Sequence)
                WITH s.length as length, count(s) as count
                WHERE count < 5 AND length > 6 AND length < 50
                RETURN length, count
                ORDER BY count ASC, length ASC
                LIMIT 20
            """)
            
            for record in result:
                gaps.append({
                    'type': 'sequence_length_gap',
                    'length': record['length'],
                    'current_count': record['count'],
                    'priority': 1.0 - (record['count'] / 10.0),  # Higher priority for fewer examples
                    'description': f"Under-represented sequence length: {record['length']} residues"
                })
            
            # Find motif gaps
            motif_result = session.run("""
                MATCH (m:StructuralMotif)
                WITH m.motif_type as type, count(m) as count, avg(m.confidence) as avg_conf
                WHERE count < 10
                RETURN type, count, avg_conf
                ORDER BY count ASC
                LIMIT 15
            """)
            
            for record in motif_result:
                gaps.append({
                    'type': 'motif_gap',
                    'motif_type': record['type'],
                    'current_count': record['count'],
                    'avg_confidence': record['avg_conf'],
                    'priority': 0.8,
                    'description': f"Insufficient examples of {record['type']} motifs"
                })
        
        return gaps
    
    def _generate_targeted_sequences(self, knowledge_gaps: List[Dict]) -> List[Dict[str, Any]]:
        """Generate sequences to fill identified knowledge gaps"""
        
        targeted_sequences = []
        
        for gap in knowledge_gaps:
            if gap['type'] == 'sequence_length_gap':
                # Generate sequences of the under-represented length
                target_length = gap['length']
                for i in range(5):  # Generate 5 sequences per gap
                    sequence = self._generate_sequence_for_length(target_length)
                    targeted_sequences.append({
                        'sequence': sequence,
                        'target_length': target_length,
                        'gap_type': 'length_diversity',
                        'priority': gap['priority'],
                        'purpose': f"Fill length gap for {target_length}-residue proteins"
                    })
            
            elif gap['type'] == 'motif_gap':
                # Generate sequences likely to contain the missing motif
                motif_type = gap['motif_type']
                for i in range(3):  # Generate 3 sequences per motif gap
                    sequence = self._generate_sequence_for_motif(motif_type)
                    targeted_sequences.append({
                        'sequence': sequence,
                        'target_motif': motif_type,
                        'gap_type': 'motif_diversity',
                        'priority': gap['priority'],
                        'purpose': f"Increase examples of {motif_type} motifs"
                    })
        
        return targeted_sequences
    
    def _generate_sequence_for_length(self, target_length: int) -> str:
        """Generate a sequence of specific length with diverse properties"""
        
        # Simple sequence generation with balanced composition
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        import random
        
        # Ensure some structural diversity
        sequence = []
        
        # Add some charged residues (20%)
        charged_count = max(1, target_length // 5)
        charged_aa = 'EDRK'
        
        # Add some hydrophobic residues (30%)
        hydrophobic_count = max(1, target_length * 3 // 10)
        hydrophobic_aa = 'FILVWYAM'
        
        # Add charged residues
        for _ in range(charged_count):
            sequence.append(random.choice(charged_aa))
        
        # Add hydrophobic residues
        for _ in range(hydrophobic_count):
            sequence.append(random.choice(hydrophobic_aa))
        
        # Fill remaining with diverse amino acids
        remaining = target_length - len(sequence)
        for _ in range(remaining):
            sequence.append(random.choice(amino_acids))
        
        # Shuffle to avoid patterns
        random.shuffle(sequence)
        
        return ''.join(sequence)
    
    def _generate_sequence_for_motif(self, motif_type: str) -> str:
        """Generate a sequence likely to contain a specific motif type"""
        
        import random
        
        # Motif-specific sequence patterns
        motif_patterns = {
            'beta_hairpin': 'FKVIGG',  # Example beta hairpin motif
            'alpha_helix': 'EEAKAAAK',  # Example alpha helix motif
            'cysteine_bridge': 'CXXXXC',  # Cysteine bridge pattern
            'binding_site': 'FILVWY',  # Hydrophobic binding site
        }
        
        # Get base pattern
        base_pattern = motif_patterns.get(motif_type, 'AKDEFG')
        
        # Expand to full sequence (20-30 residues)
        target_length = random.randint(20, 30)
        sequence = list(base_pattern)
        
        # Fill remaining positions
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        while len(sequence) < target_length:
            sequence.append(random.choice(amino_acids))
        
        # Insert the motif pattern at a random position
        if len(base_pattern) < len(sequence):
            insert_pos = random.randint(0, len(sequence) - len(base_pattern))
            for i, aa in enumerate(base_pattern):
                if insert_pos + i < len(sequence):
                    sequence[insert_pos + i] = aa
        
        return ''.join(sequence)
    
    def _create_learning_priorities(self, convergence_analysis: Dict, knowledge_gaps: List[Dict]) -> List[Dict[str, Any]]:
        """Create prioritized learning targets"""
        
        priorities = []
        
        # Add convergence-based priorities
        if convergence_analysis['slow_converging_count'] > 0:
            priorities.append({
                'type': 'convergence_improvement',
                'priority': 0.9,
                'target': 'slow_converging_sequences',
                'count': convergence_analysis['slow_converging_count'],
                'description': 'Focus on sequences with slow FoT convergence'
            })
        
        if convergence_analysis['unstable_systems_count'] > 0:
            priorities.append({
                'type': 'stability_improvement',
                'priority': 0.85,
                'target': 'unstable_systems',
                'count': convergence_analysis['unstable_systems_count'],
                'description': 'Improve stability of quantum state systems'
            })
        
        # Add knowledge gap priorities
        for gap in sorted(knowledge_gaps, key=lambda x: x['priority'], reverse=True)[:10]:
            priorities.append({
                'type': 'knowledge_gap',
                'priority': gap['priority'],
                'target': gap['type'],
                'description': gap['description']
            })
        
        return sorted(priorities, key=lambda x: x['priority'], reverse=True)
    
    def _save_active_learning_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save active learning analysis data"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"active_learning_analysis_{timestamp}.json"
        filepath = self.active_learning_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {
            'filename': filename,
            'filepath': str(filepath),
            'timestamp': timestamp
        }
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _calculate_stability(self, history: List[float]) -> float:
        """Calculate stability score from FoT history"""
        if len(history) < 2:
            return 1.0
        
        # Calculate how much the values fluctuate
        differences = [abs(history[i+1] - history[i]) for i in range(len(history)-1)]
        avg_change = sum(differences) / len(differences)
        
        # Stability is inverse of average change (normalized)
        return max(0.0, 1.0 - (avg_change * 10))  # Scale factor of 10
    
    def _identify_challenging_lengths(self, convergence_data: List[Dict]) -> List[int]:
        """Identify sequence lengths that are challenging for the system"""
        
        length_performance = {}
        for item in convergence_data:
            length = item['sequence_length']
            if length not in length_performance:
                length_performance[length] = []
            length_performance[length].append(item['convergence_rate'])
        
        # Find lengths with poor average convergence
        challenging_lengths = []
        for length, rates in length_performance.items():
            avg_rate = sum(rates) / len(rates)
            if avg_rate < 0.015 and len(rates) >= 3:  # Multiple examples of poor performance
                challenging_lengths.append(length)
        
        return sorted(challenging_lengths)

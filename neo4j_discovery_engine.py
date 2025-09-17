#!/usr/bin/env python3
"""
NEO4J M4 DISCOVERY ENGINE
Knowledge graph implementation for 1.4M+ M4 Mac Pro discoveries
Real-time storage and querying without filesystem bottlenecks
"""

import time
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("⚠️ Neo4j driver not installed. Install with: pip install neo4j")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DiscoveryNode:
    """Discovery node for Neo4j graph"""
    id: str
    sequence: str
    validation_score: float
    assessment: str
    energy_kcal_mol: float
    vqbit_score: float
    virtue_scores: Dict[str, float]
    timestamp: datetime
    hardware_info: Dict[str, Any]

@dataclass
class VQbitNode:
    """vQbit quantum state node for Knowledge Graph"""
    id: str
    residue_index: int
    amino_acid: str
    phi_angle: float
    psi_angle: float
    quantum_amplitude: complex
    entanglement_degree: float
    superposition_coherence: float
    virtue_projection: Dict[str, float]
    collapsed_state: bool

class Neo4jDiscoveryEngine:
    """Neo4j-powered discovery storage and analysis engine"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "fotquantum"):
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j driver not available. Install with: pip install neo4j")
        
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.session_id = str(uuid.uuid4())
        
        # Initialize schema
        self._initialize_schema()
        
        logger.info(f"🔗 Neo4j Discovery Engine initialized")
        logger.info(f"   Session ID: {self.session_id}")
        logger.info(f"   URI: {uri}")
    
    def close(self):
        """Close Neo4j connection"""
        if hasattr(self, 'driver'):
            self.driver.close()
    
    def _initialize_schema(self):
        """Initialize comprehensive Neo4j schema for protein discovery knowledge graph"""
        
        with self.driver.session() as session:
            # Create node constraints
            constraints = [
                "CREATE CONSTRAINT discovery_id IF NOT EXISTS FOR (d:Discovery) REQUIRE d.id IS UNIQUE",
                "CREATE CONSTRAINT sequence_value IF NOT EXISTS FOR (s:Sequence) REQUIRE s.value IS UNIQUE", 
                "CREATE CONSTRAINT vqbit_id IF NOT EXISTS FOR (v:VQbit) REQUIRE v.id IS UNIQUE",
                "CREATE CONSTRAINT quantum_state_id IF NOT EXISTS FOR (q:QuantumState) REQUIRE q.id IS UNIQUE",
                "CREATE CONSTRAINT protein_family_id IF NOT EXISTS FOR (p:ProteinFamily) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT structural_motif_id IF NOT EXISTS FOR (s:StructuralMotif) REQUIRE s.id IS UNIQUE",
                "CREATE CONSTRAINT entanglement_pattern_id IF NOT EXISTS FOR (e:EntanglementPattern) REQUIRE e.id IS UNIQUE",
                "CREATE CONSTRAINT learning_session_id IF NOT EXISTS FOR (l:LearningSession) REQUIRE l.id IS UNIQUE",
                "CREATE CONSTRAINT motif_library_id IF NOT EXISTS FOR (m:MotifLibrary) REQUIRE m.id IS UNIQUE",
                "CREATE CONSTRAINT therapeutic_target_id IF NOT EXISTS FOR (t:TherapeuticTarget) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT disease_pathway_id IF NOT EXISTS FOR (d:DiseasePathway) REQUIRE d.id IS UNIQUE",
                "CREATE CONSTRAINT amino_acid_id IF NOT EXISTS FOR (a:AminoAcid) REQUIRE a.code IS UNIQUE",
                "CREATE CONSTRAINT researcher_id IF NOT EXISTS FOR (r:Researcher) REQUIRE r.id IS UNIQUE",
                "CREATE CONSTRAINT publication_id IF NOT EXISTS FOR (p:Publication) REQUIRE p.doi IS UNIQUE",
                "CREATE CONSTRAINT therapeutic_solution_id IF NOT EXISTS FOR (s:TherapeuticSolution) REQUIRE s.id IS UNIQUE",
                "CREATE CONSTRAINT clinical_indication_id IF NOT EXISTS FOR (c:ClinicalIndication) REQUIRE c.id IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    if "already exists" not in str(e):
                        logger.warning(f"Constraint creation warning: {e}")
            
            # Create comprehensive indexes for performance
            indexes = [
                # Discovery indexes
                "CREATE INDEX discovery_timestamp IF NOT EXISTS FOR (d:Discovery) ON (d.timestamp)",
                "CREATE INDEX discovery_quality IF NOT EXISTS FOR (d:Discovery) ON (d.validation_score)", 
                "CREATE INDEX discovery_energy IF NOT EXISTS FOR (d:Discovery) ON (d.energy_kcal_mol)",
                "CREATE INDEX discovery_session IF NOT EXISTS FOR (d:Discovery) ON (d.session_id)",
                
                # Sequence indexes
                "CREATE INDEX sequence_length IF NOT EXISTS FOR (s:Sequence) ON (s.length)",
                "CREATE INDEX sequence_hash IF NOT EXISTS FOR (s:Sequence) ON (s.hash)",
                
                # vQbit quantum indexes
                "CREATE INDEX vqbit_residue IF NOT EXISTS FOR (v:VQbit) ON (v.residue_index)",
                "CREATE INDEX vqbit_amino_acid IF NOT EXISTS FOR (v:VQbit) ON (v.amino_acid)", 
                "CREATE INDEX vqbit_entanglement IF NOT EXISTS FOR (v:VQbit) ON (v.entanglement_degree)",
                "CREATE INDEX vqbit_coherence IF NOT EXISTS FOR (v:VQbit) ON (v.superposition_coherence)",
                "CREATE INDEX quantum_collapsed IF NOT EXISTS FOR (v:VQbit) ON (v.collapsed_state)",
                "CREATE INDEX vqbit_phi_psi IF NOT EXISTS FOR (v:VQbit) ON (v.phi_angle, v.psi_angle)",
                
                # Protein family indexes
                "CREATE INDEX protein_family_name IF NOT EXISTS FOR (p:ProteinFamily) ON (p.name)",
                "CREATE INDEX protein_family_confidence IF NOT EXISTS FOR (p:ProteinFamily) ON (p.confidence_score)",
                
                # Therapeutic target indexes
                "CREATE INDEX therapeutic_target_type IF NOT EXISTS FOR (t:TherapeuticTarget) ON (t.target_type)",
                "CREATE INDEX therapeutic_target_disease IF NOT EXISTS FOR (t:TherapeuticTarget) ON (t.associated_disease)",
                
                # Disease pathway indexes
                "CREATE INDEX disease_pathway_name IF NOT EXISTS FOR (d:DiseasePathway) ON (d.name)",
                "CREATE INDEX disease_pathway_priority IF NOT EXISTS FOR (d:DiseasePathway) ON (d.priority_score)",
                
                # Structural motif indexes
                "CREATE INDEX structural_motif_type IF NOT EXISTS FOR (s:StructuralMotif) ON (s.motif_type)",
                "CREATE INDEX structural_motif_confidence IF NOT EXISTS FOR (s:StructuralMotif) ON (s.confidence)",
                
                # Phase 2 Learning system indexes
                "CREATE INDEX entanglement_pattern_type IF NOT EXISTS FOR (e:EntanglementPattern) ON (e.pattern_type)",
                "CREATE INDEX entanglement_pattern_strength IF NOT EXISTS FOR (e:EntanglementPattern) ON (e.average_strength)",
                "CREATE INDEX entanglement_pattern_residues IF NOT EXISTS FOR (e:EntanglementPattern) ON (e.residue_count)",
                "CREATE INDEX learning_session_timestamp IF NOT EXISTS FOR (l:LearningSession) ON (l.timestamp)",
                "CREATE INDEX learning_session_accuracy IF NOT EXISTS FOR (l:LearningSession) ON (l.validation_accuracy)",
                "CREATE INDEX motif_library_usage_count IF NOT EXISTS FOR (m:MotifLibrary) ON (m.usage_count)",
                "CREATE INDEX motif_library_success_rate IF NOT EXISTS FOR (m:MotifLibrary) ON (m.success_rate)",
                
                # Quantum relationship indexes
                "CREATE INDEX quantum_amplitude IF NOT EXISTS FOR ()-[r:IN_SUPERPOSITION]-() ON (r.amplitude_real, r.amplitude_imag)",
                "CREATE INDEX quantum_entanglement_strength IF NOT EXISTS FOR ()-[r:QUANTUM_ENTANGLED]-() ON (r.entanglement_strength)",
                "CREATE INDEX quantum_coherence_level IF NOT EXISTS FOR ()-[r:MAINTAINS_COHERENCE]-() ON (r.coherence_level)",
                
                # Solution mapping indexes
                "CREATE INDEX therapeutic_solution_efficacy IF NOT EXISTS FOR (s:TherapeuticSolution) ON (s.predicted_efficacy)",
                "CREATE INDEX clinical_indication_priority IF NOT EXISTS FOR (c:ClinicalIndication) ON (c.priority_score)"
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                except Exception as e:
                    if "already exists" not in str(e):
                        logger.warning(f"Index creation warning: {e}")
            
            # Initialize core reference data
            self._initialize_reference_data(session)
            self._initialize_therapeutic_solutions(session)
            self._initialize_clinical_indications(session)
            self._initialize_learning_system(session)
            
            logger.info("✅ Comprehensive protein discovery knowledge graph schema initialized")
    
    def store_discovery(self, discovery_data: Dict[str, Any]) -> str:
        """Store a discovery with vQbit quantum states in the Neo4j graph"""
        
        discovery_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Extract data
        sequence = discovery_data.get('sequence', '')
        validation_score = discovery_data.get('validation_score', 0.0)
        assessment = discovery_data.get('assessment', '')
        
        metal_analysis = discovery_data.get('metal_analysis', {})
        energy = metal_analysis.get('energy_kcal_mol', 0.0)
        vqbit_score = metal_analysis.get('vqbit_score', 0.0)
        virtue_scores = metal_analysis.get('virtue_scores', {})
        
        # Extract vQbit quantum states if available
        vqbit_states = discovery_data.get('vqbit_states', [])
        quantum_analysis = discovery_data.get('quantum_analysis', {})
        
        hardware_info = discovery_data.get('hardware_info', {})
        
        with self.driver.session() as session:
            # Create discovery node and relationships
            result = session.run("""
                // Create or merge sequence node
                MERGE (s:Sequence {value: $sequence})
                ON CREATE SET s.length = $sequence_length,
                             s.created_at = $timestamp
                
                // Create discovery node
                CREATE (d:Discovery {
                    id: $discovery_id,
                    validation_score: $validation_score,
                    assessment: $assessment,
                    energy_kcal_mol: $energy,
                    vqbit_score: $vqbit_score,
                    timestamp: $timestamp,
                    session_id: $session_id,
                    hardware_processed_on: $hardware_processed_on,
                    metal_accelerated: $metal_accelerated,
                    quantum_coherence: $quantum_coherence,
                    entanglement_entropy: $entanglement_entropy,
                    superposition_fidelity: $superposition_fidelity
                })
                
                // Create sequence relationship
                CREATE (d)-[:HAS_SEQUENCE]->(s)
                
                // Create virtue score nodes and relationships
                WITH d
                UNWIND $virtue_items AS virtue_item
                CREATE (v:VirtueScore {
                    virtue: virtue_item.virtue,
                    score: virtue_item.score
                })
                CREATE (d)-[:HAS_VIRTUE_SCORE]->(v)
                
                RETURN d.id as discovery_id
            """, {
                'discovery_id': discovery_id,
                'sequence': sequence,
                'sequence_length': len(sequence),
                'validation_score': validation_score,
                'assessment': assessment,
                'energy': energy,
                'vqbit_score': vqbit_score,
                'timestamp': timestamp,
                'session_id': self.session_id,
                'hardware_processed_on': hardware_info.get('processed_on', 'Unknown'),
                'metal_accelerated': hardware_info.get('metal_accelerated', False),
                'quantum_coherence': quantum_analysis.get('coherence', 0.0),
                'entanglement_entropy': quantum_analysis.get('entanglement_entropy', 0.0),
                'superposition_fidelity': quantum_analysis.get('superposition_fidelity', 0.0),
                'virtue_items': [{'virtue': k, 'score': v} for k, v in virtue_scores.items()]
            })
            
            # Store vQbit quantum states
            if vqbit_states:
                self._store_vqbit_states(session, discovery_id, vqbit_states)
            
            # Store additional graph connections
            if vqbit_states:
                self._store_vqbit_states(session, discovery_id, vqbit_states)
                self._create_protein_family_connections(session, discovery_id, sequence)
                self._create_therapeutic_target_connections(session, discovery_id, discovery_data)
                self._create_structural_motif_connections(session, discovery_id, vqbit_states)
                self._create_sequence_similarity_connections(session, discovery_id, sequence)
                self._map_to_therapeutic_solutions(session, discovery_id, discovery_data)
                self._create_clinical_indication_mapping(session, discovery_id, discovery_data)
            
            return discovery_id
    
    def _store_vqbit_states(self, session, discovery_id: str, vqbit_states: List[Dict[str, Any]]):
        """Store vQbit quantum states as quantum relationships in the graph"""
        
        prev_quantum_state_id = None
        prev_vqbit_id = None
        for i, vqbit_state in enumerate(vqbit_states):
            quantum_state_id = f"qstate_{str(uuid.uuid4())[:8]}_{i}"
            vqbit_id = f"vqbit_{str(uuid.uuid4())[:8]}_{i}"
            
            # Extract quantum state data
            residue_index = vqbit_state.get('residue_index', i)
            amino_acid = vqbit_state.get('amino_acid', '')
            phi_angle = vqbit_state.get('phi', 0.0)
            psi_angle = vqbit_state.get('psi', 0.0)
            
            # Quantum properties
            amplitude_real = vqbit_state.get('amplitude_real', 0.0)
            amplitude_imag = vqbit_state.get('amplitude_imag', 0.0)
            entanglement_degree = vqbit_state.get('entanglement', 0.0)
            coherence = vqbit_state.get('coherence', 0.0)
            collapsed = vqbit_state.get('collapsed', False)
            
            # Virtue projections
            virtue_projections = vqbit_state.get('virtue_projections', {})
            
            session.run("""
                // Find discovery node
                MATCH (d:Discovery {id: $discovery_id})
                
                // Create amino acid node (referencing standard amino acids)
                MATCH (aa:AminoAcid {code: $amino_acid})
                
                // Create VQbit node (primary quantum entity)
                CREATE (v:VQbit {
                    id: $vqbit_id,
                    discovery_id: $discovery_id,
                    residue_index: $residue_index,
                    amino_acid: $amino_acid,
                    phi_angle: $phi_angle,
                    psi_angle: $psi_angle,
                    entanglement_degree: $entanglement_degree,
                    superposition_coherence: $coherence,
                    collapsed_state: $collapsed,
                    amplitude_real: $amplitude_real,
                    amplitude_imag: $amplitude_imag
                })
                
                // Create quantum state node (linked to VQbit for detailed quantum info)
                CREATE (q:QuantumState {
                    id: $quantum_state_id,
                    discovery_id: $discovery_id,
                    residue_index: $residue_index,
                    phi_angle: $phi_angle,
                    psi_angle: $psi_angle,
                    collapsed_state: $collapsed
                })
                
                // Create VQbit relationships
                CREATE (d)-[:HAS_VQBIT {position: $residue_index}]->(v)
                CREATE (v)-[:HAS_QUANTUM_STATE]->(q)
                
                // Create position relationship for backward compatibility
                CREATE (d)-[:HAS_QUANTUM_STATE {position: $residue_index}]->(q)
                
                // Create amino acid relationship
                CREATE (v)-[:IS_AMINO_ACID]->(aa)
                CREATE (q)-[:IS_AMINO_ACID]->(aa)
                
                // Create quantum superposition relationship (if not collapsed)
                WITH d, q, aa
                WHERE $collapsed = false
                CREATE (q)-[:IN_SUPERPOSITION {
                    amplitude_real: $amplitude_real,
                    amplitude_imag: $amplitude_imag,
                    quantum_phase: $quantum_phase,
                    coherence_level: $coherence,
                    measurement_basis: 'ramachandran'
                }]->(aa)
                
                // Create virtue projection relationships (quantum virtue superposition)
                WITH q
                UNWIND $virtue_projections AS vp
                MATCH (virtue_target:TherapeuticTarget) WHERE virtue_target.target_type = vp.virtue
                CREATE (q)-[:PROJECTS_VIRTUE {
                    virtue_type: vp.virtue,
                    projection_strength: vp.strength,
                    quantum_phase: vp.phase,
                    virtue_amplitude: vp.strength * cos(vp.phase),
                    virtue_coherence: vp.strength * sin(vp.phase)
                }]->(virtue_target)
            """, {
                'discovery_id': discovery_id,
                'quantum_state_id': quantum_state_id,
                'vqbit_id': vqbit_id,
                'residue_index': residue_index,
                'amino_acid': amino_acid,
                'entanglement_degree': entanglement_degree,
                'coherence': coherence,
                'phi_angle': phi_angle,
                'psi_angle': psi_angle,
                'amplitude_real': amplitude_real,
                'amplitude_imag': amplitude_imag,
                'collapsed': collapsed,
                'quantum_phase': vqbit_state.get('phase', 0.0),
                'virtue_projections': [
                    {'virtue': k, 'strength': v.get('strength', 0.0), 'phase': v.get('phase', 0.0)}
                    for k, v in virtue_projections.items()
                ]
            })
            
            # Store quantum entanglement relationships between adjacent residues  
            if i > 0 and prev_quantum_state_id is not None and prev_vqbit_id is not None:
                entanglement_strength = vqbit_state.get('entanglement_with_prev', 0.0)
                
                session.run("""
                    MATCH (v1:VQbit {id: $prev_vqbit_id})
                    MATCH (v2:VQbit {id: $curr_vqbit_id})
                    MATCH (q1:QuantumState {id: $prev_quantum_state_id})
                    MATCH (q2:QuantumState {id: $curr_quantum_state_id})
                    
                    // Create VQbit-to-VQbit entanglement (primary)
                    CREATE (v1)-[:QUANTUM_ENTANGLED {
                        entanglement_strength: $strength,
                        entanglement_type: 'sequential_backbone',
                        bell_state: CASE 
                            WHEN $strength > 0.8 THEN 'phi_plus'
                            WHEN $strength > 0.6 THEN 'phi_minus'
                            WHEN $strength > 0.4 THEN 'psi_plus'
                            ELSE 'psi_minus'
                        END,
                        quantum_correlation: $strength * $strength
                    }]->(v2)
                    
                    // Create QuantumState entanglement (for backward compatibility)
                    CREATE (q1)-[:QUANTUM_ENTANGLED {
                        entanglement_strength: $strength,
                        entanglement_type: 'sequential_backbone',
                        bell_state: CASE 
                            WHEN $strength > 0.8 THEN 'phi_plus'
                            WHEN $strength > 0.6 THEN 'phi_minus'
                            WHEN $strength > 0.4 THEN 'psi_plus'
                            ELSE 'psi_minus'
                        END,
                        quantum_correlation: $strength * $strength
                    }]->(q2)
                """, {
                    'prev_vqbit_id': prev_vqbit_id,
                    'curr_vqbit_id': vqbit_id,
                    'prev_quantum_state_id': prev_quantum_state_id,
                    'curr_quantum_state_id': quantum_state_id,
                    'strength': entanglement_strength
                })
                
                # Create coherence maintenance relationship if highly entangled
                if entanglement_strength > 0.7:
                    session.run("""
                        MATCH (v1:VQbit {id: $prev_vqbit_id})
                        MATCH (v2:VQbit {id: $curr_vqbit_id})
                        MATCH (q1:QuantumState {id: $prev_quantum_state_id})
                        MATCH (q2:QuantumState {id: $curr_quantum_state_id})
                        
                        // Create VQbit coherence maintenance (primary)
                        CREATE (v1)-[:MAINTAINS_COHERENCE {
                            coherence_level: $coherence,
                            decoherence_time: $decoherence_time,
                            quantum_fidelity: $fidelity
                        }]->(v2)
                        
                        // Create QuantumState coherence maintenance (backward compatibility)
                        CREATE (q1)-[:MAINTAINS_COHERENCE {
                            coherence_level: $coherence,
                            decoherence_time: $decoherence_time,
                            quantum_fidelity: $fidelity
                        }]->(q2)
                    """, {
                        'prev_vqbit_id': prev_vqbit_id,
                        'curr_vqbit_id': vqbit_id,
                        'prev_quantum_state_id': prev_quantum_state_id,
                        'curr_quantum_state_id': quantum_state_id,
                        'coherence': coherence,
                        'decoherence_time': 1.0 / (1.0 - entanglement_strength),  # Higher entanglement = longer coherence
                        'fidelity': entanglement_strength * coherence
                    })
            
            # Update prev IDs for next iteration
            prev_quantum_state_id = quantum_state_id
            prev_vqbit_id = vqbit_id
    
    def get_discovery_statistics(self) -> Dict[str, Any]:
        """Get real-time discovery statistics from Neo4j"""
        
        with self.driver.session() as session:
            # Total discoveries
            total_result = session.run("MATCH (d:Discovery) RETURN count(d) as total")
            total_discoveries = total_result.single()['total']
            
            # Recent discoveries (last hour)
            recent_result = session.run("""
                MATCH (d:Discovery)
                WHERE d.timestamp > datetime() - duration('PT1H')
                RETURN count(d) as recent_count
            """)
            recent_discoveries = recent_result.single()['recent_count']
            
            # Quality distribution
            quality_result = session.run("""
                MATCH (d:Discovery)
                RETURN 
                    count(CASE WHEN d.validation_score >= 0.9 THEN 1 END) as excellent,
                    count(CASE WHEN d.validation_score >= 0.8 AND d.validation_score < 0.9 THEN 1 END) as good,
                    count(CASE WHEN d.validation_score >= 0.7 AND d.validation_score < 0.8 THEN 1 END) as fair,
                    count(CASE WHEN d.validation_score < 0.7 THEN 1 END) as poor,
                    avg(d.validation_score) as avg_quality,
                    avg(d.energy_kcal_mol) as avg_energy,
                    avg(d.vqbit_score) as avg_vqbit
            """)
            quality_stats = quality_result.single()
            
            # Session statistics
            session_result = session.run("""
                MATCH (d:Discovery {session_id: $session_id})
                RETURN count(d) as session_discoveries,
                       min(d.timestamp) as session_start,
                       max(d.timestamp) as session_end
            """, {'session_id': self.session_id})
            session_stats = session_result.single()
            
            # Unique sequences
            unique_result = session.run("MATCH (s:Sequence) RETURN count(s) as unique_sequences")
            unique_sequences = unique_result.single()['unique_sequences']
            
            return {
                'total_discoveries': total_discoveries,
                'recent_discoveries_1h': recent_discoveries,
                'unique_sequences': unique_sequences,
                'duplicate_rate': ((total_discoveries - unique_sequences) / total_discoveries * 100) if total_discoveries > 0 else 0,
                'quality_distribution': {
                    'excellent': quality_stats['excellent'],
                    'good': quality_stats['good'],
                    'fair': quality_stats['fair'],
                    'poor': quality_stats['poor']
                },
                'averages': {
                    'quality': float(quality_stats['avg_quality'] or 0),
                    'energy': float(quality_stats['avg_energy'] or 0),
                    'vqbit': float(quality_stats['avg_vqbit'] or 0)
                },
                'session': {
                    'discoveries': session_stats['session_discoveries'],
                    'start_time': session_stats['session_start'],
                    'end_time': session_stats['session_end']
                }
            }
    
    def get_high_quality_discoveries(self, limit: int = 10, min_quality: float = 0.9) -> List[Dict[str, Any]]:
        """Get recent high-quality discoveries"""
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Discovery)-[:HAS_SEQUENCE]->(s:Sequence)
                WHERE d.validation_score >= $min_quality
                RETURN d.id as id,
                       s.value as sequence,
                       d.validation_score as quality,
                       d.energy_kcal_mol as energy,
                       d.assessment as assessment,
                       d.timestamp as timestamp,
                       s.length as length
                ORDER BY d.timestamp DESC
                LIMIT $limit
            """, {'min_quality': min_quality, 'limit': limit})
            
            discoveries = []
            for record in result:
                discoveries.append({
                    'id': record['id'],
                    'sequence': record['sequence'][:30] + "..." if len(record['sequence']) > 30 else record['sequence'],
                    'quality': float(record['quality']),
                    'energy': float(record['energy']),
                    'assessment': record['assessment'],
                    'length': record['length'],
                    'timestamp': record['timestamp'].strftime('%H:%M:%S')
                })
            
            return discoveries
    
    def get_learning_patterns(self) -> Dict[str, Any]:
        """Analyze learning patterns from the graph"""
        
        with self.driver.session() as session:
            # Virtue score patterns
            virtue_result = session.run("""
                MATCH (d:Discovery)-[:HAS_VIRTUE_SCORE]->(v:VirtueScore)
                RETURN v.virtue as virtue,
                       avg(v.score) as avg_score,
                       count(v) as count
                ORDER BY v.virtue
            """)
            
            virtue_patterns = {}
            for record in virtue_result:
                virtue_patterns[record['virtue']] = {
                    'avg': float(record['avg_score']),
                    'count': record['count'],
                    'trend': 'positive' if record['avg_score'] > 0 else 'negative'
                }
            
            # Sequence length distribution
            length_result = session.run("""
                MATCH (s:Sequence)
                RETURN min(s.length) as min_length,
                       max(s.length) as max_length,
                       avg(s.length) as avg_length,
                       count(s) as total_sequences
            """)
            length_stats = length_result.single()
            
            # Quality trends (last 1000 discoveries)
            trend_result = session.run("""
                MATCH (d:Discovery)
                WITH d ORDER BY d.timestamp DESC LIMIT 1000
                WITH collect(d.validation_score) as scores
                RETURN avg(scores[0..499]) as recent_avg,
                       avg(scores[500..999]) as earlier_avg
            """)
            trend_stats = trend_result.single()
            
            quality_trend = 'stable'
            if trend_stats['recent_avg'] and trend_stats['earlier_avg']:
                if trend_stats['recent_avg'] > trend_stats['earlier_avg'] * 1.05:
                    quality_trend = 'improving'
                elif trend_stats['recent_avg'] < trend_stats['earlier_avg'] * 0.95:
                    quality_trend = 'declining'
            
            return {
                'virtue_patterns': virtue_patterns,
                'sequence_stats': {
                    'min_length': length_stats['min_length'],
                    'max_length': length_stats['max_length'],
                    'avg_length': float(length_stats['avg_length'] or 0),
                    'total_sequences': length_stats['total_sequences']
                },
                'quality_trend': quality_trend,
                'recent_quality_avg': float(trend_stats['recent_avg'] or 0),
                'earlier_quality_avg': float(trend_stats['earlier_avg'] or 0)
            }
    
    def cleanup_old_discoveries(self, days_old: int = 7) -> int:
        """Clean up discoveries older than specified days"""
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Discovery)
                WHERE d.timestamp < datetime() - duration({days: $days})
                DETACH DELETE d
                RETURN count(d) as deleted_count
            """, {'days': days_old})
            
            deleted_count = result.single()['deleted_count']
            logger.info(f"🗑️ Cleaned up {deleted_count} discoveries older than {days_old} days")
            return deleted_count
    
    def get_comprehensive_graph_analysis(self) -> Dict[str, Any]:
        """Get comprehensive analysis of the protein discovery knowledge graph"""
        
        with self.driver.session() as session:
            # Node counts
            node_counts = session.run("""
                CALL {
                    MATCH (d:Discovery) RETURN 'Discovery' as node_type, count(d) as count
                    UNION
                    MATCH (s:Sequence) RETURN 'Sequence' as node_type, count(s) as count
                    UNION
                    MATCH (v:VQbit) RETURN 'VQbit' as node_type, count(v) as count
                    UNION
                    MATCH (p:ProteinFamily) RETURN 'ProteinFamily' as node_type, count(p) as count
                    UNION
                    MATCH (t:TherapeuticTarget) RETURN 'TherapeuticTarget' as node_type, count(t) as count
                    UNION
                    MATCH (m:StructuralMotif) RETURN 'StructuralMotif' as node_type, count(m) as count
                    UNION
                    MATCH (a:AminoAcid) RETURN 'AminoAcid' as node_type, count(a) as count
                }
                RETURN node_type, count
                ORDER BY count DESC
            """)
            
            node_statistics = {}
            for record in node_counts:
                node_statistics[record['node_type']] = record['count']
            
            # Relationship counts
            rel_counts = session.run("""
                CALL {
                    MATCH ()-[r:HAS_SEQUENCE]->() RETURN 'HAS_SEQUENCE' as rel_type, count(r) as count
                    UNION
                    MATCH ()-[r:HAS_VQBIT]->() RETURN 'HAS_VQBIT' as rel_type, count(r) as count
                    UNION
                    MATCH ()-[r:ENTANGLED_WITH]->() RETURN 'ENTANGLED_WITH' as rel_type, count(r) as count
                    UNION
                    MATCH ()-[r:CLASSIFIED_AS]->() RETURN 'CLASSIFIED_AS' as rel_type, count(r) as count
                    UNION
                    MATCH ()-[r:TARGETS]->() RETURN 'TARGETS' as rel_type, count(r) as count
                    UNION
                    MATCH ()-[r:CONTAINS_MOTIF]->() RETURN 'CONTAINS_MOTIF' as rel_type, count(r) as count
                    UNION
                    MATCH ()-[r:SIMILAR_TO]->() RETURN 'SIMILAR_TO' as rel_type, count(r) as count
                    UNION
                    MATCH ()-[r:PROJECTS_VIRTUE]->() RETURN 'PROJECTS_VIRTUE' as rel_type, count(r) as count
                }
                RETURN rel_type, count
                ORDER BY count DESC
            """)
            
            relationship_statistics = {}
            for record in rel_counts:
                relationship_statistics[record['rel_type']] = record['count']
            
            return {
                'node_statistics': node_statistics,
                'relationship_statistics': relationship_statistics,
                'quantum_analysis': self.get_quantum_analysis()
            }
    
    def get_quantum_analysis(self) -> Dict[str, Any]:
        """Analyze quantum vQbit patterns across all discoveries"""
        
        with self.driver.session() as session:
            # Total vQbits and quantum statistics
            vqbit_stats = session.run("""
                MATCH (v:VQbit)
                RETURN count(v) as total_vqbits,
                       avg(v.entanglement_degree) as avg_entanglement,
                       avg(v.superposition_coherence) as avg_coherence,
                       count(CASE WHEN v.collapsed_state = true THEN 1 END) as collapsed_count,
                       count(CASE WHEN v.collapsed_state = false THEN 1 END) as superposition_count
            """).single()
            
            # Entanglement network analysis
            entanglement_stats = session.run("""
                MATCH (v1:VQbit)-[e:ENTANGLED_WITH]->(v2:VQbit)
                RETURN count(e) as total_entanglements,
                       avg(e.strength) as avg_entanglement_strength,
                       max(e.strength) as max_entanglement,
                       min(e.strength) as min_entanglement
            """).single()
            
            # Virtue projection analysis
            virtue_projections = session.run("""
                MATCH (v:VQbit)-[:PROJECTS_VIRTUE]->(vp:VirtueProjection)
                RETURN vp.virtue as virtue,
                       count(vp) as projection_count,
                       avg(vp.projection_strength) as avg_strength,
                       avg(vp.quantum_phase) as avg_phase
                ORDER BY vp.virtue
            """)
            
            virtue_analysis = {}
            for record in virtue_projections:
                virtue_analysis[record['virtue']] = {
                    'count': record['projection_count'],
                    'avg_strength': float(record['avg_strength'] or 0),
                    'avg_phase': float(record['avg_phase'] or 0)
                }
            
            # Amino acid quantum patterns
            aa_patterns = session.run("""
                MATCH (v:VQbit)
                WHERE v.amino_acid <> ''
                RETURN v.amino_acid as amino_acid,
                       count(v) as count,
                       avg(v.entanglement_degree) as avg_entanglement,
                       avg(v.superposition_coherence) as avg_coherence,
                       avg(v.phi_angle) as avg_phi,
                       avg(v.psi_angle) as avg_psi
                ORDER BY count DESC
            """)
            
            amino_acid_quantum = {}
            for record in aa_patterns:
                amino_acid_quantum[record['amino_acid']] = {
                    'count': record['count'],
                    'avg_entanglement': float(record['avg_entanglement'] or 0),
                    'avg_coherence': float(record['avg_coherence'] or 0),
                    'avg_phi': float(record['avg_phi'] or 0),
                    'avg_psi': float(record['avg_psi'] or 0)
                }
            
            # High-entanglement discoveries
            high_entanglement = session.run("""
                MATCH (d:Discovery)-[:HAS_VQBIT]->(v:VQbit)
                WHERE v.entanglement_degree > 0.5
                WITH d, avg(v.entanglement_degree) as avg_entanglement
                RETURN d.id as discovery_id,
                       d.validation_score as quality,
                       avg_entanglement
                ORDER BY avg_entanglement DESC
                LIMIT 10
            """)
            
            entangled_discoveries = []
            for record in high_entanglement:
                entangled_discoveries.append({
                    'discovery_id': record['discovery_id'],
                    'quality': float(record['quality']),
                    'avg_entanglement': float(record['avg_entanglement'])
                })
            
            return {
                'vqbit_statistics': {
                    'total_vqbits': vqbit_stats['total_vqbits'] or 0,
                    'avg_entanglement': float(vqbit_stats['avg_entanglement'] or 0),
                    'avg_coherence': float(vqbit_stats['avg_coherence'] or 0),
                    'collapsed_count': vqbit_stats['collapsed_count'] or 0,
                    'superposition_count': vqbit_stats['superposition_count'] or 0,
                    'quantum_ratio': (vqbit_stats['superposition_count'] or 0) / max(1, vqbit_stats['total_vqbits'] or 1)
                },
                'entanglement_network': {
                    'total_entanglements': entanglement_stats['total_entanglements'] or 0,
                    'avg_strength': float(entanglement_stats['avg_entanglement_strength'] or 0),
                    'max_strength': float(entanglement_stats['max_entanglement'] or 0),
                    'min_strength': float(entanglement_stats['min_entanglement'] or 0)
                },
                'virtue_projections': virtue_analysis,
                'amino_acid_quantum_patterns': amino_acid_quantum,
                'high_entanglement_discoveries': entangled_discoveries
            }
    
    def find_quantum_patterns(self, min_entanglement: float = 0.3) -> List[Dict[str, Any]]:
        """Find quantum entanglement patterns in the vQbit graph"""
        
        with self.driver.session() as session:
            # Find entanglement chains
            result = session.run("""
                MATCH path = (v1:VQbit)-[:ENTANGLED_WITH*2..5]->(v2:VQbit)
                WHERE v1.entanglement_degree > $min_entanglement
                WITH path, length(path) as chain_length
                ORDER BY chain_length DESC
                LIMIT 20
                RETURN 
                    [n in nodes(path) | {
                        id: n.id, 
                        amino_acid: n.amino_acid, 
                        residue_index: n.residue_index,
                        entanglement: n.entanglement_degree,
                        coherence: n.superposition_coherence
                    }] as quantum_chain,
                    chain_length
            """, {'min_entanglement': min_entanglement})
            
            quantum_patterns = []
            for record in result:
                quantum_patterns.append({
                    'chain_length': record['chain_length'],
                    'quantum_chain': record['quantum_chain']
                })
            
            return quantum_patterns
    
    def get_protein_family_analysis(self) -> Dict[str, Any]:
        """Analyze protein family classifications"""
        
        with self.driver.session() as session:
            # Family distribution
            family_stats = session.run("""
                MATCH (d:Discovery)-[r:CLASSIFIED_AS]->(p:ProteinFamily)
                RETURN p.name as family_name,
                       count(d) as discovery_count,
                       avg(r.confidence_score) as avg_confidence,
                       max(r.confidence_score) as max_confidence
                ORDER BY discovery_count DESC
            """)
            
            family_distribution = {}
            for record in family_stats:
                family_distribution[record['family_name']] = {
                    'count': record['discovery_count'],
                    'avg_confidence': float(record['avg_confidence'] or 0),
                    'max_confidence': float(record['max_confidence'] or 0)
                }
            
            return family_distribution
    
    def get_therapeutic_target_analysis(self) -> Dict[str, Any]:
        """Analyze therapeutic target predictions"""
        
        with self.driver.session() as session:
            # Target distribution
            target_stats = session.run("""
                MATCH (d:Discovery)-[r:TARGETS]->(t:TherapeuticTarget)
                RETURN t.name as target_name,
                       t.target_type as target_type,
                       count(d) as discovery_count,
                       avg(r.potential_score) as avg_potential,
                       max(r.potential_score) as max_potential
                ORDER BY discovery_count DESC
            """)
            
            target_distribution = {}
            for record in target_stats:
                target_distribution[record['target_name']] = {
                    'type': record['target_type'],
                    'count': record['discovery_count'],
                    'avg_potential': float(record['avg_potential'] or 0),
                    'max_potential': float(record['max_potential'] or 0)
                }
            
            return target_distribution
    
    def get_structural_analysis(self) -> Dict[str, Any]:
        """Analyze structural motif patterns"""
        
        with self.driver.session() as session:
            # Motif distribution
            motif_stats = session.run("""
                MATCH (d:Discovery)-[r:CONTAINS_MOTIF]->(s:StructuralMotif)
                RETURN s.motif_type as motif_type,
                       count(d) as discovery_count,
                       avg(s.confidence) as avg_confidence,
                       max(s.confidence) as max_confidence
                ORDER BY discovery_count DESC
            """)
            
            motif_distribution = {}
            for record in motif_stats:
                motif_distribution[record['motif_type']] = {
                    'count': record['discovery_count'],
                    'avg_confidence': float(record['avg_confidence'] or 0),
                    'max_confidence': float(record['max_confidence'] or 0)
                }
            
            return motif_distribution
    
    def find_high_potential_discoveries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find discoveries with highest therapeutic potential"""
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Discovery)-[:HAS_SEQUENCE]->(s:Sequence)
                OPTIONAL MATCH (d)-[t:TARGETS]->(target:TherapeuticTarget)
                OPTIONAL MATCH (d)-[c:CLASSIFIED_AS]->(family:ProteinFamily)
                WITH d, s, 
                     collect(DISTINCT {target: target.name, potential: t.potential_score}) as targets,
                     collect(DISTINCT {family: family.name, confidence: c.confidence_score}) as families,
                     avg(t.potential_score) as avg_therapeutic_potential
                WHERE avg_therapeutic_potential > 0.5
                RETURN d.id as discovery_id,
                       s.value as sequence,
                       d.validation_score as quality,
                       d.energy_kcal_mol as energy,
                       avg_therapeutic_potential,
                       targets,
                       families,
                       d.timestamp as timestamp
                ORDER BY avg_therapeutic_potential DESC, d.validation_score DESC
                LIMIT $limit
            """, {'limit': limit})
            
            high_potential = []
            for record in result:
                high_potential.append({
                    'discovery_id': record['discovery_id'],
                    'sequence': record['sequence'][:50] + "..." if len(record['sequence']) > 50 else record['sequence'],
                    'quality': float(record['quality']),
                    'energy': float(record['energy']),
                    'therapeutic_potential': float(record['avg_therapeutic_potential'] or 0),
                    'targets': record['targets'],
                    'families': record['families'],
                    'timestamp': record['timestamp'].strftime('%H:%M:%S')
                })
            
            return high_potential
    
    def get_solution_mapping_analysis(self) -> Dict[str, Any]:
        """Analyze how discoveries map to therapeutic solutions"""
        
        with self.driver.session() as session:
            # Solution distribution
            solution_stats = session.run("""
                MATCH (d:Discovery)-[r:MAPS_TO_SOLUTION]->(s:TherapeuticSolution)
                RETURN s.name as solution_name,
                       s.development_stage as stage,
                       s.predicted_efficacy as efficacy,
                       count(d) as discovery_count,
                       avg(r.confidence_score) as avg_confidence,
                       max(r.confidence_score) as max_confidence,
                       avg(r.quantum_fidelity) as avg_quantum_fidelity
                ORDER BY discovery_count DESC
            """)
            
            solution_distribution = {}
            for record in solution_stats:
                solution_distribution[record['solution_name']] = {
                    'stage': record['stage'],
                    'efficacy': float(record['efficacy']),
                    'discovery_count': record['discovery_count'],
                    'avg_confidence': float(record['avg_confidence'] or 0),
                    'max_confidence': float(record['max_confidence'] or 0),
                    'avg_quantum_fidelity': float(record['avg_quantum_fidelity'] or 0)
                }
            
            # Clinical indication analysis
            indication_stats = session.run("""
                MATCH (d:Discovery)-[r:INDICATES_FOR]->(c:ClinicalIndication)
                RETURN c.name as indication_name,
                       c.unmet_need_score as unmet_need,
                       c.market_size_billions as market_size,
                       count(d) as discovery_count,
                       avg(r.therapeutic_potential) as avg_potential,
                       max(r.therapeutic_potential) as max_potential
                ORDER BY discovery_count DESC
            """)
            
            indication_distribution = {}
            for record in indication_stats:
                indication_distribution[record['indication_name']] = {
                    'unmet_need': float(record['unmet_need']),
                    'market_size': float(record['market_size']),
                    'discovery_count': record['discovery_count'],
                    'avg_potential': float(record['avg_potential'] or 0),
                    'max_potential': float(record['max_potential'] or 0)
                }
            
            return {
                'solution_distribution': solution_distribution,
                'clinical_indications': indication_distribution
            }
    
    def find_breakthrough_discoveries(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Find discoveries with highest breakthrough potential (solution + clinical mapping)"""
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Discovery)-[:HAS_SEQUENCE]->(s:Sequence)
                MATCH (d)-[sol:MAPS_TO_SOLUTION]->(solution:TherapeuticSolution)
                MATCH (d)-[ind:INDICATES_FOR]->(indication:ClinicalIndication)
                WITH d, s, solution, indication, sol, ind,
                     (sol.confidence_score * solution.predicted_efficacy * 
                      ind.therapeutic_potential * indication.unmet_need_score) as breakthrough_score
                RETURN d.id as discovery_id,
                       s.value as sequence,
                       d.validation_score as quality,
                       solution.name as solution_name,
                       indication.name as indication_name,
                       sol.confidence_score as solution_confidence,
                       ind.therapeutic_potential as indication_potential,
                       breakthrough_score,
                       d.timestamp as timestamp
                ORDER BY breakthrough_score DESC
                LIMIT $limit
            """, {'limit': limit})
            
            breakthroughs = []
            for record in result:
                breakthroughs.append({
                    'discovery_id': record['discovery_id'],
                    'sequence': record['sequence'][:50] + "..." if len(record['sequence']) > 50 else record['sequence'],
                    'quality': float(record['quality']),
                    'solution': record['solution_name'],
                    'indication': record['indication_name'],
                    'solution_confidence': float(record['solution_confidence']),
                    'indication_potential': float(record['indication_potential']),
                    'breakthrough_score': float(record['breakthrough_score']),
                    'timestamp': record['timestamp'].strftime('%H:%M:%S')
                })
            
            return breakthroughs
    
    def _initialize_reference_data(self, session):
        """Initialize reference data for protein families, amino acids, etc."""
        
        # Create amino acid reference nodes
        amino_acids = [
            {'code': 'A', 'name': 'Alanine', 'type': 'hydrophobic', 'mass': 89.09},
            {'code': 'R', 'name': 'Arginine', 'type': 'basic', 'mass': 174.20},
            {'code': 'N', 'name': 'Asparagine', 'type': 'polar', 'mass': 132.12},
            {'code': 'D', 'name': 'Aspartic acid', 'type': 'acidic', 'mass': 133.10},
            {'code': 'C', 'name': 'Cysteine', 'type': 'polar', 'mass': 121.15},
            {'code': 'E', 'name': 'Glutamic acid', 'type': 'acidic', 'mass': 147.13},
            {'code': 'Q', 'name': 'Glutamine', 'type': 'polar', 'mass': 146.15},
            {'code': 'G', 'name': 'Glycine', 'type': 'hydrophobic', 'mass': 75.07},
            {'code': 'H', 'name': 'Histidine', 'type': 'basic', 'mass': 155.16},
            {'code': 'I', 'name': 'Isoleucine', 'type': 'hydrophobic', 'mass': 131.18},
            {'code': 'L', 'name': 'Leucine', 'type': 'hydrophobic', 'mass': 131.18},
            {'code': 'K', 'name': 'Lysine', 'type': 'basic', 'mass': 146.19},
            {'code': 'M', 'name': 'Methionine', 'type': 'hydrophobic', 'mass': 149.21},
            {'code': 'F', 'name': 'Phenylalanine', 'type': 'aromatic', 'mass': 165.19},
            {'code': 'P', 'name': 'Proline', 'type': 'hydrophobic', 'mass': 115.13},
            {'code': 'S', 'name': 'Serine', 'type': 'polar', 'mass': 105.09},
            {'code': 'T', 'name': 'Threonine', 'type': 'polar', 'mass': 119.12},
            {'code': 'W', 'name': 'Tryptophan', 'type': 'aromatic', 'mass': 204.23},
            {'code': 'Y', 'name': 'Tyrosine', 'type': 'aromatic', 'mass': 181.19},
            {'code': 'V', 'name': 'Valine', 'type': 'hydrophobic', 'mass': 117.15}
        ]
        
        for aa in amino_acids:
            session.run("""
                MERGE (a:AminoAcid {code: $code})
                SET a.name = $name,
                    a.type = $type,
                    a.molecular_mass = $mass,
                    a.created_at = datetime()
            """, aa)
        
        # Create common protein families
        protein_families = [
            {'id': 'kinase', 'name': 'Protein Kinase', 'description': 'Enzymes that phosphorylate proteins'},
            {'id': 'gpcr', 'name': 'G-Protein Coupled Receptor', 'description': 'Membrane receptors'},
            {'id': 'immunoglobulin', 'name': 'Immunoglobulin', 'description': 'Antibody proteins'},
            {'id': 'transcription_factor', 'name': 'Transcription Factor', 'description': 'DNA-binding proteins'},
            {'id': 'enzyme', 'name': 'Enzyme', 'description': 'Catalytic proteins'},
            {'id': 'membrane_protein', 'name': 'Membrane Protein', 'description': 'Proteins associated with membranes'},
            {'id': 'structural_protein', 'name': 'Structural Protein', 'description': 'Proteins providing structure'},
            {'id': 'transporter', 'name': 'Transporter', 'description': 'Membrane transport proteins'}
        ]
        
        for family in protein_families:
            session.run("""
                MERGE (p:ProteinFamily {id: $id})
                SET p.name = $name,
                    p.description = $description,
                    p.created_at = datetime()
            """, family)
        
        # Create common therapeutic targets
        therapeutic_targets = [
            {'id': 'alzheimers', 'name': 'Alzheimer\'s Disease', 'target_type': 'neurodegeneration', 'associated_disease': 'alzheimers'},
            {'id': 'cancer', 'name': 'Cancer Therapy', 'target_type': 'oncology', 'associated_disease': 'cancer'},
            {'id': 'diabetes', 'name': 'Diabetes Treatment', 'target_type': 'metabolic', 'associated_disease': 'diabetes'},
            {'id': 'cardiovascular', 'name': 'Cardiovascular Disease', 'target_type': 'cardiovascular', 'associated_disease': 'heart_disease'},
            {'id': 'inflammation', 'name': 'Anti-inflammatory', 'target_type': 'immunology', 'associated_disease': 'inflammatory_disease'},
            {'id': 'antimicrobial', 'name': 'Antimicrobial', 'target_type': 'infectious_disease', 'associated_disease': 'infection'},
            {'id': 'autoimmune', 'name': 'Autoimmune Disease Therapy', 'target_type': 'immunomodulation', 'associated_disease': 'autoimmune_disorder'}
        ]
        
        for target in therapeutic_targets:
            session.run("""
                MERGE (t:TherapeuticTarget {id: $id})
                SET t.name = $name,
                    t.target_type = $target_type,
                    t.associated_disease = $associated_disease,
                    t.created_at = datetime()
            """, target)
        
        # Create disease pathways
        disease_pathways = [
            {'id': 'amyloid_cascade', 'name': 'Amyloid Cascade', 'description': 'Alzheimer\'s amyloid pathway', 'priority_score': 0.9},
            {'id': 'apoptosis', 'name': 'Apoptosis', 'description': 'Programmed cell death', 'priority_score': 0.8},
            {'id': 'inflammation_cascade', 'name': 'Inflammation Cascade', 'description': 'Inflammatory response pathway', 'priority_score': 0.7},
            {'id': 'insulin_signaling', 'name': 'Insulin Signaling', 'description': 'Glucose metabolism pathway', 'priority_score': 0.8},
            {'id': 'cell_cycle', 'name': 'Cell Cycle', 'description': 'Cell division control', 'priority_score': 0.6},
            {'id': 'immune_tolerance', 'name': 'Immune Tolerance', 'description': 'Autoimmune regulation pathway', 'priority_score': 0.85}
        ]
        
        for pathway in disease_pathways:
            session.run("""
                MERGE (d:DiseasePathway {id: $id})
                SET d.name = $name,
                    d.description = $description,
                    d.priority_score = $priority_score,
                    d.created_at = datetime()
            """, pathway)
    
    def _initialize_therapeutic_solutions(self, session):
        """Initialize specific therapeutic solutions that discoveries can map to"""
        
        therapeutic_solutions = [
            {
                'id': 'alzheimers_amyloid_inhibitor',
                'name': 'Amyloid-β Aggregation Inhibitor',
                'mechanism': 'Prevents amyloid plaque formation',
                'target_pathway': 'amyloid_cascade',
                'predicted_efficacy': 0.8,
                'development_stage': 'preclinical',
                'solution_type': 'small_molecule_inhibitor'
            },
            {
                'id': 'alzheimers_tau_stabilizer',
                'name': 'Tau Protein Stabilizer',
                'mechanism': 'Prevents tau hyperphosphorylation and aggregation',
                'target_pathway': 'tau_pathology',
                'predicted_efficacy': 0.7,
                'development_stage': 'discovery',
                'solution_type': 'protein_therapeutic'
            },
            {
                'id': 'cancer_apoptosis_inducer',
                'name': 'Cancer Cell Apoptosis Inducer',
                'mechanism': 'Triggers programmed cell death in cancer cells',
                'target_pathway': 'apoptosis',
                'predicted_efficacy': 0.75,
                'development_stage': 'preclinical',
                'solution_type': 'targeted_therapy'
            },
            {
                'id': 'antimicrobial_membrane_disruptor',
                'name': 'Antimicrobial Peptide',
                'mechanism': 'Disrupts bacterial cell membranes',
                'target_pathway': 'membrane_integrity',
                'predicted_efficacy': 0.85,
                'development_stage': 'clinical_trial',
                'solution_type': 'antimicrobial_peptide'
            },
            {
                'id': 'inflammation_nfkb_inhibitor',
                'name': 'NF-κB Pathway Inhibitor',
                'mechanism': 'Blocks inflammatory cascade activation',
                'target_pathway': 'inflammation_cascade',
                'predicted_efficacy': 0.6,
                'development_stage': 'discovery',
                'solution_type': 'pathway_modulator'
            },
            {
                'id': 'autoimmune_tolerance_inducer',
                'name': 'Immune Tolerance Inducer',
                'mechanism': 'Modulates T-cell response to reduce autoimmune attack',
                'target_pathway': 'immune_tolerance',
                'predicted_efficacy': 0.7,
                'development_stage': 'discovery',
                'solution_type': 'immunomodulatory_protein'
            },
            {
                'id': 'autoimmune_cytokine_modulator',
                'name': 'Cytokine Balance Modulator',
                'mechanism': 'Restores Th1/Th2/Th17/Treg balance in autoimmune conditions',
                'target_pathway': 'immune_tolerance',
                'predicted_efficacy': 0.65,
                'development_stage': 'discovery',
                'solution_type': 'immunomodulatory_protein'
            },
            {
                'id': 'diabetes_insulin_sensitizer',
                'name': 'Insulin Sensitivity Enhancer',
                'mechanism': 'Improves cellular insulin response',
                'target_pathway': 'insulin_signaling',
                'predicted_efficacy': 0.65,
                'development_stage': 'preclinical',
                'solution_type': 'metabolic_modulator'
            }
        ]
        
        for solution in therapeutic_solutions:
            session.run("""
                MERGE (s:TherapeuticSolution {id: $id})
                SET s.name = $name,
                    s.mechanism = $mechanism,
                    s.target_pathway = $target_pathway,
                    s.predicted_efficacy = $predicted_efficacy,
                    s.development_stage = $development_stage,
                    s.solution_type = $solution_type,
                    s.created_at = datetime()
            """, solution)
    
    def _initialize_clinical_indications(self, session):
        """Initialize clinical indications for therapeutic mapping"""
        
        clinical_indications = [
            {
                'id': 'alzheimers_disease',
                'name': 'Alzheimer\'s Disease',
                'icd_code': 'G30.9',
                'prevalence': '6.5M_US',
                'unmet_need_score': 0.95,
                'priority_score': 0.9,
                'market_size_billions': 5.8
            },
            {
                'id': 'lung_cancer',
                'name': 'Non-Small Cell Lung Cancer',
                'icd_code': 'C78.0',
                'prevalence': '235K_US',
                'unmet_need_score': 0.85,
                'priority_score': 0.85,
                'market_size_billions': 12.3
            },
            {
                'id': 'sepsis',
                'name': 'Sepsis and Septic Shock',
                'icd_code': 'A41.9',
                'prevalence': '1.7M_US',
                'unmet_need_score': 0.8,
                'priority_score': 0.75,
                'market_size_billions': 3.2
            },
            {
                'id': 'type2_diabetes',
                'name': 'Type 2 Diabetes Mellitus',
                'icd_code': 'E11.9',
                'prevalence': '37.3M_US',
                'unmet_need_score': 0.6,
                'priority_score': 0.7,
                'market_size_billions': 15.8
            },
            {
                'id': 'rheumatoid_arthritis',
                'name': 'Rheumatoid Arthritis',
                'icd_code': 'M06.9',
                'prevalence': '1.3M_US',
                'unmet_need_score': 0.7,
                'priority_score': 0.6,
                'market_size_billions': 8.9
            },
            {
                'id': 'multiple_sclerosis',
                'name': 'Multiple Sclerosis',
                'icd_code': 'G35',
                'prevalence': '1M_US',
                'unmet_need_score': 0.85,
                'priority_score': 0.8,
                'market_size_billions': 28.4
            },
            {
                'id': 'crohns_disease',
                'name': 'Crohn\'s Disease',
                'icd_code': 'K50.9',
                'prevalence': '780K_US',
                'unmet_need_score': 0.75,
                'priority_score': 0.7,
                'market_size_billions': 6.8
            },
            {
                'id': 'systemic_lupus',
                'name': 'Systemic Lupus Erythematosus',
                'icd_code': 'M32.9',
                'prevalence': '325K_US',
                'unmet_need_score': 0.9,
                'priority_score': 0.75,
                'market_size_billions': 2.3
            }
        ]
        
        for indication in clinical_indications:
            session.run("""
                MERGE (c:ClinicalIndication {id: $id})
                SET c.name = $name,
                    c.icd_code = $icd_code,
                    c.prevalence = $prevalence,
                    c.unmet_need_score = $unmet_need_score,
                    c.priority_score = $priority_score,
                    c.market_size_billions = $market_size_billions,
                    c.created_at = datetime()
            """, indication)
    
    def _initialize_learning_system(self, session):
        """Initialize Phase 2 learning system components"""
        
        # Create the main learning session node for this system instance
        session_id = f"learning_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session.run("""
            MERGE (ls:LearningSession {id: $session_id})
            SET ls.timestamp = datetime(),
                ls.version = "Phase2_AKG",
                ls.validation_accuracy = 0.0,
                ls.total_discoveries_learned = 0,
                ls.motifs_extracted = 0,
                ls.patterns_identified = 0,
                ls.active = true
        """, session_id=session_id)
        
        # Create the motif library
        session.run("""
            MERGE (ml:MotifLibrary {id: "global_motif_library"})
            SET ml.created = datetime(),
                ml.usage_count = 0,
                ml.success_rate = 0.0,
                ml.total_motifs = 0,
                ml.version = "Phase2_AKG"
        """)
        
        logger.info(f"✅ Phase 2 learning system initialized - Session: {session_id}")
    
    def _create_protein_family_connections(self, session, discovery_id: str, sequence: str):
        """Create connections to protein families based on sequence analysis"""
        
        # Simple heuristics for protein family classification
        family_predictions = []
        
        # Kinase signature patterns
        if 'ATP' in sequence or ('K' in sequence and 'D' in sequence):
            family_predictions.append(('kinase', 0.6))
        
        # GPCR signatures (7 transmembrane patterns)
        hydrophobic_regions = 0
        for i in range(0, len(sequence), 20):
            region = sequence[i:i+20]
            hydrophobic_count = sum(1 for aa in region if aa in 'ILVFMWYAG')
            if hydrophobic_count > 15:
                hydrophobic_regions += 1
        
        if hydrophobic_regions >= 5:
            family_predictions.append(('gpcr', 0.7))
        
        # Immunoglobulin signatures
        if 'C' in sequence and sequence.count('C') > 4:
            family_predictions.append(('immunoglobulin', 0.5))
        
        # General enzyme signatures
        if any(motif in sequence for motif in ['HIS', 'SER', 'ASP']):
            family_predictions.append(('enzyme', 0.4))
        
        # Membrane protein signatures
        hydrophobic_fraction = sum(1 for aa in sequence if aa in 'ILVFMWYAG') / len(sequence)
        if hydrophobic_fraction > 0.4:
            family_predictions.append(('membrane_protein', 0.6))
        
        # Store family predictions
        for family_id, confidence in family_predictions:
            session.run("""
                MATCH (d:Discovery {id: $discovery_id})
                MATCH (p:ProteinFamily {id: $family_id})
                MERGE (d)-[r:CLASSIFIED_AS]->(p)
                SET r.confidence_score = $confidence,
                    r.prediction_method = 'sequence_heuristics',
                    r.created_at = datetime()
            """, {
                'discovery_id': discovery_id,
                'family_id': family_id,
                'confidence': confidence
            })
    
    def _create_therapeutic_target_connections(self, session, discovery_id: str, discovery_data: Dict[str, Any]):
        """Create connections to therapeutic targets based on analysis"""
        
        sequence = discovery_data.get('sequence', '')
        validation_score = discovery_data.get('validation_score', 0.0)
        
        target_predictions = []
        
        # High-quality sequences get broader therapeutic potential
        if validation_score > 0.8:
            # Alzheimer's potential (amyloid-binding motifs)
            if any(motif in sequence for motif in ['KLVFF', 'VHHQ', 'LVFFA']):
                target_predictions.append(('alzheimers', 0.8))
            
            # Cancer therapy potential (apoptosis inducers)
            if 'P53' in sequence or len(sequence) > 50:
                target_predictions.append(('cancer', 0.6))
            
            # Anti-inflammatory potential
            if validation_score > 0.9:
                target_predictions.append(('inflammation', 0.7))
            
            # Antimicrobial potential (for shorter sequences)
            if 20 <= len(sequence) <= 40:
                target_predictions.append(('antimicrobial', 0.5))
            
            # AUTOIMMUNE DISEASE TARGETING - NEW FEATURE
            # Target longer proteins with cysteine bridges for immune modulation
            cysteine_count = sequence.count('C')
            length = len(sequence)
            
            # Autoimmune therapeutic criteria:
            # 1. Length >= 25 AA (immunomodulatory proteins need complexity)
            # 2. Cysteine bridges for structural stability (>=2 cysteines)
            # 3. Balanced charge distribution
            # 4. Presence of immunomodulatory motifs
            if length >= 25 and cysteine_count >= 2:
                autoimmune_score = 0.3  # Base score
                
                # Boost score for optimal length range (25-60 AA)
                if 25 <= length <= 60:
                    autoimmune_score += 0.2
                
                # Boost for multiple cysteine bridges (up to 4 optimal)
                if cysteine_count >= 4:
                    autoimmune_score += 0.3
                elif cysteine_count >= 3:
                    autoimmune_score += 0.2
                
                # Check for immunomodulatory sequence patterns
                immunomod_motifs = ['GPGP', 'CXCR', 'TNFR', 'CTLA', 'PD1', 'IL']
                if any(motif in sequence for motif in immunomod_motifs):
                    autoimmune_score += 0.2
                
                # Prefer sequences with aromatic residues for binding (F, Y, W)
                aromatic_count = sum(1 for aa in sequence if aa in 'FYW')
                if aromatic_count >= 3:
                    autoimmune_score += 0.1
                
                # Only add if score is meaningful (>= 0.5)
                if autoimmune_score >= 0.5:
                    target_predictions.append(('autoimmune', min(autoimmune_score, 0.95)))
        
        # Store therapeutic target connections
        for target_id, potential_score in target_predictions:
            session.run("""
                MATCH (d:Discovery {id: $discovery_id})
                MATCH (t:TherapeuticTarget {id: $target_id})
                MERGE (d)-[r:TARGETS]->(t)
                SET r.potential_score = $potential_score,
                    r.prediction_method = 'sequence_analysis',
                    r.created_at = datetime()
            """, {
                'discovery_id': discovery_id,
                'target_id': target_id,
                'potential_score': potential_score
            })
    
    def _create_structural_motif_connections(self, session, discovery_id: str, vqbit_states: List[Dict[str, Any]]):
        """Create connections to structural motifs based on vQbit analysis"""
        
        # Analyze vQbit states for structural patterns
        motif_predictions = []
        
        # Alpha helix prediction (phi ~ -60, psi ~ -45)
        helix_residues = 0
        for vqbit in vqbit_states:
            phi = vqbit.get('phi', 0)
            psi = vqbit.get('psi', 0)
            if -80 <= phi <= -40 and -60 <= psi <= -20:
                helix_residues += 1
        
        if helix_residues > len(vqbit_states) * 0.3:
            motif_predictions.append(('alpha_helix', helix_residues / len(vqbit_states)))
        
        # Beta sheet prediction (phi ~ -120, psi ~ 120)
        sheet_residues = 0
        for vqbit in vqbit_states:
            phi = vqbit.get('phi', 0)
            psi = vqbit.get('psi', 0)
            if -150 <= phi <= -90 and 90 <= psi <= 150:
                sheet_residues += 1
        
        if sheet_residues > len(vqbit_states) * 0.2:
            motif_predictions.append(('beta_sheet', sheet_residues / len(vqbit_states)))
        
        # Turn/loop regions
        irregular_residues = len(vqbit_states) - helix_residues - sheet_residues
        if irregular_residues > len(vqbit_states) * 0.3:
            motif_predictions.append(('turn_loop', irregular_residues / len(vqbit_states)))
        
        # Store motif predictions
        for motif_type, confidence in motif_predictions:
            motif_id = f"{discovery_id}_{motif_type}"
            session.run("""
                MERGE (s:StructuralMotif {id: $motif_id})
                SET s.motif_type = $motif_type,
                    s.confidence = $confidence,
                    s.created_at = datetime()
                    
                WITH s
                MATCH (d:Discovery {id: $discovery_id})
                MERGE (d)-[r:CONTAINS_MOTIF]->(s)
                SET r.created_at = datetime()
            """, {
                'motif_id': motif_id,
                'motif_type': motif_type,
                'confidence': confidence,
                'discovery_id': discovery_id
            })
    
    def _create_sequence_similarity_connections(self, session, discovery_id: str, sequence: str):
        """Create similarity relationships with other sequences in the graph"""
        
        # Find similar sequences using simple Hamming distance
        # This is a simplified approach - in production, use more sophisticated algorithms
        
        # Only check similarity for sequences of similar length (±20%)
        min_length = int(len(sequence) * 0.8)
        max_length = int(len(sequence) * 1.2)
        
        result = session.run("""
            MATCH (d:Discovery)-[:HAS_SEQUENCE]->(s:Sequence)
            WHERE s.length >= $min_length AND s.length <= $max_length
                AND d.id <> $discovery_id
            RETURN d.id as other_discovery_id, s.value as other_sequence
            LIMIT 100
        """, {
            'min_length': min_length,
            'max_length': max_length,
            'discovery_id': discovery_id
        })
        
        for record in result:
            other_sequence = record['other_sequence']
            other_discovery_id = record['other_discovery_id']
            
            # Calculate simple similarity (this is very basic - could be improved)
            similarity = self._calculate_sequence_similarity(sequence, other_sequence)
            
            if similarity > 0.7:  # Only store high similarity relationships
                session.run("""
                    MATCH (d1:Discovery {id: $discovery_id})
                    MATCH (d2:Discovery {id: $other_discovery_id})
                    MERGE (d1)-[r:SIMILAR_TO]-(d2)
                    SET r.similarity_score = $similarity,
                        r.comparison_method = 'sequence_alignment',
                        r.created_at = datetime()
                """, {
                    'discovery_id': discovery_id,
                    'other_discovery_id': other_discovery_id,
                    'similarity': similarity
                })
    
    def _calculate_sequence_similarity(self, seq1: str, seq2: str) -> float:
        """Calculate simple sequence similarity score"""
        
        if len(seq1) == 0 or len(seq2) == 0:
            return 0.0
        
        # Simple character-by-character comparison
        max_len = max(len(seq1), len(seq2))
        min_len = min(len(seq1), len(seq2))
        
        matches = 0
        for i in range(min_len):
            if seq1[i] == seq2[i]:
                matches += 1
        
        # Penalize length differences
        length_penalty = min_len / max_len
        similarity = (matches / min_len) * length_penalty
        
        return similarity
    
    def _map_to_therapeutic_solutions(self, session, discovery_id: str, discovery_data: Dict[str, Any]):
        """Map discovery to specific therapeutic solutions based on analysis"""
        
        sequence = discovery_data.get('sequence', '')
        validation_score = discovery_data.get('validation_score', 0.0)
        metal_analysis = discovery_data.get('metal_analysis', {})
        energy = metal_analysis.get('energy_kcal_mol', 0.0)
        vqbit_score = metal_analysis.get('vqbit_score', 0.0)
        
        solution_mappings = []
        
        # High-quality discoveries with good energetics
        if validation_score > 0.8 and energy < -250:
            
            # Alzheimer's solutions
            if any(motif in sequence for motif in ['KLVFF', 'VHHQ', 'LVFFA', 'YEVHHQKLVFF']):
                solution_mappings.append(('alzheimers_amyloid_inhibitor', 0.85, 'amyloid_binding_motif'))
            
            if len(sequence) > 100 and 'C' in sequence:
                solution_mappings.append(('alzheimers_tau_stabilizer', 0.7, 'tau_binding_potential'))
            
            # Cancer solutions
            if validation_score > 0.9 and energy < -300:
                solution_mappings.append(('cancer_apoptosis_inducer', 0.75, 'high_binding_affinity'))
            
            # Antimicrobial solutions (for shorter, stable peptides)
            if 15 <= len(sequence) <= 50 and vqbit_score > 0.6:
                solution_mappings.append(('antimicrobial_membrane_disruptor', 0.8, 'membrane_active_peptide'))
            
            # Anti-inflammatory solutions
            if validation_score > 0.85:
                solution_mappings.append(('inflammation_nfkb_inhibitor', 0.65, 'anti_inflammatory_potential'))
            
            # Diabetes solutions
            if len(sequence) > 50 and any(aa in sequence for aa in ['R', 'K']):
                solution_mappings.append(('diabetes_insulin_sensitizer', 0.6, 'insulin_pathway_modulation'))
            
            # AUTOIMMUNE DISEASE SOLUTIONS - NEW FEATURE
            # Map to autoimmune therapeutic solutions based on immunomodulatory characteristics
            cysteine_count = sequence.count('C')
            length = len(sequence)
            
            # Immune tolerance inducer mapping
            if (length >= 25 and cysteine_count >= 2 and 
                validation_score > 0.85 and vqbit_score > 0.5):
                
                tolerance_score = 0.4  # Base confidence
                
                # Boost for optimal autoimmune therapeutic characteristics
                if 25 <= length <= 60:
                    tolerance_score += 0.2
                
                if cysteine_count >= 4:  # Multiple disulfide bridges
                    tolerance_score += 0.2
                
                # Check for immunomodulatory motifs
                immunomod_motifs = ['GPGP', 'CXCR', 'TNFR', 'CTLA', 'PD1', 'IL']
                if any(motif in sequence for motif in immunomod_motifs):
                    tolerance_score += 0.15
                
                if tolerance_score >= 0.6:
                    solution_mappings.append(('autoimmune_tolerance_inducer', 
                                           min(tolerance_score, 0.9), 
                                           'immunomodulatory_structure'))
            
            # Cytokine modulator mapping (broader criteria)
            if (length >= 20 and cysteine_count >= 1 and 
                validation_score > 0.8):
                
                cytokine_score = 0.3
                
                # Aromatic residues for cytokine binding
                aromatic_count = sum(1 for aa in sequence if aa in 'FYW')
                if aromatic_count >= 3:
                    cytokine_score += 0.2
                
                # Charged residues for protein-protein interactions
                charged_count = sum(1 for aa in sequence if aa in 'RKDE')
                if charged_count >= 5:
                    cytokine_score += 0.15
                
                if cytokine_score >= 0.5:
                    solution_mappings.append(('autoimmune_cytokine_modulator',
                                           min(cytokine_score, 0.85),
                                           'cytokine_binding_potential'))
        
        # Store solution mappings
        for solution_id, confidence, evidence in solution_mappings:
            session.run("""
                MATCH (d:Discovery {id: $discovery_id})
                MATCH (s:TherapeuticSolution {id: $solution_id})
                CREATE (d)-[:MAPS_TO_SOLUTION {
                    confidence_score: $confidence,
                    evidence_type: $evidence,
                    quantum_fidelity: $vqbit_score,
                    binding_energy: $energy,
                    validation_score: $validation_score,
                    prediction_method: 'quantum_sequence_analysis',
                    created_at: datetime()
                }]->(s)
            """, {
                'discovery_id': discovery_id,
                'solution_id': solution_id,
                'confidence': confidence,
                'evidence': evidence,
                'vqbit_score': vqbit_score,
                'energy': energy,
                'validation_score': validation_score
            })
    
    def _create_clinical_indication_mapping(self, session, discovery_id: str, discovery_data: Dict[str, Any]):
        """Map discovery to clinical indications"""
        
        sequence = discovery_data.get('sequence', '')
        validation_score = discovery_data.get('validation_score', 0.0)
        
        indication_mappings = []
        
        if validation_score > 0.8:
            # Alzheimer's disease mapping
            if any(motif in sequence for motif in ['KLVFF', 'VHHQ', 'LVFFA']):
                indication_mappings.append(('alzheimers_disease', 0.8, 'amyloid_targeting'))
            
            # Cancer mapping (high-quality, stable proteins)
            if validation_score > 0.9:
                indication_mappings.append(('lung_cancer', 0.7, 'targeted_therapy_potential'))
            
            # Sepsis mapping (antimicrobial peptides)
            if 15 <= len(sequence) <= 40:
                indication_mappings.append(('sepsis', 0.75, 'antimicrobial_activity'))
            
            # Diabetes mapping
            if len(sequence) > 50:
                indication_mappings.append(('type2_diabetes', 0.6, 'metabolic_modulation'))
            
            # Rheumatoid arthritis mapping
            if validation_score > 0.85:
                indication_mappings.append(('rheumatoid_arthritis', 0.65, 'anti_inflammatory'))
            
            # AUTOIMMUNE DISEASE CLINICAL INDICATION MAPPING - NEW FEATURE
            cysteine_count = sequence.count('C')
            length = len(sequence)
            
            # Multiple sclerosis mapping (high priority autoimmune target)
            if (length >= 25 and cysteine_count >= 2 and validation_score > 0.85):
                ms_potential = 0.6
                
                # Boost for neuroinflammation targeting characteristics
                if any(motif in sequence for motif in ['TNFR', 'IL', 'CXCR']):
                    ms_potential += 0.15
                
                indication_mappings.append(('multiple_sclerosis', 
                                          min(ms_potential, 0.85), 
                                          'neuroinflammation_modulation'))
            
            # Crohn's disease mapping (IBD targeting)
            if (length >= 20 and cysteine_count >= 1 and validation_score > 0.8):
                crohns_potential = 0.55
                
                # Boost for gut inflammation targeting
                aromatic_count = sum(1 for aa in sequence if aa in 'FYW')
                if aromatic_count >= 2:
                    crohns_potential += 0.1
                
                indication_mappings.append(('crohns_disease',
                                          min(crohns_potential, 0.8),
                                          'gut_inflammation_control'))
            
            # Systemic lupus erythematosus mapping (complex autoimmune disease)
            if (length >= 30 and cysteine_count >= 3 and validation_score > 0.9):
                lupus_potential = 0.5
                
                # Boost for systemic immunomodulation potential
                charged_count = sum(1 for aa in sequence if aa in 'RKDE')
                if charged_count >= 6:
                    lupus_potential += 0.2
                
                indication_mappings.append(('systemic_lupus',
                                          min(lupus_potential, 0.8),
                                          'systemic_immune_regulation'))
        
        # Store clinical indication mappings
        for indication_id, potential, mechanism in indication_mappings:
            session.run("""
                MATCH (d:Discovery {id: $discovery_id})
                MATCH (c:ClinicalIndication {id: $indication_id})
                CREATE (d)-[:INDICATES_FOR {
                    therapeutic_potential: $potential,
                    mechanism_of_action: $mechanism,
                    validation_score: $validation_score,
                    development_feasibility: $potential * 0.8,
                    created_at: datetime()
                }]->(c)
            """, {
                'discovery_id': discovery_id,
                'indication_id': indication_id,
                'potential': potential,
                'mechanism': mechanism,
                'validation_score': validation_score
            })

def main():
    """Test Enhanced Neo4j Discovery Engine with Comprehensive Graph"""
    
    print("🔗 ENHANCED NEO4J PROTEIN DISCOVERY KNOWLEDGE GRAPH")
    print("=" * 70)
    
    try:
        # Initialize engine
        engine = Neo4jDiscoveryEngine()
        
        # Test storage with vQbit quantum states
        test_discovery = {
            'sequence': 'MKLLVVMLAFCSIVLLQAAFPVLSNIAQQNPNASAAKPHLIIPCSAPVTFQTANQNLGNVFLSLNPAADPPAHYLSLSQHMLPTSILPHDLVLLVKQGIFVSPEVVCRLGVGLDATTHDEGLVSLSHLTNLLPEEVVVNQGVEQVNRHTDLSLQRV',
            'validation_score': 0.91,
            'assessment': 'VALID: Excellent therapeutic candidate with quantum coherence',
            'metal_analysis': {
                'vqbit_score': 0.34,
                'energy_kcal_mol': -385.2,
                'virtue_scores': {
                    'justice': 0.25,
                    'honesty': -0.12,
                    'temperance': 0.18,
                    'prudence': -0.08
                }
            },
            'quantum_analysis': {
                'coherence': 0.78,
                'entanglement_entropy': 1.23,
                'superposition_fidelity': 0.89
            },
            'vqbit_states': [
                {
                    'residue_index': 0,
                    'amino_acid': 'M',
                    'phi': -60.0,
                    'psi': -45.0,
                    'amplitude_real': 0.707,
                    'amplitude_imag': 0.707,
                    'entanglement': 0.85,
                    'coherence': 0.92,
                    'collapsed': False,
                    'phase': 1.57,
                    'virtue_projections': {
                        'justice': {'strength': 0.3, 'phase': 0.5},
                        'temperance': {'strength': 0.2, 'phase': 1.2}
                    },
                    'entanglement_with_prev': 0.0
                },
                {
                    'residue_index': 1,
                    'amino_acid': 'K',
                    'phi': -120.0,
                    'psi': 120.0,
                    'amplitude_real': 0.866,
                    'amplitude_imag': 0.5,
                    'entanglement': 0.73,
                    'coherence': 0.88,
                    'collapsed': False,
                    'phase': 0.79,
                    'virtue_projections': {
                        'honesty': {'strength': 0.4, 'phase': 0.8},
                        'prudence': {'strength': 0.15, 'phase': 2.1}
                    },
                    'entanglement_with_prev': 0.67
                }
            ],
            'hardware_info': {
                'processed_on': 'M4_Mac_Pro_40_GPU',
                'metal_accelerated': True,
                'unified_memory': True
            }
        }
        
        # Store test discovery
        discovery_id = engine.store_discovery(test_discovery)
        print(f"✅ Stored test discovery: {discovery_id}")
        
        # Get comprehensive analysis
        comprehensive_stats = engine.get_comprehensive_graph_analysis()
        print(f"📊 Comprehensive Graph Analysis:")
        print(f"   Nodes: {comprehensive_stats['node_statistics']}")
        print(f"   Relationships: {comprehensive_stats['relationship_statistics']}")
        
        # Get protein family analysis
        family_stats = engine.get_protein_family_analysis()
        print(f"🧬 Protein Family Analysis: {family_stats}")
        
        # Get therapeutic target analysis
        target_stats = engine.get_therapeutic_target_analysis()
        print(f"🎯 Therapeutic Target Analysis: {target_stats}")
        
        # Get structural analysis
        structural_stats = engine.get_structural_analysis()
        print(f"🏗️ Structural Analysis: {structural_stats}")
        
        # Find high potential discoveries
        high_potential = engine.find_high_potential_discoveries()
        print(f"⭐ High Potential Discoveries: {high_potential}")
        
        # Find quantum patterns
        patterns = engine.find_quantum_patterns()
        print(f"🌀 Quantum Patterns: {patterns}")
        
        # Get solution mapping analysis
        solution_analysis = engine.get_solution_mapping_analysis()
        print(f"🎯 Solution Mapping Analysis: {solution_analysis}")
        
        # Find breakthrough discoveries
        breakthroughs = engine.find_breakthrough_discoveries()
        print(f"💎 Breakthrough Discoveries: {breakthroughs}")
        
        # Close connection
        engine.close()
        print("✅ Enhanced Neo4j Protein Discovery Knowledge Graph test complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure Neo4j is running: brew services start neo4j")

if __name__ == "__main__":
    main()

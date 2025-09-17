"""
Phase 2: Agentic Knowledge Graph (AKG) Learning System
Part of the FoT AlphaFold Independence Roadmap

This module implements the learning capabilities for the AKG system,
allowing it to extract patterns and improve from discoveries.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)

class AKGLearningSystem:
    """
    Phase 2: Agentic Knowledge Graph Learning System
    
    This system learns from validated discoveries and stores structural motifs
    and entanglement patterns to improve future predictions.
    """
    
    def __init__(self, neo4j_engine):
        """Initialize the learning system with a Neo4j engine"""
        self.neo4j_engine = neo4j_engine
        self.driver = neo4j_engine.driver
        
    def learn_from_discovery(self, discovery_id: str) -> Dict[str, Any]:
        """
        Phase 2.1: Learn from a validated discovery and update the AKG
        
        This method extracts structural motifs and entanglement patterns from 
        successful discoveries and stores them in the learning system.
        """
        
        try:
            with self.driver.session() as session:
                # Get the discovery and its validated data
                discovery_query = """
                MATCH (d:Discovery {id: $discovery_id})
                MATCH (d)-[:HAS_SEQUENCE]->(s:Sequence)
                MATCH (d)-[:HAS_VQBIT]->(v:VQbit)
                WITH d, s, collect(v) as vqbits
                RETURN d, s, vqbits
                """
                
                result = session.run(discovery_query, discovery_id=discovery_id)
                record = result.single()
                
                if not record:
                    return {'success': False, 'error': 'Discovery not found'}
                
                discovery = record['d']
                sequence = record['s']
                vqbits = record['vqbits']
                
                # Extract structural motifs from the sequence and vQbits
                motifs_extracted = self._extract_structural_motifs(session, discovery, sequence, vqbits)
                
                # Identify entanglement patterns
                patterns_identified = self._identify_entanglement_patterns(session, discovery, vqbits)
                
                # Update learning session statistics
                self._update_learning_statistics(session, motifs_extracted, patterns_identified)
                
                logger.info(f"✅ Learned from discovery {discovery_id}: {motifs_extracted} motifs, {patterns_identified} patterns")
                
                return {
                    'success': True,
                    'discovery_id': discovery_id,
                    'motifs_extracted': motifs_extracted,
                    'patterns_identified': patterns_identified,
                    'learning_session_updated': True
                }
                
        except Exception as e:
            logger.error(f"Error learning from discovery {discovery_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_structural_motifs(self, session, discovery, sequence, vqbits) -> int:
        """Extract and store structural motifs from a discovery"""
        
        motifs_count = 0
        sequence_value = sequence['value']
        validation_score = discovery.get('validation_score', 0.0)
        
        # Extract common motifs based on sequence patterns
        motifs_found = []
        
        # Beta hairpin patterns (commonly XXXGXXXX)
        for i in range(len(sequence_value) - 7):
            fragment = sequence_value[i:i+8]
            if 'G' in fragment[3:5]:  # Glycine in turn region
                motifs_found.append({
                    'type': 'beta_hairpin',
                    'fragment': fragment,
                    'start': i,
                    'end': i+7,
                    'confidence': 0.7
                })
        
        # Alpha helix patterns (commonly EXXXAXXXE or similar charged residues)
        for i in range(len(sequence_value) - 8):
            fragment = sequence_value[i:i+9]
            charged_count = sum(1 for aa in fragment if aa in 'EDRK')
            if charged_count >= 3:
                motifs_found.append({
                    'type': 'alpha_helix',
                    'fragment': fragment,
                    'start': i,
                    'end': i+8,
                    'confidence': 0.6
                })
        
        # Cysteine bridge patterns
        cys_positions = [i for i, aa in enumerate(sequence_value) if aa == 'C']
        for i in range(len(cys_positions) - 1):
            start_pos = cys_positions[i]
            end_pos = cys_positions[i + 1]
            if end_pos - start_pos >= 3:  # Minimum distance for bridge
                fragment = sequence_value[start_pos:end_pos+1]
                motifs_found.append({
                    'type': 'cysteine_bridge',
                    'fragment': fragment,
                    'start': start_pos,
                    'end': end_pos,
                    'confidence': 0.8
                })
        
        # Binding site patterns (hydrophobic clusters)
        for i in range(len(sequence_value) - 5):
            fragment = sequence_value[i:i+6]
            hydrophobic_count = sum(1 for aa in fragment if aa in 'FILVWYAM')
            if hydrophobic_count >= 4:
                motifs_found.append({
                    'type': 'binding_site',
                    'fragment': fragment,
                    'start': i,
                    'end': i+5,
                    'confidence': 0.65
                })
        
        # Store each motif
        for motif in motifs_found:
            motif_id = f"{motif['type']}_{motif['start']}_{motif['end']}_{sequence['hash'][:8]}"
            
            session.run("""
                MERGE (m:StructuralMotif {id: $motif_id})
                SET m.motif_type = $motif_type,
                    m.sequence_fragment = $fragment,
                    m.start_position = $start,
                    m.end_position = $end,
                    m.confidence = $confidence,
                    m.validation_score = $validation_score,
                    m.discovered_from = $discovery_id,
                    m.timestamp = datetime(),
                    m.length = $length
                
                MERGE (ml:MotifLibrary {id: "global_motif_library"})
                MERGE (ml)-[:CONTAINS_MOTIF]->(m)
                
                MERGE (d:Discovery {id: $discovery_id})
                MERGE (d)-[:DISCOVERED_MOTIF]->(m)
            """, 
            motif_id=motif_id,
            motif_type=motif['type'],
            fragment=motif['fragment'],
            start=motif['start'],
            end=motif['end'],
            confidence=motif['confidence'],
            validation_score=validation_score,
            discovery_id=discovery['id'],
            length=len(motif['fragment'])
            )
            
            motifs_count += 1
        
        return motifs_count
    
    def _identify_entanglement_patterns(self, session, discovery, vqbits) -> int:
        """Identify and store quantum entanglement patterns"""
        
        patterns_count = 0
        discovery_id = discovery['id']
        
        # Find highly entangled vQbit pairs
        entangled_pairs = []
        for i, vqbit1 in enumerate(vqbits):
            for j, vqbit2 in enumerate(vqbits[i+1:], i+1):
                entanglement1 = vqbit1.get('entanglement_degree', 0.0)
                entanglement2 = vqbit2.get('entanglement_degree', 0.0)
                entanglement_strength = entanglement1 * entanglement2
                
                if entanglement_strength > 0.7:  # High entanglement threshold
                    entangled_pairs.append({
                        'vqbit1_id': vqbit1['id'],
                        'vqbit2_id': vqbit2['id'],
                        'strength': entanglement_strength,
                        'distance': abs(vqbit1['residue_index'] - vqbit2['residue_index'])
                    })
        
        # Create entanglement pattern if significant
        if len(entangled_pairs) >= 3:  # Minimum pattern size
            pattern_id = f"entanglement_pattern_{discovery_id}_{len(entangled_pairs)}"
            
            avg_strength = sum(pair['strength'] for pair in entangled_pairs) / len(entangled_pairs)
            residue_count = len(set([pair['vqbit1_id'] for pair in entangled_pairs] + [pair['vqbit2_id'] for pair in entangled_pairs]))
            
            session.run("""
                MERGE (ep:EntanglementPattern {id: $pattern_id})
                SET ep.pattern_type = "quantum_entanglement_network",
                    ep.average_strength = $avg_strength,
                    ep.residue_count = $residue_count,
                    ep.pair_count = $pair_count,
                    ep.discovered_from = $discovery_id,
                    ep.timestamp = datetime(),
                    ep.validation_score = $validation_score
                
                MERGE (d:Discovery {id: $discovery_id})
                MERGE (d)-[:EXHIBITS_PATTERN]->(ep)
            """,
            pattern_id=pattern_id,
            avg_strength=avg_strength,
            residue_count=residue_count,
            pair_count=len(entangled_pairs),
            discovery_id=discovery_id,
            validation_score=discovery.get('validation_score', 0.0)
            )
            
            patterns_count += 1
        
        return patterns_count
    
    def _update_learning_statistics(self, session, motifs_extracted: int, patterns_identified: int):
        """Update learning session statistics"""
        
        session.run("""
            MATCH (ls:LearningSession {active: true})
            SET ls.total_discoveries_learned = ls.total_discoveries_learned + 1,
                ls.motifs_extracted = ls.motifs_extracted + $motifs,
                ls.patterns_identified = ls.patterns_identified + $patterns,
                ls.last_updated = datetime()
                
            WITH ls
            MATCH (ml:MotifLibrary {id: "global_motif_library"})
            SET ml.total_motifs = ml.total_motifs + $motifs,
                ml.usage_count = ml.usage_count + 1
        """, motifs=motifs_extracted, patterns=patterns_identified)
    
    def query_learned_motifs(self, sequence_fragment: str) -> List[Dict[str, Any]]:
        """
        Phase 2.2: Query the AKG for learned motifs matching a sequence fragment
        
        This enables experience-based seeding for new sequences.
        """
        
        try:
            with self.driver.session() as session:
                # Find motifs that match or overlap with the given fragment
                result = session.run("""
                    MATCH (m:StructuralMotif)
                    WHERE m.sequence_fragment CONTAINS $fragment 
                       OR $fragment CONTAINS m.sequence_fragment
                    RETURN m.id as motif_id,
                           m.motif_type as type,
                           m.sequence_fragment as fragment,
                           m.confidence as confidence,
                           m.validation_score as validation_score,
                           m.start_position as start_pos,
                           m.end_position as end_pos
                    ORDER BY m.confidence DESC, m.validation_score DESC
                    LIMIT 10
                """, fragment=sequence_fragment)
                
                motifs = []
                for record in result:
                    motifs.append({
                        'motif_id': record['motif_id'],
                        'type': record['type'],
                        'fragment': record['fragment'],
                        'confidence': record['confidence'],
                        'validation_score': record['validation_score'],
                        'start_position': record['start_pos'],
                        'end_position': record['end_pos']
                    })
                
                logger.info(f"Found {len(motifs)} learned motifs for fragment: {sequence_fragment}")
                return motifs
                
        except Exception as e:
            logger.error(f"Error querying learned motifs: {e}")
            return []
    
    def get_entanglement_patterns(self, discovery_id: str = None) -> List[Dict[str, Any]]:
        """Get entanglement patterns, optionally filtered by discovery"""
        
        try:
            with self.driver.session() as session:
                if discovery_id:
                    query = """
                    MATCH (d:Discovery {id: $discovery_id})-[:EXHIBITS_PATTERN]->(ep:EntanglementPattern)
                    RETURN ep.id as pattern_id, ep.pattern_type as type,
                           ep.average_strength as strength, ep.residue_count as residues
                    """
                    result = session.run(query, discovery_id=discovery_id)
                else:
                    query = """
                    MATCH (ep:EntanglementPattern)
                    RETURN ep.id as pattern_id, ep.pattern_type as type,
                           ep.average_strength as strength, ep.residue_count as residues
                    ORDER BY ep.average_strength DESC
                    LIMIT 20
                    """
                    result = session.run(query)
                
                patterns = []
                for record in result:
                    patterns.append({
                        'pattern_id': record['pattern_id'],
                        'type': record['type'],
                        'average_strength': record['strength'],
                        'residue_count': record['residues']
                    })
                
                return patterns
                
        except Exception as e:
            logger.error(f"Error getting entanglement patterns: {e}")
            return []
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get current learning system statistics"""
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (ls:LearningSession {active: true})
                    MATCH (ml:MotifLibrary {id: "global_motif_library"})
                    OPTIONAL MATCH (:EntanglementPattern)
                    WITH ls, ml, count(*) as total_patterns
                    RETURN ls.total_discoveries_learned as discoveries_learned,
                           ls.motifs_extracted as motifs_extracted,
                           ls.patterns_identified as patterns_identified,
                           ml.total_motifs as library_motifs,
                           total_patterns
                """)
                
                record = result.single()
                if record:
                    return {
                        'discoveries_learned': record['discoveries_learned'] or 0,
                        'motifs_extracted': record['motifs_extracted'] or 0,
                        'patterns_identified': record['patterns_identified'] or 0,
                        'library_motifs': record['library_motifs'] or 0,
                        'total_patterns': record['total_patterns'] or 0
                    }
                else:
                    return {
                        'discoveries_learned': 0,
                        'motifs_extracted': 0,
                        'patterns_identified': 0,
                        'library_motifs': 0,
                        'total_patterns': 0
                    }
                    
        except Exception as e:
            logger.error(f"Error getting learning statistics: {e}")
            return {}

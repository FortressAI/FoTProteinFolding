"""
Comprehensive 5-Layer Genetics Ontology for FoT Framework
Extends protein discovery to full DNA-to-therapy optimization
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

class LayerType(Enum):
    GENOMIC = "genomic"
    EPIGENOMIC = "epigenomic" 
    REGULATORY = "regulatory"
    PROTEOSTASIS = "proteostasis"
    PHENOTYPIC = "phenotypic"

class VirtueType(Enum):
    FIDELITY = "fidelity"
    ROBUSTNESS = "robustness"
    EFFICIENCY = "efficiency"
    RESILIENCE = "resilience"
    PARSIMONY = "parsimony"

@dataclass
class GeneticsEntity:
    """Base class for all genetics entities"""
    id: str
    layer: LayerType
    name: str
    description: str
    properties: Dict[str, Any]

@dataclass
class GeneticVariant(GeneticsEntity):
    """SNP or other genetic variant affecting protein folding/regulation"""
    rsid: str
    chromosome: str
    position: int
    ref_allele: str
    alt_allele: str
    allele_frequency: float
    folding_impact: float  # Impact on protein folding success
    regulatory_impact: float  # Impact on gene regulation
    
@dataclass
class RegulatoryElement(GeneticsEntity):
    """Transcription factor, miRNA, or other regulatory element"""
    regulatory_type: str  # TF, miRNA, lncRNA, etc.
    binding_affinity: float
    expression_level: float
    target_genes: List[str]
    
class GeneticsOntology:
    """Complete 5-layer genetics ontology"""
    
    def __init__(self):
        self.entities = {}
        self.relationships = {}
        self.virtue_weights = {
            VirtueType.FIDELITY: 0.3,
            VirtueType.ROBUSTNESS: 0.25,
            VirtueType.EFFICIENCY: 0.2,
            VirtueType.RESILIENCE: 0.15,
            VirtueType.PARSIMONY: 0.1
        }
        
    def add_entity(self, entity: GeneticsEntity):
        """Add entity to ontology"""
        self.entities[entity.id] = entity
        
    def create_relationship(self, from_id: str, to_id: str, 
                          relationship_type: str, properties: Dict[str, Any] = None):
        """Create relationship between entities"""
        if from_id not in self.relationships:
            self.relationships[from_id] = []
        self.relationships[from_id].append({
            'to': to_id,
            'type': relationship_type,
            'properties': properties or {}
        })
        
    def get_entities_by_layer(self, layer: LayerType) -> List[GeneticsEntity]:
        """Get all entities in a specific layer"""
        return [entity for entity in self.entities.values() 
                if entity.layer == layer]
        
    def calculate_virtue_score(self, entity_id: str, virtue: VirtueType) -> float:
        """Calculate virtue score for an entity"""
        if entity_id not in self.entities:
            return 0.0
            
        entity = self.entities[entity_id]
        
        # Simple virtue calculation based on entity properties
        if virtue == VirtueType.FIDELITY:
            return entity.properties.get('accuracy', 0.5)
        elif virtue == VirtueType.ROBUSTNESS:
            return entity.properties.get('stability', 0.5)
        elif virtue == VirtueType.EFFICIENCY:
            return entity.properties.get('efficiency', 0.5)
        elif virtue == VirtueType.RESILIENCE:
            return entity.properties.get('resilience', 0.5)
        elif virtue == VirtueType.PARSIMONY:
            return entity.properties.get('simplicity', 0.5)
        
        return 0.5

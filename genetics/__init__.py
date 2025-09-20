"""
Genetics & Therapeutics Framework for FoT
Extends protein discovery to complete DNA-to-therapy optimization
"""

from .genetics_ontology import GeneticsOntology, VirtueType, GeneticsEntity
from .genetics_optimization import GeneticsOptimizer, OptimizationVariable
from .genetics_simulation import GeneticsAnalyzer, AnalysisState

__version__ = "1.0.0"
__all__ = [
    "GeneticsOntology", "VirtueType", "GeneticsEntity",
    "GeneticsOptimizer", "OptimizationVariable", 
    "GeneticsAnalyzer", "AnalysisState"
]

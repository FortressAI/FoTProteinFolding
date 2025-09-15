#!/usr/bin/env python3
"""
Scientific Sequence Generator
Generates biologically realistic protein sequences based on known structural principles
"""

import random
import numpy as np
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from collections import Counter

@dataclass
class SequenceConstraints:
    """Constraints for generating realistic sequences"""
    min_length: int = 15
    max_length: int = 50
    max_hydrophobic_run: int = 4
    min_charged_residues: int = 2
    max_single_aa_fraction: float = 0.3
    target_disorder_content: float = 0.7
    target_beta_content: float = 0.2
    target_helix_content: float = 0.1

class ScientificSequenceGenerator:
    """
    Generate scientifically realistic protein sequences
    Based on experimental amino acid frequencies and structural propensities
    """
    
    def __init__(self, random_seed: int = None):
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)
        
        # Amino acid frequencies from natural disordered proteins
        self.disorder_frequencies = {
            'G': 0.12,  # Glycine - high flexibility
            'S': 0.10,  # Serine - polar, flexible
            'P': 0.08,  # Proline - helix breaker
            'E': 0.08,  # Glutamate - charged, disorder-promoting
            'D': 0.07,  # Aspartate - charged, disorder-promoting
            'K': 0.07,  # Lysine - charged, disorder-promoting
            'R': 0.06,  # Arginine - charged, disorder-promoting
            'N': 0.06,  # Asparagine - polar, flexible
            'Q': 0.05,  # Glutamine - polar, flexible
            'T': 0.05,  # Threonine - polar, flexible
            'A': 0.08,  # Alanine - small, flexible
            'H': 0.03,  # Histidine - charged (pH dependent)
            'C': 0.02,  # Cysteine - can form disulfides
            'Y': 0.03,  # Tyrosine - aromatic, moderate disorder
            'M': 0.02,  # Methionine - hydrophobic but flexible
            'W': 0.015, # Tryptophan - large aromatic
            'F': 0.025, # Phenylalanine - aromatic
            'L': 0.04,  # Leucine - hydrophobic
            'I': 0.03,  # Isoleucine - hydrophobic
            'V': 0.04   # Valine - hydrophobic
        }
        
        # Secondary structure propensities (Chou-Fasman scale)
        self.helix_propensities = {
            'E': 1.51, 'A': 1.42, 'L': 1.21, 'H': 1.00, 'M': 1.45,
            'Q': 1.11, 'W': 1.08, 'V': 1.06, 'F': 1.13, 'K': 1.16,
            'I': 1.08, 'D': 1.01, 'T': 0.83, 'S': 0.77, 'R': 0.98,
            'C': 0.70, 'N': 0.67, 'Y': 0.69, 'P': 0.57, 'G': 0.57
        }
        
        self.sheet_propensities = {
            'M': 1.05, 'V': 1.70, 'I': 1.60, 'C': 1.19, 'Y': 1.47,
            'F': 1.38, 'Q': 1.10, 'L': 1.21, 'T': 1.19, 'W': 1.37,
            'A': 0.83, 'R': 0.93, 'G': 0.75, 'D': 0.54, 'K': 0.74,
            'S': 0.75, 'H': 0.87, 'N': 0.89, 'P': 0.55, 'E': 0.37
        }
        
        # Hydrophobic residues
        self.hydrophobic = {'A', 'I', 'L', 'M', 'F', 'W', 'Y', 'V'}
        self.charged = {'D', 'E', 'K', 'R', 'H'}
        self.polar = {'S', 'T', 'N', 'Q', 'C'}
        
        # Known pathological motifs (to include sparingly)
        self.pathological_motifs = {
            'KLVFF': 'amyloid_beta_core',
            'LVFFA': 'amyloid_variant',
            'GYMLG': 'alpha_synuclein',
            'GGVV': 'aggregation_prone'
        }
        
        # Disorder-promoting motifs
        self.disorder_motifs = {
            'GPG': 'proline_hinge',
            'GSG': 'flexible_linker',
            'EEK': 'charge_cluster',
            'DDD': 'charge_cluster',
            'KKK': 'charge_cluster'
        }
    
    def generate_realistic_sequence(self, constraints: SequenceConstraints = None) -> str:
        """Generate a biologically realistic sequence"""
        
        if constraints is None:
            constraints = SequenceConstraints()
        
        length = random.randint(constraints.min_length, constraints.max_length)
        
        # Design sequence composition
        target_composition = self._design_composition(length, constraints)
        
        # Build sequence with structural awareness
        sequence = self._build_structured_sequence(target_composition, constraints)
        
        # Validate and adjust if necessary
        sequence = self._validate_and_adjust_sequence(sequence, constraints)
        
        return sequence
    
    def _design_composition(self, length: int, constraints: SequenceConstraints) -> Dict[str, int]:
        """Design amino acid composition based on constraints"""
        
        composition = {}
        
        # Start with disorder-promoting residues
        disorder_count = int(length * constraints.target_disorder_content)
        
        # Ensure minimum charged residues
        charged_count = max(constraints.min_charged_residues, int(length * 0.15))
        
        # Calculate hydrophobic content (but not too much)
        hydrophobic_count = int(length * 0.25)  # 25% hydrophobic max
        
        # Distribute amino acids
        remaining = length
        
        # Add charged residues first
        charged_aas = ['D', 'E', 'K', 'R']
        for aa in charged_aas:
            count = max(1, charged_count // len(charged_aas))
            composition[aa] = min(count, remaining)
            remaining -= composition[aa]
        
        # Add flexibility residues
        flexibility_aas = ['G', 'P', 'S']
        flexibility_count = int(length * 0.2)
        for aa in flexibility_aas:
            count = flexibility_count // len(flexibility_aas)
            composition[aa] = min(count, remaining)
            remaining -= composition[aa]
        
        # Add polar residues
        polar_aas = ['N', 'Q', 'T']
        polar_count = int(length * 0.15)
        for aa in polar_aas:
            count = polar_count // len(polar_aas)
            composition[aa] = min(count, remaining)
            remaining -= composition[aa]
        
        # Add moderate hydrophobic residues
        hydrophobic_aas = ['A', 'L', 'V', 'I']
        for aa in hydrophobic_aas:
            count = min(2, remaining // len(hydrophobic_aas))
            composition[aa] = count
            remaining -= count
        
        # Fill remaining with aromatic residues (sparingly)
        aromatic_aas = ['F', 'Y', 'W']
        for aa in aromatic_aas:
            if remaining > 0:
                composition[aa] = min(1, remaining)
                remaining -= composition.get(aa, 0)
        
        # Add any remaining as alanine (small, neutral)
        if remaining > 0:
            composition['A'] = composition.get('A', 0) + remaining
        
        return composition
    
    def _build_structured_sequence(self, composition: Dict[str, int], constraints: SequenceConstraints) -> str:
        """Build sequence with some structural logic"""
        
        # Create amino acid pool
        aa_pool = []
        for aa, count in composition.items():
            aa_pool.extend([aa] * count)
        
        # Shuffle the pool
        random.shuffle(aa_pool)
        
        sequence = []
        i = 0
        
        while i < len(aa_pool):
            # Occasionally insert disorder motifs
            if i < len(aa_pool) - 3 and random.random() < 0.1:
                motif = random.choice(list(self.disorder_motifs.keys()))
                # Check if we have the required amino acids
                motif_aas = list(motif)
                if all(aa in aa_pool[i:] for aa in motif_aas):
                    # Remove required amino acids from pool
                    for aa in motif_aas:
                        if aa in aa_pool[i:]:
                            idx = aa_pool.index(aa, i)
                            aa_pool.pop(idx)
                    sequence.extend(motif_aas)
                    continue
            
            # Avoid long hydrophobic runs
            if (len(sequence) >= constraints.max_hydrophobic_run and 
                all(aa in self.hydrophobic for aa in sequence[-constraints.max_hydrophobic_run:])):
                # Force a non-hydrophobic residue
                non_hydrophobic = [aa for aa in aa_pool[i:] if aa not in self.hydrophobic]
                if non_hydrophobic:
                    chosen_aa = non_hydrophobic[0]
                    aa_pool.remove(chosen_aa)
                    sequence.append(chosen_aa)
                    continue
            
            # Add next amino acid from pool
            if i < len(aa_pool):
                sequence.append(aa_pool[i])
                i += 1
        
        return ''.join(sequence)
    
    def _validate_and_adjust_sequence(self, sequence: str, constraints: SequenceConstraints) -> str:
        """Validate sequence meets constraints and adjust if needed"""
        
        # Check hydrophobic runs
        sequence = self._fix_hydrophobic_runs(sequence, constraints.max_hydrophobic_run)
        
        # Check amino acid diversity
        sequence = self._ensure_diversity(sequence, constraints.max_single_aa_fraction)
        
        # Ensure minimum charged residues
        sequence = self._ensure_charged_residues(sequence, constraints.min_charged_residues)
        
        return sequence
    
    def _fix_hydrophobic_runs(self, sequence: str, max_run: int) -> str:
        """Break up long hydrophobic runs"""
        
        sequence_list = list(sequence)
        
        i = 0
        while i < len(sequence_list) - max_run:
            # Check for hydrophobic run
            if all(aa in self.hydrophobic for aa in sequence_list[i:i+max_run+1]):
                # Insert a polar residue in the middle
                insert_pos = i + max_run // 2
                polar_residues = ['S', 'T', 'N', 'Q']
                sequence_list[insert_pos] = random.choice(polar_residues)
            i += 1
        
        return ''.join(sequence_list)
    
    def _ensure_diversity(self, sequence: str, max_fraction: float) -> str:
        """Ensure no amino acid dominates the sequence"""
        
        composition = Counter(sequence)
        sequence_list = list(sequence)
        
        for aa, count in composition.items():
            if count / len(sequence) > max_fraction:
                # Replace excess amino acids
                excess = count - int(len(sequence) * max_fraction)
                positions = [i for i, s_aa in enumerate(sequence_list) if s_aa == aa]
                
                # Replace random positions
                replace_positions = random.sample(positions, excess)
                replacement_aas = [a for a in 'GSTNEQDK' if a != aa]
                
                for pos in replace_positions:
                    sequence_list[pos] = random.choice(replacement_aas)
        
        return ''.join(sequence_list)
    
    def _ensure_charged_residues(self, sequence: str, min_charged: int) -> str:
        """Ensure minimum number of charged residues"""
        
        charged_count = sum(1 for aa in sequence if aa in self.charged)
        sequence_list = list(sequence)  # Always create sequence_list
        
        if charged_count < min_charged:
            # Replace some residues with charged ones
            needed = min_charged - charged_count
            
            # Find replaceable positions (avoid breaking known motifs)
            replaceable = []
            for i, aa in enumerate(sequence_list):
                if aa not in self.charged and aa not in 'GP':  # Don't replace G or P
                    replaceable.append(i)
            
            if len(replaceable) >= needed:
                replace_positions = random.sample(replaceable, needed)
                charged_aas = ['D', 'E', 'K', 'R']
                
                for pos in replace_positions:
                    sequence_list[pos] = random.choice(charged_aas)
        
        return ''.join(sequence_list)
    
    def generate_known_pathological_sequence(self) -> Tuple[str, str]:
        """Generate a sequence based on known pathological proteins"""
        
        known_sequences = {
            'amyloid_beta_42': 'DAEFRHDSGYEVHHQKLVFFAEDVGSNKGAIIGLMVGGVVIA',
            'amyloid_beta_core': 'KLVFFAEDVGSNKGAIIGLMVGGVV',
            'alpha_synuclein_nac': 'GVVHGVATVAEKTKEQVTNVGGAVVTGVTAVA',
            'tau_r3': 'GKVQIINKKLDLSNVQSKCGSKDNIKHVPGGGS'
        }
        
        # Choose a known sequence and create a variant
        base_name, base_seq = random.choice(list(known_sequences.items()))
        
        # Create a conservative variant (1-3 mutations)
        variant = self._create_conservative_variant(base_seq)
        
        return variant, f"{base_name}_variant"
    
    def _create_conservative_variant(self, sequence: str) -> str:
        """Create a conservative variant of a known sequence"""
        
        sequence_list = list(sequence)
        n_mutations = random.randint(1, min(3, len(sequence) // 10))
        
        # Conservative substitution matrix
        conservative_subs = {
            'D': ['E', 'N'], 'E': ['D', 'Q'], 'K': ['R'], 'R': ['K'],
            'S': ['T', 'N'], 'T': ['S', 'N'], 'N': ['S', 'T', 'Q'],
            'Q': ['N', 'E'], 'L': ['I', 'V'], 'I': ['L', 'V'], 'V': ['L', 'I'],
            'F': ['Y', 'W'], 'Y': ['F'], 'A': ['G', 'S'], 'G': ['A', 'S']
        }
        
        positions = random.sample(range(len(sequence)), n_mutations)
        
        for pos in positions:
            original_aa = sequence_list[pos]
            if original_aa in conservative_subs:
                sequence_list[pos] = random.choice(conservative_subs[original_aa])
        
        return ''.join(sequence_list)
    
    def calculate_sequence_quality_score(self, sequence: str) -> float:
        """Calculate a quality score for the sequence (0-1)"""
        
        score = 1.0
        composition = Counter(sequence)
        
        # Penalize extreme compositions
        for aa, count in composition.items():
            fraction = count / len(sequence)
            if fraction > 0.4:  # No amino acid should be >40%
                score *= 0.5
        
        # Check hydrophobic balance
        hydrophobic_count = sum(1 for aa in sequence if aa in self.hydrophobic)
        hydrophobic_fraction = hydrophobic_count / len(sequence)
        
        if hydrophobic_fraction > 0.7:  # Too hydrophobic
            score *= 0.3
        elif hydrophobic_fraction < 0.1:  # Too hydrophilic
            score *= 0.7
        
        # Check for long hydrophobic runs
        max_hydrophobic_run = 0
        current_run = 0
        for aa in sequence:
            if aa in self.hydrophobic:
                current_run += 1
                max_hydrophobic_run = max(max_hydrophobic_run, current_run)
            else:
                current_run = 0
        
        if max_hydrophobic_run > 5:
            score *= 0.4
        
        # Check charge content
        charged_count = sum(1 for aa in sequence if aa in self.charged)
        if charged_count < 2:
            score *= 0.6
        
        return max(0.0, min(1.0, score))

def test_generator():
    """Test the sequence generator"""
    
    print("🧬 TESTING SCIENTIFIC SEQUENCE GENERATOR")
    print("=" * 50)
    
    generator = ScientificSequenceGenerator(random_seed=42)
    
    # Test realistic sequences
    print("\n🔬 REALISTIC SEQUENCES:")
    for i in range(5):
        sequence = generator.generate_realistic_sequence()
        score = generator.calculate_sequence_quality_score(sequence)
        print(f"{i+1}. {sequence} (Quality: {score:.3f})")
    
    # Test known pathological variants
    print("\n🦠 PATHOLOGICAL VARIANTS:")
    for i in range(3):
        sequence, name = generator.generate_known_pathological_sequence()
        score = generator.calculate_sequence_quality_score(sequence)
        print(f"{i+1}. {name}: {sequence} (Quality: {score:.3f})")

if __name__ == "__main__":
    test_generator()

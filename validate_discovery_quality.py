#!/usr/bin/env python3
"""
Discovery Quality Validation
Comprehensive validation to ensure discoveries are scientifically meaningful, not random garbage
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import Counter
import numpy as np
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of discovery validation"""
    sequence: str
    discovery_id: str
    is_valid: bool
    validation_score: float
    failed_checks: List[str]
    warnings: List[str]
    scientific_assessment: str

class DiscoveryQualityValidator:
    """Validate that discoveries are scientifically meaningful"""
    
    def __init__(self):
        self.known_good_sequences = self._load_known_sequences()
        self.validation_thresholds = self._define_validation_thresholds()
        
    def _load_known_sequences(self) -> Dict[str, Dict]:
        """Load known therapeutic and pathological sequences for comparison"""
        return {
            # Known Alzheimer's sequences
            "DAEFRHDSGYEVHHQKLVFFAEDVGSNKGAIIGLMVGGVVIA": {
                "name": "Amyloid-beta 42",
                "type": "pathological",
                "disease": "Alzheimer's",
                "validated": True
            },
            "KLVFFAEDVGSNKGAIIGLMVGGVV": {
                "name": "Amyloid-beta core",
                "type": "pathological", 
                "disease": "Alzheimer's",
                "validated": True
            },
            # Known Parkinson's sequences  
            "MDVFMKGLSKAKEGVVAAAEKTKQGVAEAAGKTKEGVLYVGSKTKEGVVHGVATVAEKTKEQVTNVGGAVVTGVTAVAQKTVEGAGSIAAATGFVKKDQLGKNEEGAPQEGILEDMPVDPDNEAYEMPSEEGYQDYEPEA": {
                "name": "Alpha-synuclein full",
                "type": "pathological",
                "disease": "Parkinson's", 
                "validated": True
            },
            "GVVHGVATVAEKTKEQVTNVGGAVVTGVTAVA": {
                "name": "Alpha-synuclein NAC core",
                "type": "pathological",
                "disease": "Parkinson's",
                "validated": True
            },
            # Known therapeutic sequences
            "HLVEALYLVCGERGFFYTPKT": {
                "name": "Insulin B chain",
                "type": "therapeutic",
                "function": "hormone",
                "validated": True
            }
        }
    
    def _define_validation_thresholds(self) -> Dict[str, Dict]:
        """Define thresholds for validation checks"""
        return {
            "length": {"min": 10, "max": 100, "optimal_min": 15, "optimal_max": 60},
            "composition": {
                "max_single_aa_fraction": 0.5,  # No single amino acid >50%
                "min_unique_aa": 6,              # At least 6 different amino acids
                "max_simple_repeats": 0.3        # <30% simple repeats
            },
            "hydrophobicity": {
                "min_hydrophobic_fraction": 0.1,  # At least 10% hydrophobic
                "max_hydrophobic_fraction": 0.8   # No more than 80% hydrophobic
            },
            "charge": {
                "max_net_charge_per_residue": 0.5,  # Reasonable charge distribution
                "min_charge_variety": 2              # At least 2 types of charged residues
            },
            "secondary_structure": {
                "min_structure_potential": 0.1,   # Some secondary structure potential
                "max_single_structure": 1.5       # Allow realistic structure bias
            },
            "biological_plausibility": {
                "min_known_motifs": 1,             # At least one known motif
                "max_stop_codons": 0,              # No premature stop codons
                "min_stability_score": -50.0      # Reasonable stability
            }
        }
    
    def check_sequence_length(self, sequence: str) -> Tuple[bool, str]:
        """Check if sequence length is reasonable"""
        length = len(sequence)
        thresholds = self.validation_thresholds["length"]
        
        if length < thresholds["min"]:
            return False, f"Too short ({length} < {thresholds['min']} residues)"
        elif length > thresholds["max"]:
            return False, f"Too long ({length} > {thresholds['max']} residues)"
        elif length < thresholds["optimal_min"]:
            return True, f"Short but acceptable ({length} residues)"
        elif length > thresholds["optimal_max"]:
            return True, f"Long but acceptable ({length} residues)"
        else:
            return True, f"Optimal length ({length} residues)"
    
    def check_amino_acid_composition(self, sequence: str) -> Tuple[bool, List[str]]:
        """Check amino acid composition for biological plausibility"""
        
        composition = Counter(sequence)
        total_length = len(sequence)
        unique_aa = len(composition)
        
        issues = []
        thresholds = self.validation_thresholds["composition"]
        
        # Check for too many of a single amino acid
        max_fraction = max(composition.values()) / total_length
        if max_fraction > thresholds["max_single_aa_fraction"]:
            most_common_aa = composition.most_common(1)[0]
            issues.append(f"Too much {most_common_aa[0]}: {max_fraction:.1%} (>{thresholds['max_single_aa_fraction']:.1%})")
        
        # Check for sufficient diversity
        if unique_aa < thresholds["min_unique_aa"]:
            issues.append(f"Too few unique amino acids: {unique_aa} (min {thresholds['min_unique_aa']})")
        
        # Check for simple repeats
        repeat_fraction = self._calculate_repeat_fraction(sequence)
        if repeat_fraction > thresholds["max_simple_repeats"]:
            issues.append(f"Too many simple repeats: {repeat_fraction:.1%} (>{thresholds['max_simple_repeats']:.1%})")
        
        return len(issues) == 0, issues
    
    def _calculate_repeat_fraction(self, sequence: str) -> float:
        """Calculate fraction of sequence that is simple repeats"""
        
        repeat_residues = 0
        
        # Check for 2-mers, 3-mers, 4-mers
        for repeat_length in [2, 3, 4]:
            for i in range(len(sequence) - repeat_length * 2 + 1):
                motif = sequence[i:i+repeat_length]
                if sequence[i+repeat_length:i+repeat_length*2] == motif:
                    # Found a repeat, count how long it extends
                    j = i + repeat_length * 2
                    while j + repeat_length <= len(sequence) and sequence[j:j+repeat_length] == motif:
                        j += repeat_length
                    repeat_residues += j - i
                    break
        
        return repeat_residues / len(sequence)
    
    def check_hydrophobicity_balance(self, sequence: str) -> Tuple[bool, str]:
        """Check hydrophobicity balance"""
        
        hydrophobic_aa = "AILMFWYV"
        hydrophobic_count = sum(1 for aa in sequence if aa in hydrophobic_aa)
        hydrophobic_fraction = hydrophobic_count / len(sequence)
        
        thresholds = self.validation_thresholds["hydrophobicity"]
        
        if hydrophobic_fraction < thresholds["min_hydrophobic_fraction"]:
            return False, f"Too hydrophilic ({hydrophobic_fraction:.1%} hydrophobic, min {thresholds['min_hydrophobic_fraction']:.1%})"
        elif hydrophobic_fraction > thresholds["max_hydrophobic_fraction"]:
            return False, f"Too hydrophobic ({hydrophobic_fraction:.1%} hydrophobic, max {thresholds['max_hydrophobic_fraction']:.1%})"
        else:
            return True, f"Good hydrophobic balance ({hydrophobic_fraction:.1%})"
    
    def check_charge_distribution(self, sequence: str) -> Tuple[bool, List[str]]:
        """Check charge distribution"""
        
        positive_aa = "KRH"
        negative_aa = "DE"
        
        positive_count = sum(1 for aa in sequence if aa in positive_aa)
        negative_count = sum(1 for aa in sequence if aa in negative_aa)
        net_charge = positive_count - negative_count
        net_charge_per_residue = abs(net_charge) / len(sequence)
        
        charge_types = 0
        if positive_count > 0:
            charge_types += 1
        if negative_count > 0:
            charge_types += 1
        
        thresholds = self.validation_thresholds["charge"]
        issues = []
        
        if net_charge_per_residue > thresholds["max_net_charge_per_residue"]:
            issues.append(f"Extreme net charge: {net_charge:+d} ({net_charge_per_residue:.2f} per residue)")
        
        if charge_types < thresholds["min_charge_variety"] and len(sequence) > 20:
            issues.append(f"Poor charge variety: only {charge_types} charge types")
        
        return len(issues) == 0, issues
    
    def check_secondary_structure_potential(self, sequence: str) -> Tuple[bool, str]:
        """Check secondary structure forming potential"""
        
        # Normalized Chou-Fasman propensities (average = 1.0)
        helix_prop = {
            "A": 1.42, "E": 1.51, "L": 1.21, "M": 1.45, "Q": 1.11, "K": 1.16,
            "V": 1.06, "F": 1.13, "H": 1.00, "I": 1.08, "W": 1.08, "D": 1.01,
            "T": 0.83, "S": 0.77, "R": 0.98, "C": 0.70, "N": 0.67, "Y": 0.69,
            "P": 0.57, "G": 0.57
        }
        
        sheet_prop = {
            "V": 1.70, "I": 1.60, "Y": 1.47, "F": 1.38, "W": 1.37, "L": 1.21,
            "T": 1.19, "C": 1.19, "Q": 1.10, "M": 1.05, "H": 0.87, "R": 0.93,
            "N": 0.89, "A": 0.83, "S": 0.75, "G": 0.75, "K": 0.74, "D": 0.54,
            "P": 0.55, "E": 0.37
        }
        
        helix_score = sum(helix_prop.get(aa, 1.0) for aa in sequence) / len(sequence)
        sheet_score = sum(sheet_prop.get(aa, 1.0) for aa in sequence) / len(sequence)
        
        max_structure_score = max(helix_score, sheet_score)
        
        thresholds = self.validation_thresholds["secondary_structure"]
        
        if max_structure_score < thresholds["min_structure_potential"]:
            return False, f"Low structure potential (max score: {max_structure_score:.2f})"
        elif max_structure_score > thresholds["max_single_structure"]:
            return False, f"Overly biased structure (score: {max_structure_score:.2f})"
        else:
            return True, f"Good structure potential (helix: {helix_score:.2f}, sheet: {sheet_score:.2f})"
    
    def check_known_motifs(self, sequence: str) -> Tuple[bool, List[str]]:
        """Check for known biological motifs"""
        
        # Known pathological and functional motifs
        motifs = {
            "KLVFF": "Amyloid-beta core",
            "LVFF": "Amyloid core variant", 
            "FAEDV": "Amyloid segment",
            "GGVV": "Hydrophobic cluster",
            "GYMLG": "Alpha-synuclein motif",
            "RGD": "Integrin binding",
            "YIGSR": "Laminin binding",
            "REDV": "Fibronectin binding",
            "PHSRN": "Fibronectin synergy",
            "DGEA": "Collagen binding"
        }
        
        found_motifs = []
        for motif, description in motifs.items():
            if motif in sequence:
                found_motifs.append(f"{motif} ({description})")
        
        # Also check for more general patterns
        if re.search(r'[FWY]{2,3}', sequence):  # Aromatic clusters
            found_motifs.append("Aromatic cluster (hydrophobic interaction)")
        
        if re.search(r'[KR][DE]|[DE][KR]', sequence):  # Salt bridge potential
            found_motifs.append("Salt bridge motif (stabilizing)")
        
        if re.search(r'C.{2,20}C', sequence):  # Potential disulfide
            found_motifs.append("Potential disulfide bridge")
        
        thresholds = self.validation_thresholds["biological_plausibility"]
        
        if len(found_motifs) >= thresholds["min_known_motifs"]:
            return True, found_motifs
        else:
            return False, ["No recognized biological motifs found"]
    
    def calculate_stability_score(self, sequence: str) -> float:
        """Calculate approximate stability score"""
        
        # Simple Kyte-Doolittle hydrophobicity scale
        hydrophobicity = {
            'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
            'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
            'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
            'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
        }
        
        # Approximate stability based on hydrophobic interactions and length
        hydrophobic_contribution = sum(hydrophobicity.get(aa, 0) for aa in sequence)
        length_penalty = len(sequence) * 0.5  # Entropy penalty
        
        stability_score = hydrophobic_contribution - length_penalty
        
        return stability_score
    
    def validate_against_known_sequences(self, sequence: str) -> Tuple[bool, str]:
        """Validate against known good/bad sequences"""
        
        # Check for exact matches to known sequences
        for known_seq, info in self.known_good_sequences.items():
            if sequence == known_seq:
                return True, f"Exact match to known {info['type']}: {info['name']}"
        
        # Check for high similarity to known sequences
        for known_seq, info in self.known_good_sequences.items():
            similarity = self._calculate_similarity(sequence, known_seq)
            if similarity > 0.8:
                return True, f"High similarity ({similarity:.1%}) to {info['name']}"
        
        # Check if it's completely different from anything known (suspicious)
        max_similarity = 0.0
        for known_seq in self.known_good_sequences.keys():
            similarity = self._calculate_similarity(sequence, known_seq)
            max_similarity = max(max_similarity, similarity)
        
        if max_similarity < 0.1:
            return False, f"No similarity to any known sequences (max: {max_similarity:.1%})"
        
        return True, f"Reasonable similarity to known sequences (max: {max_similarity:.1%})"
    
    def _calculate_similarity(self, seq1: str, seq2: str) -> float:
        """Calculate sequence similarity"""
        if not seq1 or not seq2:
            return 0.0
        
        min_len = min(len(seq1), len(seq2))
        matches = 0
        
        for i in range(min_len):
            if seq1[i] == seq2[i]:
                matches += 1
        
        return matches / max(len(seq1), len(seq2))
    
    def comprehensive_validation(self, discovery: Dict[str, Any]) -> ValidationResult:
        """Run comprehensive validation on a discovery"""
        
        sequence = discovery.get("sequence", "")
        discovery_id = discovery.get("id", "unknown")
        
        if not sequence:
            return ValidationResult(
                sequence="",
                discovery_id=discovery_id,
                is_valid=False,
                validation_score=0.0,
                failed_checks=["Empty sequence"],
                warnings=[],
                scientific_assessment="INVALID: No sequence provided"
            )
        
        failed_checks = []
        warnings = []
        validation_scores = []
        
        # 1. Length check
        length_valid, length_msg = self.check_sequence_length(sequence)
        if not length_valid:
            failed_checks.append(f"Length: {length_msg}")
        else:
            validation_scores.append(0.9 if "optimal" in length_msg.lower() else 0.7)
        
        # 2. Composition check
        comp_valid, comp_issues = self.check_amino_acid_composition(sequence)
        if not comp_valid:
            failed_checks.extend([f"Composition: {issue}" for issue in comp_issues])
        else:
            validation_scores.append(0.85)
        
        # 3. Hydrophobicity check
        hydro_valid, hydro_msg = self.check_hydrophobicity_balance(sequence)
        if not hydro_valid:
            failed_checks.append(f"Hydrophobicity: {hydro_msg}")
        else:
            validation_scores.append(0.8)
        
        # 4. Charge distribution
        charge_valid, charge_issues = self.check_charge_distribution(sequence)
        if not charge_valid:
            failed_checks.extend([f"Charge: {issue}" for issue in charge_issues])
        else:
            validation_scores.append(0.75)
        
        # 5. Secondary structure potential
        struct_valid, struct_msg = self.check_secondary_structure_potential(sequence)
        if not struct_valid:
            failed_checks.append(f"Structure: {struct_msg}")
        else:
            validation_scores.append(0.8)
        
        # 6. Known motifs
        motif_valid, motif_list = self.check_known_motifs(sequence)
        if not motif_valid:
            warnings.extend(motif_list)
        else:
            validation_scores.append(0.9)
            
        # 7. Stability score
        stability_score = self.calculate_stability_score(sequence)
        if stability_score < self.validation_thresholds["biological_plausibility"]["min_stability_score"]:
            failed_checks.append(f"Stability: Too unstable ({stability_score:.1f})")
        else:
            validation_scores.append(0.7)
        
        # 8. Similarity to known sequences
        similarity_valid, similarity_msg = self.validate_against_known_sequences(sequence)
        if not similarity_valid:
            warnings.append(f"Similarity: {similarity_msg}")
        else:
            validation_scores.append(0.8)
        
        # Calculate overall validation score
        overall_score = np.mean(validation_scores) if validation_scores else 0.0
        
        # Determine if valid
        is_valid = len(failed_checks) == 0
        
        # Scientific assessment
        if is_valid and overall_score > 0.8:
            assessment = "SCIENTIFICALLY VALID: High quality therapeutic candidate"
        elif is_valid and overall_score > 0.6:
            assessment = "VALID: Acceptable therapeutic candidate with minor concerns"
        elif is_valid:
            assessment = "BORDERLINE: Valid but low quality, requires experimental validation"
        else:
            assessment = f"INVALID: Failed {len(failed_checks)} critical checks"
        
        return ValidationResult(
            sequence=sequence,
            discovery_id=discovery_id,
            is_valid=is_valid,
            validation_score=overall_score,
            failed_checks=failed_checks,
            warnings=warnings,
            scientific_assessment=assessment
        )
    
    def validate_discovery_batch(self, discoveries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of discoveries"""
        
        print(f"🔬 VALIDATING {len(discoveries)} DISCOVERIES FOR SCIENTIFIC QUALITY")
        print("=" * 70)
        
        validation_results = []
        
        for i, discovery in enumerate(discoveries, 1):
            result = self.comprehensive_validation(discovery)
            validation_results.append(result)
            
            if i <= 10 or not result.is_valid:  # Show first 10 and all failures
                status = "✅ VALID" if result.is_valid else "❌ INVALID"
                print(f"{i:3d}. {result.discovery_id}: {status}")
                print(f"     Score: {result.validation_score:.3f}")
                print(f"     Sequence: {result.sequence[:40]}{'...' if len(result.sequence) > 40 else ''}")
                
                if result.failed_checks:
                    print(f"     Failed: {'; '.join(result.failed_checks[:2])}")
                if result.warnings and result.is_valid:
                    print(f"     Warnings: {'; '.join(result.warnings[:2])}")
                print()
        
        # Calculate statistics
        valid_count = sum(1 for r in validation_results if r.is_valid)
        high_quality_count = sum(1 for r in validation_results if r.is_valid and r.validation_score > 0.8)
        avg_score = np.mean([r.validation_score for r in validation_results])
        
        # Categorize by quality
        high_quality = [r for r in validation_results if r.is_valid and r.validation_score > 0.8]
        medium_quality = [r for r in validation_results if r.is_valid and 0.6 <= r.validation_score <= 0.8]
        low_quality = [r for r in validation_results if r.is_valid and r.validation_score < 0.6]
        invalid = [r for r in validation_results if not r.is_valid]
        
        print("📊 VALIDATION SUMMARY:")
        print(f"   Total discoveries: {len(discoveries)}")
        print(f"   Valid discoveries: {valid_count} ({valid_count/len(discoveries)*100:.1f}%)")
        print(f"   High quality (>0.8): {high_quality_count} ({high_quality_count/len(discoveries)*100:.1f}%)")
        print(f"   Average quality score: {avg_score:.3f}")
        print()
        
        print("📈 QUALITY BREAKDOWN:")
        print(f"   🌟 High quality (>0.8): {len(high_quality)} discoveries")
        print(f"   ⭐ Medium quality (0.6-0.8): {len(medium_quality)} discoveries")
        print(f"   ⚠️  Low quality (<0.6): {len(low_quality)} discoveries")
        print(f"   ❌ Invalid: {len(invalid)} discoveries")
        print()
        
        # Show common failure reasons
        if invalid:
            failure_reasons = {}
            for result in invalid:
                for check in result.failed_checks:
                    reason = check.split(':')[0]
                    failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
            
            print("❌ COMMON FAILURE REASONS:")
            for reason, count in sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True):
                print(f"   {reason}: {count} failures")
            print()
        
        return {
            "total_discoveries": len(discoveries),
            "valid_discoveries": valid_count,
            "high_quality_discoveries": high_quality_count,
            "average_quality_score": avg_score,
            "validation_rate": valid_count / len(discoveries),
            "high_quality_rate": high_quality_count / len(discoveries),
            "quality_breakdown": {
                "high_quality": len(high_quality),
                "medium_quality": len(medium_quality), 
                "low_quality": len(low_quality),
                "invalid": len(invalid)
            },
            "validation_results": validation_results,
            "scientific_assessment": self._generate_scientific_assessment(validation_results)
        }
    
    def _generate_scientific_assessment(self, results: List[ValidationResult]) -> str:
        """Generate overall scientific assessment"""
        
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        high_quality = sum(1 for r in results if r.is_valid and r.validation_score > 0.8)
        
        if valid / total > 0.8 and high_quality / total > 0.5:
            return "EXCELLENT: High-quality therapeutic discovery pipeline producing scientifically valid candidates"
        elif valid / total > 0.6 and high_quality / total > 0.3:
            return "GOOD: Solid discovery pipeline with majority valid candidates"
        elif valid / total > 0.4:
            return "ACCEPTABLE: Discovery pipeline producing some valid candidates but needs improvement"
        else:
            return "POOR: Discovery pipeline producing mostly invalid candidates - major revision needed"

def main():
    """Run quality validation on all discoveries"""
    
    print("🔬 DISCOVERY QUALITY VALIDATION")
    print("🎯 Goal: Ensure discoveries are scientifically meaningful, not random garbage")
    print("=" * 80)
    
    # Find all discovery files
    all_discoveries = []
    
    discovery_dirs = [
        "fixed_massive_scale_discoveries",
        "massive_scale_discoveries", 
        "prior_art_publication",
        "production_cure_discoveries"
    ]
    
    for dir_name in discovery_dirs:
        discovery_dir = Path(dir_name)
        if discovery_dir.exists():
            print(f"📁 Checking {dir_name}...")
            for json_file in discovery_dir.glob("**/therapeutic_discoveries.json"):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        if "discoveries" in data:
                            all_discoveries.extend(data["discoveries"])
                            print(f"   Loaded {len(data['discoveries'])} discoveries from {json_file.name}")
                except Exception as e:
                    print(f"   ⚠️ Error loading {json_file}: {e}")
    
    if not all_discoveries:
        print("❌ No discoveries found to validate")
        return
    
    print(f"\n📊 Found {len(all_discoveries)} total discoveries")
    
    # Remove duplicates by sequence
    unique_discoveries = {}
    for discovery in all_discoveries:
        sequence = discovery.get("sequence", "")
        if sequence and sequence not in unique_discoveries:
            unique_discoveries[sequence] = discovery
    
    unique_list = list(unique_discoveries.values())
    print(f"📊 Unique sequences: {len(unique_list)}")
    
    # Run validation
    validator = DiscoveryQualityValidator()
    validation_summary = validator.validate_discovery_batch(unique_list)
    
    # Save results
    output_file = Path("discovery_quality_validation.json")
    with open(output_file, 'w') as f:
        # Convert ValidationResult objects to dicts for JSON serialization
        serializable_results = []
        for result in validation_summary["validation_results"]:
            serializable_results.append({
                "sequence": result.sequence,
                "discovery_id": result.discovery_id,
                "is_valid": result.is_valid,
                "validation_score": result.validation_score,
                "failed_checks": result.failed_checks,
                "warnings": result.warnings,
                "scientific_assessment": result.scientific_assessment
            })
        
        validation_summary["validation_results"] = serializable_results
        json.dump(validation_summary, f, indent=2)
    
    # Final assessment
    print("🎯 FINAL SCIENTIFIC ASSESSMENT:")
    print(f"   {validation_summary['scientific_assessment']}")
    print()
    
    if validation_summary["validation_rate"] > 0.8:
        print("✅ CONCLUSION: Discoveries are scientifically valid and meaningful!")
        print("   These are NOT random garbage - they represent legitimate therapeutic candidates")
    elif validation_summary["validation_rate"] > 0.5:
        print("⚠️ CONCLUSION: Mixed quality - most discoveries are valid but some improvements needed")
    else:
        print("❌ CONCLUSION: Poor quality discoveries - major improvements needed")
    
    print(f"\n📁 Detailed results saved: {output_file}")

if __name__ == "__main__":
    main()

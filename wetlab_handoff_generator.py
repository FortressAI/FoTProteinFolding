#!/usr/bin/env python3
"""
Wet-Lab Handoff Generator
Creates experiment-ready protocols and parameter sheets for top therapeutic candidates
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np

@dataclass 
class ExperimentalProtocol:
    """Experimental protocol parameters for a therapeutic candidate"""
    
    # Sample identification
    candidate_id: str
    sequence: str
    molecular_weight: float
    net_charge: float
    
    # CD Spectroscopy parameters
    cd_peptide_length: int
    cd_buffer: str
    cd_pathlength: float  # mm
    cd_concentration: float  # μM
    cd_expected_beta_content: float
    cd_expected_helix_content: float
    cd_confidence_interval: Tuple[float, float]
    
    # ThT Aggregation parameters
    tht_concentrations: List[float]  # μM
    tht_agitation: str
    tht_timecourse_hours: int
    tht_predicted_class: str
    tht_confidence_interval: Tuple[float, float]
    
    # NMR parameters
    nmr_target_chemical_shifts: Dict[str, float]
    nmr_uncertainty_hotspots: List[int]  # residue numbers
    nmr_recommended_experiments: List[str]
    
    # Microscopy parameters
    tem_predicted_morphology: str
    tem_sample_prep: str
    afm_recommended: bool

class WetLabHandoffGenerator:
    """Generate experiment-ready protocols and parameter sheets"""
    
    def __init__(self):
        self.protocols = []
        self.amino_acid_mw = {
            'A': 71.04, 'R': 156.10, 'N': 114.04, 'D': 115.03, 'C': 103.01,
            'E': 129.04, 'Q': 128.06, 'G': 57.02, 'H': 137.06, 'I': 113.08,
            'L': 113.08, 'K': 128.09, 'M': 131.04, 'F': 147.07, 'P': 97.05,
            'S': 87.03, 'T': 101.05, 'W': 186.08, 'Y': 163.06, 'V': 99.07
        }
        self.amino_acid_charge = {
            'K': +1, 'R': +1, 'H': +0.5, 'D': -1, 'E': -1
        }
    
    def calculate_molecular_properties(self, sequence: str) -> Tuple[float, float]:
        """Calculate molecular weight and net charge"""
        
        # Molecular weight calculation
        mw = sum(self.amino_acid_mw.get(aa, 110.0) for aa in sequence)
        mw += 18.015  # Add water for peptide bond formation correction
        mw -= 18.015 * (len(sequence) - 1)  # Subtract water lost in peptide bonds
        
        # Net charge calculation (pH 7.0)
        net_charge = sum(self.amino_acid_charge.get(aa, 0) for aa in sequence)
        
        return mw, net_charge
    
    def generate_cd_protocol(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CD spectroscopy protocol"""
        
        sequence = candidate["sequence"]
        length = len(sequence)
        
        # Recommended parameters based on sequence length
        if length < 25:
            pathlength = 1.0  # mm
            concentration = 50.0  # μM
        elif length < 40:
            pathlength = 0.5  # mm
            concentration = 30.0  # μM
        else:
            pathlength = 0.2  # mm
            concentration = 20.0  # μM
        
        # Buffer selection based on sequence properties
        basic_residues = sum(1 for aa in sequence if aa in 'KRH')
        acidic_residues = sum(1 for aa in sequence if aa in 'DE')
        
        if basic_residues > acidic_residues + 2:
            buffer = "10 mM Tris-HCl, pH 7.4, 150 mM NaCl"
        elif acidic_residues > basic_residues + 2:
            buffer = "10 mM phosphate, pH 7.0, 150 mM NaCl"
        else:
            buffer = "10 mM phosphate, pH 7.4, 150 mM NaCl"
        
        # Expected secondary structure from computational prediction
        beta_content = candidate.get("aggregation_propensity", 0.3)
        helix_content = max(0.05, 1.0 - beta_content - 0.6)  # Assume some helix
        
        return {
            "peptide_length": length,
            "buffer": buffer,
            "pathlength_mm": pathlength,
            "concentration_uM": concentration,
            "expected_beta_content": beta_content,
            "expected_helix_content": helix_content,
            "confidence_interval": (beta_content * 0.8, beta_content * 1.2),
            "scan_range": "190-250 nm",
            "scan_speed": "50 nm/min",
            "response_time": "1 sec",
            "bandwidth": "1 nm"
        }
    
    def generate_tht_protocol(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ThT aggregation assay protocol"""
        
        sequence = candidate["sequence"]
        aggregation_prop = candidate.get("aggregation_propensity", 0.3)
        
        # Concentration series based on aggregation propensity
        if aggregation_prop > 0.7:
            concentrations = [5, 10, 25, 50]  # High aggregation - lower concentrations
            predicted_class = "fast_aggregator"
        elif aggregation_prop > 0.4:
            concentrations = [10, 25, 50, 100]  # Medium aggregation
            predicted_class = "moderate_aggregator"
        else:
            concentrations = [25, 50, 100, 200]  # Low aggregation - higher concentrations
            predicted_class = "slow_aggregator"
        
        # Agitation based on sequence hydrophobicity
        hydrophobic_residues = sum(1 for aa in sequence if aa in 'FILVWY')
        hydrophobic_fraction = hydrophobic_residues / len(sequence)
        
        if hydrophobic_fraction > 0.4:
            agitation = "continuous orbital shaking at 200 rpm"
        else:
            agitation = "intermittent shaking every 30 min"
        
        # Timecourse based on predicted aggregation rate
        if aggregation_prop > 0.6:
            timecourse_hours = 48
        elif aggregation_prop > 0.3:
            timecourse_hours = 72
        else:
            timecourse_hours = 120
        
        return {
            "concentrations_uM": concentrations,
            "agitation": agitation,
            "timecourse_hours": timecourse_hours,
            "predicted_class": predicted_class,
            "confidence_interval": (aggregation_prop * 0.7, aggregation_prop * 1.3),
            "buffer": "20 mM Tris-HCl, pH 7.4, 150 mM NaCl",
            "tht_concentration": "20 μM",
            "excitation_wavelength": "440 nm",
            "emission_wavelength": "480 nm",
            "measurement_interval": "30 min"
        }
    
    def generate_nmr_protocol(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Generate NMR experimental recommendations"""
        
        sequence = candidate["sequence"]
        length = len(sequence)
        
        # Predict key chemical shift regions
        aromatic_residues = [i for i, aa in enumerate(sequence, 1) if aa in 'FYW']
        charged_residues = [i for i, aa in enumerate(sequence, 1) if aa in 'KRDEH']
        
        # Target chemical shifts (mock predictions)
        target_shifts = {}
        for i, aa in enumerate(sequence, 1):
            if aa == 'F':
                target_shifts[f"{aa}{i}_H"] = 7.2  # Aromatic region
            elif aa in 'KR':
                target_shifts[f"{aa}{i}_H"] = 8.1  # Amide NH region
            elif aa in 'DE':
                target_shifts[f"{aa}{i}_H"] = 8.3  # Shifted amide
        
        # Uncertainty hotspots (residues with high conformational flexibility)
        glycine_positions = [i for i, aa in enumerate(sequence, 1) if aa == 'G']
        loop_regions = glycine_positions + aromatic_residues  # Simplified prediction
        
        # Recommended experiments based on sequence properties
        experiments = ["1H-1D", "2D TOCSY", "2D NOESY"]
        
        if length > 30:
            experiments.append("15N-HSQC")
        if any(aa in 'FYW' for aa in sequence):
            experiments.append("Aromatic region analysis")
        if len(charged_residues) > 3:
            experiments.append("pH titration series")
        
        return {
            "target_chemical_shifts": target_shifts,
            "uncertainty_hotspots": loop_regions[:5],  # Top 5 uncertain residues
            "recommended_experiments": experiments,
            "sample_concentration": "0.5-1.0 mM",
            "buffer": "20 mM phosphate, pH 6.5, 50 mM NaCl, 10% D2O",
            "temperature": "298 K",
            "key_residues_to_monitor": aromatic_residues + charged_residues
        }
    
    def generate_microscopy_protocol(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Generate TEM/AFM microscopy recommendations"""
        
        sequence = candidate["sequence"]
        aggregation_prop = candidate.get("aggregation_propensity", 0.3)
        
        # Predict morphology based on sequence properties
        beta_content = candidate.get("aggregation_propensity", 0.3)
        hydrophobic_residues = sum(1 for aa in sequence if aa in 'FILVWY')
        
        if beta_content > 0.6 and hydrophobic_residues > len(sequence) * 0.3:
            morphology = "amyloid_fibrils"
            sample_prep = "negative staining with 2% uranyl acetate"
        elif beta_content > 0.4:
            morphology = "short_fibrils_or_protofilaments"
            sample_prep = "negative staining with 2% phosphotungstic acid"
        else:
            morphology = "amorphous_aggregates"
            sample_prep = "cryo-TEM or negative staining"
        
        # AFM recommendation
        afm_recommended = aggregation_prop > 0.5  # AFM good for fibrillar structures
        
        return {
            "predicted_morphology": morphology,
            "tem_sample_prep": sample_prep,
            "afm_recommended": afm_recommended,
            "sample_concentration": "10-50 μM",
            "incubation_time": "24-72 hours",
            "grid_preparation": "carbon-coated copper grids",
            "staining_time": "1-2 minutes"
        }
    
    def generate_protocol_for_candidate(self, candidate: Dict[str, Any]) -> ExperimentalProtocol:
        """Generate complete experimental protocol for a candidate"""
        
        sequence = candidate["sequence"]
        candidate_id = candidate.get("id", candidate.get("name", "unknown"))
        
        # Calculate molecular properties
        mw, net_charge = self.calculate_molecular_properties(sequence)
        
        # Generate protocols for each technique
        cd_params = self.generate_cd_protocol(candidate)
        tht_params = self.generate_tht_protocol(candidate)
        nmr_params = self.generate_nmr_protocol(candidate)
        microscopy_params = self.generate_microscopy_protocol(candidate)
        
        protocol = ExperimentalProtocol(
            candidate_id=candidate_id,
            sequence=sequence,
            molecular_weight=mw,
            net_charge=net_charge,
            cd_peptide_length=cd_params["peptide_length"],
            cd_buffer=cd_params["buffer"],
            cd_pathlength=cd_params["pathlength_mm"],
            cd_concentration=cd_params["concentration_uM"],
            cd_expected_beta_content=cd_params["expected_beta_content"],
            cd_expected_helix_content=cd_params["expected_helix_content"],
            cd_confidence_interval=cd_params["confidence_interval"],
            tht_concentrations=tht_params["concentrations_uM"],
            tht_agitation=tht_params["agitation"],
            tht_timecourse_hours=tht_params["timecourse_hours"],
            tht_predicted_class=tht_params["predicted_class"],
            tht_confidence_interval=tht_params["confidence_interval"],
            nmr_target_chemical_shifts=nmr_params["target_chemical_shifts"],
            nmr_uncertainty_hotspots=nmr_params["uncertainty_hotspots"],
            nmr_recommended_experiments=nmr_params["recommended_experiments"],
            tem_predicted_morphology=microscopy_params["predicted_morphology"],
            tem_sample_prep=microscopy_params["tem_sample_prep"],
            afm_recommended=microscopy_params["afm_recommended"]
        )
        
        self.protocols.append(protocol)
        return protocol
    
    def generate_protocol_pdf_content(self, protocol: ExperimentalProtocol) -> str:
        """Generate one-page PDF content for a candidate (as markdown)"""
        
        content = f"""# Experimental Protocol: {protocol.candidate_id}

## Candidate Information
- **Sequence**: `{protocol.sequence}`
- **Length**: {len(protocol.sequence)} residues
- **Molecular Weight**: {protocol.molecular_weight:.1f} Da
- **Net Charge (pH 7.0)**: {protocol.net_charge:+.1f}

## 🔬 CD Spectroscopy Protocol

### Parameters
- **Buffer**: {protocol.cd_buffer}
- **Pathlength**: {protocol.cd_pathlength} mm
- **Concentration**: {protocol.cd_concentration} μM
- **Scan range**: 190-250 nm
- **Temperature**: 25°C

### Expected Results
- **β-sheet content**: {protocol.cd_expected_beta_content:.1%} ± {(protocol.cd_confidence_interval[1] - protocol.cd_confidence_interval[0])/2:.1%}
- **α-helix content**: {protocol.cd_expected_helix_content:.1%}

## 🧪 ThT Aggregation Assay

### Parameters
- **Concentrations**: {', '.join(map(str, protocol.tht_concentrations))} μM
- **Agitation**: {protocol.tht_agitation}
- **Timecourse**: {protocol.tht_timecourse_hours} hours
- **Buffer**: 20 mM Tris-HCl, pH 7.4, 150 mM NaCl
- **ThT concentration**: 20 μM

### Expected Results
- **Predicted class**: {protocol.tht_predicted_class}
- **Aggregation propensity**: {(protocol.tht_confidence_interval[0] + protocol.tht_confidence_interval[1])/2:.2f} ± {(protocol.tht_confidence_interval[1] - protocol.tht_confidence_interval[0])/2:.2f}

## 🧲 NMR Quick Check

### Recommended Experiments
{chr(10).join(f"- {exp}" for exp in protocol.nmr_recommended_experiments)}

### Key Residues to Monitor
- **Uncertainty hotspots**: Residues {', '.join(map(str, protocol.nmr_uncertainty_hotspots))}
- **Target chemical shifts**: {len(protocol.nmr_target_chemical_shifts)} key protons identified

### Sample Conditions
- **Concentration**: 0.5-1.0 mM
- **Buffer**: 20 mM phosphate, pH 6.5, 50 mM NaCl, 10% D₂O
- **Temperature**: 298 K

## 🔬 TEM/AFM Microscopy

### TEM Protocol
- **Predicted morphology**: {protocol.tem_predicted_morphology}
- **Sample preparation**: {protocol.tem_sample_prep}
- **Sample concentration**: 10-50 μM
- **Incubation time**: 24-72 hours

### AFM Recommendation
- **AFM recommended**: {'✅ Yes' if protocol.afm_recommended else '❌ No'}

## 📋 Experimental Checklist

### Pre-synthesis
- [ ] Verify peptide synthesis feasibility
- [ ] Check for disulfide bonds (Cys residues)
- [ ] Plan purification strategy (RP-HPLC)

### Characterization
- [ ] MALDI-TOF mass spectrometry confirmation
- [ ] Analytical RP-HPLC purity check (>95%)
- [ ] Lyophilization and storage at -20°C

### Experimental execution
- [ ] CD spectroscopy (secondary structure)
- [ ] ThT aggregation kinetics
- [ ] NMR structural validation
- [ ] Electron microscopy (if aggregation observed)

---
*Protocol generated by Field of Truth Protein Folding Framework*
*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        return content
    
    def export_protocols_csv(self, output_file: Path = Path("experimental_protocols.csv")):
        """Export all protocols to CSV format"""
        
        if not self.protocols:
            print("❌ No protocols generated")
            return
        
        # Define CSV fields
        fieldnames = [
            "candidate_id", "sequence", "length", "molecular_weight", "net_charge",
            "cd_buffer", "cd_pathlength_mm", "cd_concentration_uM", 
            "cd_expected_beta", "cd_expected_helix",
            "tht_concentrations", "tht_agitation", "tht_timecourse_hours", "tht_predicted_class",
            "nmr_experiments", "nmr_uncertainty_hotspots", 
            "tem_morphology", "tem_sample_prep", "afm_recommended"
        ]
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for protocol in self.protocols:
                writer.writerow({
                    "candidate_id": protocol.candidate_id,
                    "sequence": protocol.sequence,
                    "length": len(protocol.sequence),
                    "molecular_weight": f"{protocol.molecular_weight:.1f}",
                    "net_charge": f"{protocol.net_charge:+.1f}",
                    "cd_buffer": protocol.cd_buffer,
                    "cd_pathlength_mm": protocol.cd_pathlength,
                    "cd_concentration_uM": protocol.cd_concentration,
                    "cd_expected_beta": f"{protocol.cd_expected_beta_content:.2f}",
                    "cd_expected_helix": f"{protocol.cd_expected_helix_content:.2f}",
                    "tht_concentrations": "; ".join(map(str, protocol.tht_concentrations)),
                    "tht_agitation": protocol.tht_agitation,
                    "tht_timecourse_hours": protocol.tht_timecourse_hours,
                    "tht_predicted_class": protocol.tht_predicted_class,
                    "nmr_experiments": "; ".join(protocol.nmr_recommended_experiments),
                    "nmr_uncertainty_hotspots": "; ".join(map(str, protocol.nmr_uncertainty_hotspots)),
                    "tem_morphology": protocol.tem_predicted_morphology,
                    "tem_sample_prep": protocol.tem_sample_prep,
                    "afm_recommended": protocol.afm_recommended
                })
        
        print(f"📊 Experimental protocols exported: {output_file}")

def main():
    """Generate wet-lab handoff protocols for top candidates"""
    
    print("🧪 WET-LAB HANDOFF GENERATOR")
    print("=" * 50)
    
    # Load top 5 candidates from postprocessing
    top5_file = Path("top5.fasta")
    shortlist_file = Path("discovery_shortlist.csv")
    
    if not shortlist_file.exists():
        print("❌ Error: discovery_shortlist.csv not found")
        print("   Run postprocess_discoveries.py first")
        return
    
    # Read shortlist to get top candidates
    candidates = []
    with open(shortlist_file, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i < 5:  # Top 5
                candidates.append({
                    "id": row["id"],
                    "sequence": row["sequence"],
                    "aggregation_propensity": float(row["aggregation_propensity"]),
                    "research_score": float(row["research_score"]),
                    "priority": float(row["priority"])
                })
    
    if not candidates:
        print("❌ No candidates found in shortlist")
        return
    
    print(f"🧬 Generating protocols for {len(candidates)} top candidates...")
    
    # Initialize generator
    generator = WetLabHandoffGenerator()
    
    # Generate protocols
    protocols_dir = Path("experimental_protocols")
    protocols_dir.mkdir(exist_ok=True)
    
    for i, candidate in enumerate(candidates, 1):
        protocol = generator.generate_protocol_for_candidate(candidate)
        
        # Generate protocol document
        content = generator.generate_protocol_pdf_content(protocol)
        protocol_file = protocols_dir / f"protocol_{i:02d}_{candidate['id']}.md"
        
        with open(protocol_file, 'w') as f:
            f.write(content)
        
        print(f"📄 Generated protocol {i}: {protocol_file}")
    
    # Export summary CSV
    generator.export_protocols_csv(protocols_dir / "protocols_summary.csv")
    
    print(f"\n✅ Wet-lab handoff complete!")
    print(f"📁 Protocols directory: {protocols_dir}")
    print(f"📊 Summary CSV: {protocols_dir}/protocols_summary.csv")
    
    # Show summary
    print(f"\n🎯 EXPERIMENTAL SUMMARY:")
    for i, protocol in enumerate(generator.protocols, 1):
        print(f"   {i}. {protocol.candidate_id}")
        print(f"      Sequence: {protocol.sequence[:30]}{'...' if len(protocol.sequence) > 30 else ''}")
        print(f"      MW: {protocol.molecular_weight:.0f} Da | Charge: {protocol.net_charge:+.0f}")
        print(f"      CD: {protocol.cd_concentration} μM | ThT: {protocol.tht_predicted_class}")
        print(f"      TEM: {protocol.tem_predicted_morphology}")
        print()

if __name__ == "__main__":
    main()

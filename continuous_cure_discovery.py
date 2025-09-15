#!/usr/bin/env python3
"""
Continuous Cure Discovery Engine

Runs continuously to find therapeutic targets using the scientifically rigorous
protein folding analysis. Uses ONLY the existing validated code.

This system:
1. Uses protein_folding_analysis.py (scientifically rigorous)
2. Uses fot/vqbit_mathematics.py (graph-based quantum framework)
3. Runs continuously with different parameters
4. Identifies therapeutic targets when found
5. Saves all discoveries for review

NO NEW MATHEMATICS - USES EXISTING VALIDATED CODE ONLY
"""

import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np

# Import our existing validated modules
import protein_folding_analysis as pfa
from fot.vqbit_mathematics import ProteinVQbitGraph

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContinuousCureDiscovery:
    """
    Continuous discovery engine using existing validated code
    
    Combines:
    - Rigorous molecular mechanics (protein_folding_analysis.py)
    - vQbit graph framework (fot/vqbit_mathematics.py)
    - Systematic parameter exploration
    - Therapeutic target identification
    """
    
    def __init__(self):
        self.sequence = "DAEFRHDSGYEVHHQKLVFFAEDVGSNKGAIIGLMVGGVVIA"  # Aβ42
        self.discoveries = []
        self.iteration_count = 0
        self.start_time = time.time()
        
        # Output directory
        self.output_dir = Path("continuous_discoveries")
        self.output_dir.mkdir(exist_ok=True)
        
        print("🔄 CONTINUOUS CURE DISCOVERY ENGINE")
        print("=" * 60)
        print("Using existing validated code:")
        print("• protein_folding_analysis.py - Rigorous molecular mechanics")
        print("• fot/vqbit_mathematics.py - Graph-based vQbit framework")
        print()
        print(f"Target sequence: {self.sequence}")
        print(f"Output directory: {self.output_dir}")
        print()
    
    def run_rigorous_analysis(self, temperature: float, n_samples: int) -> Dict[str, Any]:
        """Run the rigorous molecular mechanics analysis"""
        
        logger.info(f"Running rigorous analysis: T={temperature}K, samples={n_samples}")
        
        # Use the existing validated RigorousProteinFolder
        folder = pfa.RigorousProteinFolder(self.sequence, temperature=temperature)
        results = folder.run_folding_simulation(n_samples=n_samples)
        
        # Add experimental validation
        validation = pfa.validate_against_experimental_data(results, self.sequence)
        results['experimental_validation'] = validation
        
        return results
    
    def run_vqbit_analysis(self, max_iterations: int) -> Dict[str, Any]:
        """Run the vQbit graph-based analysis"""
        
        logger.info(f"Running vQbit analysis: iterations={max_iterations}")
        
        # Use the existing validated ProteinVQbitGraph
        vqbit_system = ProteinVQbitGraph(self.sequence, device="cpu")
        vqbit_system.initialize_vqbit_states()
        
        # Run optimization
        results = vqbit_system.run_fot_optimization(max_iterations=max_iterations)
        
        # Analyze conformations
        conformations = results['final_conformations']
        
        # Calculate secondary structure distribution
        structure_counts = {'alpha_helix': 0, 'beta_sheet': 0, 'extended': 0, 'left_handed': 0}
        for conf_data in conformations.values():
            struct_type = conf_data['conformation']['type']
            structure_counts[struct_type] += 1
        
        # Convert to fractions
        total = len(conformations)
        structure_fractions = {k: v/total for k, v in structure_counts.items()}
        
        results['structure_analysis'] = structure_fractions
        
        return results
    
    def identify_therapeutic_targets(self, rigorous_results: Dict[str, Any], 
                                   vqbit_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify therapeutic targets from combined analysis"""
        
        targets = []
        
        # Target 1: High β-sheet regions (aggregation risk)
        rigorous_beta = rigorous_results['structure_analysis']['sheet']
        vqbit_beta = vqbit_results['structure_analysis']['beta_sheet']
        
        if rigorous_beta > 0.3 and vqbit_beta > 0.3:  # Both methods agree on high β-sheet
            targets.append({
                'target_type': 'aggregation_inhibitor',
                'target_name': 'Beta_Sheet_Aggregation_Sites',
                'rigorous_beta_content': rigorous_beta,
                'vqbit_beta_content': vqbit_beta,
                'therapeutic_strategy': 'small_molecule_inhibitor',
                'priority': 'high' if rigorous_beta > 0.4 else 'medium'
            })
        
        # Target 2: High aggregation propensity
        aggregation_prop = rigorous_results['aggregation_propensity']
        
        if aggregation_prop > 0.4:
            targets.append({
                'target_type': 'aggregation_prevention',
                'target_name': 'High_Aggregation_Propensity_Regions',
                'aggregation_score': aggregation_prop,
                'therapeutic_strategy': 'conformational_stabilizer',
                'priority': 'high' if aggregation_prop > 0.6 else 'medium'
            })
        
        # Target 3: Energetically unstable regions (high energy conformations)
        if rigorous_results['best_energy'] > 5.0:  # Unusually high energy
            targets.append({
                'target_type': 'energy_stabilization',
                'target_name': 'High_Energy_Conformations',
                'energy': rigorous_results['best_energy'],
                'therapeutic_strategy': 'chaperone_mimetic',
                'priority': 'medium'
            })
        
        # Target 4: vQbit virtue deficiencies (low virtue scores)
        conformations = vqbit_results['final_conformations']
        low_virtue_residues = []
        
        for res_id, conf_data in conformations.items():
            avg_virtue = np.mean(list(conf_data['virtue_scores'].values()))
            if avg_virtue < 15.0:  # Low virtue threshold
                low_virtue_residues.append(res_id)
        
        if len(low_virtue_residues) > 5:  # Significant number of low-virtue residues
            targets.append({
                'target_type': 'virtue_enhancement',
                'target_name': 'Low_Virtue_Residue_Clusters',
                'affected_residues': low_virtue_residues,
                'therapeutic_strategy': 'targeted_peptide_therapy',
                'priority': 'medium'
            })
        
        return targets
    
    def evaluate_discovery_significance(self, targets: List[Dict[str, Any]], 
                                      rigorous_results: Dict[str, Any],
                                      vqbit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if discoveries are significant enough to be therapeutic"""
        
        evaluation = {
            'significant_discovery': False,
            'target_count': len(targets),
            'high_priority_targets': 0,
            'validation_score': 0.0,
            'significance_metrics': {}
        }
        
        # Count high-priority targets
        high_priority = [t for t in targets if t.get('priority') == 'high']
        evaluation['high_priority_targets'] = len(high_priority)
        
        # Validation score from rigorous analysis
        validation = rigorous_results.get('experimental_validation', {})
        validation_passes = sum(1 for v in validation.values() if v)
        validation_total = len(validation)
        evaluation['validation_score'] = validation_passes / validation_total if validation_total > 0 else 0
        
        # Significance metrics
        evaluation['significance_metrics'] = {
            'beta_sheet_agreement': abs(rigorous_results['structure_analysis']['sheet'] - 
                                      vqbit_results['structure_analysis']['beta_sheet']),
            'aggregation_propensity': rigorous_results['aggregation_propensity'],
            'energy_stability': rigorous_results['best_energy'],
            'fot_value': vqbit_results['final_fot_value']
        }
        
        # Determine significance
        significance_criteria = [
            len(targets) >= 2,  # At least 2 therapeutic targets
            len(high_priority) >= 1,  # At least 1 high-priority target
            evaluation['validation_score'] >= 0.3,  # Some experimental validation
            rigorous_results['aggregation_propensity'] > 0.3  # Meaningful aggregation risk
        ]
        
        evaluation['significant_discovery'] = sum(significance_criteria) >= 3
        
        return evaluation
    
    def save_discovery(self, targets: List[Dict[str, Any]], 
                      rigorous_results: Dict[str, Any],
                      vqbit_results: Dict[str, Any],
                      evaluation: Dict[str, Any],
                      parameters: Dict[str, Any]) -> None:
        """Save discovery results"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        discovery_record = {
            'discovery_timestamp': datetime.now().isoformat(),
            'iteration': self.iteration_count,
            'runtime_hours': (time.time() - self.start_time) / 3600,
            'sequence': self.sequence,
            'parameters': parameters,
            'therapeutic_targets': targets,
            'rigorous_analysis': {
                'energy_statistics': {
                    'best_energy': rigorous_results['best_energy'],
                    'mean_energy': rigorous_results['mean_energy'],
                    'std_energy': rigorous_results['std_energy']
                },
                'structure_analysis': rigorous_results['structure_analysis'],
                'aggregation_propensity': rigorous_results['aggregation_propensity'],
                'experimental_validation': rigorous_results['experimental_validation']
            },
            'vqbit_analysis': {
                'final_fot_value': vqbit_results['final_fot_value'],
                'structure_analysis': vqbit_results['structure_analysis'],
                'iterations': vqbit_results['iterations'],
                'converged': vqbit_results['converged']
            },
            'significance_evaluation': evaluation
        }
        
        # Save to file
        if evaluation['significant_discovery']:
            filename = f"SIGNIFICANT_DISCOVERY_{timestamp}.json"
        else:
            filename = f"discovery_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        # Convert any non-serializable objects to strings
        def make_serializable(obj):
            if isinstance(obj, (bool, int, float, str, list, dict, type(None))):
                return obj
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif hasattr(obj, '__dict__'):
                return str(obj)
            else:
                return str(obj)
        
        # Recursively convert the discovery record
        def convert_dict(d):
            if isinstance(d, dict):
                return {k: convert_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [convert_dict(v) for v in d]
            else:
                return make_serializable(d)
        
        serializable_record = convert_dict(discovery_record)
        
        with open(filepath, 'w') as f:
            json.dump(serializable_record, f, indent=2)
        
        # Add to discoveries list
        self.discoveries.append(discovery_record)
        
        logger.info(f"Discovery saved: {filepath}")
    
    def run_single_iteration(self) -> bool:
        """Run single discovery iteration"""
        
        self.iteration_count += 1
        
        print(f"\n🔍 DISCOVERY ITERATION {self.iteration_count}")
        print(f"⏱️  Runtime: {(time.time() - self.start_time)/3600:.1f} hours")
        
        # Vary parameters for exploration
        # Temperature exploration (physiological range)
        temp_range = [298.15, 310.15, 320.15]  # Room temp, body temp, mild fever
        temperature = temp_range[self.iteration_count % len(temp_range)]
        
        # Sample size exploration
        sample_ranges = [500, 1000, 1500]
        n_samples = sample_ranges[self.iteration_count % len(sample_ranges)]
        
        # vQbit iteration exploration
        vqbit_iterations = [200, 500, 1000]
        max_iterations = vqbit_iterations[self.iteration_count % len(vqbit_iterations)]
        
        parameters = {
            'temperature': temperature,
            'n_samples': n_samples,
            'vqbit_iterations': max_iterations
        }
        
        print(f"Parameters: T={temperature}K, samples={n_samples}, vQbit_iter={max_iterations}")
        
        try:
            # Run rigorous analysis
            print("🔬 Running rigorous molecular mechanics...")
            rigorous_results = self.run_rigorous_analysis(temperature, n_samples)
            
            # Run vQbit analysis
            print("⚛️  Running vQbit graph analysis...")
            vqbit_results = self.run_vqbit_analysis(max_iterations)
            
            # Identify therapeutic targets
            print("🎯 Identifying therapeutic targets...")
            targets = self.identify_therapeutic_targets(rigorous_results, vqbit_results)
            
            # Evaluate significance
            evaluation = self.evaluate_discovery_significance(targets, rigorous_results, vqbit_results)
            
            # Report results
            print(f"🎯 Targets found: {len(targets)} ({evaluation['high_priority_targets']} high-priority)")
            print(f"📊 Validation score: {evaluation['validation_score']:.1%}")
            print(f"🧬 β-sheet content: {rigorous_results['structure_analysis']['sheet']:.1%}")
            print(f"⚡ Aggregation risk: {rigorous_results['aggregation_propensity']:.3f}")
            
            if evaluation['significant_discovery']:
                print("🎉 SIGNIFICANT THERAPEUTIC DISCOVERY!")
            else:
                print("📝 Discovery logged, continuing search...")
            
            # Save discovery
            self.save_discovery(targets, rigorous_results, vqbit_results, evaluation, parameters)
            
            return evaluation['significant_discovery']
            
        except Exception as e:
            logger.error(f"Iteration {self.iteration_count} failed: {e}")
            return False
    
    def run_continuous_discovery(self, max_iterations: int = None, 
                                max_runtime_hours: float = None) -> None:
        """Run continuous discovery until significant findings or limits reached"""
        
        print("🚀 Starting continuous discovery...")
        print(f"Will run until significant discovery found")
        if max_iterations:
            print(f"Maximum iterations: {max_iterations}")
        if max_runtime_hours:
            print(f"Maximum runtime: {max_runtime_hours} hours")
        print()
        
        significant_found = False
        
        while not significant_found:
            
            # Check limits
            if max_iterations and self.iteration_count >= max_iterations:
                print(f"⏱️  Reached maximum iterations ({max_iterations})")
                break
            
            if max_runtime_hours and (time.time() - self.start_time) / 3600 >= max_runtime_hours:
                print(f"⏱️  Reached maximum runtime ({max_runtime_hours} hours)")
                break
            
            # Run iteration
            significant_found = self.run_single_iteration()
            
            # Brief pause between iterations
            time.sleep(1)
        
        # Final summary
        print("\n🏁 CONTINUOUS DISCOVERY COMPLETE")
        print("=" * 60)
        
        runtime_hours = (time.time() - self.start_time) / 3600
        print(f"⏱️  Total runtime: {runtime_hours:.1f} hours")
        print(f"🔄 Total iterations: {self.iteration_count}")
        print(f"📁 Discoveries saved: {len(self.discoveries)}")
        
        significant_discoveries = [d for d in self.discoveries if d['significance_evaluation']['significant_discovery']]
        print(f"🎯 Significant discoveries: {len(significant_discoveries)}")
        
        if significant_discoveries:
            print("\n🎉 THERAPEUTIC TARGETS DISCOVERED:")
            for i, discovery in enumerate(significant_discoveries, 1):
                targets = discovery['therapeutic_targets']
                print(f"   {i}. {len(targets)} targets at iteration {discovery['iteration']}")
                for target in targets:
                    print(f"      - {target['target_name']} ({target['priority']} priority)")
        
        print(f"\n📁 All results saved in: {self.output_dir}")


def main():
    """Run continuous cure discovery"""
    
    # Create discovery engine
    engine = ContinuousCureDiscovery()
    
    # Ask user for parameters
    print("🔄 CONTINUOUS CURE DISCOVERY")
    print("This will run until therapeutic targets are found.")
    print()
    
    try:
        max_hours = input("Maximum runtime (hours, or Enter for unlimited): ")
        max_hours = float(max_hours) if max_hours.strip() else None
        
        max_iter = input("Maximum iterations (or Enter for unlimited): ")
        max_iter = int(max_iter) if max_iter.strip() else None
        
    except (ValueError, KeyboardInterrupt):
        print("Using default settings: unlimited runtime, 100 max iterations")
        max_hours = None
        max_iter = 100
    
    print()
    print("🚀 Starting discovery engine...")
    print("Press Ctrl+C to stop early")
    print()
    
    try:
        engine.run_continuous_discovery(max_iterations=max_iter, max_runtime_hours=max_hours)
    except KeyboardInterrupt:
        print("\n⏹️  Discovery stopped by user")
        print(f"📊 Completed {engine.iteration_count} iterations")
        print(f"📁 Results saved in: {engine.output_dir}")


if __name__ == "__main__":
    main()

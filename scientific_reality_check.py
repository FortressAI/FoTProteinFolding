#!/usr/bin/env python3
"""
Scientific Reality Check Module

This module enforces scientific realism by validating computational models
against known experimental data BEFORE allowing any discovery runs.

The agent is NOT ALLOWED to search for "cures" until it can accurately
reproduce basic experimental facts about Aβ42.
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from protein_folding_analysis import RigorousProteinFolder
# from fot.experimental_integration import ExperimentalDataIntegrator  # Not needed for basic reality check

logger = logging.getLogger(__name__)

@dataclass
class ExperimentalBenchmark:
    """Represents a known experimental fact that must be reproduced"""
    name: str
    measurement_type: str  # 'secondary_structure', 'energy', 'aggregation', etc.
    expected_value: float
    expected_range: Tuple[float, float]  # (min, max) acceptable range
    experimental_source: str
    validation_weight: float = 1.0

@dataclass
class RealityCheckResult:
    """Results of scientific reality validation"""
    benchmark_name: str
    predicted_value: float
    expected_value: float
    expected_range: Tuple[float, float]
    passes_validation: bool
    deviation_magnitude: float
    experimental_source: str

class ScientificRealityChecker:
    """
    Enforces scientific realism by validating against experimental benchmarks.
    
    This is the gatekeeper that prevents the agent from making up results.
    NO discovery runs are allowed until this validation passes.
    """
    
    def __init__(self, sequence: str):
        self.sequence = sequence
        self.experimental_benchmarks = self._define_experimental_benchmarks()
        self.reality_check_passed = False
        self.last_validation_results = []
        
    def _define_experimental_benchmarks(self) -> List[ExperimentalBenchmark]:
        """
        Define the known experimental facts about Aβ42 that MUST be reproduced.
        
        These are non-negotiable scientific truths from real experiments.
        """
        
        return [
            # Secondary structure benchmarks from NMR/CD studies
            ExperimentalBenchmark(
                name="alpha_helix_content",
                measurement_type="secondary_structure", 
                expected_value=5.0,  # ~5% alpha helix in solution
                expected_range=(0.0, 10.0),  # Must be <10%
                experimental_source="Kirkitadze et al. (2001) J Mol Biol, Vivekanandan et al. (2011) Biochem Biophys Res Commun",
                validation_weight=2.0  # Critical benchmark
            ),
            
            ExperimentalBenchmark(
                name="beta_sheet_content",
                measurement_type="secondary_structure",
                expected_value=15.0,  # ~15% beta sheet in monomeric form
                expected_range=(5.0, 30.0),  # Some variation acceptable
                experimental_source="Kirkitadze et al. (2001), Crescenzi et al. (2002) Eur J Biochem",
                validation_weight=1.5
            ),
            
            ExperimentalBenchmark(
                name="disorder_content", 
                measurement_type="secondary_structure",
                expected_value=75.0,  # ~75% disordered/random coil
                expected_range=(60.0, 85.0),  # Intrinsically disordered
                experimental_source="Multiple CD/NMR studies consensus",
                validation_weight=2.0  # Critical benchmark
            ),
            
            # Energy scale benchmarks
            ExperimentalBenchmark(
                name="total_energy_per_residue",
                measurement_type="energy",
                expected_value=-8.0,  # ~-8 kcal/mol per residue
                expected_range=(-12.0, -5.0),  # Reasonable protein range
                experimental_source="Thermodynamic protein folding literature",
                validation_weight=1.0
            ),
            
            # Aggregation benchmarks
            ExperimentalBenchmark(
                name="aggregation_propensity",
                measurement_type="aggregation",
                expected_value=0.3,  # Moderate aggregation propensity for monomer
                expected_range=(0.2, 0.5),  # Not extremely high in monomeric form
                experimental_source="Aggregation kinetics studies",
                validation_weight=1.0
            )
        ]
    
    def run_reality_check(self, n_samples: int = 500) -> Tuple[bool, List[RealityCheckResult]]:
        """
        Run the scientific reality check.
        
        Returns:
            Tuple of (passes_all_checks, detailed_results)
            
        The agent is FORBIDDEN from running discovery until this returns True.
        """
        
        logger.info("🔬 ENFORCING SCIENTIFIC REALISM")
        logger.info("=" * 60)
        logger.info("Validating computational model against experimental benchmarks...")
        logger.info("⚠️  NO DISCOVERY RUNS ALLOWED UNTIL VALIDATION PASSES")
        
        # Run computational simulation
        folder = RigorousProteinFolder(self.sequence, temperature=298.15)
        results = folder.run_folding_simulation(n_samples=n_samples)
        
        validation_results = []
        
        # Check each benchmark
        for benchmark in self.experimental_benchmarks:
            result = self._validate_benchmark(benchmark, results)
            validation_results.append(result)
            
            status = "✅ PASS" if result.passes_validation else "❌ FAIL"
            logger.info(f"{benchmark.name}: {status}")
            logger.info(f"   Predicted: {result.predicted_value:.1f}")
            logger.info(f"   Expected: {result.expected_value:.1f} ({result.expected_range[0]:.1f}-{result.expected_range[1]:.1f})")
            logger.info(f"   Source: {result.experimental_source}")
            
            if not result.passes_validation:
                logger.warning(f"   ⚠️  DEVIATION: {result.deviation_magnitude:.1f} units from expected range")
        
        # Calculate overall pass rate
        total_checks = len(validation_results)
        passed_checks = sum(1 for r in validation_results if r.passes_validation)
        critical_checks = [r for r in validation_results if any(b.validation_weight > 1.5 for b in self.experimental_benchmarks if b.name == r.benchmark_name)]
        critical_passed = sum(1 for r in critical_checks if r.passes_validation)
        
        # Require ALL critical checks to pass + 80% of others
        overall_pass = (critical_passed == len(critical_checks) and 
                       passed_checks / total_checks >= 0.8)
        
        self.reality_check_passed = overall_pass
        self.last_validation_results = validation_results
        
        logger.info("=" * 60)
        logger.info(f"📊 REALITY CHECK SUMMARY:")
        logger.info(f"   Total checks: {total_checks}")
        logger.info(f"   Passed: {passed_checks} ({passed_checks/total_checks:.1%})")
        logger.info(f"   Critical passed: {critical_passed}/{len(critical_checks)}")
        
        if overall_pass:
            logger.info("✅ SCIENTIFIC REALITY CHECK PASSED")
            logger.info("   🔓 Discovery runs are now AUTHORIZED")
        else:
            logger.error("❌ SCIENTIFIC REALITY CHECK FAILED")
            logger.error("   🔒 Discovery runs are FORBIDDEN until model is fixed")
            logger.error("   🔧 FIX THE MODEL BEFORE CLAIMING TO FIND CURES")
        
        return overall_pass, validation_results
    
    def _validate_benchmark(self, benchmark: ExperimentalBenchmark, 
                          simulation_results: Dict[str, Any]) -> RealityCheckResult:
        """Validate a single experimental benchmark"""
        
        # Extract predicted value based on benchmark type
        if benchmark.measurement_type == "secondary_structure":
            if benchmark.name == "alpha_helix_content":
                predicted = simulation_results['structure_analysis']['helix'] * 100
            elif benchmark.name == "beta_sheet_content":
                predicted = simulation_results['structure_analysis']['sheet'] * 100
            elif benchmark.name == "disorder_content":
                predicted = (simulation_results['structure_analysis']['extended'] + 
                           simulation_results['structure_analysis']['other']) * 100
            else:
                predicted = 0.0
                
        elif benchmark.measurement_type == "energy":
            if benchmark.name == "total_energy_per_residue":
                predicted = simulation_results['best_energy'] / len(self.sequence)
            else:
                predicted = simulation_results['best_energy']
                
        elif benchmark.measurement_type == "aggregation":
            predicted = simulation_results['aggregation_propensity']
            
        else:
            predicted = 0.0
        
        # Check if within acceptable range
        in_range = (benchmark.expected_range[0] <= predicted <= benchmark.expected_range[1])
        
        # Calculate deviation magnitude
        if predicted < benchmark.expected_range[0]:
            deviation = benchmark.expected_range[0] - predicted
        elif predicted > benchmark.expected_range[1]:
            deviation = predicted - benchmark.expected_range[1]
        else:
            deviation = 0.0
        
        return RealityCheckResult(
            benchmark_name=benchmark.name,
            predicted_value=predicted,
            expected_value=benchmark.expected_value,
            expected_range=benchmark.expected_range,
            passes_validation=in_range,
            deviation_magnitude=deviation,
            experimental_source=benchmark.experimental_source
        )
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Generate detailed validation report"""
        
        if not self.last_validation_results:
            return {"error": "No validation has been run"}
        
        return {
            "reality_check_passed": self.reality_check_passed,
            "validation_summary": {
                "total_benchmarks": len(self.last_validation_results),
                "passed_benchmarks": sum(1 for r in self.last_validation_results if r.passes_validation),
                "failed_benchmarks": sum(1 for r in self.last_validation_results if not r.passes_validation),
                "pass_rate": sum(1 for r in self.last_validation_results if r.passes_validation) / len(self.last_validation_results)
            },
            "detailed_results": [
                {
                    "benchmark": r.benchmark_name,
                    "predicted": r.predicted_value,
                    "expected": r.expected_value,
                    "range": r.expected_range,
                    "passes": r.passes_validation,
                    "deviation": r.deviation_magnitude,
                    "source": r.experimental_source
                }
                for r in self.last_validation_results
            ],
            "authorization_status": {
                "discovery_runs_authorized": self.reality_check_passed,
                "message": ("Model validated against experimental data - discovery authorized" 
                          if self.reality_check_passed 
                          else "Model fails experimental validation - discovery FORBIDDEN")
            }
        }

def enforce_reality_check(sequence: str, min_samples: int = 500) -> bool:
    """
    Convenience function to enforce reality check.
    
    Returns True only if the model passes experimental validation.
    Discovery runs should call this first and exit if it returns False.
    """
    
    checker = ScientificRealityChecker(sequence)
    passed, results = checker.run_reality_check(min_samples)
    
    if not passed:
        print("🚨 REALITY CHECK FAILED - DISCOVERY RUNS FORBIDDEN")
        print("🔧 Fix the computational model before searching for cures!")
        
    return passed

if __name__ == "__main__":
    # Test with Aβ42
    ab42_sequence = 'DAEFRHDSGYEVHHQKLVFFAEDVGSNKGAIIGLMVGGVVIA'
    
    print("🔬 Testing Scientific Reality Check")
    print("=" * 50)
    
    success = enforce_reality_check(ab42_sequence, min_samples=200)
    
    if success:
        print("✅ Model validated - ready for scientific discovery")
    else:
        print("❌ Model invalid - fix before proceeding")

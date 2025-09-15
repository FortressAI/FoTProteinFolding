#!/usr/bin/env python3
"""
Large-Scale Scientific Discovery System

This system runs rigorous scientific discovery at scale across multiple sequences,
continuing until novel discoveries are found. It maintains a database of known
sequences for validation and focuses computational resources on finding new insights.
"""

import json
import logging
import multiprocessing as mp
import random
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass

from rigorous_scientific_discovery import run_rigorous_discovery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SequenceTarget:
    """Represents a sequence target for discovery"""
    sequence: str
    name: str
    known_properties: Dict[str, Any]
    validation_category: str  # 'known', 'novel', 'validation'
    priority: int  # 1=highest, 5=lowest

@dataclass
class DiscoveryResult:
    """Represents a discovery result"""
    sequence: str
    sequence_name: str
    scientific_verdict: str
    confidence_level: str
    rigor_score: float
    novel_findings: List[str]
    validation_status: str
    timestamp: str

class LargeScaleDiscoveryEngine:
    """
    Large-scale discovery engine that runs until novel discoveries are found.
    
    Features:
    - Multi-sequence processing with parallel execution
    - Known sequence validation database
    - Novel discovery detection and prioritization
    - Continuous operation until discoveries found
    - Resource-aware scaling
    """
    
    def __init__(self, output_dir: str = "large_scale_discoveries"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.known_sequences_db = self._initialize_known_sequences()
        self.discovered_sequences = set()
        self.validation_results = []
        self.novel_discoveries = []
        
        # Discovery criteria
        self.min_rigor_score = 0.7
        self.required_novel_discoveries = 3
        self.max_parallel_workers = min(8, mp.cpu_count())
        
    def _initialize_known_sequences(self) -> List[SequenceTarget]:
        """Initialize database of known sequences for validation"""
        
        known_sequences = [
            # Amyloid-beta variants (known pathological)
            SequenceTarget(
                sequence='DAEFRHDSGYEVHHQKLVFFAEDVGSNKGAIIGLMVGGVVIA',  # Aβ42
                name='Amyloid_beta_42',
                known_properties={
                    'pathological': True,
                    'aggregation_prone': True,
                    'helix_content_max': 0.10,
                    'disorder_content': 0.75,
                    'clinical_relevance': 'Alzheimer_disease'
                },
                validation_category='known',
                priority=1
            ),
            SequenceTarget(
                sequence='DAEFRHDSGYEVHHQKLVFFAEDVGSNKGAIIGLMVGGVV',  # Aβ40
                name='Amyloid_beta_40',
                known_properties={
                    'pathological': True,
                    'aggregation_prone': True,
                    'less_toxic_than_ab42': True,
                    'clinical_relevance': 'Alzheimer_disease'
                },
                validation_category='known',
                priority=1
            ),
            
            # Alpha-synuclein variants (known pathological)
            SequenceTarget(
                sequence='MDVFMKGLSKAKEGVVAAAEKTKQGVAEAAGKTKEGVLYVGSKTKEGVVHGVATVAEKTKEQVTNVGGAVVTGVTAVAQKTVEGAGSIAAATGFVKKDQLGKNEEGAPQEGILEDMPVDPDNEAYEMPSEEGYQDYEPEA',
                name='Alpha_synuclein_full',
                known_properties={
                    'pathological': True,
                    'aggregation_prone': True,
                    'clinical_relevance': 'Parkinsons_disease',
                    'intrinsically_disordered': True
                },
                validation_category='known',
                priority=1
            ),
            
            # Tau protein segments (known pathological)
            SequenceTarget(
                sequence='VQIINKKLDLSNVQSKCGSKDNIKHVPGGGS',  # Tau repeat region
                name='Tau_repeat_R2',
                known_properties={
                    'pathological': True,
                    'aggregation_prone': True,
                    'clinical_relevance': 'Alzheimer_tauopathy',
                    'microtubule_binding': True
                },
                validation_category='known',
                priority=2
            ),
            
            # Prion protein segments (known pathological)
            SequenceTarget(
                sequence='PHGGGWGQPHGGGWGQPHGGGWGQPHGGGWGQGGGTHSQWNKPSKPKTNMKHMAGAAAAGAVVGGLGGYMLGSAMSRP',
                name='Prion_protein_segment',
                known_properties={
                    'pathological': True,
                    'aggregation_prone': True,
                    'clinical_relevance': 'Prion_diseases',
                    'beta_sheet_conversion': True
                },
                validation_category='known',
                priority=2
            ),
            
            # Non-pathological controls (should NOT aggregate)
            SequenceTarget(
                sequence='MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKREAA',
                name='Ubiquitin_control',
                known_properties={
                    'pathological': False,
                    'aggregation_prone': False,
                    'well_folded': True,
                    'clinical_relevance': 'Control_protein'
                },
                validation_category='validation',
                priority=3
            ),
        ]
        
        return known_sequences
    
    def generate_novel_sequences(self, n_sequences: int = 50) -> List[SequenceTarget]:
        """Generate novel sequences for discovery"""
        
        logger.info(f"🧬 Generating {n_sequences} novel sequences for discovery...")
        
        novel_sequences = []
        
        # Strategy 1: Variations of known pathological sequences
        base_sequences = [seq for seq in self.known_sequences_db if seq.known_properties.get('pathological', False)]
        
        for i in range(n_sequences // 3):
            base_seq = random.choice(base_sequences)
            variant = self._create_sequence_variant(base_seq.sequence)
            
            novel_sequences.append(SequenceTarget(
                sequence=variant,
                name=f"Novel_variant_{i+1}",
                known_properties={'source': f'variant_of_{base_seq.name}'},
                validation_category='novel',
                priority=2
            ))
        
        # Strategy 2: Random aggregation-prone sequences
        for i in range(n_sequences // 3):
            random_seq = self._generate_aggregation_prone_sequence(random.randint(20, 50))
            
            novel_sequences.append(SequenceTarget(
                sequence=random_seq,
                name=f"Random_aggregation_{i+1}",
                known_properties={'generation_method': 'aggregation_prone_design'},
                validation_category='novel',
                priority=3
            ))
        
        # Strategy 3: Completely random sequences
        for i in range(n_sequences - len(novel_sequences)):
            random_seq = self._generate_random_sequence(random.randint(15, 60))
            
            novel_sequences.append(SequenceTarget(
                sequence=random_seq,
                name=f"Random_sequence_{i+1}",
                known_properties={'generation_method': 'random'},
                validation_category='novel',
                priority=4
            ))
        
        logger.info(f"✅ Generated {len(novel_sequences)} novel sequences")
        return novel_sequences
    
    def _create_sequence_variant(self, base_sequence: str) -> str:
        """Create a variant of a known sequence with mutations"""
        
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        sequence = list(base_sequence)
        
        # Make 1-5 random mutations
        n_mutations = random.randint(1, min(5, len(sequence) // 8))
        
        for _ in range(n_mutations):
            pos = random.randint(0, len(sequence) - 1)
            sequence[pos] = random.choice(amino_acids)
        
        return ''.join(sequence)
    
    def _generate_aggregation_prone_sequence(self, length: int) -> str:
        """Generate sequence with high aggregation propensity"""
        
        # Amino acids with high beta-sheet propensity
        high_beta = 'FIVLMYW'  # Hydrophobic, aromatic
        medium_beta = 'TNQH'    # Can form beta-sheets
        low_beta = 'GSPADE'     # Beta-breakers
        
        sequence = []
        for i in range(length):
            if i % 4 == 0:  # 25% beta-breakers for realism
                sequence.append(random.choice(low_beta))
            elif i % 3 == 0:  # ~33% medium beta
                sequence.append(random.choice(medium_beta))
            else:  # ~42% high beta
                sequence.append(random.choice(high_beta))
        
        return ''.join(sequence)
    
    def _generate_random_sequence(self, length: int) -> str:
        """Generate completely random sequence"""
        
        amino_acids = 'ACDEFGHIKLMNPQRSTVWY'
        return ''.join(random.choice(amino_acids) for _ in range(length))
    
    def run_large_scale_discovery(self, max_sequences: int = 100, 
                                max_runtime_hours: int = 24) -> Dict[str, Any]:
        """
        Run large-scale discovery until novel findings are discovered.
        
        Args:
            max_sequences: Maximum number of sequences to test
            max_runtime_hours: Maximum runtime in hours
            
        Returns:
            Dictionary with discovery results and statistics
        """
        
        logger.info("🚀 INITIATING LARGE-SCALE SCIENTIFIC DISCOVERY")
        logger.info("=" * 70)
        logger.info(f"Target: Find {self.required_novel_discoveries} novel discoveries")
        logger.info(f"Max sequences: {max_sequences}")
        logger.info(f"Max runtime: {max_runtime_hours} hours")
        logger.info(f"Parallel workers: {self.max_parallel_workers}")
        logger.info(f"Min rigor score: {self.min_rigor_score}")
        
        start_time = time.time()
        max_runtime_seconds = max_runtime_hours * 3600
        
        # Phase 1: Validate system on known sequences
        logger.info("\n🧪 PHASE 1: VALIDATION ON KNOWN SEQUENCES")
        validation_results = self._run_validation_phase()
        
        if not self._validation_passed(validation_results):
            logger.error("❌ VALIDATION FAILED - stopping discovery")
            return self._generate_failure_report("validation_failed", validation_results)
        
        logger.info("✅ Validation passed - system is working correctly")
        
        # Phase 2: Discovery on novel sequences
        logger.info("\n🔍 PHASE 2: NOVEL SEQUENCE DISCOVERY")
        
        sequences_processed = 0
        discovery_batch_size = 20
        
        while (len(self.novel_discoveries) < self.required_novel_discoveries and 
               sequences_processed < max_sequences and
               time.time() - start_time < max_runtime_seconds):
            
            # Generate batch of novel sequences
            remaining_sequences = min(discovery_batch_size, max_sequences - sequences_processed)
            novel_batch = self.generate_novel_sequences(remaining_sequences)
            
            logger.info(f"\n🔬 Processing batch {sequences_processed // discovery_batch_size + 1}")
            logger.info(f"   Sequences in batch: {len(novel_batch)}")
            logger.info(f"   Total processed: {sequences_processed}")
            logger.info(f"   Novel discoveries found: {len(self.novel_discoveries)}")
            
            # Process batch in parallel
            batch_results = self._process_sequence_batch(novel_batch)
            
            # Evaluate results for novel discoveries
            new_discoveries = self._evaluate_novel_discoveries(batch_results)
            self.novel_discoveries.extend(new_discoveries)
            
            sequences_processed += len(novel_batch)
            
            # Progress update
            elapsed_hours = (time.time() - start_time) / 3600
            logger.info(f"📊 PROGRESS UPDATE:")
            logger.info(f"   Runtime: {elapsed_hours:.1f}/{max_runtime_hours} hours")
            logger.info(f"   Sequences: {sequences_processed}/{max_sequences}")
            logger.info(f"   Novel discoveries: {len(self.novel_discoveries)}/{self.required_novel_discoveries}")
            
            if new_discoveries:
                logger.info("🎉 NEW DISCOVERIES FOUND!")
                for discovery in new_discoveries:
                    logger.info(f"   • {discovery.sequence_name}: {discovery.scientific_verdict}")
        
        # Generate final report
        total_runtime = time.time() - start_time
        return self._generate_discovery_report(
            validation_results, sequences_processed, total_runtime)
    
    def _run_validation_phase(self) -> List[DiscoveryResult]:
        """Run validation on known sequences"""
        
        validation_targets = [seq for seq in self.known_sequences_db 
                            if seq.validation_category in ['known', 'validation']]
        
        logger.info(f"Running validation on {len(validation_targets)} known sequences...")
        
        validation_results = self._process_sequence_batch(validation_targets)
        self.validation_results = validation_results
        
        return validation_results
    
    def _process_sequence_batch(self, sequences: List[SequenceTarget]) -> List[DiscoveryResult]:
        """Process a batch of sequences in parallel"""
        
        logger.info(f"🔄 Processing {len(sequences)} sequences with {self.max_parallel_workers} workers...")
        
        results = []
        
        with ProcessPoolExecutor(max_workers=self.max_parallel_workers) as executor:
            # Submit all jobs
            future_to_sequence = {
                executor.submit(self._process_single_sequence, seq): seq 
                for seq in sequences
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_sequence):
                sequence = future_to_sequence[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"✅ Completed: {sequence.name} - {result.scientific_verdict}")
                except Exception as e:
                    logger.error(f"❌ Failed: {sequence.name} - {str(e)}")
        
        return results
    
    def _process_single_sequence(self, sequence_target: SequenceTarget) -> DiscoveryResult:
        """Process a single sequence"""
        
        # Run rigorous scientific discovery
        discovery_result = run_rigorous_discovery(
            sequence=sequence_target.sequence,
            n_samples=500,  # Moderate sampling for speed
            output_dir=str(self.output_dir / "individual_results")
        )
        
        # Extract key information
        scientific_verdict = discovery_result['scientific_verdict']['overall_assessment']
        confidence_level = discovery_result['scientific_verdict']['confidence_level']
        rigor_score = discovery_result['scientific_verdict']['rigor_score']
        
        # Identify novel findings
        novel_findings = self._identify_novel_findings(discovery_result, sequence_target)
        
        # Determine validation status
        validation_status = self._determine_validation_status(discovery_result, sequence_target)
        
        return DiscoveryResult(
            sequence=sequence_target.sequence,
            sequence_name=sequence_target.name,
            scientific_verdict=scientific_verdict,
            confidence_level=confidence_level,
            rigor_score=rigor_score,
            novel_findings=novel_findings,
            validation_status=validation_status,
            timestamp=datetime.now().isoformat()
        )
    
    def _identify_novel_findings(self, discovery_result: Dict[str, Any], 
                               sequence_target: SequenceTarget) -> List[str]:
        """Identify novel findings in discovery result"""
        
        novel_findings = []
        
        # Check for high rigor discoveries
        if discovery_result['scientific_verdict']['rigor_score'] > self.min_rigor_score:
            novel_findings.append(f"High rigor score: {discovery_result['scientific_verdict']['rigor_score']:.2f}")
        
        # Check for survived hypotheses
        survived = discovery_result.get('detailed_results', {}).get('hypothesis_testing', {}).get('survived_falsification', 0)
        if survived > 0:
            novel_findings.append(f"Hypotheses survived falsification: {survived}")
        
        # Check for unexpected properties
        if sequence_target.validation_category == 'novel':
            # Any successful discovery on novel sequence is potentially novel
            if discovery_result['scientific_verdict']['overall_assessment'] not in ['SCIENTIFICALLY INVALID', 'EXPERIMENTALLY INCONSISTENT']:
                novel_findings.append(f"Novel sequence shows: {discovery_result['scientific_verdict']['overall_assessment']}")
        
        return novel_findings
    
    def _determine_validation_status(self, discovery_result: Dict[str, Any], 
                                   sequence_target: SequenceTarget) -> str:
        """Determine if discovery validates against known properties"""
        
        if sequence_target.validation_category == 'known':
            # Check if results match known properties
            known_props = sequence_target.known_properties
            
            if known_props.get('pathological', False):
                # Should show aggregation tendency
                if 'aggregation' in discovery_result['scientific_verdict']['overall_assessment'].lower():
                    return "VALIDATES_KNOWN"
                else:
                    return "CONTRADICTS_KNOWN"
            else:
                # Should NOT show pathological properties
                if discovery_result['scientific_verdict']['overall_assessment'] in ['SCIENTIFICALLY INVALID', 'EXPERIMENTALLY INCONSISTENT']:
                    return "VALIDATES_KNOWN"
                else:
                    return "CONTRADICTS_KNOWN"
        
        elif sequence_target.validation_category == 'validation':
            # Control sequences - should behave predictably
            return "CONTROL_RESULT"
        
        else:
            # Novel sequences
            return "NOVEL_RESULT"
    
    def _validation_passed(self, validation_results: List[DiscoveryResult]) -> bool:
        """Check if validation phase passed"""
        
        known_results = [r for r in validation_results if 'known' in r.validation_status.lower()]
        
        if not known_results:
            return False
        
        validated_count = sum(1 for r in known_results if r.validation_status == "VALIDATES_KNOWN")
        validation_rate = validated_count / len(known_results)
        
        logger.info(f"📊 VALIDATION SUMMARY:")
        logger.info(f"   Known sequences tested: {len(known_results)}")
        logger.info(f"   Correctly validated: {validated_count}")
        logger.info(f"   Validation rate: {validation_rate:.1%}")
        
        # Require 70% validation rate
        return validation_rate >= 0.7
    
    def _evaluate_novel_discoveries(self, batch_results: List[DiscoveryResult]) -> List[DiscoveryResult]:
        """Evaluate batch results for novel discoveries"""
        
        novel_discoveries = []
        
        for result in batch_results:
            if (result.rigor_score > self.min_rigor_score and 
                result.novel_findings and
                result.validation_status == "NOVEL_RESULT" and
                result.scientific_verdict not in ['SCIENTIFICALLY INVALID', 'EXPERIMENTALLY INCONSISTENT']):
                
                novel_discoveries.append(result)
                logger.info(f"🌟 NOVEL DISCOVERY: {result.sequence_name}")
                logger.info(f"   Rigor: {result.rigor_score:.2f}")
                logger.info(f"   Findings: {', '.join(result.novel_findings)}")
        
        return novel_discoveries
    
    def _generate_discovery_report(self, validation_results: List[DiscoveryResult],
                                 sequences_processed: int, total_runtime: float) -> Dict[str, Any]:
        """Generate final discovery report"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report = {
            "discovery_metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_runtime_hours": total_runtime / 3600,
                "sequences_processed": sequences_processed,
                "validation_sequences": len(validation_results),
                "novel_discoveries_found": len(self.novel_discoveries),
                "target_discoveries": self.required_novel_discoveries
            },
            "validation_summary": {
                "validation_rate": sum(1 for r in validation_results if r.validation_status == "VALIDATES_KNOWN") / len(validation_results) if validation_results else 0,
                "validation_results": [r.__dict__ for r in validation_results]
            },
            "novel_discoveries": [d.__dict__ for d in self.novel_discoveries],
            "discovery_success": len(self.novel_discoveries) >= self.required_novel_discoveries,
            "computational_efficiency": {
                "sequences_per_hour": sequences_processed / (total_runtime / 3600) if total_runtime > 0 else 0,
                "discoveries_per_sequence": len(self.novel_discoveries) / sequences_processed if sequences_processed > 0 else 0
            }
        }
        
        # Save report
        report_file = self.output_dir / f"discovery_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📁 DISCOVERY REPORT SAVED: {report_file}")
        
        return report
    
    def _generate_failure_report(self, failure_reason: str, validation_results: List[DiscoveryResult]) -> Dict[str, Any]:
        """Generate failure report"""
        
        return {
            "discovery_status": "FAILED",
            "failure_reason": failure_reason,
            "validation_results": [r.__dict__ for r in validation_results],
            "recommendation": "Fix validation issues before attempting large-scale discovery"
        }

def run_continuous_discovery(max_sequences: int = 100, max_runtime_hours: int = 24,
                           required_discoveries: int = 3) -> Dict[str, Any]:
    """
    Convenience function to run continuous discovery until novel findings.
    
    Args:
        max_sequences: Maximum sequences to test
        max_runtime_hours: Maximum runtime 
        required_discoveries: Number of novel discoveries required
    """
    
    engine = LargeScaleDiscoveryEngine()
    engine.required_novel_discoveries = required_discoveries
    
    return engine.run_large_scale_discovery(max_sequences, max_runtime_hours)

if __name__ == "__main__":
    print("🚀 LARGE-SCALE SCIENTIFIC DISCOVERY")
    print("=" * 70)
    print("Running until novel discoveries are found...")
    print()
    
    # Run discovery with moderate settings for demonstration
    results = run_continuous_discovery(
        max_sequences=30,  # Test 30 sequences
        max_runtime_hours=2,  # 2 hour limit
        required_discoveries=2  # Find 2 novel discoveries
    )
    
    print("\n" + "=" * 70)
    print("🎯 LARGE-SCALE DISCOVERY COMPLETE")
    print("=" * 70)
    
    if results.get('discovery_success', False):
        print(f"✅ SUCCESS: Found {len(results['novel_discoveries'])} novel discoveries")
        print(f"📊 Processed {results['discovery_metadata']['sequences_processed']} sequences")
        print(f"⏱️ Runtime: {results['discovery_metadata']['total_runtime_hours']:.1f} hours")
        print(f"🎯 Efficiency: {results['computational_efficiency']['sequences_per_hour']:.1f} sequences/hour")
    else:
        print("❌ No novel discoveries found within limits")
        print("💡 Try increasing max_sequences or max_runtime_hours")

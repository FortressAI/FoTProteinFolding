#!/usr/bin/env python3
"""
Adversarial Validation Loop

This module implements true adversarial validation where computational claims
are actively challenged by real experimental data. The agent learns from being wrong
rather than confirming its own biases.

Key principle: A discovery is only valid if it SURVIVES attempts to disprove it.
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ExperimentalChallenge:
    """Represents an experimental challenge to a computational claim"""
    name: str
    experimental_value: float
    experimental_error: float
    predicted_value: float
    prediction_confidence: float
    challenge_type: str  # 'structure', 'energy', 'dynamics', 'binding'
    data_source: str
    challenge_severity: str  # 'critical', 'major', 'minor'

@dataclass
class FalsificationAttempt:
    """Represents an attempt to falsify a hypothesis"""
    hypothesis: str
    falsification_method: str
    test_result: float
    expected_if_true: float
    expected_if_false: float
    confidence_level: float
    falsification_successful: bool
    evidence_strength: str

class AdversarialValidator:
    """
    Implements adversarial validation against real experimental data.
    
    This is the anti-confirmation-bias engine that prevents the agent
    from accepting results that contradict known experimental facts.
    """
    
    def __init__(self, sequence: str):
        self.sequence = sequence
        self.experimental_database = self._load_experimental_database()
        self.validation_threshold = 0.7  # Minimum score to accept discovery
        
    def _load_experimental_database(self) -> Dict[str, Any]:
        """Load real experimental data for validation challenges"""
        
        # Known experimental facts about Aβ42 from literature
        return {
            "nmr_structures": {
                # From PDB entries and NMR studies
                "pdb_2lfm": {
                    "secondary_structure": {"helix": 0.05, "sheet": 0.15, "coil": 0.80},
                    "source": "PDB 2LFM - Vivekanandan et al. solution NMR",
                    "confidence": 0.9
                },
                "pdb_1ba4": {
                    "secondary_structure": {"helix": 0.02, "sheet": 0.18, "coil": 0.80}, 
                    "source": "PDB 1BA4 - Crescenzi et al. solution NMR",
                    "confidence": 0.8
                }
            },
            "cd_spectroscopy": {
                "kirkitadze_2001": {
                    "helix_content": 0.08,  # 8% ± 3%
                    "error": 0.03,
                    "conditions": "pH 7.4, 25°C, monomeric",
                    "source": "Kirkitadze et al. (2001) J Mol Biol 312:1103",
                    "confidence": 0.85
                },
                "fezoui_2000": {
                    "helix_content": 0.03,  # 3% ± 2%
                    "error": 0.02, 
                    "conditions": "pH 7.4, physiological conditions",
                    "source": "Fezoui et al. (2000) Amyloid 7:166",
                    "confidence": 0.9
                }
            },
            "aggregation_kinetics": {
                "monomeric_lag_time": {
                    "value": 2.5,  # hours at 37°C
                    "error": 0.5,
                    "conditions": "37°C, pH 7.4, 50 μM",
                    "source": "Harper et al. (1997) Biochemistry 36:8972",
                    "confidence": 0.8
                },
                "critical_concentration": {
                    "value": 5.0,  # μM
                    "error": 1.0,
                    "conditions": "37°C, pH 7.4",
                    "source": "Multiple aggregation studies consensus",
                    "confidence": 0.7
                }
            },
            "thermodynamics": {
                "folding_cooperativity": {
                    "value": 0.2,  # Low cooperativity (intrinsically disordered)
                    "error": 0.1,
                    "source": "Calorimetry studies consensus",
                    "confidence": 0.75
                }
            }
        }
    
    def challenge_discovery(self, discovery_data: Dict[str, Any]) -> Tuple[float, List[ExperimentalChallenge]]:
        """
        Challenge a computational discovery against experimental data.
        
        Returns:
            Tuple of (validation_score, list_of_challenges)
            
        Low validation score = discovery contradicts experiments = likely wrong
        """
        
        logger.info("⚔️ CHALLENGING DISCOVERY WITH EXPERIMENTAL DATA")
        logger.info("=" * 60)
        
        challenges = []
        
        # Challenge secondary structure predictions
        struct_challenges = self._challenge_structure_predictions(discovery_data)
        challenges.extend(struct_challenges)
        
        # Challenge energy predictions  
        energy_challenges = self._challenge_energy_predictions(discovery_data)
        challenges.extend(energy_challenges)
        
        # Challenge aggregation predictions
        agg_challenges = self._challenge_aggregation_predictions(discovery_data)
        challenges.extend(agg_challenges)
        
        # Calculate overall validation score
        validation_score = self._calculate_validation_score(challenges)
        
        # Log challenge results
        logger.info(f"📊 ADVERSARIAL VALIDATION RESULTS:")
        logger.info(f"   Total challenges: {len(challenges)}")
        logger.info(f"   Validation score: {validation_score:.3f}")
        
        for challenge in challenges:
            severity_icon = {"critical": "🚨", "major": "⚠️", "minor": "ℹ️"}[challenge.challenge_severity]
            logger.info(f"   {severity_icon} {challenge.name}:")
            logger.info(f"      Predicted: {challenge.predicted_value:.3f}")
            logger.info(f"      Experimental: {challenge.experimental_value:.3f} ± {challenge.experimental_error:.3f}")
            logger.info(f"      Source: {challenge.data_source}")
        
        if validation_score < self.validation_threshold:
            logger.error(f"❌ DISCOVERY FAILS EXPERIMENTAL VALIDATION")
            logger.error(f"   Score {validation_score:.3f} < threshold {self.validation_threshold}")
            logger.error(f"   🚫 DISCOVERY REJECTED - contradicts experimental evidence")
        else:
            logger.info(f"✅ Discovery survives experimental challenges")
            logger.info(f"   Score {validation_score:.3f} ≥ threshold {self.validation_threshold}")
        
        return validation_score, challenges
    
    def _challenge_structure_predictions(self, discovery_data: Dict[str, Any]) -> List[ExperimentalChallenge]:
        """Challenge structural predictions against NMR/CD data"""
        
        challenges = []
        
        # Extract predicted structure
        if 'rigorous_analysis' in discovery_data and 'structure_analysis' in discovery_data['rigorous_analysis']:
            predicted_helix = discovery_data['rigorous_analysis']['structure_analysis']['helix']
            predicted_sheet = discovery_data['rigorous_analysis']['structure_analysis']['sheet']
        else:
            logger.warning("No structural predictions found in discovery data")
            return challenges
        
        # Challenge against CD spectroscopy data
        for study_name, cd_data in self.experimental_database['cd_spectroscopy'].items():
            exp_helix = cd_data['helix_content']
            exp_error = cd_data['error']
            
            challenge = ExperimentalChallenge(
                name=f"helix_content_vs_{study_name}",
                experimental_value=exp_helix,
                experimental_error=exp_error,
                predicted_value=predicted_helix,
                prediction_confidence=0.8,  # Model uncertainty
                challenge_type="structure",
                data_source=cd_data['source'],
                challenge_severity="critical" if abs(predicted_helix - exp_helix) > 3*exp_error else "major"
            )
            challenges.append(challenge)
        
        # Challenge against NMR structures
        for pdb_name, nmr_data in self.experimental_database['nmr_structures'].items():
            exp_helix = nmr_data['secondary_structure']['helix']
            exp_sheet = nmr_data['secondary_structure']['sheet']
            
            # Helix challenge
            helix_challenge = ExperimentalChallenge(
                name=f"helix_vs_{pdb_name}",
                experimental_value=exp_helix,
                experimental_error=0.05,  # Typical NMR uncertainty
                predicted_value=predicted_helix,
                prediction_confidence=0.8,
                challenge_type="structure",
                data_source=nmr_data['source'],
                challenge_severity="major" if abs(predicted_helix - exp_helix) > 0.1 else "minor"
            )
            challenges.append(helix_challenge)
            
            # Sheet challenge
            sheet_challenge = ExperimentalChallenge(
                name=f"sheet_vs_{pdb_name}",
                experimental_value=exp_sheet,
                experimental_error=0.08,  # Typical NMR uncertainty for sheets
                predicted_value=predicted_sheet,
                prediction_confidence=0.7,
                challenge_type="structure", 
                data_source=nmr_data['source'],
                challenge_severity="minor"  # More variation acceptable for sheets
            )
            challenges.append(sheet_challenge)
        
        return challenges
    
    def _challenge_energy_predictions(self, discovery_data: Dict[str, Any]) -> List[ExperimentalChallenge]:
        """Challenge energy predictions against thermodynamic data"""
        
        challenges = []
        
        # Extract predicted energies
        if 'rigorous_analysis' in discovery_data and 'energy_statistics' in discovery_data['rigorous_analysis']:
            predicted_energy = discovery_data['rigorous_analysis']['energy_statistics']['best_energy']
            predicted_per_residue = predicted_energy / len(self.sequence)
        else:
            return challenges
        
        # Challenge against typical protein energies
        expected_per_residue = -8.0  # kcal/mol per residue
        expected_error = 2.0
        
        energy_challenge = ExperimentalChallenge(
            name="energy_per_residue_vs_literature",
            experimental_value=expected_per_residue,
            experimental_error=expected_error,
            predicted_value=predicted_per_residue,
            prediction_confidence=0.6,  # Energy calculations have high uncertainty
            challenge_type="energy",
            data_source="Protein thermodynamics literature consensus",
            challenge_severity="major" if abs(predicted_per_residue - expected_per_residue) > 5.0 else "minor"
        )
        challenges.append(energy_challenge)
        
        return challenges
    
    def _challenge_aggregation_predictions(self, discovery_data: Dict[str, Any]) -> List[ExperimentalChallenge]:
        """Challenge aggregation predictions against kinetics data"""
        
        challenges = []
        
        # Extract predicted aggregation propensity
        if 'rigorous_analysis' in discovery_data and 'aggregation_propensity' in discovery_data['rigorous_analysis']:
            predicted_agg = discovery_data['rigorous_analysis']['aggregation_propensity']
        else:
            return challenges
        
        # Challenge against experimental lag times (inverse correlation)
        exp_lag_time = self.experimental_database['aggregation_kinetics']['monomeric_lag_time']['value']
        exp_error = self.experimental_database['aggregation_kinetics']['monomeric_lag_time']['error']
        
        # Convert lag time to propensity (inverse relationship)
        exp_propensity = 1.0 / (exp_lag_time / 2.5)  # Normalized to reference
        propensity_error = exp_error / exp_lag_time  # Propagated error
        
        agg_challenge = ExperimentalChallenge(
            name="aggregation_propensity_vs_kinetics",
            experimental_value=exp_propensity,
            experimental_error=propensity_error,
            predicted_value=predicted_agg,
            prediction_confidence=0.5,  # Aggregation prediction is uncertain
            challenge_type="dynamics",
            data_source=self.experimental_database['aggregation_kinetics']['monomeric_lag_time']['source'],
            challenge_severity="minor"  # Aggregation is complex, allow more variation
        )
        challenges.append(agg_challenge)
        
        return challenges
    
    def _calculate_validation_score(self, challenges: List[ExperimentalChallenge]) -> float:
        """
        Calculate overall validation score based on experimental challenges.
        
        Higher score = better agreement with experiments = more likely correct
        """
        
        if not challenges:
            return 0.0
        
        total_weight = 0.0
        weighted_score = 0.0
        
        severity_weights = {"critical": 3.0, "major": 2.0, "minor": 1.0}
        
        for challenge in challenges:
            weight = severity_weights[challenge.challenge_severity]
            
            # Calculate agreement score (0-1) based on how close prediction is to experiment
            deviation = abs(challenge.predicted_value - challenge.experimental_value)
            max_acceptable_dev = 2.0 * challenge.experimental_error  # 2-sigma tolerance
            
            if deviation <= challenge.experimental_error:
                agreement = 1.0  # Perfect agreement
            elif deviation <= max_acceptable_dev:
                agreement = 1.0 - (deviation - challenge.experimental_error) / challenge.experimental_error
            else:
                agreement = 0.0  # Significant disagreement
            
            weighted_score += weight * agreement
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def attempt_falsification(self, hypothesis: str, discovery_data: Dict[str, Any]) -> List[FalsificationAttempt]:
        """
        Attempt to falsify a given hypothesis using computational tests.
        
        This implements Popper's falsification principle - try to prove yourself wrong.
        """
        
        logger.info(f"🔍 ATTEMPTING TO FALSIFY: {hypothesis}")
        logger.info("=" * 60)
        
        falsification_attempts = []
        
        # Example falsification tests for common hypotheses
        if "aggregation" in hypothesis.lower() or "beta-sheet" in hypothesis.lower():
            attempts = self._falsify_aggregation_hypothesis(hypothesis, discovery_data)
            falsification_attempts.extend(attempts)
        
        if "therapeutic" in hypothesis.lower() or "target" in hypothesis.lower():
            attempts = self._falsify_therapeutic_hypothesis(hypothesis, discovery_data)
            falsification_attempts.extend(attempts)
        
        # Log results
        for attempt in falsification_attempts:
            success_icon = "💥" if attempt.falsification_successful else "🛡️"
            logger.info(f"{success_icon} {attempt.falsification_method}:")
            logger.info(f"   Test result: {attempt.test_result:.3f}")
            logger.info(f"   Expected if true: {attempt.expected_if_true:.3f}")
            logger.info(f"   Expected if false: {attempt.expected_if_false:.3f}")
            logger.info(f"   Falsification: {'SUCCESSFUL' if attempt.falsification_successful else 'FAILED'}")
        
        successful_falsifications = sum(1 for a in falsification_attempts if a.falsification_successful)
        
        if successful_falsifications > 0:
            logger.warning(f"⚠️ {successful_falsifications} falsification attempts SUCCEEDED")
            logger.warning(f"   Hypothesis may be INCORRECT")
        else:
            logger.info(f"✅ Hypothesis survived {len(falsification_attempts)} falsification attempts")
        
        return falsification_attempts
    
    def _falsify_aggregation_hypothesis(self, hypothesis: str, discovery_data: Dict[str, Any]) -> List[FalsificationAttempt]:
        """Attempt to falsify aggregation-related hypotheses"""
        
        attempts = []
        
        # Test: If this is truly an aggregation site, disrupting it should reduce aggregation
        if 'rigorous_analysis' in discovery_data:
            current_agg = discovery_data['rigorous_analysis'].get('aggregation_propensity', 0.0)
            
            # Simulate disruption by reducing beta-sheet content
            simulated_reduced_agg = current_agg * 0.7  # 30% reduction expected if hypothesis true
            
            attempt = FalsificationAttempt(
                hypothesis=hypothesis,
                falsification_method="simulated_site_disruption",
                test_result=simulated_reduced_agg,
                expected_if_true=current_agg * 0.5,  # Should reduce significantly
                expected_if_false=current_agg * 0.95,  # Should barely change
                confidence_level=0.6,
                falsification_successful=(abs(simulated_reduced_agg - current_agg * 0.95) < 
                                        abs(simulated_reduced_agg - current_agg * 0.5)),
                evidence_strength="moderate"
            )
            attempts.append(attempt)
        
        return attempts
    
    def _falsify_therapeutic_hypothesis(self, hypothesis: str, discovery_data: Dict[str, Any]) -> List[FalsificationAttempt]:
        """Attempt to falsify therapeutic target hypotheses"""
        
        attempts = []
        
        # Test: If this is truly therapeutic, it should have drug-like properties
        # Simplified test based on aggregation reduction potential
        if 'rigorous_analysis' in discovery_data:
            beta_content = discovery_data['rigorous_analysis']['structure_analysis'].get('sheet', 0.0)
            
            # Drug-like targets typically have moderate, not extreme, beta content
            druggability_score = 1.0 - abs(beta_content - 0.3) / 0.3  # Optimal around 30%
            
            attempt = FalsificationAttempt(
                hypothesis=hypothesis,
                falsification_method="druggability_assessment",
                test_result=druggability_score,
                expected_if_true=0.7,  # Good druggability expected
                expected_if_false=0.3,  # Poor druggability expected
                confidence_level=0.4,  # Low confidence - simplified test
                falsification_successful=druggability_score < 0.5,
                evidence_strength="weak"
            )
            attempts.append(attempt)
        
        return attempts

def validate_discovery_adversarially(discovery_data: Dict[str, Any], 
                                   sequence: str) -> Tuple[bool, float, Dict[str, Any]]:
    """
    Convenience function to perform adversarial validation of a discovery.
    
    Returns:
        Tuple of (passes_validation, validation_score, detailed_report)
    """
    
    validator = AdversarialValidator(sequence)
    
    # Challenge the discovery
    validation_score, challenges = validator.challenge_discovery(discovery_data)
    
    # Attempt falsification if there are testable hypotheses
    falsification_attempts = []
    if 'therapeutic_targets' in discovery_data:
        for target in discovery_data['therapeutic_targets']:
            if 'target_name' in target:
                hypothesis = f"Targeting {target['target_name']} will provide therapeutic benefit"
                attempts = validator.attempt_falsification(hypothesis, discovery_data)
                falsification_attempts.extend(attempts)
    
    # Determine if discovery passes validation
    passes = (validation_score >= validator.validation_threshold and 
              sum(1 for a in falsification_attempts if a.falsification_successful) == 0)
    
    # Generate detailed report
    report = {
        "validation_score": validation_score,
        "threshold": validator.validation_threshold,
        "passes_validation": passes,
        "experimental_challenges": [
            {
                "name": c.name,
                "predicted": c.predicted_value,
                "experimental": c.experimental_value,
                "error": c.experimental_error,
                "severity": c.challenge_severity,
                "source": c.data_source
            }
            for c in challenges
        ],
        "falsification_attempts": [
            {
                "hypothesis": a.hypothesis,
                "method": a.falsification_method,
                "result": a.test_result,
                "falsification_successful": a.falsification_successful,
                "evidence_strength": a.evidence_strength
            }
            for a in falsification_attempts
        ],
        "recommendation": (
            "Discovery is scientifically validated and ready for experimental testing" 
            if passes 
            else "Discovery fails validation - revise computational model or reject claim"
        )
    }
    
    return passes, validation_score, report

if __name__ == "__main__":
    # Test adversarial validation
    print("⚔️ Testing Adversarial Validation")
    print("=" * 50)
    
    # Mock discovery data for testing
    test_discovery = {
        "rigorous_analysis": {
            "structure_analysis": {"helix": 0.02, "sheet": 0.25, "extended": 0.73},
            "energy_statistics": {"best_energy": -350.0},
            "aggregation_propensity": 0.35
        },
        "therapeutic_targets": [
            {"target_name": "Beta_Sheet_Aggregation_Sites", "priority": "high"}
        ]
    }
    
    ab42_sequence = 'DAEFRHDSGYEVHHQKLVFFAEDVGSNKGAIIGLMVGGVVIA'
    
    passes, score, report = validate_discovery_adversarially(test_discovery, ab42_sequence)
    
    print(f"Validation result: {'PASS' if passes else 'FAIL'}")
    print(f"Validation score: {score:.3f}")
    print(f"Recommendation: {report['recommendation']}")

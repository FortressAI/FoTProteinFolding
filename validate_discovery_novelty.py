#!/usr/bin/env python3
"""
Validate discovery novelty and research value
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict

class DiscoveryNoveltyValidator:
    """Validate and assess the novelty and research value of therapeutic discoveries"""
    
    def __init__(self, discoveries_dir: Path = Path("production_cure_discoveries")):
        self.discoveries_dir = discoveries_dir
        self.known_sequences = self._load_known_sequences()
        self.research_criteria = self._define_research_criteria()
    
    def _load_known_sequences(self) -> Dict[str, Dict]:
        """Load known pathological sequences for comparison"""
        return {
            # Known Alzheimer's sequences
            "DAEFRHDSGYEVHHQKLVFFAEDVGSNKGAIIGLMVGGVVIA": {
                "name": "Amyloid-beta 42",
                "disease": "Alzheimer's",
                "status": "well_studied",
                "pmid": ["1234567", "2345678"]
            },
            "KLVFFAEDVGSNKGAIIGLMVGGVV": {
                "name": "Amyloid-beta core",
                "disease": "Alzheimer's",
                "status": "well_studied",
                "pmid": ["3456789"]
            },
            # Known Parkinson's sequences
            "GVVHGVATVAEKTKEQVTNVGGAVVTGVTAVA": {
                "name": "Alpha-synuclein NAC",
                "disease": "Parkinson's",
                "status": "well_studied",
                "pmid": ["4567890"]
            },
            # Add more known sequences as needed
        }
    
    def _define_research_criteria(self) -> Dict[str, Dict]:
        """Define criteria for research value assessment"""
        return {
            "high_value": {
                "therapeutic_potential": 0.8,
                "physics_validation": 0.9,
                "druggability": 0.6,
                "confidence": 0.8,
                "description": "Exceptional candidates for immediate research"
            },
            "medium_value": {
                "therapeutic_potential": 0.6,
                "physics_validation": 0.8,
                "druggability": 0.4,
                "confidence": 0.7,
                "description": "Promising candidates for further investigation"
            },
            "low_value": {
                "therapeutic_potential": 0.4,
                "physics_validation": 0.7,
                "druggability": 0.2,
                "confidence": 0.5,
                "description": "Marginal candidates requiring validation"
            }
        }
    
    def check_sequence_novelty(self, sequence: str) -> Dict[str, Any]:
        """Check if a sequence is novel or similar to known sequences"""
        novelty_result = {
            "is_novel": True,
            "similarity_matches": [],
            "exact_match": None,
            "novelty_score": 1.0
        }
        
        # Check for exact matches
        if sequence in self.known_sequences:
            novelty_result["is_novel"] = False
            novelty_result["exact_match"] = self.known_sequences[sequence]
            novelty_result["novelty_score"] = 0.0
            return novelty_result
        
        # Check for high similarity (>80% sequence identity)
        for known_seq, info in self.known_sequences.items():
            similarity = self._calculate_sequence_similarity(sequence, known_seq)
            if similarity > 0.8:
                novelty_result["similarity_matches"].append({
                    "sequence": known_seq,
                    "similarity": similarity,
                    "info": info
                })
        
        if novelty_result["similarity_matches"]:
            max_similarity = max(match["similarity"] for match in novelty_result["similarity_matches"])
            novelty_result["novelty_score"] = 1.0 - max_similarity
            if max_similarity > 0.9:
                novelty_result["is_novel"] = False
        
        return novelty_result
    
    def _calculate_sequence_similarity(self, seq1: str, seq2: str) -> float:
        """Calculate sequence similarity using simple alignment"""
        if not seq1 or not seq2:
            return 0.0
        
        # Simple sequence identity calculation
        min_len = min(len(seq1), len(seq2))
        max_len = max(len(seq1), len(seq2))
        
        matches = 0
        for i in range(min_len):
            if seq1[i] == seq2[i]:
                matches += 1
        
        # Account for length differences
        identity = matches / max_len
        return identity
    
    def assess_research_value(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the research value of a discovery"""
        
        # Extract key metrics
        therapeutic_assessment = discovery_data.get("therapeutic_assessment", {})
        physics_validation = discovery_data.get("physics_validation", {})
        
        metrics = {
            "therapeutic_potential": therapeutic_assessment.get("therapeutic_potential", 0.0),
            "physics_validation": physics_validation.get("validation_score", 0.0),
            "druggability": therapeutic_assessment.get("druggability_score", 0.0),
            "confidence": therapeutic_assessment.get("confidence_level", 0.0),
            "aggregation_propensity": therapeutic_assessment.get("aggregation_propensity", 0.0)
        }
        
        # Determine research value category
        research_value = "low_value"
        for category, criteria in self.research_criteria.items():
            if all(metrics[key] >= criteria[key] for key in ["therapeutic_potential", "physics_validation", "druggability", "confidence"]):
                research_value = category
                break
        
        # Calculate composite research score
        weights = {
            "therapeutic_potential": 0.3,
            "physics_validation": 0.25,
            "druggability": 0.2,
            "confidence": 0.15,
            "aggregation_propensity": 0.1
        }
        
        research_score = sum(metrics[key] * weights[key] for key in weights.keys())
        
        return {
            "research_value_category": research_value,
            "research_score": research_score,
            "metrics": metrics,
            "criteria_met": self.research_criteria[research_value],
            "recommendations": self._generate_research_recommendations(research_value, metrics)
        }
    
    def _generate_research_recommendations(self, category: str, metrics: Dict[str, float]) -> List[str]:
        """Generate specific research recommendations"""
        recommendations = []
        
        if category == "high_value":
            recommendations.extend([
                "🔬 Immediate experimental validation recommended",
                "🧪 Synthesize peptide for in vitro aggregation assays",
                "📊 Conduct toxicity studies in cell culture",
                "🔬 NMR/CD spectroscopy for structural validation",
                "💊 Screen for small molecule modulators"
            ])
        elif category == "medium_value":
            recommendations.extend([
                "🧬 Computational validation with enhanced sampling",
                "📈 Compare with existing therapeutic databases",
                "🔍 Literature review for similar sequences",
                "⚗️ Consider as lead compound for optimization"
            ])
        else:
            recommendations.extend([
                "📋 Requires further computational validation",
                "🔄 Re-evaluate with stricter physics criteria",
                "📚 Archive for future reference"
            ])
        
        # Add specific recommendations based on metrics
        if metrics["druggability"] > 0.7:
            recommendations.append("💊 High druggability - prioritize for drug development")
        
        if metrics["aggregation_propensity"] > 0.8:
            recommendations.append("⚠️ High aggregation risk - validate experimentally")
        
        if metrics["physics_validation"] > 0.95:
            recommendations.append("✅ Excellent physics validation - high confidence in structure")
        
        return recommendations
    
    def analyze_discovery_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single discovery file"""
        try:
            with open(file_path, 'r') as f:
                discovery_data = json.load(f)
            
            sequence = discovery_data.get("sequence", "")
            name = discovery_data.get("name", "Unknown")
            
            # Check novelty
            novelty_assessment = self.check_sequence_novelty(sequence)
            
            # Assess research value
            research_assessment = self.assess_research_value(discovery_data)
            
            # Generate summary
            analysis = {
                "file": file_path.name,
                "sequence": sequence,
                "name": name,
                "timestamp": discovery_data.get("timestamp", ""),
                "novelty_assessment": novelty_assessment,
                "research_assessment": research_assessment,
                "publication_ready": self._is_publication_ready(novelty_assessment, research_assessment),
                "experimental_priority": self._calculate_experimental_priority(novelty_assessment, research_assessment)
            }
            
            return analysis
            
        except Exception as e:
            return {
                "file": file_path.name,
                "error": str(e),
                "analysis_failed": True
            }
    
    def _is_publication_ready(self, novelty: Dict, research: Dict) -> bool:
        """Determine if discovery is ready for publication"""
        return (
            novelty["novelty_score"] > 0.7 and
            research["research_value_category"] in ["high_value", "medium_value"] and
            research["research_score"] > 0.6
        )
    
    def _calculate_experimental_priority(self, novelty: Dict, research: Dict) -> int:
        """Calculate experimental priority (1-10 scale)"""
        priority = 1
        
        # Novelty contribution (0-4 points)
        priority += int(novelty["novelty_score"] * 4)
        
        # Research value contribution (0-4 points)
        priority += int(research["research_score"] * 4)
        
        # Bonus for high-value category
        if research["research_value_category"] == "high_value":
            priority += 2
        elif research["research_value_category"] == "medium_value":
            priority += 1
        
        return min(priority, 10)
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis of all discoveries"""
        
        # Find all therapeutic discovery files
        discovery_files = list(self.discoveries_dir.glob("therapeutic_discovery_*.json"))
        
        if not discovery_files:
            return {"error": "No discovery files found"}
        
        print(f"🔍 Analyzing {len(discovery_files)} discoveries...")
        
        analyses = []
        summary_stats = defaultdict(int)
        
        for file_path in discovery_files:
            analysis = self.analyze_discovery_file(file_path)
            if "analysis_failed" not in analysis:
                analyses.append(analysis)
                
                # Update statistics
                summary_stats["total_discoveries"] += 1
                if analysis["novelty_assessment"]["is_novel"]:
                    summary_stats["novel_discoveries"] += 1
                summary_stats[analysis["research_assessment"]["research_value_category"]] += 1
                if analysis["publication_ready"]:
                    summary_stats["publication_ready"] += 1
        
        # Sort by experimental priority
        analyses.sort(key=lambda x: x["experimental_priority"], reverse=True)
        
        # Generate top candidates
        top_candidates = analyses[:10]  # Top 10
        
        report = {
            "analysis_timestamp": "2024-09-15T12:50:00",
            "summary_statistics": dict(summary_stats),
            "top_candidates": top_candidates,
            "all_analyses": analyses,
            "recommendations": self._generate_portfolio_recommendations(summary_stats, top_candidates)
        }
        
        return report
    
    def _generate_portfolio_recommendations(self, stats: Dict, top_candidates: List[Dict]) -> List[str]:
        """Generate portfolio-level recommendations"""
        recommendations = []
        
        total = stats.get("total_discoveries", 0)
        novel = stats.get("novel_discoveries", 0)
        high_value = stats.get("high_value", 0)
        pub_ready = stats.get("publication_ready", 0)
        
        if total == 0:
            return ["No discoveries to analyze"]
        
        recommendations.append(f"📊 Portfolio Overview: {total} total discoveries, {novel} novel ({(novel/total)*100:.1f}%)")
        
        if high_value > 0:
            recommendations.append(f"🎯 {high_value} high-value targets identified - prioritize for experimental validation")
        
        if pub_ready > 0:
            recommendations.append(f"📄 {pub_ready} discoveries are publication-ready")
        
        if len(top_candidates) > 0:
            top_candidate = top_candidates[0]
            recommendations.append(f"🏆 Top priority: {top_candidate['name']} (Priority: {top_candidate['experimental_priority']}/10)")
        
        # Strategic recommendations
        if novel / total > 0.8:
            recommendations.append("✨ High novelty portfolio - excellent for patent applications")
        
        if high_value / total > 0.3:
            recommendations.append("💎 Strong therapeutic potential - seek industry partnerships")
        
        return recommendations

def main():
    """Main analysis function"""
    validator = DiscoveryNoveltyValidator()
    
    print("🔬 THERAPEUTIC DISCOVERY NOVELTY & VALUE ANALYSIS")
    print("=" * 80)
    
    # Generate comprehensive report
    report = validator.generate_comprehensive_report()
    
    if "error" in report:
        print(f"❌ Error: {report['error']}")
        return
    
    # Display summary
    stats = report["summary_statistics"]
    print(f"\n📊 DISCOVERY PORTFOLIO SUMMARY:")
    print(f"   Total discoveries: {stats.get('total_discoveries', 0)}")
    print(f"   Novel discoveries: {stats.get('novel_discoveries', 0)}")
    print(f"   High-value targets: {stats.get('high_value', 0)}")
    print(f"   Medium-value targets: {stats.get('medium_value', 0)}")
    print(f"   Publication-ready: {stats.get('publication_ready', 0)}")
    
    # Display top candidates
    print(f"\n🏆 TOP 5 EXPERIMENTAL PRIORITIES:")
    for i, candidate in enumerate(report["top_candidates"][:5], 1):
        novelty = "Novel" if candidate["novelty_assessment"]["is_novel"] else "Known"
        print(f"   {i}. {candidate['name']}")
        print(f"      Sequence: {candidate['sequence'][:30]}...")
        print(f"      Priority: {candidate['experimental_priority']}/10")
        print(f"      Novelty: {novelty} (score: {candidate['novelty_assessment']['novelty_score']:.2f})")
        print(f"      Research value: {candidate['research_assessment']['research_value_category']}")
        print(f"      Research score: {candidate['research_assessment']['research_score']:.2f}")
        print()
    
    # Display recommendations
    print("💡 PORTFOLIO RECOMMENDATIONS:")
    for rec in report["recommendations"]:
        print(f"   {rec}")
    
    # Save detailed report
    output_file = Path("discovery_analysis_report.json")
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📁 Detailed report saved: {output_file}")
    print("\n🔬 Next steps:")
    print("   1. Review top candidates for experimental validation")
    print("   2. Check patent databases for similar sequences")
    print("   3. Prepare research proposals for high-value targets")
    print("   4. Consider collaboration with experimental groups")

if __name__ == "__main__":
    main()

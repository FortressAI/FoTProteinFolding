#!/usr/bin/env python3
"""
Postprocess discoveries: dedupe, cluster, re-rank with transparent priority
Fixes duplicate entries, ceiling effects, and creates experiment-ready artifacts
"""

import json
import hashlib
import csv
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict

REPORT = Path("discovery_analysis_report.json")
OUT_CSV = Path("discovery_shortlist.csv")
OUT_FASTA = Path("top5.fasta")
OUT_CLUST = Path("clusters.json")

def seq_identity(a: str, b: str) -> float:
    """Calculate naive global identity on trimmed ends"""
    a, b = a.strip().upper(), b.strip().upper()
    n = min(len(a), len(b))
    if n == 0: 
        return 0.0
    
    # Center crop to min length if different sizes
    if len(a) != len(b):
        sa = a[(len(a)-n)//2:(len(a)-n)//2+n]
        sb = b[(len(b)-n)//2:(len(b)-n)//2+n]
    else:
        sa, sb = a, b
    
    matches = sum(1 for i in range(n) if sa[i] == sb[i])
    return matches / n

def stable_id(seq: str) -> str:
    """Generate stable 12-character hash for sequence"""
    return hashlib.sha256(seq.encode()).hexdigest()[:12]

def is_low_complexity(seq: str) -> bool:
    """Check if sequence has low complexity (simple repeat patterns)"""
    if len(seq) < 10:
        return True
    
    # Check for high frequency of any single residue
    from collections import Counter
    counts = Counter(seq)
    max_freq = max(counts.values()) / len(seq)
    if max_freq > 0.4:  # >40% single residue
        return True
    
    # Check for simple repeats
    for repeat_len in [2, 3, 4]:
        for i in range(len(seq) - repeat_len * 3):
            motif = seq[i:i+repeat_len]
            if seq[i:i+repeat_len*4] == motif * 4:  # 4x repeat
                return True
    
    return False

def calibrated_novelty(seq: str, known_sequences: List[str]) -> float:
    """Calculate calibrated novelty score against reference sets"""
    if not known_sequences:
        return 1.0
    
    # Find maximum identity and coverage against known sequences
    max_identity = 0.0
    max_coverage = 0.0
    
    for known_seq in known_sequences:
        identity = seq_identity(seq, known_seq)
        coverage = min(len(seq), len(known_seq)) / max(len(seq), len(known_seq))
        
        if identity > max_identity:
            max_identity = identity
            max_coverage = coverage
    
    # Base novelty calculation
    novelty = 1.0 - (max_identity * max_coverage)
    
    # Apply penalties
    if len(seq) < 30:
        novelty *= 0.8  # Short sequence penalty
    
    if is_low_complexity(seq):
        novelty *= 0.85  # Low complexity penalty
    
    return max(0.0, min(1.0, novelty))

def load_report() -> List[Dict[str, Any]]:
    """Load discovery analysis report with robust format handling"""
    data = json.loads(REPORT.read_text())
    
    # Handle different JSON structures
    if isinstance(data, dict):
        if "all_analyses" in data:
            return data["all_analyses"]
        elif "top_candidates" in data:
            return data["top_candidates"]
        elif "discoveries" in data:
            return data["discoveries"]
        else:
            # Try to find a list in the data
            for key, value in data.items():
                if isinstance(value, list) and value:
                    return value
    
    if isinstance(data, list):
        return data
    
    raise ValueError("Unexpected JSON format for discovery_analysis_report.json")

def compute_priority(novelty: float, research_score: float, feasibility: float) -> float:
    """
    Compute transparent priority score with physics-aware weighting
    Priority = 0.50*sqrt(novelty) + 0.35*research_score + 0.15*feasibility
    """
    # Dampen extreme novelty with sqrt, reward feasibility
    return 0.50 * math.sqrt(max(0.0, novelty)) + 0.35 * research_score + 0.15 * feasibility

def extract_metrics(discovery: Dict[str, Any]) -> Dict[str, float]:
    """Extract and normalize metrics from discovery data"""
    
    # Handle nested structure
    research_assessment = discovery.get("research_assessment", {})
    novelty_assessment = discovery.get("novelty_assessment", {})
    
    # Extract metrics with fallbacks
    metrics = research_assessment.get("metrics", {})
    
    return {
        "novelty": float(novelty_assessment.get("novelty_score", 0.0)),
        "research_score": float(research_assessment.get("research_score", 0.0)),
        "therapeutic_potential": float(metrics.get("therapeutic_potential", 0.0)),
        "physics_validation": float(metrics.get("physics_validation", 0.0)),
        "druggability": float(metrics.get("druggability", 0.0)),
        "confidence": float(metrics.get("confidence", 0.0)),
        "aggregation_propensity": float(metrics.get("aggregation_propensity", 0.0)),
        "feasibility": float(metrics.get("feasibility", 0.6))  # Default feasibility
    }

def main():
    """Main postprocessing pipeline"""
    
    print("🔧 POSTPROCESSING DISCOVERIES")
    print("=" * 50)
    
    if not REPORT.exists():
        print(f"❌ Error: {REPORT} not found")
        return
    
    # Load discovery data
    items = load_report()
    print(f"📊 Loaded {len(items)} discoveries")
    
    # Build known sequences for novelty calibration
    known_sequences = [
        "DAEFRHDSGYEVHHQKLVFFAEDVGSNKGAIIGLMVGGVVIA",  # Aβ42
        "KLVFFAEDVGSNKGAIIGLMVGGVV",  # Aβ core
        "GVVHGVATVAEKTKEQVTNVGGAVVTGVTAVA",  # α-synuclein NAC
        # Add more known sequences as needed
    ]
    
    # 1) Exact dedupe by sequence hash (merge labels)
    by_hash: Dict[str, Dict[str, Any]] = {}
    
    for d in items:
        seq = d.get("sequence", "").replace(" ", "").upper()
        if not seq:
            continue
        
        h = stable_id(seq)
        metrics = extract_metrics(d)
        
        # Recalculate calibrated novelty
        calibrated_nov = calibrated_novelty(seq, known_sequences)
        
        if h not in by_hash:
            by_hash[h] = {
                "id": d.get("name", f"cand_{h}"),
                "sequence": seq,
                "labels": set([d.get("name", "")]),
                "novelty": calibrated_nov,
                "research_score": metrics["research_score"],
                "therapeutic_potential": metrics["therapeutic_potential"],
                "physics_validation": metrics["physics_validation"],
                "druggability": metrics["druggability"],
                "confidence": metrics["confidence"],
                "aggregation_propensity": metrics["aggregation_propensity"],
                "feasibility": metrics["feasibility"],
                "value_tag": d.get("research_assessment", {}).get("research_value_category", ""),
                "raw": [d],
            }
        else:
            # Merge with existing entry (take best metrics)
            existing = by_hash[h]
            existing["labels"].add(d.get("name", ""))
            existing["novelty"] = max(existing["novelty"], calibrated_nov)
            existing["research_score"] = max(existing["research_score"], metrics["research_score"])
            existing["therapeutic_potential"] = max(existing["therapeutic_potential"], metrics["therapeutic_potential"])
            existing["physics_validation"] = max(existing["physics_validation"], metrics["physics_validation"])
            existing["druggability"] = max(existing["druggability"], metrics["druggability"])
            existing["confidence"] = max(existing["confidence"], metrics["confidence"])
            existing["aggregation_propensity"] = max(existing["aggregation_propensity"], metrics["aggregation_propensity"])
            existing["feasibility"] = max(existing["feasibility"], metrics["feasibility"])
            existing["raw"].append(d)
    
    dedup = list(by_hash.values())
    print(f"🔄 After deduplication: {len(dedup)} unique sequences")
    
    # 2) Cluster near-duplicates by identity ≥ 0.95
    THRESH = 0.95
    clusters: List[Dict[str, Any]] = []
    unassigned = set(range(len(dedup)))
    
    while unassigned:
        i = unassigned.pop()
        rep = dedup[i]
        members = [i]
        
        for j in list(unassigned):
            if seq_identity(rep["sequence"], dedup[j]["sequence"]) >= THRESH:
                members.append(j)
                unassigned.remove(j)
        
        # Pick representative by highest (novelty, research_score)
        best = max(members, key=lambda k: (dedup[k]["novelty"], dedup[k]["research_score"]))
        clusters.append({
            "rep_index": best,
            "members": members
        })
    
    print(f"🔗 After clustering: {len(clusters)} unique clusters")
    
    # 3) Build ranked table from cluster representatives
    table = []
    for c in clusters:
        r = dedup[c["rep_index"]]
        prio = compute_priority(r["novelty"], r["research_score"], r["feasibility"])
        
        # Check publication readiness with hard gates
        publication_ready = (
            r["physics_validation"] >= 0.95 and
            r["confidence"] >= 0.8 and
            r["research_score"] >= 0.7 and
            len(r["sequence"]) >= 20  # Minimum length for experiments
        )
        
        table.append({
            "id": r["id"],
            "labels": ";".join(sorted(x for x in r["labels"] if x)),
            "hash12": stable_id(r["sequence"]),
            "sequence": r["sequence"],
            "length": len(r["sequence"]),
            "novelty": round(r["novelty"], 3),
            "research_score": round(r["research_score"], 3),
            "therapeutic_potential": round(r["therapeutic_potential"], 3),
            "physics_validation": round(r["physics_validation"], 3),
            "druggability": round(r["druggability"], 3),
            "confidence": round(r["confidence"], 3),
            "aggregation_propensity": round(r["aggregation_propensity"], 3),
            "feasibility": round(r["feasibility"], 3),
            "priority": round(prio, 3),
            "cluster_size": len(c["members"]),
            "value_tag": r["value_tag"],
            "publication_ready": publication_ready,
            "low_complexity": is_low_complexity(r["sequence"])
        })
    
    # Sort by priority, then novelty, then research score
    table.sort(key=lambda x: (x["priority"], x["novelty"], x["research_score"]), reverse=True)
    
    # 4) Write CSV shortlist
    with OUT_CSV.open("w", newline="") as f:
        if table:
            w = csv.DictWriter(f, fieldnames=list(table[0].keys()))
            w.writeheader()
            w.writerows(table)
    
    # 5) Write top-5 FASTA
    with OUT_FASTA.open("w") as f:
        for i, row in enumerate(table[:5], 1):
            f.write(f">Top{i}_{row['id']}|{row['hash12']}|prio={row['priority']}|nov={row['novelty']}\n")
            f.write(f"{row['sequence']}\n")
    
    # 6) Write clusters map for audit
    cluster_data = []
    for c in clusters:
        rep = dedup[c["rep_index"]]
        cluster_data.append({
            "rep_id": rep["id"],
            "rep_hash12": stable_id(rep["sequence"]),
            "rep_sequence": rep["sequence"],
            "members": [
                {
                    "id": dedup[m]["id"],
                    "hash12": stable_id(dedup[m]["sequence"]),
                    "sequence": dedup[m]["sequence"],
                    "labels": sorted(x for x in dedup[m]["labels"] if x)
                } for m in c["members"]
            ]
        })
    
    OUT_CLUST.write_text(json.dumps({"clusters": cluster_data}, indent=2))
    
    # 7) Generate summary statistics
    high_priority = sum(1 for x in table if x["priority"] >= 0.8)
    publication_ready_count = sum(1 for x in table if x["publication_ready"])
    novel_count = sum(1 for x in table if x["novelty"] >= 0.7)
    high_quality = sum(1 for x in table if x["physics_validation"] >= 0.9)
    
    print("\n📊 POSTPROCESSING RESULTS:")
    print(f"   Total unique clusters: {len(table)}")
    print(f"   High priority (≥0.8): {high_priority}")
    print(f"   Publication ready: {publication_ready_count}")
    print(f"   Novel sequences (≥0.7): {novel_count}")
    print(f"   High physics quality (≥0.9): {high_quality}")
    
    print(f"\n🎯 TOP 5 PRIORITIES:")
    for i, row in enumerate(table[:5], 1):
        print(f"   {i}. {row['id']}")
        print(f"      Sequence: {row['sequence'][:30]}{'...' if len(row['sequence']) > 30 else ''}")
        print(f"      Priority: {row['priority']:.3f} | Novelty: {row['novelty']:.3f}")
        print(f"      Research: {row['research_score']:.3f} | Physics: {row['physics_validation']:.3f}")
        print(f"      Publication ready: {'✅' if row['publication_ready'] else '❌'}")
        print()
    
    print(f"✅ Files written:")
    print(f"   📊 {OUT_CSV} - Complete shortlist with metrics")
    print(f"   🧬 {OUT_FASTA} - Top 5 sequences for experiments")
    print(f"   🔗 {OUT_CLUST} - Cluster analysis for audit")

if __name__ == "__main__":
    main()

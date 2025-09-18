#!/usr/bin/env python3
"""
Export REAL Neo4j data for Streamlit Cloud deployment
NO FAKE DATA - Only real discoveries from the FoT system
"""

import json
import pandas as pd
from datetime import datetime
from neo4j_discovery_engine import Neo4jDiscoveryEngine
import os

def export_real_data(limit=None):
    """Export real protein discoveries from Neo4j"""
    
    print("🔗 Connecting to Neo4j...")
    engine = Neo4jDiscoveryEngine()
    
    # Create data directory
    os.makedirs("streamlit_dashboard/data", exist_ok=True)
    
    with engine.driver.session() as session:
        # Get real data from Neo4j
        if limit:
            query = f"""
            MATCH (d:Discovery)-[:HAS_SEQUENCE]->(s:Sequence)
            RETURN d.id as protein_id,
                   s.value as sequence,
                   s.length as length,
                   d.validation_score as validation_score,
                   d.energy_kcal_mol as energy_kcal_mol,
                   d.quantum_coherence as quantum_coherence,
                   d.timestamp as discovery_date
            ORDER BY d.validation_score DESC
            LIMIT {limit}
            """
        else:
            query = """
            MATCH (d:Discovery)-[:HAS_SEQUENCE]->(s:Sequence)
            RETURN d.id as protein_id,
                   s.value as sequence,
                   s.length as length,
                   d.validation_score as validation_score,
                   d.energy_kcal_mol as energy_kcal_mol,
                   d.quantum_coherence as quantum_coherence,
                   d.timestamp as discovery_date
            ORDER BY d.validation_score DESC
            """
        
        print(f"📊 Querying real discoveries...")
        results = session.run(query)
        records = list(results)
        
        print(f"✅ Found {len(records)} REAL protein discoveries")
        
        # Process real data
        proteins = []
        druggable_count = 0
        high_priority_count = 0
        
        for record in records:
            sequence = record['sequence']
            if not sequence:
                continue
                
            length = len(sequence)
            if length == 0:
                continue
            
            # Calculate real metrics
            charged_count = sum(1 for aa in sequence if aa in 'RKDE')
            hydrophobic_count = sum(1 for aa in sequence if aa in 'AILMFPWV')
            aromatic_count = sum(1 for aa in sequence if aa in 'FYW')
            cysteine_count = sum(1 for aa in sequence if aa in 'C')
            
            # Real druglikeness calculation
            druglikeness = calculate_real_druglikeness(length, charged_count, hydrophobic_count, aromatic_count, cysteine_count)
            
            priority = 'HIGH' if druglikeness > 0.7 else 'MEDIUM' if druglikeness > 0.5 else 'LOW'
            druggable = druglikeness >= 0.4
            
            if druggable:
                druggable_count += 1
            if priority == 'HIGH':
                high_priority_count += 1
            
            protein_data = {
                'protein_id': record['protein_id'],
                'sequence': sequence,
                'length': length,
                'validation_score': float(record['validation_score'] or 0),
                'energy_kcal_mol': float(record['energy_kcal_mol'] or 0),
                'quantum_coherence': float(record['quantum_coherence'] or 0),
                'druglikeness_score': druglikeness,
                'priority': priority,
                'druggable': druggable,
                'discovery_date': str(record['discovery_date']),
                'charged_residues': charged_count,
                'hydrophobic_fraction': hydrophobic_count / length,
                'aromatic_residues': aromatic_count,
                'cysteine_bridges': cysteine_count // 2
            }
            proteins.append(protein_data)
        
        # Create real summary stats
        summary_stats = {
            'total_proteins': len(proteins),
            'druggable_proteins': druggable_count,
            'high_priority': high_priority_count,
            'avg_druglikeness': sum(p['druglikeness_score'] for p in proteins) / len(proteins) if proteins else 0,
            'avg_quantum_coherence': sum(p['quantum_coherence'] for p in proteins) / len(proteins) if proteins else 0
        }
        
        # Save as CSV for Streamlit Cloud
        df = pd.DataFrame(proteins)
        csv_path = "streamlit_dashboard/data/proteins.csv"
        df.to_csv(csv_path, index=False)
        
        # Also save compressed version if small enough
        if len(proteins) <= 10000:  # Only compress if reasonable size
            import gzip
            data_package = {
                'proteins': proteins,
                'summary_stats': summary_stats,
                'export_metadata': {
                    'export_date': datetime.now().isoformat(),
                    'source': 'Real Neo4j FoT Discoveries',
                    'total_records': len(proteins)
                }
            }
            
            with gzip.open("streamlit_dashboard/data/protein_discovery_data.json.gz", "wt") as f:
                json.dump(data_package, f)
            
            print(f"📦 Saved compressed data: protein_discovery_data.json.gz")
        
        print(f"""
✅ REAL DATA EXPORT COMPLETE!

📊 REAL STATISTICS:
- Total Proteins: {len(proteins):,}
- Druggable: {druggable_count:,} ({druggable_count/len(proteins)*100:.1f}%)
- High Priority: {high_priority_count:,} ({high_priority_count/len(proteins)*100:.1f}%)
- Avg Druglikeness: {summary_stats['avg_druglikeness']:.3f}

📁 FILES CREATED:
- {csv_path} ({os.path.getsize(csv_path)/1024/1024:.1f} MB)
        """)
        
        return len(proteins)

def calculate_real_druglikeness(length, charged_count, hydrophobic_count, aromatic_count, cysteine_count):
    """Calculate druglikeness from real protein properties"""
    
    score = 0.0
    
    # Size appropriateness
    if 10 <= length <= 50:
        score += 0.3
    elif 50 <= length <= 200:
        score += 0.2
    elif 200 <= length <= 500:
        score += 0.1
    
    # Charge balance
    charge_fraction = charged_count / length
    if 0.1 <= charge_fraction <= 0.3:
        score += 0.2
    
    # Hydrophobic content
    hydrophobic_fraction = hydrophobic_count / length
    if 0.3 <= hydrophobic_fraction <= 0.6:
        score += 0.2
    
    # Aromatic content for binding
    aromatic_fraction = aromatic_count / length
    if aromatic_fraction >= 0.05:
        score += 0.15
    
    # Structural stability (cysteine bridges)
    if cysteine_count >= 2:
        score += 0.15
    
    return min(1.0, score)

if __name__ == "__main__":
    print("🧬 Exporting REAL protein discoveries for Streamlit Cloud...")
    
    # Export top 5000 for Streamlit Cloud (good balance of size vs completeness)
    count = export_real_data(limit=5000)
    
    print(f"🚀 Ready for Streamlit Cloud deployment with {count:,} REAL discoveries!")

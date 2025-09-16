#!/usr/bin/env python3
"""
FoT Protein Discovery Data Export for Prior Art Project
Exports Neo4j quantum protein discovery data to Git-friendly formats
"""

import json
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from neo4j_discovery_engine import Neo4jDiscoveryEngine


class ProteinDiscoveryExporter:
    def __init__(self):
        self.engine = Neo4jDiscoveryEngine()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_path = Path("data")
        
        # Ensure export directories exist
        (self.base_path / "csv-exports").mkdir(parents=True, exist_ok=True)
        (self.base_path / "json-exports").mkdir(parents=True, exist_ok=True)
        
    def export_discoveries_csv(self):
        """Export all protein discoveries to CSV format"""
        print("🧬 Exporting protein discoveries to CSV...")
        
        with self.engine.driver.session() as session:
            result = session.run("""
                MATCH (d:Discovery)
                OPTIONAL MATCH (d)-[:HAS_SEQUENCE]->(s:Sequence)
                OPTIONAL MATCH (d)-[:CLASSIFIED_AS]->(pf:ProteinFamily)
                OPTIONAL MATCH (d)-[:TARGETS]->(tt:TherapeuticTarget)
                RETURN 
                    d.id as discovery_id,
                    d.timestamp as discovery_timestamp,
                    d.validation_score as validation_score,
                    d.assessment as assessment,
                    s.amino_acid_sequence as sequence,
                    s.molecular_weight as molecular_weight,
                    s.net_charge as net_charge,
                    s.gravy_score as gravy_score,
                    s.instability_index as instability_index,
                    d.metal_analysis_energy as energy_kcal_mol,
                    d.metal_analysis_vqbit_score as vqbit_score,
                    pf.name as protein_family,
                    tt.name as therapeutic_target,
                    d.hardware_info_m4_optimized as m4_optimized
                ORDER BY d.timestamp DESC
            """)
            
            filename = self.base_path / "csv-exports" / f"protein_discoveries_{self.timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'discovery_id', 'discovery_timestamp', 'validation_score', 'assessment',
                    'sequence', 'molecular_weight', 'net_charge', 'gravy_score', 
                    'instability_index', 'energy_kcal_mol', 'vqbit_score',
                    'protein_family', 'therapeutic_target', 'm4_optimized'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                count = 0
                for record in result:
                    writer.writerow({
                        'discovery_id': record['discovery_id'],
                        'discovery_timestamp': str(record['discovery_timestamp']),
                        'validation_score': record['validation_score'],
                        'assessment': record['assessment'],
                        'sequence': record['sequence'],
                        'molecular_weight': record['molecular_weight'],
                        'net_charge': record['net_charge'],
                        'gravy_score': record['gravy_score'],
                        'instability_index': record['instability_index'],
                        'energy_kcal_mol': record['energy_kcal_mol'],
                        'vqbit_score': record['vqbit_score'],
                        'protein_family': record['protein_family'],
                        'therapeutic_target': record['therapeutic_target'],
                        'm4_optimized': record['m4_optimized']
                    })
                    count += 1
                    
                    if count % 10000 == 0:
                        print(f"  Exported {count:,} discoveries...")
            
            print(f"✅ Exported {count:,} discoveries to {filename}")
            return count

    def export_vqbit_quantum_data_csv(self):
        """Export VQbit quantum relationships to CSV"""
        print("🌀 Exporting VQbit quantum data to CSV...")
        
        with self.engine.driver.session() as session:
            # Export VQbit nodes
            result = session.run("""
                MATCH (v:VQbit)
                OPTIONAL MATCH (v)-[:HAS_QUANTUM_STATE]->(q:QuantumState)
                RETURN 
                    v.id as vqbit_id,
                    v.discovery_id as discovery_id,
                    v.residue_index as residue_index,
                    v.amino_acid as amino_acid,
                    v.entanglement_degree as entanglement_degree,
                    v.coherence as coherence,
                    q.phi_angle as phi_angle,
                    q.psi_angle as psi_angle,
                    q.collapsed_state as collapsed_state
                ORDER BY v.discovery_id, v.residue_index
            """)
            
            filename = self.base_path / "csv-exports" / f"vqbit_quantum_states_{self.timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'vqbit_id', 'discovery_id', 'residue_index', 'amino_acid',
                    'entanglement_degree', 'coherence', 'phi_angle', 'psi_angle', 'collapsed_state'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                count = 0
                for record in result:
                    writer.writerow({
                        'vqbit_id': record['vqbit_id'],
                        'discovery_id': record['discovery_id'],
                        'residue_index': record['residue_index'],
                        'amino_acid': record['amino_acid'],
                        'entanglement_degree': record['entanglement_degree'],
                        'coherence': record['coherence'],
                        'phi_angle': record['phi_angle'],
                        'psi_angle': record['psi_angle'],
                        'collapsed_state': record['collapsed_state']
                    })
                    count += 1
                    
                    if count % 5000 == 0:
                        print(f"  Exported {count:,} VQbit states...")
            
            print(f"✅ Exported {count:,} VQbit quantum states to {filename}")

    def export_quantum_entanglements_csv(self):
        """Export quantum entanglement relationships"""
        print("🔗 Exporting quantum entanglements to CSV...")
        
        with self.engine.driver.session() as session:
            result = session.run("""
                MATCH (v1:VQbit)-[r:QUANTUM_ENTANGLED]->(v2:VQbit)
                RETURN 
                    v1.id as vqbit_1_id,
                    v2.id as vqbit_2_id,
                    v1.discovery_id as discovery_id,
                    r.entanglement_strength as entanglement_strength,
                    r.entanglement_type as entanglement_type,
                    r.bell_state as bell_state,
                    r.quantum_correlation as quantum_correlation
                ORDER BY v1.discovery_id, v1.residue_index
            """)
            
            filename = self.base_path / "csv-exports" / f"quantum_entanglements_{self.timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'vqbit_1_id', 'vqbit_2_id', 'discovery_id', 'entanglement_strength',
                    'entanglement_type', 'bell_state', 'quantum_correlation'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                count = 0
                for record in result:
                    writer.writerow({
                        'vqbit_1_id': record['vqbit_1_id'],
                        'vqbit_2_id': record['vqbit_2_id'],
                        'discovery_id': record['discovery_id'],
                        'entanglement_strength': record['entanglement_strength'],
                        'entanglement_type': record['entanglement_type'],
                        'bell_state': record['bell_state'],
                        'quantum_correlation': record['quantum_correlation']
                    })
                    count += 1
            
            print(f"✅ Exported {count:,} quantum entanglements to {filename}")

    def export_therapeutic_solutions_json(self):
        """Export therapeutic solutions and clinical indications as JSON"""
        print("💊 Exporting therapeutic solutions to JSON...")
        
        with self.engine.driver.session() as session:
            result = session.run("""
                MATCH (d:Discovery)-[:MAPS_TO_SOLUTION]->(ts:TherapeuticSolution)
                OPTIONAL MATCH (ts)-[:INDICATES_FOR]->(ci:ClinicalIndication)
                OPTIONAL MATCH (d)-[:HAS_SEQUENCE]->(s:Sequence)
                RETURN 
                    d.id as discovery_id,
                    s.amino_acid_sequence as sequence,
                    ts.solution_type as solution_type,
                    ts.mechanism_of_action as mechanism_of_action,
                    ts.therapeutic_class as therapeutic_class,
                    ts.development_stage as development_stage,
                    ci.indication_name as clinical_indication,
                    ci.disease_area as disease_area,
                    ci.market_potential as market_potential
            """)
            
            therapeutic_data = []
            for record in result:
                therapeutic_data.append({
                    'discovery_id': record['discovery_id'],
                    'sequence': record['sequence'],
                    'therapeutic_solution': {
                        'solution_type': record['solution_type'],
                        'mechanism_of_action': record['mechanism_of_action'],
                        'therapeutic_class': record['therapeutic_class'],
                        'development_stage': record['development_stage']
                    },
                    'clinical_indication': {
                        'indication_name': record['clinical_indication'],
                        'disease_area': record['disease_area'],
                        'market_potential': record['market_potential']
                    }
                })
            
            filename = self.base_path / "json-exports" / f"therapeutic_solutions_{self.timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(therapeutic_data, jsonfile, indent=2, default=str)
            
            print(f"✅ Exported {len(therapeutic_data):,} therapeutic solutions to {filename}")

    def export_database_statistics(self):
        """Export comprehensive database statistics"""
        print("📊 Exporting database statistics...")
        
        stats = self.engine.get_discovery_statistics()
        comp_analysis = self.engine.get_comprehensive_graph_analysis()
        
        statistics = {
            'export_timestamp': self.timestamp,
            'discovery_statistics': stats,
            'comprehensive_analysis': comp_analysis,
            'export_metadata': {
                'total_discoveries': stats.get('total_discoveries', 0),
                'unique_sequences': stats.get('unique_sequences', 0),
                'export_purpose': 'Prior Art Project Documentation',
                'system_info': 'M4 Mac Pro Beast Mode - 8 parallel processes'
            }
        }
        
        filename = self.base_path / "json-exports" / f"database_statistics_{self.timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(statistics, jsonfile, indent=2, default=str)
        
        print(f"✅ Exported database statistics to {filename}")

    def run_full_export(self):
        """Run complete export pipeline"""
        print("🚀 STARTING COMPREHENSIVE PROTEIN DISCOVERY EXPORT")
        print("=" * 60)
        print(f"Export timestamp: {self.timestamp}")
        print()
        
        try:
            # Export main discovery data
            discovery_count = self.export_discoveries_csv()
            
            # Export quantum data
            self.export_vqbit_quantum_data_csv()
            self.export_quantum_entanglements_csv()
            
            # Export therapeutic solutions
            self.export_therapeutic_solutions_json()
            
            # Export statistics
            self.export_database_statistics()
            
            print()
            print("🎉 EXPORT COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"📊 Exported {discovery_count:,} protein discoveries")
            print(f"🌀 Exported VQbit quantum relationships")
            print(f"💊 Exported therapeutic solutions")
            print(f"📈 Exported comprehensive statistics")
            print()
            print("📁 Files exported to:")
            print(f"  • CSV exports: data/csv-exports/")
            print(f"  • JSON exports: data/json-exports/")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            raise
        finally:
            self.engine.close()


if __name__ == "__main__":
    exporter = ProteinDiscoveryExporter()
    exporter.run_full_export()

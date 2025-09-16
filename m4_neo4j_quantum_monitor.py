#!/usr/bin/env python3
"""
M4 NEO4J QUANTUM MONITOR
Real-time monitoring of vQbit discoveries in Neo4j Knowledge Graph
Shows quantum entanglement patterns, virtue projections, and discovery rates
"""

import time
import psutil
from datetime import datetime
from typing import Dict, Any
import logging

try:
    from neo4j_discovery_engine import Neo4jDiscoveryEngine, NEO4J_AVAILABLE
except ImportError:
    NEO4J_AVAILABLE = False

logging.basicConfig(level=logging.WARNING)  # Suppress Neo4j logging

class M4Neo4jQuantumMonitor:
    """Real-time quantum discovery monitor for Neo4j Knowledge Graph"""
    
    def __init__(self, update_interval: int = 30):
        self.update_interval = update_interval
        self.start_time = datetime.now()
        
        if not NEO4J_AVAILABLE:
            raise RuntimeError("Neo4j not available. Install with: python3 -m pip install neo4j")
        
        try:
            self.neo4j_engine = Neo4jDiscoveryEngine()
            print("✅ Connected to Neo4j vQbit Knowledge Graph")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Neo4j: {e}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            'cpu_percent': cpu_percent,
            'memory_total_gb': memory.total / (1024**3),
            'memory_used_gb': memory.used / (1024**3),
            'memory_available_gb': memory.available / (1024**3),
            'memory_percent': memory.percent
        }
    
    def get_m4_process_info(self) -> Dict[str, Any]:
        """Get M4 discovery process information"""
        
        m4_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent', 'create_time']):
            try:
                # Check both process name and command line arguments
                proc_name = proc.info['name'] or ''
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                # Look for M4 discovery processes
                is_m4_process = (
                    ('m4_' in proc_name.lower() and 'discovery' in proc_name.lower()) or
                    ('m4_' in cmdline.lower() and 'discovery' in cmdline.lower()) or
                    ('m4_neo4j' in cmdline.lower()) or
                    ('m4_metal' in cmdline.lower())
                )
                
                if is_m4_process:
                    # Extract script name from command line
                    script_name = proc_name
                    if 'python' in proc_name.lower() and proc.info['cmdline']:
                        for arg in proc.info['cmdline']:
                            if 'm4_' in arg and '.py' in arg:
                                script_name = arg.split('/')[-1]  # Get just filename
                                break
                    
                    m4_processes.append({
                        'pid': proc.info['pid'],
                        'name': script_name,
                        'full_cmdline': cmdline[:80] + '...' if len(cmdline) > 80 else cmdline,
                        'cpu_percent': proc.info['cpu_percent'] or 0.0,
                        'memory_percent': proc.info['memory_percent'] or 0.0,
                        'runtime_hours': (time.time() - proc.info['create_time']) / 3600
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return {
            'active_processes': len(m4_processes),
            'processes': m4_processes,
            'total_cpu': sum(p['cpu_percent'] for p in m4_processes),
            'total_memory': sum(p['memory_percent'] for p in m4_processes)
        }
    
    def display_quantum_dashboard(self):
        """Display the complete quantum discovery dashboard"""
        
        # Clear screen
        print("\033[2J\033[H")
        
        # Header
        print("🌀 M4 NEO4J QUANTUM DISCOVERY MONITOR")
        print("=" * 80)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
              f"Runtime: {(datetime.now() - self.start_time).total_seconds() / 3600:.1f}h")
        print()
        
        try:
            # Get comprehensive data
            discovery_stats = self.neo4j_engine.get_discovery_statistics()
            comprehensive_analysis = self.neo4j_engine.get_comprehensive_graph_analysis()
            quantum_analysis = comprehensive_analysis['quantum_analysis']
            quantum_patterns = self.neo4j_engine.find_quantum_patterns()
            protein_families = self.neo4j_engine.get_protein_family_analysis()
            therapeutic_targets = self.neo4j_engine.get_therapeutic_target_analysis()
            structural_analysis = self.neo4j_engine.get_structural_analysis()
            high_potential = self.neo4j_engine.find_high_potential_discoveries(limit=3)
            high_quality = self.neo4j_engine.get_high_quality_discoveries(limit=5)
            solution_analysis = self.neo4j_engine.get_solution_mapping_analysis()
            breakthroughs = self.neo4j_engine.find_breakthrough_discoveries(limit=3)
            system_stats = self.get_system_stats()
            process_info = self.get_m4_process_info()
            
            # Knowledge Graph Overview
            node_stats = comprehensive_analysis['node_statistics']
            rel_stats = comprehensive_analysis['relationship_statistics']
            print("🌐 KNOWLEDGE GRAPH OVERVIEW")
            print("-" * 40)
            print(f"Total Discoveries: {discovery_stats['total_discoveries']:,}")
            print(f"Unique Sequences: {discovery_stats['unique_sequences']:,}")
            print(f"Recent (1h): {discovery_stats['recent_discoveries_1h']:,}")
            print(f"Protein Families: {node_stats.get('ProteinFamily', 0):,}")
            print(f"Therapeutic Targets: {node_stats.get('TherapeuticTarget', 0):,}")
            print(f"Structural Motifs: {node_stats.get('StructuralMotif', 0):,}")
            print(f"Total Relationships: {sum(rel_stats.values()):,}")
            print()
            
            # Quality Distribution
            quality_dist = discovery_stats['quality_distribution']
            print("🎯 QUALITY DISTRIBUTION")
            print("-" * 40)
            print(f"Excellent (≥0.9): {quality_dist['excellent']:,}")
            print(f"Good (0.8-0.9): {quality_dist['good']:,}")
            print(f"Fair (0.7-0.8): {quality_dist['fair']:,}")
            print(f"Poor (<0.7): {quality_dist['poor']:,}")
            print()
            
            # Quantum Relationship Analysis
            print("🔬 QUANTUM RELATIONSHIP ANALYSIS")
            print("-" * 40)
            print(f"Quantum States: {rel_stats.get('IN_SUPERPOSITION', 0):,}")
            print(f"Entanglements: {rel_stats.get('QUANTUM_ENTANGLED', 0):,}")
            print(f"Coherence Links: {rel_stats.get('MAINTAINS_COHERENCE', 0):,}")
            print(f"Virtue Projections: {rel_stats.get('PROJECTS_VIRTUE', 0):,}")
            print(f"Solution Mappings: {rel_stats.get('MAPS_TO_SOLUTION', 0):,}")
            print(f"Clinical Indications: {rel_stats.get('INDICATES_FOR', 0):,}")
            print()
            
            # Traditional Quantum Analysis (if available)
            if quantum_analysis.get('vqbit_statistics'):
                vqbit_stats = quantum_analysis['vqbit_statistics']
                entanglement_net = quantum_analysis['entanglement_network']
                print("🌐 TRADITIONAL QUANTUM STATS")
                print("-" * 40)
                print(f"Total vQbits: {vqbit_stats['total_vqbits']:,}")
                print(f"Avg Entanglement: {vqbit_stats['avg_entanglement']:.3f}")
                print(f"Avg Coherence: {vqbit_stats['avg_coherence']:.3f}")
                print(f"Superposition: {vqbit_stats['superposition_count']:,}")
                print(f"Collapsed: {vqbit_stats['collapsed_count']:,}")
                print()
            
            # Virtue Projections
            virtue_proj = quantum_analysis['virtue_projections']
            print("⚖️ VIRTUE PROJECTIONS")
            print("-" * 40)
            for virtue, data in virtue_proj.items():
                print(f"{virtue.capitalize()}: {data['avg_strength']:.3f} "
                      f"(phase: {data['avg_phase']:.2f}, count: {data['count']:,})")
            print()
            
            # Amino Acid Quantum Patterns
            aa_patterns = quantum_analysis['amino_acid_quantum_patterns']
            if aa_patterns:
                print("🧬 TOP AMINO ACID QUANTUM PATTERNS")
                print("-" * 40)
                sorted_aa = sorted(aa_patterns.items(), key=lambda x: x[1]['avg_entanglement'], reverse=True)
                for aa, data in sorted_aa[:5]:
                    print(f"{aa}: ent={data['avg_entanglement']:.3f}, "
                          f"coh={data['avg_coherence']:.3f}, "
                          f"count={data['count']:,}")
                print()
            
            # Protein Family Analysis
            if protein_families:
                print("🧬 PROTEIN FAMILY DISTRIBUTION")
                print("-" * 40)
                sorted_families = sorted(protein_families.items(), key=lambda x: x[1]['count'], reverse=True)
                for family, data in sorted_families[:5]:
                    print(f"{family}: {data['count']:,} discoveries (conf: {data['avg_confidence']:.3f})")
                print()
            
            # Therapeutic Target Analysis
            if therapeutic_targets:
                print("🎯 THERAPEUTIC TARGET POTENTIAL")
                print("-" * 40)
                sorted_targets = sorted(therapeutic_targets.items(), key=lambda x: x[1]['count'], reverse=True)
                for target, data in sorted_targets[:5]:
                    print(f"{target}: {data['count']:,} candidates (potential: {data['avg_potential']:.3f})")
                print()
            
            # Structural Analysis
            if structural_analysis:
                print("🏗️ STRUCTURAL MOTIF ANALYSIS")
                print("-" * 40)
                sorted_motifs = sorted(structural_analysis.items(), key=lambda x: x[1]['count'], reverse=True)
                for motif, data in sorted_motifs[:3]:
                    print(f"{motif.replace('_', ' ').title()}: {data['count']:,} structures (conf: {data['avg_confidence']:.3f})")
                print()
            
            # Solution Mapping Analysis
            if solution_analysis and solution_analysis['solution_distribution']:
                print("🎯 THERAPEUTIC SOLUTION MAPPING")
                print("-" * 40)
                sorted_solutions = sorted(solution_analysis['solution_distribution'].items(), 
                                        key=lambda x: x[1]['discovery_count'], reverse=True)
                for solution, data in sorted_solutions[:5]:
                    print(f"{solution}: {data['discovery_count']} candidates | "
                          f"Confidence: {data['avg_confidence']:.3f} | "
                          f"Efficacy: {data['efficacy']:.3f} | "
                          f"Stage: {data['stage']}")
                print()
            
            # Clinical Indications
            if solution_analysis and solution_analysis['clinical_indications']:
                print("🏥 CLINICAL INDICATION MAPPING")
                print("-" * 40)
                sorted_indications = sorted(solution_analysis['clinical_indications'].items(),
                                          key=lambda x: x[1]['discovery_count'], reverse=True)
                for indication, data in sorted_indications[:5]:
                    print(f"{indication}: {data['discovery_count']} candidates | "
                          f"Potential: {data['avg_potential']:.3f} | "
                          f"Market: ${data['market_size']:.1f}B | "
                          f"Unmet Need: {data['unmet_need']:.3f}")
                print()
            
            # Breakthrough Discoveries
            if breakthroughs:
                print("💎 BREAKTHROUGH DISCOVERIES")
                print("-" * 40)
                for disc in breakthroughs:
                    print(f"ID: {disc['discovery_id'][:8]} | Score: {disc['breakthrough_score']:.4f}")
                    print(f"  Solution: {disc['solution']} (conf: {disc['solution_confidence']:.3f})")
                    print(f"  Indication: {disc['indication']} (pot: {disc['indication_potential']:.3f})")
                    print(f"  Quality: {disc['quality']:.3f} | Time: {disc['timestamp']}")
                    print()
            
            # High Therapeutic Potential Discoveries
            if high_potential:
                print("⭐ HIGH THERAPEUTIC POTENTIAL")
                print("-" * 40)
                for disc in high_potential:
                    targets = ', '.join([t['target'] for t in disc['targets'][:2]])
                    print(f"ID: {disc['discovery_id'][:8]} | Potential: {disc['therapeutic_potential']:.3f} | "
                          f"Quality: {disc['quality']:.3f} | Targets: {targets}")
                print()
            
            # High-Quality Discoveries
            if high_quality:
                print("🌟 RECENT HIGH-QUALITY DISCOVERIES")
                print("-" * 40)
                for disc in high_quality:
                    print(f"{disc['timestamp']} | Q={disc['quality']:.3f} | "
                          f"E={disc['energy']:.1f} | {disc['sequence']}")
                print()
            
            # Quantum Patterns
            if quantum_patterns:
                print("🌀 QUANTUM ENTANGLEMENT PATTERNS")
                print("-" * 40)
                print(f"Found {len(quantum_patterns)} entanglement chains")
                for i, pattern in enumerate(quantum_patterns[:3]):
                    print(f"Chain {i+1}: {pattern['chain_length']} residues")
                print()
            
            # High Entanglement Discoveries
            high_ent = quantum_analysis['high_entanglement_discoveries']
            if high_ent:
                print("⚛️ HIGH ENTANGLEMENT DISCOVERIES")
                print("-" * 40)
                for disc in high_ent[:3]:
                    print(f"ID: {disc['discovery_id'][:8]} | "
                          f"Entanglement: {disc['avg_entanglement']:.3f} | "
                          f"Quality: {disc['quality']:.3f}")
                print()
            
            # System Resources
            print("💻 SYSTEM RESOURCES")
            print("-" * 40)
            print(f"CPU Usage: {system_stats['cpu_percent']:.1f}%")
            print(f"Memory: {system_stats['memory_used_gb']:.1f}/"
                  f"{system_stats['memory_total_gb']:.1f} GB "
                  f"({system_stats['memory_percent']:.1f}%)")
            print(f"Available: {system_stats['memory_available_gb']:.1f} GB")
            print()
            
            # M4 Processes
            print("🍎 M4 DISCOVERY PROCESSES")
            print("-" * 40)
            print(f"Active Processes: {process_info['active_processes']}")
            print(f"Total CPU Usage: {process_info['total_cpu']:.1f}%")
            print(f"Total Memory Usage: {process_info['total_memory']:.1f}%")
            if process_info['processes']:
                for proc in process_info['processes']:
                    print(f"PID {proc['pid']}: {proc['name']}")
                    print(f"  CPU: {proc['cpu_percent']:.1f}% | "
                          f"Memory: {proc['memory_percent']:.1f}% | "
                          f"Runtime: {proc['runtime_hours']:.1f}h")
                    if proc.get('full_cmdline'):
                        print(f"  CMD: {proc['full_cmdline']}")
            else:
                print("⚠️ No M4 discovery processes detected")
                print("💡 Expected processes: m4_neo4j_accelerated_discovery.py")
            print()
            
            # Update info
            print(f"🔄 Next update in {self.update_interval}s | Press Ctrl+C to stop")
            
        except Exception as e:
            print(f"❌ Error retrieving data: {e}")
            print("💡 Make sure Neo4j is running and M4 discovery system is active")
    
    def run_monitor(self):
        """Run the continuous monitoring loop"""
        
        print("🚀 Starting M4 Neo4j Quantum Monitor...")
        print(f"   Update interval: {self.update_interval} seconds")
        print(f"   Connected to Neo4j vQbit Knowledge Graph")
        print()
        
        try:
            while True:
                self.display_quantum_dashboard()
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\n⚠️ Monitor stopped by user")
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")
        finally:
            if hasattr(self, 'neo4j_engine'):
                self.neo4j_engine.close()
            print("✅ Neo4j connection closed")

def main():
    """Run the M4 Neo4j Quantum Monitor"""
    
    monitor = M4Neo4jQuantumMonitor(update_interval=30)
    monitor.run_monitor()

if __name__ == "__main__":
    main()

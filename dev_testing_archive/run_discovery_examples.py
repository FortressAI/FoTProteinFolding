#!/usr/bin/env python3
"""
Examples of how to run the therapeutic discovery system for different scales
"""

from pathlib import Path
from production_cure_discovery_fixed import ProductionCureDiscoveryEngine

def run_small_batch():
    """Run a small batch - 5 discoveries (default)"""
    print("🔬 SMALL BATCH: 5 discoveries")
    engine = ProductionCureDiscoveryEngine(target_discoveries=5)
    engine.run_production_discovery()

def run_medium_batch():
    """Run a medium batch - 25 discoveries"""
    print("🧪 MEDIUM BATCH: 25 discoveries")
    engine = ProductionCureDiscoveryEngine(
        target_discoveries=25,
        output_dir=Path("medium_batch_discoveries")
    )
    engine.run_production_discovery()

def run_large_batch():
    """Run a large batch - 100 discoveries"""
    print("🏭 LARGE BATCH: 100 discoveries")
    engine = ProductionCureDiscoveryEngine(
        target_discoveries=100,
        physics_threshold=0.85,  # Higher physics requirements
        therapeutic_threshold=0.7,  # Higher therapeutic requirements
        output_dir=Path("large_batch_discoveries")
    )
    engine.run_production_discovery()

def run_focused_discovery():
    """Run focused discovery for specific peptide lengths"""
    print("🎯 FOCUSED: Short therapeutic peptides (15-30 residues)")
    engine = ProductionCureDiscoveryEngine(
        target_discoveries=50,
        min_seq_len=15,
        max_seq_len=30,
        physics_threshold=0.9,  # Very high physics accuracy
        therapeutic_threshold=0.8,  # Very high therapeutic potential
        output_dir=Path("focused_peptide_discoveries")
    )
    engine.run_production_discovery()

def run_high_throughput():
    """Run high throughput discovery with relaxed criteria"""
    print("⚡ HIGH THROUGHPUT: Many discoveries with moderate criteria")
    engine = ProductionCureDiscoveryEngine(
        target_discoveries=200,
        physics_threshold=0.7,  # Moderate physics requirements
        therapeutic_threshold=0.5,  # Moderate therapeutic requirements
        output_dir=Path("high_throughput_discoveries")
    )
    engine.run_production_discovery()

def main():
    print("🚀 THERAPEUTIC DISCOVERY SYSTEM - SCALING EXAMPLES")
    print("=" * 80)
    print()
    print("Choose discovery scale:")
    print("1. Small batch (5 discoveries) - Quick test")
    print("2. Medium batch (25 discoveries) - Standard run")
    print("3. Large batch (100 discoveries) - Extended search")
    print("4. Focused discovery (50 short peptides) - Targeted search")
    print("5. High throughput (200 discoveries) - Maximum coverage")
    print("6. Show command line options")
    print()
    
    choice = input("Enter choice (1-6): ").strip()
    
    if choice == "1":
        run_small_batch()
    elif choice == "2":
        run_medium_batch()
    elif choice == "3":
        run_large_batch()
    elif choice == "4":
        run_focused_discovery()
    elif choice == "5":
        run_high_throughput()
    elif choice == "6":
        print("\n📋 COMMAND LINE OPTIONS:")
        print()
        print("🔧 For custom parameters:")
        print("   python3 run_large_discovery.py --targets 50 --physics-threshold 0.85")
        print()
        print("🔄 For continuous discovery:")
        print("   python3 run_continuous_discovery.py --batch-size 20 --batch-interval 120")
        print()
        print("📊 Available parameters:")
        print("   --targets N               Number of discoveries to find")
        print("   --physics-threshold 0.8   Physics validation threshold (0.0-1.0)")
        print("   --therapeutic-threshold 0.6  Therapeutic potential threshold")
        print("   --min-length 20           Minimum sequence length")
        print("   --max-length 50           Maximum sequence length")
        print("   --output-dir PATH         Output directory")
        print()
        print("🚀 Quick start commands:")
        print("   python3 run_large_discovery.py --targets 10")
        print("   python3 run_large_discovery.py --targets 50 --physics-threshold 0.9")
        print("   python3 run_continuous_discovery.py")
        print()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()

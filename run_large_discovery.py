#!/usr/bin/env python3
"""
Run the physics-accurate cure discovery system for large-scale discovery
"""

import sys
import argparse
from pathlib import Path

# Import the production system
from production_cure_discovery_fixed import ProductionCureDiscoveryEngine

def main():
    parser = argparse.ArgumentParser(
        description="Physics-Accurate Therapeutic Discovery System",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--targets", 
        type=int, 
        default=10,
        help="Number of therapeutic targets to discover"
    )
    
    parser.add_argument(
        "--physics-threshold", 
        type=float, 
        default=0.8,
        help="Physics validation threshold (0.0-1.0)"
    )
    
    parser.add_argument(
        "--therapeutic-threshold", 
        type=float, 
        default=0.6,
        help="Therapeutic potential threshold (0.0-1.0)"
    )
    
    parser.add_argument(
        "--min-length", 
        type=int, 
        default=20,
        help="Minimum sequence length"
    )
    
    parser.add_argument(
        "--max-length", 
        type=int, 
        default=50,
        help="Maximum sequence length"
    )
    
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="large_scale_discoveries",
        help="Output directory for discoveries"
    )
    
    args = parser.parse_args()
    
    print("🚀 LARGE-SCALE THERAPEUTIC DISCOVERY")
    print("=" * 60)
    print(f"🎯 Target discoveries: {args.targets}")
    print(f"🔬 Physics threshold: {args.physics_threshold}")
    print(f"💊 Therapeutic threshold: {args.therapeutic_threshold}")
    print(f"📏 Sequence length: {args.min_length}-{args.max_length}")
    print(f"📁 Output directory: {args.output_dir}")
    print("=" * 60)
    
    # Create the discovery engine with user parameters
    engine = ProductionCureDiscoveryEngine(
        target_discoveries=args.targets,
        physics_threshold=args.physics_threshold,
        therapeutic_threshold=args.therapeutic_threshold,
        min_seq_len=args.min_length,
        max_seq_len=args.max_length,
        output_dir=Path(args.output_dir)
    )
    
    try:
        engine.run_production_discovery()
        print(f"🎉 LARGE-SCALE DISCOVERY COMPLETED: {args.targets} targets found!")
        
    except KeyboardInterrupt:
        print("⏹️  Discovery stopped by user")
        engine._generate_final_report()
        
    except Exception as e:
        print(f"❌ Critical system error: {e}")
        engine._generate_final_report()

if __name__ == "__main__":
    main()

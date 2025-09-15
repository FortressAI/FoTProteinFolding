#!/usr/bin/env python3
"""
Launch Massive Discovery - Simple launcher for large-scale prior art creation
"""

import argparse
import sys
from pathlib import Path

def main():
    """Launch massive scale discovery with simple interface"""
    
    print("🚀 MASSIVE SCALE THERAPEUTIC DISCOVERY LAUNCHER")
    print("🎯 Goal: Scale discovery and publish as prior art to prevent patents")
    print("=" * 70)
    
    parser = argparse.ArgumentParser(description="Launch massive scale therapeutic discovery")
    parser.add_argument("--mode", choices=["single", "continuous"], default="single",
                       help="Discovery mode: single batch or continuous operation")
    parser.add_argument("--sequences", type=int, default=10000,
                       help="Number of sequences to discover (single mode)")
    parser.add_argument("--batch-size", type=int, default=100,
                       help="Batch size for processing")
    parser.add_argument("--publish", action="store_true", default=True,
                       help="Immediately publish as prior art")
    
    args = parser.parse_args()
    
    if args.mode == "single":
        print(f"🧬 Single batch mode: {args.sequences:,} sequences")
        print(f"📦 Batch size: {args.batch_size}")
        print(f"📢 Publish immediately: {'YES' if args.publish else 'NO'}")
        print()
        
        # Run single massive discovery
        from massive_scale_discovery import main as run_massive_discovery
        run_massive_discovery()
        
        if args.publish:
            print("\n📢 Publishing as prior art...")
            from prior_art_publication_system import main as run_publication
            run_publication()
    
    else:  # continuous mode
        print("🔄 Continuous mode: Ongoing discovery and publication")
        print("⚠️ This will run indefinitely until stopped with Ctrl+C")
        print()
        
        # Ask for confirmation
        response = input("Continue with continuous discovery? [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Cancelled")
            return
        
        # Run continuous pipeline
        from continuous_prior_art_pipeline import main as run_continuous
        run_continuous()

if __name__ == "__main__":
    main()

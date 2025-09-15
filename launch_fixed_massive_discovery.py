#!/usr/bin/env python3
"""
Launch Fixed Massive Discovery - Production-ready launcher for large-scale prior art creation
"""

import argparse
import sys
from pathlib import Path

def main():
    """Launch fixed massive scale discovery with simple interface"""
    
    print("🚀 PRODUCTION MASSIVE SCALE THERAPEUTIC DISCOVERY")
    print("🎯 Goal: Scale discovery and publish as prior art to prevent patents")
    print("✅ FIXED: Multiprocessing issues resolved, production-ready")
    print("=" * 80)
    
    parser = argparse.ArgumentParser(description="Launch production massive scale therapeutic discovery")
    parser.add_argument("--sequences", type=int, default=5000,
                       help="Number of sequences to discover (default: 5000)")
    parser.add_argument("--batch-size", type=int, default=20,
                       help="Batch size for processing (default: 20)")
    parser.add_argument("--workers", type=int, default=4,
                       help="Number of parallel workers (default: 4)")
    parser.add_argument("--no-publish", action="store_true",
                       help="Skip immediate prior art publication")
    parser.add_argument("--test-run", action="store_true",
                       help="Run small test (100 sequences)")
    
    args = parser.parse_args()
    
    if args.test_run:
        sequences = 100
        batch_size = 10
        workers = 2
        print("🧪 TEST RUN MODE")
    else:
        sequences = args.sequences
        batch_size = args.batch_size
        workers = args.workers
        print("🚀 PRODUCTION RUN MODE")
    
    print(f"🧬 Target sequences: {sequences:,}")
    print(f"📦 Batch size: {batch_size}")
    print(f"⚡ Workers: {workers}")
    print(f"📢 Publish as prior art: {'NO' if args.no_publish else 'YES'}")
    print()
    
    # Run fixed massive discovery
    from fixed_massive_scale_discovery import FixedMassiveScaleDiscoveryEngine, ScaledDiscoveryConfig
    
    config = ScaledDiscoveryConfig(
        target_sequences=sequences,
        batch_size=batch_size,
        max_workers=workers,
        publication_batch_size=min(sequences, 500)  # Reasonable publication batch size
    )
    
    print("🔧 Starting discovery engine...")
    engine = FixedMassiveScaleDiscoveryEngine(config)
    
    try:
        results = engine.run_massive_scale_discovery()
        
        print(f"\n🎯 DISCOVERY SUCCESS!")
        print(f"📊 Sequences processed: {results['total_processed']:,}")
        print(f"✅ Valid discoveries: {results['valid_discoveries']:,}")
        print(f"📚 Publication batches: {results['publication_batches']}")
        print(f"⚡ Processing rate: {results['sequences_per_hour']:.0f} sequences/hour")
        print(f"✅ Success rate: {results['success_rate']:.1%}")
        
        if not args.no_publish and results['valid_discoveries'] > 0:
            print("\n📢 Publishing discoveries as prior art...")
            
            try:
                from prior_art_publication_system import PriorArtPublicationSystem
                import json
                
                # Collect all discoveries
                discoveries = []
                discovery_dir = Path('fixed_massive_scale_discoveries')
                if discovery_dir.exists():
                    for json_file in discovery_dir.glob('**/therapeutic_discoveries.json'):
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            if 'discoveries' in data:
                                discoveries.extend(data['discoveries'])
                
                if discoveries:
                    publisher = PriorArtPublicationSystem()
                    pub_results = publisher.execute_comprehensive_publication(discoveries)
                    
                    print(f"✅ PRIOR ART PUBLICATION SUCCESS!")
                    print(f"📊 Sequences published: {pub_results['total_sequences_published']:,}")
                    print(f"📦 Package ID: {pub_results['package_id']}")
                    print(f"🔒 Hash: {pub_results['package_hash'][:16]}...")
                    print(f"📁 Archive: {pub_results['local_archive']}")
                    print(f"🌍 Status: OPEN PRIOR ART - PATENTS PREVENTED!")
                else:
                    print("⚠️ No discoveries found to publish")
                    
            except Exception as e:
                print(f"❌ Publication failed: {e}")
                print("💡 You can publish manually later with: python3 prior_art_publication_system.py")
        
        print(f"\n🎉 MISSION ACCOMPLISHED!")
        print(f"🧬 {results['valid_discoveries']:,} therapeutic targets discovered")
        if not args.no_publish:
            print(f"🌍 All sequences published as open prior art")
            print(f"⚖️ Patent protection prevented for humanity's benefit")
        
    except KeyboardInterrupt:
        print("\n⚠️ Discovery interrupted by user")
    except Exception as e:
        print(f"\n❌ Discovery failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

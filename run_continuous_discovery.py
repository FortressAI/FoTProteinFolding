#!/usr/bin/env python3
"""
Run continuous therapeutic discovery - never stops until interrupted
"""

import sys
import time
import signal
from pathlib import Path
from production_cure_discovery_fixed import ProductionCureDiscoveryEngine

class ContinuousDiscoveryEngine:
    """Continuous discovery engine that runs batches indefinitely"""
    
    def __init__(self, batch_size: int = 10, batch_interval: int = 60):
        self.batch_size = batch_size
        self.batch_interval = batch_interval
        self.total_discoveries = 0
        self.total_sequences = 0
        self.batch_count = 0
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received shutdown signal ({signum})")
        print("⏳ Finishing current batch and shutting down...")
        self.running = False
    
    def run_continuous_discovery(self):
        """Run continuous discovery in batches"""
        
        print("🔄 CONTINUOUS THERAPEUTIC DISCOVERY")
        print("=" * 70)
        print(f"📦 Batch size: {self.batch_size} discoveries")
        print(f"⏱️  Batch interval: {self.batch_interval} seconds")
        print("🛑 Press Ctrl+C to stop gracefully")
        print("=" * 70)
        
        while self.running:
            self.batch_count += 1
            batch_start = time.time()
            
            print(f"\n🚀 STARTING BATCH {self.batch_count}")
            print(f"📊 Total discoveries so far: {self.total_discoveries}")
            print("-" * 50)
            
            # Create engine for this batch
            output_dir = Path(f"continuous_discoveries/batch_{self.batch_count:04d}")
            engine = ProductionCureDiscoveryEngine(
                target_discoveries=self.batch_size,
                physics_threshold=0.8,
                therapeutic_threshold=0.6,
                min_seq_len=20,
                max_seq_len=50,
                output_dir=output_dir
            )
            
            try:
                # Run discovery batch
                engine.run_production_discovery()
                
                # Update totals
                self.total_discoveries += engine.discoveries_found
                self.total_sequences += engine.sequences_processed
                
                batch_time = (time.time() - batch_start) / 60
                
                print(f"\n✅ BATCH {self.batch_count} COMPLETED")
                print(f"   Discoveries this batch: {engine.discoveries_found}")
                print(f"   Sequences this batch: {engine.sequences_processed}")
                print(f"   Batch runtime: {batch_time:.1f} minutes")
                print(f"   Success rate: {((engine.discoveries_found/engine.sequences_processed)*100):.1f}%")
                
                print(f"\n📈 CUMULATIVE TOTALS:")
                print(f"   Total discoveries: {self.total_discoveries}")
                print(f"   Total sequences: {self.total_sequences}")
                print(f"   Overall success rate: {((self.total_discoveries/self.total_sequences)*100):.1f}%")
                print(f"   Discovery rate: {(self.total_discoveries/((time.time()-self._start_time)/3600)):.1f} per hour")
                
                # Wait between batches (unless shutting down)
                if self.running and self.batch_interval > 0:
                    print(f"\n⏸️  Waiting {self.batch_interval} seconds before next batch...")
                    for i in range(self.batch_interval):
                        if not self.running:
                            break
                        time.sleep(1)
                        if (i + 1) % 10 == 0:
                            print(f"   {self.batch_interval - i - 1} seconds remaining...")
                
            except KeyboardInterrupt:
                print("⏹️  Batch interrupted by user")
                self.running = False
                
            except Exception as e:
                print(f"❌ Batch error: {e}")
                print("🔄 Continuing to next batch in 30 seconds...")
                if self.running:
                    time.sleep(30)
        
        # Final summary
        total_time = (time.time() - self._start_time) / 3600
        print(f"\n🏁 CONTINUOUS DISCOVERY COMPLETED")
        print("=" * 70)
        print(f"📊 FINAL STATISTICS:")
        print(f"   Batches completed: {self.batch_count}")
        print(f"   Total discoveries: {self.total_discoveries}")
        print(f"   Total sequences: {self.total_sequences}")
        print(f"   Total runtime: {total_time:.1f} hours")
        print(f"   Overall success rate: {((self.total_discoveries/self.total_sequences)*100):.1f}%")
        print(f"   Discovery rate: {(self.total_discoveries/total_time):.1f} per hour")
        print("=" * 70)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Continuous Physics-Accurate Therapeutic Discovery",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--batch-size", 
        type=int, 
        default=10,
        help="Number of discoveries per batch"
    )
    
    parser.add_argument(
        "--batch-interval", 
        type=int, 
        default=60,
        help="Seconds to wait between batches (0 = no delay)"
    )
    
    args = parser.parse_args()
    
    # Create and run continuous discovery
    engine = ContinuousDiscoveryEngine(
        batch_size=args.batch_size,
        batch_interval=args.batch_interval
    )
    
    engine._start_time = time.time()
    engine.run_continuous_discovery()

if __name__ == "__main__":
    main()

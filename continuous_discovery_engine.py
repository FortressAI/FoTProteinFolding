#!/usr/bin/env python3
"""
CONTINUOUS DISCOVERY ENGINE - PRODUCTION READY
Scientifically validated continuous protein discovery system

🎯 PRODUCTION FEATURES:
- Continuous operation with configurable batches
- Automatic resource monitoring and scaling
- Crash recovery and error handling
- Real-time progress reporting
- Automatic file management and cleanup
- Memory optimization for long runs

Author: FoT Research Team
Purpose: Scalable therapeutic discovery for saving lives
"""

import json
import time
import signal
import logging
import argparse
import traceback
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import psutil
import gc

from validated_discovery_system import ValidatedDiscoverySystem, ValidatedDiscovery

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] %(message)s',
    handlers=[
        logging.FileHandler('continuous_discovery.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ContinuousConfig:
    """Configuration for continuous discovery"""
    batch_size: int = 10
    batch_interval_seconds: int = 300  # 5 minutes between batches
    max_attempts_per_batch: int = 100
    min_validation_score: float = 0.8
    min_therapeutic_potential: float = 0.6
    max_memory_usage_gb: float = None  # Auto-detect system memory
    max_cpu_usage_percent: float = 90.0  # Use 90% of available CPU
    output_dir: Path = Path("continuous_discoveries")
    archive_after_hours: int = 24
    cleanup_interval_batches: int = 10

@dataclass
class BatchResult:
    """Result of a discovery batch"""
    batch_id: str
    start_time: str
    end_time: str
    discoveries_found: int
    attempts_made: int
    success_rate: float
    avg_validation_score: float
    system_resources: Dict[str, Any]
    error_count: int
    discoveries: List[ValidatedDiscovery]

class ContinuousDiscoveryEngine:
    """Production-ready continuous discovery system"""
    
    def __init__(self, config: ContinuousConfig):
        self.config = config
        self.running = False
        self.total_discoveries = 0
        self.total_batches = 0
        self.total_attempts = 0
        self.start_time = None
        
        # Create output directories
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        (self.config.output_dir / "batches").mkdir(exist_ok=True)
        (self.config.output_dir / "archives").mkdir(exist_ok=True)
        (self.config.output_dir / "discoveries").mkdir(exist_ok=True)
        
        # Initialize discovery system
        self.discovery_system = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Auto-detect system capabilities
        total_memory_gb = psutil.virtual_memory().total / (1024**3)
        if config.max_memory_usage_gb is None:
            # Use 85% of total system memory
            config.max_memory_usage_gb = total_memory_gb * 0.85
        
        # Performance monitoring
        self.resource_monitor = ResourceMonitor(
            max_memory_gb=config.max_memory_usage_gb,
            max_cpu_percent=config.max_cpu_usage_percent
        )
        
        logger.info("🚀 ContinuousDiscoveryEngine initialized")
        logger.info(f"💾 System Memory: {total_memory_gb:.1f} GB total, using up to {config.max_memory_usage_gb:.1f} GB")
        logger.info(f"📊 Config: {config.batch_size} discoveries per batch, {config.batch_interval_seconds}s intervals")
    
    def start_continuous_discovery(self):
        """Start continuous discovery operation"""
        
        logger.info("🔄 Starting continuous discovery...")
        self.running = True
        self.start_time = datetime.now()
        
        try:
            batch_count = 0
            
            while self.running:
                batch_count += 1
                
                # Check system resources
                if not self.resource_monitor.check_resources():
                    logger.warning("⚠️ System resources too high, waiting for cooldown...")
                    time.sleep(60)
                    continue
                
                # Run discovery batch
                logger.info(f"🧬 Starting batch {batch_count}...")
                batch_result = self._run_discovery_batch(batch_count)
                
                # Process results
                self._process_batch_result(batch_result)
                
                # Cleanup if needed
                if batch_count % self.config.cleanup_interval_batches == 0:
                    self._cleanup_old_files()
                    gc.collect()  # Force garbage collection
                
                # Wait for next batch
                if self.running:
                    logger.info(f"⏰ Waiting {self.config.batch_interval_seconds}s for next batch...")
                    time.sleep(self.config.batch_interval_seconds)
        
        except Exception as e:
            logger.error(f"❌ Critical error in continuous discovery: {str(e)}")
            logger.error(traceback.format_exc())
        
        finally:
            self._shutdown()
    
    def _run_discovery_batch(self, batch_id: int) -> BatchResult:
        """Run a single discovery batch"""
        
        batch_start = datetime.now()
        
        try:
            # Initialize fresh discovery system for each batch
            self.discovery_system = ValidatedDiscoverySystem(
                output_dir=self.config.output_dir / "batches" / f"batch_{batch_id:06d}",
                min_validation_score=self.config.min_validation_score,
                min_therapeutic_potential=self.config.min_therapeutic_potential
            )
            
            # Run discovery
            results = self.discovery_system.run_validated_discovery(
                max_attempts=self.config.max_attempts_per_batch,
                target_discoveries=self.config.batch_size
            )
            
            # Extract discoveries
            discoveries = []
            if 'discoveries' in results and results['discoveries']:
                for discovery_data in results['discoveries']:
                    # Convert dict back to ValidatedDiscovery object
                    discovery = ValidatedDiscovery(**discovery_data)
                    discoveries.append(discovery)
            
            discoveries_found = len(discoveries)
            attempts_made = results.get('summary', {}).get('generation_attempts', 0)
            success_rate = discoveries_found / max(attempts_made, 1)
            
            # Calculate average validation score
            avg_validation_score = 0.0
            if discoveries:
                avg_validation_score = sum(d.validation_score for d in discoveries) / len(discoveries)
            
            batch_end = datetime.now()
            
            # Update totals
            self.total_discoveries += discoveries_found
            self.total_batches += 1
            self.total_attempts += attempts_made
            
            logger.info(f"✅ Batch {batch_id} complete: {discoveries_found} discoveries, {success_rate:.1%} success rate")
            
            return BatchResult(
                batch_id=f"batch_{batch_id:06d}",
                start_time=batch_start.isoformat(),
                end_time=batch_end.isoformat(),
                discoveries_found=discoveries_found,
                attempts_made=attempts_made,
                success_rate=success_rate,
                avg_validation_score=avg_validation_score,
                system_resources=self.resource_monitor.get_current_usage(),
                error_count=0,
                discoveries=discoveries
            )
        
        except Exception as e:
            logger.error(f"❌ Error in batch {batch_id}: {str(e)}")
            
            return BatchResult(
                batch_id=f"batch_{batch_id:06d}",
                start_time=batch_start.isoformat(),
                end_time=datetime.now().isoformat(),
                discoveries_found=0,
                attempts_made=0,
                success_rate=0.0,
                avg_validation_score=0.0,
                system_resources=self.resource_monitor.get_current_usage(),
                error_count=1,
                discoveries=[]
            )
    
    def _process_batch_result(self, result: BatchResult):
        """Process and save batch results"""
        
        # Save batch summary
        batch_file = self.config.output_dir / "batches" / f"{result.batch_id}_summary.json"
        with open(batch_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        
        # Save individual discoveries to main discoveries folder
        for discovery in result.discoveries:
            discovery_file = self.config.output_dir / "discoveries" / f"{discovery.discovery_id}.json"
            with open(discovery_file, 'w') as f:
                json.dump(asdict(discovery), f, indent=2, default=str)
        
        # Update continuous summary
        self._update_continuous_summary()
        
        # Report progress
        elapsed_time = (datetime.now() - self.start_time).total_seconds() / 3600  # hours
        discoveries_per_hour = self.total_discoveries / max(elapsed_time, 0.01)
        
        logger.info(f"📊 PROGRESS: {self.total_discoveries} total discoveries in {self.total_batches} batches")
        logger.info(f"⏱️ Rate: {discoveries_per_hour:.1f} discoveries/hour, {self.total_attempts} total attempts")
        
        # Archive old batches if needed
        if elapsed_time > self.config.archive_after_hours:
            self._archive_old_batches()
    
    def _update_continuous_summary(self):
        """Update the continuous summary file"""
        
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        
        summary = {
            'continuous_operation': {
                'start_time': self.start_time.isoformat(),
                'current_time': datetime.now().isoformat(),
                'elapsed_hours': elapsed_time / 3600,
                'running': self.running
            },
            'totals': {
                'discoveries': self.total_discoveries,
                'batches': self.total_batches,
                'attempts': self.total_attempts,
                'overall_success_rate': self.total_discoveries / max(self.total_attempts, 1)
            },
            'rates': {
                'discoveries_per_hour': self.total_discoveries / max(elapsed_time / 3600, 0.01),
                'batches_per_hour': self.total_batches / max(elapsed_time / 3600, 0.01),
                'attempts_per_hour': self.total_attempts / max(elapsed_time / 3600, 0.01)
            },
            'system_status': {
                'memory_usage_gb': psutil.virtual_memory().used / (1024**3),
                'cpu_percent': psutil.cpu_percent(),
                'disk_usage_gb': psutil.disk_usage('.').used / (1024**3)
            },
            'configuration': asdict(self.config)
        }
        
        summary_file = self.config.output_dir / "continuous_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
    
    def _cleanup_old_files(self):
        """Clean up old temporary files"""
        
        logger.info("🧹 Performing cleanup...")
        
        # Clean up temporary batch files older than 1 hour
        cutoff_time = time.time() - 3600
        batch_dir = self.config.output_dir / "batches"
        
        cleaned_count = 0
        for file_path in batch_dir.glob("batch_*"):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                cleaned_count += 1
        
        if cleaned_count > 0:
            logger.info(f"🗑️ Cleaned up {cleaned_count} old files")
    
    def _archive_old_batches(self):
        """Archive old batch results"""
        
        logger.info("📦 Archiving old batches...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = self.config.output_dir / "archives" / f"archive_{timestamp}"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Move old batch files to archive
        batch_dir = self.config.output_dir / "batches"
        for file_path in batch_dir.glob("batch_*"):
            archive_path = archive_dir / file_path.name
            file_path.rename(archive_path)
        
        logger.info(f"📦 Archived batches to {archive_dir}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def _shutdown(self):
        """Graceful shutdown"""
        
        logger.info("🔄 Shutting down continuous discovery...")
        
        # Update final summary
        self._update_continuous_summary()
        
        # Report final statistics
        if self.start_time:
            elapsed_time = (datetime.now() - self.start_time).total_seconds() / 3600
            logger.info(f"📊 FINAL STATS:")
            logger.info(f"   Total discoveries: {self.total_discoveries}")
            logger.info(f"   Total batches: {self.total_batches}")
            logger.info(f"   Total attempts: {self.total_attempts}")
            logger.info(f"   Runtime: {elapsed_time:.1f} hours")
            logger.info(f"   Rate: {self.total_discoveries / max(elapsed_time, 0.01):.1f} discoveries/hour")
        
        logger.info("✅ Shutdown complete")

class ResourceMonitor:
    """Monitor system resources"""
    
    def __init__(self, max_memory_gb: float, max_cpu_percent: float):
        self.max_memory_gb = max_memory_gb
        self.max_cpu_percent = max_cpu_percent
    
    def check_resources(self) -> bool:
        """Check if system resources are within limits"""
        
        memory_gb = psutil.virtual_memory().used / (1024**3)
        cpu_percent = psutil.cpu_percent(interval=1)
        
        if memory_gb > self.max_memory_gb:
            logger.warning(f"⚠️ Memory usage too high: {memory_gb:.1f} GB > {self.max_memory_gb} GB")
            return False
        
        if cpu_percent > self.max_cpu_percent:
            logger.warning(f"⚠️ CPU usage too high: {cpu_percent:.1f}% > {self.max_cpu_percent}%")
            return False
        
        return True
    
    def get_current_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        
        return {
            'memory_gb': psutil.virtual_memory().used / (1024**3),
            'memory_percent': psutil.virtual_memory().percent,
            'cpu_percent': psutil.cpu_percent(),
            'disk_gb': psutil.disk_usage('.').used / (1024**3),
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description="Continuous Discovery Engine")
    parser.add_argument("--batch-size", type=int, default=10, help="Discoveries per batch")
    parser.add_argument("--interval", type=int, default=300, help="Seconds between batches")
    parser.add_argument("--max-attempts", type=int, default=100, help="Max attempts per batch")
    parser.add_argument("--validation-score", type=float, default=0.8, help="Min validation score")
    parser.add_argument("--therapeutic-potential", type=float, default=0.6, help="Min therapeutic potential")
    parser.add_argument("--max-cpu", type=float, default=90.0, help="Max CPU usage (%)")
    parser.add_argument("--output-dir", type=str, default="continuous_discoveries", help="Output directory")
    
    args = parser.parse_args()
    
    # Create configuration
    config = ContinuousConfig(
        batch_size=args.batch_size,
        batch_interval_seconds=args.interval,
        max_attempts_per_batch=args.max_attempts,
        min_validation_score=args.validation_score,
        min_therapeutic_potential=args.therapeutic_potential,
        max_memory_usage_gb=None,  # Auto-detect
        max_cpu_usage_percent=args.max_cpu,
        output_dir=Path(args.output_dir)
    )
    
    # Get system info for display
    import psutil
    total_memory_gb = psutil.virtual_memory().total / (1024**3)
    
    print("🚀 CONTINUOUS DISCOVERY ENGINE")
    print("🎯 PRODUCTION-READY SCALING SYSTEM")
    print("=" * 60)
    print(f"💾 System: {total_memory_gb:.1f} GB RAM (auto-scaling enabled)")
    print(f"📊 Configuration:")
    print(f"   Batch size: {config.batch_size} discoveries")
    print(f"   Interval: {config.batch_interval_seconds} seconds")
    print(f"   Max attempts per batch: {config.max_attempts_per_batch}")
    print(f"   Validation threshold: {config.min_validation_score:.2f}")
    print(f"   Therapeutic threshold: {config.min_therapeutic_potential:.2f}")
    print(f"   CPU limit: {config.max_cpu_usage_percent}% CPU")
    print(f"   Output: {config.output_dir}")
    print("\n🔄 Starting continuous operation...")
    print("   Press Ctrl+C to stop gracefully")
    print("=" * 60)
    
    # Start continuous discovery
    engine = ContinuousDiscoveryEngine(config)
    engine.start_continuous_discovery()

if __name__ == "__main__":
    main()

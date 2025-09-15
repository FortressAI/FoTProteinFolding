#!/usr/bin/env python3
"""
Continuous Prior Art Pipeline
Automated system for continuous discovery and immediate prior art publication
"""

import json
import time
import threading
import signal
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
import schedule
import subprocess

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from massive_scale_discovery import MassiveScaleDiscoveryEngine, ScaledDiscoveryConfig
from prior_art_publication_system import PriorArtPublicationSystem

@dataclass
class ContinuousPipelineConfig:
    """Configuration for continuous prior art pipeline"""
    
    # Discovery parameters
    sequences_per_batch: int = 1000      # Discover 1000 sequences per batch
    discovery_interval_hours: int = 6    # Run discovery every 6 hours
    max_daily_sequences: int = 10000     # Maximum sequences per day
    
    # Publication parameters
    publish_immediately: bool = True     # Publish as soon as discovered
    min_sequences_for_publication: int = 100  # Minimum sequences to trigger publication
    
    # Quality thresholds
    min_research_score: float = 0.5
    min_novelty_score: float = 0.6
    
    # System parameters
    max_workers: int = None              # Use all available cores
    enable_monitoring: bool = True       # Enable system monitoring
    
    # Storage
    base_output_dir: Path = Path("continuous_prior_art")
    log_file: Path = Path("continuous_pipeline.log")

class ContinuousPriorArtPipeline:
    """Automated pipeline for continuous discovery and prior art publication"""
    
    def __init__(self, config: ContinuousPipelineConfig = None):
        self.config = config or ContinuousPipelineConfig()
        self.running = False
        self.stats = {
            "pipeline_start_time": None,
            "total_discoveries": 0,
            "total_publications": 0,
            "sequences_today": 0,
            "last_discovery_run": None,
            "last_publication": None,
            "daily_reset_time": None
        }
        
        # Initialize directories
        self.config.base_output_dir.mkdir(exist_ok=True)
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Thread-safe logging
        self.log_lock = threading.Lock()
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n⚠️ Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def log_message(self, message: str, level: str = "INFO"):
        """Thread-safe logging with timestamps"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {level}: {message}"
        
        with self.log_lock:
            print(log_line)
            
            # Append to log file
            with open(self.config.log_file, 'a') as f:
                f.write(log_line + "\n")
    
    def _reset_daily_counters(self):
        """Reset daily counters at midnight"""
        now = datetime.now()
        if (self.stats["daily_reset_time"] is None or 
            now.date() > self.stats["daily_reset_time"].date()):
            
            self.stats["sequences_today"] = 0
            self.stats["daily_reset_time"] = now
            self.log_message(f"Daily counters reset for {now.date()}")
    
    def run_discovery_batch(self) -> Dict[str, Any]:
        """Run a single discovery batch"""
        
        self.log_message("🧬 Starting discovery batch...")
        
        # Check daily limits
        self._reset_daily_counters()
        if self.stats["sequences_today"] >= self.config.max_daily_sequences:
            self.log_message(f"⚠️ Daily limit reached ({self.config.max_daily_sequences} sequences)")
            return {"status": "daily_limit_reached", "discoveries": []}
        
        # Calculate sequences to discover (respect daily limit)
        remaining_today = self.config.max_daily_sequences - self.stats["sequences_today"]
        sequences_to_discover = min(self.config.sequences_per_batch, remaining_today)
        
        try:
            # Configure discovery engine
            discovery_config = ScaledDiscoveryConfig(
                target_sequences=sequences_to_discover,
                batch_size=50,  # Smaller batches for continuous operation
                max_workers=self.config.max_workers,
                min_research_score=self.config.min_research_score,
                min_novelty_score=self.config.min_novelty_score,
                publication_batch_size=sequences_to_discover,  # Publish everything
                create_prior_art_docs=True,
                output_base_dir=self.config.base_output_dir / "discoveries"
            )
            
            # Run discovery
            engine = MassiveScaleDiscoveryEngine(discovery_config)
            results = engine.run_massive_scale_discovery()
            
            # Update statistics
            self.stats["total_discoveries"] += results.get("valid_discoveries", 0)
            self.stats["sequences_today"] += results.get("total_processed", 0)
            self.stats["last_discovery_run"] = datetime.now()
            
            self.log_message(f"✅ Discovery batch complete: {results.get('valid_discoveries', 0)} valid discoveries")
            
            return {
                "status": "success",
                "discoveries_found": results.get("valid_discoveries", 0),
                "total_processed": results.get("total_processed", 0),
                "discovery_rate": results.get("valid_discoveries", 0) / max(results.get("total_processed", 1), 1)
            }
            
        except Exception as e:
            self.log_message(f"❌ Discovery batch failed: {e}", "ERROR")
            return {"status": "error", "error": str(e)}
    
    def collect_pending_discoveries(self) -> List[Dict[str, Any]]:
        """Collect all unpublished discoveries"""
        
        discoveries = []
        
        # Look for discovery files in the continuous output directory
        discovery_dir = self.config.base_output_dir / "discoveries"
        if discovery_dir.exists():
            for json_file in discovery_dir.glob("**/therapeutic_discoveries.json"):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        if "discoveries" in data:
                            discoveries.extend(data["discoveries"])
                except Exception as e:
                    self.log_message(f"⚠️ Error loading {json_file}: {e}", "WARNING")
        
        # Also check existing discovery files
        for discovery_dir_name in ["massive_scale_discoveries", "prior_art_publication"]:
            discovery_path = Path(discovery_dir_name)
            if discovery_path.exists():
                for json_file in discovery_path.glob("**/therapeutic_discoveries.json"):
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            if "discoveries" in data:
                                discoveries.extend(data["discoveries"])
                    except Exception as e:
                        self.log_message(f"⚠️ Error loading {json_file}: {e}", "WARNING")
        
        # Remove duplicates by sequence
        unique_discoveries = {}
        for discovery in discoveries:
            sequence = discovery.get("sequence", "")
            if sequence and sequence not in unique_discoveries:
                unique_discoveries[sequence] = discovery
        
        return list(unique_discoveries.values())
    
    def run_publication_batch(self, discoveries: List[Dict[str, Any]]) -> bool:
        """Run publication for a batch of discoveries"""
        
        if len(discoveries) < self.config.min_sequences_for_publication:
            self.log_message(f"⚠️ Insufficient discoveries for publication ({len(discoveries)} < {self.config.min_sequences_for_publication})")
            return False
        
        self.log_message(f"📢 Starting publication batch for {len(discoveries)} discoveries...")
        
        try:
            # Initialize publication system
            publisher = PriorArtPublicationSystem()
            
            # Execute comprehensive publication
            results = publisher.execute_comprehensive_publication(discoveries)
            
            # Update statistics
            self.stats["total_publications"] += 1
            self.stats["last_publication"] = datetime.now()
            
            self.log_message(f"✅ Publication complete: {results['total_sequences_published']} sequences published")
            self.log_message(f"📦 Package ID: {results['package_id']}")
            self.log_message(f"🔒 Hash: {results['package_hash'][:16]}...")
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Publication failed: {e}", "ERROR")
            return False
    
    def run_discovery_and_publication_cycle(self):
        """Run one complete discovery and publication cycle"""
        
        self.log_message("🔄 Starting discovery and publication cycle...")
        
        # Run discovery
        discovery_results = self.run_discovery_batch()
        
        if discovery_results["status"] == "success" and discovery_results["discoveries_found"] > 0:
            self.log_message(f"🧬 Discovery successful: {discovery_results['discoveries_found']} new sequences")
            
            # Collect all pending discoveries for publication
            if self.config.publish_immediately:
                pending_discoveries = self.collect_pending_discoveries()
                
                if len(pending_discoveries) >= self.config.min_sequences_for_publication:
                    self.log_message(f"📢 Publishing {len(pending_discoveries)} total discoveries...")
                    publication_success = self.run_publication_batch(pending_discoveries)
                    
                    if publication_success:
                        self.log_message("✅ Publication cycle complete")
                        
                        # Clean up published discovery files to avoid republishing
                        self._cleanup_published_files()
                    else:
                        self.log_message("❌ Publication failed, will retry next cycle")
                else:
                    self.log_message(f"⏳ Waiting for more discoveries before publication ({len(pending_discoveries)} available)")
        else:
            self.log_message(f"⚠️ Discovery cycle status: {discovery_results['status']}")
    
    def _cleanup_published_files(self):
        """Clean up discovery files after successful publication"""
        
        try:
            # Move discovery files to published archive
            published_dir = self.config.base_output_dir / "published_archive"
            published_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_dir = published_dir / f"published_{timestamp}"
            
            # Move discovery files
            discovery_dir = self.config.base_output_dir / "discoveries"
            if discovery_dir.exists():
                import shutil
                shutil.move(str(discovery_dir), str(archive_dir))
                
            self.log_message(f"📁 Discovery files archived to {archive_dir}")
            
        except Exception as e:
            self.log_message(f"⚠️ Cleanup warning: {e}", "WARNING")
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate current status report"""
        
        now = datetime.now()
        uptime = now - self.stats["pipeline_start_time"] if self.stats["pipeline_start_time"] else timedelta(0)
        
        return {
            "pipeline_status": "RUNNING" if self.running else "STOPPED",
            "uptime_hours": uptime.total_seconds() / 3600,
            "total_discoveries": self.stats["total_discoveries"],
            "total_publications": self.stats["total_publications"],
            "sequences_today": self.stats["sequences_today"],
            "daily_limit": self.config.max_daily_sequences,
            "last_discovery_run": self.stats["last_discovery_run"].isoformat() if self.stats["last_discovery_run"] else None,
            "last_publication": self.stats["last_publication"].isoformat() if self.stats["last_publication"] else None,
            "next_scheduled_run": self._get_next_scheduled_time(),
            "discovery_rate_per_hour": self.stats["total_discoveries"] / max(uptime.total_seconds() / 3600, 0.1),
            "configuration": {
                "sequences_per_batch": self.config.sequences_per_batch,
                "discovery_interval_hours": self.config.discovery_interval_hours,
                "publish_immediately": self.config.publish_immediately
            }
        }
    
    def _get_next_scheduled_time(self) -> str:
        """Get next scheduled discovery time"""
        
        if self.stats["last_discovery_run"]:
            next_run = self.stats["last_discovery_run"] + timedelta(hours=self.config.discovery_interval_hours)
            return next_run.isoformat()
        else:
            return "IMMEDIATE"
    
    def run_continuous_pipeline(self):
        """Run the continuous discovery and publication pipeline"""
        
        self.log_message("🚀 STARTING CONTINUOUS PRIOR ART PIPELINE")
        self.log_message("=" * 70)
        self.log_message(f"🎯 Target: {self.config.sequences_per_batch} sequences every {self.config.discovery_interval_hours} hours")
        self.log_message(f"📊 Daily limit: {self.config.max_daily_sequences} sequences")
        self.log_message(f"📢 Immediate publication: {'ENABLED' if self.config.publish_immediately else 'DISABLED'}")
        self.log_message(f"💾 Output directory: {self.config.base_output_dir}")
        
        self.running = True
        self.stats["pipeline_start_time"] = datetime.now()
        
        # Schedule discovery runs
        schedule.every(self.config.discovery_interval_hours).hours.do(self.run_discovery_and_publication_cycle)
        
        # Run initial discovery immediately
        self.log_message("🧬 Running initial discovery batch...")
        self.run_discovery_and_publication_cycle()
        
        # Main loop
        while self.running:
            try:
                # Run scheduled tasks
                schedule.run_pending()
                
                # Status update every hour
                if datetime.now().minute == 0:  # Top of the hour
                    status = self.generate_status_report()
                    self.log_message(f"📊 Status: {status['total_discoveries']} discoveries, {status['total_publications']} publications, {status['uptime_hours']:.1f}h uptime")
                
                # Sleep for 1 minute before checking again
                time.sleep(60)
                
            except KeyboardInterrupt:
                self.log_message("⚠️ Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                self.log_message(f"❌ Pipeline error: {e}", "ERROR")
                # Continue running despite errors
                time.sleep(300)  # Wait 5 minutes before retrying
        
        self.running = False
        self.log_message("🛑 Continuous pipeline stopped")
        
        # Final status report
        final_status = self.generate_status_report()
        self.log_message("📊 FINAL STATISTICS:")
        self.log_message(f"   Total discoveries: {final_status['total_discoveries']}")
        self.log_message(f"   Total publications: {final_status['total_publications']}")
        self.log_message(f"   Uptime: {final_status['uptime_hours']:.2f} hours")
        self.log_message(f"   Discovery rate: {final_status['discovery_rate_per_hour']:.1f} sequences/hour")

def main():
    """Run continuous prior art pipeline"""
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Continuous Prior Art Pipeline")
    parser.add_argument("--sequences-per-batch", type=int, default=1000, help="Sequences per discovery batch")
    parser.add_argument("--interval", type=int, default=6, help="Discovery interval in hours")
    parser.add_argument("--daily-limit", type=int, default=10000, help="Maximum sequences per day")
    parser.add_argument("--min-publication", type=int, default=100, help="Minimum sequences for publication")
    parser.add_argument("--no-immediate-publish", action="store_true", help="Disable immediate publication")
    parser.add_argument("--output-dir", type=str, default="continuous_prior_art", help="Output directory")
    
    args = parser.parse_args()
    
    # Configure pipeline
    config = ContinuousPipelineConfig(
        sequences_per_batch=args.sequences_per_batch,
        discovery_interval_hours=args.interval,
        max_daily_sequences=args.daily_limit,
        min_sequences_for_publication=args.min_publication,
        publish_immediately=not args.no_immediate_publish,
        base_output_dir=Path(args.output_dir)
    )
    
    # Create and run pipeline
    pipeline = ContinuousPriorArtPipeline(config)
    
    try:
        pipeline.run_continuous_pipeline()
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

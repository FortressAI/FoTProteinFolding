#!/usr/bin/env python3
"""
M4 BEAST MODE LAUNCHER
Launches multiple scaled M4 Neo4j discovery processes and actively monitors scaling
Designed to fully utilize M4 Mac Pro with 128GB RAM and 40-core GPU
"""

import subprocess
import time
import psutil
import signal
import sys
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class M4BeastModeLauncher:
    """Launches and manages multiple M4 discovery processes for maximum throughput"""
    
    def __init__(self):
        self.processes = []
        self.running = True
        
        # System specs
        self.total_memory_gb = psutil.virtual_memory().total / (1024**3)
        self.cpu_count = psutil.cpu_count()
        
        # M4 Mac Pro Beast Mode parameters
        if self.total_memory_gb >= 100:  # M4 Mac Pro detected
            self.max_processes = min(8, self.cpu_count // 2)  # Up to 8 parallel processes
            self.target_memory_usage = 80  # Use 80% of 128GB
            self.sequences_per_process = 512  # Massive sequences per process
            logger.info(f"🚀 M4 MAC PRO BEAST MODE DETECTED!")
            logger.info(f"   Total RAM: {self.total_memory_gb:.1f} GB")
            logger.info(f"   CPU Cores: {self.cpu_count}")
            logger.info(f"   Max Processes: {self.max_processes}")
        else:
            self.max_processes = 2
            self.target_memory_usage = 70
            self.sequences_per_process = 128
            logger.info(f"Standard system: {self.total_memory_gb:.1f} GB")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum} - shutting down M4 Beast Mode...")
        self.running = False
        self._shutdown_all_processes()
        sys.exit(0)
    
    def _launch_discovery_process(self) -> subprocess.Popen:
        """Launch a single M4 Neo4j discovery process"""
        
        cmd = ['python3', 'm4_neo4j_accelerated_discovery.py']
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            logger.info(f"🚀 Launched M4 discovery process: PID {process.pid}")
            return process
        except Exception as e:
            logger.error(f"❌ Failed to launch discovery process: {e}")
            return None
    
    def _monitor_system_resources(self) -> Dict[str, float]:
        """Monitor current system resource usage"""
        
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'cpu_percent': cpu_percent,
            'active_processes': len([p for p in self.processes if p and p.poll() is None])
        }
    
    def _scale_processes(self, stats: Dict[str, float]):
        """Dynamically scale the number of processes based on resource usage"""
        
        memory_percent = stats['memory_percent']
        available_memory_gb = stats['memory_available_gb']
        active_processes = stats['active_processes']
        
        # M4 Mac Pro aggressive scaling
        if self.total_memory_gb >= 100:
            # Scale up aggressively if resources available
            if (memory_percent < 75 and 
                available_memory_gb > 30 and 
                active_processes < self.max_processes):
                
                logger.info(f"🚀 M4 BEAST MODE - Scaling UP: {active_processes} → {active_processes + 1}")
                new_process = self._launch_discovery_process()
                if new_process:
                    self.processes.append(new_process)
            
            # Only scale down if extremely high memory usage
            elif memory_percent > 90 and active_processes > 1:
                logger.warning(f"⚠️ High memory usage - scaling DOWN: {active_processes} → {active_processes - 1}")
                self._terminate_oldest_process()
        else:
            # Standard scaling for non-M4 systems
            if (memory_percent < 70 and 
                available_memory_gb > 10 and 
                active_processes < self.max_processes):
                
                new_process = self._launch_discovery_process()
                if new_process:
                    self.processes.append(new_process)
            
            elif memory_percent > 85 and active_processes > 1:
                self._terminate_oldest_process()
    
    def _terminate_oldest_process(self):
        """Terminate the oldest running process"""
        
        for i, process in enumerate(self.processes):
            if process and process.poll() is None:  # Process is still running
                logger.info(f"🛑 Terminating process PID {process.pid}")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                self.processes.pop(i)
                break
    
    def _cleanup_dead_processes(self):
        """Remove dead processes from the list"""
        
        self.processes = [p for p in self.processes if p and p.poll() is None]
    
    def _shutdown_all_processes(self):
        """Shutdown all discovery processes"""
        
        logger.info(f"🛑 Shutting down {len(self.processes)} discovery processes...")
        
        for process in self.processes:
            if process and process.poll() is None:
                logger.info(f"🛑 Terminating PID {process.pid}")
                process.terminate()
        
        # Wait for graceful shutdown
        time.sleep(3)
        
        # Force kill if necessary
        for process in self.processes:
            if process and process.poll() is None:
                logger.warning(f"🔥 Force killing PID {process.pid}")
                process.kill()
        
        self.processes.clear()
    
    def _print_status(self, stats: Dict[str, float]):
        """Print current status"""
        
        print(f"\n🍎 M4 BEAST MODE STATUS")
        print(f"=" * 50)
        print(f"⏰ {time.strftime('%H:%M:%S')}")
        print(f"🔄 Active Processes: {stats['active_processes']}/{self.max_processes}")
        print(f"💾 Memory Usage: {stats['memory_percent']:.1f}% "
              f"(Available: {stats['memory_available_gb']:.1f} GB)")
        print(f"🔥 CPU Usage: {stats['cpu_percent']:.1f}%")
        print(f"🎯 Target Memory: {self.target_memory_usage}%")
        
        if self.total_memory_gb >= 100:
            estimated_sequences_per_hour = stats['active_processes'] * self.sequences_per_process * 60
            print(f"⚡ Estimated Throughput: {estimated_sequences_per_hour:,} sequences/hour")
        
        print(f"🔄 Next check in 30 seconds...")
    
    def run_beast_mode(self):
        """Run M4 Beast Mode with continuous scaling"""
        
        logger.info(f"🚀 STARTING M4 BEAST MODE LAUNCHER")
        logger.info(f"   System: {self.total_memory_gb:.1f} GB RAM, {self.cpu_count} CPU cores")
        logger.info(f"   Max processes: {self.max_processes}")
        logger.info(f"   Target memory usage: {self.target_memory_usage}%")
        
        # Launch initial process
        initial_process = self._launch_discovery_process()
        if initial_process:
            self.processes.append(initial_process)
        
        # Main monitoring loop
        cycle = 0
        while self.running:
            try:
                cycle += 1
                
                # Monitor system resources
                stats = self._monitor_system_resources()
                
                # Clean up dead processes
                self._cleanup_dead_processes()
                
                # Scale processes based on resources
                self._scale_processes(stats)
                
                # Update stats after scaling
                stats = self._monitor_system_resources()
                
                # Print status every 6 cycles (3 minutes)
                if cycle % 6 == 0:
                    self._print_status(stats)
                
                # Sleep for 30 seconds
                time.sleep(30)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(10)
        
        # Cleanup
        self._shutdown_all_processes()
        logger.info("✅ M4 Beast Mode launcher stopped")

def main():
    """Main entry point"""
    
    print("🍎 M4 MAC PRO BEAST MODE LAUNCHER")
    print("=" * 60)
    print("Designed to maximize M4 Mac Pro utilization")
    print("128GB RAM + 40-core GPU + Neo4j vQbit Knowledge Graph")
    print("=" * 60)
    
    launcher = M4BeastModeLauncher()
    launcher.run_beast_mode()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
DISCOVERY STATUS MONITOR
Real-time monitoring of continuous discovery operations
"""

import json
import time
import os
import signal
from pathlib import Path
from datetime import datetime

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_time(seconds):
    """Format seconds into human readable time"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def display_status():
    """Display current discovery status"""
    
    status_file = Path("continuous_discoveries/continuous_summary.json")
    
    if not status_file.exists():
        print("📊 DISCOVERY STATUS MONITOR")
        print("=" * 50)
        print("❌ No active continuous discovery found")
        print("\nTo start discovery:")
        print("   python3 launch_continuous_discovery.py")
        return False
    
    try:
        with open(status_file) as f:
            summary = json.load(f)
        
        # Check if still running
        running = summary['continuous_operation']['running']
        start_time = datetime.fromisoformat(summary['continuous_operation']['start_time'])
        current_time = datetime.fromisoformat(summary['continuous_operation']['current_time'])
        
        # Time since last update
        now = datetime.now()
        time_since_update = (now - current_time).total_seconds()
        
        status_indicator = "🟢 RUNNING" if running and time_since_update < 600 else "🔴 STOPPED"
        
        clear_screen()
        print("📊 DISCOVERY STATUS MONITOR")
        print("=" * 50)
        print(f"Status: {status_indicator}")
        print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Runtime: {format_time(summary['continuous_operation']['elapsed_hours'] * 3600)}")
        print()
        
        print("📈 PERFORMANCE METRICS:")
        print(f"   Total Discoveries: {summary['totals']['discoveries']:,}")
        print(f"   Total Batches: {summary['totals']['batches']:,}")
        print(f"   Total Attempts: {summary['totals']['attempts']:,}")
        print(f"   Success Rate: {summary['totals']['overall_success_rate']:.2%}")
        print()
        
        print("⚡ CURRENT RATES:")
        print(f"   Discoveries/Hour: {summary['rates']['discoveries_per_hour']:.1f}")
        print(f"   Batches/Hour: {summary['rates']['batches_per_hour']:.1f}")
        print(f"   Attempts/Hour: {summary['rates']['attempts_per_hour']:.1f}")
        print()
        
        print("💻 SYSTEM RESOURCES:")
        print(f"   Memory Usage: {summary['system_status']['memory_usage_gb']:.1f} GB")
        print(f"   CPU Usage: {summary['system_status']['cpu_percent']:.1f}%")
        print(f"   Disk Usage: {summary['system_status']['disk_usage_gb']:.1f} GB")
        print()
        
        print("⚙️ CONFIGURATION:")
        config = summary['configuration']
        print(f"   Batch Size: {config['batch_size']} discoveries")
        print(f"   Interval: {config['batch_interval_seconds']}s between batches")
        print(f"   Validation Score: ≥{config['min_validation_score']:.2f}")
        print(f"   Therapeutic Potential: ≥{config['min_therapeutic_potential']:.2f}")
        print()
        
        # Recent discoveries
        discoveries_dir = Path("continuous_discoveries/discoveries")
        if discoveries_dir.exists():
            recent_discoveries = sorted(
                discoveries_dir.glob("*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:5]
            
            if recent_discoveries:
                print("🔬 RECENT DISCOVERIES:")
                for discovery_file in recent_discoveries:
                    try:
                        with open(discovery_file) as f:
                            discovery = json.load(f)
                        
                        discovery_time = datetime.fromisoformat(discovery['analysis_timestamp'])
                        time_ago = (now - discovery_time).total_seconds()
                        
                        print(f"   {discovery['discovery_id']}: "
                              f"Score {discovery['validation_score']:.3f}, "
                              f"Therapeutic {discovery['therapeutic_potential']:.3f} "
                              f"({format_time(time_ago)} ago)")
                    except:
                        continue
                print()
        
        print("🔄 Press Ctrl+C to exit monitor")
        print(f"   Last updated: {format_time(time_since_update)} ago")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading status: {e}")
        return False

def main():
    """Main monitoring loop"""
    
    def signal_handler(signum, frame):
        clear_screen()
        print("👋 Discovery monitor stopped")
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        while True:
            if not display_status():
                time.sleep(5)
            else:
                time.sleep(10)  # Update every 10 seconds
    
    except KeyboardInterrupt:
        clear_screen()
        print("👋 Discovery monitor stopped")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
LAUNCH CONTINUOUS DISCOVERY - SIMPLE INTERFACE
Easy launcher for continuous discovery operations
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch continuous discovery with predefined configurations"""
    
    import psutil
    total_memory_gb = psutil.virtual_memory().total / (1024**3)
    cpu_count = psutil.cpu_count()
    
    print("🚀 CONTINUOUS DISCOVERY LAUNCHER")
    print("=" * 50)
    print(f"💾 System: {total_memory_gb:.1f} GB RAM, {cpu_count} CPU cores")
    print("🎯 Auto-scaling enabled - using 85% of available memory")
    print()
    print("Select operation mode:")
    print("1. 🔬 Research Mode (5 discoveries/batch, 5min intervals)")
    print("2. ⚡ Production Mode (15 discoveries/batch, 10min intervals)")  
    print("3. 🏭 Industrial Mode (50 discoveries/batch, 15min intervals)")
    print("4. 🚀 Maximum Performance (100 discoveries/batch, 30min intervals)")
    print("5. 🎯 Custom Configuration")
    print("6. 📊 View Current Status")
    print("7. 🛑 Stop Running Processes")
    print()
    
    choice = input("Enter choice (1-7): ").strip()
    
    if choice == "1":
        # Research mode
        cmd = [
            "python3", "continuous_discovery_engine.py",
            "--batch-size", "5",
            "--interval", "300",
            "--max-attempts", "50",
            "--validation-score", "0.8",
            "--therapeutic-potential", "0.6",
            "--max-cpu", "70.0"
        ]
        print("🔬 Starting Research Mode...")
        
    elif choice == "2":
        # Production mode  
        cmd = [
            "python3", "continuous_discovery_engine.py",
            "--batch-size", "15", 
            "--interval", "600",
            "--max-attempts", "150",
            "--validation-score", "0.8",
            "--therapeutic-potential", "0.6",
            "--max-cpu", "90.0"
        ]
        print("⚡ Starting Production Mode...")
        
    elif choice == "3":
        # Industrial mode
        cmd = [
            "python3", "continuous_discovery_engine.py",
            "--batch-size", "50",
            "--interval", "900", 
            "--max-attempts", "500",
            "--validation-score", "0.75",
            "--therapeutic-potential", "0.55",
            "--max-cpu", "95.0"
        ]
        print("🏭 Starting Industrial Mode...")
        
    elif choice == "4":
        # Maximum performance mode
        cmd = [
            "python3", "continuous_discovery_engine.py",
            "--batch-size", "100",
            "--interval", "1800",
            "--max-attempts", "1000", 
            "--validation-score", "0.75",
            "--therapeutic-potential", "0.5",
            "--max-cpu", "95.0"
        ]
        print("🚀 Starting Maximum Performance Mode...")
        
    elif choice == "5":
        # Custom configuration
        print("\n🎯 Custom Configuration:")
        batch_size = input("Batch size (discoveries per batch) [10]: ").strip() or "10"
        interval = input("Interval between batches (seconds) [600]: ").strip() or "600"
        max_attempts = input("Max attempts per batch [100]: ").strip() or "100"
        validation_score = input("Min validation score [0.8]: ").strip() or "0.8"
        therapeutic_potential = input("Min therapeutic potential [0.6]: ").strip() or "0.6"
        max_cpu = input("Max CPU usage (%) [90.0]: ").strip() or "90.0"
        
        cmd = [
            "python3", "continuous_discovery_engine.py",
            "--batch-size", batch_size,
            "--interval", interval,
            "--max-attempts", max_attempts,
            "--validation-score", validation_score,
            "--therapeutic-potential", therapeutic_potential,
            "--max-cpu", max_cpu
        ]
        print("🎯 Starting Custom Configuration...")
        
    elif choice == "6":
        # View status
        status_file = Path("continuous_discoveries/continuous_summary.json")
        if status_file.exists():
            import json
            with open(status_file) as f:
                summary = json.load(f)
            
            print("\n📊 CURRENT STATUS:")
            print(f"   Running: {summary['continuous_operation']['running']}")
            print(f"   Total discoveries: {summary['totals']['discoveries']}")
            print(f"   Total batches: {summary['totals']['batches']}")
            print(f"   Runtime: {summary['continuous_operation']['elapsed_hours']:.1f} hours")
            print(f"   Rate: {summary['rates']['discoveries_per_hour']:.1f} discoveries/hour")
            print(f"   Memory: {summary['system_status']['memory_usage_gb']:.1f} GB")
            print(f"   CPU: {summary['system_status']['cpu_percent']:.1f}%")
        else:
            print("📊 No active continuous discovery found")
        return
        
    elif choice == "7":
        # Stop processes
        print("🛑 Stopping continuous discovery processes...")
        try:
            import psutil
            killed = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline'] or []
                    if any('continuous_discovery_engine.py' in arg for arg in cmdline):
                        proc.terminate()
                        killed += 1
                        print(f"   Terminated process {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if killed == 0:
                print("   No continuous discovery processes found")
            else:
                print(f"   Stopped {killed} processes")
                
        except ImportError:
            print("   psutil not available, cannot check processes")
        return
        
    else:
        print("❌ Invalid choice")
        return
    
    # Launch the continuous discovery
    try:
        print(f"🚀 Launching: {' '.join(cmd)}")
        print("   Press Ctrl+C to stop")
        print("=" * 50)
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching: {e}")
    except FileNotFoundError:
        print("❌ continuous_discovery_engine.py not found")

if __name__ == "__main__":
    main()

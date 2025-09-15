#!/usr/bin/env python3
"""
Discovery Daemon Status Monitor

Provides real-time status information about the running discovery daemon,
including discovery statistics, recent findings, and system health.
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
import psutil

def check_daemon_status():
    """Check if daemon is running and get process info"""
    
    daemon_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'cpu_percent', 'memory_info']):
        try:
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            if 'discovery_daemon.py' in cmdline:
                daemon_processes.append({
                    'pid': proc.info['pid'],
                    'runtime_hours': (time.time() - proc.info['create_time']) / 3600,
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_mb': proc.info['memory_info'].rss / 1024 / 1024,
                    'cmdline': cmdline
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return daemon_processes

def parse_daemon_log():
    """Parse daemon log for statistics"""
    
    log_file = Path("discovery_daemon.log")
    if not log_file.exists():
        return None
    
    stats = {
        'discoveries_found': 0,
        'sequences_tested': 0,
        'last_discovery_time': None,
        'last_log_entry': None,
        'recent_discoveries': []
    }
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            if 'SIGNIFICANT DISCOVERY FOUND!' in line:
                stats['discoveries_found'] += 1
                # Extract timestamp
                if line.startswith('2025-'):
                    timestamp = line.split(' - ')[0]
                    stats['last_discovery_time'] = timestamp
            
            elif 'sequences tested' in line and 'runtime' in line:
                # Extract numbers from progress lines
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'discoveries,' and i > 0:
                        stats['discoveries_found'] = int(parts[i-1])
                    elif part == 'tested,' and i > 0:
                        stats['sequences_tested'] = int(parts[i-1])
            
            # Keep last log entry
            stats['last_log_entry'] = line.strip()
    
    except Exception as e:
        print(f"Error parsing log: {e}")
    
    return stats

def get_discovery_files():
    """Get list of recent discovery files"""
    
    discovery_dir = Path("daemon_discoveries")
    if not discovery_dir.exists():
        return []
    
    discovery_files = []
    for file_path in discovery_dir.glob("significant_discovery_*.json"):
        try:
            stat = file_path.stat()
            discovery_files.append({
                'filename': file_path.name,
                'size_kb': stat.st_size / 1024,
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'path': str(file_path)
            })
        except Exception:
            continue
    
    # Sort by modification time (newest first)
    discovery_files.sort(key=lambda x: x['modified_time'], reverse=True)
    return discovery_files

def load_recent_discovery():
    """Load the most recent significant discovery"""
    
    discovery_files = get_discovery_files()
    if not discovery_files:
        return None
    
    most_recent = discovery_files[0]
    try:
        with open(most_recent['path'], 'r') as f:
            discovery_data = json.load(f)
        return discovery_data
    except Exception as e:
        print(f"Error loading discovery: {e}")
        return None

def format_time_ago(timestamp_str):
    """Format time ago string"""
    try:
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            timestamp = timestamp_str
        
        now = datetime.now()
        if timestamp.tzinfo is not None:
            # Make timezone-aware
            import datetime as dt
            now = now.replace(tzinfo=dt.timezone.utc)
        
        delta = now - timestamp
        
        if delta.days > 0:
            return f"{delta.days} days ago"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600} hours ago"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60} minutes ago"
        else:
            return "Just now"
    except Exception:
        return "Unknown"

def display_status():
    """Display comprehensive daemon status"""
    
    print("🔄 DISCOVERY DAEMON STATUS")
    print("=" * 60)
    
    # Check daemon process
    daemon_processes = check_daemon_status()
    
    if daemon_processes:
        print("✅ DAEMON RUNNING")
        for proc in daemon_processes:
            print(f"   PID: {proc['pid']}")
            print(f"   Runtime: {proc['runtime_hours']:.1f} hours")
            print(f"   CPU: {proc['cpu_percent']:.1f}%")
            print(f"   Memory: {proc['memory_mb']:.1f} MB")
    else:
        print("❌ DAEMON NOT RUNNING")
        print("   Use ./start_discovery_daemon.sh to start")
    
    print()
    
    # Parse log statistics
    log_stats = parse_daemon_log()
    if log_stats:
        print("📊 DISCOVERY STATISTICS")
        print("-" * 30)
        print(f"   Discoveries found: {log_stats['discoveries_found']}")
        print(f"   Sequences tested:  {log_stats['sequences_tested']}")
        if log_stats['sequences_tested'] > 0:
            rate = (log_stats['discoveries_found'] / log_stats['sequences_tested']) * 100
            print(f"   Discovery rate:    {rate:.2f}%")
        
        if log_stats['last_discovery_time']:
            print(f"   Last discovery:    {log_stats['last_discovery_time']}")
        
        print()
    
    # Discovery files
    discovery_files = get_discovery_files()
    print(f"📁 DISCOVERY FILES ({len(discovery_files)} total)")
    print("-" * 35)
    
    if discovery_files:
        for i, file_info in enumerate(discovery_files[:5]):  # Show latest 5
            age = format_time_ago(file_info['modified_time'])
            print(f"   {i+1}. {file_info['filename']}")
            print(f"      Size: {file_info['size_kb']:.1f} KB, {age}")
        
        if len(discovery_files) > 5:
            print(f"   ... and {len(discovery_files) - 5} more files")
    else:
        print("   No discovery files found")
    
    print()
    
    # Recent discovery details
    recent_discovery = load_recent_discovery()
    if recent_discovery:
        print("🎯 MOST RECENT DISCOVERY")
        print("-" * 30)
        print(f"   Sequence: {recent_discovery.get('sequence', 'Unknown')[:30]}...")
        print(f"   Significance: {recent_discovery.get('significance_score', 0):.3f}")
        print(f"   Rigor score: {recent_discovery.get('rigor_score', 0):.3f}")
        print(f"   Assessment: {recent_discovery.get('overall_assessment', 'Unknown')}")
        
        timestamp = recent_discovery.get('timestamp')
        if timestamp:
            age = format_time_ago(timestamp)
            print(f"   Time: {age}")
    
    print()
    
    # System health
    print("💊 SYSTEM HEALTH")
    print("-" * 20)
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('.')
    
    print(f"   CPU usage: {cpu_percent:.1f}%")
    print(f"   Memory: {memory.percent:.1f}% used ({memory.available // 1024 // 1024 // 1024} GB free)")
    print(f"   Disk: {disk.percent:.1f}% used ({disk.free // 1024 // 1024 // 1024} GB free)")
    
    print()
    
    # Instructions
    print("🛠️  DAEMON MANAGEMENT")
    print("-" * 25)
    if daemon_processes:
        print("   ./stop_discovery_daemon.sh    # Stop daemon")
        print("   tail -f discovery_daemon.log  # View live log")
    else:
        print("   ./start_discovery_daemon.sh   # Start daemon")
    
    print("   python3 daemon_status.py      # Refresh status")
    print("   ls daemon_discoveries/         # Browse discoveries")

def main():
    """Main status display"""
    try:
        display_status()
    except KeyboardInterrupt:
        print("\nStatus check interrupted")
    except Exception as e:
        print(f"Error checking status: {e}")

if __name__ == "__main__":
    main()

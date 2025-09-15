#!/usr/bin/env python3
"""
M4 DISCOVERY MONITOR
Real-time monitoring for M4 Metal continuous discoveries
Optimized for high-throughput M4 Mac Pro discovery pipeline
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import psutil
from collections import defaultdict, Counter

def clear_screen():
    """Clear terminal screen"""
    os.system('clear')

def format_time_ago(file_time):
    """Format how long ago a file was modified"""
    now = datetime.now()
    diff = now - file_time
    
    if diff.total_seconds() < 60:
        return f"{int(diff.total_seconds())}s ago"
    elif diff.total_seconds() < 3600:
        return f"{int(diff.total_seconds() / 60)}m ago"
    elif diff.total_seconds() < 86400:
        return f"{int(diff.total_seconds() / 3600)}h ago"
    else:
        return f"{int(diff.total_seconds() / 86400)}d ago"

def get_file_size(file_path):
    """Get file size in human readable format"""
    try:
        size = file_path.stat().st_size
        if size < 1024:
            return f"{size}B"
        elif size < 1024**2:
            return f"{size/1024:.1f}KB"
        elif size < 1024**3:
            return f"{size/(1024**2):.1f}MB"
        else:
            return f"{size/(1024**3):.1f}GB"
    except:
        return "N/A"

def analyze_discovery_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Analyze a discovery JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Extract key information
        analysis = {
            'sequence': data.get('sequence', 'Unknown'),
            'sequence_length': len(data.get('sequence', '')),
            'quality_score': data.get('quality_score', 0.0),
            'validation_status': data.get('validation_status', 'Unknown'),
            'therapeutic_potential': data.get('therapeutic_potential', 0.0),
            'timestamp': data.get('timestamp', 'Unknown'),
            'metal_accelerated': data.get('metal_accelerated', False),
            'vqbit_energy': data.get('vqbit_results', {}).get('total_energy', 0.0),
            'file_size': get_file_size(file_path),
            'file_age': format_time_ago(datetime.fromtimestamp(file_path.stat().st_mtime))
        }
        return analysis
    except Exception as e:
        return None

def scan_m4_discoveries(discovery_dir: Path) -> Dict[str, Any]:
    """Scan M4 continuous discoveries directory"""
    
    if not discovery_dir.exists():
        return {
            'status': 'Directory not found',
            'total_files': 0,
            'discoveries': [],
            'summaries': [],
            'latest_activity': None
        }
    
    # Scan for discovery files
    discovery_files = []
    summary_files = []
    
    for file_path in discovery_dir.rglob("*.json"):
        if file_path.name.startswith("m4_discovery_"):
            discovery_files.append(file_path)
        elif file_path.name.startswith("continuous_summary_"):
            summary_files.append(file_path)
    
    # Sort by modification time (newest first)
    discovery_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    summary_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Analyze recent discoveries
    recent_discoveries = []
    for file_path in discovery_files[:20]:  # Top 20 most recent
        analysis = analyze_discovery_file(file_path)
        if analysis:
            recent_discoveries.append(analysis)
    
    # Get latest summary
    latest_summary = None
    if summary_files:
        try:
            with open(summary_files[0], 'r') as f:
                latest_summary = json.load(f)
        except:
            pass
    
    # Calculate statistics
    total_discoveries = len(discovery_files)
    
    # Activity analysis
    now = datetime.now()
    recent_cutoff = now - timedelta(minutes=5)
    very_recent_cutoff = now - timedelta(minutes=1)
    
    recent_activity = len([f for f in discovery_files 
                          if datetime.fromtimestamp(f.stat().st_mtime) > recent_cutoff])
    very_recent_activity = len([f for f in discovery_files 
                               if datetime.fromtimestamp(f.stat().st_mtime) > very_recent_cutoff])
    
    # Quality analysis
    quality_scores = [d['quality_score'] for d in recent_discoveries if d['quality_score'] > 0]
    therapeutic_scores = [d['therapeutic_potential'] for d in recent_discoveries if d['therapeutic_potential'] > 0]
    
    return {
        'status': 'Active',
        'total_files': total_discoveries,
        'summary_files': len(summary_files),
        'recent_discoveries': recent_discoveries,
        'latest_summary': latest_summary,
        'activity': {
            'last_5_minutes': recent_activity,
            'last_1_minute': very_recent_activity,
            'rate_per_minute': recent_activity / 5 if recent_activity > 0 else 0
        },
        'quality_stats': {
            'avg_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            'max_quality': max(quality_scores) if quality_scores else 0,
            'avg_therapeutic': sum(therapeutic_scores) / len(therapeutic_scores) if therapeutic_scores else 0,
            'max_therapeutic': max(therapeutic_scores) if therapeutic_scores else 0
        },
        'directory_size': sum(f.stat().st_size for f in discovery_files) / (1024**2)  # MB
    }

def get_m4_process_info():
    """Get information about running M4 discovery processes"""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
        try:
            if 'm4_metal_accelerated_discovery.py' in ' '.join(proc.info['cmdline'] or []):
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_mb': proc.info['memory_info'].rss / (1024**2) if proc.info['memory_info'] else 0
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return processes

def display_m4_monitor(discovery_data: Dict[str, Any], processes: List[Dict]):
    """Display M4 discovery monitoring dashboard"""
    
    clear_screen()
    
    print("🍎 M4 MAC PRO CONTINUOUS DISCOVERY MONITOR")
    print("🚀 REAL-TIME M4 METAL PIPELINE TRACKING")
    print("=" * 80)
    print(f"📂 Directory: /Users/richardgillespie/Documents/FoTProtein/m4_continuous_discoveries")
    print(f"⏰ Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # System status
    memory = psutil.virtual_memory()
    print(f"💾 SYSTEM STATUS:")
    print(f"   Memory: {memory.percent:.1f}% used ({memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB)")
    
    if processes:
        total_cpu = sum(p['cpu_percent'] for p in processes)
        total_memory = sum(p['memory_mb'] for p in processes)
        print(f"   M4 Processes: {len(processes)} active (CPU: {total_cpu:.1f}%, Memory: {total_memory:.0f} MB)")
        for proc in processes:
            print(f"     PID {proc['pid']}: {proc['cpu_percent']:.1f}% CPU, {proc['memory_mb']:.0f} MB")
    else:
        print(f"   M4 Processes: ❌ No active discovery processes")
    print()
    
    # Discovery statistics
    print(f"📊 DISCOVERY STATISTICS:")
    print(f"   Total discoveries: {discovery_data['total_files']:,}")
    print(f"   Summary files: {discovery_data['summary_files']}")
    print(f"   Directory size: {discovery_data['directory_size']:.1f} MB")
    print(f"   Status: {discovery_data['status']}")
    print()
    
    # Activity monitoring
    activity = discovery_data['activity']
    print(f"🔥 ACTIVITY MONITOR:")
    print(f"   Last 1 minute: {activity['last_1_minute']} discoveries")
    print(f"   Last 5 minutes: {activity['last_5_minutes']} discoveries")
    print(f"   Current rate: {activity['rate_per_minute']:.1f} discoveries/minute")
    print(f"   Estimated hourly: {activity['rate_per_minute'] * 60:.0f} discoveries/hour")
    print()
    
    # Quality analysis
    quality = discovery_data['quality_stats']
    print(f"⭐ QUALITY METRICS:")
    print(f"   Average quality score: {quality['avg_quality']:.3f}")
    print(f"   Max quality score: {quality['max_quality']:.3f}")
    print(f"   Average therapeutic potential: {quality['avg_therapeutic']:.3f}")
    print(f"   Max therapeutic potential: {quality['max_therapeutic']:.3f}")
    print()
    
    # Latest summary
    if discovery_data['latest_summary']:
        summary = discovery_data['latest_summary']
        runtime = summary.get('total_runtime_hours', 0)
        metrics = summary.get('performance_metrics', {})
        
        print(f"📈 LATEST PERFORMANCE SUMMARY:")
        print(f"   Runtime: {runtime:.2f} hours")
        print(f"   Total sequences: {metrics.get('sequences_processed', 0):,}")
        print(f"   Valid discoveries: {metrics.get('valid_discoveries_found', 0)}")
        print(f"   Average rate: {metrics.get('sequences_per_second_avg', 0):.1f} seq/sec")
        print()
    
    # Recent discoveries
    recent = discovery_data['recent_discoveries']
    print(f"🧬 RECENT DISCOVERIES (Top 10):")
    print(f"{'#':<3} {'Length':<6} {'Quality':<7} {'Therapeutic':<11} {'Age':<8} {'Sequence':<30}")
    print("-" * 80)
    
    for i, discovery in enumerate(recent[:10], 1):
        sequence = discovery['sequence'][:27] + "..." if len(discovery['sequence']) > 30 else discovery['sequence']
        print(f"{i:<3} {discovery['sequence_length']:<6} {discovery['quality_score']:<7.3f} "
              f"{discovery['therapeutic_potential']:<11.3f} {discovery['file_age']:<8} {sequence:<30}")
    
    if not recent:
        print("   No discoveries found yet...")
    
    print()
    print("🔄 Auto-refreshing every 5 seconds... Press Ctrl+C to stop")

def main():
    """Run M4 discovery monitor"""
    
    discovery_dir = Path("/Users/richardgillespie/Documents/FoTProtein/m4_continuous_discoveries")
    
    print("🍎 Starting M4 Discovery Monitor...")
    print("🔄 Monitoring M4 continuous discoveries in real-time")
    print()
    
    try:
        while True:
            # Scan discoveries
            discovery_data = scan_m4_discoveries(discovery_dir)
            
            # Get process info
            processes = get_m4_process_info()
            
            # Display dashboard
            display_m4_monitor(discovery_data, processes)
            
            # Wait before refresh
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 M4 Discovery Monitor stopped")
    except Exception as e:
        print(f"\n❌ Monitor error: {e}")

if __name__ == "__main__":
    main()

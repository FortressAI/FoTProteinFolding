#!/usr/bin/env python3
"""
OUTPUT FILE MONITOR
Monitor discovery output files and directories in real-time
"""

import json
import time
import os
import signal
from pathlib import Path
from datetime import datetime
import glob

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

def format_file_size(bytes_size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def scan_discovery_files():
    """Scan all discovery-related files and directories"""
    
    base_dirs = [
        "continuous_discoveries",
        "validated_discoveries", 
        "production_cure_discoveries"
    ]
    
    file_info = {
        'total_discoveries': 0,
        'total_batches': 0,
        'recent_files': [],
        'directories': {},
        'summary_files': []
    }
    
    for base_dir in base_dirs:
        if Path(base_dir).exists():
            file_info['directories'][base_dir] = scan_directory(Path(base_dir))
    
    # Count total discoveries
    for dir_info in file_info['directories'].values():
        file_info['total_discoveries'] += dir_info.get('discovery_count', 0)
        file_info['total_batches'] += dir_info.get('batch_count', 0)
        file_info['recent_files'].extend(dir_info.get('recent_files', []))
        file_info['summary_files'].extend(dir_info.get('summary_files', []))
    
    # Sort recent files by modification time
    file_info['recent_files'].sort(key=lambda x: x['mtime'], reverse=True)
    file_info['recent_files'] = file_info['recent_files'][:10]  # Keep only 10 most recent
    
    return file_info

def scan_directory(directory):
    """Scan a directory for discovery files"""
    
    info = {
        'discovery_count': 0,
        'batch_count': 0,
        'recent_files': [],
        'summary_files': [],
        'total_size': 0
    }
    
    if not directory.exists():
        return info
    
    # Scan for discovery files
    discovery_patterns = [
        "**/*discovery*.json",
        "**/VD_*.json",
        "**/discoveries/**/*.json"
    ]
    
    for pattern in discovery_patterns:
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                stat = file_path.stat()
                info['discovery_count'] += 1
                info['total_size'] += stat.st_size
                
                info['recent_files'].append({
                    'path': str(file_path),
                    'name': file_path.name,
                    'size': stat.st_size,
                    'mtime': stat.st_mtime,
                    'age': time.time() - stat.st_mtime
                })
    
    # Scan for batch files
    batch_patterns = [
        "**/batch_*.json",
        "**/batches/**/*.json"
    ]
    
    for pattern in batch_patterns:
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                info['batch_count'] += 1
    
    # Scan for summary files
    summary_patterns = [
        "**/continuous_summary.json",
        "**/discovery_report_*.json",
        "**/summary.json"
    ]
    
    for pattern in summary_patterns:
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                stat = file_path.stat()
                info['summary_files'].append({
                    'path': str(file_path),
                    'name': file_path.name,
                    'size': stat.st_size,
                    'mtime': stat.st_mtime,
                    'age': time.time() - stat.st_mtime
                })
    
    return info

def read_latest_summary():
    """Read the latest summary file if available"""
    
    summary_files = []
    
    # Look for summary files
    for pattern in ["**/continuous_summary.json", "**/discovery_report_*.json"]:
        for file_path in Path(".").glob(pattern):
            if file_path.is_file():
                summary_files.append(file_path)
    
    if not summary_files:
        return None
    
    # Get the most recent summary
    latest_summary = max(summary_files, key=lambda x: x.stat().st_mtime)
    
    try:
        with open(latest_summary) as f:
            return json.load(f)
    except:
        return None

def display_file_monitor():
    """Display file monitoring information"""
    
    clear_screen()
    
    print("📁 DISCOVERY OUTPUT FILE MONITOR")
    print("=" * 60)
    
    # Scan files
    file_info = scan_discovery_files()
    
    # Display overview
    print(f"📊 OVERVIEW:")
    print(f"   Total Discoveries: {file_info['total_discoveries']:,}")
    print(f"   Total Batches: {file_info['total_batches']:,}")
    print(f"   Active Directories: {len([d for d in file_info['directories'] if file_info['directories'][d]['discovery_count'] > 0])}")
    print()
    
    # Display directory breakdown
    print(f"📁 DIRECTORIES:")
    for dir_name, dir_info in file_info['directories'].items():
        if dir_info['discovery_count'] > 0 or dir_info['batch_count'] > 0:
            size_str = format_file_size(dir_info['total_size'])
            print(f"   {dir_name}:")
            print(f"     Discoveries: {dir_info['discovery_count']:,}")
            print(f"     Batches: {dir_info['batch_count']:,}")
            print(f"     Size: {size_str}")
    print()
    
    # Display recent files
    if file_info['recent_files']:
        print(f"🕒 RECENT DISCOVERIES (Last 10):")
        for file_info_item in file_info['recent_files']:
            age_str = format_time(file_info_item['age'])
            size_str = format_file_size(file_info_item['size'])
            print(f"   {file_info_item['name']} ({size_str}, {age_str} ago)")
        print()
    
    # Display summary information
    summary_data = read_latest_summary()
    if summary_data:
        print(f"📈 LATEST SUMMARY:")
        
        if 'continuous_operation' in summary_data:
            # Continuous discovery summary
            op = summary_data['continuous_operation']
            totals = summary_data.get('totals', {})
            rates = summary_data.get('rates', {})
            
            print(f"   Status: {'🟢 Running' if op.get('running', False) else '🔴 Stopped'}")
            print(f"   Runtime: {op.get('elapsed_hours', 0):.1f} hours")
            print(f"   Discoveries: {totals.get('discoveries', 0):,}")
            print(f"   Success Rate: {totals.get('overall_success_rate', 0):.2%}")
            print(f"   Rate: {rates.get('discoveries_per_hour', 0):.1f}/hour")
        
        elif 'summary' in summary_data:
            # Single run summary
            summary = summary_data['summary']
            print(f"   Discoveries: {summary.get('total_discoveries', 0)}")
            print(f"   Success Rate: {summary.get('success_rate', 0):.2%}")
            print(f"   Runtime: {summary.get('elapsed_time_seconds', 0):.0f}s")
        
        print()
    
    # Display summary files
    if file_info['summary_files']:
        print(f"📋 SUMMARY FILES:")
        for summary_file in file_info['summary_files']:
            age_str = format_time(summary_file['age'])
            size_str = format_file_size(summary_file['size'])
            print(f"   {summary_file['name']} ({size_str}, {age_str} ago)")
        print()
    
    # Display commands
    print(f"🔧 COMMANDS:")
    print(f"   Ctrl+C: Exit monitor")
    print(f"   Press 'd' + Enter: Show detailed file list")
    print(f"   Press 'c' + Enter: Clear and refresh")
    print(f"   Press 's' + Enter: Start continuous discovery")
    print()
    
    now = datetime.now()
    print(f"🔄 Last updated: {now.strftime('%H:%M:%S')}")
    
    return file_info

def show_detailed_files():
    """Show detailed file listing"""
    
    clear_screen()
    print("📁 DETAILED FILE LISTING")
    print("=" * 60)
    
    file_info = scan_discovery_files()
    
    for dir_name, dir_info in file_info['directories'].items():
        if dir_info['discovery_count'] > 0:
            print(f"\n📁 {dir_name}/")
            
            for file_item in sorted(dir_info['recent_files'], key=lambda x: x['mtime'], reverse=True):
                age_str = format_time(file_item['age'])
                size_str = format_file_size(file_item['size'])
                rel_path = file_item['path'].replace(str(Path.cwd()) + "/", "")
                print(f"   {rel_path}")
                print(f"     Size: {size_str}, Age: {age_str}")
    
    print(f"\nPress Enter to return to main monitor...")
    input()

def main():
    """Main monitoring loop"""
    
    def signal_handler(signum, frame):
        clear_screen()
        print("👋 File monitor stopped")
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("📁 Starting Discovery Output File Monitor...")
    print("   Monitoring all discovery output files and directories")
    print("   Press Ctrl+C to exit")
    time.sleep(2)
    
    try:
        while True:
            file_info = display_file_monitor()
            
            # Check for user input (non-blocking)
            import select
            import sys
            
            if select.select([sys.stdin], [], [], 5):  # 5 second timeout
                user_input = input().strip().lower()
                
                if user_input == 'd':
                    show_detailed_files()
                elif user_input == 'c':
                    clear_screen()
                    continue
                elif user_input == 's':
                    clear_screen()
                    print("🚀 Starting continuous discovery...")
                    os.system("python3 launch_continuous_discovery.py")
                    break
            
            time.sleep(5)  # Update every 5 seconds
    
    except KeyboardInterrupt:
        clear_screen()
        print("👋 File monitor stopped")
    except Exception as e:
        clear_screen()
        print(f"❌ Monitor error: {e}")

if __name__ == "__main__":
    main()

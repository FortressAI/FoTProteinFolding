#!/usr/bin/env python3
"""
SIMPLE FILE MONITOR
Watch discovery output files and show real-time status
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime

def clear_screen():
    """Clear terminal screen"""
    os.system('clear')

def scan_discovery_outputs():
    """Scan for ALL types of discovery output files"""
    
    results = {
        'therapeutic_discoveries': [],
        'scientific_inquiries': [],
        'final_reports': [],
        'validated_discoveries': [],
        'batch_files': [],
        'summary_files': [],
        'prior_art_files': [],
        'total_discoveries': 0,
        'latest_discovery': None
    }
    
    # PRODUCTION-ONLY patterns (exclude test/example data)
    file_patterns = {
        'therapeutic_discoveries': ["**/therapeutic_discovery_*.json"],
        'scientific_inquiries': ["**/scientific_inquiry_*.json"],
        'final_reports': ["**/final_discovery_report_*.json"],
        'validated_discoveries': ["**/VD_*.json"],  # Removed validated_discovery_example_* patterns
        'batch_files': ["**/batch_*.json"],
        'summary_files': ["**/continuous_summary.json", "**/discovery_report_*.json", "**/summary.json"],
        'prior_art_files': ["**/prior_art_archive/**/*.json", "**/complete_prior_art_package.json"]
    }
    
    # Exclude test/development directories
    excluded_paths = ["dev_testing_archive", "tests", "examples"]
    
    for category, patterns in file_patterns.items():
        for pattern in patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file():
                    # Skip files in excluded directories
                    if any(excluded in str(file_path) for excluded in excluded_paths):
                        continue
                    
                    # Skip files with test/example keywords in filename
                    if any(keyword in file_path.name.lower() for keyword in ['example', 'test', 'demo']):
                        continue
                    
                    stat = file_path.stat()
                    file_info = {
                        'path': str(file_path),
                        'name': file_path.name,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'age_seconds': time.time() - stat.st_mtime,
                        'category': category
                    }
                    
                    results[category].append(file_info)
                    
                    # Count all discoveries
                    if category in ['therapeutic_discoveries', 'scientific_inquiries', 'validated_discoveries']:
                        results['total_discoveries'] += 1
                        
                        if not results['latest_discovery'] or stat.st_mtime > results['latest_discovery']['modified'].timestamp():
                            results['latest_discovery'] = file_info
    
    # Sort all categories by modification time
    for category in results:
        if isinstance(results[category], list):
            results[category].sort(key=lambda x: x['modified'], reverse=True)
    
    return results

def format_age(age_seconds):
    """Format age in human readable format"""
    if age_seconds < 60:
        return f"{age_seconds:.0f}s ago"
    elif age_seconds < 3600:
        return f"{age_seconds/60:.0f}m ago"
    else:
        return f"{age_seconds/3600:.1f}h ago"

def format_size(size_bytes):
    """Format file size"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024*1024:
        return f"{size_bytes/1024:.1f} KB"
    else:
        return f"{size_bytes/(1024*1024):.1f} MB"

def read_discovery_file(file_path):
    """Try to read and parse a discovery file"""
    try:
        with open(file_path) as f:
            data = json.load(f)
        
        # Extract key information
        info = {}
        if 'sequence' in data:
            info['sequence'] = data['sequence'][:50] + ('...' if len(data['sequence']) > 50 else '')
        if 'validation_score' in data:
            info['validation_score'] = data['validation_score']
        if 'therapeutic_potential' in data:
            info['therapeutic_potential'] = data['therapeutic_potential']
        if 'discovery_id' in data:
            info['discovery_id'] = data['discovery_id']
        
        return info
    except:
        return None

def display_monitor():
    """Display the comprehensive file monitor"""
    
    clear_screen()
    
    print("📁 PRODUCTION DISCOVERY FILE MONITOR")
    print("=" * 50)
    print("🏭 PRODUCTION FILES ONLY (excludes test/example data)")
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Scan files
    results = scan_discovery_outputs()
    
    # Display comprehensive summary
    print(f"📊 FILE BREAKDOWN:")
    print(f"   🧬 Therapeutic Discoveries: {len(results['therapeutic_discoveries'])}")
    print(f"   🔬 Scientific Inquiries: {len(results['scientific_inquiries'])}")
    print(f"   📊 Final Reports: {len(results['final_reports'])}")
    print(f"   ✅ Validated Discoveries: {len(results['validated_discoveries'])}")
    print(f"   📦 Batch Files: {len(results['batch_files'])}")
    print(f"   📋 Summary Files: {len(results['summary_files'])}")
    print(f"   ⚖️ Prior Art Files: {len(results['prior_art_files'])}")
    print(f"   🎯 TOTAL DISCOVERIES: {results['total_discoveries']}")
    print()
    
    # Display latest discovery
    if results['latest_discovery']:
        latest = results['latest_discovery']
        category_emoji = {
            'therapeutic_discoveries': '🧬',
            'scientific_inquiries': '🔬',
            'validated_discoveries': '✅'
        }
        emoji = category_emoji.get(latest['category'], '📄')
        
        print(f"🔬 LATEST DISCOVERY ({emoji} {latest['category'].replace('_', ' ').title()}):")
        print(f"   File: {latest['name']}")
        print(f"   Size: {format_size(latest['size'])}")
        print(f"   Modified: {format_age(latest['age_seconds'])}")
        
        # Try to read discovery details
        discovery_data = read_discovery_file(latest['path'])
        if discovery_data:
            if 'discovery_id' in discovery_data:
                print(f"   ID: {discovery_data['discovery_id']}")
            if 'validation_score' in discovery_data:
                print(f"   Validation: {discovery_data['validation_score']:.3f}")
            if 'therapeutic_potential' in discovery_data:
                print(f"   Therapeutic: {discovery_data['therapeutic_potential']:.3f}")
            if 'sequence' in discovery_data:
                print(f"   Sequence: {discovery_data['sequence']}")
        print()
    
    # Display recent files by category
    categories_to_show = [
        ('therapeutic_discoveries', '🧬 RECENT THERAPEUTIC DISCOVERIES', 5),
        ('scientific_inquiries', '🔬 RECENT SCIENTIFIC INQUIRIES', 3),
        ('final_reports', '📊 RECENT FINAL REPORTS', 3),
        ('validated_discoveries', '✅ RECENT VALIDATED DISCOVERIES', 3)
    ]
    
    for category_key, title, max_show in categories_to_show:
        if results[category_key]:
            print(f"{title}:")
            for i, file_info in enumerate(results[category_key][:max_show]):
                print(f"   {i+1}. {file_info['name']} ({format_size(file_info['size'])}, {format_age(file_info['age_seconds'])})")
            if len(results[category_key]) > max_show:
                print(f"   ... and {len(results[category_key]) - max_show} more")
            print()
    
    # Display summary files
    if results['summary_files']:
        print(f"📋 SUMMARY FILES:")
        for file_info in results['summary_files'][:3]:
            print(f"   {file_info['name']} ({format_size(file_info['size'])}, {format_age(file_info['age_seconds'])})")
        print()
    
    # Display prior art files
    if results['prior_art_files']:
        print(f"⚖️ PRIOR ART FILES:")
        for file_info in results['prior_art_files'][:3]:
            print(f"   {file_info['name']} ({format_size(file_info['size'])}, {format_age(file_info['age_seconds'])})")
        print()
    
    # Check for running processes
    try:
        import psutil
        running_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline'] or []
                if any('continuous_discovery' in arg for arg in cmdline):
                    running_processes.append(proc.info['pid'])
            except:
                pass
        
        if running_processes:
            print(f"🔄 RUNNING PROCESSES:")
            for pid in running_processes:
                print(f"   PID {pid}: continuous_discovery")
            print()
    except ImportError:
        pass
    
    if results['total_discoveries'] == 0:
        print("📭 No discovery files found yet")
        print("   Run 'python3 launch_continuous_discovery.py' to start")
        print()
    
    print("🔧 Press Ctrl+C to exit")

def main():
    """Main monitoring loop"""
    
    print("📁 Starting Simple File Monitor...")
    print("   Monitoring discovery output files")
    time.sleep(1)
    
    try:
        while True:
            display_monitor()
            time.sleep(10)  # Update every 10 seconds
    
    except KeyboardInterrupt:
        clear_screen()
        print("👋 File monitor stopped")

if __name__ == "__main__":
    main()

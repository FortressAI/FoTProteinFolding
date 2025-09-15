#!/usr/bin/env python3
"""
MANAGE JSON FILES
Simple tool to manage and organize JSON discovery files
"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def get_file_stats():
    """Get basic statistics about JSON files"""
    
    json_files = list(Path(".").glob("**/*.json"))
    total_size = sum(f.stat().st_size for f in json_files)
    
    return {
        'count': len(json_files),
        'size_mb': total_size / (1024 * 1024),
        'size_gb': total_size / (1024 * 1024 * 1024)
    }

def archive_old_files(days_old=7, dry_run=True):
    """Archive files older than specified days"""
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    archive_dir = Path("archived_discoveries")
    
    if not dry_run:
        archive_dir.mkdir(exist_ok=True)
    
    candidates = []
    
    # Find old therapeutic discovery files
    for pattern in ["**/therapeutic_discovery_*.json", "**/scientific_inquiry_*.json"]:
        for file_path in Path(".").glob(pattern):
            if file_path.stat().st_mtime < cutoff_date.timestamp():
                candidates.append(file_path)
    
    if dry_run:
        print(f"📦 ARCHIVE CANDIDATES (older than {days_old} days):")
        for file_path in candidates[:10]:
            age_days = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).days
            size_kb = file_path.stat().st_size / 1024
            print(f"   {file_path.name} ({age_days} days old, {size_kb:.1f} KB)")
        
        if len(candidates) > 10:
            print(f"   ... and {len(candidates) - 10} more files")
        
        total_size_mb = sum(f.stat().st_size for f in candidates) / (1024 * 1024)
        print(f"\n   Total: {len(candidates)} files, {total_size_mb:.1f} MB")
        print(f"   Run with --execute to actually archive them")
    else:
        for file_path in candidates:
            dest_path = archive_dir / file_path.name
            shutil.move(str(file_path), str(dest_path))
        
        print(f"✅ Archived {len(candidates)} files to {archive_dir}")

def show_latest_discoveries(count=10):
    """Show the latest discovery files"""
    
    discovery_files = []
    
    for pattern in ["**/therapeutic_discovery_*.json", "**/VD_*.json"]:
        for file_path in Path(".").glob(pattern):
            discovery_files.append(file_path)
    
    # Sort by modification time
    discovery_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"🔬 LATEST {count} DISCOVERIES:")
    
    for i, file_path in enumerate(discovery_files[:count]):
        age_minutes = (datetime.now().timestamp() - file_path.stat().st_mtime) / 60
        size_kb = file_path.stat().st_size / 1024
        
        # Try to read discovery info
        try:
            with open(file_path) as f:
                data = json.load(f)
            
            sequence = data.get('sequence', 'Unknown')[:30]
            validation_score = data.get('validation_score', 'N/A')
            therapeutic_potential = data.get('therapeutic_potential', 'N/A')
            
            print(f"   {i+1}. {file_path.name}")
            print(f"      Age: {age_minutes:.0f} minutes, Size: {size_kb:.1f} KB")
            print(f"      Sequence: {sequence}...")
            print(f"      Validation: {validation_score}, Therapeutic: {therapeutic_potential}")
        
        except:
            print(f"   {i+1}. {file_path.name} (could not read)")
        
        print()

def show_discovery_summary():
    """Show summary of all discoveries"""
    
    stats = get_file_stats()
    
    print(f"📊 DISCOVERY FILE SUMMARY:")
    print(f"   Total JSON files: {stats['count']:,}")
    print(f"   Total size: {stats['size_mb']:.1f} MB ({stats['size_gb']:.2f} GB)")
    print()
    
    # Count by type
    therapeutic_count = len(list(Path(".").glob("**/therapeutic_discovery_*.json")))
    scientific_count = len(list(Path(".").glob("**/scientific_inquiry_*.json")))
    report_count = len(list(Path(".").glob("**/final_discovery_report_*.json")))
    
    print(f"   Therapeutic discoveries: {therapeutic_count:,}")
    print(f"   Scientific inquiries: {scientific_count:,}")
    print(f"   Final reports: {report_count:,}")
    print()

def main():
    """Main function with menu options"""
    
    import sys
    
    if len(sys.argv) < 2:
        print("📁 JSON FILE MANAGER")
        print("=" * 30)
        print()
        print("Usage:")
        print("  python3 manage_json_files.py summary      # Show file summary")
        print("  python3 manage_json_files.py latest       # Show latest discoveries")
        print("  python3 manage_json_files.py archive      # Preview archive candidates")
        print("  python3 manage_json_files.py archive --execute  # Actually archive old files")
        print()
        return
    
    command = sys.argv[1]
    
    if command == "summary":
        show_discovery_summary()
    
    elif command == "latest":
        show_latest_discoveries()
    
    elif command == "archive":
        execute = "--execute" in sys.argv
        archive_old_files(days_old=7, dry_run=not execute)
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()

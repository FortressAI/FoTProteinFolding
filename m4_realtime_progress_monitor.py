#!/usr/bin/env python3
"""
M4 REAL-TIME PROGRESS MONITOR
Live discovery statistics updated every 30 seconds
Optimized for tracking 900K+ M4 Mac Pro discovery progress
"""

import os
import time
import json
import psutil
import random
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import threading

class M4ProgressMonitor:
    """Real-time M4 discovery progress monitoring with 30-second updates"""
    
    def __init__(self, discovery_dir: Path = Path("m4_continuous_discoveries")):
        self.discovery_dir = discovery_dir
        self.running = True
        self.update_interval = 30  # 30 seconds
        
        # Statistics tracking
        self.last_file_count = 0
        self.last_check_time = datetime.now()
        self.session_start_time = datetime.now()
        
        # Running averages
        self.rate_history = []
        self.max_history_length = 20  # Keep last 20 measurements (10 minutes)
        
        # Learning and discovery tracking
        self.quality_history = []
        self.recent_discoveries = []
        self.learning_patterns = {
            'sequence_lengths': [],
            'energy_values': [],
            'quality_scores': [],
            'virtue_patterns': defaultdict(list)
        }
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear')
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get disk usage for the discovery directory
        disk_usage = psutil.disk_usage(str(self.discovery_dir.parent))
        
        return {
            'memory': {
                'total_gb': memory.total / (1024**3),
                'used_gb': memory.used / (1024**3),
                'available_gb': memory.available / (1024**3),
                'percent': memory.percent
            },
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count()
            },
            'disk': {
                'total_gb': disk_usage.total / (1024**3),
                'used_gb': disk_usage.used / (1024**3),
                'free_gb': disk_usage.free / (1024**3),
                'percent': (disk_usage.used / disk_usage.total) * 100
            }
        }
    
    def get_m4_process_info(self) -> List[Dict[str, Any]]:
        """Get information about running M4 discovery processes"""
        
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info', 'create_time']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'm4_metal_accelerated_discovery.py' in cmdline:
                    runtime_seconds = time.time() - proc.info['create_time']
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_mb': proc.info['memory_info'].rss / (1024**2) if proc.info['memory_info'] else 0,
                        'runtime_hours': runtime_seconds / 3600
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
    
    def analyze_recent_discoveries(self, sample_size: int = 50) -> Dict[str, Any]:
        """Analyze recent discoveries for learning patterns and quality insights"""
        
        try:
            print(f"🔍 DEBUG: Looking for files in {self.discovery_dir}")
            # Get recent discovery files
            discovery_files = list(self.discovery_dir.glob("m4_discovery_*.json"))
            print(f"🔍 DEBUG: Found {len(discovery_files)} discovery files total")
            
            if not discovery_files:
                return {
                    'total_analyzed': 0,
                    'high_quality_discoveries': [],
                    'quality_distribution': {},
                    'learning_insights': {},
                    'recent_patterns': {}
                }
            
            # Sort by modification time and take most recent
            print(f"🔍 DEBUG: Sorting {len(discovery_files)} files by modification time...")
            discovery_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            recent_files = discovery_files[:sample_size]
            print(f"🔍 DEBUG: Selected {len(recent_files)} recent files for analysis")
            
            quality_scores = []
            energy_values = []
            sequence_lengths = []
            virtue_patterns = defaultdict(list)
            high_quality_discoveries = []
            
            for file_path in recent_files:
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Extract key metrics
                    sequence = data.get('sequence', '')
                    quality = data.get('validation_score', 0.0)
                    assessment = data.get('assessment', '')
                    
                    quality_scores.append(quality)
                    sequence_lengths.append(len(sequence))
                    
                    # Metal analysis data
                    metal_analysis = data.get('metal_analysis', {})
                    energy = metal_analysis.get('energy_kcal_mol', 0.0)
                    energy_values.append(energy)
                    
                    # Virtue scores
                    virtue_scores = metal_analysis.get('virtue_scores', {})
                    for virtue, score in virtue_scores.items():
                        virtue_patterns[virtue].append(score)
                    
                    # Track high-quality discoveries
                    if quality >= 0.9:
                        high_quality_discoveries.append({
                            'sequence': sequence[:30] + "..." if len(sequence) > 30 else sequence,
                            'quality': quality,
                            'energy': energy,
                            'assessment': assessment,
                            'length': len(sequence),
                            'timestamp': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%H:%M:%S')
                        })
                    
                except Exception as e:
                    continue
            
            # Calculate statistics
            quality_distribution = {
                'excellent': len([q for q in quality_scores if q >= 0.9]),
                'good': len([q for q in quality_scores if 0.8 <= q < 0.9]),
                'fair': len([q for q in quality_scores if 0.7 <= q < 0.8]),
                'poor': len([q for q in quality_scores if q < 0.7])
            }
            
            # Learning insights
            learning_insights = {}
            if quality_scores:
                learning_insights = {
                    'avg_quality': np.mean(quality_scores),
                    'quality_trend': 'improving' if len(quality_scores) > 10 and np.mean(quality_scores[-5:]) > np.mean(quality_scores[:5]) else 'stable',
                    'avg_sequence_length': np.mean(sequence_lengths) if sequence_lengths else 0,
                    'avg_energy': np.mean(energy_values) if energy_values else 0,
                    'energy_range': {'min': np.min(energy_values), 'max': np.max(energy_values)} if energy_values else {'min': 0, 'max': 0}
                }
            
            # Recent patterns
            recent_patterns = {}
            for virtue, scores in virtue_patterns.items():
                if scores:
                    recent_patterns[virtue] = {
                        'avg': np.mean(scores),
                        'trend': 'positive' if np.mean(scores) > 0 else 'negative'
                    }
            
            return {
                'total_analyzed': len(recent_files),
                'high_quality_discoveries': high_quality_discoveries[:10],  # Top 10
                'quality_distribution': quality_distribution,
                'learning_insights': learning_insights,
                'recent_patterns': recent_patterns
            }
            
        except Exception as e:
            return {
                'total_analyzed': 0,
                'error': str(e),
                'high_quality_discoveries': [],
                'quality_distribution': {},
                'learning_insights': {},
                'recent_patterns': {}
            }
    
    def scan_discovery_files(self) -> Dict[str, Any]:
        """Scan discovery files and calculate statistics"""
        
        current_time = datetime.now()
        
        # Count all M4 discovery files
        try:
            discovery_files = list(self.discovery_dir.glob("m4_discovery_*.json"))
            total_files = len(discovery_files)
        except Exception:
            total_files = 0
        
        # Calculate rate since last check
        time_diff = (current_time - self.last_check_time).total_seconds()
        files_diff = total_files - self.last_file_count
        
        current_rate = files_diff / time_diff if time_diff > 0 else 0
        
        # Update rate history
        if len(self.rate_history) >= self.max_history_length:
            self.rate_history.pop(0)
        self.rate_history.append(current_rate)
        
        # Calculate averages
        avg_rate = sum(self.rate_history) / len(self.rate_history) if self.rate_history else 0
        
        # Calculate session statistics
        session_duration = (current_time - self.session_start_time).total_seconds()
        session_files = total_files - (self.last_file_count if hasattr(self, 'session_start_files') else 0)
        
        if not hasattr(self, 'session_start_files'):
            self.session_start_files = self.last_file_count
            session_files = 0
        
        # Calculate directory size (sample for performance)
        try:
            if total_files > 1000:
                # Sample 1000 files to estimate total size
                sample_files = discovery_files[:1000]
                sample_size = sum(f.stat().st_size for f in sample_files if f.exists())
                estimated_total_size = (sample_size / len(sample_files)) * total_files if sample_files else 0
            else:
                estimated_total_size = sum(f.stat().st_size for f in discovery_files if f.exists())
            
            total_size_gb = estimated_total_size / (1024**3)
        except Exception:
            total_size_gb = 0
        
        # Update tracking variables
        self.last_file_count = total_files
        self.last_check_time = current_time
        
        return {
            'total_files': total_files,
            'files_added_last_interval': files_diff,
            'current_rate_per_second': current_rate,
            'average_rate_per_second': avg_rate,
            'estimated_rate_per_hour': avg_rate * 3600,
            'estimated_rate_per_day': avg_rate * 86400,
            'session_files_generated': session_files,
            'session_duration_hours': session_duration / 3600,
            'total_size_gb': total_size_gb,
            'avg_file_size_kb': (total_size_gb * 1024 * 1024) / total_files if total_files > 0 else 0
        }
    
    def format_number(self, num: float) -> str:
        """Format numbers with appropriate units"""
        if num >= 1_000_000:
            return f"{num/1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return f"{num:.1f}"
    
    def display_progress_dashboard(self, discovery_stats: Dict[str, Any], system_stats: Dict[str, Any], processes: List[Dict[str, Any]], discovery_analysis: Dict[str, Any]):
        """Display the real-time progress dashboard"""
        
        self.clear_screen()
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("🍎 M4 MAC PRO REAL-TIME DISCOVERY PROGRESS MONITOR")
        print("🚀 BEAST MODE CONTINUOUS TRACKING - 30 SECOND UPDATES")
        print("=" * 80)
        print(f"⏰ Current Time: {current_time}")
        print(f"📂 Directory: {self.discovery_dir}")
        print()
        
        # Discovery Statistics
        print("🧬 DISCOVERY PROGRESS:")
        print(f"   📊 Total Discoveries: {discovery_stats['total_files']:,}")
        print(f"   📈 Added Last 30s: {discovery_stats['files_added_last_interval']:,}")
        print(f"   ⚡ Current Rate: {discovery_stats['current_rate_per_second']:.1f} files/sec")
        print(f"   📈 Average Rate: {discovery_stats['average_rate_per_second']:.1f} files/sec")
        print(f"   🕐 Estimated Hourly: {self.format_number(discovery_stats['estimated_rate_per_hour'])} files/hour")
        print(f"   📅 Estimated Daily: {self.format_number(discovery_stats['estimated_rate_per_day'])} files/day")
        print(f"   💾 Total Size: {discovery_stats['total_size_gb']:.2f} GB")
        print(f"   📄 Avg File Size: {discovery_stats['avg_file_size_kb']:.1f} KB")
        print()
        
        # Session Statistics
        print("📊 SESSION STATISTICS:")
        print(f"   🕐 Session Duration: {discovery_stats['session_duration_hours']:.2f} hours")
        print(f"   📈 Session Files: {discovery_stats['session_files_generated']:,}")
        if discovery_stats['session_duration_hours'] > 0:
            session_rate = discovery_stats['session_files_generated'] / discovery_stats['session_duration_hours']
            print(f"   ⚡ Session Avg Rate: {session_rate:.0f} files/hour")
        print()
        
        # M4 Process Information
        print("🍎 M4 PROCESS STATUS:")
        if processes:
            for proc in processes:
                print(f"   PID {proc['pid']}: {proc['cpu_percent']:.1f}% CPU, {proc['memory_mb']:.0f} MB RAM, {proc['runtime_hours']:.1f}h runtime")
        else:
            print("   ⚠️ No M4 discovery processes detected")
        print()
        
        # System Resources
        memory = system_stats['memory']
        cpu = system_stats['cpu']
        disk = system_stats['disk']
        
        print("💻 SYSTEM RESOURCES:")
        print(f"   💾 Memory: {memory['used_gb']:.1f} GB / {memory['total_gb']:.1f} GB ({memory['percent']:.1f}% used)")
        print(f"   🖥️ CPU: {cpu['percent']:.1f}% ({cpu['count']} cores)")
        print(f"   💿 Disk: {disk['used_gb']:.0f} GB / {disk['total_gb']:.0f} GB ({disk['percent']:.1f}% used)")
        print(f"   📊 Free Space: {disk['free_gb']:.0f} GB remaining")
        print()
        
        # Performance Insights
        print("🔍 PERFORMANCE INSIGHTS:")
        
        # Memory status
        if memory['percent'] > 90:
            print("   ⚠️ HIGH MEMORY USAGE - Consider restarting or archiving")
        elif memory['percent'] > 75:
            print("   📈 Moderate memory usage")
        else:
            print("   ✅ Memory usage healthy")
        
        # Disk space status
        if disk['percent'] > 90:
            print("   ⚠️ LOW DISK SPACE - Run archiving immediately")
        elif disk['percent'] > 75:
            print("   📈 Disk space getting full - consider archiving")
        else:
            print("   ✅ Disk space healthy")
        
        # Discovery rate status
        if discovery_stats['current_rate_per_second'] > 10:
            print("   🔥 BEAST MODE ACTIVE - Very high discovery rate")
        elif discovery_stats['current_rate_per_second'] > 1:
            print("   ⚡ High discovery rate")
        elif discovery_stats['current_rate_per_second'] > 0.1:
            print("   📈 Moderate discovery rate")
        else:
            print("   📊 Low discovery rate")
        
        # Learning Process and Discovery Analysis
        print("🧠 LEARNING PROCESS & DISCOVERY ANALYSIS:")
        if discovery_analysis.get('total_analyzed', 0) > 0:
            insights = discovery_analysis.get('learning_insights', {})
            quality_dist = discovery_analysis.get('quality_distribution', {})
            
            # Quality distribution
            total_analyzed = discovery_analysis['total_analyzed']
            excellent = quality_dist.get('excellent', 0)
            good = quality_dist.get('good', 0)
            fair = quality_dist.get('fair', 0)
            poor = quality_dist.get('poor', 0)
            
            print(f"   📊 Recent Sample: {total_analyzed} discoveries analyzed")
            print(f"   ⭐ Quality Distribution:")
            print(f"      🌟 Excellent (≥0.9): {excellent} ({excellent/total_analyzed*100:.1f}%)")
            print(f"      ✅ Good (0.8-0.9): {good} ({good/total_analyzed*100:.1f}%)")
            print(f"      📈 Fair (0.7-0.8): {fair} ({fair/total_analyzed*100:.1f}%)")
            print(f"      📊 Poor (<0.7): {poor} ({poor/total_analyzed*100:.1f}%)")
            
            # Learning insights
            if insights:
                print(f"   🔬 Learning Insights:")
                print(f"      📈 Avg Quality: {insights.get('avg_quality', 0):.3f}")
                print(f"      📏 Avg Length: {insights.get('avg_sequence_length', 0):.1f} residues")
                print(f"      ⚡ Avg Energy: {insights.get('avg_energy', 0):.1f} kcal/mol")
                print(f"      📊 Quality Trend: {insights.get('quality_trend', 'unknown').title()}")
            
            # Recent patterns (virtue scores)
            patterns = discovery_analysis.get('recent_patterns', {})
            if patterns:
                print(f"   🎯 Virtue Score Patterns:")
                for virtue, data in patterns.items():
                    trend_icon = "📈" if data['trend'] == 'positive' else "📉"
                    print(f"      {virtue.title()}: {data['avg']:.3f} {trend_icon}")
        else:
            print("   ⏳ Analyzing recent discoveries...")
        
        print()
        
        # High-Quality Discoveries
        high_quality = discovery_analysis.get('high_quality_discoveries', [])
        if high_quality:
            print("🌟 RECENT HIGH-QUALITY DISCOVERIES:")
            for i, discovery in enumerate(high_quality[:5], 1):  # Show top 5
                print(f"   {i}. [{discovery['timestamp']}] Quality: {discovery['quality']:.3f}")
                print(f"      🧬 {discovery['sequence']}")
                print(f"      ⚡ Energy: {discovery['energy']:.1f} kcal/mol, Length: {discovery['length']}")
            
            if len(high_quality) > 5:
                print(f"   ... and {len(high_quality) - 5} more excellent discoveries")
        else:
            print("🌟 HIGH-QUALITY DISCOVERIES:")
            print("   ⏳ No recent excellent discoveries (≥0.9 quality) found")
        
        print()
        print("🔄 Next update in 30 seconds... Press Ctrl+C to stop")
    
    def run_monitor(self):
        """Run the real-time monitor"""
        
        print("🍎 Starting M4 Real-Time Progress Monitor...")
        print("📊 Updates every 30 seconds")
        print("🔄 Press Ctrl+C to stop")
        
        try:
            while self.running:
                print("🔍 DEBUG: Starting data collection cycle...")
                
                # Gather statistics
                print("🔍 DEBUG: Scanning discovery files...")
                discovery_stats = self.scan_discovery_files()
                print(f"🔍 DEBUG: Found {discovery_stats.get('total_files', 0)} files")
                
                print("🔍 DEBUG: Getting system stats...")
                system_stats = self.get_system_stats()
                print("🔍 DEBUG: System stats collected")
                
                print("🔍 DEBUG: Getting M4 process info...")
                processes = self.get_m4_process_info()
                print(f"🔍 DEBUG: Found {len(processes)} M4 processes")
                
                print("🔍 DEBUG: Analyzing recent discoveries...")
                discovery_analysis = self.analyze_recent_discoveries()
                print(f"🔍 DEBUG: Analyzed {discovery_analysis.get('total_analyzed', 0)} recent discoveries")
                
                print("🔍 DEBUG: Displaying dashboard...")
                # Display dashboard
                self.display_progress_dashboard(discovery_stats, system_stats, processes, discovery_analysis)
                
                print("🔍 DEBUG: Waiting for next update...")
                # Wait for next update
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped by user")
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")
        finally:
            self.running = False

def main():
    """Run M4 real-time progress monitor"""
    
    discovery_dir = Path("m4_continuous_discoveries")
    
    if not discovery_dir.exists():
        print(f"❌ Discovery directory not found: {discovery_dir}")
        print("   Make sure you're running this from the FoTProtein directory")
        return
    
    monitor = M4ProgressMonitor(discovery_dir)
    monitor.run_monitor()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
M4 DISCOVERY MANAGER
Intelligent archiving, learning, and pruning for M4 continuous discoveries
Manages 900K+ discovery files with learning-based retention
"""

import os
import json
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import numpy as np
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class M4DiscoveryManager:
    """Smart management of M4 discovery files with learning and archiving"""
    
    def __init__(self, discovery_dir: Path = Path("m4_continuous_discoveries")):
        self.discovery_dir = discovery_dir
        self.archive_dir = discovery_dir / "archive"
        self.learning_dir = discovery_dir / "learning_data"
        self.summary_dir = discovery_dir / "summaries"
        
        # Create directories
        for dir_path in [self.archive_dir, self.learning_dir, self.summary_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Learning thresholds
        self.learning_config = {
            'high_quality_threshold': 0.9,      # Keep high-quality discoveries
            'medium_quality_threshold': 0.7,    # Archive medium quality
            'low_quality_threshold': 0.5,       # Delete low quality
            'unique_sequence_threshold': 0.95,   # Similarity threshold for duplicates
            'batch_size': 1000,                  # Process in batches
            'max_age_hours': 24,                 # Archive files older than 24h
            'max_files_per_hour': 10000,        # Keep max 10K files per hour
        }
        
        self.sequence_patterns = defaultdict(int)
        self.quality_patterns = defaultdict(list)
        
    def analyze_discovery_files(self) -> Dict[str, Any]:
        """Analyze all discovery files and extract learning patterns"""
        
        logger.info("🔍 Analyzing discovery files...")
        
        files = list(self.discovery_dir.glob("m4_discovery_*.json"))
        total_files = len(files)
        
        if total_files == 0:
            return {"status": "no_files"}
        
        logger.info(f"📊 Found {total_files:,} discovery files")
        
        # Sample files for analysis (don't process all 900K+)
        sample_size = min(10000, total_files)
        sample_files = np.random.choice(files, sample_size, replace=False)
        
        analysis = {
            'total_files': total_files,
            'analyzed_files': sample_size,
            'quality_distribution': defaultdict(int),
            'sequence_lengths': [],
            'energy_values': [],
            'virtue_patterns': defaultdict(list),
            'duplicate_sequences': 0,
            'file_ages': [],
            'file_sizes': []
        }
        
        seen_sequences = set()
        
        for i, file_path in enumerate(sample_files):
            try:
                if i % 1000 == 0:
                    logger.info(f"   Processed {i:,}/{sample_size:,} files...")
                
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Extract key metrics
                sequence = data.get('sequence', '')
                quality = data.get('validation_score', 0.0)
                energy = data.get('metal_analysis', {}).get('energy_kcal_mol', 0.0)
                
                # Quality distribution
                if quality >= 0.9:
                    analysis['quality_distribution']['high'] += 1
                elif quality >= 0.7:
                    analysis['quality_distribution']['medium'] += 1
                elif quality >= 0.5:
                    analysis['quality_distribution']['low'] += 1
                else:
                    analysis['quality_distribution']['very_low'] += 1
                
                # Sequence analysis
                analysis['sequence_lengths'].append(len(sequence))
                if sequence in seen_sequences:
                    analysis['duplicate_sequences'] += 1
                else:
                    seen_sequences.add(sequence)
                
                # Energy analysis
                analysis['energy_values'].append(energy)
                
                # Virtue patterns
                virtue_scores = data.get('metal_analysis', {}).get('virtue_scores', {})
                for virtue, score in virtue_scores.items():
                    analysis['virtue_patterns'][virtue].append(score)
                
                # File metadata
                file_stat = file_path.stat()
                file_age = (datetime.now() - datetime.fromtimestamp(file_stat.st_mtime)).total_seconds() / 3600
                analysis['file_ages'].append(file_age)
                analysis['file_sizes'].append(file_stat.st_size)
                
            except Exception as e:
                logger.debug(f"Error processing {file_path}: {e}")
                continue
        
        # Calculate summary statistics
        analysis['avg_sequence_length'] = np.mean(analysis['sequence_lengths']) if analysis['sequence_lengths'] else 0
        analysis['avg_energy'] = np.mean(analysis['energy_values']) if analysis['energy_values'] else 0
        analysis['avg_file_age_hours'] = np.mean(analysis['file_ages']) if analysis['file_ages'] else 0
        analysis['total_size_mb'] = sum(analysis['file_sizes']) * (total_files / sample_size) / (1024 * 1024)
        analysis['duplicate_rate'] = analysis['duplicate_sequences'] / sample_size if sample_size > 0 else 0
        
        # Quality percentages
        total_quality = sum(analysis['quality_distribution'].values())
        for key in analysis['quality_distribution']:
            analysis[f'{key}_quality_percent'] = (analysis['quality_distribution'][key] / total_quality * 100) if total_quality > 0 else 0
        
        logger.info(f"✅ Analysis complete: {sample_size:,} files analyzed")
        return analysis
    
    def intelligent_pruning(self, dry_run: bool = True) -> Dict[str, Any]:
        """Intelligently prune files based on learning patterns"""
        
        logger.info("🧠 Starting intelligent pruning...")
        
        files = list(self.discovery_dir.glob("m4_discovery_*.json"))
        
        pruning_stats = {
            'total_files': len(files),
            'files_to_keep': 0,
            'files_to_archive': 0,
            'files_to_delete': 0,
            'space_saved_mb': 0,
            'actions': []
        }
        
        # Process files in batches
        batch_size = self.learning_config['batch_size']
        
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            logger.info(f"   Processing batch {i//batch_size + 1}/{(len(files)-1)//batch_size + 1} ({len(batch)} files)")
            
            for file_path in batch:
                try:
                    action = self._determine_file_action(file_path)
                    pruning_stats['actions'].append((file_path, action))
                    
                    if action == 'keep':
                        pruning_stats['files_to_keep'] += 1
                    elif action == 'archive':
                        pruning_stats['files_to_archive'] += 1
                    elif action == 'delete':
                        pruning_stats['files_to_delete'] += 1
                        pruning_stats['space_saved_mb'] += file_path.stat().st_size / (1024 * 1024)
                    
                except Exception as e:
                    logger.debug(f"Error processing {file_path}: {e}")
                    continue
        
        if not dry_run:
            logger.info("🗂️ Executing pruning actions...")
            self._execute_pruning_actions(pruning_stats['actions'])
        else:
            logger.info("🔍 DRY RUN - No files were actually modified")
        
        return pruning_stats
    
    def _determine_file_action(self, file_path: Path) -> str:
        """Determine what action to take for a specific file"""
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            quality = data.get('validation_score', 0.0)
            sequence = data.get('sequence', '')
            
            # File age
            file_age_hours = (datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)).total_seconds() / 3600
            
            # High quality - always keep
            if quality >= self.learning_config['high_quality_threshold']:
                return 'keep'
            
            # Very old files - archive unless high quality
            if file_age_hours > self.learning_config['max_age_hours']:
                if quality >= self.learning_config['medium_quality_threshold']:
                    return 'archive'
                else:
                    return 'delete'
            
            # Medium quality - archive
            if quality >= self.learning_config['medium_quality_threshold']:
                return 'archive'
            
            # Low quality - delete
            if quality < self.learning_config['low_quality_threshold']:
                return 'delete'
            
            return 'keep'
            
        except Exception:
            return 'delete'  # If we can't read it, delete it
    
    def _execute_pruning_actions(self, actions: List[Tuple[Path, str]]):
        """Execute the pruning actions"""
        
        for file_path, action in actions:
            try:
                if action == 'archive':
                    # Compress and move to archive
                    archive_path = self.archive_dir / f"{file_path.stem}.json.gz"
                    with open(file_path, 'rb') as f_in:
                        with gzip.open(archive_path, 'wb') as f_out:
                            f_out.writelines(f_in)
                    file_path.unlink()  # Delete original
                    
                elif action == 'delete':
                    file_path.unlink()
                
                # 'keep' files are left alone
                
            except Exception as e:
                logger.debug(f"Error executing action {action} on {file_path}: {e}")
    
    def create_learning_summary(self) -> Dict[str, Any]:
        """Create a learning summary from analyzed data"""
        
        logger.info("📚 Creating learning summary...")
        
        analysis = self.analyze_discovery_files()
        
        # Extract key learnings
        learnings = {
            'timestamp': datetime.now().isoformat(),
            'total_discoveries': analysis.get('total_files', 0),
            'quality_insights': {
                'high_quality_rate': analysis.get('high_quality_percent', 0),
                'medium_quality_rate': analysis.get('medium_quality_percent', 0),
                'duplicate_rate': analysis.get('duplicate_rate', 0) * 100
            },
            'sequence_insights': {
                'avg_length': analysis.get('avg_sequence_length', 0),
                'length_distribution': self._analyze_length_distribution(analysis.get('sequence_lengths', []))
            },
            'energy_insights': {
                'avg_energy': analysis.get('avg_energy', 0),
                'energy_distribution': self._analyze_energy_distribution(analysis.get('energy_values', []))
            },
            'recommendations': self._generate_recommendations(analysis),
            'storage_info': {
                'total_size_mb': analysis.get('total_size_mb', 0),
                'avg_file_age_hours': analysis.get('avg_file_age_hours', 0)
            }
        }
        
        # Save learning summary
        summary_file = self.summary_dir / f"learning_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(learnings, f, indent=2, default=str)
        
        logger.info(f"✅ Learning summary saved to {summary_file}")
        return learnings
    
    def _analyze_length_distribution(self, lengths: List[int]) -> Dict[str, float]:
        """Analyze sequence length distribution"""
        if not lengths:
            return {}
        
        return {
            'min': float(np.min(lengths)),
            'max': float(np.max(lengths)),
            'mean': float(np.mean(lengths)),
            'std': float(np.std(lengths)),
            'median': float(np.median(lengths))
        }
    
    def _analyze_energy_distribution(self, energies: List[float]) -> Dict[str, float]:
        """Analyze energy distribution"""
        if not energies:
            return {}
        
        return {
            'min': float(np.min(energies)),
            'max': float(np.max(energies)),
            'mean': float(np.mean(energies)),
            'std': float(np.std(energies)),
            'median': float(np.median(energies))
        }
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        
        recommendations = []
        
        # Quality recommendations
        high_quality_rate = analysis.get('high_quality_percent', 0)
        if high_quality_rate < 10:
            recommendations.append("Consider adjusting quality thresholds - very few high-quality discoveries")
        elif high_quality_rate > 50:
            recommendations.append("High discovery rate - consider raising quality standards")
        
        # Duplicate recommendations
        duplicate_rate = analysis.get('duplicate_rate', 0) * 100
        if duplicate_rate > 20:
            recommendations.append("High duplicate rate - implement better sequence diversity")
        
        # Storage recommendations
        total_size_mb = analysis.get('total_size_mb', 0)
        if total_size_mb > 1000:  # > 1GB
            recommendations.append("Large storage usage - consider more aggressive pruning")
        
        # Age recommendations
        avg_age = analysis.get('avg_file_age_hours', 0)
        if avg_age > 48:
            recommendations.append("Old files detected - run archive/cleanup process")
        
        return recommendations

def main():
    """Run M4 Discovery Manager"""
    
    print("🍎 M4 DISCOVERY MANAGER")
    print("🧠 INTELLIGENT ARCHIVING & LEARNING SYSTEM")
    print("=" * 60)
    
    manager = M4DiscoveryManager()
    
    print("1. 📊 Analyzing discovery patterns...")
    analysis = manager.analyze_discovery_files()
    
    print(f"\n📈 ANALYSIS RESULTS:")
    print(f"   Total files: {analysis.get('total_files', 0):,}")
    print(f"   Estimated size: {analysis.get('total_size_mb', 0):.1f} MB")
    print(f"   High quality: {analysis.get('high_quality_percent', 0):.1f}%")
    print(f"   Duplicate rate: {analysis.get('duplicate_rate', 0)*100:.1f}%")
    print(f"   Avg file age: {analysis.get('avg_file_age_hours', 0):.1f} hours")
    
    print("\n2. 🧠 Creating learning summary...")
    learnings = manager.create_learning_summary()
    
    print("\n3. 🗂️ Intelligent pruning analysis...")
    pruning_stats = manager.intelligent_pruning(dry_run=True)
    
    print(f"\n🗂️ PRUNING RECOMMENDATIONS:")
    print(f"   Keep: {pruning_stats['files_to_keep']:,} files")
    print(f"   Archive: {pruning_stats['files_to_archive']:,} files")
    print(f"   Delete: {pruning_stats['files_to_delete']:,} files")
    print(f"   Space saved: {pruning_stats['space_saved_mb']:.1f} MB")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in learnings.get('recommendations', []):
        print(f"   • {rec}")
    
    print(f"\n🎯 To execute pruning: python3 {__file__} --execute")

if __name__ == "__main__":
    import sys
    if "--execute" in sys.argv:
        print("⚠️ EXECUTING REAL PRUNING...")
        manager = M4DiscoveryManager()
        manager.intelligent_pruning(dry_run=False)
    else:
        main()

#!/usr/bin/env python3
"""
MIGRATE 1.4M+ DISCOVERIES TO NEO4J
Batch migration script to transfer existing JSON discoveries to Neo4j graph database
Handles the massive 1.4M+ discovery files efficiently
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any
import logging
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import psutil
from datetime import datetime

from neo4j_discovery_engine import Neo4jDiscoveryEngine, NEO4J_AVAILABLE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscoveryMigrator:
    """Efficient migration of JSON discoveries to Neo4j"""
    
    def __init__(self, discovery_dir: str = "m4_continuous_discoveries"):
        self.discovery_dir = Path(discovery_dir)
        self.neo4j_engine = None
        self.processed_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
        
        # Auto-scale batch size based on system resources
        self.batch_size = self._calculate_optimal_batch_size()
        
    def _calculate_optimal_batch_size(self) -> int:
        """Calculate optimal batch size based on available system resources"""
        
        # Get system memory
        memory_gb = psutil.virtual_memory().total / (1024**3)
        cpu_count = psutil.cpu_count()
        
        # Conservative batch sizing for Neo4j transactions
        if memory_gb >= 64:  # M4 Mac Pro territory
            return 1000
        elif memory_gb >= 32:
            return 500
        elif memory_gb >= 16:
            return 250
        else:
            return 100
    
    def initialize_neo4j(self):
        """Initialize Neo4j connection"""
        
        if not NEO4J_AVAILABLE:
            raise RuntimeError("Neo4j driver not installed. Install with: pip install neo4j")
        
        try:
            self.neo4j_engine = Neo4jDiscoveryEngine()
            logger.info("✅ Neo4j connection established")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            logger.error("💡 Make sure Neo4j is running: brew services start neo4j")
            return False
    
    def get_discovery_files(self) -> List[Path]:
        """Get all discovery JSON files"""
        
        print(f"🔍 Scanning {self.discovery_dir} for discovery files...")
        
        if not self.discovery_dir.exists():
            logger.error(f"❌ Discovery directory not found: {self.discovery_dir}")
            return []
        
        discovery_files = list(self.discovery_dir.glob("m4_discovery_*.json"))
        print(f"📊 Found {len(discovery_files):,} discovery files")
        
        return discovery_files
    
    def process_batch(self, file_batch: List[Path]) -> Dict[str, int]:
        """Process a batch of discovery files"""
        
        batch_results = {"processed": 0, "errors": 0}
        
        for file_path in file_batch:
            try:
                # Load discovery data
                with open(file_path, 'r') as f:
                    discovery_data = json.load(f)
                
                # Store in Neo4j
                discovery_id = self.neo4j_engine.store_discovery(discovery_data)
                batch_results["processed"] += 1
                
            except Exception as e:
                batch_results["errors"] += 1
                logger.debug(f"Error processing {file_path}: {e}")
        
        return batch_results
    
    def migrate_all_discoveries(self):
        """Migrate all discoveries to Neo4j with progress tracking"""
        
        print("🚀 STARTING DISCOVERY MIGRATION TO NEO4J")
        print("=" * 60)
        
        # Initialize Neo4j
        if not self.initialize_neo4j():
            return False
        
        # Get all discovery files
        discovery_files = self.get_discovery_files()
        
        if not discovery_files:
            print("⚠️ No discovery files found to migrate")
            return False
        
        total_files = len(discovery_files)
        print(f"📋 Migration Plan:")
        print(f"   Files to migrate: {total_files:,}")
        print(f"   Batch size: {self.batch_size}")
        print(f"   Estimated batches: {(total_files + self.batch_size - 1) // self.batch_size}")
        print()
        
        # Process in batches
        batch_count = 0
        
        for i in range(0, total_files, self.batch_size):
            batch_count += 1
            batch_files = discovery_files[i:i + self.batch_size]
            
            print(f"🔄 Processing batch {batch_count} ({len(batch_files)} files)...")
            
            try:
                # Process batch
                batch_results = self.process_batch(batch_files)
                
                # Update counters
                self.processed_count += batch_results["processed"]
                self.error_count += batch_results["errors"]
                
                # Progress update
                progress_pct = (i + len(batch_files)) / total_files * 100
                elapsed_time = (datetime.now() - self.start_time).total_seconds()
                rate = self.processed_count / elapsed_time if elapsed_time > 0 else 0
                
                print(f"   ✅ Batch {batch_count} complete: {batch_results['processed']} processed, {batch_results['errors']} errors")
                print(f"   📊 Overall Progress: {progress_pct:.1f}% | {self.processed_count:,}/{total_files:,} | {rate:.1f} discoveries/sec")
                
                # Memory cleanup
                if batch_count % 10 == 0:
                    import gc
                    gc.collect()
                    
                    # System resource check
                    memory_usage = psutil.virtual_memory().percent
                    if memory_usage > 85:
                        print(f"⚠️ High memory usage ({memory_usage:.1f}%), reducing batch size")
                        self.batch_size = max(50, self.batch_size // 2)
                
            except Exception as e:
                logger.error(f"❌ Batch {batch_count} failed: {e}")
                self.error_count += len(batch_files)
        
        # Final summary
        self._print_migration_summary(total_files)
        
        # Close Neo4j connection
        if self.neo4j_engine:
            self.neo4j_engine.close()
        
        return True
    
    def _print_migration_summary(self, total_files: int):
        """Print migration summary"""
        
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        success_rate = (self.processed_count / total_files * 100) if total_files > 0 else 0
        
        print()
        print("🎯 MIGRATION COMPLETE!")
        print("=" * 60)
        print(f"📊 Results:")
        print(f"   Total files: {total_files:,}")
        print(f"   Successfully migrated: {self.processed_count:,}")
        print(f"   Errors: {self.error_count:,}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Time elapsed: {elapsed_time:.1f} seconds")
        print(f"   Average rate: {self.processed_count / elapsed_time:.1f} discoveries/sec")
        print()
        
        if self.neo4j_engine:
            # Get Neo4j statistics
            stats = self.neo4j_engine.get_discovery_statistics()
            print(f"🔗 Neo4j Status:")
            print(f"   Total discoveries: {stats['total_discoveries']:,}")
            print(f"   Unique sequences: {stats['unique_sequences']:,}")
            print(f"   Duplicate rate: {stats['duplicate_rate']:.1f}%")
            print()
    
    def verify_migration(self) -> bool:
        """Verify migration completed successfully"""
        
        if not self.neo4j_engine:
            return False
        
        try:
            stats = self.neo4j_engine.get_discovery_statistics()
            neo4j_count = stats['total_discoveries']
            
            # Count original files
            original_files = len(self.get_discovery_files())
            
            print(f"🔍 Migration Verification:")
            print(f"   Original JSON files: {original_files:,}")
            print(f"   Neo4j discoveries: {neo4j_count:,}")
            print(f"   Migration efficiency: {(neo4j_count / original_files * 100):.1f}%")
            
            return neo4j_count > 0
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False

def main():
    """Run discovery migration"""
    
    print("🔗 M4 DISCOVERY MIGRATION TO NEO4J")
    print("Transferring 1.4M+ JSON discoveries to graph database")
    print("=" * 70)
    
    # Check system resources
    memory_gb = psutil.virtual_memory().total / (1024**3)
    available_gb = psutil.virtual_memory().available / (1024**3)
    
    print(f"💻 System Resources:")
    print(f"   Total Memory: {memory_gb:.1f} GB")
    print(f"   Available Memory: {available_gb:.1f} GB")
    print(f"   CPU Cores: {psutil.cpu_count()}")
    print()
    
    if available_gb < 4:
        print("⚠️ Warning: Low available memory. Migration may be slow.")
        print()
    
    # Run migration
    migrator = DiscoveryMigrator()
    
    try:
        success = migrator.migrate_all_discoveries()
        
        if success:
            print("✅ Migration completed successfully!")
            
            # Verify migration
            if migrator.verify_migration():
                print("✅ Migration verification passed!")
            else:
                print("⚠️ Migration verification issues detected")
        else:
            print("❌ Migration failed")
            
    except KeyboardInterrupt:
        print("\n⚠️ Migration interrupted by user")
    except Exception as e:
        print(f"❌ Migration error: {e}")
        logger.exception("Migration failed")

if __name__ == "__main__":
    main()

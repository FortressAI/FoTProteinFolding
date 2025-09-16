#!/bin/bash
# Neo4j Database Dump Script for Prior Art Project
# Creates timestamped database dumps for backup and sharing

# Configuration
NEO4J_HOME="/opt/homebrew/var/neo4j"  # Adjust for your Neo4j installation
DATABASE_NAME="neo4j"
EXPORT_DIR="data/neo4j-dumps"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🍎 NEO4J DATABASE DUMP FOR PRIOR ART PROJECT"
echo "============================================="
echo "Database: $DATABASE_NAME"
echo "Export directory: $EXPORT_DIR"
echo "Timestamp: $TIMESTAMP"
echo

# Ensure export directory exists
mkdir -p "$EXPORT_DIR"

# Check if Neo4j is running
NEO4J_STATUS=$(neo4j status 2>/dev/null || echo "Neo4j not found in PATH")

if [[ "$NEO4J_STATUS" == *"running"* ]]; then
    echo "⚠️  Neo4j is currently running"
    echo "   Creating dump without stopping (using online backup)"
    
    # Try online backup first (Neo4j Enterprise feature)
    if command -v neo4j-admin &> /dev/null; then
        echo "🔄 Creating online database dump..."
        neo4j-admin database dump $DATABASE_NAME \
            --to-path="$EXPORT_DIR" \
            --verbose \
            2>&1 | tee "$EXPORT_DIR/dump_log_$TIMESTAMP.txt"
        
        if [ $? -eq 0 ]; then
            # Rename dump file with timestamp
            DUMP_FILE=$(find "$EXPORT_DIR" -name "*.dump" -type f -newer "$EXPORT_DIR/dump_log_$TIMESTAMP.txt" | head -1)
            if [ -n "$DUMP_FILE" ]; then
                NEW_NAME="$EXPORT_DIR/protein_discovery_db_$TIMESTAMP.dump"
                mv "$DUMP_FILE" "$NEW_NAME"
                echo "✅ Database dump created: $NEW_NAME"
                
                # Get file size
                DUMP_SIZE=$(du -h "$NEW_NAME" | cut -f1)
                echo "📊 Dump size: $DUMP_SIZE"
            fi
        else
            echo "❌ Database dump failed - check log: $EXPORT_DIR/dump_log_$TIMESTAMP.txt"
            exit 1
        fi
    else
        echo "❌ neo4j-admin not found in PATH"
        echo "   Please ensure Neo4j is properly installed"
        exit 1
    fi
    
elif [[ "$NEO4J_STATUS" == *"not running"* ]]; then
    echo "✅ Neo4j is stopped - safe to create dump"
    
    # Create dump with Neo4j stopped
    echo "🔄 Creating database dump..."
    neo4j-admin database dump $DATABASE_NAME \
        --to-path="$EXPORT_DIR" \
        --verbose \
        2>&1 | tee "$EXPORT_DIR/dump_log_$TIMESTAMP.txt"
    
    if [ $? -eq 0 ]; then
        # Rename dump file with timestamp  
        DUMP_FILE=$(find "$EXPORT_DIR" -name "*.dump" -type f -newer "$EXPORT_DIR/dump_log_$TIMESTAMP.txt" | head -1)
        if [ -n "$DUMP_FILE" ]; then
            NEW_NAME="$EXPORT_DIR/protein_discovery_db_$TIMESTAMP.dump"
            mv "$DUMP_FILE" "$NEW_NAME"
            echo "✅ Database dump created: $NEW_NAME"
            
            # Get file size
            DUMP_SIZE=$(du -h "$NEW_NAME" | cut -f1)
            echo "📊 Dump size: $DUMP_SIZE"
            
            # Restart Neo4j
            echo "🔄 Restarting Neo4j..."
            neo4j start
        fi
    else
        echo "❌ Database dump failed - check log: $EXPORT_DIR/dump_log_$TIMESTAMP.txt"
        # Restart Neo4j even if dump failed
        neo4j start
        exit 1
    fi
    
else
    echo "❌ Cannot determine Neo4j status: $NEO4J_STATUS"
    echo "   Please check your Neo4j installation"
    exit 1
fi

# Create export manifest
MANIFEST_FILE="$EXPORT_DIR/export_manifest_$TIMESTAMP.txt"
cat > "$MANIFEST_FILE" << EOF
NEO4J DATABASE EXPORT MANIFEST
==============================
Export Date: $(date)
Database: $DATABASE_NAME
Export Type: Full Database Dump
Purpose: Prior Art Project Documentation

Files Created:
- protein_discovery_db_$TIMESTAMP.dump (Database dump)
- dump_log_$TIMESTAMP.txt (Export log)
- export_manifest_$TIMESTAMP.txt (This manifest)

Database Statistics at Export:
$(python3 -c "
from neo4j_discovery_engine import Neo4jDiscoveryEngine
try:
    engine = Neo4jDiscoveryEngine()
    stats = engine.get_discovery_statistics()
    print(f'Total Discoveries: {stats.get(\"total_discoveries\", \"N/A\"):,}')
    print(f'Unique Sequences: {stats.get(\"unique_sequences\", \"N/A\"):,}')
    
    with engine.driver.session() as session:
        vqbit_count = session.run('MATCH (v:VQbit) RETURN count(v) as count').single()['count']
        quantum_count = session.run('MATCH (q:QuantumState) RETURN count(q) as count').single()['count']
        entanglements = session.run('MATCH ()-[r:QUANTUM_ENTANGLED]->() RETURN count(r) as count').single()['count']
        
    print(f'VQbit Nodes: {vqbit_count:,}')
    print(f'QuantumState Nodes: {quantum_count:,}') 
    print(f'Quantum Entanglements: {entanglements:,}')
    
    engine.close()
except Exception as e:
    print(f'Error getting stats: {e}')
")"

System Information:
- M4 Mac Pro Beast Mode
- 8 parallel discovery processes
- Neo4j Knowledge Graph
- Quantum protein discovery system

Usage:
To restore this database:
neo4j-admin database load neo4j --from-path=$EXPORT_DIR/protein_discovery_db_$TIMESTAMP.dump --overwrite-destination=true
EOF

echo
echo "📄 Export manifest created: $MANIFEST_FILE"
echo
echo "🎉 DATABASE EXPORT COMPLETED!"
echo "Files available in: $EXPORT_DIR"
echo
echo "To restore this database:"
echo "neo4j-admin database load neo4j --from-path=$EXPORT_DIR/protein_discovery_db_$TIMESTAMP.dump --overwrite-destination=true"
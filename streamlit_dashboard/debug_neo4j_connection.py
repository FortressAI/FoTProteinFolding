#!/usr/bin/env python3
"""
Debug Neo4j Connection for Streamlit Dashboard
"""

import streamlit as st
import sys
import os

st.title("🔍 Neo4j Connection Debug")

# Test the import path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

st.write(f"**Current directory:** {current_dir}")
st.write(f"**Parent directory:** {parent_dir}")

# Add parent to path
sys.path.insert(0, parent_dir)
st.write(f"**Added to Python path:** {parent_dir}")

# Test if neo4j file exists
neo4j_file = os.path.join(parent_dir, "neo4j_discovery_engine.py")
st.write(f"**Neo4j file path:** {neo4j_file}")
st.write(f"**File exists:** {os.path.exists(neo4j_file)}")

# Try to import
try:
    st.info("🔄 Attempting to import Neo4jDiscoveryEngine...")
    from neo4j_discovery_engine import Neo4jDiscoveryEngine
    st.success("✅ Successfully imported Neo4jDiscoveryEngine")
    
    # Try to create engine
    st.info("🔄 Creating Neo4j engine...")
    engine = Neo4jDiscoveryEngine()
    st.success("✅ Neo4j engine created successfully")
    
    # Try to connect and count
    st.info("🔄 Connecting to database and counting discoveries...")
    with engine.driver.session() as session:
        result = session.run("MATCH (d:Discovery) RETURN count(d) as total")
        count = result.single()['total']
        st.success(f"🎉 **FOUND {count:,} DISCOVERIES IN DATABASE!**")
        
        # Test sequence query
        st.info("🔄 Testing sequence query...")
        seq_result = session.run("""
        MATCH (d:Discovery)-[:HAS_SEQUENCE]->(s:Sequence)
        RETURN d.id, s.value, d.validation_score
        LIMIT 5
        """)
        sequences = list(seq_result)
        st.success(f"✅ Found {len(sequences)} sample sequences")
        
        for i, record in enumerate(sequences):
            st.write(f"**Sample {i+1}:** ID={record['d.id']}, Length={len(record['s.value']) if record['s.value'] else 0}, Score={record['d.validation_score']}")
            
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.write("**Error details:**")
    import traceback
    st.code(traceback.format_exc())

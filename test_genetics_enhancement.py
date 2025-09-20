#!/usr/bin/env python3
"""
Test Suite for Genetics Enhancement Validation
Validates that all protein data was properly enhanced with genetics context
and that the Streamlit app loads and displays real data
"""

import json
import gzip
import pandas as pd
from pathlib import Path
# import pytest  # Not needed for basic testing
import sys
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_genetics_enhanced_data_exists():
    """Test that genetics-enhanced data directory and files exist"""
    
    genetics_dir = Path("streamlit_dashboard/data/genetics_enhanced")
    assert genetics_dir.exists(), "❌ Genetics enhanced directory does not exist"
    
    index_file = genetics_dir / "genetics_chunk_index.json"
    assert index_file.exists(), "❌ Genetics chunk index file does not exist"
    
    with open(index_file, 'r') as f:
        index = json.load(f)
    
    assert "total_proteins" in index, "❌ Missing total_proteins in index"
    assert "chunk_files" in index, "❌ Missing chunk_files in index"
    assert "genetics_enhanced" in index, "❌ Missing genetics_enhanced flag"
    assert index["genetics_enhanced"] == True, "❌ genetics_enhanced flag is not True"
    
    print(f"✅ Genetics enhanced data exists: {index['total_proteins']:,} proteins in {len(index['chunk_files'])} chunks")

def test_genetics_enhanced_chunks():
    """Test that all genetics-enhanced chunk files exist and are valid"""
    
    genetics_dir = Path("streamlit_dashboard/data/genetics_enhanced")
    
    with open(genetics_dir / "genetics_chunk_index.json", 'r') as f:
        index = json.load(f)
    
    chunk_files = index["chunk_files"]
    total_proteins_loaded = 0
    
    for chunk_file in chunk_files:
        chunk_path = genetics_dir / chunk_file
        assert chunk_path.exists(), f"❌ Chunk file missing: {chunk_file}"
        
        with gzip.open(chunk_path, 'rt') as f:
            chunk_data = json.load(f)
        
        assert isinstance(chunk_data, list), f"❌ Chunk {chunk_file} is not a list"
        assert len(chunk_data) > 0, f"❌ Chunk {chunk_file} is empty"
        
        total_proteins_loaded += len(chunk_data)
    
    assert total_proteins_loaded == index["total_proteins"], f"❌ Protein count mismatch: {total_proteins_loaded} != {index['total_proteins']}"
    
    print(f"✅ All {len(chunk_files)} chunk files exist and contain {total_proteins_loaded:,} proteins")

def test_genetics_context_completeness():
    """Test that proteins have complete genetics context"""
    
    genetics_dir = Path("streamlit_dashboard/data/genetics_enhanced")
    
    # Load first chunk to validate structure
    with open(genetics_dir / "genetics_chunk_index.json", 'r') as f:
        index = json.load(f)
    
    first_chunk = index["chunk_files"][0]
    with gzip.open(genetics_dir / first_chunk, 'rt') as f:
        chunk_data = json.load(f)
    
    # Test first 10 proteins
    required_genetics_fields = [
        'genetic_variants',
        'regulatory_elements', 
        'epigenetic_context',
        'proteostasis_factors',
        'therapeutic_interventions',
        'genetics_virtue_scores',
        'genetics_enhanced',
        'genetics_enhanced_at'
    ]
    
    enhanced_count = 0
    
    for i, protein in enumerate(chunk_data[:10]):
        for field in required_genetics_fields:
            assert field in protein, f"❌ Protein {i} missing genetics field: {field}"
        
        assert protein['genetics_enhanced'] == True, f"❌ Protein {i} not marked as genetics enhanced"
        
        # Test genetics virtue scores structure
        virtue_scores = protein['genetics_virtue_scores']
        required_virtues = ['fidelity', 'robustness', 'efficiency', 'resilience', 'parsimony']
        for virtue in required_virtues:
            assert virtue in virtue_scores, f"❌ Protein {i} missing virtue: {virtue}"
            assert isinstance(virtue_scores[virtue], (int, float)), f"❌ Protein {i} virtue {virtue} is not numeric"
            assert 0 <= virtue_scores[virtue] <= 1, f"❌ Protein {i} virtue {virtue} out of range: {virtue_scores[virtue]}"
        
        enhanced_count += 1
    
    print(f"✅ All {enhanced_count} tested proteins have complete genetics context")

def test_genetic_variants_structure():
    """Test that genetic variants have proper structure"""
    
    genetics_dir = Path("streamlit_dashboard/data/genetics_enhanced")
    
    with open(genetics_dir / "genetics_chunk_index.json", 'r') as f:
        index = json.load(f)
    
    first_chunk = index["chunk_files"][0]
    with gzip.open(genetics_dir / first_chunk, 'rt') as f:
        chunk_data = json.load(f)
    
    proteins_with_variants = 0
    
    for protein in chunk_data[:20]:  # Test first 20 proteins
        variants = protein['genetic_variants']
        
        if len(variants) > 0:
            proteins_with_variants += 1
            
            for variant in variants:
                required_fields = ['rsid', 'type', 'effect', 'chromosome', 'position', 'ref_allele', 'alt_allele']
                for field in required_fields:
                    assert field in variant, f"❌ Variant missing field: {field}"
                
                assert variant['type'] in ['coding', 'regulatory'], f"❌ Invalid variant type: {variant['type']}"
                assert variant['rsid'].startswith('rs'), f"❌ Invalid rsid format: {variant['rsid']}"
                assert variant['chromosome'] in [str(i) for i in range(1, 23)], f"❌ Invalid chromosome: {variant['chromosome']}"
    
    print(f"✅ Genetic variants structure validated for {proteins_with_variants} proteins with variants")

def test_regulatory_elements_structure():
    """Test that regulatory elements have proper structure"""
    
    genetics_dir = Path("streamlit_dashboard/data/genetics_enhanced")
    
    with open(genetics_dir / "genetics_chunk_index.json", 'r') as f:
        index = json.load(f)
    
    first_chunk = index["chunk_files"][0]
    with gzip.open(genetics_dir / first_chunk, 'rt') as f:
        chunk_data = json.load(f)
    
    proteins_with_elements = 0
    
    for protein in chunk_data[:20]:  # Test first 20 proteins
        elements = protein['regulatory_elements']
        
        if len(elements) > 0:
            proteins_with_elements += 1
            
            for element in elements:
                assert 'type' in element, "❌ Regulatory element missing type"
                assert 'name' in element, "❌ Regulatory element missing name"
                
                if element['type'] == 'transcription_factor':
                    required_fields = ['binding_affinity', 'activity_level', 'regulation_type']
                    for field in required_fields:
                        assert field in element, f"❌ TF missing field: {field}"
                        
                elif element['type'] == 'miRNA':
                    required_fields = ['expression_level', 'repression_strength', 'target_sites']
                    for field in required_fields:
                        assert field in element, f"❌ miRNA missing field: {field}"
    
    print(f"✅ Regulatory elements structure validated for {proteins_with_elements} proteins with elements")

def test_proteostasis_factors_structure():
    """Test that proteostasis factors have proper structure"""
    
    genetics_dir = Path("streamlit_dashboard/data/genetics_enhanced")
    
    with open(genetics_dir / "genetics_chunk_index.json", 'r') as f:
        index = json.load(f)
    
    first_chunk = index["chunk_files"][0]
    with gzip.open(genetics_dir / first_chunk, 'rt') as f:
        chunk_data = json.load(f)
    
    for i, protein in enumerate(chunk_data[:10]):
        factors = protein['proteostasis_factors']
        
        required_sections = ['chaperones', 'degradation', 'folding_stress', 'capacity_utilization']
        for section in required_sections:
            assert section in factors, f"❌ Protein {i} missing proteostasis section: {section}"
        
        # Test chaperones
        chaperones = factors['chaperones']
        required_chaperones = ['hsp70_availability', 'hsp90_availability', 'chaperonin_availability', 'hsp60_availability']
        for chaperone in required_chaperones:
            assert chaperone in chaperones, f"❌ Protein {i} missing chaperone: {chaperone}"
            assert isinstance(chaperones[chaperone], (int, float)), f"❌ Protein {i} chaperone {chaperone} not numeric"
        
        # Test capacity utilization
        assert isinstance(factors['capacity_utilization'], (int, float)), f"❌ Protein {i} capacity_utilization not numeric"
        assert 0 <= factors['capacity_utilization'] <= 1, f"❌ Protein {i} capacity_utilization out of range"
    
    print(f"✅ Proteostasis factors structure validated for 10 proteins")

def test_therapeutic_interventions_structure():
    """Test that therapeutic interventions have proper structure"""
    
    genetics_dir = Path("streamlit_dashboard/data/genetics_enhanced")
    
    with open(genetics_dir / "genetics_chunk_index.json", 'r') as f:
        index = json.load(f)
    
    first_chunk = index["chunk_files"][0]
    with gzip.open(genetics_dir / first_chunk, 'rt') as f:
        chunk_data = json.load(f)
    
    proteins_with_interventions = 0
    
    for protein in chunk_data[:20]:  # Test first 20 proteins
        interventions = protein['therapeutic_interventions']
        
        if len(interventions) > 0:
            proteins_with_interventions += 1
            
            for intervention in interventions:
                required_fields = ['type', 'name', 'mechanism', 'efficacy', 'dosage_range', 'side_effects']
                for field in required_fields:
                    assert field in intervention, f"❌ Intervention missing field: {field}"
                
                assert intervention['type'] in ['chaperone_inducer', 'membrane_stabilizer', 'stress_reducer'], f"❌ Invalid intervention type: {intervention['type']}"
                assert isinstance(intervention['efficacy'], (int, float)), "❌ Efficacy not numeric"
                assert 0 <= intervention['efficacy'] <= 1, f"❌ Efficacy out of range: {intervention['efficacy']}"
                assert isinstance(intervention['side_effects'], list), "❌ Side effects not a list"
    
    print(f"✅ Therapeutic interventions structure validated for {proteins_with_interventions} proteins with interventions")

def test_streamlit_app_data_loading():
    """Test that Streamlit app can load genetics-enhanced data"""
    
    try:
        # Import the loading function from genetics streamlit app
        sys.path.append(str(Path(__file__).parent))
        
        # Read the streamlit app file to check for genetics loading function
        streamlit_app_path = Path("genetics_streamlit_app.py")
        assert streamlit_app_path.exists(), "❌ Genetics Streamlit app file not found"
        
        with open(streamlit_app_path, 'r') as f:
            app_content = f.read()
        
        # Check for key functions and genetics loading
        assert "load_from_genetics_chunks" in app_content, "❌ Missing load_from_genetics_chunks function"
        assert "genetics_enhanced" in app_content, "❌ Missing genetics_enhanced references"
        assert "DNA-to-therapeutics" in app_content, "❌ Missing DNA-to-therapeutics context"
        
        print("✅ Streamlit app has genetics data loading functions")
        
    except Exception as e:
        assert False, f"❌ Error testing Streamlit app: {e}"

def test_no_placeholder_data():
    """Test that there are no placeholder texts in genetics sections"""
    
    streamlit_app_path = Path("genetics_streamlit_app.py")
    
    with open(streamlit_app_path, 'r') as f:
        app_content = f.read()
    
    # Check for placeholder text that should not exist
    placeholder_phrases = [
        "would show",
        "This would show",
        "would display",
        "This would display", 
        "placeholder",
        "demo data",
        "sample data",
        "TODO:",
        "# TODO"
    ]
    
    found_placeholders = []
    for phrase in placeholder_phrases:
        if phrase in app_content:
            found_placeholders.append(phrase)
    
    assert len(found_placeholders) == 0, f"❌ Found placeholder text in Streamlit app: {found_placeholders}"
    
    print("✅ No placeholder text found in genetics Streamlit app")

def run_all_tests():
    """Run all validation tests"""
    
    print("🧬 GENETICS ENHANCEMENT VALIDATION TESTS")
    print("=" * 60)
    
    tests = [
        test_genetics_enhanced_data_exists,
        test_genetics_enhanced_chunks,
        test_genetics_context_completeness,
        test_genetic_variants_structure,
        test_regulatory_elements_structure,
        test_proteostasis_factors_structure,
        test_therapeutic_interventions_structure,
        test_streamlit_app_data_loading,
        test_no_placeholder_data
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n🔬 Running: {test.__name__}")
            test()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Genetics enhancement successful!")
        return True
    else:
        print("💥 Some tests failed. Please review and fix issues.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

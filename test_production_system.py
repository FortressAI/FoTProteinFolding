#!/usr/bin/env python3
"""
Test the fixed production cure discovery system
"""

import sys
from pathlib import Path

def test_imports():
    """Test all required imports work"""
    print("🔧 Testing imports...")
    
    try:
        from protein_folding_analysis import RigorousProteinFolder
        print("✅ protein_folding_analysis imported")
    except ImportError as e:
        print(f"❌ protein_folding_analysis: {e}")
        return False
    
    try:
        from fot.vqbit_mathematics import ProteinVQbitGraph
        print("✅ vqbit_mathematics imported")
    except ImportError as e:
        print(f"❌ vqbit_mathematics: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic system functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test short sequence to avoid long computation
        test_sequence = "ACDEFGHIKLMNPQRSTVWY"  # All 20 amino acids
        
        from protein_folding_analysis import RigorousProteinFolder
        folder = RigorousProteinFolder(test_sequence)
        
        # Quick test
        results = folder.run_folding_simulation(n_samples=10)
        print("✅ Classical folding analysis works")
        
        from fot.vqbit_mathematics import ProteinVQbitGraph
        vqbit = ProteinVQbitGraph(test_sequence)
        vqbit_results = vqbit.run_fot_optimization(max_iterations=10)
        print("✅ vQbit analysis works")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 TESTING PRODUCTION CURE DISCOVERY SYSTEM")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed - fix dependencies first")
        return False
    
    # Test functionality
    if not test_basic_functionality():
        print("\n❌ Functionality tests failed - fix implementation")
        return False
    
    print("\n✅ ALL TESTS PASSED")
    print("🎯 Production system ready to run!")
    print("\nTo run: python3 production_cure_discovery_fixed.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

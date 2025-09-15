#!/usr/bin/env python3
"""
Test vQbit-Classical Alignment

Verify that tuned vQbit method produces results aligned with 
the validated classical force field parameters.
"""

import numpy as np
from protein_folding_analysis import RigorousProteinFolder
from fot.vqbit_mathematics import ProteinVQbitGraph

def test_method_alignment():
    """Test alignment between classical and vQbit methods"""
    
    print("🔧 TESTING vQbit-CLASSICAL ALIGNMENT")
    print("=" * 50)
    
    # Aβ42 sequence
    ab42_sequence = 'DAEFRHDSGYEVHHQKLVFFAEDVGSNKGAIIGLMVGGVVIA'
    
    print(f"Testing sequence: {ab42_sequence}")
    print(f"Length: {len(ab42_sequence)} residues")
    
    # Test classical method (validated)
    print(f"\n🧮 CLASSICAL METHOD (VALIDATED):")
    folder = RigorousProteinFolder(ab42_sequence, temperature=298.15)
    classical_results = folder.run_folding_simulation(n_samples=200)
    
    classical_helix = classical_results['structure_analysis']['helix'] * 100
    classical_sheet = classical_results['structure_analysis']['sheet'] * 100
    classical_other = classical_results['structure_analysis']['other'] * 100
    classical_energy = classical_results['best_energy']
    
    print(f"   α-helix:  {classical_helix:.1f}%")
    print(f"   β-sheet:  {classical_sheet:.1f}%")
    print(f"   Other:    {classical_other:.1f}%")
    print(f"   Energy:   {classical_energy:.1f} kcal/mol")
    
    # Test vQbit method (tuned)
    print(f"\n🔮 vQBIT METHOD (TUNED):")
    vqbit_graph = ProteinVQbitGraph(ab42_sequence)
    vqbit_results = vqbit_graph.run_fot_optimization(max_iterations=500)
    
    vqbit_helix = vqbit_results['structure_analysis']['alpha_helix'] * 100
    vqbit_sheet = vqbit_results['structure_analysis']['beta_sheet'] * 100
    vqbit_other = (vqbit_results['structure_analysis']['extended'] + 
                   vqbit_results['structure_analysis']['left_handed']) * 100
    vqbit_fot = vqbit_results['final_fot_value']
    
    print(f"   α-helix:  {vqbit_helix:.1f}%")
    print(f"   β-sheet:  {vqbit_sheet:.1f}%")
    print(f"   Other:    {vqbit_other:.1f}%")
    print(f"   FoT:      {vqbit_fot:.1f}")
    
    # Calculate alignment metrics
    print(f"\n📊 ALIGNMENT ANALYSIS:")
    helix_diff = abs(classical_helix - vqbit_helix)
    sheet_diff = abs(classical_sheet - vqbit_sheet)
    other_diff = abs(classical_other - vqbit_other)
    
    print(f"   Helix difference:  {helix_diff:.1f}% (target: <10%)")
    print(f"   Sheet difference:  {sheet_diff:.1f}% (target: <10%)")
    print(f"   Other difference:  {other_diff:.1f}% (target: <15%)")
    
    # Assessment
    alignment_checks = {
        'helix_aligned': helix_diff < 10.0,
        'sheet_aligned': sheet_diff < 10.0,
        'other_aligned': other_diff < 15.0,
        'both_low_helix': classical_helix < 10.0 and vqbit_helix < 10.0,
        'both_moderate_sheet': 10.0 <= classical_sheet <= 40.0 and 10.0 <= vqbit_sheet <= 40.0
    }
    
    print(f"\n✅ ALIGNMENT CHECKS:")
    for check, passed in alignment_checks.items():
        symbol = "✅" if passed else "❌"
        print(f"   {check}: {symbol}")
    
    overall_aligned = all(alignment_checks.values())
    
    print(f"\n🎯 OVERALL ASSESSMENT:")
    if overall_aligned:
        print(f"   ✅ vQbit method ALIGNED with validated classical method")
        print(f"   ✅ Both methods produce realistic Aβ42 structure")
        print(f"   ✅ Ready for therapeutic discovery")
    else:
        print(f"   🔧 vQbit method needs further tuning")
        print(f"   📊 Classical method remains gold standard")
    
    return overall_aligned, {
        'classical': {
            'helix': classical_helix,
            'sheet': classical_sheet, 
            'other': classical_other,
            'energy': classical_energy
        },
        'vqbit': {
            'helix': vqbit_helix,
            'sheet': vqbit_sheet,
            'other': vqbit_other,
            'fot': vqbit_fot
        },
        'alignment': alignment_checks
    }

if __name__ == "__main__":
    success, results = test_method_alignment()
    if success:
        print(f"\n🎉 METHOD ALIGNMENT SUCCESSFUL!")
    else:
        print(f"\n🔧 FURTHER TUNING NEEDED")

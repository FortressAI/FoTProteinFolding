#!/usr/bin/env python3
"""
Repository Setup Verification

This script verifies that the FoT Protein Folding repository is properly
configured and all essential components are working.
"""

import sys
import subprocess
from pathlib import Path

def check_git_setup():
    """Verify git repository is properly configured"""
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "Not a git repository"
        
        # Check remote
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if 'FortressAI/FoTProteinFolding' not in result.stdout:
            return False, "GitHub remote not configured"
        
        return True, "Git repository properly configured"
    except Exception as e:
        return False, f"Git check failed: {e}"

def check_core_files():
    """Verify core files are present"""
    essential_files = [
        'README.md',
        'requirements.txt',
        'setup.py',
        'protein_folding_analysis.py',
        'vqbit_classical_calibration.py',
        'publication_grade_analysis.py',
        'fot/vqbit_mathematics.py',
        'demo_calibration_pipeline.py'
    ]
    
    missing_files = []
    for file_path in essential_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        return False, f"Missing files: {missing_files}"
    
    return True, f"All {len(essential_files)} essential files present"

def check_calibration_demo():
    """Verify the calibration demo can import properly"""
    try:
        from vqbit_classical_calibration import VQbitClassicalCalibrator
        from publication_grade_analysis import PublicationGradeAnalyzer
        from protein_folding_analysis import RigorousProteinFolder
        return True, "Core modules import successfully"
    except ImportError as e:
        return False, f"Import error: {e}"

def main():
    """Run all verification checks"""
    
    print("🔬 FoT Protein Folding Repository Verification")
    print("=" * 60)
    
    checks = [
        ("Git Setup", check_git_setup),
        ("Core Files", check_core_files),
        ("Module Imports", check_calibration_demo)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            passed, message = check_func()
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {check_name}: {message}")
            
            if not passed:
                all_passed = False
                
        except Exception as e:
            print(f"❌ FAIL {check_name}: Exception - {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 REPOSITORY VERIFICATION COMPLETE")
        print("✅ All checks passed - repository is ready for review!")
        print("\nNext steps:")
        print("1. Review at: https://github.com/FortressAI/FoTProteinFolding")
        print("2. Run demo: python3 demo_calibration_pipeline.py")
        print("3. Full analysis: python3 run_publication_pipeline.py")
        return 0
    else:
        print("❌ REPOSITORY VERIFICATION FAILED")
        print("Some checks failed - please address issues before proceeding")
        return 1

if __name__ == "__main__":
    sys.exit(main())

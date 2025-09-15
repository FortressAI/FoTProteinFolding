#!/usr/bin/env python3
"""
EXPLAIN JSON FILES
Categorize and explain all the different JSON files being created
"""

import json
from pathlib import Path
from collections import defaultdict

def categorize_json_files():
    """Categorize all JSON files by type and purpose"""
    
    categories = defaultdict(list)
    
    # Find all JSON files
    json_files = list(Path(".").glob("**/*.json"))
    
    for file_path in json_files:
        file_name = file_path.name
        dir_name = file_path.parent.name
        
        # Categorize by naming pattern and location
        if "therapeutic_discovery_" in file_name:
            categories["🧬 Therapeutic Discoveries"].append({
                'file': str(file_path),
                'purpose': 'Individual therapeutic target discovery results',
                'contains': 'Sequence, validation scores, therapeutic potential, physics data'
            })
        
        elif "scientific_inquiry_" in file_name:
            categories["🔬 Scientific Inquiries"].append({
                'file': str(file_path),
                'purpose': 'Scientific research discovery results',
                'contains': 'Validated discoveries with experimental correlation'
            })
        
        elif "final_discovery_report_" in file_name:
            categories["📊 Final Reports"].append({
                'file': str(file_path),
                'purpose': 'Summary reports of discovery sessions',
                'contains': 'Aggregated results, statistics, performance metrics'
            })
        
        elif "continuous_summary" in file_name:
            categories["⏰ Continuous Monitoring"].append({
                'file': str(file_path),
                'purpose': 'Real-time status of continuous discovery operations',
                'contains': 'Live metrics, performance data, system status'
            })
        
        elif "batch_" in file_name:
            categories["📦 Batch Results"].append({
                'file': str(file_path),
                'purpose': 'Individual batch processing results',
                'contains': 'Batch statistics, discoveries found, resource usage'
            })
        
        elif file_path.name.startswith("VD_"):
            categories["✅ Validated Discoveries"].append({
                'file': str(file_path),
                'purpose': 'Fully validated therapeutic discoveries',
                'contains': 'Complete discovery data with physics validation'
            })
        
        elif "prior_art" in str(file_path):
            categories["⚖️ Prior Art / Legal"].append({
                'file': str(file_path),
                'purpose': 'Patent protection and prior art documentation',
                'contains': 'Legal timestamps, publication data, patent challenges'
            })
        
        elif "bmrb_" in file_name or "constraints" in str(file_path):
            categories["🧪 Experimental Data"].append({
                'file': str(file_path),
                'purpose': 'Real experimental data from BMRB database',
                'contains': 'NMR chemical shifts, distance constraints, NOE data'
            })
        
        elif "structures" in str(file_path):
            categories["🏗️ Structural Data"].append({
                'file': str(file_path),
                'purpose': 'Known protein structure data from PDB',
                'contains': 'Atomic coordinates, structural annotations'
            })
        
        elif "thermodynamics" in str(file_path):
            categories["🌡️ Thermodynamic Data"].append({
                'file': str(file_path),
                'purpose': 'Protein thermodynamic properties',
                'contains': 'Free energies, stability data, temperature effects'
            })
        
        elif "calibration" in file_name:
            categories["⚙️ Calibration Data"].append({
                'file': str(file_path),
                'purpose': 'System calibration and optimization results',
                'contains': 'Parameter tuning, validation benchmarks'
            })
        
        elif "example" in file_name:
            categories["📝 Examples"].append({
                'file': str(file_path),
                'purpose': 'Example data for testing and demonstration',
                'contains': 'Sample discovery formats, test data'
            })
        
        else:
            categories["❓ Other"].append({
                'file': str(file_path),
                'purpose': 'Miscellaneous or unclassified files',
                'contains': 'Various data types'
            })
    
    return categories

def analyze_file_content(file_path, max_files=3):
    """Analyze content of a few files from each category"""
    
    try:
        with open(file_path) as f:
            data = json.load(f)
        
        # Extract key information
        info = {
            'size_kb': file_path.stat().st_size / 1024,
            'keys': list(data.keys()) if isinstance(data, dict) else ['array_data'],
            'sample_data': {}
        }
        
        if isinstance(data, dict):
            # Extract interesting fields
            for key in ['sequence', 'discovery_id', 'validation_score', 'therapeutic_potential', 
                       'total_discoveries', 'success_rate', 'timestamp']:
                if key in data:
                    info['sample_data'][key] = data[key]
        
        return info
    
    except Exception as e:
        return {'error': str(e), 'size_kb': file_path.stat().st_size / 1024}

def main():
    """Main function to explain JSON files"""
    
    print("📁 JSON FILES EXPLANATION")
    print("=" * 60)
    print()
    
    categories = categorize_json_files()
    
    total_files = sum(len(files) for files in categories.values())
    total_size_mb = sum(f.stat().st_size for f in Path(".").glob("**/*.json")) / (1024*1024)
    
    print(f"📊 OVERVIEW:")
    print(f"   Total JSON files: {total_files:,}")
    print(f"   Total size: {total_size_mb:.1f} MB")
    print(f"   Categories: {len(categories)}")
    print()
    
    # Display each category
    for category, files in categories.items():
        if not files:
            continue
            
        print(f"{category}")
        print(f"   Count: {len(files)} files")
        
        if files:
            print(f"   Purpose: {files[0]['purpose']}")
            print(f"   Contains: {files[0]['contains']}")
            
            # Show a few example files with analysis
            print(f"   Examples:")
            for i, file_info in enumerate(files[:3]):
                file_path = Path(file_info['file'])
                analysis = analyze_file_content(file_path)
                
                print(f"     {i+1}. {file_path.name}")
                print(f"        Size: {analysis.get('size_kb', 0):.1f} KB")
                
                if 'keys' in analysis:
                    print(f"        Keys: {', '.join(analysis['keys'][:5])}")
                
                if analysis.get('sample_data'):
                    for key, value in list(analysis['sample_data'].items())[:2]:
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        print(f"        {key}: {value}")
            
            if len(files) > 3:
                print(f"     ... and {len(files) - 3} more files")
        
        print()
    
    print("🔧 RECOMMENDATIONS:")
    print()
    print("   📁 File Management:")
    print("     - Therapeutic discoveries: Keep for research value")
    print("     - Scientific inquiries: Archive older ones periodically") 
    print("     - Batch results: Can be cleaned up after summarizing")
    print("     - Continuous monitoring: Keep latest, archive old ones")
    print()
    print("   💾 Storage Optimization:")
    print("     - Consider compressing old discovery files")
    print("     - Archive completed batches to separate directory")
    print("     - Keep only recent continuous_summary files")
    print()
    print("   🔍 Most Important Files:")
    print("     - VD_* files: These are your validated discoveries")
    print("     - therapeutic_discovery_* files: Individual research results")
    print("     - final_discovery_report_* files: Summary reports")

if __name__ == "__main__":
    main()

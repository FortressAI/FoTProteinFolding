#!/usr/bin/env python3
"""Test new scientifically generated sequences"""

from scientific_sequence_generator import ScientificSequenceGenerator
from validate_discovery_quality import DiscoveryQualityValidator

def test_sequence_quality():
    """Test that new sequences pass quality validation"""
    
    print("🧪 TESTING NEW SCIENTIFIC SEQUENCES")
    print("=" * 50)
    
    # Generate sequences
    generator = ScientificSequenceGenerator(random_seed=42)
    validator = DiscoveryQualityValidator()
    
    test_sequences = []
    
    # Generate realistic sequences
    for i in range(10):
        sequence = generator.generate_realistic_sequence()
        test_sequences.append({
            "id": f"realistic_{i+1}",
            "sequence": sequence,
            "type": "realistic"
        })
    
    # Generate pathological variants
    for i in range(5):
        sequence, name = generator.generate_known_pathological_sequence()
        test_sequences.append({
            "id": f"pathological_{i+1}",
            "sequence": sequence,
            "type": "pathological",
            "name": name
        })
    
    print(f"🔬 Testing {len(test_sequences)} sequences...")
    
    # Validate each sequence
    valid_count = 0
    for seq_data in test_sequences:
        result = validator.comprehensive_validation(seq_data)
        
        status = "✅ VALID" if result.is_valid else "❌ INVALID"
        print(f"{seq_data['id']}: {status} (Score: {result.validation_score:.3f})")
        print(f"   Sequence: {result.sequence}")
        
        if result.is_valid:
            valid_count += 1
            print(f"   Assessment: {result.scientific_assessment}")
        else:
            print(f"   Failed: {'; '.join(result.failed_checks[:2])}")
        print()
    
    print("📊 RESULTS:")
    print(f"   Valid sequences: {valid_count}/{len(test_sequences)} ({valid_count/len(test_sequences)*100:.1f}%)")
    
    if valid_count > len(test_sequences) * 0.8:
        print("✅ SUCCESS: New generator produces high-quality sequences!")
        return True
    else:
        print("❌ FAILURE: Generator still needs improvement")
        return False

if __name__ == "__main__":
    test_sequence_quality()

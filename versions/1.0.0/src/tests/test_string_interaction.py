#!/usr/bin/env python3
"""
Test script for STRING interaction analysis.

This script demonstrates how to use step1_string_interaction.py
with different configuration examples.
"""

import json
import os
import logging
from pathlib import Path

def create_test_config(test_name: str, protein_id: str, species_id: int) -> str:
    """Create a test configuration file."""
    config = {
        "target_protein_id": protein_id,
        "species_id": species_id,
        "confidence_threshold": 0.7,  # Lower threshold for testing
        "analysis_parameters": {
            "description": f"Test configuration for {test_name}",
            "test_case": test_name
        },
        "output_settings": {
            "cache_directory": "./cache",
            "output_filename": f"{test_name}_receptors.csv"
        }
    }
    
    config_path = f"config_{test_name}.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config_path

def run_test_case(test_name: str, protein_id: str, species_id: int):
    """Run a test case with specified parameters."""
    print(f"\n{'='*60}")
    print(f"Running test: {test_name}")
    print(f"Protein ID: {protein_id}")
    print(f"Species ID: {species_id}")
    print(f"{'='*60}")
    
    # Create test configuration
    config_path = create_test_config(test_name, protein_id, species_id)
    
    try:
        # Import and run analysis
        from step1_string_interaction import STRINGInteractionAnalysis
        
        analysis = STRINGInteractionAnalysis(config_path)
        receptors = analysis.analyze_interactions(confidence_threshold=0.7)
        
        if not receptors.empty:
            # Save results
            output_file = analysis.save_results(receptors, f"{test_name}_receptors.csv")
            
            print(f"\n✅ Test completed successfully!")
            print(f"📊 Found {len(receptors)} potential receptors")
            print(f"💾 Results saved to: {output_file}")
            
            # Show top 5 results
            print(f"\n🔝 Top 5 receptor candidates:")
            top_results = receptors.head(5)
            for i, (_, row) in enumerate(top_results.iterrows(), 1):
                print(f"  {i}. {row['receptor_id']}: confidence={row['confidence']:.3f}, "
                      f"literature_support={row['literature_support']}")
                print(f"     Location: {row['subcellular_location'][:60]}...")
        else:
            print("❌ No potential receptors found")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        logging.error(f"Test {test_name} failed: {str(e)}")
    
    finally:
        # Clean up config file
        if os.path.exists(config_path):
            os.remove(config_path)

def main():
    """Run test cases."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='test_results.log'
    )
    
    print("🧪 STRING Interaction Analysis Test Suite")
    print("Testing various protein targets and species...")
    
    # Test cases
    test_cases = [
        {
            "name": "human_insulin",
            "protein_id": "INSR_HUMAN",  # Insulin receptor
            "species_id": 9606,  # Human
            "description": "Human insulin receptor - should find membrane receptors"
        },
        {
            "name": "mouse_growth_factor", 
            "protein_id": "EGF_MOUSE",  # Epidermal growth factor
            "species_id": 10090,  # Mouse
            "description": "Mouse EGF - should find membrane receptors"
        },
        {
            "name": "human_cytokine",
            "protein_id": "IL6_HUMAN",  # Interleukin-6
            "species_id": 9606,  # Human
            "description": "Human interleukin-6 - should find cytokine receptors"
        }
    ]
    
    # Create cache directory
    cache_dir = Path("./cache")
    cache_dir.mkdir(exist_ok=True)
    
    for test_case in test_cases:
        run_test_case(
            test_case["name"],
            test_case["protein_id"], 
            test_case["species_id"]
        )
    
    print(f"\n{'='*60}")
    print("🏁 All tests completed!")
    print("📋 Check './cache/' directory for output files")
    print("📋 Check 'test_results.log' for detailed logs")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()

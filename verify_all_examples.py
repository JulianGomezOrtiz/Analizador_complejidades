"""
Script to verify all .pseudo files in the examples directory can be parsed without errors.
"""
import os
import sys
from pathlib import Path

# Add src directory to path to import the analyzer
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from analyzer.parser import parse_source
except ImportError:
    print("Error: Could not import analizador_complejidades module")
    sys.exit(1)

def verify_all_examples():
    """Verify all .pseudo files in the examples directory."""
    examples_dir = Path(__file__).parent / "examples"
    
    if not examples_dir.exists():
        print(f"Error: Examples directory not found at {examples_dir}")
        return False
    
    pseudo_files = sorted(examples_dir.glob("*.pseudo"))
    
    if not pseudo_files:
        print(f"No .pseudo files found in {examples_dir}")
        return False
    
    print(f"Checking {len(pseudo_files)} .pseudo files...\n")
    
    all_passed = True
    for pseudo_file in pseudo_files:
        try:
            with open(pseudo_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Try to parse the file
            parse_source(code)
            print(f"✅ {pseudo_file.name}: OK")
        except Exception as e:
            print(f"❌ Error en {pseudo_file.name}: {e}")
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All files parsed successfully!")
    else:
        print("❌ Some files have errors")
    
    return all_passed

if __name__ == "__main__":
    success = verify_all_examples()
    sys.exit(0 if success else 1)

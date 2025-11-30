import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer.parser import parse_source
from analyzer.preprocessor import normalize_source

def test_file(filepath):
    print(f"Testing {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        normalized = normalize_source(content)
        tree = parse_source(normalized)
        print(f"SUCCESS: {filepath} parsed correctly.")
        return True
    except Exception as e:
        print(f"FAILURE: {filepath} failed to parse.")
        print(e)
        return False

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    examples_dir = os.path.join(base_dir, 'examples')
    
    success = True
    for filename in os.listdir(examples_dir):
        filepath = os.path.join(examples_dir, filename)
        if os.path.isfile(filepath):
            success &= test_file(filepath)
    
    if success:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed.")
        sys.exit(1)

"""
Verification script to test all .pseudo files against the grammar
"""
import os
import sys

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

from lark import Lark

# Load grammar
grammar_path = os.path.join(current_dir, 'src', 'analyzer', 'grammar.lark')
with open(grammar_path, 'r', encoding='utf-8') as f:
    grammar = f.read()

parser = Lark(grammar, start='start', parser='lalr')

# Test all .pseudo files
examples_dir = os.path.join(current_dir, 'examples')
errors = []
successes = []

print("=" * 60)
print("PSEUDOCODE GRAMMAR VERIFICATION")
print("=" * 60)
print()

for filename in sorted(os.listdir(examples_dir)):
    if filename.endswith('.pseudo'):
        filepath = os.path.join(examples_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            parser.parse(code)
            print(f"✓ {filename:40} OK")
            successes.append(filename)
        except Exception as e:
            error_msg = str(e).split('\n')[0]  # Get first line of error
            print(f"✗ {filename:40} ERROR")
            print(f"  → {error_msg}")
            errors.append((filename, str(e)))

print()
print("=" * 60)
print(f"RESULTS: {len(successes)}/{len(successes) + len(errors)} files passed")
print("=" * 60)

if errors:
    print(f"\n{len(errors)} files with errors:")
    for filename, error in errors:
        print(f"  - {filename}")
    sys.exit(1)
else:
    print("\n✓ All files parsed successfully!")
    sys.exit(0)

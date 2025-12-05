
import sys
import os

print(f"sys.executable: {sys.executable}")
print(f"sys.path: {sys.path}")
try:
    import google.generativeai
    print("Successfully imported google.generativeai")
    print(f"google.generativeai file: {google.generativeai.__file__}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")

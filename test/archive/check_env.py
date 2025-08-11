#!/usr/bin/env python3
"""
Check environment variables and .env file
"""
import os
from pathlib import Path

print("=== Environment Check ===\n")

# Check current environment
print("1. Current Environment Variables:")
google_key = os.getenv("GOOGLE_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")
print(f"   GOOGLE_API_KEY: {'[SET]' if google_key else '[NOT SET]'}")
print(f"   GEMINI_API_KEY: {'[SET]' if gemini_key else '[NOT SET]'}")

# Check .env file
print("\n2. .env File Contents:")
env_file = Path(".env")
if env_file.exists():
    print("   .env file found!")
    with open(env_file, 'r') as f:
        for line in f:
            if 'API_KEY' in line and not line.strip().startswith('#'):
                key_name = line.split('=')[0].strip()
                print(f"   Found in .env: {key_name}=[VALUE HIDDEN]")
else:
    print("   .env file NOT found!")

# Try loading with python-dotenv
print("\n3. Trying to load .env with python-dotenv:")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("   ✓ .env loaded successfully!")
    
    # Check again
    google_key = os.getenv("GOOGLE_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    print(f"   GOOGLE_API_KEY: {'[SET]' if google_key else '[NOT SET]'}")
    print(f"   GEMINI_API_KEY: {'[SET]' if gemini_key else '[NOT SET]'}")
    
except ImportError:
    print("   ❌ python-dotenv not installed")
    print("   Install with: pip install python-dotenv")

print("\n4. Solution:")
print("   Option A: Install python-dotenv and it will auto-load .env files")
print("   Option B: Manually export: source .env")
print("   Option C: In your Python code, add at the top:")
print("            from dotenv import load_dotenv")
print("            load_dotenv()")
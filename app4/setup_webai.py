"""
Quick setup script to configure WebAI integration
"""
import os
from pathlib import Path

# Path to .env file
env_file = Path(__file__).parent / ".env"

# Check if .env exists
if not env_file.exists():
    print("❌ .env file not found")
    print("   Creating from .env.example...")
    example_file = Path(__file__).parent / ".env.example"
    if example_file.exists():
        import shutil
        shutil.copy(example_file, env_file)
        print("✅ Created .env from .env.example")
    else:
        print("❌ .env.example not found either!")
        exit(1)

# Read current .env
with open(env_file, 'r') as f:
    lines = f.readlines()

# Check current settings
print("\n📋 Current WebAI Configuration:")
print("="*50)

webai_settings = {}
for line in lines:
    line = line.strip()
    if line.startswith('USE_LOCAL_GEMINI'):
        key, val = line.split('=', 1)
        webai_settings['USE_LOCAL_GEMINI'] = val
        print(f"   USE_LOCAL_GEMINI: {val}")
    elif line.startswith('WEBAI_API_BASE_URL'):
        key, val = line.split('=', 1)
        webai_settings['WEBAI_API_BASE_URL'] = val
        print(f"   WEBAI_API_BASE_URL: {val}")
    elif line.startswith('GOOGLE_API_KEY'):
        key, val = line.split('=', 1)
        has_key = val and val != 'your_api_key_here'
        print(f"   GOOGLE_API_KEY: {'✅ Set' if has_key else '❌ Not set'}")

print("="*50)

# Suggest changes
print("\n💡 Recommended Settings for WebAI Integration:")
print("   USE_LOCAL_GEMINI=true")
print("   WEBAI_API_BASE_URL=http://localhost:6969/v1")
print("\n⚠️  Note: GOOGLE_API_KEY still needed as fallback")

# Ask if user wants to update
print("\n❓ Update .env to enable local WebAI mode? (y/n): ", end='')
response = input().strip().lower()

if response == 'y':
    # Update .env
    new_lines = []
    updated = {'USE_LOCAL_GEMINI': False, 'WEBAI_API_BASE_URL': False}
    
    for line in lines:
        if line.strip().startswith('USE_LOCAL_GEMINI'):
            new_lines.append('USE_LOCAL_GEMINI=true\n')
            updated['USE_LOCAL_GEMINI'] = True
        elif line.strip().startswith('WEBAI_API_BASE_URL'):
            new_lines.append('WEBAI_API_BASE_URL=http://localhost:6969/v1\n')
            updated['WEBAI_API_BASE_URL'] = True
        else:
            new_lines.append(line)
    
    # Add if not found
    if not updated['USE_LOCAL_GEMINI']:
        new_lines.append('\n# WebAI Integration\n')
        new_lines.append('USE_LOCAL_GEMINI=true\n')
    if not updated['WEBAI_API_BASE_URL']:
        new_lines.append('WEBAI_API_BASE_URL=http://localhost:6969/v1\n')
    
    # Write back
    with open(env_file, 'w') as f:
        f.writelines(new_lines)
    
    print("\n✅ .env updated successfully!")
    print("   USE_LOCAL_GEMINI=true")
    print("   WEBAI_API_BASE_URL=http://localhost:6969/v1")
else:
    print("\n⏭️  Skipped .env update")

print("\n🚀 Next steps:")
print("   1. Ensure WebAI-to-API is running: curl http://localhost:6969/health")
print("   2. Run integration test: python test_webai_integration.py")
print("   3. Start app4: python start.py")

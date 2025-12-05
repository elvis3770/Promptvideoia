"""
Verify .env configuration for WebAI integration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    print("❌ .env file not found!")
    exit(1)

load_dotenv(env_path)

print("\n" + "="*60)
print("📋 Environment Configuration Verification")
print("="*60)

# Check critical variables
checks = {
    "MongoDB": {
        "MONGODB_URL": os.getenv("MONGODB_URL"),
        "MONGODB_DB_NAME": os.getenv("MONGODB_DB_NAME")
    },
    "Google API": {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY")
    },
    "WebAI Integration": {
        "USE_LOCAL_GEMINI": os.getenv("USE_LOCAL_GEMINI"),
        "WEBAI_API_BASE_URL": os.getenv("WEBAI_API_BASE_URL"),
        "WEBAI_API_KEY": os.getenv("WEBAI_API_KEY")
    },
    "Prompt Optimization": {
        "PROMPT_OPTIMIZATION_ENABLED": os.getenv("PROMPT_OPTIMIZATION_ENABLED"),
        "PROMPT_OPTIMIZATION_MODEL": os.getenv("PROMPT_OPTIMIZATION_MODEL")
    }
}

all_good = True

for category, vars in checks.items():
    print(f"\n📦 {category}:")
    for key, value in vars.items():
        if value:
            # Mask sensitive values
            if "KEY" in key or "URL" in key:
                if "localhost" in value or "127.0.0.1" in value:
                    display_value = value
                elif len(value) > 20:
                    display_value = value[:10] + "..." + value[-5:]
                else:
                    display_value = "***" + value[-4:]
            else:
                display_value = value
            
            status = "✅"
            print(f"   {status} {key}: {display_value}")
        else:
            status = "❌" if key in ["GOOGLE_API_KEY", "GEMINI_API_KEY"] else "⚠️ "
            print(f"   {status} {key}: NOT SET")
            if key in ["GOOGLE_API_KEY", "GEMINI_API_KEY"]:
                all_good = False

print("\n" + "="*60)

# WebAI Integration Status
use_local = os.getenv("USE_LOCAL_GEMINI", "false").lower() == "true"
has_api_key = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))

print("\n🎯 Integration Mode:")
if use_local:
    print("   🌐 LOCAL WebAI-to-API mode ENABLED")
    print(f"   📍 Server: {os.getenv('WEBAI_API_BASE_URL', 'http://localhost:6969/v1')}")
    if has_api_key:
        print("   🛡️  Fallback to official API: AVAILABLE")
    else:
        print("   ⚠️  Fallback to official API: NOT AVAILABLE (no API key)")
else:
    print("   ☁️  OFFICIAL Google API mode")
    if has_api_key:
        print("   ✅ API key configured")
    else:
        print("   ❌ API key MISSING - optimization will fail!")
        all_good = False

print("\n" + "="*60)

# Recommendations
print("\n💡 Recommendations:")

if not has_api_key:
    print("   ⚠️  Set GOOGLE_API_KEY for fallback/official mode")
    print("      Get key: https://makersuite.google.com/app/apikey")

if use_local:
    print("   ℹ️  Make sure WebAI-to-API is running:")
    print("      curl http://localhost:6969/health")
    
if not use_local and has_api_key:
    print("   ✅ Configuration looks good for official API mode")
    
if use_local and has_api_key:
    print("   ✅ Configuration looks good for local mode with fallback")

print("\n" + "="*60)

if all_good:
    print("\n🎉 Configuration is READY!")
else:
    print("\n⚠️  Configuration needs attention (see above)")

print()

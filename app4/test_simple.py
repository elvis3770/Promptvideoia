"""Simple WebAI connectivity test"""
import asyncio
import sys
sys.path.insert(0, ".")

from backend.core.webai_client import WebAIClient

async def main():
    print("\n" + "="*60)
    print("WebAI-to-API Integration Test")
    print("="*60)
    
    client = WebAIClient(base_url="http://localhost:6969/v1")
    
    # Test 1: Connectivity
    print("\n[TEST] Testing connectivity...")
    is_connected = await client.check_connection()
    
    if is_connected:
        print("[OK] WebAI-to-API server is REACHABLE")
        
        # Test 2: Simple generation
        print("\n[TEST] Testing prompt generation...")
        try:
            response = await client.generate_content(
                prompt="Describe a woman smiling in cinematic terms",
                model="gemini-3.0-pro",
                temperature=0.7,
                max_tokens=100
            )
            
            print(f"[OK] Generation successful!")
            print(f"\n[RESPONSE] Response preview:")
            print(f"   {response.text[:200]}...")
            print(f"\n[SUCCESS] WebAI integration is WORKING!")
            
        except Exception as e:
            print(f"[ERROR] Generation failed: {e}")
            
    else:
        print("[ERROR] WebAI-to-API server is NOT reachable")
        print("   Make sure it's running on http://localhost:6969")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    asyncio.run(main())

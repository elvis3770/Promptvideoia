"""Test WebAI client connection"""
import asyncio
import sys
sys.path.insert(0, ".")

from backend.core.webai_client import WebAIClient

async def test():
    client = WebAIClient(base_url="http://localhost:6969/v1")
    
    print("Testing connection...")
    is_connected = await client.check_connection()
    print(f"Connection result: {is_connected}")
    
    if is_connected:
        print("\nTesting generation...")
        response = await client.generate_content(
            prompt="Say hello",
            model="gemini-3.0-pro"
        )
        print(f"Response: {response.text[:100]}")

if __name__ == "__main__":
    asyncio.run(test())

"""Test WebAI client with longer prompt"""
import asyncio
import sys
sys.path.insert(0, ".")

from backend.core.webai_client import WebAIClient

async def test():
    client = WebAIClient(base_url="http://localhost:6969/v1")
    
    # Use a simpler prompt first
    print("Testing with simple prompt...")
    response = await client.generate_content(
        prompt="Optimize this video prompt for Veo 3.1: woman smiling at camera, happy mood. Return as JSON with optimized_action and optimized_emotion fields.",
        model="gemini-3.0-pro",
        temperature=0.7,
        max_tokens=500
    )
    print(f"Response: {response.text[:200]}...")
    print("SUCCESS!")

if __name__ == "__main__":
    asyncio.run(test())

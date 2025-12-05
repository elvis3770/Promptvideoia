"""Test if gemini-3.0-pro works"""
import asyncio
import aiohttp

async def test_gemini_3_pro():
    async with aiohttp.ClientSession() as session:
        payload = {
            "model": "gemini-3.0-pro",
            "messages": [{"role": "user", "content": "Say 'hello' if you're Gemini 3.0 Pro"}]
        }
        
        async with session.post(
            "http://localhost:6969/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            print(f"Status: {response.status}")
            text = await response.text()
            print(f"Response: {text}")

if __name__ == "__main__":
    asyncio.run(test_gemini_3_pro())

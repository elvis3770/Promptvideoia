"""Test simple de optimización"""
import asyncio
import sys
import os
sys.path.insert(0, ".")

# Load .env
from dotenv import load_dotenv
load_dotenv()

from backend.core.prompt_engineer_agent import PromptEngineerAgent

async def main():
    print("Inicializando agente...")
    agent = PromptEngineerAgent(
        api_key=os.getenv("GOOGLE_API_KEY", "dummy"),
        model_name="gemini-3.0-pro",
        use_local=True,
        webai_base_url="http://localhost:6969/v1"
    )
    
    print("Optimizando prompt...")
    result = await agent.optimize_prompt("woman smiling")
    print(f"Resultado: {result[:100]}...")

if __name__ == "__main__":
    asyncio.run(main())

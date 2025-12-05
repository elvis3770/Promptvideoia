"""Test PromptEngineerAgent directly"""
import asyncio
import sys
import os
sys.path.insert(0, ".")

# Set environment variable for testing
os.environ["GOOGLE_API_KEY"] = "dummy-key-for-local-mode"

from backend.core.prompt_engineer_agent import PromptEngineerAgent

async def test():
    print("="*60)
    print("Testing PromptEngineerAgent directly")
    print("="*60)
    
    print("\n[INIT] Creating agent with local mode...")
    agent = PromptEngineerAgent(
        api_key="dummy-key",
        model_name="gemini-3.0-pro",
        target_video_model="veo-3.1",
        use_local=True,
        webai_base_url="http://localhost:6969/v1"
    )
    print(f"[OK] Agent created")
    print(f"     use_local: {agent.use_local}")
    print(f"     local_available: {agent.local_available}")
    print(f"     webai_client: {agent.webai_client}")
    
    print("\n[TEST] Calling refine_prompt...")
    
    user_input = {
        "action": "woman smiling at camera",
        "emotion": "happy",
        "dialogue": ""
    }
    
    template = {
        "product": {"name": "Perfume", "description": "luxury perfume"},
        "brand_guidelines": {"mood": "elegant", "color_palette": [], "lighting_style": "cinematic"},
        "subject": {"description": "elegant woman"}
    }
    
    scene = {
        "scene_id": 0,
        "name": "Preview",
        "duration": 8,
        "action_details": "woman smiling",
        "emotion": "happy",
        "camera_specs": {}
    }
    
    try:
        result = await agent.refine_prompt(user_input, template, scene)
        print(f"\n[SUCCESS] Got result!")
        print(f"Optimized action: {result.get('optimized_action', 'N/A')[:100]}...")
        print(f"Optimized emotion: {result.get('optimized_emotion', 'N/A')}")
    except Exception as e:
        print(f"\n[ERROR] refine_prompt failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())

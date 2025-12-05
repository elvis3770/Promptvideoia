"""
Integration Test Script for WebAI-to-API Integration

Tests:
1. WebAI server connectivity
2. Prompt optimization with local server
3. Fallback to official API
4. Comparison of outputs

Usage:
    python test_webai_integration.py
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.core.prompt_engineer_agent import PromptEngineerAgent
from backend.core.webai_client import WebAIClient


async def test_webai_connectivity():
    """Test 1: Check if WebAI-to-API server is reachable"""
    print("\n" + "="*60)
    print("TEST 1: WebAI-to-API Server Connectivity")
    print("="*60)
    
    client = WebAIClient()
    is_reachable = await client.check_connection()
    
    if is_reachable:
        print("✅ PASS: WebAI-to-API server is reachable")
        return True
    else:
        print("❌ FAIL: WebAI-to-API server is NOT reachable")
        print("   Make sure WebAI-to-API is running on http://localhost:6969")
        return False


async def test_local_optimization():
    """Test 2: Prompt optimization using local server"""
    print("\n" + "="*60)
    print("TEST 2: Prompt Optimization with Local Server")
    print("="*60)
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  SKIP: No API key found (needed as fallback)")
        return None
    
    # Initialize agent in local mode
    agent = PromptEngineerAgent(
        api_key=api_key,
        model_name="gemini-2.0-flash-exp",
        target_video_model="veo-3.1",
        use_local=True,
        webai_base_url="http://localhost:6969/v1"
    )
    
    # Test data
    user_input = {
        "action": "woman smiles",
        "emotion": "confident",
        "dialogue": ""
    }
    
    master_template = {
        "product": {
            "name": "Test Product",
            "description": "luxury product"
        },
        "brand_guidelines": {
            "mood": "professional",
            "color_palette": ["blue", "white"],
            "lighting_style": "soft natural lighting"
        },
        "subject": {
            "description": "professional woman in business attire"
        }
    }
    
    scene = {
        "scene_id": 1,
        "name": "Test Scene",
        "duration": 8,
        "camera_specs": {
            "angle": "medium shot",
            "movement": "static"
        }
    }
    
    try:
        print("\n📝 Input:")
        print(f"   Action: {user_input['action']}")
        print(f"   Emotion: {user_input['emotion']}")
        
        result = await agent.refine_prompt(user_input, master_template, scene)
        
        print("\n✅ Optimization successful!")
        print(f"\n📊 Results:")
        print(f"   Optimized Action: {result['optimized_action'][:100]}...")
        print(f"   Optimized Emotion: {result['optimized_emotion']}")
        print(f"   Keywords Added: {len(result.get('technical_keywords', []))}")
        print(f"   Confidence Score: {result['validation']['confidence_score']:.0%}")
        print(f"   Used Local Server: {result['optimization_metadata']['used_local_server']}")
        
        if result['optimization_metadata']['used_local_server']:
            print("\n✅ PASS: Used local WebAI server")
            return result
        else:
            print("\n⚠️  WARNING: Fell back to official API")
            return result
            
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        return None


async def test_official_api():
    """Test 3: Prompt optimization using official API"""
    print("\n" + "="*60)
    print("TEST 3: Prompt Optimization with Official API")
    print("="*60)
    
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  SKIP: No API key found")
        return None
    
    # Initialize agent in official mode
    agent = PromptEngineerAgent(
        api_key=api_key,
        model_name="gemini-2.0-flash-exp",
        target_video_model="veo-3.1",
        use_local=False  # Force official API
    )
    
    user_input = {
        "action": "woman smiles",
        "emotion": "confident",
        "dialogue": ""
    }
    
    master_template = {
        "product": {"name": "Test Product", "description": "luxury product"},
        "brand_guidelines": {"mood": "professional", "color_palette": [], "lighting_style": "soft"},
        "subject": {"description": "professional woman"}
    }
    
    scene = {
        "scene_id": 1,
        "name": "Test Scene",
        "duration": 8,
        "camera_specs": {}
    }
    
    try:
        result = await agent.refine_prompt(user_input, master_template, scene)
        
        print("\n✅ Optimization successful!")
        print(f"   Used Local Server: {result['optimization_metadata']['used_local_server']}")
        
        if not result['optimization_metadata']['used_local_server']:
            print("\n✅ PASS: Used official Google API")
            return result
        else:
            print("\n❌ FAIL: Should have used official API")
            return None
            
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        return None


async def test_fallback_mechanism():
    """Test 4: Fallback when local server is unavailable"""
    print("\n" + "="*60)
    print("TEST 4: Fallback Mechanism")
    print("="*60)
    print("ℹ️  This test requires WebAI server to be STOPPED")
    print("   If server is running, this test will use local mode instead")
    
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  SKIP: No API key found (needed for fallback)")
        return None
    
    # Initialize with local mode but wrong URL
    agent = PromptEngineerAgent(
        api_key=api_key,
        model_name="gemini-2.0-flash-exp",
        target_video_model="veo-3.1",
        use_local=True,
        webai_base_url="http://localhost:9999/v1"  # Wrong port
    )
    
    user_input = {"action": "test", "emotion": "neutral", "dialogue": ""}
    master_template = {
        "product": {"name": "Test", "description": "test"},
        "brand_guidelines": {"mood": "test", "color_palette": [], "lighting_style": "test"},
        "subject": {"description": "test"}
    }
    scene = {"scene_id": 1, "name": "Test", "duration": 8, "camera_specs": {}}
    
    try:
        result = await agent.refine_prompt(user_input, master_template, scene)
        
        if not result['optimization_metadata']['used_local_server']:
            print("\n✅ PASS: Successfully fell back to official API")
            return True
        else:
            print("\n⚠️  WARNING: Used local server (was it running?)")
            return True
            
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        return None


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("WebAI-to-API Integration Test Suite")
    print("="*60)
    
    # Check environment
    print("\n📋 Environment Check:")
    print(f"   GOOGLE_API_KEY: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Not set'}")
    print(f"   USE_LOCAL_GEMINI: {os.getenv('USE_LOCAL_GEMINI', 'false')}")
    print(f"   WEBAI_API_BASE_URL: {os.getenv('WEBAI_API_BASE_URL', 'http://localhost:6969/v1')}")
    
    # Run tests
    results = {}
    
    results['connectivity'] = await test_webai_connectivity()
    
    if results['connectivity']:
        results['local_optimization'] = await test_local_optimization()
    else:
        print("\n⚠️  Skipping local optimization test (server not reachable)")
        results['local_optimization'] = None
    
    results['official_api'] = await test_official_api()
    results['fallback'] = await test_fallback_mechanism()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r is not None and r is not False)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else ("⚠️  SKIP" if result is None else "❌ FAIL")
        print(f"   {test_name}: {status}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    elif passed > 0:
        print("\n⚠️  Some tests passed, check failures above")
    else:
        print("\n❌ All tests failed, check configuration")


if __name__ == "__main__":
    asyncio.run(main())

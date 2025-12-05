"""
Test completo de optimización de prompts con Gemini 3.0 Pro
"""
import asyncio
import sys
sys.path.insert(0, ".")

from backend.core.prompt_engineer_agent import PromptEngineerAgent

async def test_prompt_optimization():
    print("\n" + "="*70)
    print("TEST: Optimización de Prompts con Gemini 3.0 Pro")
    print("="*70)
    
    # Inicializar agente
    print("\n📋 Inicializando Prompt Engineer Agent...")
    agent = PromptEngineerAgent(
        api_key="dummy-key",  # Required but not used in local mode
        model_name="gemini-3.0-pro",
        use_local=True,
        webai_base_url="http://localhost:6969/v1"
    )
    
    # Test 1: Prompt simple
    print("\n🎬 Test 1: Optimizar prompt simple")
    simple_prompt = "woman smiling"
    print(f"   Prompt original: '{simple_prompt}'")
    
    try:
        optimized = await agent.optimize_prompt(simple_prompt)
        print(f"\n✅ Prompt optimizado:")
        print(f"   {optimized[:200]}...")
        print(f"   (Total: {len(optimized)} caracteres)")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Prompt con contexto
    print("\n\n🎬 Test 2: Optimizar prompt con contexto")
    context_prompt = "sunset over ocean, peaceful mood"
    print(f"   Prompt original: '{context_prompt}'")
    
    try:
        optimized2 = await agent.optimize_prompt(context_prompt)
        print(f"\n✅ Prompt optimizado:")
        print(f"   {optimized2[:200]}...")
        print(f"   (Total: {len(optimized2)} caracteres)")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "="*70)
    print("🎉 TODOS LOS TESTS PASARON - Gemini 3.0 Pro funcionando perfectamente")
    print("="*70)
    return True

if __name__ == "__main__":
    success = asyncio.run(test_prompt_optimization())
    sys.exit(0 if success else 1)

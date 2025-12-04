"""
Test script to run LVE Perfume commercial production
"""
import asyncio
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.core.orchestrator import ProductionOrchestrator
from backend.db.database import db

async def main():
    """Run commercial production"""
    
    # Connect to database
    print("🔌 Connecting to MongoDB...")
    await db.connect()
    
    # Load project template
    template_path = os.path.join(
        os.path.dirname(__file__),
        '../templates/lve_perfume_commercial.json'
    )
    
    print(f"📄 Loading template: {template_path}")
    with open(template_path, 'r', encoding='utf-8') as f:
        project_template = json.load(f)
    
    # Create orchestrator
    orchestrator = ProductionOrchestrator()
    
    # Run production
    print("\n" + "="*60)
    print("🎬 STARTING COMMERCIAL PRODUCTION")
    print("="*60 + "\n")
    
    try:
        result = await orchestrator.produce_commercial(
            project_template=project_template,
            auto_mode=True  # Set to False for manual approval between scenes
        )
        
        print("\n" + "="*60)
        print("✅ PRODUCTION SUCCESSFUL!")
        print("="*60)
        print(f"\n📹 Final Video: {result['final_video']}")
        print(f"📊 Clips Generated: {len(result['clips'])}")
        print(f"⏱️  Total Duration: {result['metadata']['duration']:.1f}s")
        print(f"💾 File Size: {result['metadata']['size_bytes'] / 1024 / 1024:.1f} MB")
        
    except Exception as e:
        print(f"\n❌ Production failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close database connection
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())

"""
FastAPI REST API for App4 Video Commercial Generator
"""
from __future__ import annotations

import sys
import os

# Load .env file FIRST before any other imports
from dotenv import load_dotenv
load_dotenv()

# Agregar el directorio actual al PYTHONPATH para que Python encuentre el paquete 'backend'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Any
import os
import asyncio
from datetime import datetime

from backend.core.prompt_orchestrator import PromptOrchestrator
from backend.db.database import db
from backend.db.repositories import ProjectRepository, ClipRepository
from backend.models.models import Project, ProjectStatus, ClipStatus

# Imports opcionales para el agente de optimización
try:
    from backend.core.prompt_engineer_agent import PromptEngineerAgent
    from backend.core.prompt_validator import PromptValidator
    from backend.core.prompt_optimizer import PromptOptimizer
    from backend.models.models import PromptOptimizationConfig
    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Optimization agent not available: {e}")
    AGENT_AVAILABLE = False

app = FastAPI(
    title="App4 Video Commercial Generator API",
    description="API for automated commercial video production with AI",
    version="1.0.0"
)

# CORS - Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5175",  # Current frontend port
        "http://127.0.0.1:5175",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator - initialized lazily to prevent blocking
orchestrator = None

def get_orchestrator():
    global orchestrator
    if orchestrator is None:
        orchestrator = PromptOrchestrator()
    return orchestrator

# Active productions tracking
active_productions: dict[str, dict[str]] = {}

# ============================================================
# STARTUP / SHUTDOWN
# ============================================================

@app.on_event("startup")
async def startup():
    """Connect to database on startup"""
    await db.connect()
    print("[OK] API started and connected to MongoDB")

@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown"""
    await db.close()
    print("[BYE] API shutdown")

# ============================================================
# MODELS
# ============================================================

class ProjectCreate(BaseModel):
    """Request model for creating a project"""
    template: dict
    auto_mode: bool = True

class ProductionStart(BaseModel):
    """Request model for starting production"""
    project_id: str
    auto_mode: bool = True

class PromptOptimizationRequest(BaseModel):
    """Request model for prompt optimization"""
    action: str
    emotion: str
    dialogue: Optional[str] = None
    voice_gender: Optional[str] = "female"  # Add voice gender field
    negative_prompt: Optional[str] = None  # What NOT to include in video
    product_tone: Optional[str] = None
    scene_type: Optional[str] = "general"
    camera_specs: Optional[dict] = None
    image_context: Optional[dict] = None  # Visual analysis from image (for first scene)

class PromptValidationRequest(BaseModel):
    """Request model for prompt validation"""
    action: str
    emotion: str
    product_tone: str
    dialogue: Optional[str] = None


# ============================================================
# ENDPOINTS - PROJECTS
# ============================================================

@app.get("/")
async def root():
    """API root"""
    return {
        "name": "App4 Video Commercial Generator API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/projects")
async def get_projects(
    status: Optional[str] = None,
    limit: int = 50
):
    """Get all projects"""
    try:
        project_status = ProjectStatus(status) if status else None
        projects = await ProjectRepository.get_all(status=project_status, limit=limit)
        return {"ok": True, "projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get project by ID"""
    try:
        project = await ProjectRepository.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"ok": True, "project": project}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/projects")
async def create_project(data: ProjectCreate):
    """Create a new project from template"""
    try:
        # Validate template
        project = Project(**data.template)
        
        # Create in database
        project_id = await ProjectRepository.create(project)
        
        return {
            "ok": True,
            "project_id": project.project_id,
            "message": "Project created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        # Delete clips first
        from backend.db.repositories import ClipRepository
        await ClipRepository.delete_by_project(project_id)
        
        # Delete project
        deleted = await ProjectRepository.delete(project_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {"ok": True, "message": "Project deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# ENDPOINTS - PRODUCTION
# ============================================================

async def run_production_background(project_id: str, template: dict[str], auto_mode: bool):
    """Background task for running production"""
    try:
        active_productions[project_id] = {
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
            "current_scene": 0,
            "total_scenes": len(template.get('scenes', []))
        }
        
        result = await orchestrator.produce_commercial(
            project_template=template,
            auto_mode=auto_mode
        )
        
        active_productions[project_id] = {
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat(),
            "result": result
        }
        
    except Exception as e:
        active_productions[project_id] = {
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }

@app.post("/api/production/start")
async def start_production(data: ProductionStart, background_tasks: BackgroundTasks):
    """Start production for a project"""
    try:
        # Get project
        project = await ProjectRepository.get_by_id(data.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if already running
        if data.project_id in active_productions:
            status = active_productions[data.project_id].get("status")
            if status == "running":
                raise HTTPException(status_code=400, detail="Production already running")
        
        # Update project status
        await ProjectRepository.update(data.project_id, {"status": ProjectStatus.IN_PROGRESS})
        
        # Start production in background
        background_tasks.add_task(
            run_production_background,
            data.project_id,
            project,
            data.auto_mode
        )
        
        return {
            "ok": True,
            "message": "Production started",
            "project_id": data.project_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/production/status/{project_id}")
async def get_production_status(project_id: str):
    """Get production status"""
    try:
        if project_id not in active_productions:
            # Check database
            project = await ProjectRepository.get_by_id(project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            return {
                "ok": True,
                "status": project.get("status", "draft"),
                "project": project
            }
        
        return {
            "ok": True,
            **active_productions[project_id]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# ENDPOINTS - CLIPS
# ============================================================

@app.get("/api/clips/{project_id}")
async def get_clips(project_id: str):
    """Get all clips for a project"""
    try:
        clips = await ClipRepository.get_by_project(project_id)
        return {"ok": True, "clips": clips}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clips/{project_id}/{scene_id}")
async def get_clip_by_scene(project_id: str, scene_id: int):
    """Get clip for specific scene"""
    try:
        clip = await ClipRepository.get_by_scene(project_id, scene_id)
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        return {"ok": True, "clip": clip}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# ENDPOINTS - FILES
# ============================================================

@app.get("/api/video/{project_id}/final")
async def get_final_video(project_id: str):
    """Download final commercial video"""
    try:
        project = await ProjectRepository.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        final_video = project.get("final_video")
        if not final_video or not final_video.get("path"):
            raise HTTPException(status_code=404, detail="Final video not available")
        
        video_path = final_video["path"]
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        return FileResponse(
            video_path,
            media_type="video/mp4",
            filename=f"{project_id}_commercial.mp4"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/clip/{clip_id}")
async def get_clip_video(clip_id: str):
    """Download individual clip"""
    try:
        clip = await ClipRepository.get_by_id(clip_id)
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        clip_file = clip.get("file")
        if not clip_file or not clip_file.get("path"):
            raise HTTPException(status_code=404, detail="Clip file not available")
        
        clip_path = clip_file["path"]
        if not os.path.exists(clip_path):
            raise HTTPException(status_code=404, detail="Clip file not found")
        
        return FileResponse(
            clip_path,
            media_type="video/mp4",
            filename=f"clip_{clip_id}.mp4"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# ENDPOINTS - PROMPT OPTIMIZATION
# ============================================================

@app.post("/api/prompts/optimize")
async def optimize_prompt(data: PromptOptimizationRequest):
    """
    Optimiza un prompt usando el Agente Gemini
    Útil para preview antes de crear proyecto
    """
    try:
        # Verificar si el agente está disponible
        if not AGENT_AVAILABLE:
            return {
                "ok": False,
                "error": "Prompt optimization agent not available",
                "original": {
                    "action": data.action,
                    "emotion": data.emotion
                }
            }
        
        # Verificar si el agente está habilitado
        optimization_enabled = os.getenv("PROMPT_OPTIMIZATION_ENABLED", "true").lower() == "true"
        
        if not optimization_enabled:
            return {
                "ok": False,
                "error": "Prompt optimization is disabled",
                "original": {
                    "action": data.action,
                    "emotion": data.emotion
                }
            }
        
        # Obtener API key
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {
                "ok": False,
                "error": "GEMINI_API_KEY not configured",
                "original": {
                    "action": data.action,
                    "emotion": data.emotion
                }
            }
        
        # Inicializar agente con modo local WebAI
        print("[DEBUG] Creating PromptEngineerAgent...")
        import sys; sys.stdout.flush()
        
        config = PromptOptimizationConfig()
        model_name = str("gemini-3.0-pro")  # Force pure string, confirmed available
        agent = PromptEngineerAgent(
            api_key=str(api_key),  # Force string
            model_name=model_name,
            target_video_model=str(config.model_type),  # Force string
            use_local=True,
            webai_base_url=str("http://localhost:6969/v1")  # Force string
        )
        print(f"[DEBUG] Agent created with model: {model_name}")
        
        # Crear template mínimo
        minimal_template = {
            "product": {
                "name": "Product",
                "description": data.product_tone or "Premium product"
            },
            "brand_guidelines": {
                "mood": data.product_tone or "professional",
                "color_palette": [],
                "lighting_style": "cinematic"
            },
            "subject": {
                "description": "Main subject"
            }
        }
        
        # Crear escena mínima
        scene = {
            "scene_id": 0,
            "name": "Preview",
            "duration": 8,
            "action_details": data.action,
            "emotion": data.emotion,
            "camera_specs": data.camera_specs or {}
        }
        
        # Optimizar
        user_input = {
            "action": data.action,
            "emotion": data.emotion,
            "dialogue": data.dialogue or "",
            "voice_gender": data.voice_gender or "female"
        }
        
        
        print("[DEBUG] About to call agent.refine_prompt...")
        print(f"[DEBUG] dialogue value: '{data.dialogue}'")
        print(f"[DEBUG] voice_gender: {data.voice_gender}")
        if data.image_context:
            print(f"[DEBUG] image_context received: {list(data.image_context.keys())}")
        else:
            print("[DEBUG] No image_context provided")
        import sys; sys.stdout.flush()
        
        optimized_data = await agent.refine_prompt(
            user_input=user_input,
            master_template=minimal_template,
            scene=scene,
            image_context=data.image_context  # Pass visual analysis if available
        )
        
        print("[DEBUG] refine_prompt completed!")
        
        # Return optimized data directly
        return {
            "ok": True,
            "optimized": {
                "action": optimized_data.get("optimized_action", user_input["action"]),
                "emotion": optimized_data.get("optimized_emotion", user_input["emotion"]),
                "dialogue": optimized_data.get("optimized_dialogue", ""),
                "keywords": optimized_data.get("technical_keywords", [])
            },
            "validation": optimized_data.get("validation", {}),
            "used_local_server": optimized_data.get("optimization_metadata", {}).get("used_local_server", False)
        }
        
    except Exception as e:
        print(f"[ERROR] Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

@app.post("/api/prompts/validate")
async def validate_prompt(data: PromptValidationRequest):
    """Valida coherencia de un prompt"""
    try:
        if not AGENT_AVAILABLE:
            return {
                "ok": False,
                "error": "Prompt validation not available"
            }
        
        validator = PromptValidator()
        result = validator.validate_scene_coherence(
            action=data.action,
            emotion=data.emotion,
            product_tone=data.product_tone,
            dialogue=data.dialogue
        )
        
        return {
            "ok": True,
            "validation": {
                "is_valid": result.is_valid,
                "is_coherent": result.is_coherent,
                "confidence_score": result.confidence_score,
                "issues": result.issues,
                "suggestions": result.suggestions,
                "notes": result.notes
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

# ============================================================
# FRAME ANALYSIS FOR SCENE CONTINUITY
# ============================================================

class FrameAnalysisRequest(BaseModel):
    """Request for frame analysis"""
    image_data: str  # Base64 encoded image
    mime_type: str = "image/jpeg"
    scene_context: Optional[str] = None  # Optional context about the scene
    is_first_scene: bool = False  # True if this is the first scene (product image)

@app.post("/api/prompts/analyze-frame")
async def analyze_frame_for_continuity(data: FrameAnalysisRequest):
    """
    Analyze a frame image to extract visual context for scene continuity.
    
    Send the last frame of a generated video to get analysis that can be used
    to create continuity in the next scene's prompt.
    """
    try:
        if not AGENT_AVAILABLE:
            return {
                "ok": False,
                "error": "Frame analysis not available - agent module not loaded"
            }
        
        # Get API key
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {
                "ok": False,
                "error": "GEMINI_API_KEY not configured"
            }
        
        # Create agent with official API (WebAI doesn't support vision)
        import google.generativeai as genai
        genai.configure(api_key=str(api_key))
        
        # Use Gemini 2.5 Flash for vision (has available quota)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Different prompts for first scene (product) vs continuity
        if data.is_first_scene:
            # FIRST SCENE: Comprehensive scene analysis for commercial video
            analysis_prompt = """Analyze this commercial scene image in COMPLETE DETAIL for AI video generation.

This is the FIRST SCENE of a commercial video. You must describe EVERYTHING in the image with maximum detail.

ANALYZE AND DESCRIBE:

1. CHARACTER/PERSON (if present):
   - Physical appearance (age, gender, ethnicity, hair, facial features)
   - Clothing (color, style, fabric, details)
   - Pose and body language
   - Facial expression and emotion
   - Position in frame (left, right, center, foreground, background)

2. PRODUCT(S):
   - Type and brand (if visible)
   - Physical characteristics (shape, size, materials, texture)
   - Colors and design elements
   - Packaging details
   - Position relative to character and camera
   - How many products and their arrangement

3. ENVIRONMENT/SETTING:
   - Background (studio, interior, exterior, abstract)
   - Surface/table/platform details
   - Props or decorative elements
   - Spatial composition

4. LIGHTING:
   - Direction (top, side, front, back)
   - Quality (soft, hard, diffused, dramatic)
   - Color temperature (warm, cool, neutral)
   - Shadows and highlights

5. COLORS:
   - Dominant colors in the scene
   - Color palette and harmony
   - Accent colors

6. CAMERA & COMPOSITION:
   - Shot type (close-up, medium, wide, etc.)
   - Angle (eye-level, high, low)
   - Framing and composition rules used

7. MOOD & STYLE:
   - Overall emotional tone
   - Visual style (elegant, modern, playful, dramatic, etc.)
   - Brand personality conveyed

8. COMPLETE VIDEO PROMPT:
   Generate a detailed, comprehensive prompt that describes this exact scene as the STARTING POINT for video generation.
   Include ALL elements: character description, product details, environment, lighting, colors, camera angle, and mood.

Format as JSON:
{
    "subject_position": "DETAILED character description and position",
    "camera_angle": "specific shot type and angle",
    "lighting": "complete lighting description",
    "colors": ["color1", "color2", "color3", ...],
    "mood": "emotional tone and style",
    "elements": ["character details", "product1", "product2", "environment elements", ...],
    "video_prompt": "ULTRA-DETAILED prompt describing the ENTIRE scene: character appearance and pose, all products visible, environment, lighting, colors, camera angle, and mood. This should be 3-5 sentences minimum with maximum visual detail."
}

Example video_prompt format:
"[Detailed character description: appearance, clothing, pose, expression], positioned [location in frame], [detailed product description with colors and features], arranged [product placement], on [surface description], [complete lighting description], [camera shot and angle], [color palette], [mood and style], [any additional visual details]"

BE EXTREMELY DETAILED. This prompt will be used to generate the video, so include EVERYTHING visible in the image.

Example video_prompt: "Luxury perfume bottle with gold cap and purple liquid, centered on glossy black surface, soft studio lighting from above, medium close-up shot, elegant and sophisticated mood, minimalist aesthetic"
"""
        else:
            # SUBSEQUENT SCENES: Continuity analysis
            analysis_prompt = """Analyze this video frame for scene continuity:

IMPORTANT: This is the LAST FRAME of the current scene. You need to describe how the FIRST FRAME of the NEXT scene should look to maintain visual continuity.

1. Subject position and pose in this frame
2. Camera angle and framing in this frame
3. Lighting conditions
4. Dominant colors
5. Mood/emotion conveyed
6. Key visual elements
7. How should the FIRST FRAME of the next scene look?
   - Describe the exact framing and composition to START the next scene
   - NOT camera movement, but the INITIAL STATE
   - Example: "Start with close-up of hand holding bottle, same lighting"
   - NOT: "Dolly in to close-up" (this is movement, not initial state)

Format as JSON:
{
    "subject_position": "description",
    "camera_angle": "shot type",
    "lighting": "description",
    "colors": ["color1", "color2"],
    "mood": "emotional tone",
    "elements": ["element1", "element2"],
    "next_scene_suggestion": "How the FIRST FRAME of next scene should look for continuity"
}"""
        
        # Decode base64 image
        import base64
        image_bytes = base64.b64decode(data.image_data)
        
        # Create image part for Gemini
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(image_bytes))
        
        # Generate content with image
        response = model.generate_content([analysis_prompt, image])
        response_text = response.text
        
        # Parse JSON from response
        import json
        try:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                analysis = json.loads(response_text[json_start:json_end])
            else:
                analysis = {"raw_analysis": response_text}
        except:
            analysis = {"raw_analysis": response_text}
        
        # Extract continuity elements using tracker
        from backend.core.continuity_tracker import ContinuityTracker
        tracker = ContinuityTracker()
        tracked_elements = tracker.extract_elements(analysis)
        
        # Convert to dict for JSON serialization
        elements_dict = [
            {
                'type': e.type,
                'description': e.description,
                'position': e.position,
                'details': e.details
            }
            for e in tracked_elements
        ]
        
        return {
            "ok": True,
            "analysis": analysis,
            "tracked_elements": elements_dict,  # Add tracked elements
            "used_local_server": False  # Using official API for vision
        }
            
    except Exception as e:
        print(f"[ERROR] Frame analysis failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Frame analysis error: {str(e)}")

# ============================================================
# CONTINUITY VALIDATION
# ============================================================

class ContinuityValidationRequest(BaseModel):
    """Request for continuity validation between scenes"""
    previous_elements: List[Dict]
    current_elements: List[Dict]

@app.post("/api/continuity/validate")
async def validate_continuity(data: ContinuityValidationRequest):
    """
    Validate continuity between two scenes
    
    Returns warnings and suggestions for maintaining visual consistency
    """
    try:
        from backend.core.continuity_tracker import ContinuityTracker, ContinuityElement
        
        tracker = ContinuityTracker()
        
        # Convert dicts back to ContinuityElement objects
        prev_elements = [
            ContinuityElement(
                type=e['type'],
                description=e['description'],
                position=e['position'],
                details=e['details']
            )
            for e in data.previous_elements
        ]
        
        curr_elements = [
            ContinuityElement(
                type=e['type'],
                description=e['description'],
                position=e['position'],
                details=e['details']
            )
            for e in data.current_elements
        ]
        
        # Validate continuity
        validation_result = tracker.validate_continuity(prev_elements, curr_elements)
        
        return {
            "ok": True,
            **validation_result
        }
        
    except Exception as e:
        print(f"[ERROR] Continuity validation failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@app.get("/api/prompts/keywords/{model}")
async def get_keywords(model: str = "veo-3.1"):
    """Obtiene keywords para un modelo"""
    try:
        if not AGENT_AVAILABLE:
            return {
                "ok": False,
                "error": "Keywords database not available"
            }
        
        optimizer = PromptOptimizer(model_type=model)
        keywords = optimizer.get_model_specific_keywords(category="all")
        
        return {
            "ok": True,
            "model": model,
            "keywords": keywords,
            "count": len(keywords)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting keywords: {str(e)}")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8003,
        reload=True
    )


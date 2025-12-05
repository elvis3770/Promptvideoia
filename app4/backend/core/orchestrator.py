"""
Production Orchestrator - Main coordinator for commercial production
"""
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .prompt_generator import PromptGenerator
from .continuity_engine import ContinuityEngine
from .veo_client import VeoClient
from .video_assembler import VideoAssembler
from .prompt_engineer_agent import PromptEngineerAgent
from .prompt_validator import PromptValidator
from .prompt_optimizer import PromptOptimizer
from ..db.repositories import ProjectRepository, ClipRepository, AssetRepository
from ..models.models import (
    Project, Clip, ClipStatus, ProjectStatus,
    ClipGeneration, ClipContinuity, ClipFile, ContinuityMode,
    PromptOptimizationConfig
)
from ..utils.frame_extractor import FrameExtractor

class ProductionOrchestrator:
    """Orchestrate the entire commercial production process"""
    
    def __init__(self, optimization_config: Optional[PromptOptimizationConfig] = None):
        """Initialize orchestrator with all components"""
        self.veo_client = VeoClient()
        self.frame_extractor = FrameExtractor()
        self.continuity_engine = ContinuityEngine(self.frame_extractor)
        self.video_assembler = VideoAssembler()
        self.prompt_generator = PromptGenerator({})
        
        # Optimization components
        self.optimization_config = optimization_config or PromptOptimizationConfig()
        
        # Initialize agent if enabled
        if self.optimization_config.use_agent:
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if api_key:
                # WebAI-to-API configuration
                use_local = os.getenv("USE_LOCAL_GEMINI", "false").lower() == "true"
                webai_url = os.getenv("WEBAI_API_BASE_URL", "http://localhost:6969/v1")
                
                self.prompt_agent = PromptEngineerAgent(
                    api_key=api_key,
                    model_name=self.optimization_config.gemini_model,
                    target_video_model=self.optimization_config.model_type,
                    use_local=use_local,
                    webai_base_url=webai_url
                )
                self.prompt_validator = PromptValidator()
                self.prompt_optimizer = PromptOptimizer(
                    model_type=self.optimization_config.model_type
                )
                
                if use_local:
                    print(f"[OK] Prompt optimization agent enabled with LOCAL WebAI server: {webai_url}")
                else:
                    print("[OK] Prompt optimization agent enabled with OFFICIAL Google API")
            else:
                print("[WARN] GEMINI_API_KEY not found, disabling agent")
                self.optimization_config.use_agent = False
                self.prompt_agent = None
        else:
            self.prompt_agent = None
            print("[INFO] Prompt optimization agent disabled")
        
        self.projects_dir = os.getenv("PROJECTS_DIR", "./projects")
        self.temp_dir = os.getenv("TEMP_DIR", "./temp")
    
    async def _optimize_prompt_with_agent(
        self,
        scene: dict,
        project_template: dict
    ) -> str:
        """
        Optimiza el prompt de una escena usando el agente de Gemini
        
        Args:
            scene: Datos de la escena
            project_template: Template completo del proyecto
            
        Returns:
            Prompt optimizado
        """
        if not self.prompt_agent:
            # Fallback: usar PromptGenerator tradicional
            prompt_gen = PromptGenerator(project_template)
            return prompt_gen.generate_scene_prompt(
                scene['scene_id'],
                refinement_level=2
            )
        
        try:
            print("✨ Optimizando prompt con Agente Gemini...")
            
            # Extraer campos mutables del usuario
            user_input = {
                "action": scene.get("action_details", ""),
                "emotion": scene.get("emotion", ""),
                "dialogue": scene.get("variables", {}).get("dialogue", "")
            }
            
            # Llamar al agente para optimización
            optimized_data = await self.prompt_agent.refine_prompt(
                user_input=user_input,
                master_template=project_template,
                scene=scene
            )
            
            # Mostrar resultados de optimización
            validation = optimized_data.get("validation", {})
            print(f"  ├─ Coherencia: {validation.get('confidence_score', 0):.0%}")
            print(f"  ├─ Keywords agregadas: {len(optimized_data.get('technical_keywords', []))}")
            print(f"  └─ {validation.get('notes', 'Optimización completada')}")
            
            # Construir prompt final con datos optimizados
            optimized_action = optimized_data.get("optimized_action", user_input["action"])
            optimized_emotion = optimized_data.get("optimized_emotion", user_input["emotion"])
            
            # Usar PromptGenerator para estructura final
            # pero con datos optimizados
            scene_optimized = scene.copy()
            scene_optimized["action_details"] = optimized_action
            scene_optimized["emotion"] = optimized_emotion
            
            prompt_gen = PromptGenerator(project_template)
            final_prompt = prompt_gen.generate_scene_prompt(
                scene['scene_id'],
                refinement_level=1  # Nivel bajo porque ya está optimizado
            )
            
            # Reemplazar con acción optimizada si es necesario
            if optimized_action and optimized_action not in final_prompt:
                final_prompt = optimized_action
            
            return final_prompt
            
        except Exception as e:
            print(f"⚠️  Error en optimización con agente: {e}")
            print("   Usando PromptGenerator tradicional como fallback")
            
            # Fallback
            prompt_gen = PromptGenerator(project_template)
            return prompt_gen.generate_scene_prompt(
                scene['scene_id'],
                refinement_level=2
            )
    
    async def produce_commercial(
        self,
        project_template: dict,
        auto_mode: bool = True
    ) -> dict:
        """
        Orchestrate full commercial production
        
        Args:
            project_template: Full project configuration
            auto_mode: If True, run automatically. If False, wait for approval between scenes
        
        Returns:
            Production result with final video path and metadata
        """
        project_id = project_template['project_id']
        print(f"\n🎬 Starting production: {project_id}")
        print(f"📋 Mode: {'Automatic' if auto_mode else 'Manual approval'}")
        
        # Create project in database
        project = Project(**project_template)
        await ProjectRepository.create(project)
        await ProjectRepository.update(project_id, {'status': ProjectStatus.IN_PROGRESS})
        
        # Setup directories
        project_dir = os.path.join(self.projects_dir, project_id)
        clips_dir = os.path.join(project_dir, 'clips')
        final_dir = os.path.join(project_dir, 'final')
        os.makedirs(clips_dir, exist_ok=True)
        os.makedirs(final_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize prompt generator
        prompt_gen = PromptGenerator(project_template)
        refinement_level = project_template.get('refinement_settings', {}).get('iterations', 2)
        
        # Generate all clips
        clips_info = []
        scenes = project_template['scenes']
        
        for scene_idx, scene in enumerate(scenes):
            scene_id = scene['scene_id']
            print(f"\n{'='*60}")
            print(f"🎬 Scene {scene_idx + 1}/{len(scenes)}: {scene.get('name', f'Scene {scene_id}')}")
            print(f"{'='*60}")
            
            # Generate prompt with agent optimization if enabled
            if self.optimization_config.use_agent and self.prompt_agent:
                prompt = await self._optimize_prompt_with_agent(scene, project_template)
            else:
                prompt = prompt_gen.generate_scene_prompt(scene_id, refinement_level)
            
            print(f"📝 Prompt: {prompt[:100]}...")
            
            # Determine generation mode
            is_first_scene = scene_idx == 0
            continuity_mode = scene.get('continuity_mode', 'initial')
            
            # Generate clip
            if is_first_scene or continuity_mode == 'initial':
                clip_result = await self._generate_initial_clip(
                    project_template, scene, prompt, clips_dir, scene_idx
                )
            else:
                # Use continuity from previous clip
                previous_clip = clips_info[-1]
                clip_result = await self._generate_continuation_clip(
                    project_template, scene, prompt, clips_dir, scene_idx, previous_clip
                )
            
            clips_info.append(clip_result)
            
            # Update scene status in project
            await ProjectRepository.update_scene_status(
                project_id, scene_id, ClipStatus.COMPLETED, clip_result['clip_id']
            )
            
            print(f"✅ Scene {scene_idx + 1} completed: {clip_result['local_path']}")
            
            # Manual mode: wait for approval
            if not auto_mode and scene_idx < len(scenes) - 1:
                print(f"\n⏸️  Waiting for approval to continue to scene {scene_idx + 2}...")
                # In real implementation, this would wait for user input via API
                await asyncio.sleep(2)  # Placeholder
        
        # Assemble final video
        print(f"\n{'='*60}")
        print("🎞️  Assembling final commercial...")
        print(f"{'='*60}")
        
        clip_paths = [c['local_path'] for c in clips_info]
        final_video_path = os.path.join(final_dir, f"{project_id}_commercial.mp4")
        
        self.video_assembler.assemble(
            clips=clip_paths,
            output_path=final_video_path,
            add_transitions=True
        )
        
        # Get final video info
        video_info = self.video_assembler.get_video_info(final_video_path)
        
        # Update project with final video
        await ProjectRepository.update(project_id, {
            'status': ProjectStatus.COMPLETED,
            'final_video': {
                'path': final_video_path,
                'duration': video_info['duration'],
                'size_bytes': video_info['size_bytes'],
                'created_at': datetime.utcnow()
            }
        })
        
        # Cleanup temp files
        self.continuity_engine.cleanup_temp_frames(self.temp_dir)
        
        print(f"\n{'='*60}")
        print(f"🎉 Production Complete!")
        print(f"📹 Final video: {final_video_path}")
        print(f"⏱️  Duration: {video_info['duration']:.1f}s")
        print(f"💾 Size: {video_info['size_bytes'] / 1024 / 1024:.1f} MB")
        print(f"{'='*60}\n")
        
        return {
            'project_id': project_id,
            'status': 'completed',
            'final_video': final_video_path,
            'clips': clips_info,
            'metadata': video_info
        }
    
    async def _generate_initial_clip(
        self,
        project_template: dict,
        scene: dict,
        prompt: str,
        clips_dir: str,
        scene_idx: int
    ) -> dict:
        """Generate first clip or clip without continuity"""
        
        # Check if we have reference images for subject
        reference_images = []
        subject = project_template.get('subject', {})
        if subject.get('reference_image_ids'):
            # In real implementation, would load from assets
            # For now, just note that references would be used
            print("📸 Using subject reference images")
        
        # Generate video
        print("🎬 Generating initial clip...")
        
        if reference_images:
            result = await self.veo_client.generate_from_reference_images(
                prompt=prompt,
                reference_images=reference_images,
                duration_seconds=scene.get('duration', 8)
            )
        else:
            result = await self.veo_client.generate_text_to_video(
                prompt=prompt,
                duration_seconds=scene.get('duration', 8)
            )
        
        # Wait for completion
        operation_name = result['operation_name']
        await self.veo_client.wait_for_completion(operation_name)
        
        # Download clip
        clip_path = await self._download_and_save_clip(
            operation_name, clips_dir, scene_idx
        )
        
        # Save to database
        clip_id = f"clip_{uuid.uuid4().hex[:8]}"
        clip = Clip(
            clip_id=clip_id,
            project_id=project_template['project_id'],
            scene_id=scene['scene_id'],
            status=ClipStatus.COMPLETED,
            generation=ClipGeneration(
                operation_name=operation_name,
                prompt=prompt,
                model=result.get('model', 'veo-3.1-fast-generate-preview'),
                duration_seconds=scene.get('duration', 8)
            ),
            continuity=ClipContinuity(mode=ContinuityMode.INITIAL),
            file=ClipFile(
                path=clip_path,
                size_bytes=os.path.getsize(clip_path),
                duration=scene.get('duration', 8),
                resolution="1080p"
            )
        )
        
        await ClipRepository.create(clip)
        
        return {
            'clip_id': clip_id,
            'scene_id': scene['scene_id'],
            'local_path': clip_path,
            'operation_name': operation_name
        }
    
    async def _generate_continuation_clip(
        self,
        project_template: dict,
        scene: dict,
        prompt: str,
        clips_dir: str,
        scene_idx: int,
        previous_clip: dict
    ) -> dict:
        """Generate clip with continuity from previous"""
        
        print("🔗 Generating clip with continuity...")
        
        # Prepare continuity references
        reference_images = await self.continuity_engine.prepare_continuity_references(
            previous_clip_path=previous_clip['local_path'],
            temp_dir=self.temp_dir
        )
        
        # Generate with references
        result = await self.veo_client.generate_from_reference_images(
            prompt=prompt,
            reference_images=reference_images,
            duration_seconds=scene.get('duration', 8),
            model="veo-3.1-generate-preview"  # Use full model for reference images
        )
        
        # Wait for completion
        operation_name = result['operation_name']
        await self.veo_client.wait_for_completion(operation_name)
        
        # Download clip
        clip_path = await self._download_and_save_clip(
            operation_name, clips_dir, scene_idx
        )
        
        # Save to database
        clip_id = f"clip_{uuid.uuid4().hex[:8]}"
        clip = Clip(
            clip_id=clip_id,
            project_id=project_template['project_id'],
            scene_id=scene['scene_id'],
            status=ClipStatus.COMPLETED,
            generation=ClipGeneration(
                operation_name=operation_name,
                prompt=prompt,
                model="veo-3.1-generate-preview",
                duration_seconds=scene.get('duration', 8)
            ),
            continuity=ClipContinuity(
                mode=ContinuityMode.LAST_FRAME_REFERENCE,
                previous_clip_id=previous_clip['clip_id']
            ),
            file=ClipFile(
                path=clip_path,
                size_bytes=os.path.getsize(clip_path),
                duration=scene.get('duration', 8),
                resolution="1080p"
            )
        )
        
        await ClipRepository.create(clip)
        
        return {
            'clip_id': clip_id,
            'scene_id': scene['scene_id'],
            'local_path': clip_path,
            'operation_name': operation_name
        }
    
    async def _download_and_save_clip(
        self,
        operation_name: str,
        clips_dir: str,
        scene_idx: int
    ) -> str:
        """Download and save a generated clip"""
        
        print("⬇️  Downloading clip...")
        video_bytes = await self.veo_client.download_video(operation_name)
        
        clip_filename = f"scene_{scene_idx + 1:02d}.mp4"
        clip_path = os.path.join(clips_dir, clip_filename)
        
        with open(clip_path, 'wb') as f:
            f.write(video_bytes)
        
        print(f"💾 Saved: {clip_path} ({len(video_bytes) / 1024 / 1024:.1f} MB)")
        
        return clip_path

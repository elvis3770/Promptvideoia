"""
Prompt Orchestrator - Main coordinator for prompt optimization only
Simplified version without video generation components
"""
import os
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from .prompt_generator import PromptGenerator
from .prompt_engineer_agent import PromptEngineerAgent
from .prompt_validator import PromptValidator
from .prompt_optimizer import PromptOptimizer
from ..models.models import PromptOptimizationConfig


class PromptOrchestrator:
    """Orchestrate prompt optimization process - no video generation"""
    
    def __init__(self, optimization_config: Optional[PromptOptimizationConfig] = None):
        """Initialize orchestrator with prompt optimization components only"""
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
    
    async def optimize_prompt(
        self,
        user_input: Dict[str, Any],
        template: Optional[Dict[str, Any]] = None,
        scene: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Optimize a prompt using the Gemini agent
        
        Args:
            user_input: Dict with action, emotion, dialogue
            template: Optional brand/product template
            scene: Optional scene configuration
            
        Returns:
            Dict with optimized prompt data
        """
        if not self.prompt_agent:
            return {
                "ok": False,
                "error": "Prompt agent not initialized",
                "original": user_input
            }
        
        try:
            result = await self.prompt_agent.refine_prompt(
                user_input=user_input,
                master_template=template,
                scene=scene or {}
            )
            
            return {
                "ok": True,
                "optimized": result,
                "original": user_input
            }
            
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "original": user_input
            }
    
    async def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Validate a prompt for video generation compatibility"""
        if not hasattr(self, 'prompt_validator') or not self.prompt_validator:
            return {"valid": True, "notes": "No validator available"}
        
        return self.prompt_validator.validate(prompt)
    
    async def generate_prompt_from_template(
        self,
        template: Dict[str, Any],
        scene_index: int = 0
    ) -> str:
        """Generate a base prompt from a template"""
        return self.prompt_generator.generate_for_scene(template, scene_index)

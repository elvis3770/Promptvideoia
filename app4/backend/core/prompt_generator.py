"""
Prompt Generator - Generate optimized prompts from templates
"""
from typing import Dict, Any, List
import re

class PromptGenerator:
    """Generate structured prompts from templates"""
    
    def __init__(self, project_template: dict):
        """
        Initialize with project template
        
        Args:
            project_template: Full project configuration
        """
        self.template = project_template
        self.subject = project_template.get('subject', {})
        self.product = project_template.get('product', {})
        self.brand_guidelines = project_template.get('brand_guidelines', {})
    
    def generate_scene_prompt(self, scene_id: int, refinement_level: int = 0) -> str:
        """
        Generate optimized prompt for a specific scene
        
        Args:
            scene_id: ID of the scene (1-indexed)
            refinement_level: Level of detail (0-3)
                0 = Basic
                1 = + Emotion
                2 = + Camera specs
                3 = + Cinematic quality
        
        Returns:
            Optimized prompt string
        """
        # Find scene by ID
        scene = None
        for s in self.template['scenes']:
            if s['scene_id'] == scene_id:
                scene = s
                break
        
        if not scene:
            raise ValueError(f"Scene {scene_id} not found in template")
        
        # Start with template
        prompt = scene['prompt_template']
        
        # Replace variables
        variables = scene.get('variables', {})
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            prompt = prompt.replace(placeholder, value)
        
        # Replace subject
        subject_desc = self.subject.get('description', '')
        prompt = prompt.replace("{{subject}}", subject_desc)
        
        # Replace product
        if self.product:
            product_desc = self.product.get('description', '')
            prompt = prompt.replace("{{product}}", product_desc)
        
        # Add refinement details
        if refinement_level >= 1:
            emotion = scene.get('emotion', '')
            if emotion:
                prompt += f", {emotion}"
        
        if refinement_level >= 2:
            camera_specs = scene.get('camera_specs', {})
            if camera_specs:
                angle = camera_specs.get('angle', '')
                movement = camera_specs.get('movement', '')
                if angle:
                    prompt += f", {angle}"
                if movement:
                    prompt += f", {movement}"
        
        if refinement_level >= 3:
            # Add cinematic quality descriptors
            lighting = self.brand_guidelines.get('lighting_style', '')
            if lighting:
                prompt += f", {lighting}"
            prompt += ", cinematic lighting, 8k quality, professional commercial photography"
        
        return prompt
    
    def generate_all_prompts(self, refinement_level: int = 2) -> List[dict]:
        """
        Generate prompts for all scenes
        
        Args:
            refinement_level: Level of detail for all prompts
        
        Returns:
            List of dicts with scene_id and prompt
        """
        prompts = []
        for scene in self.template['scenes']:
            scene_id = scene['scene_id']
            prompt = self.generate_scene_prompt(scene_id, refinement_level)
            prompts.append({
                'scene_id': scene_id,
                'scene_name': scene.get('name', f'Scene {scene_id}'),
                'prompt': prompt,
                'duration': scene.get('duration', 8)
            })
        return prompts
    
    def refine_prompt(self, base_prompt: str, focus_areas: List[str]) -> str:
        """
        Refine a prompt with specific focus areas
        
        Args:
            base_prompt: Original prompt
            focus_areas: List of areas to emphasize
                e.g., ['subject_consistency', 'product_visibility', 'lighting']
        
        Returns:
            Refined prompt
        """
        refinements = {
            'subject_consistency': f"maintaining exact appearance of {self.subject.get('description', 'subject')}",
            'product_visibility': f"clearly showing {self.product.get('name', 'product')} with prominent placement",
            'lighting_coherence': f"consistent {self.brand_guidelines.get('lighting_style', 'lighting')}",
            'emotional_progression': "natural emotional transition",
            'motion_smoothness': "smooth fluid motion, no jerky movements"
        }
        
        refined = base_prompt
        for area in focus_areas:
            if area in refinements:
                refined += f", {refinements[area]}"
        
        return refined

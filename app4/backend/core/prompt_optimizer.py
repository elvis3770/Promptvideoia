"""
Prompt Optimizer - Optimización de prompts con keywords técnicas
"""
from __future__ import annotations
from typing import List, Dict
import re


class PromptOptimizer:
    """
    Optimiza prompts agregando keywords técnicas y mejorando estructura
    
    Funciones:
    - Agregar keywords específicas para el modelo target
    - Optimizar estructura del prompt
    - Mejorar especificaciones cinematográficas
    - Mantener base de conocimiento de keywords efectivas
    """
    
    # Keywords por modelo
    MODEL_KEYWORDS = {
        "veo-3.1": {
            "quality": ["4K quality", "high-resolution", "professional", "cinematic"],
            "lighting": [
                "soft key lighting", "dramatic rim light", "golden hour",
                "studio lighting", "natural light", "diffused lighting"
            ],
            "camera": [
                "shallow depth of field", "bokeh", "smooth tracking shot",
                "dolly movement", "crane shot", "steadicam"
            ],
            "composition": [
                "rule of thirds", "symmetrical composition", "leading lines",
                "negative space", "balanced frame"
            ],
            "style": [
                "luxury commercial aesthetic", "editorial style",
                "fashion photography", "product photography"
            ]
        }
    }
    
    # Keywords por tipo de escena
    SCENE_TYPE_KEYWORDS = {
        "product_reveal": [
            "product photography", "clean background", "focused lighting",
            "detailed texture", "premium presentation"
        ],
        "character_closeup": [
            "portrait lighting", "soft focus background", "eye contact",
            "facial expression", "emotional depth"
        ],
        "action": [
            "dynamic movement", "motion blur", "energetic", "fluid motion"
        ],
        "atmospheric": [
            "moody lighting", "atmospheric", "cinematic mood",
            "dramatic shadows", "depth"
        ]
    }
    
    # Keywords por emoción
    EMOTION_KEYWORDS = {
        "confianza": ["confident posture", "direct gaze", "powerful presence"],
        "misterio": ["mysterious atmosphere", "enigmatic expression", "shadowy"],
        "alegría": ["bright", "radiant", "joyful energy", "warm tones"],
        "elegancia": ["graceful movement", "refined", "sophisticated", "poised"]
    }
    
    def __init__(self, model_type: str = "veo-3.1"):
        """
        Inicializa el optimizador
        
        Args:
            model_type: Modelo de video target
        """
        self.model_type = model_type
        self.model_keywords = self.MODEL_KEYWORDS.get(model_type, {})
    
    def add_technical_keywords(
        self,
        prompt: str,
        scene_type: str = "general",
        emotion: Optional[str] = None
    ) -> str:
        """
        Agrega keywords técnicas al prompt
        
        Args:
            prompt: Prompt original
            scene_type: Tipo de escena (product_reveal, character_closeup, etc)
            emotion: Emoción de la escena
            
        Returns:
            Prompt con keywords agregadas
        """
        keywords_to_add = []
        
        # 1. Keywords de calidad (siempre agregar una)
        if "4K" not in prompt and "quality" not in prompt.lower():
            keywords_to_add.append("4K quality")
        
        # 2. Keywords por tipo de escena
        scene_keywords = self.SCENE_TYPE_KEYWORDS.get(scene_type, [])
        for keyword in scene_keywords[:2]:  # Máximo 2 keywords de escena
            if keyword.lower() not in prompt.lower():
                keywords_to_add.append(keyword)
        
        # 3. Keywords por emoción
        if emotion:
            emotion_lower = emotion.lower()
            for emotion_key, keywords in self.EMOTION_KEYWORDS.items():
                if emotion_key in emotion_lower:
                    for keyword in keywords[:1]:  # 1 keyword de emoción
                        if keyword.lower() not in prompt.lower():
                            keywords_to_add.append(keyword)
                    break
        
        # 4. Agregar keywords al final del prompt
        if keywords_to_add:
            enhanced_prompt = f"{prompt}, {', '.join(keywords_to_add)}"
            return enhanced_prompt
        
        return prompt
    
    def optimize_structure(self, prompt: str) -> str:
        """
        Optimiza la estructura del prompt para mejor rendimiento
        
        Args:
            prompt: Prompt original
            
        Returns:
            Prompt con estructura optimizada
        """
        # 1. Remover puntos finales innecesarios
        prompt = prompt.rstrip(".")
        
        # 2. Asegurar que las comas estén bien espaciadas
        prompt = re.sub(r'\s*,\s*', ', ', prompt)
        
        # 3. Remover espacios múltiples
        prompt = re.sub(r'\s+', ' ', prompt)
        
        # 4. Capitalizar primera letra
        if prompt:
            prompt = prompt[0].upper() + prompt[1:]
        
        return prompt.strip()
    
    def enhance_cinematography(
        self,
        prompt: str,
        camera_specs: Optional[dict] = None
    ) -> str:
        """
        Mejora las especificaciones cinematográficas del prompt
        
        Args:
            prompt: Prompt original
            camera_specs: Especificaciones de cámara (angle, movement, etc)
            
        Returns:
            Prompt con cinematografía mejorada
        """
        if not camera_specs:
            return prompt
        
        enhancements = []
        
        # Agregar movimiento de cámara si no existe
        movement = camera_specs.get("movement", "")
        if movement and movement.lower() not in prompt.lower():
            movement_map = {
                "dolly": "smooth dolly movement",
                "pan": "slow pan",
                "zoom": "gradual zoom",
                "static": "static shot",
                "tracking": "tracking shot"
            }
            for key, value in movement_map.items():
                if key in movement.lower():
                    enhancements.append(value)
                    break
        
        # Agregar ángulo si no existe
        angle = camera_specs.get("angle", "")
        if angle and "shot" not in prompt.lower():
            angle_map = {
                "close-up": "close-up shot",
                "medium": "medium shot",
                "wide": "wide shot",
                "full": "full shot"
            }
            for key, value in angle_map.items():
                if key in angle.lower():
                    enhancements.append(value)
                    break
        
        # Agregar focal length si existe
        focal_length = camera_specs.get("focal_length", "")
        if focal_length and "mm" not in prompt.lower():
            enhancements.append(f"{focal_length} lens")
        
        # Integrar mejoras al prompt
        if enhancements:
            enhanced_prompt = f"{prompt}, {', '.join(enhancements)}"
            return enhanced_prompt
        
        return prompt
    
    def get_model_specific_keywords(self, category: str = "all") -> List[str]:
        """
        Obtiene keywords específicas para el modelo actual
        
        Args:
            category: Categoría de keywords (quality, lighting, camera, etc)
            
        Returns:
            Lista de keywords
        """
        if category == "all":
            all_keywords = []
            for cat_keywords in self.model_keywords.values():
                all_keywords.extend(cat_keywords)
            return all_keywords
        
        return self.model_keywords.get(category, [])
    
    def optimize_full_prompt(
        self,
        prompt: str,
        scene_type: str = "general",
        emotion: Optional[str] = None,
        camera_specs: Optional[dict] = None
    ) -> Dict[str, any]:
        """
        Optimización completa del prompt
        
        Args:
            prompt: Prompt original
            scene_type: Tipo de escena
            emotion: Emoción
            camera_specs: Especificaciones de cámara
            
        Returns:
            dict con prompt optimizado y metadata
        """
        original_prompt = prompt
        keywords_added = []
        
        # 1. Optimizar estructura
        prompt = self.optimize_structure(prompt)
        
        # 2. Agregar keywords técnicas
        prompt_before_keywords = prompt
        prompt = self.add_technical_keywords(prompt, scene_type, emotion)
        
        # Detectar qué keywords se agregaron
        if prompt != prompt_before_keywords:
            added_text = prompt[len(prompt_before_keywords):].strip(", ")
            keywords_added = [k.strip() for k in added_text.split(",")]
        
        # 3. Mejorar cinematografía
        prompt = self.enhance_cinematography(prompt, camera_specs)
        
        return {
            "original_prompt": original_prompt,
            "optimized_prompt": prompt,
            "keywords_added": keywords_added,
            "optimization_applied": {
                "structure": True,
                "keywords": len(keywords_added) > 0,
                "cinematography": camera_specs is not None
            }
        }

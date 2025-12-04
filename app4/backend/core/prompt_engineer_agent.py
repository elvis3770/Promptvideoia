"""
Prompt Engineer Agent - Agente de Gemini para optimización de prompts
Actúa como capa de refinamiento entre entrada del usuario y generación de video
"""
from __future__ import annotations
import google.generativeai as genai
import json
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptEngineerAgent:
    """
    Agente de IA que optimiza prompts para generación de video.
    
    Responsabilidades:
    - Refinar lenguaje simple a términos técnicos cinematográficos
    - Validar coherencia entre acción, emoción y tono del producto
    - Optimizar keywords para Veo 3.1
    - Ajustar tono y acento del diálogo
    """
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash-exp",
        target_video_model: str = "veo-3.1"
    ):
        """
        Inicializa el agente con configuración de Gemini
        
        Args:
            api_key: API key de Google Gemini
            model_name: Modelo de Gemini a usar
            target_video_model: Modelo de video target (veo-3.1, runway, etc)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.target_video_model = target_video_model
        
        # Configurar Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"PromptEngineerAgent initialized with model: {model_name}")
    
    async def refine_prompt(
        self,
        user_input: dict,
        master_template: dict,
        scene: dict
    ) -> dict:
        """
        Refina y optimiza un prompt usando el agente de Gemini
        
        Args:
            user_input: Campos mutables del usuario (dialogue, action, emotion)
            master_template: Template maestro del proyecto
            scene: Datos completos de la escena
            
        Returns:
            dict con campos optimizados y metadata de optimización
        """
        try:
            # 1. Construir prompt del sistema para el agente
            system_prompt = self._build_system_prompt(master_template, scene)
            
            # 2. Construir prompt del usuario
            user_prompt = self._build_user_prompt(user_input, scene)
            
            # 3. Llamar a Gemini
            logger.info(f"Calling Gemini to optimize prompt for scene {scene.get('scene_id')}")
            
            response = self.model.generate_content(
                f"{system_prompt}\n\n{user_prompt}",
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    top_p=0.9,
                    max_output_tokens=2048,
                )
            )
            
            # 4. Parsear respuesta
            optimized_data = self._parse_agent_response(response.text)
            
            # 5. Agregar metadata
            optimized_data["optimization_metadata"] = {
                "agent_model": self.model_name,
                "target_model": self.target_video_model,
                "timestamp": datetime.utcnow().isoformat(),
                "original_input": user_input
            }
            
            logger.info(f"Prompt optimized successfully. Confidence: {optimized_data.get('validation', {}).get('confidence_score', 0)}")
            
            return optimized_data
            
        except Exception as e:
            logger.error(f"Error in refine_prompt: {e}")
            # Fallback: retornar input original
            return {
                "optimized_action": user_input.get("action", ""),
                "optimized_emotion": user_input.get("emotion", ""),
                "optimized_dialogue": user_input.get("dialogue", ""),
                "technical_keywords": [],
                "validation": {
                    "is_coherent": True,
                    "confidence_score": 0.5,
                    "notes": f"Fallback mode - agent error: {str(e)}"
                },
                "error": str(e)
            }
    
    def _build_system_prompt(self, master_template: dict, scene: dict) -> str:
        """
        Construye el prompt del sistema que define el rol del agente
        """
        product_info = master_template.get("product", {})
        brand_guidelines = master_template.get("brand_guidelines", {})
        subject_info = master_template.get("subject", {})
        
        system_prompt = f"""Eres un ingeniero de prompts experto especializado en generación de video con IA.

TU ROL:
Optimizar prompts para el modelo {self.target_video_model}, transformando lenguaje simple del usuario en descripciones técnicas cinematográficas profesionales.

CONTEXTO DEL PROYECTO:
- Producto: {product_info.get('name', 'N/A')}
- Descripción del producto: {product_info.get('description', 'N/A')}
- Tono de marca: {brand_guidelines.get('mood', 'N/A')}
- Paleta de colores: {', '.join(brand_guidelines.get('color_palette', []))}
- Estilo de iluminación: {brand_guidelines.get('lighting_style', 'N/A')}
- Sujeto principal: {subject_info.get('description', 'N/A')}
- Modelo de video target: {self.target_video_model}

ESCENA ACTUAL:
- ID: {scene.get('scene_id')}
- Nombre: {scene.get('name', 'N/A')}
- Duración: {scene.get('duration', 8)} segundos
- Especificaciones de cámara: {scene.get('camera_specs', {})}

TAREAS QUE DEBES REALIZAR:

1. REFINAMIENTO DE ESTILO:
   - Traducir lenguaje simple a términos técnicos cinematográficos
   - Agregar especificaciones de iluminación profesional
   - Incluir detalles de composición y encuadre
   - Usar vocabulario técnico de producción de video

2. VALIDACIÓN DE COHERENCIA:
   - Verificar que acción, emoción y diálogo sean coherentes entre sí
   - Asegurar que todo esté alineado con el tono de marca
   - Detectar y reportar contradicciones
   - Asignar score de coherencia (0.0 - 1.0)

3. OPTIMIZACIÓN DE KEYWORDS:
   - Insertar keywords técnicas que mejoran el score en {self.target_video_model}
   - Agregar términos de calidad: "4K", "cinematic", "professional"
   - Incluir especificaciones técnicas relevantes
   - Mantener naturalidad del prompt

4. CONTROL DE TONO:
   - Preservar diálogos en español
   - Asegurar que el texto funcione con acento argentino
   - Mantener la emoción y tono original del usuario

KEYWORDS EFECTIVAS PARA {self.target_video_model.upper()}:
- Calidad: "4K quality", "cinematic", "professional", "high-resolution"
- Iluminación: "soft key lighting", "dramatic rim light", "golden hour", "studio lighting"
- Cámara: "shallow depth of field", "bokeh", "smooth tracking shot", "dolly movement"
- Composición: "rule of thirds", "symmetrical composition", "leading lines"
- Estilo: "luxury commercial aesthetic", "editorial style", "fashion photography"

FORMATO DE RESPUESTA:
Debes responder ÚNICAMENTE con un objeto JSON válido (sin markdown, sin backticks) con esta estructura exacta:
{{
  "optimized_action": "descripción técnica detallada de la acción con keywords cinematográficas",
  "optimized_emotion": "emoción refinada con términos precisos",
  "optimized_dialogue": "diálogo preservado en español (si existe)",
  "technical_keywords": ["keyword1", "keyword2", "keyword3"],
  "validation": {{
    "is_coherent": true/false,
    "confidence_score": 0.0-1.0,
    "notes": "explicación breve de la coherencia y optimizaciones realizadas",
    "issues": ["issue1", "issue2"] // si hay problemas
  }}
}}

IMPORTANTE:
- Responde SOLO con el JSON, sin texto adicional
- No uses markdown ni backticks
- Mantén los diálogos en español
- Sé técnico pero natural
- Prioriza coherencia sobre complejidad"""

        return system_prompt
    
    def _build_user_prompt(self, user_input: dict, scene: dict) -> str:
        """
        Construye el prompt del usuario con los datos a optimizar
        """
        action = user_input.get("action", scene.get("action_details", ""))
        emotion = user_input.get("emotion", scene.get("emotion", ""))
        dialogue = user_input.get("dialogue", "")
        
        user_prompt = f"""ENTRADA DEL USUARIO PARA OPTIMIZAR:

Acción: {action}
Emoción: {emotion}
Diálogo: {dialogue if dialogue else "N/A"}

Por favor, optimiza estos campos aplicando todas las tareas descritas en el prompt del sistema.
Recuerda responder ÚNICAMENTE con el objeto JSON, sin texto adicional."""

        return user_prompt
    
    def _parse_agent_response(self, response_text: str) -> dict:
        """
        Parsea la respuesta del agente y extrae el JSON
        
        Args:
            response_text: Texto de respuesta del agente
            
        Returns:
            dict con datos optimizados
        """
        try:
            # Limpiar respuesta (remover markdown si existe)
            cleaned_text = response_text.strip()
            
            # Remover backticks de markdown si existen
            if cleaned_text.startswith("```"):
                # Encontrar el JSON entre backticks
                start = cleaned_text.find("{")
                end = cleaned_text.rfind("}") + 1
                if start != -1 and end > start:
                    cleaned_text = cleaned_text[start:end]
            
            # Parsear JSON
            data = json.loads(cleaned_text)
            
            # Validar estructura mínima
            required_fields = ["optimized_action", "optimized_emotion", "validation"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent response as JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            raise ValueError(f"Invalid JSON response from agent: {e}")
        except Exception as e:
            logger.error(f"Error parsing agent response: {e}")
            raise
    
    def get_optimization_preview(
        self,
        original: dict,
        optimized: dict
    ) -> dict:
        """
        Genera un preview comparativo para mostrar en UI
        
        Args:
            original: Datos originales del usuario
            optimized: Datos optimizados por el agente
            
        Returns:
            dict con comparación formateada
        """
        return {
            "comparison": {
                "action": {
                    "original": original.get("action", ""),
                    "optimized": optimized.get("optimized_action", ""),
                    "improvement": len(optimized.get("technical_keywords", []))
                },
                "emotion": {
                    "original": original.get("emotion", ""),
                    "optimized": optimized.get("optimized_emotion", "")
                },
                "dialogue": {
                    "original": original.get("dialogue", ""),
                    "optimized": optimized.get("optimized_dialogue", "")
                }
            },
            "keywords_added": optimized.get("technical_keywords", []),
            "coherence_score": optimized.get("validation", {}).get("confidence_score", 0),
            "validation_notes": optimized.get("validation", {}).get("notes", ""),
            "issues": optimized.get("validation", {}).get("issues", [])
        }

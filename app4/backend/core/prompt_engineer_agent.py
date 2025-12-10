"""
Prompt Engineer Agent - Agente de Gemini para optimización de prompts
Actúa como capa de refinamiento entre entrada del usuario y generación de video

Supports both:
- Local WebAI-to-API server (cost-free, no rate limits)
- Official Google Gemini API (fallback)
- Image analysis for scene continuity
"""
from __future__ import annotations
import google.generativeai as genai
import json
import logging
import base64
from typing import Optional
from datetime import datetime
from pathlib import Path

# Import local WebAI client
from .webai_client import WebAIClient

logger = logging.getLogger(__name__)


class PromptEngineerAgent:
    """
    Agente de IA que optimiza prompts para generación de video.
    
    Responsabilidades:
    - Refinar lenguaje simple a términos técnicos cinematográficos
    - Validar coherencia entre acción, emoción y tono del producto
    - Optimizar keywords para Veo 3.1
    - Ajustar tono y acento del diálogo
    
    Supports two modes:
    - Local mode: Uses WebAI-to-API server (localhost:6969)
    - Official mode: Uses Google Gemini API directly
    """
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash-exp",
        target_video_model: str = "veo-3.1",
        use_local: bool = False,
        webai_base_url: str = "http://localhost:6969/v1"
    ):
        """
        Inicializa el agente con configuración de Gemini
        
        Args:
            api_key: API key de Google Gemini (required even for local mode as fallback)
            model_name: Modelo de Gemini a usar
            target_video_model: Modelo de video target (veo-3.1, runway, etc)
            use_local: If True, use WebAI-to-API local server
            webai_base_url: Base URL of WebAI-to-API server
        """
        self.api_key = api_key
        self.model_name = model_name
        self.target_video_model = target_video_model
        self.use_local = use_local
        self.webai_base_url = webai_base_url
        
        # Initialize clients
        if use_local:
            logger.info(f"[LOCAL] Initializing with LOCAL WebAI-to-API server: {webai_base_url}")
            self.webai_client = WebAIClient(base_url=webai_base_url)
            self.local_available = True
            self.model = None  # Don't initialize blocking official client
        else:
            logger.info(f"[CLOUD] Initializing with OFFICIAL Google Gemini API")
            self.webai_client = None
            self.local_available = False
            # Only initialize official client when NOT using local mode
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"PromptEngineerAgent initialized with model: {model_name}")

    def _encode_image_to_base64(self, image_path: str) -> str:
        """Encode an image file to base64 string"""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def _get_image_mime_type(self, image_path: str) -> str:
        """Get MIME type from image extension"""
        ext = Path(image_path).suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        return mime_types.get(ext, "image/jpeg")
    
    async def analyze_frame_for_continuity(self, image_path: str) -> dict:
        """
        Analyze a frame image to extract visual context for scene continuity.
        
        Args:
            image_path: Path to the last frame of the previous scene
            
        Returns:
            dict with visual analysis including colors, position, elements, mood
        """
        try:
            image_data = self._encode_image_to_base64(image_path)
            mime_type = self._get_image_mime_type(image_path)
            
            analysis_prompt = """Analyze this video frame and extract the following information for scene continuity:

1. **Subject Position**: Where is the main subject located in the frame? (left, center, right, foreground, background)
2. **Camera Angle**: What type of shot is this? (close-up, medium, wide, etc.)
3. **Lighting**: Describe the lighting conditions (soft, dramatic, natural, studio, etc.)
4. **Color Palette**: What are the dominant colors?
5. **Mood/Emotion**: What emotional tone does this frame convey?
6. **Key Elements**: What objects or elements are visible?
7. **Motion Direction**: If there's implied motion, in what direction?

Respond in JSON format:
{
    "subject_position": "description",
    "camera_angle": "shot type",
    "lighting": "lighting description",
    "color_palette": ["color1", "color2", "color3"],
    "mood": "emotional tone",
    "key_elements": ["element1", "element2"],
    "motion_direction": "direction or none",
    "continuity_notes": "suggestions for smooth transition to next scene"
}"""

            if self.use_local and self.webai_client:
                # Use WebAI with vision support
                response = await self.webai_client.generate_content_with_image(
                    prompt=analysis_prompt,
                    image_data=image_data,
                    mime_type=mime_type,
                    model=str(self.model_name)
                )
                response_text = response.text
            else:
                # Use official Gemini API with vision
                response = self.model.generate_content([
                    {"mime_type": mime_type, "data": image_data},
                    analysis_prompt
                ])
                response_text = response.text
            
            # Parse JSON response
            try:
                # Find JSON in response
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    analysis = json.loads(response_text[json_start:json_end])
                    logger.info("[OK] Frame analysis completed successfully")
                    return analysis
            except json.JSONDecodeError:
                pass
            
            # Return basic structure if parsing fails
            return {
                "subject_position": "unknown",
                "camera_angle": "unknown",
                "lighting": "unknown",
                "color_palette": [],
                "mood": "neutral",
                "key_elements": [],
                "motion_direction": "none",
                "continuity_notes": response_text[:500],
                "raw_analysis": response_text
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Frame analysis failed: {e}")
            return {
                "error": str(e),
                "continuity_notes": "Could not analyze frame"
            }
    
    async def refine_prompt(
        self,
        user_input: dict,
        master_template: dict,
        scene: dict,
        image_context: dict = None  # Visual analysis from image (for first scene)
    ) -> dict:
        """
        Refina y optimiza un prompt usando el agente de Gemini
        
        Args:
            user_input: Campos mutables del usuario (dialogue, action, emotion)
            master_template: Template maestro del proyecto
            scene: Datos completos de la escena
            image_context: Visual analysis from product image (optional, for first scene)
            
        Returns:
            dict con campos optimizados y metadata de optimización
        """
        try:
            # 1. Construir prompt del sistema para el agente
            system_prompt = self._build_system_prompt(master_template, scene)
            
            # 2. Construir prompt del usuario (with image context if available)
            user_prompt = self._build_user_prompt(user_input, scene, image_context)
            
            # 3. Combine prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # 4. Use local WebAI server (forced - no check)
            if self.use_local and self.webai_client and self.local_available:
                try:
                    logger.info(f"[LOCAL] Using LOCAL WebAI-to-API server for scene {scene.get('scene_id')}")
                    logger.info(f"[MODEL] Model: {self.model_name}, Base URL: {self.webai_client.base_url}")
                    
                    response = await self.webai_client.generate_content(
                        prompt=full_prompt,
                        model=str(self.model_name),  # Force pure string
                        temperature=0.7,
                        top_p=0.9,
                        max_tokens=2048
                    )
                    
                    response_text = response.text
                    logger.info("[OK] Local server response received")
                    
                except Exception as e:
                    logger.error(f"[ERROR] Local WebAI-to-API failed: {e}")
                    # Re-raise the error - don't use blocking fallback
                    raise
            else:
                # 5. Use official Gemini API
                logger.info(f"[CLOUD] Using OFFICIAL Google Gemini API for scene {scene.get('scene_id')}")
                
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.7,
                        top_p=0.9,
                        max_output_tokens=2048,
                    )
                )
                response_text = response.text
                logger.info("[OK] Official API response received")
            
            # 6. Parsear respuesta
            optimized_data = self._parse_agent_response(response_text)
            
            # 7. Agregar metadata
            optimized_data["optimization_metadata"] = {
                "agent_model": self.model_name,
                "target_model": self.target_video_model,
                "timestamp": datetime.utcnow().isoformat(),
                "original_input": user_input,
                "used_local_server": self.use_local and self.local_available
            }
            
            logger.info(f"[OK] Prompt optimized successfully. Confidence: {optimized_data.get('validation', {}).get('confidence_score', 0):.0%}")
            
            return optimized_data
            
        except Exception as e:
            logger.error(f"[ERROR] Error in refine_prompt: {e}")
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

MANEJO DE DIÁLOGOS (MUY IMPORTANTE):
Si el usuario proporcionó un diálogo:
1. DEBES incluirlo en "optimized_dialogue" EXACTAMENTE como está
2. NO traduzcas ni modifiques el diálogo
3. El diálogo debe aparecer en "optimized_action" con el formato:
   "speaks: '[diálogo exacto]' with [female/male] voice, Argentine accent"
4. Si NO hay diálogo, deja "optimized_dialogue" vacío

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
    
    def _build_user_prompt(self, user_input: dict, scene: dict, image_context: dict = None) -> str:
        """
        Construye el prompt del usuario con los datos a optimizar
        """
        action = user_input.get("action", scene.get("action_details", ""))
        emotion = user_input.get("emotion", scene.get("emotion", ""))
        dialogue = user_input.get("dialogue", "")
        voice_gender = user_input.get("voice_gender", "female")  # Default to female
        
        # Build base prompt
        user_prompt = f"""ENTRADA DEL USUARIO PARA OPTIMIZAR:

Acción: {action}
Emoción: {emotion}
Diálogo: {dialogue if dialogue else "N/A"}
Voz: {"Mujer" if voice_gender == "female" else "Hombre"} (acento argentino)"""

        # Add visual context if this is first scene with image analysis
        if image_context:
            # Define voice text for use in prompt
            voice_gender_text = "female" if voice_gender == "female" else "male"
            
            user_prompt += f"""

CONTEXTO VISUAL DE LA IMAGEN (PRODUCTO/ESCENA INICIAL):
Esta es la imagen que se usará como referencia para generar el video.
Debes combinar esta información visual con la acción/emoción/diálogo del usuario.

Análisis de la imagen:
- Posición del sujeto: {image_context.get('subject_position', 'N/A')}
- Ángulo de cámara sugerido: {image_context.get('camera_angle', 'N/A')}
- Iluminación: {image_context.get('lighting', 'N/A')}
- Colores dominantes: {', '.join(image_context.get('colors', []))}
- Mood/emoción: {image_context.get('mood', 'N/A')}
- Elementos clave: {', '.join(image_context.get('elements', []))}

IMPORTANTE - CÓMO COMBINAR IMAGEN + ACCIÓN:

1. ESTADO INICIAL (de la imagen):
   Describe cómo se ve la escena AL INICIO, exactamente como está en la imagen.
   
2. ACCIÓN DEL USUARIO (movimiento/gesto):
   Incorpora la acción específica que el usuario describió.
   Mantén los detalles exactos: qué mano usa, qué objeto toma, hacia dónde mira, etc.
   
   Ejemplos de acciones detalladas:
   - "toma el perfume negro con la mano izquierda" → mantén "mano izquierda" y "perfume negro"
   - "sonríe y lo muestra a cámara" → mantén el gesto específico
   - "lo deja con los otros perfumes y sale de cuadro" → mantén la secuencia exacta
   
3. DIÁLOGO (si existe):
   Incluye el diálogo EXACTAMENTE como está, sin cambios.
   Especifica que se dice con voz {voice_gender_text} y acento argentino.

4. DETALLES TÉCNICOS:
   Agrega keywords cinematográficas, especificaciones de cámara, iluminación profesional.

ESTRUCTURA DEL PROMPT OPTIMIZADO:
"[Descripción inicial de la imagen: personaje, productos, ambiente], 
[ACCIÓN ESPECÍFICA del usuario con todos los detalles], 
speaks: '[diálogo exacto]' with {voice_gender_text} voice, Argentine accent,
[especificaciones técnicas: cámara, iluminación, mood]"

Ejemplo completo:
"Woman in red dress standing behind five LVE perfume bottles on glossy white surface, 
reaches with her left hand and picks up the black perfume bottle, 
lifts it to eye level showing it to camera with confident smile,
speaks: 'Este es mi favorito' with female voice, Argentine accent,
medium shot, soft studio lighting from above, elegant and sophisticated mood, 
4K quality, cinematic commercial aesthetic"
"""

        user_prompt += """

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

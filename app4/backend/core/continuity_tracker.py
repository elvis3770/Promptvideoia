"""
Continuity Tracker - Mantiene consistencia visual entre escenas

Responsabilidades:
- Rastrear elementos clave (personajes, productos, ambiente)
- Validar continuidad entre escenas
- Generar sugerencias de transición
- Alertar sobre inconsistencias
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ContinuityElement:
    """Elemento rastreado para continuidad"""
    type: str  # 'character', 'product', 'environment'
    description: str
    position: str
    details: Dict[str, str]


class ContinuityTracker:
    """
    Rastrea elementos visuales entre escenas para mantener continuidad
    """
    
    def __init__(self):
        self.tracked_elements = {}
    
    def extract_elements(self, scene_analysis: Dict) -> List[ContinuityElement]:
        """
        Extrae elementos clave del análisis de una escena
        
        Args:
            scene_analysis: Análisis de Gemini de la imagen
            
        Returns:
            Lista de elementos rastreados
        """
        elements = []
        
        # Defensive check - ensure scene_analysis is a dict
        if not isinstance(scene_analysis, dict):
            logger.warning(f"scene_analysis is not a dict: {type(scene_analysis)}")
            return elements
        
        # Extract character info (only if present)
        if scene_analysis.get('subject_position'):
            elements.append(ContinuityElement(
                type='character',
                description=scene_analysis.get('subject_position', ''),
                position=scene_analysis.get('camera_angle', 'unknown'),
                details={
                    'mood': scene_analysis.get('mood', ''),
                    'lighting': scene_analysis.get('lighting', '')
                }
            ))
        
        # Extract product info (safely handle missing 'elements' key)
        scene_elements = scene_analysis.get('elements', [])
        if isinstance(scene_elements, list):
            product_elements = [e for e in scene_elements 
                              if isinstance(e, str) and any(keyword in e.lower() for keyword in 
                                    ['bottle', 'perfume', 'product', 'package', 'box', 'container'])]
            
            for product in product_elements:
                elements.append(ContinuityElement(
                    type='product',
                    description=product,
                    position='visible in frame',
                    details={
                        'colors': ', '.join(scene_analysis.get('colors', []))
                    }
                ))
        
        # Extract environment info (always add, even if minimal)
        lighting = scene_analysis.get('lighting', 'unknown')
        colors = scene_analysis.get('colors', [])
        colors_str = ', '.join(colors) if isinstance(colors, list) else ''
        
        elements.append(ContinuityElement(
            type='environment',
            description=f"Lighting: {lighting}",
            position='overall scene',
            details={
                'colors': colors_str,
                'mood': scene_analysis.get('mood', '')
            }
        ))
        
        return elements
    
    def validate_continuity(
        self, 
        previous_elements: List[ContinuityElement],
        current_elements: List[ContinuityElement]
    ) -> Dict:
        """
        Valida continuidad entre dos escenas
        
        Returns:
            Dict con warnings y sugerencias
        """
        warnings = []
        suggestions = []
        
        # Check character continuity
        prev_chars = [e for e in previous_elements if e.type == 'character']
        curr_chars = [e for e in current_elements if e.type == 'character']
        
        if prev_chars and not curr_chars:
            warnings.append({
                'severity': 'high',
                'message': 'Personaje desapareció de la escena',
                'element': 'character'
            })
            suggestions.append('Mantén el personaje visible o explica su salida')
        
        # Check product continuity
        prev_products = [e for e in previous_elements if e.type == 'product']
        curr_products = [e for e in current_elements if e.type == 'product']
        
        if prev_products and not curr_products:
            warnings.append({
                'severity': 'high',
                'message': 'Producto desapareció del frame',
                'element': 'product'
            })
            suggestions.append('El producto debe mantenerse visible para continuidad')
        
        # Check lighting consistency
        prev_env = next((e for e in previous_elements if e.type == 'environment'), None)
        curr_env = next((e for e in current_elements if e.type == 'environment'), None)
        
        if prev_env and curr_env:
            prev_lighting = prev_env.details.get('lighting', '')
            curr_lighting = curr_env.details.get('lighting', '')
            
            # Simple check - could be more sophisticated
            if prev_lighting and curr_lighting and prev_lighting != curr_lighting:
                warnings.append({
                    'severity': 'medium',
                    'message': f'Iluminación cambió: {prev_lighting} → {curr_lighting}',
                    'element': 'environment'
                })
                suggestions.append(f'Mantén iluminación consistente: {prev_lighting}')
        
        return {
            'is_valid': len([w for w in warnings if w['severity'] == 'high']) == 0,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    def generate_continuity_prompt(
        self, 
        previous_elements: List[ContinuityElement],
        user_action: str
    ) -> str:
        """
        Genera prompt de continuidad para Gemini
        
        Args:
            previous_elements: Elementos de la escena anterior
            user_action: Acción que el usuario quiere en la nueva escena
            
        Returns:
            Prompt con contexto de continuidad
        """
        prompt = "CONTINUITY CONTEXT FROM PREVIOUS SCENE:\n\n"
        
        # Character info
        chars = [e for e in previous_elements if e.type == 'character']
        if chars:
            char = chars[0]
            prompt += f"CHARACTER:\n"
            prompt += f"- Position: {char.description}\n"
            prompt += f"- Camera: {char.position}\n"
            prompt += f"- Mood: {char.details.get('mood', 'N/A')}\n\n"
        
        # Product info
        products = [e for e in previous_elements if e.type == 'product']
        if products:
            prompt += f"PRODUCT(S):\n"
            for p in products:
                prompt += f"- {p.description}\n"
            prompt += "\n"
        
        # Environment info
        env = next((e for e in previous_elements if e.type == 'environment'), None)
        if env:
            prompt += f"ENVIRONMENT:\n"
            prompt += f"- {env.description}\n"
            prompt += f"- Colors: {env.details.get('colors', 'N/A')}\n\n"
        
        prompt += "NEXT SCENE MUST MAINTAIN:\n"
        prompt += "- Same character position and appearance\n"
        prompt += "- Product(s) visible in consistent location\n"
        prompt += "- Consistent lighting and color palette\n"
        prompt += "- Smooth transition (no jarring changes)\n\n"
        
        prompt += f"USER'S DESIRED ACTION: {user_action}\n\n"
        prompt += "Optimize the prompt to maintain continuity while incorporating the user's action."
        
        return prompt

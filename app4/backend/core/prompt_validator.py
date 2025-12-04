"""
Prompt Validator - Validación de coherencia y calidad de prompts
"""
from __future__ import annotations
from typing import List, Optional
from dataclasses import dataclass
import re


@dataclass
class ValidationResult:
    """Resultado de validación de un prompt"""
    is_valid: bool
    is_coherent: bool
    confidence_score: float  # 0.0 - 1.0
    issues: List[str]
    suggestions: List[str]
    notes: str


class PromptValidator:
    """
    Valida coherencia y calidad de prompts para generación de video
    
    Funciones:
    - Validar coherencia entre acción, emoción y tono del producto
    - Detectar contradicciones
    - Verificar longitud y formato
    - Validar compatibilidad con modelo target
    """
    
    # Palabras clave por emoción
    EMOTION_KEYWORDS = {
        "alegría": ["sonrisa", "risa", "feliz", "contento", "radiante", "brillante"],
        "tristeza": ["lágrimas", "melancólico", "triste", "apagado", "oscuro"],
        "misterio": ["enigmático", "misterioso", "intrigante", "sombra", "secreto"],
        "confianza": ["determinado", "seguro", "firme", "poderoso", "fuerte"],
        "miedo": ["asustado", "nervioso", "tenso", "tembloroso"],
        "sorpresa": ["asombrado", "sorprendido", "impactado", "boquiabierto"]
    }
    
    # Tonos de producto
    PRODUCT_TONES = {
        "lujo": ["elegante", "sofisticado", "premium", "exclusivo", "refinado"],
        "juvenil": ["dinámico", "enérgico", "vibrante", "moderno", "fresco"],
        "profesional": ["serio", "formal", "corporativo", "confiable"],
        "casual": ["relajado", "informal", "cómodo", "natural"],
        "oscuro": ["misterioso", "intenso", "dramático", "profundo"]
    }
    
    def __init__(self):
        """Inicializa el validador"""
        pass
    
    def validate_scene_coherence(
        self,
        action: str,
        emotion: str,
        product_tone: str,
        dialogue: Optional[str] = None
    ) -> ValidationResult:
        """
        Valida la coherencia de una escena completa
        
        Args:
            action: Descripción de la acción
            emotion: Emoción de la escena
            product_tone: Tono del producto/marca
            dialogue: Diálogo opcional
            
        Returns:
            ValidationResult con análisis completo
        """
        issues = []
        suggestions = []
        
        # 1. Verificar contradicciones
        contradictions = self.check_contradictions(action, emotion, product_tone)
        if contradictions:
            issues.extend(contradictions)
        
        # 2. Validar longitud
        if not self.validate_prompt_length(action, max_length=500):
            issues.append("Acción demasiado larga (máximo 500 caracteres)")
            suggestions.append("Simplifica la descripción de la acción")
        
        # 3. Validar que no esté vacío
        if not action or not action.strip():
            issues.append("La acción no puede estar vacía")
        
        if not emotion or not emotion.strip():
            issues.append("La emoción no puede estar vacía")
        
        # 4. Calcular score de coherencia
        confidence_score = self._calculate_coherence_score(
            action, emotion, product_tone, len(issues)
        )
        
        # 5. Generar notas
        notes = self._generate_validation_notes(
            action, emotion, product_tone, issues, confidence_score
        )
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            is_coherent=len(contradictions) == 0,
            confidence_score=confidence_score,
            issues=issues,
            suggestions=suggestions,
            notes=notes
        )
    
    def check_contradictions(
        self,
        action: str,
        emotion: str,
        product_tone: str
    ) -> List[str]:
        """
        Detecta contradicciones entre acción, emoción y tono del producto
        
        Returns:
            Lista de contradicciones encontradas
        """
        contradictions = []
        
        action_lower = action.lower()
        emotion_lower = emotion.lower()
        tone_lower = product_tone.lower()
        
        # Detectar contradicciones emoción-acción
        if "alegr" in emotion_lower or "feliz" in emotion_lower:
            if any(word in action_lower for word in ["triste", "llora", "lágrima", "melancól"]):
                contradictions.append(
                    "Contradicción: Emoción alegre pero acción triste"
                )
        
        if "triste" in emotion_lower or "melanc" in emotion_lower:
            if any(word in action_lower for word in ["sonr", "risa", "feliz", "alegr"]):
                contradictions.append(
                    "Contradicción: Emoción triste pero acción alegre"
                )
        
        # Detectar contradicciones tono-emoción
        if "lujo" in tone_lower or "elegante" in tone_lower:
            if any(word in emotion_lower for word in ["casual", "informal", "descuidado"]):
                contradictions.append(
                    "Contradicción: Tono de lujo pero emoción casual"
                )
        
        if "oscur" in tone_lower or "misterio" in tone_lower:
            if any(word in emotion_lower for word in ["alegr", "radiante", "brillante"]):
                contradictions.append(
                    "Contradicción: Tono oscuro/misterioso pero emoción brillante"
                )
        
        return contradictions
    
    def validate_prompt_length(
        self,
        prompt: str,
        max_length: int = 500,
        min_length: int = 10
    ) -> bool:
        """
        Valida que el prompt tenga una longitud apropiada
        
        Args:
            prompt: Texto del prompt
            max_length: Longitud máxima permitida
            min_length: Longitud mínima permitida
            
        Returns:
            True si la longitud es válida
        """
        if not prompt:
            return False
        
        length = len(prompt.strip())
        return min_length <= length <= max_length
    
    def validate_model_compatibility(
        self,
        prompt: str,
        model: str = "veo-3.1"
    ) -> bool:
        """
        Valida que el prompt sea compatible con el modelo target
        
        Args:
            prompt: Texto del prompt
            model: Modelo de video (veo-3.1, runway, etc)
            
        Returns:
            True si es compatible
        """
        # Por ahora, validación básica
        # En el futuro, agregar reglas específicas por modelo
        
        if not prompt or not prompt.strip():
            return False
        
        # Veo 3.1 tiene límite de ~500 caracteres
        if model.startswith("veo"):
            return len(prompt) <= 500
        
        return True
    
    def _calculate_coherence_score(
        self,
        action: str,
        emotion: str,
        product_tone: str,
        num_issues: int
    ) -> float:
        """
        Calcula un score de coherencia basado en varios factores
        
        Returns:
            Score entre 0.0 y 1.0
        """
        base_score = 1.0
        
        # Penalizar por cada issue
        base_score -= (num_issues * 0.15)
        
        # Bonus por longitud apropiada
        if 50 <= len(action) <= 300:
            base_score += 0.05
        
        # Bonus por tener emoción específica
        if emotion and len(emotion.strip()) > 5:
            base_score += 0.05
        
        # Asegurar que esté en rango 0-1
        return max(0.0, min(1.0, base_score))
    
    def _generate_validation_notes(
        self,
        action: str,
        emotion: str,
        product_tone: str,
        issues: List[str],
        score: float
    ) -> str:
        """
        Genera notas descriptivas sobre la validación
        """
        if not issues:
            if score >= 0.9:
                return "Excelente coherencia. Todos los elementos están bien alineados."
            elif score >= 0.7:
                return "Buena coherencia. Los elementos funcionan bien juntos."
            else:
                return "Coherencia aceptable. Considera refinar algunos elementos."
        else:
            return f"Se encontraron {len(issues)} problemas que necesitan atención."

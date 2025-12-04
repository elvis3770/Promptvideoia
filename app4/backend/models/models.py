"""
Pydantic models for data validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ClipStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class ContinuityMode(str, Enum):
    INITIAL = "initial"
    LAST_FRAME_REFERENCE = "last_frame_reference"
    FIRST_LAST_FRAMES = "first_last_frames"

# Subject Model
class Subject(BaseModel):
    type: str = "person"
    name: Optional[str] = None
    description: str
    reference_image_ids: List[str] = []
    consistency_id: str
    characteristics: List[str] = []

# Product Model
class Product(BaseModel):
    name: str
    description: str
    reference_image_ids: List[str] = []
    consistency_id: str
    brand_colors: List[str] = []

# Camera Specs
class CameraSpecs(BaseModel):
    angle: str
    movement: str
    speed: str
    focal_length: Optional[str] = None

# Scene Model
class Scene(BaseModel):
    scene_id: int
    name: str
    duration: int = 8
    status: ClipStatus = ClipStatus.PENDING
    prompt_template: str
    variables: dict[str, str]
    emotion: str
    camera_specs: CameraSpecs
    action_details: str
    continuity_mode: ContinuityMode = ContinuityMode.INITIAL
    product_focus: bool = False
    clip_id: Optional[str] = None

# Brand Guidelines
class BrandGuidelines(BaseModel):
    mood: str
    color_palette: List[str]
    lighting_style: str
    music_style: Optional[str] = None

# Refinement Settings
class RefinementSettings(BaseModel):
    iterations: int = 2
    mode: str = "automatic"  # automatic, manual
    focus_areas: List[str] = []
    quality_checks: List[str] = []

# Technical Specs
class TechnicalSpecs(BaseModel):
    resolution: str = "1080p"
    aspect_ratio: str = "16:9"
    model: str = "veo-3.1-generate-preview"
    frame_rate: int = 24
    color_grading: Optional[str] = None

# Final Video
class FinalVideo(BaseModel):
    path: Optional[str] = None
    duration: Optional[float] = None
    size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None

# Project Model
class Project(BaseModel):
    project_id: str
    name: str
    status: ProjectStatus = ProjectStatus.DRAFT
    duration_target: int = 30
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    subject: Subject
    product: Optional[Product] = None
    brand_guidelines: Optional[BrandGuidelines] = None
    scenes: List[Scene]
    refinement_settings: RefinementSettings = Field(default_factory=RefinementSettings)
    technical_specs: TechnicalSpecs = Field(default_factory=TechnicalSpecs)
    final_video: Optional[FinalVideo] = None

# Clip Generation Info
class ClipGeneration(BaseModel):
    operation_name: str
    prompt: str
    model: str
    duration_seconds: int = 8
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

# Clip Continuity Info
class ClipContinuity(BaseModel):
    mode: ContinuityMode
    reference_frame_id: Optional[str] = None
    previous_clip_id: Optional[str] = None

# Clip File Info
class ClipFile(BaseModel):
    path: str
    size_bytes: int
    duration: float
    resolution: str
    frame_rate: int = 24

# Clip Metadata
class ClipMetadata(BaseModel):
    camera_movement: Optional[str] = None
    emotion: Optional[str] = None
    quality_score: Optional[float] = None

# Clip Frames
class ClipFrames(BaseModel):
    first_frame_id: Optional[str] = None
    last_frame_id: Optional[str] = None

# Clip Model
class Clip(BaseModel):
    clip_id: str
    project_id: str
    scene_id: int
    status: ClipStatus = ClipStatus.PENDING
    
    generation: Optional[ClipGeneration] = None
    continuity: Optional[ClipContinuity] = None
    file: Optional[ClipFile] = None
    frames: Optional[ClipFrames] = None
    metadata: Optional[ClipMetadata] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Asset Type
class AssetType(str, Enum):
    REFERENCE_IMAGE = "reference_image"
    EXTRACTED_FRAME = "extracted_frame"
    FINAL_VIDEO = "final_video"

# Asset File
class AssetFile(BaseModel):
    path: str
    filename: str
    size_bytes: int
    mime_type: str

# Asset Usage
class AssetUsage(BaseModel):
    used_in_scenes: List[int] = []
    purpose: Optional[str] = None

# Asset Model
class Asset(BaseModel):
    asset_id: str
    type: AssetType
    project_id: str
    file: AssetFile
    usage: Optional[AssetUsage] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

# ============================================================
# PROMPT OPTIMIZATION MODELS
# ============================================================

class PromptOptimizationConfig(BaseModel):
    """Configuración para optimización de prompts con Agente Gemini"""
    use_agent: bool = True
    model_type: str = "veo-3.1"
    accent: str = "argentino"
    technical_level: int = 3  # 1-3 (básico, intermedio, avanzado)
    validate_coherence: bool = True
    gemini_model: str = "gemini-2.0-flash-exp"

class ValidationIssue(BaseModel):
    """Problema detectado en validación"""
    type: str  # contradiction, length, format, etc
    severity: str  # low, medium, high
    message: str
    suggestion: Optional[str] = None

class PromptValidationResult(BaseModel):
    """Resultado de validación de prompt"""
    is_valid: bool
    is_coherent: bool
    confidence_score: float  # 0.0 - 1.0
    issues: List[ValidationIssue] = []
    suggestions: List[str] = []
    notes: str

class OptimizedPromptData(BaseModel):
    """Datos de un prompt optimizado por el agente"""
    optimized_action: str
    optimized_emotion: str
    optimized_dialogue: Optional[str] = None
    technical_keywords: List[str] = []
    validation: dict  # Resultado de validación del agente
    optimization_metadata: Optional[dict] = None

class PromptOptimizationResult(BaseModel):
    """Resultado completo de optimización de prompt"""
    original_prompt: str
    optimized_prompt: str
    keywords_added: List[str]
    validation_result: PromptValidationResult
    optimization_notes: str
    agent_used: bool = True
    timestamp: datetime = Field(default_factory=datetime.utcnow)


"""
Continuity Engine - Maintain visual continuity between clips
"""
import os
from typing import Optional, List
from ..utils.frame_extractor import FrameExtractor

class ContinuityEngine:
    """Manage visual continuity between video clips"""
    
    def __init__(self, frame_extractor: FrameExtractor):
        """
        Initialize continuity engine
        
        Args:
            frame_extractor: FrameExtractor instance
        """
        self.frame_extractor = frame_extractor
    
    async def prepare_continuity_references(
        self,
        previous_clip_path: str,
        reference_images: Optional[List[str]] = None,
        temp_dir: str = "./temp"
    ) -> List[str]:
        """
        Prepare reference images for next clip generation
        
        Args:
            previous_clip_path: Path to previous clip
            reference_images: Additional reference images (subject/product)
            temp_dir: Directory for temporary files
        
        Returns:
            List of reference image paths (last frame + additional refs)
        """
        os.makedirs(temp_dir, exist_ok=True)
        
        # Extract last frame from previous clip
        clip_name = os.path.splitext(os.path.basename(previous_clip_path))[0]
        last_frame_path = os.path.join(temp_dir, f"{clip_name}_last_frame.jpg")
        
        self.frame_extractor.extract_last_frame(previous_clip_path, last_frame_path)
        
        # Combine with additional references
        all_references = [last_frame_path]
        if reference_images:
            all_references.extend(reference_images)
        
        print(f"📸 Prepared {len(all_references)} reference images for continuity")
        return all_references
    
    def validate_continuity(
        self,
        clip1_path: str,
        clip2_path: str,
        temp_dir: str = "./temp"
    ) -> dict:
        """
        Validate visual continuity between two clips
        (Future: could use image similarity metrics)
        
        Args:
            clip1_path: First clip
            clip2_path: Second clip
            temp_dir: Temp directory
        
        Returns:
            Validation results
        """
        # Extract frames for comparison
        frame1_path = os.path.join(temp_dir, "clip1_last.jpg")
        frame2_path = os.path.join(temp_dir, "clip2_first.jpg")
        
        self.frame_extractor.extract_last_frame(clip1_path, frame1_path)
        self.frame_extractor.extract_first_frame(clip2_path, frame2_path)
        
        # Basic validation (file existence)
        validation = {
            'clip1_last_frame': frame1_path,
            'clip2_first_frame': frame2_path,
            'frames_extracted': os.path.exists(frame1_path) and os.path.exists(frame2_path),
            'continuity_score': 0.85  # Placeholder - could implement actual similarity check
        }
        
        return validation
    
    def cleanup_temp_frames(self, temp_dir: str = "./temp"):
        """
        Clean up temporary frame files
        
        Args:
            temp_dir: Directory to clean
        """
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                if file.endswith(('.jpg', '.png')):
                    file_path = os.path.join(temp_dir, file)
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"⚠️ Could not delete {file_path}: {e}")

"""
Veo API Client - Wrapper for Google Veo 3.1 API
"""
import os
import sys
from typing import List, Dict, Any, Optional
import asyncio

# Add parent backend directory to path to import from existing backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from helper import (
    generate_text_to_video,
    generate_image_to_video,
    generate_video_from_reference_images,
    extend_veo_video,
    get_operation_status,
    download_video_bytes
)

class VeoClient:
    """Async wrapper for Veo 3.1 API"""
    
    def __init__(self):
        """Initialize Veo client"""
        self.default_model = "veo-3.1-generate-preview"
        self.fast_model = "veo-3.1-fast-generate-preview"
    
    async def generate_text_to_video(
        self,
        prompt: str,
        duration_seconds: int = 8,
        model: Optional[str] = None,
        resolution: str = "1080p",
        aspect_ratio: str = "16:9"
    ) -> dict:
        """
        Generate video from text prompt
        
        Args:
            prompt: Text description
            duration_seconds: Video duration
            model: Model to use
            resolution: Video resolution
            aspect_ratio: Aspect ratio
        
        Returns:
            Operation info dict
        """
        model = model or self.fast_model
        
        result = await asyncio.to_thread(
            generate_text_to_video,
            prompt,
            model,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            duration_seconds=duration_seconds
        )
        
        return result
    
    async def generate_from_reference_images(
        self,
        prompt: str,
        reference_images: List[str],
        duration_seconds: int = 8,
        model: Optional[str] = None,
        resolution: str = "1080p",
        aspect_ratio: str = "16:9"
    ) -> dict:
        """
        Generate video using reference images (for continuity)
        
        Args:
            prompt: Text description
            reference_images: List of image paths
            duration_seconds: Video duration
            model: Model to use (must support reference images)
            resolution: Video resolution
            aspect_ratio: Aspect ratio
        
        Returns:
            Operation info dict
        """
        model = model or self.default_model  # Use full model for reference images
        
        # Read image files
        image_bytes_list = []
        for img_path in reference_images:
            with open(img_path, 'rb') as f:
                image_bytes_list.append(f.read())
        
        result = await asyncio.to_thread(
            generate_video_from_reference_images,
            prompt,
            image_bytes_list,
            model,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            duration_seconds=duration_seconds
        )
        
        return result
    
    async def get_status(self, operation_name: str) -> dict:
        """
        Get operation status
        
        Args:
            operation_name: Operation identifier
        
        Returns:
            Status dict
        """
        status = await asyncio.to_thread(get_operation_status, operation_name)
        return status
    
    async def download_video(self, operation_name: str) -> bytes:
        """
        Download generated video
        
        Args:
            operation_name: Operation identifier
        
        Returns:
            Video bytes
        """
        video_bytes, _ = await asyncio.to_thread(download_video_bytes, operation_name)
        return video_bytes
    
    async def wait_for_completion(
        self,
        operation_name: str,
        max_wait_seconds: int = 300,
        poll_interval: int = 10
    ) -> dict:
        """
        Wait for operation to complete
        
        Args:
            operation_name: Operation identifier
            max_wait_seconds: Maximum time to wait
            poll_interval: Seconds between status checks
        
        Returns:
            Final status dict
        
        Raises:
            TimeoutError: If operation doesn't complete in time
            Exception: If operation fails
        """
        elapsed = 0
        
        while elapsed < max_wait_seconds:
            status = await self.get_status(operation_name)
            
            state = status.get('state', 'UNKNOWN')
            
            if state == 'COMPLETED':
                print(f"✅ Operation completed: {operation_name}")
                return status
            elif state == 'FAILED':
                error = status.get('error', 'Unknown error')
                raise Exception(f"Operation failed: {error}")
            
            # Still processing
            print(f"⏳ Operation in progress... ({elapsed}s elapsed)")
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        raise TimeoutError(f"Operation {operation_name} timed out after {max_wait_seconds}s")

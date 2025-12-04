"""
Video Assembler - Assemble multiple clips into final video
"""
import subprocess
import os
from typing import List, Optional

class VideoAssembler:
    """Assemble video clips using FFmpeg"""
    
    @staticmethod
    def assemble(
        clips: List[str],
        output_path: str,
        add_transitions: bool = True,
        transition_duration: float = 0.5
    ) -> str:
        """
        Assemble multiple clips into one video
        
        Args:
            clips: List of clip paths in order
            output_path: Output video path
            add_transitions: Add crossfade transitions
            transition_duration: Duration of transitions in seconds
        
        Returns:
            Path to assembled video
        """
        if not clips:
            raise ValueError("No clips provided")
        
        if len(clips) == 1:
            # Single clip, just copy
            import shutil
            shutil.copy(clips[0], output_path)
            return output_path
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create concat file for FFmpeg
        concat_file = output_path + ".concat.txt"
        with open(concat_file, 'w') as f:
            for clip in clips:
                f.write(f"file '{os.path.abspath(clip)}'\n")
        
        try:
            if add_transitions:
                # Use xfade filter for smooth transitions
                VideoAssembler._assemble_with_transitions(
                    clips, output_path, transition_duration
                )
            else:
                # Simple concatenation
                VideoAssembler._assemble_simple(concat_file, output_path)
            
            print(f"✅ Assembled {len(clips)} clips into: {output_path}")
            return output_path
        
        finally:
            # Cleanup concat file
            if os.path.exists(concat_file):
                os.remove(concat_file)
    
    @staticmethod
    def _assemble_simple(concat_file: str, output_path: str):
        """Simple concatenation without transitions"""
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    @staticmethod
    def _assemble_with_transitions(
        clips: List[str],
        output_path: str,
        transition_duration: float
    ):
        """
        Assemble with crossfade transitions
        Note: This is a simplified version. For production, might need more complex filter
        """
        # For now, use simple concat with re-encoding for quality
        # Full xfade implementation would require complex filter graphs
        
        concat_file = output_path + ".concat.txt"
        with open(concat_file, 'w') as f:
            for clip in clips:
                f.write(f"file '{os.path.abspath(clip)}'\n")
        
        try:
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '18',  # High quality
                '-c:a', 'aac',
                '-b:a', '192k',
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
        finally:
            if os.path.exists(concat_file):
                os.remove(concat_file)
    
    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """
        Get video information
        
        Args:
            video_path: Path to video
        
        Returns:
            Dict with duration, size, etc.
        """
        # Get duration
        cmd_duration = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        
        result = subprocess.run(cmd_duration, capture_output=True, text=True)
        duration = float(result.stdout.strip()) if result.stdout.strip() else 0
        
        # Get file size
        size_bytes = os.path.getsize(video_path)
        
        return {
            'path': video_path,
            'duration': duration,
            'size_bytes': size_bytes
        }

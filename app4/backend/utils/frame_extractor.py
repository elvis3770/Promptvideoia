"""
Frame Extractor - Utility for extracting frames from videos using FFmpeg
"""
import subprocess
import os
from typing import Optional

class FrameExtractor:
    """Extract frames from video files using FFmpeg"""
    
    @staticmethod
    def extract_last_frame(video_path: str, output_path: str) -> str:
        """
        Extract the last frame of a video
        
        Args:
            video_path: Path to input video
            output_path: Path for output image
            
        Returns:
            Path to extracted frame
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        cmd = [
            'ffmpeg',
            '-sseof', '-1',  # Seek to end of file minus 1 second
            '-i', video_path,
            '-update', '1',
            '-q:v', '1',  # Maximum quality
            '-y',  # Overwrite output
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Extracted last frame: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg error extracting last frame: {e.stderr.decode()}")
    
    @staticmethod
    def extract_first_frame(video_path: str, output_path: str) -> str:
        """
        Extract the first frame of a video
        
        Args:
            video_path: Path to input video
            output_path: Path for output image
            
        Returns:
            Path to extracted frame
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vframes', '1',
            '-q:v', '1',  # Maximum quality
            '-y',  # Overwrite output
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Extracted first frame: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg error extracting first frame: {e.stderr.decode()}")
    
    @staticmethod
    def extract_frame_at_time(video_path: str, output_path: str, time_seconds: float) -> str:
        """
        Extract a frame at specific time
        
        Args:
            video_path: Path to input video
            output_path: Path for output image
            time_seconds: Time in seconds
            
        Returns:
            Path to extracted frame
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
        
        cmd = [
            'ffmpeg',
            '-ss', str(time_seconds),
            '-i', video_path,
            '-vframes', '1',
            '-q:v', '1',
            '-y',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Extracted frame at {time_seconds}s: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg error extracting frame: {e.stderr.decode()}")
    
    @staticmethod
    def get_video_duration(video_path: str) -> float:
        """
        Get video duration in seconds
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds
        """
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True)
            duration = float(result.stdout.decode().strip())
            return duration
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFprobe error getting duration: {e.stderr.decode()}")

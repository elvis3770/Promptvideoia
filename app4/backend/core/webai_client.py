"""
WebAI Client - OpenAI-compatible client for WebAI-to-API local server

This client allows using a local WebAI-to-API server (running on localhost:6969)
instead of the official Google Gemini API, saving costs and avoiding rate limits.

FIXED: Uses httpx.AsyncClient for proper async compatibility with FastAPI
"""
import httpx
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class WebAIResponse:
    """Response wrapper for Gemini-compatible response format"""
    
    def __init__(self, text: str, raw_response: Dict = None, model: str = None):
        self.text = text
        self.raw_response = raw_response or {}
        self.model = model
        self.created_at = datetime.now()
    
    def __repr__(self):
        return f"WebAIResponse(text='{self.text[:50]}...', model='{self.model}')"


class WebAIClient:
    """
    Async HTTP client for WebAI-to-API server
    
    Compatible with OpenAI Chat Completions API format
    Uses httpx.AsyncClient for proper FastAPI async compatibility
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:6969/v1",
        api_key: str = "sk-test123",
        timeout: int = 180  # Increased to 3 minutes for Gemini
    ):
        """
        Initialize WebAI client
        
        Args:
            base_url: Base URL of WebAI-to-API server
            api_key: API key (not required for local server, but kept for compatibility)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = float(timeout)
        
        logger.info(f"WebAIClient initialized with base_url: {self.base_url}")
    
    async def check_connection(self) -> bool:
        """
        Check if WebAI-to-API server is reachable
        
        Returns:
            True if server is reachable, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try health endpoint first
                response = await client.get(f"{self.base_url.replace('/v1', '')}/health")
                if response.status_code == 200:
                    logger.info("[OK] WebAI-to-API server is reachable")
                    return True
                    
                # Fallback: try models endpoint
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                if response.status_code == 200:
                    logger.info("[OK] WebAI-to-API server is reachable (via /models)")
                    return True
                    
            logger.warning(f"[WARN] WebAI-to-API server returned status {response.status_code}")
            return False
            
        except httpx.ConnectError as e:
            logger.warning(f"[WARN] Cannot reach WebAI-to-API server: {e}")
            return False
        except Exception as e:
            logger.error(f"[ERROR] Error checking WebAI-to-API connection: {e}")
            return False
    
    async def generate_content(
        self,
        prompt: str,
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 2048
    ) -> 'WebAIResponse':
        """
        Generate content using WebAI-to-API server
        
        Args:
            prompt: The prompt to send
            model: Model name (gemini-2.0-flash-exp, gemini-1.5-pro, etc.)
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate
            
        Returns:
            WebAIResponse object with generated text
            
        Raises:
            httpx.HTTPError: If request fails
            ValueError: If response is invalid
        """
        try:
            # Build OpenAI-compatible request
            request_data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"[API] Calling WebAI-to-API: {self.base_url}/chat/completions")
            logger.debug(f"Request: model={model}, temp={temperature}, max_tokens={max_tokens}")
            
            # Use httpx.AsyncClient for proper async behavior in FastAPI
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=request_data,
                    headers=headers
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"[ERROR] WebAI-to-API error {response.status_code}: {error_text}")
                    raise httpx.HTTPStatusError(
                        f"WebAI-to-API returned status {response.status_code}: {error_text}",
                        request=response.request,
                        response=response
                    )
                
                response_data = response.json()
                
                # Extract generated text
                try:
                    generated_text = response_data["choices"][0]["message"]["content"]
                except (KeyError, IndexError) as e:
                    logger.error(f"[ERROR] Invalid response format: {response_data}")
                    raise ValueError(f"Invalid response format from WebAI-to-API: {e}")
                
                logger.info(f"[OK] WebAI-to-API response received ({len(generated_text)} chars)")
                
                # Return Gemini-compatible response object
                return WebAIResponse(
                    text=generated_text,
                    raw_response=response_data,
                    model=model
                )
                    
        except httpx.HTTPError as e:
            logger.error(f"[ERROR] WebAI-to-API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error in generate_content: {e}")
            raise
    
    async def generate_content_with_image(
        self,
        prompt: str,
        image_data: str,
        mime_type: str = "image/jpeg",
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> 'WebAIResponse':
        """
        Generate content with image input for vision analysis.
        
        Args:
            prompt: The text prompt
            image_data: Base64 encoded image data
            mime_type: MIME type of the image (image/jpeg, image/png, etc.)
            model: Model name (must support vision)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            WebAIResponse object with analysis text
        """
        try:
            # Build OpenAI-compatible multimodal request
            request_data = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"[API] Calling WebAI-to-API with image: {self.base_url}/chat/completions")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=request_data,
                    headers=headers
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"[ERROR] WebAI-to-API vision error {response.status_code}: {error_text}")
                    raise httpx.HTTPStatusError(
                        f"WebAI-to-API returned status {response.status_code}: {error_text}",
                        request=response.request,
                        response=response
                    )
                
                response_data = response.json()
                
                try:
                    generated_text = response_data["choices"][0]["message"]["content"]
                except (KeyError, IndexError) as e:
                    logger.error(f"[ERROR] Invalid vision response format: {response_data}")
                    raise ValueError(f"Invalid response format from WebAI-to-API: {e}")
                
                logger.info(f"[OK] WebAI-to-API vision response received ({len(generated_text)} chars)")
                
                return WebAIResponse(
                    text=generated_text,
                    raw_response=response_data,
                    model=model
                )
                    
        except httpx.HTTPError as e:
            logger.error(f"[ERROR] WebAI-to-API vision request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error in generate_content_with_image: {e}")
            raise


# Convenience functions for quick access
async def quick_generate(prompt: str, model: str = "gemini-3.0-pro") -> str:
    """Quick generation without creating a client instance"""
    client = WebAIClient()
    response = await client.generate_content(prompt=prompt, model=model)
    return response.text

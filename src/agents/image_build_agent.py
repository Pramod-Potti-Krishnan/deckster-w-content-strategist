"""
Image Build Agent - Dedicated Image Generation Service
=====================================================

This module handles all image generation using Google's Imagen 3/4 API.
Extracted from Content Agent V6 to create a standalone image service.

Features:
- Imagen 3/4 generation
- Background removal for icons and symbols
- Base64 encoding
- Transparent PNG support

Author: AI Assistant
Date: 2024
Version: 1.0
"""

import os
import base64
import logging
from io import BytesIO
from typing import Dict, Any, Optional

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field

# Import google.genai for Imagen 3
try:
    from google import genai as google_genai
    from google.genai import types as genai_types
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("google-genai not installed. Imagen 3 generation will not be available.")

# Import PIL for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Pillow not installed. Image processing features will not be available.")

# Import rembg for background removal
try:
    from rembg import remove as rembg_remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("rembg not installed. Advanced background removal will not be available.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# IMAGE CONTENT MODEL (from Content Agent V6)
# ============================================================================

class ImageContentV4(BaseModel):
    """Enhanced image output with Imagen 3 support"""
    archetype: str  # From IMAGE_PLAYBOOK
    primary_subject: str
    art_direction: Dict[str, str]
    mood_keywords: list[str]
    composition_notes: str
    
    # New fields for Imagen 3
    imagen_prompt: str = Field(
        default="",
        description="Optimized prompt for Imagen 3 generation"
    )
    imagen_negative_prompt: Optional[str] = Field(
        default=None,
        description="What to avoid in the generated image"
    )
    imagen_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "aspectRatio": "16:9",  # Default aspect ratio
            "model": "imagen-3.0-generate-002",
            "safety_settings": "block_only_high",
            "person_generation": "allow_adult"
        },
        description="Configuration for Imagen 3 API"
    )
    generated_image_url: Optional[str] = Field(
        default=None,
        description="URL of generated image (if available)"
    )
    generated_image_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded generated image"
    )
    
    # Transparent version fields
    transparent_image_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded transparent PNG (background removed)"
    )
    has_transparent_version: bool = Field(
        default=False,
        description="Whether a transparent version was generated"
    )


# ============================================================================
# IMAGE GENERATION FUNCTIONS (from Content Agent V6)
# ============================================================================

def remove_white_background(image_bytes: bytes, threshold: int = 240) -> bytes:
    """
    Remove white background from image using color threshold.
    Perfect for clean icons and illustrations with white backgrounds.
    
    Args:
        image_bytes: Raw image bytes
        threshold: RGB threshold for white detection (default 240)
    
    Returns:
        Bytes of transparent PNG
    """
    if not PIL_AVAILABLE:
        logger.warning("PIL not available, cannot remove background")
        return image_bytes
    
    try:
        # Open image
        img = Image.open(BytesIO(image_bytes))
        
        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Get pixel data
        data = img.getdata()
        
        # Create new data with transparency
        new_data = []
        for item in data:
            # Check if pixel is white-ish
            if item[0] > threshold and item[1] > threshold and item[2] > threshold:
                # Make it transparent
                new_data.append((255, 255, 255, 0))
            else:
                # Keep original
                new_data.append(item)
        
        # Update image
        img.putdata(new_data)
        
        # Save to bytes
        output = BytesIO()
        img.save(output, format='PNG')
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Simple background removal failed: {e}")
        return image_bytes


def remove_background_advanced(image_bytes: bytes) -> bytes:
    """
    Advanced background removal using rembg.
    Works for complex backgrounds and photographs.
    
    Args:
        image_bytes: Raw image bytes
    
    Returns:
        Bytes of transparent PNG
    """
    if not REMBG_AVAILABLE:
        logger.warning("rembg not available, falling back to simple removal")
        return remove_white_background(image_bytes)
    
    try:
        # Use rembg for advanced background removal
        output_bytes = rembg_remove(image_bytes)
        return output_bytes
    except Exception as e:
        logger.error(f"Advanced background removal failed: {e}")
        # Fallback to simple method
        return remove_white_background(image_bytes)


def should_remove_background(archetype: str) -> bool:
    """
    Determine if background should be removed based on image archetype.
    
    Args:
        archetype: The image archetype (e.g., 'minimalist_vector_art')
    
    Returns:
        True if background should be removed
    """
    # Archetypes that benefit from background removal
    bg_removal_archetypes = {
        'minimalist_vector_art',  # Icons and spot illustrations
        'symbolic_representation',  # Simple symbolic images
        # Can add more archetypes as needed
    }
    
    return archetype in bg_removal_archetypes


class ImageBuildAgent:
    """Agent for building images using Imagen 3."""
    
    async def generate_image_with_imagen3(
        self,
        image_spec: ImageContentV4
    ) -> ImageContentV4:
        """Generate image and return updated spec."""
        result = await _generate_image_with_imagen3_impl(image_spec)
        if result.get("success"):
            image_spec.generated_image_base64 = result.get("base64")
            image_spec.generated_image_url = result.get("image_url")
        return image_spec


async def _generate_image_with_imagen3_impl(
    image_spec: ImageContentV4
) -> Dict[str, Any]:
    """Internal implementation."""
    return await generate_image_with_imagen3(image_spec)


async def generate_image_with_imagen3(
    image_spec: ImageContentV4
) -> Dict[str, Any]:
    """
    Call Google's imagen-3.0-generate-002 API using google.genai SDK.
    
    Returns:
        Dictionary with image data and metadata
    """
    try:
        # Check if google.genai is available
        if not GOOGLE_GENAI_AVAILABLE:
            logger.error("google-genai not installed. Run: pip install google-genai")
            return {"success": False, "error": "google-genai not installed"}
        
        # Check for API key
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY not found in environment")
            return {"success": False, "error": "GOOGLE_API_KEY or GEMINI_API_KEY not configured"}
        
        logger.info("Using google.genai for Imagen 3 generation")
        
        try:
            # Initialize client
            client = google_genai.Client(api_key=api_key)
            
            # Get aspect ratio from config
            aspect_ratio = image_spec.imagen_config.get("aspectRatio", "16:9")
            
            # Generate image
            logger.info(f"Generating image with prompt: {image_spec.imagen_prompt[:100]}...")
            
            # Use the latest Imagen model
            response = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=image_spec.imagen_prompt,
                config=genai_types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=aspect_ratio,
                )
            )
            
            # Check for generated images
            if hasattr(response, 'generated_images') and response.generated_images:
                logger.info(f"Successfully generated {len(response.generated_images)} image(s)")
                
                # Extract first image
                generated_image = response.generated_images[0]
                
                if hasattr(generated_image, 'image'):
                    image_obj = generated_image.image
                    
                    # Get image bytes
                    if hasattr(image_obj, 'image_bytes'):
                        image_bytes = image_obj.image_bytes
                        logger.info(f"Image bytes extracted: {len(image_bytes)} bytes")
                        
                        # Convert to base64
                        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        
                        result = {
                            "success": True,
                            "base64": img_base64,
                            "metadata": {
                                "model": "imagen-3.0-generate-002",
                                "aspect_ratio": aspect_ratio,
                                "prompt_used": image_spec.imagen_prompt
                            }
                        }
                        
                        # Check if background removal should be applied
                        if should_remove_background(image_spec.archetype):
                            logger.info(f"Applying background removal for archetype: {image_spec.archetype}")
                            try:
                                # For minimalist vector art, use simple white removal
                                if image_spec.archetype == 'minimalist_vector_art':
                                    transparent_bytes = remove_white_background(image_bytes)
                                else:
                                    # For other archetypes, use advanced removal
                                    transparent_bytes = remove_background_advanced(image_bytes)
                                
                                # Convert transparent version to base64
                                transparent_base64 = base64.b64encode(transparent_bytes).decode('utf-8')
                                result["transparent_base64"] = transparent_base64
                                result["has_transparent"] = True
                                logger.info("Background removal successful")
                            except Exception as e:
                                logger.error(f"Background removal failed: {e}")
                                result["has_transparent"] = False
                        
                        return result
                    else:
                        logger.error("No image_bytes attribute found")
                        return {"success": False, "error": "Unable to extract image bytes"}
                else:
                    logger.error("No image attribute found in generated_image")
                    return {"success": False, "error": "No image data in response"}
            else:
                logger.warning("No generated_images in response")
                return {"success": False, "error": "No images generated"}
                
        except Exception as e:
            logger.error(f"Imagen 3 generation failed: {e}")
            
            # Try Imagen 4 if Imagen 3 fails
            if "imagen-3" in str(e).lower() or "not found" in str(e).lower():
                logger.info("Trying Imagen 4 instead...")
                try:
                    response = client.models.generate_images(
                        model='imagen-4.0-generate-preview-06-06',
                        prompt=image_spec.imagen_prompt,
                        config=genai_types.GenerateImagesConfig(
                            number_of_images=1,
                        )
                    )
                    
                    if hasattr(response, 'generated_images') and response.generated_images:
                        generated_image = response.generated_images[0]
                        if hasattr(generated_image.image, 'image_bytes'):
                            image_bytes = generated_image.image.image_bytes
                            img_base64 = base64.b64encode(image_bytes).decode('utf-8')
                            
                            result = {
                                "success": True,
                                "base64": img_base64,
                                "metadata": {
                                    "model": "imagen-4.0-generate-preview",
                                    "aspect_ratio": "default",
                                    "prompt_used": image_spec.imagen_prompt
                                }
                            }
                            
                            # Apply background removal for Imagen 4 as well
                            if should_remove_background(image_spec.archetype):
                                logger.info(f"Applying background removal for archetype: {image_spec.archetype}")
                                try:
                                    if image_spec.archetype == 'minimalist_vector_art':
                                        transparent_bytes = remove_white_background(image_bytes)
                                    else:
                                        transparent_bytes = remove_background_advanced(image_bytes)
                                    
                                    transparent_base64 = base64.b64encode(transparent_bytes).decode('utf-8')
                                    result["transparent_base64"] = transparent_base64
                                    result["has_transparent"] = True
                                    logger.info("Background removal successful")
                                except Exception as e:
                                    logger.error(f"Background removal failed: {e}")
                                    result["has_transparent"] = False
                            
                            return result
                    
                    return {"success": False, "error": "Imagen 4 also failed"}
                    
                except Exception as e2:
                    logger.error(f"Imagen 4 fallback failed: {e2}")
                    return {"success": False, "error": f"Both Imagen 3 and 4 failed: {str(e)}"}
            
            return {"success": False, "error": str(e)}
            
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# PUBLIC INTERFACE
# ============================================================================

def convert_visual_spec_to_image_content(visual_spec) -> ImageContentV4:
    """
    Convert a VisualSpec object to ImageContentV4 for image generation.
    
    Args:
        visual_spec: VisualSpec object from ContentAgentV7
        
    Returns:
        ImageContentV4 object ready for image generation
    """
    # Extract image prompt from style notes or description
    style_notes = getattr(visual_spec, 'style_notes', {})
    
    # Build the image prompt from available information
    imagen_prompt = visual_spec.description
    
    # Add mood keywords if available
    mood_keywords = style_notes.get('mood_keywords', [])
    if not mood_keywords and 'archetype' in style_notes:
        # Derive mood from archetype
        archetype_moods = {
            'spot_illustration': ['clean', 'modern', 'focused'],
            'conceptual_metaphor': ['abstract', 'symbolic', 'thoughtful'],
            'data_visualization': ['precise', 'professional', 'clear'],
            'minimalist_vector_art': ['simple', 'clean', 'elegant']
        }
        mood_keywords = archetype_moods.get(style_notes['archetype'], ['professional', 'clear'])
    
    # Determine aspect ratio based on placement
    placement = getattr(visual_spec, 'placement_guidance', 'primary')
    aspect_ratio = "16:9" if placement == 'primary' else "1:1"
    
    # Create ImageContentV4 object
    return ImageContentV4(
        archetype=style_notes.get('archetype', 'spot_illustration'),
        primary_subject=visual_spec.description,
        art_direction=style_notes.get('art_direction', {
            'style': 'modern',
            'color_scheme': 'professional'
        }),
        mood_keywords=mood_keywords,
        composition_notes=style_notes.get('composition', 'balanced composition'),
        imagen_prompt=imagen_prompt,
        imagen_negative_prompt="blurry, low quality, distorted, text, watermark",
        imagen_config={
            "aspectRatio": aspect_ratio,
            "model": "imagen-3.0-generate-002",
            "safety_settings": "block_only_high",
            "person_generation": "allow_adult"
        }
    )


async def generate_image(image_spec) -> Dict[str, Any]:
    """
    Main entry point for image generation.
    Handles both ImageContentV4 and VisualSpec inputs.
    
    Args:
        image_spec: Either ImageContentV4 or VisualSpec object
        
    Returns:
        Dictionary with:
        - success: bool
        - base64: Base64 encoded image (if successful)
        - image_base64: Alias for base64 (for compatibility)
        - transparent_base64: Base64 encoded transparent version (if applicable)
        - metadata: Generation metadata
        - error: Error message (if failed)
    """
    # Check if we need to convert from VisualSpec
    if not isinstance(image_spec, ImageContentV4):
        # Check if this is a VisualSpec (has visual_type attribute)
        if hasattr(image_spec, 'visual_type'):
            # Only process image types, not charts/diagrams/tables
            if image_spec.visual_type != 'image':
                return {
                    "success": False,
                    "error": f"Visual type '{image_spec.visual_type}' is not an image"
                }
            # Convert VisualSpec to ImageContentV4
            image_spec = convert_visual_spec_to_image_content(image_spec)
    
    result = await generate_image_with_imagen3(image_spec)
    
    # Add image_base64 alias for compatibility
    if result.get('success') and 'base64' in result:
        result['image_base64'] = result['base64']
    
    return result
#!/usr/bin/env python3
"""
Test Imagen using google.genai API (simplified approach)
"""
import os
import base64
from PIL import Image
from io import BytesIO

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import the new google.genai module
from google import genai
from google.genai import types

def test_imagen_genai():
    """Test Imagen via google.genai API"""
    
    print("\n=== Testing Imagen via google.genai API ===\n")
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return False
    
    print("✓ API key found")
    
    try:
        # Initialize client with API key
        print("\nInitializing genai client...")
        client = genai.Client(api_key=api_key)
        print("✓ Client initialized")
        
        # Try generating an image
        print("\nGenerating test image...")
        prompt = "A simple blue circle on white background, minimalist design"
        
        # Use the latest Imagen model
        response = client.models.generate_images(
            model='imagen-3.0-generate-002',  # Try Imagen 3 first
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
            )
        )
        
        print(f"✅ Response received!")
        print(f"Response type: {type(response)}")
        
        # Process the generated images
        if hasattr(response, 'generated_images') and response.generated_images:
            print(f"\n✅ Generated {len(response.generated_images)} image(s)")
            
            for i, generated_image in enumerate(response.generated_images):
                print(f"\nProcessing image {i+1}...")
                
                # Check if image data is available
                if hasattr(generated_image, 'image'):
                    # Get image data
                    image_data = generated_image.image
                    
                    # If it's already a PIL Image, save it
                    if isinstance(image_data, Image.Image):
                        image_data.save(f"test_imagen_genai_{i+1}.png")
                        print(f"✓ Saved as test_imagen_genai_{i+1}.png")
                        
                        # Also get base64
                        buffer = BytesIO()
                        image_data.save(buffer, format="PNG")
                        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        print(f"✓ Base64 length: {len(img_base64)} chars")
                    
                    # If it's bytes, convert to image
                    elif isinstance(image_data, bytes):
                        img = Image.open(BytesIO(image_data))
                        img.save(f"test_imagen_genai_{i+1}.png")
                        print(f"✓ Saved as test_imagen_genai_{i+1}.png")
                        
                        # Get base64
                        img_base64 = base64.b64encode(image_data).decode('utf-8')
                        print(f"✓ Base64 length: {len(img_base64)} chars")
                    
                    else:
                        print(f"? Unknown image data type: {type(image_data)}")
                        # Try different attributes
                        attrs = [attr for attr in dir(image_data) if not attr.startswith('__')]
                        print(f"  Available attributes: {attrs}")
                        
                        # Try common attribute names
                        if hasattr(image_data, 'data'):
                            print("  Found 'data' attribute")
                            data = image_data.data
                            if isinstance(data, bytes):
                                img = Image.open(BytesIO(data))
                                img.save(f"test_imagen_genai_{i+1}.png")
                                print(f"✓ Saved as test_imagen_genai_{i+1}.png")
                                
                                # Get base64
                                img_base64 = base64.b64encode(data).decode('utf-8')
                                print(f"✓ Base64 length: {len(img_base64)} chars")
                        
                        # Try to save directly if it has a save method
                        elif hasattr(image_data, 'save'):
                            print("  Found 'save' method")
                            image_data.save(f"test_imagen_genai_{i+1}.png")
                            print(f"✓ Saved as test_imagen_genai_{i+1}.png")
                            
                        # Try show method to display
                        elif hasattr(image_data, 'show'):
                            print("  Found 'show' method")
                            # Convert to PIL Image if possible
                            if hasattr(image_data, 'pil'):
                                pil_img = image_data.pil()
                                pil_img.save(f"test_imagen_genai_{i+1}.png")
                                print(f"✓ Saved as test_imagen_genai_{i+1}.png")
            
            return True
        else:
            print("\n❌ No generated_images in response")
            print(f"Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        
        # Try with Imagen 4 if Imagen 3 fails
        if "imagen-3" in str(e).lower():
            print("\nTrying Imagen 4 instead...")
            try:
                response = client.models.generate_images(
                    model='imagen-4.0-generate-preview-06-06',
                    prompt=prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                    )
                )
                print("✅ Imagen 4 worked!")
                return True
            except Exception as e2:
                print(f"❌ Imagen 4 also failed: {e2}")
        
        return False

def list_available_models():
    """List all available models"""
    print("\n=== Listing Available Models ===\n")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found")
        return
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Try to list models
        print("Attempting to list models...")
        if hasattr(client.models, 'list'):
            models = client.models.list()
            for model in models:
                print(f"  - {model}")
        else:
            print("Note: models.list() not available")
            
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    # First list available models
    list_available_models()
    
    # Then test image generation
    success = test_imagen_genai()
    
    if success:
        print("\n✅ Imagen test successful!")
    else:
        print("\n❌ Imagen test failed")
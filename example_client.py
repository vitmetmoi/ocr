"""
Example client script demonstrating how to use the Vietnamese OCR API
"""
import requests
import base64
from pathlib import Path
import json

# API configuration
API_URL = "http://localhost:8000"  # Change this if using ngrok or different host

def example_1_file_upload(image_path: str):
    """
    Example 1: Upload image file directly
    """
    print("\n" + "="*60)
    print("Example 1: File Upload")
    print("="*60)
    
    url = f"{API_URL}/ocr"
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Found {result['total_boxes']} text regions")
        
        for i, item in enumerate(result['results'], 1):
            print(f"\n{i}. {item['text']}")
            print(f"   Coordinates: {item['coordinates']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def example_2_base64(image_path: str):
    """
    Example 2: Send base64 encoded image
    """
    print("\n" + "="*60)
    print("Example 2: Base64 Encoding")
    print("="*60)
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    url = f"{API_URL}/ocr/base64"
    response = requests.post(url, json={"image_base64": image_base64})
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Found {result['total_boxes']} text regions")
        
        # Extract all text
        all_text = [item['text'] for item in result['results']]
        print(f"\nAll detected text:")
        print("\n".join(all_text))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def example_3_batch_processing(image_paths: list):
    """
    Example 3: Process multiple images
    """
    print("\n" + "="*60)
    print("Example 3: Batch Processing")
    print("="*60)
    
    results = []
    
    for image_path in image_paths:
        print(f"\nProcessing: {image_path}")
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_URL}/ocr", files=files)
        
        if response.status_code == 200:
            result = response.json()
            results.append({
                'image': image_path,
                'text_count': result['total_boxes'],
                'texts': [item['text'] for item in result['results']]
            })
            print(f"  ✅ Found {result['total_boxes']} text regions")
        else:
            print(f"  ❌ Error: {response.status_code}")
    
    # Save batch results
    with open('batch_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Batch results saved to: batch_results.json")

def example_4_error_handling(image_path: str):
    """
    Example 4: Proper error handling
    """
    print("\n" + "="*60)
    print("Example 4: Error Handling")
    print("="*60)
    
    try:
        # Check if API is healthy
        health_response = requests.get(f"{API_URL}/health", timeout=5)
        
        if health_response.status_code != 200:
            print("❌ API is not healthy")
            return
        
        health_data = health_response.json()
        if not all(health_data.get('models_loaded', {}).values()):
            print("❌ Models are not fully loaded")
            return
        
        print("✅ API is healthy and ready")
        
        # Process image
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_URL}/ocr", files=files, timeout=30)
        
        response.raise_for_status()  # Raise exception for bad status codes
        
        result = response.json()
        
        if result['success']:
            print(f"✅ Successfully processed image")
            print(f"   Found {result['total_boxes']} text regions")
        else:
            print(f"⚠️ Processing completed but with issues: {result['message']}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is it running?")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
    except FileNotFoundError:
        print(f"❌ Image file not found: {image_path}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """
    Main function to run all examples
    """
    # Check if sample images exist
    sample_dir = Path("samples")
    if not sample_dir.exists():
        print("❌ 'samples' directory not found")
        print("Please provide a valid image path")
        return
    
    # Get first available sample image
    sample_images = list(sample_dir.glob("*.jpg")) + list(sample_dir.glob("*.png"))
    
    if not sample_images:
        print("❌ No sample images found in 'samples' directory")
        return
    
    test_image = str(sample_images[0])
    print(f"Using test image: {test_image}")
    
    # Run examples
    example_1_file_upload(test_image)
    example_2_base64(test_image)
    
    # Batch processing with multiple images (if available)
    if len(sample_images) > 1:
        example_3_batch_processing([str(img) for img in sample_images[:3]])
    
    example_4_error_handling(test_image)
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

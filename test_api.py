"""
Test script for the Vietnamese OCR API
"""
import sys
import requests
import json
from pathlib import Path

def test_ocr_api(image_path: str, api_url: str = "http://localhost:8000"):
    """
    Test the OCR API with an image file
    
    Args:
        image_path: Path to the image file
        api_url: Base URL of the API (default: http://localhost:8000)
    """
    # Check if image exists
    if not Path(image_path).exists():
        print(f"❌ Error: Image file not found: {image_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"Testing Vietnamese OCR API")
    print(f"{'='*60}\n")
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{api_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Models loaded: {health_data.get('models_loaded')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        print(f"   Make sure the API is running at {api_url}")
        return
    
    # Test OCR endpoint
    print(f"\n2. Testing OCR endpoint with image: {image_path}")
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{api_url}/ocr", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ OCR processing successful")
            print(f"\n{'='*60}")
            print(f"Results:")
            print(f"{'='*60}")
            print(f"Total text regions found: {result['total_boxes']}")
            print(f"\nDetected text:")
            print(f"{'-'*60}")
            
            for i, box_result in enumerate(result['results'], 1):
                coords = box_result['coordinates']
                text = box_result['text']
                print(f"{i}. Text: {text}")
                print(f"   Coordinates: {coords}")
                print()
            
            # Save results to file
            output_file = Path(image_path).stem + "_ocr_result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Results saved to: {output_file}")
            
        else:
            print(f"❌ OCR processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during OCR processing: {e}")
    
    print(f"\n{'='*60}\n")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <image_path> [api_url]")
        print("\nExample:")
        print("  python test_api.py samples/1.jpg")
        print("  python test_api.py samples/1.jpg http://localhost:8000")
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    test_ocr_api(image_path, api_url)

if __name__ == "__main__":
    main()

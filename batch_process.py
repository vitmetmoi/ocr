"""
Batch OCR Processing Script
Process multiple images and save results to a CSV file
"""
import os
import sys
import csv
import requests
from pathlib import Path
from datetime import datetime
import json

def process_batch(input_dir: str, output_file: str = None, api_url: str = "http://localhost:8000"):
    """
    Process all images in a directory and save results to CSV
    
    Args:
        input_dir: Directory containing images
        output_file: Output CSV file path (optional)
        api_url: API base URL
    """
    # Check if directory exists
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        print(f"❌ Error: Directory not found: {input_dir}")
        return
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_path.glob(f'*{ext}'))
        image_files.extend(input_path.glob(f'*{ext.upper()}'))
    
    if not image_files:
        print(f"❌ No image files found in: {input_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"Batch OCR Processing")
    print(f"{'='*60}")
    print(f"Input directory: {input_dir}")
    print(f"Total images: {len(image_files)}")
    
    # Check API health
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ API is not healthy")
            return
        print(f"✅ API is ready")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    # Set output file
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"ocr_results_{timestamp}.csv"
    
    # Process images
    results = []
    successful = 0
    failed = 0
    
    print(f"\nProcessing images...")
    print(f"{'-'*60}")
    
    for i, image_path in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] Processing: {image_path.name}...", end=' ')
        
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{api_url}/ocr", files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract all text
                all_text = ' '.join([item['text'] for item in result['results']])
                
                results.append({
                    'filename': image_path.name,
                    'path': str(image_path),
                    'text_regions': result['total_boxes'],
                    'text': all_text,
                    'status': 'success'
                })
                
                successful += 1
                print(f"✅ ({result['total_boxes']} regions)")
                
            else:
                results.append({
                    'filename': image_path.name,
                    'path': str(image_path),
                    'text_regions': 0,
                    'text': '',
                    'status': f'error: {response.status_code}'
                })
                failed += 1
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            results.append({
                'filename': image_path.name,
                'path': str(image_path),
                'text_regions': 0,
                'text': '',
                'status': f'error: {str(e)}'
            })
            failed += 1
            print(f"❌ Error: {e}")
    
    # Save results to CSV
    print(f"\n{'-'*60}")
    print(f"Saving results to: {output_file}")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['filename', 'path', 'text_regions', 'text', 'status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(results)
    
    # Also save as JSON for easier parsing
    json_file = output_file.replace('.csv', '.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Summary")
    print(f"{'='*60}")
    print(f"Total images: {len(image_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"\nOutput files:")
    print(f"  📄 CSV: {output_file}")
    print(f"  📄 JSON: {json_file}")
    print(f"{'='*60}\n")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python batch_process.py <input_directory> [output_file] [api_url]")
        print("\nExamples:")
        print("  python batch_process.py samples/")
        print("  python batch_process.py samples/ results.csv")
        print("  python batch_process.py samples/ results.csv http://localhost:8000")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    api_url = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:8000"
    
    process_batch(input_dir, output_file, api_url)

if __name__ == "__main__":
    main()

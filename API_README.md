# Vietnamese OCR API

A FastAPI-based REST API for Vietnamese text recognition using PaddleOCR and VietOCR.

## Features

- **Text Detection**: Uses PaddleOCR for accurate text region detection
- **Text Recognition**: Uses VietOCR for Vietnamese text recognition
- **REST API**: FastAPI-based API with automatic documentation
- **Public Access**: Optional ngrok integration for public URL
- **Multiple Input Formats**: Supports file upload and base64 encoded images

## Installation

The required packages are already installed:
- fastapi
- uvicorn
- pyngrok

Additional dependencies from `requirement.txt`:
- einops==0.2.0
- paddlepaddle
- pyclipper
- lmdb

## Usage

### Option 1: Run Locally

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Option 2: Run with ngrok (Public URL)

```bash
python run_with_ngrok.py
```

This will:
1. Start the FastAPI server
2. Create a public ngrok URL
3. Display both local and public URLs in the console

## API Endpoints

### 1. Root Endpoint
- **URL**: `GET /`
- **Description**: Get API information

### 2. Health Check
- **URL**: `GET /health`
- **Description**: Check if the API and models are ready

### 3. OCR from File Upload
- **URL**: `POST /ocr`
- **Content-Type**: `multipart/form-data`
- **Body**: 
  - `file`: Image file (jpg, png, etc.)

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/ocr" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/image.jpg"
```

**Example using Python:**
```python
import requests

url = "http://localhost:8000/ocr"
files = {"file": open("image.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### 4. OCR from Base64
- **URL**: `POST /ocr/base64`
- **Content-Type**: `application/json`
- **Body**: 
  - `image_base64`: Base64 encoded image string

**Example using Python:**
```python
import requests
import base64

# Read and encode image
with open("image.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

url = "http://localhost:8000/ocr/base64"
response = requests.post(url, json={"image_base64": image_base64})
print(response.json())
```

## Response Format

```json
{
  "success": true,
  "message": "Successfully processed image. Found 5 text regions.",
  "results": [
    {
      "coordinates": [[x1, y1], [x2, y2]],
      "text": "Recognized text",
      "confidence": null
    }
  ],
  "total_boxes": 5
}
```

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These provide interactive API documentation where you can test the endpoints directly.

## Configuration

### GPU Support

By default, the code is configured to use CPU. To enable GPU:

1. Open `main.py`
2. Find the `startup_event()` function
3. Change `use_gpu=False` to `use_gpu=True` in the PaddleOCR initialization

### Model Configuration

The VietOCR model uses the default `vgg_transformer` configuration. To use a custom model:

1. Open `main.py`
2. In the `startup_event()` function, modify:
```python
# Instead of:
config = Cfg.load_config_from_name('vgg_transformer')

# Use:
config = Cfg.load_config_from_file('path/to/config.yml')
config['weights'] = 'path/to/weights.pth'
```

## Testing

A test script is provided to quickly test the API:

```bash
python test_api.py path/to/image.jpg
```

## Troubleshooting

### Models not loading
- Make sure all dependencies are installed
- Check that the vietocr and PaddleOCR directories are present
- Wait for the startup process to complete (check `/health` endpoint)

### Memory issues
- If running on limited memory, consider using CPU instead of GPU
- Reduce the image size before sending to the API

### Port already in use
- Change the port in `main.py` or `run_with_ngrok.py`
- Default port is 8000

## Project Structure

```
vietnamese-ocr/
├── main.py                 # Main FastAPI application
├── run_with_ngrok.py      # Run with ngrok tunnel
├── test_api.py            # Test script
├── predict.py             # Original prediction script
├── predict.ipynb          # Jupyter notebook version
├── vietocr/               # VietOCR library
├── PaddleOCR/             # PaddleOCR library
└── samples/               # Sample images
```

## License

This project uses:
- PaddleOCR (Apache License 2.0)
- VietOCR (MIT License)

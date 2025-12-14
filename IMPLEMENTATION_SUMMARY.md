# Vietnamese OCR API - Implementation Summary

## Overview
I've created a complete FastAPI-based REST API for Vietnamese OCR using PaddleOCR and VietOCR, based on the logic from `predict.ipynb`.

## Files Created

### 1. `main.py` - Main FastAPI Application
**Purpose**: Core API implementation with OCR functionality

**Key Features**:
- FastAPI application with CORS support
- Model initialization on startup (PaddleOCR + VietOCR)
- Two OCR endpoints: file upload and base64
- Health check endpoint
- Automatic API documentation (Swagger/ReDoc)

**Endpoints**:
- `GET /` - Root endpoint with API info
- `GET /health` - Health check
- `POST /ocr` - Process uploaded image file
- `POST /ocr/base64` - Process base64 encoded image

**Models**:
- **PaddleOCR**: Text detection (finding text regions)
- **VietOCR**: Text recognition (reading Vietnamese text)

### 2. `run_with_ngrok.py` - Public URL Access
**Purpose**: Run the API with ngrok tunnel for public access

**Features**:
- Automatically creates ngrok tunnel
- Displays both local and public URLs
- Easy sharing for testing/demo

**Usage**:
```bash
python run_with_ngrok.py
```

### 3. `test_api.py` - API Testing Script
**Purpose**: Quick testing of the API

**Features**:
- Tests health endpoint
- Tests OCR with sample images
- Saves results to JSON file
- Clear console output

**Usage**:
```bash
python test_api.py samples/1.jpg
```

### 4. `example_client.py` - Usage Examples
**Purpose**: Demonstrates various ways to use the API

**Examples**:
1. File upload
2. Base64 encoding
3. Batch processing
4. Error handling

**Usage**:
```bash
python example_client.py
```

### 5. `API_README.md` - Documentation
**Purpose**: Comprehensive API documentation

**Contents**:
- Installation instructions
- API endpoint documentation
- Usage examples (curl, Python)
- Configuration options
- Troubleshooting guide

### 6. `requirements_api.txt` - Dependencies
**Purpose**: List all required packages

**Packages**:
- FastAPI, uvicorn, pyngrok
- Image processing (PIL, OpenCV)
- OCR libraries (PaddleOCR, VietOCR)

## How to Run

### Option 1: Local Only
```bash
# Install dependencies (if not already installed)
pip install -r requirements_api.txt

# Run the server
python main.py
```
Access at: `http://localhost:8000`

### Option 2: With Public URL (ngrok)
```bash
# Run with ngrok
python run_with_ngrok.py
```
You'll get a public URL like: `https://xxxx-xx-xx-xx-xx.ngrok.io`

## Testing

### Quick Test
```bash
python test_api.py samples/1.jpg
```

### Run Examples
```bash
python example_client.py
```

### Manual Test with curl
```bash
curl -X POST "http://localhost:8000/ocr" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@samples/1.jpg"
```

## API Response Format

```json
{
  "success": true,
  "message": "Successfully processed image. Found 5 text regions.",
  "results": [
    {
      "coordinates": [[x1, y1], [x2, y2]],
      "text": "Recognized Vietnamese text",
      "confidence": null
    }
  ],
  "total_boxes": 5
}
```

## Key Implementation Details

### Image Processing Flow
1. **Upload**: Image received via HTTP
2. **Detection**: PaddleOCR detects text regions
3. **Cropping**: Each region is cropped with padding
4. **Recognition**: VietOCR recognizes text in each region
5. **Response**: JSON with coordinates and text

### Model Configuration
- **VietOCR**: Uses `vgg_transformer` model
- **PaddleOCR**: Vietnamese language support
- **Device**: Auto-detects CUDA/CPU (configurable)

### Error Handling
- Invalid image format detection
- Model initialization checks
- Graceful error responses
- Detailed error messages

## Interactive Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These provide:
- Interactive API testing
- Request/response examples
- Schema documentation
- Try-it-out functionality

## Customization Options

### Change Port
Edit in `main.py` or `run_with_ngrok.py`:
```python
PORT = 8000  # Change to your preferred port
```

### Enable GPU
In `main.py`, change:
```python
detector = PaddleOCR(use_angle_cls=False, lang="vi", use_gpu=True)
```

### Custom VietOCR Model
In `main.py`, modify:
```python
config = Cfg.load_config_from_file('path/to/config.yml')
config['weights'] = 'path/to/weights.pth'
```

### Adjust Padding
In the `/ocr` endpoint, change:
```python
boxes, texts = process_image(image_bytes, padding=4)  # Adjust padding value
```

## Production Considerations

### For Production Use:
1. **Add Authentication**: Implement API keys or OAuth
2. **Rate Limiting**: Prevent abuse
3. **Logging**: Add proper logging
4. **Error Tracking**: Integrate Sentry or similar
5. **Caching**: Cache model predictions
6. **Load Balancing**: Use multiple workers
7. **HTTPS**: Use proper SSL certificates

### Performance Tips:
- Use GPU for faster processing
- Implement request queuing for high load
- Consider async processing for large batches
- Optimize image preprocessing

## Troubleshooting

### Models not loading
- Check all dependencies are installed
- Verify vietocr and PaddleOCR directories exist
- Wait for startup to complete (check `/health`)

### Memory issues
- Use CPU instead of GPU if limited memory
- Reduce image size before upload
- Process images in smaller batches

### Connection errors
- Ensure port is not in use
- Check firewall settings
- Verify API is running

## Next Steps

1. **Test the API**: Run `python test_api.py samples/1.jpg`
2. **Try Examples**: Run `python example_client.py`
3. **Read Docs**: Check `API_README.md` for details
4. **Customize**: Adjust settings as needed
5. **Deploy**: Use ngrok or deploy to cloud

## Support

For issues or questions:
1. Check `API_README.md` for detailed documentation
2. Review error messages in console
3. Test with `/health` endpoint
4. Verify all dependencies are installed

---

**Created**: Based on `predict.ipynb` and `predict.py`
**Framework**: FastAPI
**OCR**: PaddleOCR + VietOCR
**Status**: Ready to use ✅

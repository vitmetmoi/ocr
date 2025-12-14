import os
import io
import base64
from typing import List, Dict, Optional
from PIL import Image
import cv2
import numpy as np

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from vietocr.vietocr.tool.predictor import Predictor
from vietocr.vietocr.tool.config import Cfg
from PaddleOCR import PaddleOCR

# Initialize FastAPI app
app = FastAPI(
    title="Vietnamese OCR API",
    description="API for Vietnamese text recognition using PaddleOCR and VietOCR",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for models
detector = None
recognitor = None

# Response models
class OCRBox(BaseModel):
    coordinates: List[List[int]]
    text: str
    confidence: Optional[float] = None

class OCRResponse(BaseModel):
    success: bool
    message: str
    results: List[OCRBox]
    total_boxes: int

# Initialize models on startup
@app.on_event("startup")
async def startup_event():
    """Initialize OCR models when the application starts"""
    global detector, recognitor
    
    print("Initializing OCR models...")
    
    # Configure VietOCR
    config = Cfg.load_config_from_name('vgg_transformer')
    config['cnn']['pretrained'] = True
    config['predictor']['beamsearch'] = True
    
    # Set device (use 'cuda:0' for GPU, 'cpu' for CPU)
    # Change this based on your system
    try:
        import torch
        config['device'] = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        print(f"VietOCR using device: {config['device']}")
    except:
        config['device'] = 'cpu'
        print("VietOCR using device: cpu")
    
    recognitor = Predictor(config)
    print("VietOCR model loaded successfully")
    
    # Configure PaddleOCR
    # Set use_gpu=True if you have GPU, False otherwise
    detector = PaddleOCR(use_angle_cls=False, lang="vi", use_gpu=False)
    print("PaddleOCR model loaded successfully")
    
    print("All models initialized successfully!")

def process_image(image_bytes: bytes, padding: int = 4) -> tuple:
    """
    Process image and extract text using OCR
    
    Args:
        image_bytes: Image data in bytes
        padding: Padding to add around detected boxes
        
    Returns:
        tuple: (boxes, texts) where boxes are coordinates and texts are recognized text
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Failed to decode image")
    
    # Create temporary file for PaddleOCR (it requires file path)
    temp_path = "temp_image.jpg"
    cv2.imwrite(temp_path, img)
    
    try:
        # Text detection with PaddleOCR
        result = detector.ocr(temp_path, cls=False, det=True, rec=False)
        
        if result is None or len(result) == 0 or result[0] is None:
            return [], []
        
        result = result[0]
        
        # Filter and format boxes
        boxes = []
        for line in result:
            box = [[int(line[0][0]), int(line[0][1])], [int(line[2][0]), int(line[2][1])]]
            boxes.append(box)
        
        # Reverse order (bottom to top)
        boxes = boxes[::-1]
        
        # Get image dimensions
        img_height, img_width = img.shape[:2]
        
        # Add padding to boxes and ensure valid coordinates
        for box in boxes:
            box[0][0] = max(0, box[0][0] - padding)
            box[0][1] = max(0, box[0][1] - padding)
            box[1][0] = min(img_width, box[1][0] + padding)
            box[1][1] = min(img_height, box[1][1] + padding)
        
        # Text recognition with VietOCR
        texts = []
        valid_boxes = []
        
        for box in boxes:
            # Crop image
            cropped_image = img[box[0][1]:box[1][1], box[0][0]:box[1][0]]
            
            # Check if cropped image has valid dimensions
            if cropped_image.shape[0] == 0 or cropped_image.shape[1] == 0:
                print(f"Warning: Skipping invalid box with dimensions {cropped_image.shape}")
                continue
            
            try:
                # Convert to PIL Image
                cropped_pil = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
                
                # Recognize text
                text = recognitor.predict(cropped_pil)
                
                texts.append(text)
                valid_boxes.append(box)
                
            except Exception as e:
                print(f"Error processing box: {e}")
                continue
        
        return valid_boxes, texts
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vietnamese OCR API",
        "status": "running",
        "endpoints": {
            "/ocr": "POST - Process image and extract text",
            "/health": "GET - Check API health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": {
            "detector": detector is not None,
            "recognitor": recognitor is not None
        }
    }

@app.post("/ocr", response_model=OCRResponse)
async def ocr_endpoint(file: UploadFile = File(...)):
    """
    OCR endpoint to process uploaded images
    
    Args:
        file: Uploaded image file
        
    Returns:
        OCRResponse with detected text and bounding boxes
    """
    try:
        # Check if models are loaded
        if detector is None or recognitor is None:
            raise HTTPException(
                status_code=503,
                detail="OCR models not initialized. Please wait for startup to complete."
            )
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Read image file
        image_bytes = await file.read()
        
        # Process image
        boxes, texts = process_image(image_bytes, padding=4)
        
        # Format results
        results = []
        for box, text in zip(boxes, texts):
            results.append(OCRBox(
                coordinates=box,
                text=text,
                confidence=None  # VietOCR doesn't return confidence by default
            ))
        
        return OCRResponse(
            success=True,
            message=f"Successfully processed image. Found {len(results)} text regions.",
            results=results,
            total_boxes=len(results)
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error processing image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

@app.post("/ocr/base64", response_model=OCRResponse)
async def ocr_base64_endpoint(image_base64: str):
    """
    OCR endpoint to process base64 encoded images
    
    Args:
        image_base64: Base64 encoded image string
        
    Returns:
        OCRResponse with detected text and bounding boxes
    """
    try:
        # Check if models are loaded
        if detector is None or recognitor is None:
            raise HTTPException(
                status_code=503,
                detail="OCR models not initialized. Please wait for startup to complete."
            )
        
        # Decode base64 image
        try:
            # Remove data URL prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            image_bytes = base64.b64decode(image_base64)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base64 image: {str(e)}"
            )
        
        # Process image
        boxes, texts = process_image(image_bytes, padding=4)
        
        # Format results
        results = []
        for box, text in zip(boxes, texts):
            results.append(OCRBox(
                coordinates=box,
                text=text,
                confidence=None
            ))
        
        return OCRResponse(
            success=True,
            message=f"Successfully processed image. Found {len(results)} text regions.",
            results=results,
            total_boxes=len(results)
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error processing image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    
    # Run the FastAPI application
    # You can change the port if needed
    uvicorn.run(app, host="0.0.0.0", port=8000)

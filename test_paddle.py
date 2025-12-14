import os
# CRITICAL: Set these BEFORE importing paddle/PaddleOCR
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_use_cudnn"] = "0"

import cv2
from PIL import Image
from PaddleOCR import PaddleOCR

# Initialize PaddleOCR with OneDNN disabled
detector = PaddleOCR(
    use_angle_cls=False, 
    lang='en', 
    use_gpu=False,
    enable_mkldnn=False,  # Explicitly disable OneDNN
    cpu_threads=1,
    show_log=True
)

print("PaddleOCR initialized successfully!")

# Test with a simple detection
# If you have a test image, uncomment and modify the path below:
# result = detector.ocr('./samples/test.jpg', cls=False, det=True, rec=False)
# print("Detection result:", result)

# Quick Start Guide - Vietnamese OCR API

## 🚀 Get Started in 3 Steps

### Step 1: Run the API

Choose one option:

**Option A: Local only**
```bash
python main.py
```

**Option B: With public URL (recommended for testing)**
```bash
python run_with_ngrok.py
```

### Step 2: Test the API

```bash
python test_api.py samples/1.jpg
```

### Step 3: Use the API

**Python Example:**
```python
import requests

# Upload image
with open('image.jpg', 'rb') as f:
    response = requests.post('http://localhost:8000/ocr', files={'file': f})

# Get results
result = response.json()
for item in result['results']:
    print(item['text'])
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/ocr" \
  -F "file=@image.jpg"
```

## 📖 Interactive Documentation

Visit `http://localhost:8000/docs` for:
- Interactive API testing
- Request/response examples
- Try-it-out functionality

## 🔧 Common Tasks

### Check if API is ready
```bash
curl http://localhost:8000/health
```

### Process multiple images
```python
import requests

images = ['img1.jpg', 'img2.jpg', 'img3.jpg']
for img in images:
    with open(img, 'rb') as f:
        response = requests.post('http://localhost:8000/ocr', files={'file': f})
        print(f"{img}: {response.json()['total_boxes']} text regions found")
```

### Use base64 encoding
```python
import requests
import base64

with open('image.jpg', 'rb') as f:
    img_base64 = base64.b64encode(f.read()).decode()

response = requests.post(
    'http://localhost:8000/ocr/base64',
    json={'image_base64': img_base64}
)
```

## 📝 Response Format

```json
{
  "success": true,
  "message": "Successfully processed image. Found 3 text regions.",
  "results": [
    {
      "coordinates": [[10, 20], [100, 50]],
      "text": "Vietnamese text here"
    }
  ],
  "total_boxes": 3
}
```

## ⚙️ Configuration

### Enable GPU (faster processing)
Edit `main.py`, line ~77:
```python
detector = PaddleOCR(use_angle_cls=False, lang="vi", use_gpu=True)
```

### Change port
Edit `main.py`, last line:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change 8000 to your port
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Models not loading | Wait 30-60 seconds for startup, check `/health` |
| Port in use | Change port in `main.py` |
| Out of memory | Use CPU instead of GPU |
| Can't connect | Check if API is running, verify port |

## 📚 More Information

- **Full Documentation**: See `API_README.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Code Examples**: Run `python example_client.py`

## 💡 Tips

1. **First run takes longer** - Models need to load (30-60 seconds)
2. **Use `/health` endpoint** - Check if models are ready
3. **Interactive docs are your friend** - Visit `/docs` for easy testing
4. **Start with small images** - Test with small images first
5. **Check console output** - Errors and info are printed there

## 🎯 Next Steps

1. ✅ Run the API
2. ✅ Test with sample image
3. ✅ Check interactive docs
4. ✅ Try your own images
5. ✅ Integrate into your application

---

Need help? Check the full documentation in `API_README.md`

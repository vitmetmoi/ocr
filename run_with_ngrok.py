"""
Run the FastAPI OCR service with ngrok tunnel for public access
"""
import os
import uvicorn
from pyngrok import ngrok

# Import the FastAPI app
from main import app

def run_with_ngrok(port: int = 8000):
    """
    Run the FastAPI application with ngrok tunnel
    
    Args:
        port: Port to run the server on (default: 8000)
    """
    # Set your ngrok auth token if you have one
    # ngrok.set_auth_token("YOUR_AUTH_TOKEN_HERE")
    
    # Open a ngrok tunnel to the HTTP server
    public_url = ngrok.connect(port)
    print("\n" + "="*60)
    print(f"🚀 FastAPI OCR Service is running!")
    print(f"📍 Local URL: http://localhost:{port}")
    print(f"🌐 Public URL: {public_url}")
    print(f"📖 API Documentation: {public_url}/docs")
    print(f"📊 Alternative docs: {public_url}/redoc")
    print("="*60 + "\n")
    
    # Run the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    # You can change the port here if needed
    PORT = 8000
    run_with_ngrok(PORT)

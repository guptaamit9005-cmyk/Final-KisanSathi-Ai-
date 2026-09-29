from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="KisanSathi AI Crop Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "success": True,
        "message": "KisanSathi AI FastAPI server is running"
    }


@app.get("/health")
def health():
    return {
        "success": True,
        "service": "crop-analysis",
        "status": "online"
    }


@app.post("/analyze-crop")
async def analyze_crop(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No image uploaded")

    allowed_types = ["image/jpeg", "image/png", "image/webp"]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Upload a JPG, PNG, or WEBP image"
        )

    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded image is empty")

    return {
        "success": True,
        "result": {
            "disease": "Connection test successful",
            "confidence": "Not available",
            "recommendation": (
                "FastAPI received the image successfully. "
                "Connect your trained crop disease model for actual predictions."
            )
        }
    }
# backend.py
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import io, os, logging
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()

from helper import (
    generate_text_to_video,
    generate_image_to_video,
    generate_video_from_reference_images,
    generate_video_from_first_last_frames,
    extend_veo_video,
    handle_async_operation,
    get_operation_status,
    download_video_bytes,
)

logger = logging.getLogger("backend")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Veo 3.1 Backend Suite")
DEFAULT_MODEL = os.getenv("VEO_MODEL_NAME", "veo-3.1-fast-generate-preview")
# NEW: models that support referenceImages and first/last frames
SUPPORTED_MODEL = os.getenv("VEO_SUPPORTED_MODEL", "veo-3.1-generate-preview")

# Allow Streamlit (port 8501)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------
# TEXT → VIDEO
# ----------------------------------------------------------------------
@app.post("/text_to_video")
async def text_to_video(
    prompt: str = Form(...),
    model: str = Form("veo-3.1-fast-generate-preview"),
    duration_seconds: int = Form(8),
    resolution: str = Form("1080p"),
    aspect_ratio: str = Form("16:9")
):
    try:
        payload = generate_text_to_video(prompt, model, resolution, aspect_ratio, duration_seconds)
        return {"ok": True, **payload}
    except Exception as e:
        logger.exception("Error in /text_to_video")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------
# IMAGE → VIDEO
# ----------------------------------------------------------------------
@app.post("/image_to_video")
async def image_to_video(
    prompt: str = Form(...),
    image: UploadFile = File(...),
    model: str = Form("veo-3.1-fast-generate-preview"),
    duration_seconds: int = Form(8),
    resolution: str = Form("1080p"),
    aspect_ratio: str = Form("16:9")
):
    try:
        # Read once and log safely
        contents = await image.read()
        size = len(contents)
        logger.info(f"Image upload received: name={image.filename}, size={size} bytes")

        if size == 0:
            raise HTTPException(status_code=400, detail="Uploaded image is empty or unreadable.")

        # Generate video (pass bytes directly)
        payload = generate_image_to_video(prompt, contents, model, resolution, aspect_ratio, duration_seconds)
        return {"ok": True, **payload}

    except HTTPException:
        # re-raise HTTPExceptions unchanged
        raise
    except Exception as e:
        logger.exception("Error in /image_to_video")
        error_msg = str(e)
        if "all attempts including REST fallback failed" in error_msg:
            detail = "Failed to generate video. Please check your image format or try again later."
        else:
            detail = f"An error occurred: {error_msg}"
        raise HTTPException(status_code=500, detail=detail)

# ----------------------------------------------------------------------
# USING REFERENCE IMAGES
# ----------------------------------------------------------------------
@app.post("/video_from_reference_images")
async def video_from_reference_images(
    prompt: str = Form(...),
    reference_images: List[UploadFile] = File(...),
    duration_seconds: int = Form(8),
    resolution: str = Form("1080p"),
    aspect_ratio: str = Form("16:9")
):
    """
    Generate a video using multiple reference images + prompt.

    Matches Streamlit mode: "Using Reference Images".
    """
    try:
        if not reference_images:
            raise HTTPException(status_code=400, detail="No reference images uploaded")

        # Read all uploaded images into memory
        image_bytes_list = [await f.read() for f in reference_images]

        # IMPORTANT: model is a plain string, NOT Form(...)
        result = generate_video_from_reference_images(
            prompt=prompt,
            images=image_bytes_list,
            model = SUPPORTED_MODEL,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            duration_seconds=duration_seconds,
        )
        return {"ok": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("video_from_reference_images failed")
        raise HTTPException(status_code=500, detail=str(e))
# ----------------------------------------------------------------------
# FIRST + LAST FRAMES → VIDEO
# ----------------------------------------------------------------------
@app.post("/video_from_first_last_frames")
async def video_from_first_last_frames(
    prompt: str = Form(...),
    first_frame: UploadFile = File(...),
    last_frame: UploadFile = File(...),
    duration_seconds: int = Form(8),
    resolution: str = Form("1080p"),
    aspect_ratio: str = Form("16:9")
):
    """
    Generate a video using first + last frame images + prompt.

    Matches Streamlit mode: "Using First + Last Frames".
    """
    try:
        if first_frame is None or last_frame is None:
            raise HTTPException(
                status_code=400,
                detail="Both first_frame and last_frame are required",
            )

        first_bytes = await first_frame.read()
        last_bytes = await last_frame.read()

        # Again, model is a string, not Form(...)
        result = generate_video_from_first_last_frames(
            prompt=prompt,
            first=first_bytes,
            last=last_bytes,
            model = SUPPORTED_MODEL,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            duration_seconds=duration_seconds,
        )
        return {"ok": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("video_from_first_last_frames failed")
        raise HTTPException(status_code=500, detail=str(e))
    
# ----------------------------------------------------------------------
@app.post("/extend_veo_video")
async def extend_veo_video_endpoint(
    prompt: str = Form(...),
    base_video: UploadFile = File(...),
    model: str = Form("veo-3.1-fast-generate-preview"),
    duration_seconds: int = Form(8),
    resolution: str = Form("1080p"),
    aspect_ratio: str = Form("16:9")
):
    try:
        video_bytes = await base_video.read()
        payload = extend_veo_video(prompt, video_bytes, model, resolution=resolution, aspect_ratio=aspect_ratio, duration_seconds=duration_seconds)
        return {"ok": True, **payload}
    except Exception as e:
        logger.exception("Error in /extend_veo_video")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------
# ASYNC OPERATIONS
# ----------------------------------------------------------------------
@app.post("/async_operations")
async def async_operations(operation_name: str = Form(...)):
    try:
        payload = handle_async_operation(operation_name)
        return {"ok": True, **payload}
    except Exception as e:
        logger.exception("Error in /async_operations")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------
# COMMON POLLING / DOWNLOAD / SAVE
# ----------------------------------------------------------------------
@app.get("/status/{operation_name:path}")
def status(operation_name: str):
    try:
        return {"ok": True, **get_operation_status(operation_name)}
    except Exception as e:
        logger.exception("Status check failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{operation_name:path}")
def download(operation_name: str):
    data, filename = download_video_bytes(operation_name)
    if not data:
        raise HTTPException(status_code=404, detail="Video not available or incomplete")
    return StreamingResponse(io.BytesIO(data), media_type="video/mp4",
                             headers={"Content-Disposition": f'attachment; filename="{filename}"'})

@app.get("/save_local/{operation_name:path}")
def save_local(operation_name: str):
    try:
        data, filename = download_video_bytes(operation_name)
        if not data:
            raise HTTPException(status_code=404, detail="Video not available or incomplete")

        out_dir = os.path.join(os.getcwd(), "Generated_Video")
        os.makedirs(out_dir, exist_ok=True)
        IST = timezone(timedelta(hours=5, minutes=30))
        ts = datetime.now(IST).strftime("%Y%m%d-%H%M%S")
        safe_name = f"{os.path.splitext(filename)[0]}_{ts}.mp4"
        path = os.path.join(out_dir, safe_name)
        with open(path, "wb") as f:
            f.write(data)
        return {"ok": True, "file_path": os.path.abspath(path)}
    except Exception as e:
        logger.exception("Save local failed")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)

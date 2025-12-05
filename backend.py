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
    stitch_videos,
    get_video_object_from_operation,
)

logger = logging.getLogger("backend")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Veo 3.1 Backend Suite")
DEFAULT_MODEL = os.getenv("VEO_MODEL_NAME", "veo-3.1-fast-generate-preview")
# NEW: models that support referenceImages and first/last frames
SUPPORTED_MODEL = os.getenv("VEO_SUPPORTED_MODEL", "veo-3.1-generate-preview")

# Allow Streamlit (port 8501) and React Frontend (port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501", 
        "http://127.0.0.1:8501",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Veo 3.1 Backend is running"}

@app.post("/text_to_video")
async def text_to_video_endpoint(
    prompt: str = Form(...),
    model: str = Form("veo-3.1-fast-generate-preview"),
    duration_seconds: int = Form(8),
    resolution: str = Form("1080p"),
    aspect_ratio: str = Form("16:9")
):
    try:
        result = generate_text_to_video(prompt, model, resolution=resolution, aspect_ratio=aspect_ratio, duration_seconds=duration_seconds)
        return {"ok": True, **result}
    except Exception as e:
        logger.exception("text_to_video failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/image_to_video")
async def image_to_video_endpoint(
    prompt: str = Form(...),
    image: UploadFile = File(...),
    model: str = Form("veo-3.1-fast-generate-preview"),
    duration_seconds: int = Form(8),
    resolution: str = Form("1080p"),
    aspect_ratio: str = Form("16:9")
):
    try:
        image_bytes = await image.read()
        result = generate_image_to_video(prompt, image_bytes, model, resolution=resolution, aspect_ratio=aspect_ratio, duration_seconds=duration_seconds)
        return {"ok": True, **result}
    except Exception as e:
        logger.exception("image_to_video failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/video_from_reference_images")
async def video_from_reference_images_endpoint(
    prompt: str = Form(...),
    images: List[UploadFile] = File(...),
    model: str = Form("veo-3.1-generate-preview"),  # Default to supported model
    duration_seconds: int = Form(8),
    resolution: str = Form("1080p"),
    aspect_ratio: str = Form("16:9")
):
    try:
        # Read all images
        image_bytes_list = []
        for img in images:
            image_bytes_list.append(await img.read())
            
        result = generate_video_from_reference_images(
            prompt, 
            image_bytes_list, 
            model, 
            resolution=resolution, 
            aspect_ratio=aspect_ratio, 
            duration_seconds=duration_seconds
        )
        return {"ok": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("video_from_reference_images failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/video_from_first_last_frames")
async def video_from_first_last_frames_endpoint(
    prompt: str = Form(...),
    first_frame: UploadFile = File(...),
    last_frame: UploadFile = File(...),
    model: str = Form("veo-3.1-generate-preview"), # Default to supported model
    duration_seconds: int = Form(8),
    resolution: str = Form("1080p"),
    aspect_ratio: str = Form("16:9")
):
    try:
        first_bytes = await first_frame.read()
        last_bytes = await last_frame.read()
        
        result = generate_video_from_first_last_frames(
            prompt, 
            first_bytes, 
            last_bytes, 
            model, 
            resolution=resolution, 
            aspect_ratio=aspect_ratio, 
            duration_seconds=duration_seconds
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
    base_video: Optional[UploadFile] = File(None),
    previous_operation_name: Optional[str] = Form(None),
    model: str = Form("veo-3.1-fast-generate-preview"),
    duration_seconds: int = Form(8),
    resolution: str = Form("1080p"),
    aspect_ratio: str = Form("16:9")
):
    try:
        prior_video_obj = None
        video_bytes = None
        
        # Scenario 1: Extend from Gallery (using previous operation)
        if previous_operation_name:
            logger.info(f"Extending from previous operation: {previous_operation_name}")
            prior_video_obj = get_video_object_from_operation(previous_operation_name)
            if not prior_video_obj:
                raise HTTPException(status_code=400, detail="Could not retrieve video object from previous operation. It might be expired or failed.")
            
            # Try to download the video bytes from the previous operation to save as base for THIS extension
            try:
                prev_bytes, _ = download_video_bytes(previous_operation_name)
                if prev_bytes:
                    video_bytes = prev_bytes
            except Exception as e:
                logger.warning(f"Could not download bytes for previous operation: {e}")

        # Scenario 2: Extend from Upload
        elif base_video:
            video_bytes = await base_video.read()
        else:
            raise HTTPException(status_code=400, detail="Either base_video or previous_operation_name must be provided")

        if not video_bytes and not prior_video_obj:
             raise HTTPException(status_code=400, detail="Failed to get video content for extension")

        if video_bytes is None:
             video_bytes = b"" # Dummy if we strictly use prior_obj, but stitching will fail.
        
        payload = extend_veo_video(
            prompt, 
            video_bytes, 
            model, 
            prior_generated_video_obj=prior_video_obj,
            resolution=resolution, 
            aspect_ratio=aspect_ratio, 
            duration_seconds=duration_seconds
        )
        
        # Save base video for later stitching ONLY if we uploaded a file (Scenario 2).
        # If we extended from gallery (Scenario 1), the API returns the FULL video, so stitching is not needed (and causes duplication).
        print(f"DEBUG: extend_veo_video payload: {payload}")
        if payload.get("ok", True) and base_video: 
            op_name = payload.get("operation_name")
            if op_name and video_bytes:
                safe_op_name = op_name.replace("/", "_")
                base_path = f"temp_base_{safe_op_name}.mp4"
                with open(base_path, "wb") as f:
                    f.write(video_bytes)
                print(f"DEBUG: Saved base video to {base_path} (size: {len(video_bytes)})")
                logger.info(f"Saved base video for stitching: {base_path}")
                
        return {"ok": True, **payload}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("extend_veo_video failed")
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
    
    # Check if we have a base video to stitch
    safe_op_name = operation_name.replace("/", "_")
    base_path = f"temp_base_{safe_op_name}.mp4"
    
    print(f"DEBUG: Download request for {operation_name}")
    print(f"DEBUG: Looking for base video at {base_path}")
    print(f"DEBUG: File exists? {os.path.exists(base_path)}")
    
    if os.path.exists(base_path):
        logger.info(f"Found base video for stitching: {base_path}")
        stitched_data = stitch_videos(base_path, data)
        if stitched_data:
            data = stitched_data
            logger.info("Video stitching successful")
            print("DEBUG: Stitching successful")
        else:
            logger.warning("Video stitching failed, returning extension only")
            print("DEBUG: Stitching failed (returned None)")
        
        # Cleanup base video
        try:
            os.remove(base_path)
            logger.info(f"Deleted temp base video: {base_path}")
        except Exception as e:
            logger.warning(f"Failed to delete temp base video: {e}")

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
    uvicorn.run("backend:app", host="127.0.0.1", port=8002, reload=True)

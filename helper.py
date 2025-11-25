import os
import time
import io
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, List
from dotenv import load_dotenv
import mimetypes
import uuid
import inspect
from pathlib import Path
import base64
import json
import  requests, json, base64, logging
logger = logging.getLogger("helper")

load_dotenv()
logger = logging.getLogger("helper")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Lazy import of the Google GenAI SDK
try:
    import google.genai as genai
    from google.genai import types
except Exception:
    genai, types = None, None

_client = None

# --------------------------------------------------------------
# CLIENT CREATION
# --------------------------------------------------------------
def create_genai_client():
    """Initialize and cache a google.genai.Client."""
    global _client
    if _client:
        return _client
    if genai is None:
        raise RuntimeError("google-genai SDK not installed. Install via: pip install google-genai")

    api_key = os.getenv("GEMINI_API_KEY")
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    try:
        if api_key:
            _client = genai.Client(api_key=api_key)
        elif project:
            _client = genai.Client(vertexai=True, project=project, location=location)
        else:
            raise RuntimeError("Missing API credentials for GenAI / Veo 3.1.")
    except Exception as e:
        raise RuntimeError(f"Failed to create GenAI client: {e}")

    # optional: log available client.files API shapes for debugging once
    try:
        files_obj = getattr(_client, "files", None)
        if files_obj is not None:
            logger.info("create_genai_client: client.files available, dir: %s", dir(files_obj))
            upload_fn = getattr(files_obj, "upload", None)
            if upload_fn:
                try:
                    logger.info("create_genai_client: upload signature: %s", inspect.signature(upload_fn))
                except Exception:
                    logger.info("create_genai_client: could not inspect upload signature")
    except Exception:
        pass

    return _client

# --------------------------------------------------------------
# UTILITY: SAFELY EXTRACT OPERATION NAME
# --------------------------------------------------------------
def get_operation_name(op) -> str:
    """
    Safely extract an operation name whether the SDK returned:
      - an operation object (with .name), or
      - a plain string (operation name), or
      - some other wrapper.
    Also logs the returned type for debugging.
    """
    try:
        if isinstance(op, str):
            logger.info(f"get_operation_name: received str -> {op}")
            return op
        if hasattr(op, "name"):
            name = getattr(op, "name")
            logger.info(f"get_operation_name: object with .name -> {name} (type: {type(op)})")
            return name
        s = str(op)
        logger.info(f"get_operation_name: fallback str(op) -> {s} (type: {type(op)})")
        return s
    except Exception as e:
        logger.exception("get_operation_name error, falling back to str(op)")
        return str(op)

# --------------------------------------------------------------
# UTILITY: guess mime type
# --------------------------------------------------------------
def _guess_mime_type(path: str, fallback_image: str = "image/jpeg") -> str:
    mime, _ = mimetypes.guess_type(path)
    if mime:
        return mime
    ext = Path(path).suffix.lower()
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    return fallback_image

# --------------------------------------------------------------
# ADAPTIVE UPLOAD HELPER (inspects SDK signature and tries compatible shapes)
# --------------------------------------------------------------
class UploadFileError(RuntimeError):
    pass

# Replace existing upload_file with this function in helper.py
import io
import inspect
from typing import Any

class UploadFileError(RuntimeError):
    pass

def upload_file(client, local_path: str, *, debug_log_signature: bool = True) -> Any:
    """
    Adaptive uploader tuned for the google.genai SDK variant observed in logs.
    Uses upload(file=..., config=...) where config must include mime_type (not filename).
    """
    logger.info("upload_file: attempting upload for %s", local_path)

    # Read file bytes
    try:
        with open(local_path, "rb") as fh:
            data = fh.read()
    except Exception as e:
        raise UploadFileError(f"Failed to open local file '{local_path}': {e}")

    if not data:
        raise UploadFileError("upload_file: file is empty")

    basename = os.path.basename(local_path)
    mime_type = _guess_mime_type(local_path)

    files_obj = getattr(client, "files", None)
    if files_obj is None:
        raise UploadFileError("client has no attribute 'files'")

    upload_fn = getattr(files_obj, "upload", None)
    create_fn = getattr(files_obj, "create", None)
    last_exc = None

    # Inspect signature for logging
    try:
        if upload_fn is not None:
            sig = inspect.signature(upload_fn)
            logger.info("upload_file: detected upload signature: %s", sig)
            param_names = [p for p in sig.parameters.keys() if p not in ("self", "cls")]
            logger.info("upload_file: upload parameter names: %s", param_names)
        else:
            param_names = []
    except Exception:
        logger.info("upload_file: could not inspect upload signature")
        param_names = []

    # 1) Preferred: upload(file=BytesIO(...), config={"mime_type": mime_type})
    if upload_fn is not None and "file" in param_names:
        # try typed config if available, but only with accepted fields (mime_type / display_name)
        tried_cfgs = []
        # candidate configs to try (dicts or typed objects)
        cfg_candidates = []
        try:
            # prefer typed UploadFileConfig if available and accepts mime_type
            if types and hasattr(types, "UploadFileConfig"):
                try:
                    cfg_candidates.append(types.UploadFileConfig(mime_type=mime_type))
                except Exception:
                    # typed attempt failed; we'll try dict forms below
                    pass
        except Exception:
            pass

        # dict forms: mime_type only; mime_type + display_name
        cfg_candidates.append({"mime_type": mime_type})
        cfg_candidates.append({"mime_type": mime_type, "display_name": basename})
        # also try a variant using 'mimeType' if some SDKs expect camelCase
        cfg_candidates.append({"mimeType": mime_type})
        cfg_candidates.append({"mime_type": mime_type, "name": basename})

        for cfg in cfg_candidates:
            try:
                logger.info("upload_file: trying upload(file=BytesIO(...), config=%s)", type(cfg) if not isinstance(cfg, dict) else cfg)
                result = upload_fn(file=io.BytesIO(data), config=cfg)
                logger.info("upload_file: success via upload(file=..., config=...) -> %s", type(result))
                return result
            except Exception as e:
                last_exc = e
                logger.info("upload_file: upload(file=..., config=%s) failed: %s", cfg, e)

        # try upload(file=BytesIO(data), mime_type=...) if SDK unexpectedly accepts direct mime_type kw
        try:
            logger.info("upload_file: trying upload(file=BytesIO(data), mime_type=%s) as alternate", mime_type)
            result = upload_fn(file=io.BytesIO(data), mime_type=mime_type)  # may raise TypeError
            logger.info("upload_file: success via upload(file=..., mime_type=...) -> %s", type(result))
            return result
        except Exception as e:
            last_exc = e
            logger.info("upload_file: upload(file=..., mime_type=...) failed: %s", e)

    # 2) Try upload(file=BytesIO(data)) without config — sometimes SDK can infer if bytes have a header and type
    if upload_fn is not None and "file" in param_names:
        try:
            logger.info("upload_file: trying upload(file=BytesIO(data)) without config")
            result = upload_fn(file=io.BytesIO(data))
            logger.info("upload_file: success via upload(file=...) -> %s", type(result))
            return result
        except Exception as e:
            last_exc = e
            logger.info("upload_file: upload(file=...) failed: %s", e)

    # 3) Try client.files.create(...) with config variants
    if create_fn is not None:
        cfg_candidates = []
        try:
            if types and hasattr(types, "UploadFileConfig"):
                try:
                    cfg_candidates.append(types.UploadFileConfig(mime_type=mime_type))
                except Exception:
                    pass
        except Exception:
            pass
        cfg_candidates.extend([{"mime_type": mime_type}, {"mime_type": mime_type, "display_name": basename}])

        for cfg in cfg_candidates:
            try:
                logger.info("upload_file: trying create(file=BytesIO(data), config=%s)", cfg)
                result = create_fn(file=io.BytesIO(data), config=cfg)
                logger.info("upload_file: success via files.create -> %s", type(result))
                return result
            except Exception as e:
                last_exc = e
                logger.info("upload_file: files.create(file=..., config=%s) failed: %s", cfg, e)

        # fallback: try create(file=BytesIO(data), filename=...) if some variants accept that
        try:
            logger.info("upload_file: trying create(file=BytesIO(data), filename=%s)", basename)
            result = create_fn(file=io.BytesIO(data), filename=basename)
            logger.info("upload_file: success via files.create(filename) -> %s", type(result))
            return result
        except Exception as e:
            last_exc = e
            logger.info("upload_file: files.create(file=..., filename=...) failed: %s", e)

    # 4) As last resort try positional path (some SDKs accept local path)
    try:
        if upload_fn is not None:
            logger.info("upload_file: trying positional path call upload(local_path) as last resort")
            result = upload_fn(local_path)
            logger.info("upload_file: success via positional path -> %s", type(result))
            return result
    except Exception as e:
        last_exc = e
        logger.info("upload_file: positional path attempt failed: %s", e)

    # Nothing worked
    sdk_info = {}
    try:
        sdk_info["client_files_dir"] = dir(files_obj)
    except Exception:
        sdk_info["client_files_dir"] = "<dir failed>"
    try:
        sdk_info["upload_signature"] = inspect.signature(upload_fn) if upload_fn is not None else None
    except Exception:
        sdk_info["upload_signature"] = "<inspect failed>"

    raise UploadFileError(
        "upload_file: failed to upload file using client.files.upload/create. "
        f"Last exception: {last_exc!r}. SDK introspection: {sdk_info}"
    )

# --------------------------------------------------------------
# GENERATION HELPERS
# --------------------------------------------------------------
def generate_text_to_video(prompt: str, model: str, resolution: str, aspect_ratio: str, duration_seconds: int) -> Dict[str, Any]:
    client = create_genai_client()
    logger.info(f"Starting text-to-video with model={model}")
    # defensive config creation
    try:
        cfg = types.GenerateVideosConfig(resolution=resolution, aspect_ratio=aspect_ratio, duration_seconds=str(duration_seconds))
    except Exception:
        cfg = {"resolution": resolution, "aspect_ratio": aspect_ratio, "duration_seconds": str(duration_seconds)}
    op = client.models.generate_videos(model=model, prompt=prompt, config=cfg)
    logger.info(f"generate_videos returned: type={type(op)} value={op}")
    operation_name = get_operation_name(op)
    logger.info(f"Operation started: {operation_name} ({type(op)})")
    return {"operation_name": operation_name, "message": "text-to-video operation started"}

def generate_image_to_video(prompt: str, image_bytes: bytes, model: str, resolution: str = "1080p", aspect_ratio: str = "16:9", duration_seconds: int = 8) -> Dict[str, Any]:
    """
    Introspection-guided image->video generation. Tries direct base64 payloads and typed constructors,
    then falls back to upload-then-generate. If all fail, dumps SDK schema via dump_generate_videos_schema().
    """
    client = create_genai_client()
    logger.info("Starting image-to-video generation (introspection-guided)")

    # prepare config defensively
    try:
        cfg = types.GenerateVideosConfig(resolution=resolution, aspect_ratio=aspect_ratio, duration_seconds=str(duration_seconds))
    except Exception:
        cfg = {"resolution": resolution, "aspect_ratio": aspect_ratio, "duration_seconds": str(duration_seconds)}

    # guess mime
    mime_type = "image/jpeg"
    try:
        if image_bytes[:8].startswith(b'\x89PNG\r\n\x1a\n'):
            mime_type = "image/png"
        elif image_bytes[:2] == b'\xff\xd8':
            mime_type = "image/jpeg"
        elif image_bytes[:4] in (b'RIFF',):
            mime_type = "image/webp"
    except Exception:
        pass

    # base64 encode once
    try:
        b64 = base64.b64encode(image_bytes).decode("ascii")
    except Exception as e:
        logger.exception("Failed to base64-encode image bytes: %s", e)
        b64 = None

    attempt_errors: List[tuple] = []

    def try_call(desc: str, fn):
        logger.info("generate_image_to_video: attempt -> %s", desc)
        try:
            res = fn()
            logger.info("generate_image_to_video: success for attempt -> %s ; result type=%s", desc, type(res))
            return res
        except Exception as e:
            logger.info("generate_image_to_video: attempt %s failed: %s", desc, e)
            logger.debug("generate_image_to_video: full exception", exc_info=True)
            attempt_errors.append((desc, e))
            return None

    # 1) Try direct typed constructors (if SDK types provide image-like classes)
    if b64 and types:
        image_type_names = [n for n in dir(types) if "Image" in n and n[0].isupper()]
        for name in image_type_names:
            typ = getattr(types, name, None)
            if not typ:
                continue
            # try common kw permutations
            for ctor_kwargs in (
                {"bytesBase64Encoded": b64, "mimeType": mime_type},
                {"bytesBase64Encoded": b64, "mime_type": mime_type},
                {"base64": b64, "mime_type": mime_type},
                {"b64": b64, "mimeType": mime_type},
                {"content": b64, "mimeType": mime_type},
            ):
                try:
                    inst = typ(**ctor_kwargs)
                except Exception as e:
                    attempt_errors.append((f"{name} constructor {ctor_kwargs}", e))
                    continue
                # try call
                res = try_call(f"generate_videos with typed image {name}", lambda inst=inst: client.models.generate_videos(model=model, prompt=prompt, image=inst, config=cfg))
                if res:
                    return {"operation_name": get_operation_name(res), "message": "image-to-video started (typed image)"}

    # 2) Try constructing a minimal dict; but **ONLY** with keys the param model accepts.
    #    We will introspect param model to learn allowed keys.
    try:
        schema_info = dump_generate_videos_schema()
        # If param_class_schema.json_schema exists, look for image subproperties
        param_schema = schema_info.get("param_class_schema") or {}
        json_schema = param_schema.get("json_schema") if isinstance(param_schema, dict) else None
        if json_schema and isinstance(json_schema, dict):
            props = json_schema.get("properties") or {}
            image_prop = props.get("image") or {}
            image_subprops = image_prop.get("properties") or {}
            allowed_keys = list(image_subprops.keys())
            logger.info("generate_image_to_video: allowed image keys per json_schema: %s", allowed_keys)
            if allowed_keys:
                candidate = {}
                for key in allowed_keys:
                    lk = key.lower()
                    if "base64" in lk or "bytes" in lk:
                        candidate[key] = b64
                    elif "mime" in lk:
                        candidate[key] = mime_type
                if candidate:
                    res = try_call("generate_videos with introspected image dict", lambda candidate=candidate: client.models.generate_videos(model=model, prompt=prompt, image=candidate, config=cfg))
                    if res:
                        return {"operation_name": get_operation_name(res), "message": "image-to-video started (introspected dict)"}
    except Exception as e:
        logger.info("generate_image_to_video: introspection attempt failed: %s", e)
        attempt_errors.append(("introspection", e))

    # 3) Fallback to upload-based approach (we already know upload_file works)
    tmp_path = f"temp_input_image_{uuid.uuid4().hex}.jpg"
    try:
        with open(tmp_path, "wb") as f:
            f.write(image_bytes)
        logger.info("generate_image_to_video: wrote temp file %s (%d bytes)", tmp_path, os.path.getsize(tmp_path))

        uploaded = try_call("upload_file(temp_path)", lambda: upload_file(client, tmp_path))
        if uploaded:
            # Try accepted forms referencing the uploaded file
            res = try_call("generate_videos with image=uploaded", lambda uploaded=uploaded: client.models.generate_videos(model=model, prompt=prompt, image=uploaded, config=cfg))
            if res:
                return {"operation_name": get_operation_name(res), "message": "image-to-video started (image=uploaded)"}

            res = try_call("generate_videos with image={'file': uploaded}", lambda uploaded=uploaded: client.models.generate_videos(model=model, prompt=prompt, image={"file": uploaded}, config=cfg))
            if res:
                return {"operation_name": get_operation_name(res), "message": "image-to-video started (image={'file': uploaded})"}

            if hasattr(uploaded, "as_image"):
                try:
                    as_img = uploaded.as_image()
                    res = try_call("generate_videos with image=uploaded.as_image()", lambda as_img=as_img: client.models.generate_videos(model=model, prompt=prompt, image=as_img, config=cfg))
                    if res:
                        return {"operation_name": get_operation_name(res), "message": "image-to-video started (image=uploaded.as_image())"}
                except Exception as e:
                    attempt_errors.append(("uploaded.as_image()", e))

            # last attempt: pass local path
            res = try_call("generate_videos with image=tmp_path", lambda tmp_path=tmp_path: client.models.generate_videos(model=model, prompt=prompt, image=tmp_path, config=cfg))
            if res:
                return {"operation_name": get_operation_name(res), "message": "image-to-video started (image=tmp_path)"}

    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
    # inside generate_image_to_video, when all earlier attempts fail:
    try:
        logger.info("generate_image_to_video: all SDK attempts failed; trying REST fallback")
        return generate_image_to_video_rest(prompt, image_bytes, model)
    except Exception as e_rest:
        logger.exception("REST fallback failed too")
        # finally raise the original error or combined error for debugging
        raise RuntimeError(f"generate_image_to_video: all attempts including REST fallback failed. rest_error={e_rest}")

    # Nothing worked — dump schema & errors, then raise
    schema_dump = dump_generate_videos_schema()
    log_lines = ["generate_image_to_video: all attempts failed. Summary of attempts/errors:"]
    for desc, exc in attempt_errors:
        log_lines.append(f"- {desc}: {repr(exc)}")
    full_msg = "\n".join(log_lines)
    logger.error(full_msg)
    logger.error("generate_image_to_video: schema_dump -> %s", schema_dump)
    raise RuntimeError(f"generate_image_to_video: generate_videos failed for all tried signatures. last_exc summary: {full_msg}")

def dump_generate_videos_schema() -> Dict[str, Any]:
    """
    Introspect SDK types to show what the GenerateVideos parameter model expects.
    Returns a dict with discovered info and logs it.
    """
    out: Dict[str, Any] = {"found": False, "notes": []}
    try:
        if not types:
            out["notes"].append("No `types` module available in this environment.")
            logger.info("dump_generate_videos_schema -> %s", out)
            return out

        # 1) Try to detect directly named parameter model
        candidates = []
        for name in dir(types):
            if "GenerateVideos" in name and ("Parameters" in name or "Args" in name or "Request" in name):
                candidates.append(name)
        out["candidates"] = candidates

        param_cls = None
        for name in ("_GenerateVideosParameters", "GenerateVideosParameters", "_GenerateVideosArgs", "GenerateVideosArgs"):
            if hasattr(types, name):
                param_cls = getattr(types, name)
                out["picked"] = name
                break

        # 2) Attempt to inspect client.models.generate_videos signature
        try:
            client = create_genai_client()
            if hasattr(client, "models") and hasattr(client.models, "generate_videos"):
                out["generate_videos_signature"] = str(inspect.signature(client.models.generate_videos))
        except Exception as e:
            out["notes"].append(f"Could not inspect client.models.generate_videos: {e!r}")

        # 3) If we located a param class, extract model_fields or json schema
        if param_cls is not None:
            schema_info = {}
            try:
                fields = getattr(param_cls, "model_fields", None)
                if fields:
                    schema_info["model_fields"] = {k: repr(v) for k, v in fields.items()}
                else:
                    # fallback to json schema
                    try:
                        schema_info["json_schema"] = param_cls.model_json_schema()
                    except Exception as e:
                        schema_info["repr"] = repr(param_cls)
            except Exception as e:
                schema_info["error_inspecting_param_cls"] = repr(e)
            out["param_class_schema"] = schema_info
            out["found"] = True
            logger.info("dump_generate_videos_schema -> %s", out)
            return out

        # 4) Fallback: enumerate pydantic-like types in types module
        pyd_models = {}
        for name in dir(types):
            obj = getattr(types, name)
            try:
                if hasattr(obj, "__pydantic_validator__") or hasattr(obj, "model_fields"):
                    # attempt to list fields
                    fields = getattr(obj, "model_fields", None)
                    if isinstance(fields, dict):
                        pyd_models[name] = list(fields.keys())
                    else:
                        # try schema
                        try:
                            schema = obj.model_json_schema()
                            pyd_models[name] = list(schema.get("properties", {}).keys())
                        except Exception:
                            pyd_models[name] = "<schema unavailable>"
            except Exception:
                continue
        out["pydantic_models_overview"] = pyd_models
        out["found"] = True
        out["notes"].append("Listed available pydantic-like types under types.*")
    except Exception as e:
        out["error"] = repr(e)

    logger.info("dump_generate_videos_schema -> %s", out)
    return out

def generate_video_from_reference_images(
    prompt: str,
    images: List[bytes],
    model: str,
    resolution: str = "1080p",
    aspect_ratio: str = "16:9",
    duration_seconds: int = 8,
) -> Dict[str, Any]:
    """
    Fallback: call the Generative Language REST long-running endpoint directly
    to start a Veo job using multiple reference images + a text prompt.

    It uses the REST JSON shape:

        instances: [
          {
            "prompt": "...",
            "referenceImages": [
              { "image": { "bytesBase64Encoded": "...", "mimeType": "image/jpeg" } },
              ...
            ]
          }
        ]

    Returns: {"operation_name": "<op>", "message": "..."}
    Raises RuntimeError on any non-2xx response with helpful message.
    """
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GENAI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )
    if not api_key:
        raise RuntimeError(
            "No GEMINI_API_KEY/GENAI_API_KEY/GOOGLE_API_KEY set in environment "
            "for REST reference-images call"
        )

    if not images:
        raise RuntimeError("generate_video_from_reference_images_rest: no images provided")

    # Build URL for predictLongRunning
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predictLongRunning"
    params = {"key": api_key}
    headers = {"Content-Type": "application/json"}

    # Build referenceImages payload
    ref_images_payload = []
    for img_bytes in images:
        # minimal mime type guessing
        mime_type = "image/jpeg"
        try:
            if img_bytes[:8].startswith(b"\x89PNG\r\n\x1a\n"):
                mime_type = "image/png"
            elif img_bytes[:2] == b"\xff\xd8":
                mime_type = "image/jpeg"
            elif img_bytes[:4] == b"RIFF":
                mime_type = "image/webp"
        except Exception:
            pass

        b64 = base64.b64encode(img_bytes).decode("ascii")
        ref_images_payload.append(
            {
                "image": {
                    "bytesBase64Encoded": b64,
                    "mimeType": mime_type,
                }
            }
        )

    # Build top-level instance
    instance = {
        "prompt": prompt,
        "referenceImages": ref_images_payload,
    }

    body = {
        "instances": [instance],
        "parameters": {
            "aspectRatio": aspect_ratio,
            "durationSeconds": duration_seconds,
            # "resolution": resolution # resolution might not be supported in REST parameters for all models, but we can try
        }
    }

    try:
        logger.info(
            "generate_video_from_reference_images_rest: POST %s (model=%s, refs=%d)",
            url,
            model,
            len(ref_images_payload),
        )
        resp = requests.post(
            url,
            params=params,
            headers=headers,
            data=json.dumps(body),
            timeout=300,
        )
    except requests.RequestException as e:
        logger.exception("generate_video_from_reference_images_rest: HTTP request failed")
        raise RuntimeError(f"REST request failed: {e}")

    # Parse response JSON
    try:
        j = resp.json()
    except Exception:
        raise RuntimeError(
            f"REST call returned non-JSON: status={resp.status_code} text={resp.text}"
        )

    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"REST predictLongRunning (referenceImages) failed: "
            f"status={resp.status_code} body={j}"
        )

    op_name = j.get("name") or j.get("operation") or j.get("operation_name")
    if not op_name:
        raise RuntimeError(
            f"REST (referenceImages) succeeded but no operation name returned: {j}"
        )

    logger.info("generate_video_from_reference_images_rest: started operation %s", op_name)
    return {"operation_name": op_name, "message": "reference-image video started (via REST)"}

def generate_video_from_first_last_frames(
    prompt: str,
    first: bytes,
    last: bytes,
    model: str,
    resolution: str = "1080p",
    aspect_ratio: str = "16:9",
    duration_seconds: int = 8,
) -> Dict[str, Any]:
    """
    Call the Generative Language REST long-running endpoint directly
    to start a Veo job using FIRST + LAST frame images + a text prompt.

    Uses shape (approx):

        instances: [
          {
            "prompt": "...",
            "image": { "bytesBase64Encoded": "<first>", "mimeType": "image/jpeg" },
            "lastFrame": { "bytesBase64Encoded": "<last>", "mimeType": "image/jpeg" }
          }
        ]

    Returns: {"operation_name": "<op>", "message": "..."}
    Raises RuntimeError on any non-2xx response with helpful message.
    """
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GENAI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )
    if not api_key:
        raise RuntimeError(
            "No GEMINI_API_KEY/GENAI_API_KEY/GOOGLE_API_KEY set in environment "
            "for REST first+last-frames call"
        )

    if not first or not last:
        raise RuntimeError("generate_video_from_first_last_frames_rest: both first and last images are required")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predictLongRunning"
    params = {"key": api_key}
    headers = {"Content-Type": "application/json"}

    # Small helper to guess mime type
    def _guess_mime(img: bytes) -> str:
        m = "image/jpeg"
        try:
            if img[:8].startswith(b"\x89PNG\r\n\x1a\n"):
                m = "image/png"
            elif img[:2] == b"\xff\xd8":
                m = "image/jpeg"
            elif img[:4] == b"RIFF":
                m = "image/webp"
        except Exception:
            pass
        return m

    first_mime = _guess_mime(first)
    last_mime = _guess_mime(last)

    first_b64 = base64.b64encode(first).decode("ascii")
    last_b64 = base64.b64encode(last).decode("ascii")

    # Build instance as the REST API expects
    instance = {
        "prompt": prompt,
        # "image" is used for the first frame
        "image": {
            "bytesBase64Encoded": first_b64,
            "mimeType": first_mime,
        },
        # "lastFrame" describes the last frame
        "lastFrame": {
            "bytesBase64Encoded": last_b64,
            "mimeType": last_mime,
        },
    }

    body = {
        "instances": [instance],
        "parameters": {
            "aspectRatio": aspect_ratio,
            "durationSeconds": duration_seconds,
        }
    }

    try:
        logger.info(
            "generate_video_from_first_last_frames_rest: POST %s (model=%s)",
            url,
            model,
        )
        resp = requests.post(
            url,
            params=params,
            headers=headers,
            data=json.dumps(body),
            timeout=300,
        )
    except requests.RequestException as e:
        logger.exception("generate_video_from_first_last_frames_rest: HTTP request failed")
        raise RuntimeError(f"REST request failed: {e}")

    try:
        j = resp.json()
    except Exception:
        raise RuntimeError(
            f"REST call (first+last) returned non-JSON: status={resp.status_code} text={resp.text}"
        )

    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"REST predictLongRunning (first+last) failed: status={resp.status_code} body={j}"
        )

    op_name = j.get("name") or j.get("operation") or j.get("operation_name")
    if not op_name:
        raise RuntimeError(
            f"REST (first+last) succeeded but no operation name returned: {j}"
        )

    logger.info("generate_video_from_first_last_frames_rest: started operation %s", op_name)
    return {
        "operation_name": op_name,
        "message": "first+last-frame video started (via REST)",
    }

def _find_candidate_video_types():
    """
    Inspect the `types` module (SDK types) and return a list of candidate classes that might represent
    a 'generated video' type or input video wrapper. We search for names containing 'Generated' or 'Video'.
    """
    candidates = []
    try:
        for name in dir(types):
            if ("Video" in name or "Generated" in name) and name[0].isupper():
                obj = getattr(types, name, None)
                # skip simple aliases and typing.Union objects
                if inspect.isclass(obj):
                    candidates.append((name, obj))
    except Exception as e:
        logger.debug("video-type-introspect failed: %s", e)
    return candidates

def _try_construct_typed_video(candidate_cls, uploaded_or_file_obj):
    """
    Attempt to construct an instance of candidate_cls from the uploaded File object (or dict).
    We'll try several safe methods:
      - If candidate_cls has model_validate (pydantic style), use model_validate(uploaded_or_file_obj, from_attributes=True)
      - Try candidate_cls(file=uploaded_or_file_obj) and similar common kw names
      - Try to pass {'file': uploaded_or_file_obj} into candidate_cls.model_validate / constructor
    Return constructed instance or raise exception.
    """
    last_exc = None
    try:
        # If candidate class exposes pydantic validators
        if hasattr(candidate_cls, "model_validate"):
            try:
                # try from_attributes first (extract attributes)
                inst = candidate_cls.model_validate(uploaded_or_file_obj, from_attributes=True)
                return inst
            except Exception as e:
                last_exc = e
            try:
                # try direct dict (if uploaded is dict or has model_dump)
                obj_dict = None
                if isinstance(uploaded_or_file_obj, dict):
                    obj_dict = uploaded_or_file_obj
                elif hasattr(uploaded_or_file_obj, "model_dump"):
                    obj_dict = uploaded_or_file_obj.model_dump()
                elif hasattr(uploaded_or_file_obj, "to_dict"):
                    obj_dict = uploaded_or_file_obj.to_dict()
                if obj_dict is not None:
                    inst = candidate_cls.model_validate(obj_dict)
                    return inst
            except Exception as e:
                last_exc = e

        # Try calling constructor with common kw param 'file' or 'video' or 'video_file'
        for kw in ("file", "video", "video_file", "input"):
            try:
                inst = candidate_cls(**{kw: uploaded_or_file_obj})
                return inst
            except Exception as e:
                last_exc = e

        # Finally try to call with the uploaded object itself
        try:
            inst = candidate_cls(uploaded_or_file_obj)
            return inst
        except Exception as e:
            last_exc = e

    except Exception as e:
        last_exc = e

    # If we arrive here, we could not construct
    raise RuntimeError(f"_try_construct_typed_video failed for {candidate_cls} last_exc={last_exc}")

def extend_veo_video(prompt: str, video_bytes: bytes, model: str, prior_generated_video_obj: Optional[Any] = None, resolution: str = "1080p", aspect_ratio: str = "16:9", duration_seconds: int = 8) -> Dict[str, Any]:
    """
    Attempt to extend a video.

    Preferred flows:
      1) If you already have a generated-video object (like operation.response.generated_videos[0].video),
         pass it in via `prior_generated_video_obj` and we will call SDK directly (this is guaranteed by docs).
      2) Otherwise, we attempt to upload a local file and *construct* the SDK expected generated-video typed object
         by introspecting `types.*` classes and trying safe constructors. This is best-effort.
      3) If we cannot construct a typed instance, we raise a clear error instructing the user to provide a
         prior generated video object (per docs) or show how to produce one (generate a short dummy video first).

    Returns: {"operation_name": "...", "message": "..."}
    """

    client = create_genai_client()
    logger.info("Starting Veo video extension (doc-compliant flow)")

    # 1) If caller supplied a prior generated-video object (from a previous operation), use it directly
    if prior_generated_video_obj is not None:
        logger.info("extend_veo_video: Using prior generated video object supplied by caller (official doc flow).")
        try:
            op = client.models.generate_videos(model=model, video=prior_generated_video_obj, prompt=prompt)
            return {"operation_name": get_operation_name(op), "message": "video-extend started (using prior generated-video object)"}
        except Exception as e:
            logger.exception("extend_veo_video: SDK generate_videos failed with prior_generated_video_obj: %s", e)
            raise RuntimeError(f"extend_veo_video: SDK generate_videos with provided prior_generated_video_obj failed: {e}")

    # 2) No prior generated-video object: upload the local file and then attempt to construct a typed object
    tmp_path = f"temp_video_input_{uuid.uuid4().hex}.mp4"
    try:
        with open(tmp_path, "wb") as fh:
            fh.write(video_bytes)
        logger.info("extend_veo_video: wrote temp video %s (%d bytes)", tmp_path, os.path.getsize(tmp_path))

        # upload into GenAI files (we already have robust upload_file)
        uploaded = upload_file(client, tmp_path)
        logger.info("extend_veo_video: uploaded file object type=%s", type(uploaded))

        # Try SDK direct with uploaded first (some versions accept a File object directly)
        try:
            # Try a minimal SDK call with no extra config to avoid injection of 'encoding' or 'mimeType'
            op = client.models.generate_videos(model=model, video=uploaded, prompt=prompt, config={})
            return {"operation_name": get_operation_name(op), "message": "video-extend started (sdk: uploaded File accepted)"}
        except Exception as e:
            logger.info("extend_veo_video: SDK did not accept uploaded File object directly: %s", e)

        # Next: inspect SDK types and attempt to find the 'generated video' class and construct one
        candidates = _find_candidate_video_types()
        logger.info("extend_veo_video: candidate video types found: %s", [n for n, _ in candidates])

        typed_instance = None
        last_error = None
        for name, cls in candidates:
            try:
                logger.info("extend_veo_video: trying to construct typed instance for %s", name)
                inst = _try_construct_typed_video(cls, uploaded)
                # If constructed, attempt SDK call with it (minimal config)
                try:
                    op = client.models.generate_videos(model=model, video=inst, prompt=prompt, config={})
                    return {"operation_name": get_operation_name(op), "message": f"video-extend started (sdk typed {name})"}
                except Exception as e:
                    last_error = e
                    logger.info("extend_veo_video: SDK rejected typed instance of %s: %s", name, e)
            except Exception as e:
                last_error = e
                logger.info("extend_veo_video: could not construct typed instance for %s: %s", name, e)

        # If we reach here: no typed construction succeeded. According to docs, the model expects a
        # *generated-video object produced by the model itself*. So we must ask the user to follow the docs.
        raise RuntimeError(
            "extend_veo_video: Could not produce a proper 'generated-video' object from your local file. "
            "Per Veo docs you must pass a video object returned by a previous generate_videos call (e.g. "
            "`operation.response.generated_videos[0].video`).\n\n"
            "Two options:\n"
            " 1) If you actually have an earlier operation result, pass that object into this function as "
            "`prior_generated_video_obj` (preferred). Example flow in docs:\n"
            "     op = client.models.generate_videos(...)\n"
            "     prior_video = op.response.generated_videos[0].video\n"
            "     extend_veo_video(prompt, video_bytes=None, model=model, prior_generated_video_obj=prior_video)\n\n"
            " 2) If you only have a local video file and want to extend it, first *generate* a short video from it "
            "via the model's supported input flow (for example, use an initial generation that references the file "
            "and produces a generated_video object). Then pass the generated object's `.video` to this function.\n\n"
            f"Last SDK/attempt error: {last_error}"
        )

    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

def extend_veo_video_rest(prompt: str, video_bytes: Optional[bytes], model: str, file_reference: Optional[Dict[str,str]] = None) -> Dict[str, Any]:
    """
    Simpler REST helper: if file_reference provided, try a couple of standard shapes; if not, embed base64.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("No GEMINI_API_KEY/GENAI_API_KEY/GOOGLE_API_KEY set for REST fallback")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predictLongRunning"
    headers = {"Content-Type": "application/json"}

    if file_reference:
        variants = [
            {"video": file_reference, "prompt": prompt},
            {"video": {"name": file_reference.get("name")}, "prompt": prompt} if file_reference.get("name") else None,
            {"video": {"gcsUri": file_reference.get("gcsUri")}, "prompt": prompt} if file_reference.get("gcsUri") else None,
            {"video": {"uri": file_reference.get("uri")}, "prompt": prompt} if file_reference.get("uri") else None,
            {"video": {"file": file_reference}, "prompt": prompt}
        ]
        variants = [v for v in variants if v is not None]
        last_resp = None
        for inst in variants:
            body = {"instances": [inst]}
            logger.info("extend_veo_video_rest: trying variant keys=%s", list(inst.keys()))
            resp = requests.post(url, params={"key": api_key}, headers=headers, data=json.dumps(body), timeout=300)
            try:
                j = resp.json()
            except Exception:
                raise RuntimeError(f"REST call returned non-JSON: status={resp.status_code} text={resp.text}")
            if resp.status_code in (200,201):
                op_name = j.get("name") or j.get("operation") or j.get("operation_name")
                if not op_name:
                    raise RuntimeError(f"REST succeeded but no operation name returned: {j}")
                logger.info("extend_veo_video_rest: started operation %s", op_name)
                return {"operation_name": op_name, "message": "video-extend started (via REST file-ref helper)"}
            last_resp = (resp.status_code, j)
            logger.info("extend_veo_video_rest: variant rejected status=%s body=%s", resp.status_code, j)
        raise RuntimeError(f"REST file-ref attempts all rejected; last status/body: {last_resp}")
    # embed base64
    if not video_bytes:
        raise RuntimeError("extend_veo_video_rest: no video bytes to send and no file_reference provided")
    b64 = base64.b64encode(video_bytes).decode("ascii")
    instance = {"video": {"bytesBase64Encoded": b64, "mimeType": "video/mp4"}, "prompt": prompt}
    body = {"instances": [instance]}
    logger.info("extend_veo_video_rest: POST embed payload model=%s size=%d", model, len(b64))
    resp = requests.post(url, params={"key": api_key}, headers=headers, data=json.dumps(body), timeout=300)
    try:
        j = resp.json()
    except Exception:
        raise RuntimeError(f"REST call returned non-JSON: status={resp.status_code} text={resp.text}")
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"REST predictLongRunning failed: status={resp.status_code} body={j}")
    op_name = j.get("name") or j.get("operation") or j.get("operation_name")
    if not op_name:
        raise RuntimeError(f"REST succeeded but no operation name returned: {j}")
    return {"operation_name": op_name, "message": "video-extend started (via REST base64)"}

# --------------------------------------------------------------
# ASYNC / POLLING / DOWNLOAD
# --------------------------------------------------------------
def handle_async_operation(operation_name: str) -> Dict[str, Any]:
    client = create_genai_client()
    logger.info(f"Checking async operation {operation_name}")
    try:
        op = client.operations.get(operation_name)
    except Exception as e:
        try:
            if types and hasattr(types, "GenerateVideosOperation"):
                op = client.operations.get(types.GenerateVideosOperation(name=operation_name))
            else:
                raise
        except Exception as e2:
            logger.exception("handle_async_operation: failed to fetch operation object")
            return {"done": False, "message": f"failed to fetch operation: {e2}", "raw": str(e2)}

    if isinstance(op, str):
        logger.info(f"handle_async_operation: operations.get returned str -> {op}")
        return {"done": False, "message": "operation represented as string; check later", "raw": op}

    done = bool(getattr(op, "done", False))
    if done:
        return {"done": True, "message": "operation complete", "raw": str(op)}
    return {"done": False, "message": "operation still running", "raw": str(op)}

def get_operation_status(operation_name: str) -> Dict[str, Any]:
    client = create_genai_client()
    try:
        op = client.operations.get(operation_name)
    except Exception as e:
        try:
            if types and hasattr(types, "GenerateVideosOperation"):
                op = client.operations.get(types.GenerateVideosOperation(name=operation_name))
            else:
                raise
        except Exception as e2:
            logger.exception("get_operation_status: failed to get operation")
            return {"done": False, "status": "ERROR", "progress": None, "eta_seconds": None, "message": f"failed to get operation: {e2}", "raw": None}

    if isinstance(op, str):
        logger.info(f"get_operation_status: operations.get returned str -> {op}")
        return {
            "done": False,
            "status": "POLLING",
            "progress": None,
            "eta_seconds": None,
            "message": f"operation represented as string: {op}",
            "raw": op,
        }

    try:
        done = bool(getattr(op, "done", False))
        meta = getattr(op, "metadata", None)
        progress = None
        eta_seconds = None
        if meta:
            if isinstance(meta, dict):
                progress = meta.get("progress_percent") or meta.get("progress") or meta.get("percent")
                eta_seconds = meta.get("eta_seconds") or meta.get("estimated_seconds") or meta.get("eta")
            else:
                progress = getattr(meta, "progress_percent", None) or getattr(meta, "progress", None) or getattr(meta, "percent", None)
                eta_seconds = getattr(meta, "eta_seconds", None) or getattr(meta, "estimated_seconds", None) or getattr(meta, "eta", None)
            if progress is not None:
                try:
                    progress = int(progress)
                except Exception:
                    pass
        raw = str(op)
        return {
            "done": done,
            "status": "COMPLETE" if done else "POLLING",
            "progress": progress,
            "eta_seconds": eta_seconds,
            "message": "operation complete" if done else f"progress={progress} eta={eta_seconds}",
            "raw": raw
        }
    except Exception as e:
        logger.exception("get_operation_status: unexpected error while parsing operation object")
        return {"done": False, "status": "ERROR", "progress": None, "eta_seconds": None, "message": str(e), "raw": str(op)}

def download_video_bytes(operation_name: str) -> Tuple[Optional[bytes], Optional[str]]:
    client = create_genai_client()
    try:
        op = client.operations.get(operation_name)
    except Exception:
        try:
            if types and hasattr(types, "GenerateVideosOperation"):
                op = client.operations.get(types.GenerateVideosOperation(name=operation_name))
            else:
                raise
        except Exception as e:
            logger.error(f"download_video_bytes: failed to get operation: {e}")
            return None, None

    if isinstance(op, str):
        logger.info(f"download_video_bytes: operations.get returned str -> {op}")
        return None, None

    if not bool(getattr(op, "done", False)):
        logger.info(f"download_video_bytes: operation {operation_name} not done yet")
        return None, None

    resp = getattr(op, "response", None) or getattr(op, "result", None)
    if not resp:
        logger.info(f"download_video_bytes: operation {operation_name} has no response/result")
        return None, None

    videos = getattr(resp, "generated_videos", None)
    if not videos:
        logger.info(f"download_video_bytes: operation {operation_name} has no generated_videos")
        return None, None

    video_obj = videos[0]
    try:
        downloaded = client.files.download(file=video_obj.video)
    except Exception as e1:
        logger.warning(f"download_video_bytes: first download attempt failed: {e1}")
        try:
            downloaded = client.files.download(video_obj.video)
        except Exception as e2:
            logger.error(f"download_video_bytes: second download attempt failed: {e2}")
            return None, None

    if hasattr(downloaded, "read"):
        data = downloaded.read()
    else:
        data = bytes(downloaded)
    filename = f"video_{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.mp4"
    return data, filename

def generate_image_to_video_rest(prompt: str, image_bytes: bytes, model: str) -> Dict[str, Any]:
    """
    Fallback: call the Generative Language REST long-running endpoint directly
    to start a Veo job using a single image + a text prompt.
    """
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GENAI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )
    if not api_key:
        raise RuntimeError(
            "No GEMINI_API_KEY/GENAI_API_KEY/GOOGLE_API_KEY set in environment "
            "for REST image-to-video call"
        )

    if not image_bytes:
        raise RuntimeError("generate_image_to_video_rest: no image provided")

    # Build URL for predictLongRunning
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predictLongRunning"
    params = {"key": api_key}
    headers = {"Content-Type": "application/json"}

    # minimal mime type guessing
    mime_type = "image/jpeg"
    try:
        if image_bytes[:8].startswith(b"\x89PNG\r\n\x1a\n"):
            mime_type = "image/png"
        elif image_bytes[:2] == b"\xff\xd8":
            mime_type = "image/jpeg"
        elif image_bytes[:4] == b"RIFF":
            mime_type = "image/webp"
    except Exception:
        pass

    b64 = base64.b64encode(image_bytes).decode("ascii")

    # Build instance
    instance = {
        "prompt": prompt,
        "image": {
            "bytesBase64Encoded": b64,
            "mimeType": mime_type,
        }
    }

    body = {
        "instances": [instance],
        "parameters": {
            "aspectRatio": "16:9",   # Default, can be parameterized if needed
            "durationSeconds": 8     # Default
        }
    }

    try:
        logger.info(
            "generate_image_to_video_rest: POST %s (model=%s)",
            url,
            model,
        )
        resp = requests.post(
            url,
            params=params,
            headers=headers,
            data=json.dumps(body),
            timeout=300,
        )
    except requests.RequestException as e:
        logger.exception("generate_image_to_video_rest: HTTP request failed")
        raise RuntimeError(f"REST request failed: {e}")

    # Parse response JSON
    try:
        j = resp.json()
    except Exception:
        raise RuntimeError(
            f"REST call returned non-JSON: status={resp.status_code} text={resp.text}"
        )

    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"REST predictLongRunning (image-to-video) failed: "
            f"status={resp.status_code} body={j}"
        )

    op_name = j.get("name") or j.get("operation") or j.get("operation_name")
    if not op_name:
        raise RuntimeError(
            f"REST (image-to-video) succeeded but no operation name returned: {j}"
        )

    logger.info("generate_image_to_video_rest: started operation %s", op_name)
    return {"operation_name": op_name, "message": "image-to-video operation started (via REST)"}

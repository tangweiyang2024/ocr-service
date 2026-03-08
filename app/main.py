from __future__ import annotations

import io
import os
from pathlib import Path
from typing import Any
import asyncio

import pytesseract
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image, ImageFilter, ImageOps, UnidentifiedImageError

app = FastAPI(title="OCR API", version="1.0.0")

DEFAULT_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(DEFAULT_TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = DEFAULT_TESSERACT_PATH

LOCAL_TESSDATA_DIR = Path(__file__).resolve().parent.parent / "tessdata"
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
MAX_UPLOAD_BYTES = int(os.getenv("OCR_MAX_UPLOAD_BYTES", str(8 * 1024 * 1024)))
MAX_IMAGE_PIXELS = int(os.getenv("OCR_MAX_IMAGE_PIXELS", str(16_000_000)))
MAX_OCR_CONCURRENCY = int(os.getenv("OCR_MAX_CONCURRENCY", "1"))
OCR_TIMEOUT_SECONDS = int(os.getenv("OCR_TIMEOUT_SECONDS", "25"))
OCR_QUEUE_WAIT_SECONDS = int(os.getenv("OCR_QUEUE_WAIT_SECONDS", "4"))
OCR_MAX_SIDE = int(os.getenv("OCR_MAX_SIDE", "2200"))
OCR_DEFAULT_PSM = int(os.getenv("OCR_DEFAULT_PSM", "6"))
OCR_SEMAPHORE = asyncio.Semaphore(max(1, MAX_OCR_CONCURRENCY))

# Guard against decompression bombs and overly large images.
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def web_index() -> FileResponse:
    index_file = WEB_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index page not found")
    return FileResponse(index_file)


def _preprocess(image: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(image)
    # A light sharpen + auto-contrast usually improves OCR on low-quality screenshots.
    enhanced = ImageOps.autocontrast(gray.filter(ImageFilter.SHARPEN))
    return enhanced


def _downscale_large_image(image: Image.Image) -> Image.Image:
    max_side = max(image.width, image.height)
    if max_side <= OCR_MAX_SIDE:
        return image

    ratio = OCR_MAX_SIDE / max_side
    new_size = (max(1, int(image.width * ratio)), max(1, int(image.height * ratio)))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def _validate_lang(lang: str) -> str:
    cleaned = (lang or "").strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="lang is required")

    tokens = [token.strip() for token in cleaned.split("+") if token.strip()]
    if not tokens:
        raise HTTPException(status_code=400, detail="invalid lang format")

    if LOCAL_TESSDATA_DIR.exists():
        missing = [
            token
            for token in tokens
            if not (LOCAL_TESSDATA_DIR / f"{token}.traineddata").exists()
        ]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"missing traineddata for: {', '.join(missing)}",
            )

    return "+".join(tokens)


def _ocr_image(image: Image.Image, lang: str, ocr_config: str) -> str:
    return pytesseract.image_to_string(
        image,
        lang=lang,
        config=ocr_config,
        timeout=OCR_TIMEOUT_SECONDS,
    )


@app.post("/api/recognize")
@app.post("/ocr/recognize")
async def recognize_text(
    file: UploadFile = File(...),
    lang: str = Form("chi_sim+eng"),
    preprocess: bool = Form(True),
    psm: int = Form(OCR_DEFAULT_PSM),
) -> dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="file is required")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="empty file")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"file too large (max {MAX_UPLOAD_BYTES} bytes)",
        )

    try:
        image = Image.open(io.BytesIO(content))
        image.load()
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="unsupported image format") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"invalid image: {exc}") from exc

    if image.width * image.height > MAX_IMAGE_PIXELS:
        raise HTTPException(
            status_code=413,
            detail=f"image too large (max {MAX_IMAGE_PIXELS} pixels)",
        )

    image = _downscale_large_image(image)

    if preprocess:
        image = _preprocess(image)

    safe_lang = _validate_lang(lang)
    if psm < 0 or psm > 13:
        raise HTTPException(status_code=400, detail="psm must be between 0 and 13")

    ocr_config = ""
    if LOCAL_TESSDATA_DIR.exists():
        ocr_config = f"--tessdata-dir {LOCAL_TESSDATA_DIR.as_posix()}"
    ocr_config = f"{ocr_config} --psm {psm}".strip()

    try:
        await asyncio.wait_for(OCR_SEMAPHORE.acquire(), timeout=OCR_QUEUE_WAIT_SECONDS)
        try:
            text = await asyncio.to_thread(_ocr_image, image, safe_lang, ocr_config)
        finally:
            OCR_SEMAPHORE.release()
    except asyncio.TimeoutError as exc:
        raise HTTPException(
            status_code=429,
            detail="server is busy, please retry later",
        ) from exc
    except pytesseract.TesseractNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="tesseract executable not found on server",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=408, detail=f"ocr timeout: {exc}") from exc
    except pytesseract.TesseractError as exc:
        raise HTTPException(status_code=400, detail=f"ocr failed: {exc}") from exc

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return {
        "filename": file.filename,
        "lang": safe_lang,
        "psm": psm,
        "text": text.strip(),
        "lines": lines,
        "line_count": len(lines),
    }

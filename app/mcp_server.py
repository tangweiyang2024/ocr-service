from __future__ import annotations

import json
import mimetypes
import os
import uuid
import base64
from pathlib import Path
from typing import Any
from urllib import error, request

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import TransportSecuritySettings

MCP_NAME = os.getenv("OCR_MCP_NAME", "ocr-service")
OCR_API_BASE = os.getenv("OCR_API_BASE", "http://api.cstwy.top").rstrip("/")
MAX_UPLOAD_BYTES = int(os.getenv("OCR_MAX_UPLOAD_BYTES", str(8 * 1024 * 1024)))
MCP_TRANSPORT = os.getenv("OCR_MCP_TRANSPORT", "streamable-http")
MCP_HOST = os.getenv("OCR_MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("OCR_MCP_PORT", "19000"))
MCP_STREAMABLE_HTTP_PATH = os.getenv("OCR_MCP_PATH", "/mcp")
MCP_ALLOWED_HOSTS = os.getenv(
    "OCR_MCP_ALLOWED_HOSTS",
    "127.0.0.1:*,localhost:*,api.cstwy.top:*",
).split(",")
MCP_ALLOWED_ORIGINS = os.getenv(
    "OCR_MCP_ALLOWED_ORIGINS",
    "http://127.0.0.1:*,http://localhost:*,http://api.cstwy.top",
).split(",")

mcp = FastMCP(
    MCP_NAME,
    host=MCP_HOST,
    port=MCP_PORT,
    streamable_http_path=MCP_STREAMABLE_HTTP_PATH,
    stateless_http=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
        allowed_hosts=MCP_ALLOWED_HOSTS,
        allowed_origins=MCP_ALLOWED_ORIGINS,
    ),
)


def _build_multipart_body_from_bytes(
    file_name: str, file_bytes: bytes, lang: str, preprocess: bool, psm: int
) -> tuple[bytes, str]:
    boundary = f"----ocr-mcp-{uuid.uuid4().hex}"
    line_break = b"\r\n"
    content_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

    parts: list[bytes] = []

    def add_text(name: str, value: str) -> None:
        parts.extend(
            [
                f"--{boundary}".encode(),
                f'Content-Disposition: form-data; name="{name}"'.encode(),
                b"",
                value.encode("utf-8"),
            ]
        )

    add_text("lang", lang)
    add_text("preprocess", "true" if preprocess else "false")
    add_text("psm", str(psm))

    parts.extend(
        [
            f"--{boundary}".encode(),
            (
                f'Content-Disposition: form-data; name="file"; '
                f'filename="{file_name}"'
            ).encode(),
            f"Content-Type: {content_type}".encode(),
            b"",
            file_bytes,
            f"--{boundary}--".encode(),
            b"",
        ]
    )

    body = line_break.join(parts)
    return body, boundary


def _build_multipart_body(
    file_path: Path, lang: str, preprocess: bool, psm: int
) -> tuple[bytes, str]:
    return _build_multipart_body_from_bytes(
        file_name=file_path.name,
        file_bytes=file_path.read_bytes(),
        lang=lang,
        preprocess=preprocess,
        psm=psm,
    )


def _post_ocr(file_path: Path, lang: str, preprocess: bool, psm: int) -> dict[str, Any]:
    body, boundary = _build_multipart_body(file_path, lang, preprocess, psm)
    req = request.Request(
        f"{OCR_API_BASE}/api/recognize",
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )

    try:
        with request.urlopen(req, timeout=60) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload)
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OCR API HTTP {exc.code}: {details}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Cannot connect OCR API: {exc}") from exc


def _post_ocr_bytes(
    file_name: str, file_bytes: bytes, lang: str, preprocess: bool, psm: int
) -> dict[str, Any]:
    body, boundary = _build_multipart_body_from_bytes(
        file_name=file_name,
        file_bytes=file_bytes,
        lang=lang,
        preprocess=preprocess,
        psm=psm,
    )
    req = request.Request(
        f"{OCR_API_BASE}/api/recognize",
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )

    try:
        with request.urlopen(req, timeout=60) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload)
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OCR API HTTP {exc.code}: {details}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Cannot connect OCR API: {exc}") from exc


@mcp.tool()
def ocr_health() -> dict[str, Any]:
    """Check OCR API health status."""
    url = f"{OCR_API_BASE}/health"
    try:
        with request.urlopen(url, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            return {"ok": True, "api_base": OCR_API_BASE, "response": payload}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "api_base": OCR_API_BASE, "error": str(exc)}


@mcp.tool()
def ocr_recognize_file(
    file_path: str,
    lang: str = "chi_sim+eng",
    preprocess: bool = True,
    psm: int = 6,
) -> dict[str, Any]:
    """Recognize text from image path on MCP server filesystem (remote host)."""
    path = Path(file_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise ValueError(
            "file not found on MCP server filesystem: "
            f"{file_path}. If this is your local client path, use "
            "ocr_recognize_base64 instead."
        )

    file_size = path.stat().st_size
    if file_size > MAX_UPLOAD_BYTES:
        raise ValueError(f"file too large: {file_size} > {MAX_UPLOAD_BYTES} bytes")

    result = _post_ocr(path, lang=lang, preprocess=preprocess, psm=psm)
    result["local_file_path"] = str(path)
    result["file_size"] = file_size
    return result


@mcp.tool()
def ocr_recognize_base64(
    file_name: str,
    image_base64: str,
    lang: str = "chi_sim+eng",
    preprocess: bool = True,
    psm: int = 6,
) -> dict[str, Any]:
    """Recognize text from base64 image data uploaded by MCP client."""
    if not file_name.strip():
        raise ValueError("file_name is required")
    if not image_base64.strip():
        raise ValueError("image_base64 is required")

    try:
        file_bytes = base64.b64decode(image_base64, validate=True)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"invalid base64 content: {exc}") from exc

    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError(f"file too large: {len(file_bytes)} > {MAX_UPLOAD_BYTES} bytes")

    result = _post_ocr_bytes(
        file_name=file_name,
        file_bytes=file_bytes,
        lang=lang,
        preprocess=preprocess,
        psm=psm,
    )
    result["local_file_path"] = None
    result["file_size"] = len(file_bytes)
    result["uploaded_via"] = "base64"
    return result


if __name__ == "__main__":
    mcp.run(transport=MCP_TRANSPORT)

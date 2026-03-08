---
name: ocr
description: OCR images through ocr-service MCP. Accept short prompts like "/ocr path/to/img.png" or "recognize xxx.png".
---

# OCR Skill (Codex)

Use this skill whenever the user asks to recognize text from an image.

## Supported user prompt styles
- `/ocr D:/path/image.png`
- `recognize D:/path/image.png`
- `识别 D:/path/image.png 图片`

The user does NOT need to provide OCR parameters unless they want custom behavior.

## Default behavior (accuracy first)
- `lang = chi_sim+eng`
- `preprocess = true`
- `psm = 6`

## Required tool sequence
1. Call `mcp__ocr-service__ocr_health` first.
2. Determine image location:
   - If image path is accessible on MCP server filesystem, call `mcp__ocr-service__ocr_recognize_file`.
   - If image is only on client/local machine, read bytes locally, convert to base64, and call `mcp__ocr-service__ocr_recognize_base64`.
3. Return OCR text and line count.

## Path handling rules
- Local Windows paths like `D:\\...` usually are NOT accessible by remote MCP server.
- For local paths, prefer `ocr_recognize_base64`.
- Use original filename as `file_name` when calling base64 tool.

## Optional overrides
If user explicitly gives values, override defaults:
- `lang`
- `preprocess`
- `psm`

## Response format
- Brief summary line: success/failure.
- OCR result text.
- Meta: `line_count`, `lang`, `preprocess`, `psm`, and which MCP tool was used.

## Error handling
- `file not found`: switch from file-path mode to base64 mode.
- `invalid image`: verify file integrity and full base64 payload.
- timeout/5xx: retry once, then suggest smaller/cropped image.

## Security note
Images are sent to remote OCR service via MCP server endpoint `http://api.cstwy.top/mcp`.
Avoid uploading sensitive images unless user confirms.
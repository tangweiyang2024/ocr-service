# MCP Client Setup And Verification

This document explains how to add the OCR MCP server in both Codex and Claude Code, then verify end-to-end calls.

Server endpoint:
- `http://api.cstwy.top/mcp`

Recommended OCR defaults (accuracy first):
- `lang=chi_sim+eng`
- `preprocess=true`
- `psm=6`

## 1) Codex: add OCR MCP

Add server:

```bash
codex mcp add ocr-service --url http://api.cstwy.top/mcp
```

Verify config:

```bash
codex mcp list --json
codex mcp get ocr-service --json
```

Expected:
- server name is `ocr-service`
- `enabled=true`
- transport is `streamable_http`
- URL is `http://api.cstwy.top/mcp`

## 2) Claude Code: add OCR MCP

Add server:

```bash
claude mcp add --transport http ocr-service http://api.cstwy.top/mcp
```

Verify config:

```bash
claude mcp list
claude mcp get ocr-service
```

Expected:
- `ocr-service` appears in list
- transport is HTTP
- URL is `http://api.cstwy.top/mcp`

## 3) Health verification (MCP tool level)

In Codex or Claude conversation, call:
- `ocr_health`

Expected response:
- `ok: true`
- `api_base: http://api.cstwy.top`

## 4) OCR verification flow

Two modes:

1. `ocr_recognize_file`
- Use only when the image path is on MCP server filesystem (remote host path).

2. `ocr_recognize_base64` (recommended)
- Use when image is on your local machine.
- Convert local image to base64 and send `file_name + image_base64`.

### Local base64 example (PowerShell)

```powershell
$b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("D:\study\ocr-service\test2.png"))
```

Then call MCP tool:
- `ocr_recognize_base64`
  - `file_name: test2.png`
  - `image_base64: <b64>`
  - `lang: chi_sim+eng`
  - `preprocess: true`
  - `psm: 6`

Expected:
- non-empty `text`
- `line_count > 0`

## 5) Common failures

- `file not found on MCP server filesystem`
  - Cause: passed local client path to `ocr_recognize_file`.
  - Fix: use `ocr_recognize_base64`.

- `invalid image: broken data stream`
  - Cause: corrupted file or truncated base64.
  - Fix: re-read file bytes and regenerate full base64.

- timeout / 5xx
  - Fix: retry once, then use smaller/cropped image.

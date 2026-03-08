# Repository Guidelines

## Project Structure & Module Organization
This repository contains a Dockerized OCR service built with FastAPI and Tesseract.

- `app/`: backend API code (`main.py` contains routes and OCR logic).
- `web/`: frontend HTML page for manual OCR usage.
- `deploy/`: deployment artifacts (`docker-compose.yml`).
- `tessdata/`: local language model files (for example `chi_sim.traineddata`, `eng.traineddata`).
- Root files: `Dockerfile`, `requirements.txt`, `README.md`.

Keep new backend modules under `app/` and static UI assets under `web/`.

## Build, Test, and Development Commands
- `pip install -r requirements.txt`: install Python dependencies.
- `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`: run locally.
- `python -m py_compile app/main.py`: quick syntax validation.
- `docker compose -f deploy/docker-compose.yml up -d --build`: build and run container.
- `curl http://127.0.0.1:8000/health`: health check.
- `curl -X POST "http://127.0.0.1:8000/api/recognize" -F "file=@demo_cn.png" -F "lang=chi_sim+eng"`: OCR API test.

## Coding Style & Naming Conventions
- Python: PEP 8, 4-space indentation, type hints for public functions.
- Naming: `snake_case` for functions/variables, `UPPER_CASE` for constants, lowercase module names.
- Keep route handlers small; extract OCR helpers into private functions (for example `_preprocess`).
- Prefer explicit error responses (`HTTPException`) with actionable messages.

## Testing Guidelines
There is no formal test suite yet. When adding tests:

- Use `pytest` with files under `tests/` named `test_*.py`.
- Add API tests for `/health`, `/api/recognize`, and error cases (empty file, bad format, missing language data).
- Prioritize regression tests for OCR parameter handling (`lang`, `preprocess`).

## Commit & Pull Request Guidelines
Git history is unavailable in this workspace, so follow Conventional Commits:

- `feat: add batch OCR endpoint`
- `fix: handle missing tesseract binary`
- `docs: update deployment steps`

PRs should include:
- clear summary and scope,
- deployment impact (Docker/Nginx/env vars),
- test evidence (commands + key output),
- screenshots for UI changes in `web/`.

## Security & Configuration Notes
- Do not commit secrets, private keys, or production credentials.
- Keep container ports bound to localhost when behind Nginx (for example `127.0.0.1:18000:8000`).
- Validate upload size/type at API boundaries before OCR processing.

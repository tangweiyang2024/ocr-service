#!/usr/bin/env bash
set -euo pipefail

cd /opt/ocr-service

./.venv/bin/python - <<'PY'
from PIL import Image

img = Image.open("demo_cn.png").convert("RGB")
img = img.resize((4000, 4000))
img.save("/tmp/ocr_big.jpg", quality=95)
print("generated", img.size)
PY

ls -lh /tmp/ocr_big.jpg

for p in true false; do
  echo "== big image preprocess=$p =="
  curl -sS -o /tmp/ocr_big_out.json -w "code=%{http_code} time_total=%{time_total}\n" \
    -X POST "http://127.0.0.1:18000/api/recognize" \
    -F "file=@/tmp/ocr_big.jpg" \
    -F "lang=chi_sim+eng" \
    -F "preprocess=$p"
  head -c 120 /tmp/ocr_big_out.json
  echo
done

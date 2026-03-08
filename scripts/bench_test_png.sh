#!/usr/bin/env bash
set -euo pipefail

f="/opt/ocr-service/test.png"
url="http://127.0.0.1:18000/api/recognize"

run_case() {
  local lang="$1"
  local preprocess="$2"
  local psm="$3"

  echo "== lang=${lang} preprocess=${preprocess} psm=${psm} =="
  curl -sS -o /tmp/ocr_test_out.json -w "time_total=%{time_total} code=%{http_code}\n" \
    -X POST "$url" \
    -F "file=@${f}" \
    -F "lang=${lang}" \
    -F "preprocess=${preprocess}" \
    -F "psm=${psm}"

  /opt/ocr-service/.venv/bin/python - <<'PY'
import json
obj = json.load(open('/tmp/ocr_test_out.json', 'r', encoding='utf-8'))
text = obj.get('text', '')
print('line_count=', obj.get('line_count'), 'text_len=', len(text))
print('preview=', text[:120].replace('\n', '\\n'))
PY
  echo
}

run_case "chi_sim+eng" "true" "6"
run_case "chi_sim+eng" "false" "6"
run_case "chi_sim+eng" "false" "11"
run_case "eng" "false" "6"
run_case "eng" "false" "11"

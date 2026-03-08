#!/usr/bin/env bash
set -euo pipefail

URL="http://127.0.0.1:18000/api/recognize"
IMG="/opt/ocr-service/demo_cn.png"

rm -f /tmp/queue_times.txt
for i in $(seq 1 12); do
  (
    t=$(curl -sS -o /dev/null -w "%{time_total}" -X POST "$URL" \
      -F "file=@${IMG}" \
      -F "lang=chi_sim+eng" \
      -F "preprocess=true")
    echo "$i $t" >> /tmp/queue_times.txt
  ) &
done
wait
sort -n /tmp/queue_times.txt

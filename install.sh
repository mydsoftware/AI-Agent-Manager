#!/usr/bin/env bash
set -euo pipefail

# نصب سریع AI-Agent-Manager
ROOT_DIR="${AI_AGENT_MANAGER_DIR:-$HOME/ai-agent-manager}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

mkdir -p "$ROOT_DIR"
cd "$ROOT_DIR"

echo "[1/4] بررسی Python"
"$PYTHON_BIN" --version

echo "[2/4] ساخت محیط مجازی"
"$PYTHON_BIN" -m venv .venv

if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
else
  echo "محیط مجازی ساخته نشد."
  exit 1
fi

echo "[3/4] نصب وابستگی‌ها"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "[4/4] اجرای Smoke Test"
python -m pytest -q

echo "نصب و Smoke Test با موفقیت انجام شد."
echo "برای اجرای API: python http_api.py"

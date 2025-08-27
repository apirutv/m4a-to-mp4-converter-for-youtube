#!/usr/bin/env bash
set -euo pipefail

# --- Locate this script & Python script ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/m4a_to_mp4.py"

if [[ ! -f "$PY_SCRIPT" ]]; then
  echo "ERROR: Cannot find m4a_to_mp4.py in $SCRIPT_DIR"
  exit 1
fi

# --- Pick Python: use venv if available, otherwise system python3 ---
if [[ -x "$SCRIPT_DIR/venv/bin/python" ]]; then
  PY="$SCRIPT_DIR/venv/bin/python"
else
  PY="$(command -v python3 || true)"
  if [[ -z "${PY}" ]]; then
    echo "ERROR: python3 not found. Install Python 3 first."
    exit 1
  fi
fi

# --- Detect Windows username via cmd.exe (works in WSL) ---
WINUSER="$(cmd.exe /C "echo %USERNAME%" | tr -d $'\r')"
if [[ -z "${WINUSER}" ]]; then
  echo "ERROR: Could not detect Windows username."
  echo "Tip: Set it manually by running:"
  echo "  WINUSER=YourWindowsName ./run_downloads.sh"
  exit 1
fi

# Allow override by env var if needed
WINUSER="${WINUSER:-$WINUSER}"

# --- Build Windows Downloads path (mounted in WSL) ---
DOWNLOADS_PATH="/mnt/c/Users/${WINUSER}/Downloads/AI Poscast Temp"


if [[ ! -d "$DOWNLOADS_PATH" ]]; then
  echo "ERROR: Downloads folder not found at: $DOWNLOADS_PATH"
  echo "Check your Windows username or drive mapping."
  exit 1
fi

# --- Helpful info ---
echo "Using Python: $PY"
echo "Target folder: $DOWNLOADS_PATH"
echo "Passing options to m4a_to_mp4.py: $*"

# --- Check ffmpeg availability early (optional but nice) ---
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: ffmpeg not found in PATH."
  echo "Install it on WSL Ubuntu with:  sudo apt update && sudo apt install -y ffmpeg"
  exit 1
fi

# --- Run the converter (forward any arguments) ---
exec "$PY" "$PY_SCRIPT" "$DOWNLOADS_PATH" "$@"

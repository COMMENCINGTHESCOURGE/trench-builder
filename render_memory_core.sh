#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# MEMORY CORE — Automated Render Pipeline
# One command: renders camera path to MP4
#
# Usage:
#   ./render_memory_core.sh                    # default output
#   ./render_memory_core.sh --output demo.mp4  # custom output
#   ./render_memory_core.sh --fps 60           # 60fps render
#   ./render_memory_core.sh --watch            # watch mode: re-render on file change
# ═══════════════════════════════════════════════════════════════

set -e

# ── Config ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ARTIFACT="${SCRIPT_DIR}/MEMORY_CORE_ARCHITECTURAL_CAMERA.html"
RENDER_SCRIPT="${SCRIPT_DIR}/render_memory_core.js"
OUTPUT="${SCRIPT_DIR}/memory_core_render.mp4"
FPS=30
WATCH=false
PORT=8765

# ── Parse args ──
while [[ $# -gt 0 ]]; do
  case "$1" in
    --output) OUTPUT="$2"; shift 2 ;;
    --fps) FPS="$2"; shift 2 ;;
    --watch) WATCH=true; shift ;;
    --port) PORT="$2"; shift 2 ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

# ── Dependency check ──
check_deps() {
  local missing=()
  
  if ! command -v node &>/dev/null; then
    missing+=("node (Node.js)")
  fi
  
  if ! command -v ffmpeg &>/dev/null; then
    missing+=("ffmpeg")
  fi
  
  # Check puppeteer
  if ! node -e "require('puppeteer')" &>/dev/null 2>&1; then
    echo "⚠️  puppeteer not found. Installing..."
    npm install puppeteer 2>&1 | tail -1
  fi
  
  if [[ ${#missing[@]} -gt 0 ]]; then
    echo "❌ Missing dependencies: ${missing[*]}"
    exit 1
  fi
  
  echo "✅ Dependencies OK: node $(node -v), ffmpeg $(ffmpeg -version 2>&1 | head -1 | cut -d' ' -f3)"
}

# ── Start local server ──
start_server() {
  echo "🌐 Starting local server on :${PORT}..."
  cd "${SCRIPT_DIR}"
  python -m http.server "${PORT}" &
  SERVER_PID=$!
  sleep 2
  
  # Verify
  if ! kill -0 "${SERVER_PID}" 2>/dev/null; then
    echo "❌ Server failed to start"
    exit 1
  fi
  echo "   PID: ${SERVER_PID}"
}

# ── Stop server ──
stop_server() {
  if [[ -n "${SERVER_PID}" ]] && kill -0 "${SERVER_PID}" 2>/dev/null; then
    kill "${SERVER_PID}" 2>/dev/null || true
    echo "🛑 Server stopped"
  fi
}
trap stop_server EXIT

# ── Render ──
render() {
  echo ""
  echo "╔══════════════════════════════════════════════╗"
  echo "║  MEMORY CORE — AUTOMATED RENDER             ║"
  echo "║  Artifact: MEMORY_CORE_ARCHITECTURAL_CAMERA  ║"
  echo "║  Output:   $(basename "${OUTPUT}")"
  echo "║  FPS:      ${FPS}"
  echo "╚══════════════════════════════════════════════╝"
  echo ""
  echo "📐 Camera path (default demo):"
  echo "   1. Entry hold          (1.5s)"
  echo "   2. Quarter orbit pan   (2.0s)"
  echo "   3. Layer 0→1 transition (2.5s) ← SHADOW LAG"
  echo "   4. Layer 1→2 transition (2.0s) ← SHADOW LAG"
  echo "   5. Pan to 216°         (2.0s)"
  echo "   6. Layer 2→0 deep drop (3.0s) ← DEEP SHADOW"
  echo "   7. Pan to 324°         (2.0s)"
  echo "   8. Full circle          (2.0s)"
  echo "   Total: ~17s"
  echo ""

  node "${RENDER_SCRIPT}" \
    --output "${OUTPUT}" \
    --fps "${FPS}" \
    --url "http://localhost:${PORT}/MEMORY_CORE_ARCHITECTURAL_CAMERA.html" \
    --width 1920 \
    --height 1080

  echo ""
  echo "╔══════════════════════════════════════════════╗"
  echo "║  RENDER COMPLETE                            ║"
  echo "║  $(basename "${OUTPUT}")"
  if command -v wslpath &>/dev/null; then
    echo "║  $(wslpath -w "${OUTPUT}")"
  fi
  echo "╚══════════════════════════════════════════════╝"
}

# ── Watch mode ──
watch_loop() {
  echo "👁️  Watching ${ARTIFACT} for changes..."
  echo "   Modify the artifact → auto-render triggers"
  echo ""
  
  local last_mtime=$(stat -c %Y "${ARTIFACT}" 2>/dev/null || echo 0)
  
  while true; do
    sleep 2
    local current_mtime=$(stat -c %Y "${ARTIFACT}" 2>/dev/null || echo 0)
    
    if [[ "${current_mtime}" != "${last_mtime}" ]]; then
      echo ""
      echo "🔄 Change detected at $(date '+%H:%M:%S') — re-rendering..."
      last_mtime="${current_mtime}"
      
      # Timestamp output file
      local ts_output="${OUTPUT%.mp4}_$(date '+%Y%m%d_%H%M%S').mp4"
      node "${RENDER_SCRIPT}" \
        --output "${ts_output}" \
        --fps "${FPS}" \
        --url "http://localhost:${PORT}/MEMORY_CORE_ARCHITECTURAL_CAMERA.html" \
        --width 1920 \
        --height 1080
        
      echo "   → ${ts_output}"
      echo "👁️  Watching..."
    fi
  done
}

# ── Main ──
check_deps
start_server

if ${WATCH}; then
  # Initial render
  render
  watch_loop
else
  render
fi

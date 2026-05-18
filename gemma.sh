#!/data/data/com.termux/files/usr/bin/bash
# Vinculum — Gemma 4 on llama.cpp wrapper
# Usage: ./gemma "Your prompt here"

MODEL="$HOME/models/gemma-4-2b-it-Q4_K_M.gguf"
LLAMA="$HOME/llama-b9204/llama-cli"
export LD_LIBRARY_PATH="$HOME/llama-b9204"

if [ ! -f "$MODEL" ]; then
    echo "Model not found: $MODEL"
    echo "Downloading..."
    exit 1
fi

PROMPT="${1:-Explain what an S3 bucket is in one sentence.}"

echo "=== GEMMA 4 · LLAMA.CPP · OFFLINE ==="
echo "Model: $(basename $MODEL)"
echo "Device: $(getprop ro.product.model) · $(getprop ro.product.board)"
echo "RAM: $(free -h | grep Mem | awk '{print $2}')"
echo ""

$LLAMA \
    -m "$MODEL" \
    --temp 0.7 \
    --n-predict 60 \
    -p "<bos><start_of_turn>user\n${PROMPT}<end_of_turn>\n<start_of_turn>model\n" \
    --no-display-prompt \
    --simple-io \
    -ngl 0 \
    2>&1

echo ""
echo "=== INFERENCE COMPLETE ==="

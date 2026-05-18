#!/data/data/com.termux/files/usr/bin/bash
# Vinculum Phone Bootstrap — run once after Termux install
# Installs dependencies, builds llama.cpp, downloads Gemma 4 GGUF

set -e

echo "=== VINCULUM PHONE SETUP ==="
echo "Device: $(getprop ro.product.model)"
echo "RAM: $(cat /proc/meminfo | grep MemTotal)"
echo ""

# Storage setup
termux-setup-storage

# Update repos
echo "=== Updating packages ==="
pkg update -y && pkg upgrade -y

# Core tools
echo "=== Installing build tools ==="
pkg install -y git cmake python build-essential binutils wget curl clang

# llama.cpp
echo "=== Building llama.cpp ==="
cd ~
if [ ! -d llama.cpp ]; then
    git clone --depth 1 https://github.com/ggerganov/llama.cpp
fi
cd llama.cpp
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DGGML_OPENMP=ON -DGGML_NATIVE=OFF
make -j4 llama-cli

echo "=== llama.cpp built ==="
ls -lh bin/llama-cli

# Model directory
mkdir -p ~/models

echo ""
echo "=== SETUP DONE ==="
echo ""
echo "Next steps:"
echo "  1. Download Gemma 4 GGUF model to ~/models/"
echo "  2. Run benchmark: ~/llama.cpp/build/bin/llama-cli -m ~/models/gemma-4-2b-it-Q4_K_M.gguf --temp 0.7 -p 'Hello' -n 50"
echo "  3. Record screen for hackathon video"

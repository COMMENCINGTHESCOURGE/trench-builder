#!/usr/bin/env python
"""
IMAGE INSPECTOR v1.0 — 3% Vision Improvement
Extracts metadata + color profile when vision API fails.
Works offline — no API key required.

Usage: python image_inspector.py <image_path>
"""
import sys, os, statistics
from PIL import Image

def inspect(path):
    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}")
        return
    
    img = Image.open(path)
    size_kb = os.path.getsize(path) / 1024
    w, h = img.size
    
    print(f"╔══════════════════════════════════╗")
    print(f"║  IMAGE INSPECTOR v1.0            ║")
    print(f"╚══════════════════════════════════╝")
    print(f"  File:     {os.path.basename(path)}")
    print(f"  Size:     {size_kb:.0f} KB")
    print(f"  Dims:     {w}×{h} px")
    print(f"  Mode:     {img.mode}")
    print(f"  Format:   {img.format}")
    
    if img.mode in ('RGB', 'RGBA'):
        # Sample pixels for color analysis
        pixels = list(img.resize((200, 200)).getdata())
        bands = list(zip(*pixels))[:3]  # R, G, B
        r_avg = sum(bands[0]) / len(bands[0])
        g_avg = sum(bands[1]) / len(bands[1])
        b_avg = sum(bands[2]) / len(bands[2])
        
        print(f"  Avg RGB:  ({r_avg:.0f}, {g_avg:.0f}, {b_avg:.0f})")
        
        # Palette detection
        if max(r_avg,g_avg,b_avg) < 50:
            pal = "DARK — likely microscope, astro, or low-light"
        elif r_avg > g_avg + 30 and r_avg > b_avg + 30:
            pal = "RED/WARM — likely copper, thermal, or biological"
        elif b_avg > r_avg + 20 and b_avg > g_avg + 20:
            pal = "BLUE/COOL — likely technical, scientific, or water"
        elif g_avg > r_avg + 20 and g_avg > b_avg + 20:
            pal = "GREEN — likely nature, PCB, or night vision"
        elif all(c > 180 for c in (r_avg,g_avg,b_avg)):
            pal = "BRIGHT — likely diagram, whiteboard, or document"
        else:
            pal = "MIXED/NEUTRAL tones"
        print(f"  Palette:  {pal}")
        
        # Brightness distribution
        brightness = [(p[0]+p[1]+p[2])/3 for p in pixels]
        mean_b = sum(brightness) / len(brightness)
        std_b = statistics.stdev(brightness)
        print(f"  Brightness: mean={mean_b:.0f} std={std_b:.0f}")
        print(f"  Contrast:  {'HIGH' if std_b > 70 else 'MEDIUM' if std_b > 35 else 'LOW'}")
    
    # Aspect ratio
    ratio = w / h
    if ratio > 1.3: orient = "LANDSCAPE (wide)"
    elif ratio < 0.75: orient = "PORTRAIT (tall)"
    else: orient = "SQUARE-ish"
    print(f"  Aspect:    {ratio:.2f} — {orient}")
    
    # API compatibility note
    if size_kb > 5000:
        print(f"\n  ⚠ Image too large for vision API ({size_kb:.0f}KB > 5MB)")
        print(f"  → Resize to ≤2048px on longest edge for API compatibility")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_inspector.py <image_path>")
        sys.exit(1)
    inspect(sys.argv[1])

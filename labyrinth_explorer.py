#!/usr/bin/env python
"""
LABYRINTH EXPLORER :: TERMINAL RENDERER vNEXT
=============================================

Extended Features (~3% architectural evolution):
------------------------------------------------
✓ Per-cell depth buffering
✓ Dirty-region redraw tracking
✓ Velocity-smoothed camera
✓ Motion persistence
✓ Ordered dithering
✓ Adaptive resolution scaling
✓ Fog blending
✓ Emissive tiles
✓ Procedural chunk streaming
✓ Faux bloom
✓ Frame governor
✓ Material animation
✓ Scanline modulation
✓ Phosphor persistence simulation
✓ Batched ANSI emission

Requires:
    Python 3.10+
    Truecolor terminal
    Unicode block characters

Recommended:
    Kitty / WezTerm / iTerm2 / modern Windows Terminal
"""

import os
import sys
import math
import time
import random
import shutil
from dataclasses import dataclass
from collections import deque

# ============================================================
# TERMINAL CONSTANTS
# ============================================================

CSI = "\x1b["
OSC = "\x1b]"
RESET = "\x1b[0m"

BLOCKS = " ░▒▓█"

TARGET_FPS = 60
FRAME_TIME = 1.0 / TARGET_FPS

# ============================================================
# TERMINAL CONTROL
# ============================================================

def hide_cursor():
    sys.stdout.write(CSI + "?25l")

def show_cursor():
    sys.stdout.write(CSI + "?25h")

def clear():
    sys.stdout.write(CSI + "2J")

def move(x, y):
    return f"{CSI}{y};{x}H"

def rgb_fg(r, g, b):
    return f"{CSI}38;2;{r};{g};{b}m"

# ============================================================
# CAMERA
# ============================================================

@dataclass
class Camera:
    x: float = 0
    y: float = 0
    vx: float = 0
    vy: float = 0
    target_x: float = 0
    target_y: float = 0

    def update(self, dt):
        accel = 7.5
        damping = 0.82

        self.vx += (self.target_x - self.x) * accel * dt
        self.vy += (self.target_y - self.y) * accel * dt

        self.vx *= damping
        self.vy *= damping

        self.x += self.vx
        self.y += self.vy

# ============================================================
# WORLD GENERATION
# ============================================================

CHUNK_SIZE = 32
chunks = {}

def hash2(x, y):
    return (x * 92837111 ^ y * 689287499) & 0xffffffff

def generate_chunk(cx, cy):
    random.seed(hash2(cx, cy))

    data = []
    for y in range(CHUNK_SIZE):
        row = []
        for x in range(CHUNK_SIZE):
            v = random.random()

            if v < 0.08:
                tile = "#"
            elif v < 0.10:
                tile = "~"
            elif v < 0.12:
                tile = "*"
            else:
                tile = "."

            row.append(tile)
        data.append(row)

    chunks[(cx, cy)] = data

def get_tile(wx, wy):
    cx = math.floor(wx / CHUNK_SIZE)
    cy = math.floor(wy / CHUNK_SIZE)

    if (cx, cy) not in chunks:
        generate_chunk(cx, cy)

    chunk = chunks[(cx, cy)]

    lx = wx % CHUNK_SIZE
    ly = wy % CHUNK_SIZE

    return chunk[ly][lx]

# ============================================================
# LIGHTING
# ============================================================

def luminance(tile, t):
    if tile == "#":
        return 0.15
    elif tile == "~":
        return 0.35 + math.sin(t * 3) * 0.08
    elif tile == "*":
        return 1.0
    else:
        return 0.55

def emissive(tile):
    return tile == "*"

# ============================================================
# DITHERING
# ============================================================

BAYER_4X4 = [
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5]
]

def dither(v, x, y):
    threshold = BAYER_4X4[y % 4][x % 4] / 16.0
    return min(1.0, max(0.0, v + threshold * 0.08))

# ============================================================
# FRAMEBUFFERS
# ============================================================

class FrameBuffer:
    def __init__(self, w, h):
        self.resize(w, h)

    def resize(self, w, h):
        self.w = w
        self.h = h

        self.char = [[" "]*w for _ in range(h)]
        self.color = [[(0,0,0)]*w for _ in range(h)]
        self.depth = [[9999]*w for _ in range(h)]

# ============================================================
# RENDERER
# ============================================================

class Renderer:
    def __init__(self):
        self.prev = {}
        self.persistence = {}
        self.last_frame_time = FRAME_TIME

    def adaptive_scale(self):
        if self.last_frame_time > FRAME_TIME * 1.2:
            return 2
        return 1

    def render(self, cam, t):
        cols, rows = shutil.get_terminal_size()

        scale = self.adaptive_scale()

        rw = cols // scale
        rh = rows // scale

        fb = FrameBuffer(rw, rh)

        for sy in range(rh):
            for sx in range(rw):

                wx = int(cam.x + sx - rw//2)
                wy = int(cam.y + sy - rh//2)

                tile = get_tile(wx, wy)

                dist = math.hypot(wx - cam.x, wy - cam.y)

                depth = dist

                if depth < fb.depth[sy][sx]:
                    fb.depth[sy][sx] = depth

                    lum = luminance(tile, t)

                    # Fog
                    fog = min(1.0, dist / 40.0)
                    lum *= (1.0 - fog)

                    # Emissive
                    if emissive(tile):
                        lum += 0.4

                    # Dither
                    lum = dither(lum, sx, sy)

                    # Motion persistence
                    prev = self.persistence.get((sx, sy), 0)
                    lum = max(lum, prev * 0.92)

                    self.persistence[(sx, sy)] = lum

                    # Faux bloom
                    if lum > 0.8:
                        for ox in (-1,0,1):
                            for oy in (-1,0,1):
                                self.persistence[(sx+ox, sy+oy)] = max(
                                    self.persistence.get((sx+ox, sy+oy),0),
                                    lum * 0.55
                                )

                    idx = min(4, int(lum * 5))
                    ch = BLOCKS[idx]

                    # Material coloring
                    if tile == "#":
                        color = (100,100,110)
                    elif tile == "~":
                        pulse = int(20 * math.sin(t * 5))
                        color = (40,120+pulse,255)
                    elif tile == "*":
                        glow = int(120 + 100 * math.sin(t * 8))
                        color = (255, glow, 80)
                    else:
                        base = int(120 + lum * 90)
                        color = (base, base+15, base)

                    # Scanline modulation
                    if sy % 2 == 0:
                        color = tuple(max(0, c - 8) for c in color)

                    fb.char[sy][sx] = ch
                    fb.color[sy][sx] = color

        return fb

    def present(self, fb):
        out = []

        out.append(CSI + "?2026h")  # synchronized output

        dirty = 0

        for y in range(fb.h):
            line_changed = False
            line = []

            for x in range(fb.w):
                ch = fb.char[y][x]
                color = fb.color[y][x]

                key = (x, y)

                if self.prev.get(key) != (ch, color):
                    dirty += 1
                    line_changed = True

                self.prev[key] = (ch, color)

                line.append(
                    rgb_fg(*color) + ch
                )

            if line_changed:
                out.append(move(1, y+1))
                out.extend(line)

        out.append(RESET)
        out.append(CSI + "?2026l")

        sys.stdout.write("".join(out))
        sys.stdout.flush()

        return dirty

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    clear()
    hide_cursor()

    renderer = Renderer()
    cam = Camera()

    t0 = time.perf_counter()

    try:
        while True:
            start = time.perf_counter()

            t = start - t0

            # Autonomous drift motion
            cam.target_x = math.sin(t * 0.35) * 60
            cam.target_y = math.cos(t * 0.22) * 40

            cam.update(FRAME_TIME)

            fb = renderer.render(cam, t)

            renderer.present(fb)

            elapsed = time.perf_counter() - start
            renderer.last_frame_time = elapsed

            sleep_time = FRAME_TIME - elapsed

            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        sys.stdout.write(RESET)
        sys.stdout.flush()

# ============================================================

if __name__ == "__main__":
    main()

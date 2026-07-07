#!/usr/bin/env node
/**
 * MEMORY CORE — Automated Video Render Pipeline v3
 * Captures frames during the animation, stitches to MP4 via ffmpeg.
 * 
 * Usage: node render_memory_core.js [--output out.mp4] [--fps 15] [--url http://...]
 */

const puppeteer = require('puppeteer');
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const args = process.argv.slice(2);
const getArg = (flag, def) => {
  const idx = args.indexOf(flag);
  return idx >= 0 && idx + 1 < args.length ? args[idx + 1] : def;
};

const OUTPUT = path.resolve(getArg('--output', 'memory_core_render.mp4'));
const FPS = parseInt(getArg('--fps', '15'));
const URL = getArg('--url', 'http://localhost:8765/MEMORY_CORE_ARCHITECTURAL_CAMERA.html');
const WIDTH = 1280;
const HEIGHT = 720;
const FRAME_DIR = path.join(os.tmpdir(), 'mc_frames_' + Date.now());

fs.mkdirSync(FRAME_DIR, { recursive: true });

async function main() {
  console.log('══ Memory Core Render Pipeline ══');
  console.log('  URL:    ' + URL + '?auto');
  console.log('  Output: ' + OUTPUT);
  console.log('  FPS:    ' + FPS);
  console.log('  Size:   ' + WIDTH + 'x' + HEIGHT);
  console.log('  Frames: ' + FRAME_DIR);
  console.log('');

  // Launch
  console.log('Launching headless Chrome...');
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox', '--disable-setuid-sandbox',
      '--use-gl=angle', '--use-angle=swiftshader',
      '--enable-webgl', '--ignore-gpu-blocklist',
      '--window-size=' + WIDTH + ',' + HEIGHT,
    ]
  });
  const page = await browser.newPage();
  await page.setViewport({ width: WIDTH, height: HEIGHT });

  // Load
  const autoUrl = URL + (URL.includes('?') ? '&auto' : '?auto');
  console.log('Loading...');
  await page.goto(autoUrl, { waitUntil: 'load', timeout: 30000 });
  await new Promise(r => setTimeout(r, 3000));

  // Verify AutoRenderer
  const ready = await page.evaluate(() => {
    try { return window.__autoRenderer && window.__autoRenderer.active === true; }
    catch(e) { return false; }
  });
  if (!ready) {
    console.log('WARNING: AutoRenderer not active. Trying to start...');
    await page.evaluate(() => { try { window.__autoRenderer.start(); } catch(e) {} });
    await new Promise(r => setTimeout(r, 1000));
  }
  console.log('Rendering...');

  // Frame capture loop
  const frameInterval = 1000 / FPS;
  let frameCount = 0;
  let done = false;
  let lastStateLog = 0;
  const startTime = Date.now();

  while (!done) {
    const frameStart = Date.now();

    // Capture
    const frameFile = path.join(FRAME_DIR, 'f_' + String(frameCount).padStart(6, '0') + '.jpg');
    try {
      await page.screenshot({ path: frameFile, type: 'jpeg', quality: 85 });
    } catch (e) {
      console.log('  Screenshot error: ' + e.message);
      break;
    }
    frameCount++;

    // Check completion
    done = await page.evaluate(() => {
      try { return window.__AUTO_RENDER_COMPLETE === true; } catch(e) { return false; }
    });

    // Progress every 30 frames
    if (frameCount - lastStateLog >= 30) {
      lastStateLog = frameCount;
      const state = await page.evaluate(() => {
        try {
          const ar = window.__autoRenderer;
          return ar ? ar.getState() : null;
        } catch(e) { return null; }
      });
      if (state && state.status === 'rendering') {
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(0);
        process.stdout.write('\r  Frame ' + frameCount + ' | Seg ' + (state.segment+1) + '/' + state.total + ' | ' + elapsed + 's | ' + state.desc + '     ');
      }
    }

    // Timing
    const frameElapsed = Date.now() - frameStart;
    const sleepTime = Math.max(1, Math.floor(frameInterval - frameElapsed));
    if (!done) {
      await new Promise(r => setTimeout(r, sleepTime));
    }

    // Safety limits
    if (frameCount > 1200) {
      console.log('\n  Frame limit reached — stopping');
      done = true;
    }
  }

  // Hold frames (2 seconds of black at end)
  for (let i = 0; i < FPS * 2; i++) {
    const frameFile = path.join(FRAME_DIR, 'f_' + String(frameCount).padStart(6, '0') + '.jpg');
    await page.screenshot({ path: frameFile, type: 'jpeg', quality: 85 });
    frameCount++;
  }

  const totalTime = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log('\n  Captured ' + frameCount + ' frames in ' + totalTime + 's');

  await browser.close();

  // Stitch
  console.log('Stitching MP4 via ffmpeg...');
  const result = spawnSync('ffmpeg', [
    '-y',
    '-framerate', String(FPS),
    '-i', path.join(FRAME_DIR, 'f_%06d.jpg'),
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'fast',
    '-crf', '20',
    '-movflags', '+faststart',
    OUTPUT
  ], {
    stdio: 'pipe',
    timeout: 120000
  });

  if (result.error || result.status !== 0) {
    console.log('ffmpeg stderr: ' + (result.stderr ? result.stderr.toString().slice(0, 500) : 'none'));
    console.log('Frames saved in: ' + FRAME_DIR);
    console.log('Manual: ffmpeg -framerate ' + FPS + ' -i "' + FRAME_DIR + '/f_%06d.jpg" -c:v libx264 -pix_fmt yuv420p ' + OUTPUT);
    process.exit(1);
  }

  // Cleanup
  fs.rmSync(FRAME_DIR, { recursive: true, force: true });

  const fileSize = fs.statSync(OUTPUT).size;
  const duration = (frameCount / FPS).toFixed(1);
  console.log('');
  console.log('══ Render Complete ══');
  console.log('  File:     ' + OUTPUT);
  console.log('  Size:     ' + (fileSize / 1024 / 1024).toFixed(1) + 'MB');
  console.log('  Duration: ' + duration + 's');
  console.log('  Frames:   ' + frameCount);
  console.log('  FPS:      ' + FPS);
}

main().catch(err => {
  console.error('FATAL: ' + err.message);
  console.error(err.stack);
  process.exit(1);
});

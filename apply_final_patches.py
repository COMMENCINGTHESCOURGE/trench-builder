def apply_final_patches(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Remove duplicate togglePause definition
    target_pause = """function togglePause() {
  const startScreen = document.getElementById('start-screen');
  if (startScreen && startScreen.style.display !== 'none') return;
  
  if (gamePaused) {
    controls.lock();
  } else {
    controls.unlock();
  }
}"""
    html = html.replace(target_pause, "/* removed duplicate togglePause */")

    # 2. Fix namespace calls for post-processing
    html = html.replace('new THREE.RenderPass', 'new RenderPass')
    html = html.replace('new THREE.UnrealBloomPass', 'new UnrealBloomPass')
    html = html.replace('new THREE.EffectComposer', 'new EffectComposer')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Disk file patches applied successfully.")

if __name__ == '__main__':
    apply_final_patches(r'C:\Users\dasha\Projects\pangea-substrate\public\nova_horizon_aurora.html')

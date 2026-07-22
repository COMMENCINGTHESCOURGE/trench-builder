import shutil
import os

def setup_terminals():
    # 1. Copy ascii_maze_3d.html to the public directory
    src_maze = r'C:\Users\dasha\Projects\ascii_maze_3d.html'
    dest_maze = r'C:\Users\dasha\Projects\pangea-substrate\public\ascii_maze_3d.html'
    if os.path.exists(src_maze):
        shutil.copy(src_maze, dest_maze)
        print("Copied ascii_maze_3d.html successfully.")

    # 2. Modify nova_horizon_aurora.html
    game_path = r'C:\Users\dasha\Projects\pangea-substrate\public\nova_horizon_aurora.html'
    with open(game_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Inject CSS / Overlay HTML just before the end of </body>
    overlay_html = """
<!-- TERMINAL SCREEN OVERLAY -->
<div id="terminal-overlay" style="display:none; position:fixed; inset:0; z-index:99999; align-items:center; justify-content:center; background:rgba(2,6,16,0.85); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);">
  <div style="background:rgba(8,12,30,0.95); border:2px solid #8b5cf6; border-radius:12px; box-shadow:0 0 35px rgba(139,92,246,0.3); width:85%; height:85%; display:flex; flex-direction:column; overflow:hidden;">
    <div style="background:rgba(15,25,45,0.9); border-bottom:1px solid rgba(139,92,246,0.3); padding:12px; display:flex; justify-content:space-between; align-items:center;">
      <span id="terminal-title" style="font-family:Orbitron; color:#8b5cf6; font-size:14px; letter-spacing:2px; font-weight:bold;">TERMINAL SYSTEM</span>
      <button onclick="closeTerminal()" style="padding:6px 14px; background:rgba(255,68,68,0.1); border:1px solid #ff4444; color:#ff4444; font-family:Orbitron; font-size:11px; letter-spacing:1px; border-radius:4px; cursor:pointer;">EXIT TERMINAL</button>
    </div>
    <iframe id="terminal-iframe" src="" style="width:100%; height:100%; border:none; background:#000;"></iframe>
  </div>
</div>
"""
    html = html.replace('</body>', overlay_html + '\n</body>')

    # Inject Terminal Data & Initialization Code into the main script tag
    script_inject = """
  // ═══ Proximity Kiosk Terminals ═══
  const terminals = [
    { name: 'MAZE RUNNER', url: '/ascii_maze_3d.html', pos: { x: -8, z: -8 }, color: 0x00ffaa },
    { name: 'TRENCH CONSOLE', url: '/trench_builder_10001.html', pos: { x: 0, z: -8 }, color: 0xffaa00 },
    { name: 'MECHA ARENA', url: '/mecha_arena_10001.html', pos: { x: 8, z: -8 }, color: 0x00ccff }
  ];
  
  const terminalMeshes = [];
  
  terminals.forEach(t => {
    // Kiosk Base
    const baseGeo = new THREE.BoxGeometry(1.2, 2.5, 0.8);
    const baseMat = new THREE.MeshStandardMaterial({ color: 0x1f2937, roughness: 0.4, metalness: 0.8 });
    const kiosk = new THREE.Mesh(baseGeo, baseMat);
    kiosk.position.set(t.pos.x, 1.25, t.pos.z);
    kiosk.castShadow = true;
    kiosk.receiveShadow = true;
    scene.add(kiosk);
    
    // Screen mesh
    const screenGeo = new THREE.PlaneGeometry(0.9, 0.7);
    const screenMat = new THREE.MeshBasicMaterial({ color: t.color });
    const screen = new THREE.Mesh(screenGeo, screenMat);
    screen.position.set(0, 0.6, 0.41); // slightly offset forward
    kiosk.add(screen);
    
    terminalMeshes.push({ kiosk, data: t });
  });

  window.closeTerminal = function() {
    document.getElementById('terminal-overlay').style.display = 'none';
    document.getElementById('terminal-iframe').src = '';
    controls.lock();
  };
"""
    # Find place to inject (e.g. right before updateInteract())
    html = html.replace('function updateInteract()', script_inject + '\nfunction updateInteract()')

    # Inject updateInteract proximity logic
    interact_target = "  // Rock mining prompt"
    interact_replacement = """  // Terminal prompt checks
  for (let t of terminalMeshes) {
    const dist = Math.hypot(cam.position.x - t.kiosk.position.x, cam.position.z - t.kiosk.position.z);
    if (dist < 4) {
      txt = '[E] ACCESS ' + t.data.name;
      break;
    }
  }
  if (txt) { p.innerText = txt; p.classList.add('s'); return; }

  // Rock mining prompt"""
    html = html.replace(interact_target, interact_replacement)

    # Inject interact handler logic
    interact_handler_target = "function interact() {"
    interact_handler_replacement = """function interact() {
  // Proximity Terminal check
  for (let t of terminalMeshes) {
    const dist = Math.hypot(cam.position.x - t.kiosk.position.x, cam.position.z - t.kiosk.position.z);
    if (dist < 4) {
      controls.unlock();
      document.getElementById('terminal-overlay').style.display = 'flex';
      document.getElementById('terminal-title').innerText = t.data.name + ' INTERACTIVE TERMINAL';
      document.getElementById('terminal-iframe').src = t.data.url;
      return;
    }
  }"""
    html = html.replace(interact_handler_target, interact_handler_replacement)

    with open(game_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Nova Horizon Aurora upgraded with terminals successfully.")

if __name__ == '__main__':
    setup_terminals()

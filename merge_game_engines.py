import re

def create_nova_horizon_aurora(resolved_nova_path, aurora_path, output_path):
    with open(resolved_nova_path, 'r', encoding='utf-8') as f:
        nova = f.read()

    # 1. Update the imports to include post-processing addons
    import_target = "import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';"
    import_replacement = (
        "import { PointerLockControls } from 'three/addons/controls/PointerLockControls.js';\n"
        "import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';\n"
        "import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';\n"
        "import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';"
    )
    nova = nova.replace(import_target, import_replacement)

    # 2. Add tone mapping and post-processing setup to the renderer initialization
    renderer_target = (
        "const renderer = new THREE.WebGLRenderer({antialias:true,canvas:document.getElementById('c')});\n"
        "renderer.setSize(innerWidth,innerHeight);\n"
        "renderer.setPixelRatio(Math.min(devicePixelRatio,2));\n"
        "renderer.shadowMap.enabled = true;"
    )
    renderer_replacement = (
        "const renderer = new THREE.WebGLRenderer({antialias:true,canvas:document.getElementById('c'),powerPreference:'high-performance'});\n"
        "renderer.setSize(innerWidth,innerHeight);\n"
        "renderer.setPixelRatio(Math.min(devicePixelRatio,2));\n"
        "renderer.shadowMap.enabled = true;\n"
        "renderer.shadowMap.type = THREE.PCFSoftShadowMap;\n"
        "renderer.toneMapping = THREE.ReinhardToneMapping;\n"
        "renderer.toneMappingExposure = 1.25;\n\n"
        "// High-Fidelity Post-Processing (from AURORA)\n"
        "const renderPass = new THREE.RenderPass(scene, cam);\n"
        "const bloomPass = new THREE.UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85);\n"
        "bloomPass.threshold = 0.12;\n"
        "bloomPass.strength = 0.75;\n"
        "bloomPass.radius = 0.6;\n\n"
        "const composer = new THREE.EffectComposer(renderer);\n"
        "composer.addPass(renderPass);\n"
        "composer.addPass(bloomPass);"
    )
    nova = nova.replace(renderer_target, renderer_replacement)

    # 3. Surgical replacement of the render call inside animate(time) loop
    render_target = "renderer.render(scene, cam);"
    render_replacement = "composer.render();"
    nova = nova.replace(render_target, render_replacement)

    # 4. Handle resize callback for the composer
    resize_target = (
        "window.addEventListener('resize', () => {\n"
        "  cam.aspect = innerWidth / innerHeight;\n"
        "  cam.updateProjectionMatrix();\n"
        "  renderer.setSize(innerWidth, innerHeight);\n"
        "});"
    )
    resize_replacement = (
        "window.addEventListener('resize', () => {\n"
        "  cam.aspect = innerWidth / innerHeight;\n"
        "  cam.updateProjectionMatrix();\n"
        "  renderer.setSize(innerWidth, innerHeight);\n"
        "  composer.setSize(innerWidth, innerHeight);\n"
        "});"
    )
    nova = nova.replace(resize_target, resize_replacement)

    # Save the cross-pollinated game
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(nova)
    print("Cross-pollinated game created successfully.")

if __name__ == '__main__':
    create_nova_horizon_aurora(
        r'C:\Users\dasha\Projects\pangea-substrate\public\nova_horizon_3d.html',
        r'C:\Users\dasha\.gemini\antigravity-ide\scratch\portal\games\AURORA_High_Fidelity_Engine.html',
        r'C:\Users\dasha\Projects\pangea-substrate\public\nova_horizon_aurora.html'
    )

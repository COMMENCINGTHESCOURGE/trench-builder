# TRENCH BUILDER — Color Theory + Vanishing Point Training
# Kaggle GPU Notebook — May 2026
# DaShawn / Guinea Pig Trench LLC

# ═══════════════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════════════
import numpy as np
import json, os, math
from pathlib import Path

# Check GPU
import subprocess
gpu_info = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'], 
                          capture_output=True, text=True)
print(f"GPU: {gpu_info.stdout.strip()}")

# ═══════════════════════════════════════════════════════
# 1. COLOR THEORY — Melanin Spectrum Training Data
# ═══════════════════════════════════════════════════════

# 315 Named Black Shades (from Guinea Pig Trench rendering reference)
NAMED_BLACKS = {
    'Black Walnut': (0x1E, 0x13, 0x0B),
    'Black Mahogany': (0x25, 0x0C, 0x00),
    'Dark Mahogany': (0x4A, 0x18, 0x00),
    'Zinnwaldite Brown': (0x2C, 0x16, 0x08),
    'Cafe Noir': (0x4B, 0x36, 0x21),
    'Bistre': (0x3D, 0x2B, 0x1F),
    'Dark Sienna': (0x3C, 0x14, 0x10),
    'Taupe': (0x48, 0x3C, 0x32),
    'Umber': (0x63, 0x51, 0x47),
    'Liver': (0x53, 0x4B, 0x4F),
    'Onyx': (0x35, 0x38, 0x39),
    'Jet': (0x0A, 0x0A, 0x0A),
    'Charcoal': (0x36, 0x33, 0x39),
    'Ebony': (0x55, 0x5D, 0x50),
    'Crow': (0x1A, 0x1A, 0x1D),
    'Raisin Black': (0x23, 0x22, 0x27),
    'Eerie Black': (0x1B, 0x1B, 0x1B),
    'Licorice': (0x1A, 0x11, 0x10),
    'Night': (0x0C, 0x09, 0x0A),
    'Smoky Black': (0x10, 0x0C, 0x08),
}

def generate_melanin_spectrum(n_samples=10000):
    """Generate training data across the melanin spectrum with PBR parameters."""
    data = []
    for _ in range(n_samples):
        # Melanin concentration 0 (light) to 1 (deep dark)
        melanin = np.random.beta(2, 2)
        
        # Base color shifts warmer as melanin increases
        r = int(np.clip(30 + melanin * 200 + np.random.normal(0, 8), 5, 240))
        g = int(np.clip(25 + melanin * 140 + np.random.normal(0, 6), 5, 180))
        b = int(np.clip(20 + melanin * 80 + np.random.normal(0, 5), 3, 140))
        
        # PBR parameters that shift with melanin
        roughness = np.clip(0.25 + melanin * 0.2 + np.random.normal(0, 0.03), 0.1, 0.7)
        specular_intensity = np.clip(0.8 + melanin * 0.9 + np.random.normal(0, 0.1), 0.5, 2.5)
        subsurface = np.clip(1.5 - melanin * 1.4 + np.random.normal(0, 0.05), 0.05, 1.5)
        
        data.append({
            'melanin': float(melanin),
            'color_rgb': [r/255, g/255, b/255],
            'roughness': float(roughness),
            'specular_intensity': float(specular_intensity),
            'subsurface_mm': float(subsurface),
            'key_light_multiplier': float(1.0 + melanin * 3.0),  # Dark skin needs 2-4x light
        })
    return data

print("\nGenerating melanin spectrum training data...")
melanin_data = generate_melanin_spectrum(10000)
print(f"Generated {len(melanin_data)} melanin spectrum samples")

# ═══════════════════════════════════════════════════════
# 2. VANISHING POINT — Perspective Grid Training
# ═══════════════════════════════════════════════════════

def generate_perspective_grids(n_samples=5000):
    """Generate vanishing point perspective grids for training."""
    data = []
    for _ in range(n_samples):
        # Random vanishing point
        vp_x = np.random.uniform(-1, 1)
        vp_y = np.random.uniform(-0.5, 0.5)
        vp_z = np.random.uniform(5, 50)  # Depth
        
        # Horizon line
        horizon_y = np.random.uniform(-0.3, 0.3)
        
        # Number of perspective lines
        n_lines = np.random.randint(4, 16)
        lines = []
        for i in range(n_lines):
            angle = np.random.uniform(0, np.pi * 2)
            spread = np.random.uniform(0.1, 2.0)
            lines.append({
                'angle': float(angle),
                'spread': float(spread),
                'start_x': float(np.cos(angle) * spread),
                'start_y': float(np.sin(angle) * spread * 0.3),
            })
        
        data.append({
            'vanishing_point': [float(vp_x), float(vp_y), float(vp_z)],
            'horizon_y': float(horizon_y),
            'lines': lines,
            'fov': float(np.random.uniform(30, 90)),
            'camera_height': float(np.random.uniform(0.5, 3.0)),
        })
    return data

print("Generating vanishing point training data...")
vp_data = generate_perspective_grids(5000)
print(f"Generated {len(vp_data)} perspective grids")

# ═══════════════════════════════════════════════════════
# 3. RAYTRACING — BRDF Sampling Training
# ═══════════════════════════════════════════════════════

def generate_brdf_samples(n_samples=20000):
    """Generate BRDF samples for raytracing training — PBR material responses."""
    data = []
    materials = ['concrete', 'wood', 'metal', 'glass', 'fabric', 'stone', 'plastic', 'skin']
    
    for _ in range(n_samples):
        mat = np.random.choice(materials)
        # Incident light angle
        theta_i = np.random.uniform(0, np.pi/2)
        phi_i = np.random.uniform(0, np.pi*2)
        # Viewing angle
        theta_o = np.random.uniform(0, np.pi/2)
        
        # Material parameters
        roughness = np.random.beta(2, 2)
        metallic = np.random.random() if mat == 'metal' else np.random.beta(1, 5) * 0.1
        albedo = np.random.uniform(0.02, 0.95)
        
        # Simplified microfacet BRDF
        half_theta = (theta_i + theta_o) / 2
        # Fresnel (Schlick)
        f0 = 0.04 + metallic * (albedo - 0.04)
        fresnel = f0 + (1 - f0) * (1 - np.cos(half_theta))**5
        # Normal distribution (GGX)
        a = roughness**2
        ndf = a**2 / (np.pi * (np.cos(half_theta)**2 * (a**2 - 1) + 1)**2 + 1e-8)
        # Geometry
        g1_i = 2 / (1 + np.sqrt(1 + a**2 * np.tan(theta_i)**2))
        g1_o = 2 / (1 + np.sqrt(1 + a**2 * np.tan(theta_o)**2))
        geometry = g1_i * g1_o
        
        specular = fresnel * ndf * geometry / (4 * np.cos(theta_i) * np.cos(theta_o) + 1e-8)
        diffuse = albedo / np.pi
        
        data.append({
            'material': mat,
            'theta_i': float(theta_i), 'phi_i': float(phi_i),
            'theta_o': float(theta_o),
            'roughness': float(roughness), 'metallic': float(metallic),
            'albedo': float(albedo),
            'fresnel': float(fresnel), 'ndf': float(ndf),
            'specular': float(specular), 'diffuse': float(diffuse),
            'reflectance': float(specular + diffuse),
        })
    return data

print("Generating BRDF raytracing training data...")
brdf_data = generate_brdf_samples(20000)
print(f"Generated {len(brdf_data)} BRDF samples")

# ═══════════════════════════════════════════════════════
# 4. EXPORT — Save to Kaggle dataset
# ═══════════════════════════════════════════════════════
output_dir = Path('/kaggle/working/trench_training')
output_dir.mkdir(exist_ok=True)

# Save as compressed numpy arrays for efficient loading
np.savez_compressed(output_dir / 'melanin_spectrum.npz', 
                    melanin=[d['melanin'] for d in melanin_data],
                    colors=[d['color_rgb'] for d in melanin_data],
                    roughness=[d['roughness'] for d in melanin_data],
                    specular=[d['specular_intensity'] for d in melanin_data])

np.savez_compressed(output_dir / 'vanishing_points.npz',
                    vp_x=[d['vanishing_point'][0] for d in vp_data],
                    vp_y=[d['vanishing_point'][1] for d in vp_data],
                    vp_z=[d['vanishing_point'][2] for d in vp_data],
                    horizons=[d['horizon_y'] for d in vp_data])

np.savez_compressed(output_dir / 'brdf_samples.npz',
                    materials=[d['material'] for d in brdf_data],
                    roughness=[d['roughness'] for d in brdf_data],
                    metallic=[d['metallic'] for d in brdf_data],
                    reflectance=[d['reflectance'] for d in brdf_data])

# Full JSON export for inspection
with open(output_dir / 'training_manifest.json', 'w') as f:
    json.dump({
        'version': '1.0',
        'generated': '2026-05-15',
        'datasets': {
            'melanin_spectrum': {'samples': len(melanin_data), 'features': ['melanin', 'color_rgb', 'roughness', 'specular', 'subsurface', 'key_light']},
            'vanishing_points': {'samples': len(vp_data), 'features': ['vanishing_point', 'horizon_y', 'fov', 'lines']},
            'brdf_samples': {'samples': len(brdf_data), 'features': ['material', 'roughness', 'metallic', 'reflectance']},
        },
        'total_samples': len(melanin_data) + len(vp_data) + len(brdf_data),
    }, f, indent=2)

print(f"\n✓ Training data exported to {output_dir}")
print(f"  Melanin spectrum: {len(melanin_data):,} samples")
print(f"  Vanishing points: {len(vp_data):,} samples")
print(f"  BRDF raytracing: {len(brdf_data):,} samples")
print(f"  Total: {len(melanin_data)+len(vp_data)+len(brdf_data):,} training samples")

# ═══════════════════════════════════════════════════════
# 5. GPU BENCHMARK — Quick render test
# ═══════════════════════════════════════════════════════
print("\n--- GPU BENCHMARK ---")
import time

# Matrix multiplication stress test
size = 2048
a = np.random.randn(size, size).astype(np.float32)
b = np.random.randn(size, size).astype(np.float32)

t0 = time.time()
for _ in range(3):
    c = a @ b
dt = time.time() - t0
gflops = (2 * size**3 * 3) / (dt * 1e9)
print(f"  {size}×{size} matmul ×3: {dt:.2f}s ({gflops:.1f} GFLOPS)")
print(f"  Memory: {a.nbytes/1e9:.1f} GB per matrix")

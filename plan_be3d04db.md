# Hyper-Realistic Character Evolution Plan

The objective is to synthesize a hyper-realistic character presentation over the existing Layer 1 mechanical integrity. We will replace basic WebGL materials with physical transmission approximations, introduce robust analytic collisions for the Verlet cloth, and upgrade the skin lofting to support secondary inertia (jiggle physics).

## User Review Required
> [!IMPORTANT]
> **Performance Overhead**
> Upgrading to `MeshPhysicalMaterial` with transmission and adding analytic sphere/cylinder colliders will increase GPU and CPU load. Ensure the target environment can sustain this. 
> 
> Please review the proposed changes below. If approved, I will begin execution immediately.

## Proposed Changes

---

### Layer 0: Volumetric Depth & PBR (Materials)

#### [MODIFY] main.js
- Upgrade `physMat` to utilize `THREE.MeshPhysicalMaterial` instead of `MeshStandardMaterial`.
- **Subsurface Scattering (SSS) Approximation:** Configure `skinMat` with `transmission`, `thickness`, `attenuationColor` (deep red/pink), and `attenuationDistance` to simulate flesh scattering light.
- **Micro-surface details:** Add `clearcoat` and `clearcoatRoughness` to the `armorMat` and `goldMat` for hyper-realistic metallic sheens.

### Layer 1: Mechanical Integrity (Physics & Collision)

#### [MODIFY] main.js
- **Analytic Body Colliders:** Define a global array of collision primitives (e.g., `colliders = [{ type: 'sphere', pos: Vector3, radius: R }, ...]`) mapped to the torso, hips, and legs of the character.
- **Robust Cloth Collision:** Modify `ClothLayer.step()` to check every cloth node against the body colliders and project them outward along the normal if they penetrate. This ensures the robes drape *over* the body instead of passing through it.
- **Procedural Breathing / Posing:** Introduce a procedural sine-wave animation to the armature groups (chest expansion, shoulder rotation) to give the character life.

### Layer 2: Ambient Composite (Soft-Body Lofting)

#### [MODIFY] main.js
- **Secondary Inertia (Jiggle):** Modify `SkinLoftPatch.step()` to track vertex velocity and apply a harmonic oscillator formula. This transitions the skin patches from purely wind-driven motion to reacting to the character's procedural breathing and movements with realistic, delayed momentum.
- **Dynamic Anchoring:** Bind the `SkinLoftPatch` anchor functions to the moving armature transforms so the skin correctly follows the animated skeleton.

## Verification Plan

### Automated Tests
- N/A (WebGL canvas visual inspection required).

### Manual Verification
- Spin the camera to verify the light transmits through the skin patches (SSS effect).
- Observe the cloth nodes resting on the character's legs/torso without clipping.
- Verify the skin patches jiggle slightly as the character breathes.

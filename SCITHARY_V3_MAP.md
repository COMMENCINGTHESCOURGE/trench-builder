# SCITHARY GENERATOR v3.0.0 (3D) — Territory Command Interface
# May 17, 2026

SCITHARY_V3 = """
VERSION JUMP: v2 (Canvas 2D map) → v3 (Three.js 3D space)

7 SECTORS in 3D space:
  VORANIS     Mining Colony    ALLIED     cyan     86% INTEGRITY
  ZETA PRIME  Research Outpost UNKNOWN    purple   72%
  KRYPTOS     Fortress World   ALLIED     cyan     91%
  NEXUS-7     Trade Hub        ALLIED     cyan     94%
  THALASSIA   Ocean World      CONTESTED  amber    78%
  EIDOLON     Dead Zone        HOSTILE    magenta  63%
  ORION BELT  Asteroid Field   CONTESTED  amber    68%

8 CONNECTIONS — Voranis→Kryptos→Thalassia→Nexus-7→Eidolon etc.

TECH STACK:
  Three.js 0.160 (ES modules + importmap)
  OrbitControls + UnrealBloomPass (post-processing)
  Raycaster for 3D click interaction
  HTML labels projected from 3D→2D per frame
  CSS 3D transforms for cockpit panel perspective
  Glass-morphism panels with backdrop-filter
  Chromatic aberration overlay for hostile sectors

DATA: Embedded JS config (sectorsData, connections).
      Kaggle notebook can regenerate this data.
"""

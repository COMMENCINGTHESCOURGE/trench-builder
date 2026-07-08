"""
Trench-Builder Environment Domain — trees, rocks, bushes, plants.

Each asset is a minimal ComponentSpec tree feeding the Blender builder.
Output: GLB files ready for GLTFLoader in browser games.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..core.component_spec import AssemblySpec, ComponentSpec
from ..core.vinculum import JointType, Vinculum, Constraint


# ═══════════════════════════════════════════════════════
# Environment asset types
# ═══════════════════════════════════════════════════════

@dataclass
class EnvironmentAssembly(AssemblySpec):
    """A tree, rock, or bush assembly for terrain decoration."""
    domain: str = "environment"
    asset_type: str = ""          # "tree", "rock", "bush", "plant"
    variant: str = ""             # "pine", "boulder", "round", etc.
    biome: str = ""               # "forest", "plains", "rocky", "mountain", "any"
    scale_range: tuple = (0.8, 1.2)
    material_color: tuple = (0.5, 0.5, 0.5, 1.0)
    glb_export_name: str = ""

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "asset_type": self.asset_type,
            "variant": self.variant,
            "biome": self.biome,
            "scale_range": self.scale_range,
            "material_color": self.material_color,
            "glb_export_name": self.glb_export_name,
        })
        return d


# ═══════════════════════════════════════════════════════
# Factory: tree variants
# ═══════════════════════════════════════════════════════

def make_tree(variant: str, biome: str, trunk_color: tuple, foliage_color: tuple,
              height: float = 3.0, trunk_radius: float = 0.25, canopy_radius: float = 1.5) -> EnvironmentAssembly:
    return EnvironmentAssembly(
        model_id=f"tree_{variant}_v1",
        asset_type="tree",
        variant=variant,
        biome=biome,
        scale_range=(0.7, 1.3),
        material_color=trunk_color,
        glb_export_name=f"tree_{variant}.glb",
        components=[
            ComponentSpec(name="trunk", component_type="trunk",
                joint_type=JointType.FIXED,
                parameters={"height": height * 0.6, "radius": trunk_radius, "color": trunk_color}),
            ComponentSpec(name="canopy", component_type="foliage", parent="trunk",
                joint_type=JointType.FIXED,
                parameters={"radius": canopy_radius, "height": height * 0.4, "color": foliage_color,
                           "shape": "cone" if variant == "pine" else "sphere", "density": 3}),
        ],
        global_vinculum=Vinculum(domain="environment").add(
            Constraint.ratio("canopy_to_trunk_ratio", canopy_radius / trunk_radius, 0.3)
        ),
    )


def make_rock(variant: str, biome: str, color: tuple, size: float = 1.5,
              subdivisions: int = 3, displacement: float = 0.3) -> EnvironmentAssembly:
    return EnvironmentAssembly(
        model_id=f"rock_{variant}_v1",
        asset_type="rock",
        variant=variant,
        biome=biome,
        scale_range=(0.5, 1.5),
        material_color=color,
        glb_export_name=f"rock_{variant}.glb",
        components=[
            ComponentSpec(name="body", component_type="rock",
                joint_type=JointType.FIXED,
                parameters={"size": size, "subdivisions": subdivisions,
                           "displacement": displacement, "color": color,
                           "shape": variant}),
        ],
    )


def make_bush(variant: str, biome: str, color: tuple, size: float = 1.0,
              cluster_count: int = 5) -> EnvironmentAssembly:
    return EnvironmentAssembly(
        model_id=f"bush_{variant}_v1",
        asset_type="bush",
        variant=variant,
        biome=biome,
        scale_range=(0.6, 1.4),
        material_color=color,
        glb_export_name=f"bush_{variant}.glb",
        components=[
            ComponentSpec(name="body", component_type="bush",
                joint_type=JointType.FIXED,
                parameters={"size": size, "cluster_count": cluster_count,
                           "color": color, "shape": variant}),
        ],
    )


# ═══════════════════════════════════════════════════════
# FULL CATALOG
# ═══════════════════════════════════════════════════════

ENVIRONMENT_CATALOG: Dict[str, EnvironmentAssembly] = {}

# -- TREES (4 variants across biomes) --
ENVIRONMENT_CATALOG["tree_pine"] = make_tree(
    "pine", "forest",
    trunk_color=(0.25, 0.18, 0.12, 1.0),
    foliage_color=(0.08, 0.35, 0.15, 1.0),
    height=4.0, trunk_radius=0.3, canopy_radius=1.8,
)

ENVIRONMENT_CATALOG["tree_oak"] = make_tree(
    "oak", "forest",
    trunk_color=(0.35, 0.25, 0.15, 1.0),
    foliage_color=(0.10, 0.40, 0.12, 1.0),
    height=3.5, trunk_radius=0.4, canopy_radius=2.2,
)

ENVIRONMENT_CATALOG["tree_dead"] = make_tree(
    "dead", "rocky",
    trunk_color=(0.20, 0.18, 0.16, 1.0),
    foliage_color=(0.15, 0.12, 0.10, 1.0),
    height=3.0, trunk_radius=0.2, canopy_radius=0.3,
)

ENVIRONMENT_CATALOG["tree_alien"] = make_tree(
    "alien", "mountain",
    trunk_color=(0.15, 0.10, 0.25, 1.0),
    foliage_color=(0.45, 0.15, 0.55, 1.0),
    height=5.0, trunk_radius=0.35, canopy_radius=2.5,
)

# -- ROCKS (4 variants) --
ENVIRONMENT_CATALOG["rock_boulder"] = make_rock(
    "boulder", "any",
    color=(0.30, 0.28, 0.26, 1.0),
    size=1.5, subdivisions=4, displacement=0.25,
)

ENVIRONMENT_CATALOG["rock_crystal"] = make_rock(
    "crystal", "mountain",
    color=(0.35, 0.25, 0.45, 1.0),
    size=1.8, subdivisions=2, displacement=0.5,
)

ENVIRONMENT_CATALOG["rock_slab"] = make_rock(
    "slab", "rocky",
    color=(0.40, 0.38, 0.35, 1.0),
    size=2.0, subdivisions=3, displacement=0.15,
)

ENVIRONMENT_CATALOG["rock_cluster"] = make_rock(
    "cluster", "any",
    color=(0.32, 0.30, 0.28, 1.0),
    size=1.0, subdivisions=3, displacement=0.35,
)

# -- BUSHES (3 variants) --
ENVIRONMENT_CATALOG["bush_round"] = make_bush(
    "round", "plains",
    color=(0.12, 0.38, 0.18, 1.0),
    size=1.0, cluster_count=5,
)

ENVIRONMENT_CATALOG["bush_spiky"] = make_bush(
    "spiky", "rocky",
    color=(0.15, 0.30, 0.12, 1.0),
    size=0.8, cluster_count=7,
)

ENVIRONMENT_CATALOG["bush_flowering"] = make_bush(
    "flowering", "plains",
    color=(0.20, 0.35, 0.15, 1.0),
    size=1.2, cluster_count=4,
)

# ═══════════════════════════════════════════════════════
# Lookup
# ═══════════════════════════════════════════════════════

def get_asset(name: str) -> Optional[EnvironmentAssembly]:
    return ENVIRONMENT_CATALOG.get(name)

def assets_by_type(asset_type: str) -> List[EnvironmentAssembly]:
    return [a for a in ENVIRONMENT_CATALOG.values() if a.asset_type == asset_type]

def assets_by_biome(biome: str) -> List[EnvironmentAssembly]:
    return [a for a in ENVIRONMENT_CATALOG.values() if a.biome == biome or a.biome == "any"]

def all_assets() -> List[EnvironmentAssembly]:
    return list(ENVIRONMENT_CATALOG.values())

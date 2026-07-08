"""
Trench-Builder Character Domain.

Each character is an AssemblySpec with character-specific metadata:
  - lore: backstory and dialogue seeds (from b_roll_scenarios.js)
  - sprite_params: sprite sheet references for 2D/UI rendering
  - mechanics: gameplay hooks (missions, abilities, faction_affinity)
  - body_parts: standardized ComponentSpec tree (torso, limbs, head, gear)

All five b_roll characters defined as module-level constants.
Builder backends consume CharacterAssembly to generate:
  - Blender GLB with proper joint hierarchy
  - Sprite sheet UV maps + frame layouts
  - Dialogue event trees
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal

from ..core.component_spec import AssemblySpec, ComponentSpec
from ..core.vinculum import JointType, Vinculum, Constraint, ConstraintKind


# ═══════════════════════════════════════════════════════
# Character-specific types
# ═══════════════════════════════════════════════════════

BodyPart = Literal["torso", "head", "left_arm", "right_arm", "left_leg", "right_leg", "gear"]
LimbType = Literal["humanoid", "mecha", "organic", "corrupted", "reinforced"]
Faction = Literal["kraken", "dim_mak", "aku_aku", "grief_wastes", "mecha_station", "nexus"]
MissionTrigger = Literal["ransom_run", "false_flag", "inside_man", "debt_trap", "grey_market", "awakening", "betrayal", "mutiny"]


@dataclass
class CharacterAssembly(AssemblySpec):
    """
    A character is an assembly of body-part ComponentSpecs plus
    narrative and gameplay metadata.
    
    Inherits from AssemblySpec for component hierarchy, serialization,
    and vinculum validation. Adds character-specific fields that
    builder backends query for sprite/dialogue/ability generation.
    """
    domain: str = "character"

    # Narrative identity (from b_roll_scenarios.js)
    character_name: str = ""
    role: str = ""
    archetype: str = ""
    lore: str = ""
    dialogue_seeds: List[str] = field(default_factory=list)

    # Visual identity
    sprite_params: Dict = field(default_factory=dict)
    glb_export_name: str = ""

    # Gameplay
    faction: Optional[Faction] = None
    abilities: List[str] = field(default_factory=list)
    mission_triggers: List[MissionTrigger] = field(default_factory=list)
    stats: Dict[str, float] = field(default_factory=dict)

    # Generated asset paths (lazy, filled by builders)
    glb_path: Optional[str] = None
    sprite_sheet_path: Optional[str] = None

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "character_name": self.character_name,
            "role": self.role,
            "archetype": self.archetype,
            "lore": self.lore,
            "dialogue_seeds": self.dialogue_seeds,
            "sprite_params": self.sprite_params,
            "glb_export_name": self.glb_export_name,
            "faction": self.faction,
            "abilities": self.abilities,
            "mission_triggers": self.mission_triggers,
            "stats": self.stats,
            "glb_path": self.glb_path,
            "sprite_sheet_path": self.sprite_sheet_path,
        })
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "CharacterAssembly":
        base = AssemblySpec.from_dict(data)
        return cls(
            model_id=base.model_id,
            domain="character",
            components=base.components,
            global_vinculum=base.global_vinculum,
            metadata=base.metadata,
            version=base.version,
            character_name=data.get("character_name", ""),
            role=data.get("role", ""),
            archetype=data.get("archetype", ""),
            lore=data.get("lore", ""),
            dialogue_seeds=data.get("dialogue_seeds", []),
            sprite_params=data.get("sprite_params", {}),
            glb_export_name=data.get("glb_export_name", ""),
            faction=data.get("faction"),
            abilities=data.get("abilities", []),
            mission_triggers=data.get("mission_triggers", []),
            stats=data.get("stats", {}),
            glb_path=data.get("glb_path"),
            sprite_sheet_path=data.get("sprite_sheet_path"),
        )


# ═══════════════════════════════════════════════════════
# Body-part factory functions
# ═══════════════════════════════════════════════════════

def make_torso(
    torso_type: str = "standard",
    scale: float = 1.0,
    mount_points: List[str] = None,
) -> ComponentSpec:
    """Factory for torso components with mount points for limbs and head."""
    return ComponentSpec(
        name="torso",
        component_type="torso",
        parent=None,  # Torso is always root
        joint_type=JointType.FIXED,
        vinculum=Vinculum(domain="character")
            .add(Constraint.ratio("torso_height_to_total", 0.35, 0.05, "Torso ~35% of height")),
        parameters={
            "torso_type": torso_type,
            "scale": scale,
        },
        mount_points=mount_points or ["head", "l_shoulder", "r_shoulder", "hips"],
        tags=["torso", torso_type],
    )


def make_limb(
    name: str,
    limb_type: LimbType = "humanoid",
    parent: str = "torso",
    joint_type: JointType = JointType.REVOLUTE,
    joint_axis: str = "Z",
    joint_limits: tuple = (-90, 90),
    length: float = 1.0,
    scale: float = 1.0,
    mount_points: List[str] = None,
) -> ComponentSpec:
    """Factory for arm/leg components."""
    desc = f"{limb_type} {name.replace('_', ' ')}"
    vinc = Vinculum(domain="character").add(
        Constraint.ratio(f"{name}_length_to_torso", length, 0.08, f"{desc} length constraint")
    )
    if limb_type == "corrupted":
        vinc = Vinculum.corrupted()

    return ComponentSpec(
        name=name,
        component_type="limb",
        parent=parent,
        joint_type=joint_type,
        joint_axis=joint_axis,
        joint_limits=joint_limits,
        vinculum=vinc,
        parameters={
            "limb_type": limb_type,
            "length": length,
            "scale": scale,
        },
        mount_points=mount_points or [],
        tags=["limb", limb_type, name],
    )


def make_head(
    head_type: str = "standard",
    parent: str = "torso",
    scale: float = 1.0,
) -> ComponentSpec:
    """Factory for head components."""
    return ComponentSpec(
        name="head",
        component_type="head",
        parent=parent,
        joint_type=JointType.BALL_SOCKET,
        joint_axis="Z",
        joint_limits=(-70, 70),
        vinculum=Vinculum(domain="character").add(
            Constraint.ratio("head_height_to_total", 0.125, 0.03, "Head ~12.5% of height")
        ),
        parameters={
            "head_type": head_type,
            "scale": scale,
        },
        mount_points=["neck"],
        tags=["head", head_type],
    )


def make_gear(
    name: str,
    gear_type: str,
    parent: str,
    scale: float = 1.0,
    parameters: Dict = None,
) -> ComponentSpec:
    """Factory for equipment/gear attached to a body part."""
    return ComponentSpec(
        name=name,
        component_type="gear",
        parent=parent,
        joint_type=JointType.FIXED,
        parameters={
            "gear_type": gear_type,
            "scale": scale,
            **(parameters or {}),
        },
        tags=["gear", gear_type],
    )


# ═══════════════════════════════════════════════════════
# Standard body templates
# ═══════════════════════════════════════════════════════

def standard_body(
    limb_type: LimbType = "humanoid",
    torso_type: str = "standard",
    head_type: str = "standard",
    scale: float = 1.0,
) -> List[ComponentSpec]:
    """Generate a standard bipedal body with all limbs."""
    return [
        make_torso(torso_type=torso_type, scale=scale),
        make_limb("left_arm", limb_type=limb_type, parent="torso",
                  joint_limits=(-90, 180), length=0.8),
        make_limb("right_arm", limb_type=limb_type, parent="torso",
                  joint_limits=(-90, 180), length=0.8),
        make_limb("left_leg", limb_type=limb_type, parent="torso",
                  joint_limits=(-45, 120), length=1.1),
        make_limb("right_leg", limb_type=limb_type, parent="torso",
                  joint_limits=(-45, 120), length=1.1),
        make_head(head_type=head_type, scale=scale * 0.85),
    ]


# ═══════════════════════════════════════════════════════
# b_roll CHARACTERS — full CharacterAssembly specs
# ═══════════════════════════════════════════════════════

# -- KAEL VOS: Disposable Wingman --
kael_vos = CharacterAssembly(
    model_id="kael_vos_v1",
    character_name="Kael Vos",
    role="Disposable Wingman",
    archetype="Loyal until the price is right",
    lore=(
        "Flies with you for 10 missions. On the 11th, a rival offers him 3x your "
        "net worth. He takes it. But he leaves a back door in his ship systems — "
        "he wants to be caught. He wants you to stop him."
    ),
    dialogue_seeds=[
        "\"I didn't betray you for money. I betrayed you so you would finally take me seriously.\"",
        "\"The back door is still open. I never closed it. I was waiting for you to notice.\"",
    ],
    sprite_params={
        "sheet": "mecha_walk_4_corrupted.png",
        "frame_count": 4,
        "palette": "corrupted_teal",
        "variant": "corrupted",
    },
    glb_export_name="kael_vos.glb",
    faction="grief_wastes",
    abilities=["corrupted_overdrive", "joint_lock", "back_door_access"],
    mission_triggers=["awakening", "betrayal"],
    stats={
        "loyalty": 0.3,        # Low — will betray on mission 11
        "combat": 0.7,
        "stealth": 0.5,
        "negotiation": 0.4,
    },
    components=standard_body("corrupted", "corrupted", "corrupted", scale=1.0),
    global_vinculum=Vinculum.corrupted(),
)

# -- SERA QIN: The Informant --
sera_qin = CharacterAssembly(
    model_id="sera_qin_v1",
    character_name="Sera Qin",
    role="The Informant",
    archetype="Knows everything, tells nothing",
    lore=(
        "Feeds you tips that are always accurate but always incomplete. Each tip "
        "makes you money AND creates an enemy. She is building a network of people "
        "who owe her — and you're the glue."
    ),
    dialogue_seeds=[
        "\"I told you where the cargo was. I didn't tell you who else knew. That costs extra.\"",
        "\"Information is the only currency that appreciates the more you spend it.\"",
    ],
    sprite_params={
        "sheet": "dim_mak_fighter_full_sheet.jpg",
        "frame_count": 6,
        "palette": "dim_mak_crimson",
        "variant": "stealth",
    },
    glb_export_name="sera_qin.glb",
    faction="dim_mak",
    abilities=["info_network", "double_tip", "enemy_catalog"],
    mission_triggers=["inside_man", "false_flag"],
    stats={
        "loyalty": 0.1,        # Sells same info to everyone
        "combat": 0.3,
        "stealth": 0.9,
        "negotiation": 0.95,
    },
    components=standard_body("humanoid", "standard", "standard", scale=0.92),
    global_vinculum=Vinculum.humanoid(),
)

# -- GORATH VEHN: The Old Guard --
gorath_vehn = CharacterAssembly(
    model_id="gorath_vehn_v1",
    character_name="Gorath Vehn",
    role="The Old Guard",
    archetype="Retired legend, pulled back in",
    lore=(
        "Was Galactic Overlord for 12 consecutive cycles before 'retiring.' He "
        "mentors you. Every piece of advice is correct. Every piece of advice also "
        "advances his hidden agenda: reclaiming his throne by making you dependent "
        "on him. He's dying. He has 30 days. He's not training a successor — he's "
        "writing his legacy through your story."
    ),
    dialogue_seeds=[
        "\"I built this empire. I can rebuild it through you. The question is: will you step aside when I ask?\"",
        "\"Thirty days. That's what the medic gave me. But empires aren't built in thirty days. They're built in thirty years. And I've already spent those.\"",
    ],
    sprite_params={
        "sheet": "kraken_mech_render.jpg",
        "frame_count": 4,
        "palette": "kraken_gold",
        "variant": "reinforced",
    },
    glb_export_name="gorath_vehn.glb",
    faction="kraken",
    abilities=["overlord_tactics", "mentor_aura", "legacy_burn"],
    mission_triggers=["ransom_run", "debt_trap"],
    stats={
        "loyalty": 0.9,        # Loyal — but with hidden agenda
        "combat": 0.95,
        "stealth": 0.6,
        "negotiation": 0.85,
    },
    components=standard_body("reinforced", "reinforced", "standard", scale=1.15),
    global_vinculum=Vinculum.mecha(),
)

# -- THE TWINS: Mir + Kor --
the_twins = CharacterAssembly(
    model_id="the_twins_v1",
    character_name="The Twins (Mir + Kor)",
    role="Split Personality Crew",
    archetype="One honest, one corrupt",
    lore=(
        "You never know which twin you're dealing with. Mir runs fair trades. Kor "
        "skims 20% off every deal. Their ship transponder is identical. You must "
        "learn their behavioral tells — or always assume Kor. There are no twins. "
        "It's one person with a personality disorder who genuinely believes they "
        "are two people. The skimmed credits go to an account neither personality "
        "knows about."
    ),
    dialogue_seeds=[
        "\"I'm Mir today. Yesterday I was Kor. Tomorrow? Depends who's asking.\"",
        "\"Mir made this deal. I'm just... delivering it. With a surcharge.\"",
    ],
    sprite_params={
        "sheet": "void_runner_ship.png",  # Twin ship
        "alt_sheet": "mecha_walk_4_stealth.png",
        "frame_count": 4,
        "palette": "split_duality",
        "variant": "dual",
        "mir_palette": "pure_white",
        "kor_palette": "shadow_black",
    },
    glb_export_name="the_twins.glb",
    faction="mecha_station",
    abilities=["personality_swap", "skimmer", "dual_transponder"],
    mission_triggers=["inside_man", "grey_market"],
    stats={
        "loyalty": 0.5,        # Average of Mir(1.0) and Kor(0.0)
        "combat": 0.4,
        "stealth": 0.7,
        "negotiation": 0.6,    # Unpredictable
    },
    components=standard_body("organic", "standard", "standard", scale=0.95),
    global_vinculum=Vinculum.humanoid(),
)

# -- AYA NOX: The Rival --
aya_nox = CharacterAssembly(
    model_id="aya_nox_v1",
    character_name="Aya Nox",
    role="The Rival",
    archetype="Respects you, will destroy you",
    lore=(
        "Runs identical routes. Undercuts your prices. Saves your life from a "
        "police raid — then sends you the bill. The rivalry is genuine, the respect "
        "is genuine, and one of you will put the other out of business. She's your "
        "character from a previous playthrough. The game remembers. She has your "
        "old inventory, your old rank, your old debts."
    ),
    dialogue_seeds=[
        "\"I don't hate you. I am you, six months from now, if you make the choices I made. I'm trying to stop that.\"",
        "\"Check your old cargo manifest. Every item I sell, you owned first. I'm just... returning the favor.\"",
    ],
    sprite_params={
        "sheet": "grief_warrior_sprite_sheet.jpg",
        "frame_count": 8,
        "palette": "ghost_mirror",
        "variant": "overcharge",
    },
    glb_export_name="aya_nox.glb",
    faction="aku_aku",
    abilities=["mirror_route", "undercut", "previous_save_data"],
    mission_triggers=["ransom_run", "debt_trap", "mutiny"],
    stats={
        "loyalty": 0.0,        # Rival — respects you but oppositional
        "combat": 0.7,
        "stealth": 0.6,
        "negotiation": 0.8,
    },
    components=standard_body("mecha", "standard", "standard", scale=1.0),
    global_vinculum=Vinculum.mecha(),
)


# ═══════════════════════════════════════════════════════
# Character registry — all characters indexed by name
# ═══════════════════════════════════════════════════════

CHARACTER_REGISTRY: Dict[str, CharacterAssembly] = {
    "kael_vos": kael_vos,
    "sera_qin": sera_qin,
    "gorath_vehn": gorath_vehn,
    "the_twins": the_twins,
    "aya_nox": aya_nox,
}


def get_character(name: str) -> Optional[CharacterAssembly]:
    """Look up a character by name or model_id."""
    for key, char in CHARACTER_REGISTRY.items():
        if char.character_name.lower() == name.lower() or char.model_id == name:
            return char
    return None


def all_characters() -> List[CharacterAssembly]:
    return list(CHARACTER_REGISTRY.values())


def all_character_names() -> List[str]:
    return [c.character_name for c in CHARACTER_REGISTRY.values()]


# ═══════════════════════════════════════════════════════
# Bulk export — dump all characters as JSON/YAML
# ═══════════════════════════════════════════════════════

def export_all_json(indent: int = 2) -> str:
    """Serialize all characters to JSON string."""
    import json
    return json.dumps(
        {key: char.to_dict() for key, char in CHARACTER_REGISTRY.items()},
        indent=indent,
    )


def export_all_yaml() -> str:
    """Serialize all characters to YAML string."""
    import yaml
    return yaml.dump(
        {key: char.to_dict() for key, char in CHARACTER_REGISTRY.items()},
        default_flow_style=False,
        sort_keys=False,
    )


def generate_character(model_id: str = "character_v1", height_mm: float = 100.0) -> AssemblySpec:
    """Generate a 22-bone character rig with Gunpla engineering constraints.
    
    Proportions from anatomical vinculum ratios:
      head/height=0.15, torso/height=0.35, arm/height=0.38, leg/height=0.50
    """
    h = height_mm
    spec = AssemblySpec(
        model_id=model_id,
        domain="character",
        global_vinculum=Vinculum("character", {
            "head_height_total_ratio": 0.15,
            "torso_height_total_ratio": 0.35,
            "arm_length_total_ratio": 0.38,
            "leg_length_total_ratio": 0.50,
            "hand_length_total_ratio": 0.11,
            "foot_length_total_ratio": 0.16,
        }),
        metadata={"material": "PLA", "tolerance_mm": 0.20, "height_mm": h, "poly_target": 2500},
    )

    # Root → Pelvis → Spine chain
    spec.add(ComponentSpec("PELVIS", JointType.FIXED, parent=None,
        parameters={"width_mm": h * 0.15}))

    spec.add(ComponentSpec("SPINE_LOWER", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-15, 15),
        parent="PELVIS"))

    spec.add(ComponentSpec("SPINE_UPPER", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-15, 15),
        parent="SPINE_LOWER"))

    spec.add(ComponentSpec("TORSO", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-30, 30),
        parent="SPINE_UPPER",
        vinculum=Vinculum("character", {"torso_height_total_height_ratio": 0.35})))

    # Neck → Head
    spec.add(ComponentSpec("NECK", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-45, 45),
        parent="TORSO"))

    spec.add(ComponentSpec("HEAD", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-70, 70),
        parent="NECK",
        vinculum=Vinculum("character", {"head_height_total_height_ratio": 0.15})))

    # Left arm — butterfly shoulder + swivel cut
    spec.add(ComponentSpec("SHOULDER_L", JointType.BUTTERFLY, joint_axis="Z", joint_limits=(-90, 90),
        parent="TORSO",
        vinculum=Vinculum("character", {"joint_type": "butterfly", "forward_sweep_deg": 30})))

    spec.add(ComponentSpec("BICEP_SWIVEL_L", JointType.SWIVEL_CUT, joint_axis="Y", joint_limits=(-90, 90),
        parent="SHOULDER_L",
        vinculum=Vinculum("character", {"swivel_cut": True, "isolated_yaw": True})))

    spec.add(ComponentSpec("UPPER_ARM_L", JointType.REVOLUTE, joint_axis="X", joint_limits=(-135, 45),
        parent="BICEP_SWIVEL_L",
        vinculum=Vinculum("character", {"arm_length_total_height_ratio": 0.38})))

    spec.add(ComponentSpec("FOREARM_L", JointType.REVOLUTE, joint_axis="X", joint_limits=(0, 150),
        parent="UPPER_ARM_L",
        vinculum=Vinculum("character", {"forearm_upper_arm_ratio": 0.85})))

    spec.add(ComponentSpec("HAND_L", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-90, 90),
        parent="FOREARM_L",
        vinculum=Vinculum("character", {"hand_length_total_height_ratio": 0.11, "finger_segments": 3})))

    # Right arm
    spec.add(ComponentSpec("SHOULDER_R", JointType.BUTTERFLY, joint_axis="Z", joint_limits=(-90, 90),
        parent="TORSO"))

    spec.add(ComponentSpec("BICEP_SWIVEL_R", JointType.SWIVEL_CUT, joint_axis="Y", joint_limits=(-90, 90),
        parent="SHOULDER_R"))

    spec.add(ComponentSpec("UPPER_ARM_R", JointType.REVOLUTE, joint_axis="X", joint_limits=(-135, 45),
        parent="BICEP_SWIVEL_R"))

    spec.add(ComponentSpec("FOREARM_R", JointType.REVOLUTE, joint_axis="X", joint_limits=(0, 150),
        parent="UPPER_ARM_R"))

    spec.add(ComponentSpec("HAND_R", JointType.REVOLUTE, joint_axis="Z", joint_limits=(-90, 90),
        parent="FOREARM_R"))

    # Left leg — ball-and-socket hip + double-hinge knee + swivel
    spec.add(ComponentSpec("HIP_L", JointType.BALL_AND_SOCKET, joint_axis="X", joint_limits=(-45, 120),
        parent="PELVIS",
        vinculum=Vinculum("character", {"hip_joint_type": "ball_and_socket"})))

    spec.add(ComponentSpec("THIGH_SWIVEL_L", JointType.SWIVEL_CUT, joint_axis="Y", joint_limits=(-45, 45),
        parent="HIP_L"))

    spec.add(ComponentSpec("UPPER_LEG_L", JointType.REVOLUTE, joint_axis="X", joint_limits=(-45, 120),
        parent="THIGH_SWIVEL_L",
        vinculum=Vinculum("character", {"leg_length_total_height_ratio": 0.50})))

    spec.add(ComponentSpec("KNEE_UPPER_L", JointType.REVOLUTE, joint_axis="X", joint_limits=(0, 90),
        parent="UPPER_LEG_L"))

    spec.add(ComponentSpec("KNEE_LOWER_L", JointType.REVOLUTE, joint_axis="X", joint_limits=(0, 90),
        parent="KNEE_UPPER_L",
        vinculum=Vinculum("character", {"knee_double_hinge": True})))

    spec.add(ComponentSpec("FOOT_L", JointType.BALL_AND_SOCKET, joint_axis="Z", joint_limits=(-30, 45),
        parent="KNEE_LOWER_L",
        vinculum=Vinculum("character", {"foot_length_total_height_ratio": 0.16})))

    # Right leg
    spec.add(ComponentSpec("HIP_R", JointType.BALL_AND_SOCKET, joint_axis="X", joint_limits=(-45, 120),
        parent="PELVIS"))

    spec.add(ComponentSpec("THIGH_SWIVEL_R", JointType.SWIVEL_CUT, joint_axis="Y", joint_limits=(-45, 45),
        parent="HIP_R"))

    spec.add(ComponentSpec("UPPER_LEG_R", JointType.REVOLUTE, joint_axis="X", joint_limits=(-45, 120),
        parent="THIGH_SWIVEL_R"))

    spec.add(ComponentSpec("KNEE_UPPER_R", JointType.REVOLUTE, joint_axis="X", joint_limits=(0, 90),
        parent="UPPER_LEG_R"))

    spec.add(ComponentSpec("KNEE_LOWER_R", JointType.REVOLUTE, joint_axis="X", joint_limits=(0, 90),
        parent="KNEE_UPPER_R"))

    spec.add(ComponentSpec("FOOT_R", JointType.BALL_AND_SOCKET, joint_axis="Z", joint_limits=(-30, 45),
        parent="KNEE_LOWER_R"))

    spec.metadata["bone_count"] = len(spec.components)
    return spec

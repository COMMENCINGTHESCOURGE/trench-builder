# CINEMATOGRAPHY STORYBOARDS — Reference Material
# From audio_spl_sq/ directory — 2 complete narrative sequences
# DaShawn / Guinea Pig Trench LLC — May 2026

# ═══════════════════════════════════════════════════════
# STORYBOARD 1: Epic Fantasy — "The Boy and the Sword"
# 085d27df-33c2-440c-95de-8c024a7276a5.png
# ═══════════════════════════════════════════════════════

EPIC_STORYBOARD = {
    "title": "The Boy and the Sword",
    "genre": "Epic Fantasy / Hero's Journey",
    "style": "Wide landscapes, castles, intimate close-ups, communal scenes",
    "scenes": [
        {"id": 1, "name": "Introduction",
         "shots": ["Wide landscape", "Castle establishing", "Young boy introduced", "Close-up of his hand"],
         "purpose": "Establish setting and protagonist"},
        
        {"id": 2, "name": "Connection",
         "shots": ["Boy and father", "Close-ups", "Two-shots"],
         "purpose": "Establish relationship and emotional core"},
        
        {"id": 3, "name": "The Great Hall",
         "shots": ["Communal dinner scene", "Father addresses assembly", "Crowd reactions"],
         "purpose": "World-building, stakes, community"},
        
        {"id": 4, "name": "The Turning Point",
         "shots": ["Father presents sword to boy", "Close-up: boy's determined expression"],
         "purpose": "Inciting incident — the gift of destiny"},
        
        {"id": 5, "name": "Training",
         "shots": ["Training yard progression", "Boy strikes down opponent", "Father watches approvingly"],
         "purpose": "Growth, skill acquisition, approval"},
        
        {"id": 6, "name": "Departure",
         "shots": ["Dusk lighting", "Torches lit", "Army departs", "Final close-up of boy"],
         "purpose": "Closure — the journey begins"},
    ]
}

# ═══════════════════════════════════════════════════════
# STORYBOARD 2: Urban Noir — "City Man" + TRANSITIONS
# 3b92f528-8eae-40bd-9301-623a403943e9.png
# ═══════════════════════════════════════════════════════

URBAN_STORYBOARD = {
    "title": "City Man",
    "genre": "Urban Mystery / Procedural Drama",
    "style": "Modern city, apartment interiors, office environments, explicit transitions",
    "scenes": [
        {"id": 1, "name": "Ext. City Street - Day",
         "shots": ["Bustling city", "Protagonist established"],
         "transition": "1A: Motion Blur to Interior"},
        
        {"id": 2, "name": "Int. Apartment - Day",
         "shots": ["Man in living space"],
         "transition": "2A: Match Cut (hand/object → coffee cup)"},
        
        {"id": 3, "name": "Int. Apartment - Continuous",
         "shots": ["Working", "Reading"],
         "transition": "3A: Dissolve to cityscape at twilight"},
        
        {"id": 4, "name": "Ext. City Street - Night",
         "shots": ["Protagonist on street at night"],
         "transition": "4A: Wipe to office"},
        
        {"id": 5, "name": "Int. Office - Night",
         "shots": ["Man in office at night"],
         "transition": "5A: Fade to Black"},
        
        {"id": 6, "name": "Int. Office - Continuous",
         "shots": ["Reviewing documents"],
         "transition": "6A: Cut to Next Scene"},
    ]
}

# ═══════════════════════════════════════════════════════
# TRANSITION GRAMMAR — 6 Named Types
# ═══════════════════════════════════════════════════════

TRANSITIONS = {
    "motion_blur": {
        "name": "Motion Blur to Interior",
        "use": "Scene 1→2: Exterior street → apartment interior",
        "cinematography_engine": "Rapid camera push + post-process blur pass",
        "veo_prompt": "fast dolly with radial blur dissolving into interior",
    },
    "match_cut": {
        "name": "Match Cut (hand/object → coffee cup)",
        "use": "Scene 2→3: Apartment action → apartment continuous",
        "cinematography_engine": "Same composition, different subject — swap shot target",
        "veo_prompt": "hand reaching for object morphs into hand reaching for coffee cup, same frame position",
    },
    "dissolve": {
        "name": "Dissolve to cityscape at twilight",
        "use": "Scene 3→4: Indoor work → outdoor night",
        "cinematography_engine": "Crossfade opacity between two camera positions",
        "veo_prompt": "apartment interior gradually fades into twilight city skyline, 2-second crossfade",
    },
    "wipe": {
        "name": "Wipe to office",
        "use": "Scene 4→5: Night street → office interior",
        "cinematography_engine": "Camera passes behind object (wall/pillar) → new scene revealed",
        "veo_prompt": "camera pans past dark building edge revealing office interior behind it",
    },
    "fade_to_black": {
        "name": "Fade to Black",
        "use": "Scene 5→6: Office night → office continuous",
        "cinematography_engine": "Scene exposure ramps to 0 over 1 second, then back up",
        "veo_prompt": "office scene fades to complete black over 1.5 seconds, holds for beat, fades back in",
    },
    "cut": {
        "name": "Cut to Next Scene",
        "use": "Scene 6→end: Final frame → next sequence",
        "cinematography_engine": "Instantaneous switch — no transition effect",
        "veo_prompt": "hard cut with no transition, immediate next scene",
    },
}

# ═══════════════════════════════════════════════════════
# CONNECTION TO TRENCH BUILDER CINEMATOGRAPHY ENGINE
# ═══════════════════════════════════════════════════════

# The cinematography engine currently supports 12 shot types but
# has NO transition system between shots. These storyboards give
# us the missing piece: 6 named transitions with specific timing
# and visual grammar.

# MAPPING TO SENTAI BEATS:
#   Storyboard 1 (Epic)   → Sentai's "hero's journey" template
#   Storyboard 2 (Urban)  → Sentai's "civilian → suit-up" sequence
#   Transitions            → The "morphing sequence" between beats

# NEXT: Add transition system to cinematography engine
#   - Crossfade (dissolve) between camera positions
#   - Wipe (camera passes behind geometry)
#   - Match cut (same composition, new target)
#   - Motion blur dolly push
#   - Fade to black / fade in

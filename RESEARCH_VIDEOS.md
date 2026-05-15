# RESEARCH VIDEOS — May 2026
# Three domains that connect to the convergence framework

# ═══════════════════════════════════════════════════════
# VIDEO 1: Hermes Agent — 10 Features Most People Miss
# fLmlXXz5MO4 — 498 segments, 18,708 chars
# ═══════════════════════════════════════════════════════

HERMES_POWER_FEATURES = {
    "1_soul_md": "Persistent operating style, not one-off system prompts. Personality that survives sessions.",
    "2_memory": "Cross-session recall. Remembers who you are, preferences, environment, learned lessons.",
    "3_skills": "Reusable procedural knowledge. Agent learns from experience and saves as skills.",
    "4_sessions": "Searchable history across all past conversations. Resume any session.",
    "5_cron": "Scheduled autonomous jobs. Run tasks while you sleep. Multi-platform delivery.",
    "6_messaging": "Same agent on Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix.",
    "7_sub_agents": "Delegate tasks to isolated sub-agents. Parallel workstreams.",
    "8_profiles": "Multiple independent Hermes instances with isolated configs and memory.",
    "9_tools": "Browser, terminal, file system, web search, image generation, vision, TTS.",
    "10_infrastructure": "Not a chatbot — an agent layer. Memory + scheduling + multi-platform + skills.",
}

# Key insight: "Hermes is not just a terminal chatbot. It's an agent layer that can remember
# your operating context, search old sessions, load workflows, schedule tasks, run across
# different platforms, and behave more like infrastructure than a normal chat app."

# ═══════════════════════════════════════════════════════
# VIDEO 2: Superconducting Electric Motors (Hinnetics)
# KP30IV0YebE — 352 segments, 13,049 chars
# ═══════════════════════════════════════════════════════

SUPERCONDUCTING_MOTORS = {
    "company": "Hinnetics",
    "claim": "World's first practical superconducting motor",
    "target": "Aviation — electric aircraft propulsion",
    
    "how_it_works": [
        "Superconducting electromagnets on rotor (not permanent magnets)",
        "Cooled below critical temperature → resistance drops to ZERO",
        "Zero resistance → unlimited current → massive magnetic field",
        "Kevlar wrapping holds rotor together against magnetic forces",
        "No P=I²R thermal limit — the constraint that bounds all conventional motors",
    ],
    
    "key_breakthrough": """
    Conventional motors hit TWO limits:
    1. Permanent magnets: material saturation limit on field strength
    2. Conventional electromagnets: P=I²R thermal limit — more current = more heat
    
    Superconducting motors eliminate BOTH. The rotor electromagnets have zero
    resistance, so they can generate vastly stronger fields without thermal runaway.
    Kevlar wrapping (from bulletproof vests) provides the mechanical strength to
    contain the magnetic forces trying to tear the rotor apart.
    """,
    
    "connection_to_our_framework": """
    This changes the isomorphic engineering map:
    
    BEFORE:
      Audio (voice coil P=I²R) ↔ Automotive (stator P=I²R) — same thermal constraint
    
    AFTER:
      Audio (P=I²R limited) → Automotive (P=I²R limited) → Aviation (zero-R superconducting)
      
    The superconducting motor is the next evolutionary step — it removes the thermal
    constraint entirely. The rendering pipeline stays identical (copper, steel, Kevlar,
    cryogenic systems) but the simulation physics changes fundamentally.
    """,
}

# ═══════════════════════════════════════════════════════
# VIDEO 3: Hyperframes — Web-Native Video Rendering
# 1IsskexiCSw — 716 segments, 21,655 chars
# ═══════════════════════════════════════════════════════

HYPERFRAMES = {
    "what": "Open-source framework for making videos with web technology",
    "creator": "Hay Jin",
    "tech_stack": ["HTML", "CSS", "JavaScript", "GSAP", "Canvas", "WebGL", "FFmpeg"],
    
    "use_cases": [
        "Product videos from websites",
        "Animated charts and explainers",
        "Kinetic typography shorts",
    ],
    
    "hermes_integration": """
    AI agents already understand HTML very well, so they can generate and edit
    Hyperframes compositions more reliably than operating traditional video editors.
    Hermes Agent + Hyperframes skill = programmatic video generation.
    """,
    
    "connection_to_trench_builder": """
    THIS IS MASSIVE FOR TRENCH BUILDER:
    
    1. Construction animations — render build sequences as video
    2. Training data visualization — GoPro frames → animated training montages
    3. Topography flythroughs — export survey data as aerial videos
    4. CAD assembly animations — Onshape parts assembling in sequence
    5. Client presentations — one-click video export of any scene
    
    Hyperframes means TRENCH BUILDER can output VIDEOS, not just interactive scenes.
    The same HTML/JS/WebGL pipeline that renders in-browser can be captured as FFmpeg
    video via Hyperframes — no separate rendering toolchain needed.
    """,
}

# ═══════════════════════════════════════════════════════
# CONVERGENCE UPDATE — Superconducting + Hyperframes
# ═══════════════════════════════════════════════════════

# The five-layer convergence now has two new nodes:
#
# LAYER 0 (Physics): + Superconducting motors (zero-R EM, Kevlar mechanics)
# LAYER 4 (Transformation): + Hyperframes (scene → video pipeline)
#
# And TRENCH BUILDER v6 roadmap:
# 1. Hyperframes integration — one-click video export
# 2. Superconducting motor visualization — cryogenic + Kevlar + zero-R animation

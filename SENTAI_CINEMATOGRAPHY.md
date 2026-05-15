# SUPER SENTAI — The Original "Sentai Footage" (1975-2025)
# 50-Year Cinematographic DNA — DaShawn / Guinea Pig Trench LLC
# Source: Complete History of Super Sentai — AxH5qvJtM14 (46,663 chars)

# ═══════════════════════════════════════════════════════
# THE TEMPLATE — What Every Season Repeats
# ═══════════════════════════════════════════════════════

SENTAI_TEMPLATE = """
Every Super Sentai season follows the SAME structural template:
  1. Five heroes in color-coded suits (Red = leader, Blue, Yellow, Pink/White, Green/Black)
  2. Individual weapons → combine into team cannon
  3. Transforming/combining mecha (giant robot)
  4. Monster-of-the-week → grows giant → mecha battle
  5. Roll call / team pose sequence (identity assertion)

The GENIUS: same template × different motif = infinite variation.
This IS the TRENCH BUILDER model:
  same rendering pipeline × different domain = infinite application.
"""

# ═══════════════════════════════════════════════════════
# CINEMATOGRAPHIC PATTERNS — Extracted from 50 Years
# ═══════════════════════════════════════════════════════

SENTAI_PATTERNS = {
    "transformation_sequence": {
        "origin": "Gorenger (1975) — helmet visor removal produces weapons",
        "pattern": "Civilian → suit-up → helmet close-up → full team reveal",
        "tr_builder": "Material transition: wireframe → PBR → thermal → EM overlay. The 'morphing' is the render pipeline activating layer by layer.",
    },
    "color_coding": {
        "origin": "Every season — Red=leader, Blue=intellect, Yellow=strength, Pink=heart, Green/Black=wildcard",
        "pattern": "Color = role = visual shorthand for character function",
        "tr_builder": "Material color = domain: copper=audio, steel=automotive, timber=architectural, polymer=industrial. Color IS the domain identifier.",
    },
    "mecha_combination": {
        "origin": "Sun Vulcan (1981) — first combining robot. Individual vehicles → single giant robot.",
        "pattern": "Parts assemble in sequence → combination completed → new entity emerges",
        "tr_builder": "CAD assembly animation: individual STL parts → combine into engine. The 'zord combination' IS the Onshape assembly sequence.",
    },
    "team_pose": {
        "origin": "Gorenger — five rangers standing against explosion",
        "pattern": "Team formation → individual close-ups → group shot with explosion backdrop",
        "tr_builder": "Establishing shot → helta close-ups on each component → full assembly reveal. The 'team' is the system.",
    },
    "roll_call": {
        "origin": "Denjiman (1980) — each ranger announces themselves before battle",
        "pattern": "Name + color + role = identity assertion before action",
        "tr_builder": "Shot label overlay: [COPPER WINDING] [THERMAL CORE] [EM FIELD] — each component announces itself.",
    },
    "giant_battle": {
        "origin": "Battle Fever J (1979) — first giant robot battle",
        "pattern": "Ground fight → monster grows → mecha deployed → city-scale battle",
        "tr_builder": "Close-up detail → camera pulls back → full system revealed → simulation runs at scale.",
    },
}

# ═══════════════════════════════════════════════════════
# KEY ERAS — Cinematographic Evolution
# ═══════════════════════════════════════════════════════

ERAS = """
SHOWA ERA (1975-1988): Foundation
  Gorenger: Established the 5-ranger template, helmet weapons, team cannon
  JAKQ: Playing card motif — abstract theme → visual identity
  Battle Fever J: First giant robot, Marvel collaboration, international theme
  Denjiman: First transforming robot, first roll call sequence
  Sun Vulcan: First combining robot (3 vehicles → 1 robot)
  Goggle V: First full team weapon combination
  Dynaman: First transforming base/carrier
  Bioman: First two-part mecha combination
  Changeman: First mythical creature motif
  Flashman: First alien origin story
  Maskman: First martial arts focus, first 6th ranger
  Liveman: First animal motif, first student-mentor dynamic

HEISEI ERA (1989-2019): Expansion
  Turboranger: First vehicle motif, high school setting
  Fiveman: First sibling team
  Jetman: First love triangle drama — considered the best story
  Zyuranger: FIRST ADAPTED AS POWER RANGERS — dinosaur motif, Dragon Ranger
  Dairanger: Chinese martial arts motif, Kiba Ranger (White Ranger in PR)
  Kakuranger: First ninja sentai, comedy focus
  Ohranger: First ancient civilization motif, darker tone
  Carranger: First parody season — self-aware comedy
  Megaranger: Digital/tech motif, high school
  Gingaman: Nature/animal motif, earth power
  GoGoFive: Rescue theme, family team
  Timeranger: Time travel, future police
  Gaoranger: First anniversary season (25th), animal spirits
  Hurricaneger: Ninja + elemental powers
  Abaranger: Dinosaur + chaos theme
  Dekaranger: Police/space procedural
  Magiranger: Magic/fantasy, family team
  Boukenger: 30th anniversary, adventure/exploration
  Gekiranger: Martial arts, Beast-Fist style
  Go-Onger: Vehicle/racing + animal hybrids
  Shinkenger: Samurai motif, calligraphy, feudal Japan
  Goseiger: Angel/card motif, heaven vs hell
  Gokaiger: 35th anniversary — PIRATES who can transform into ALL previous rangers
  Go-Busters: Spy/espionage, buddy cop dynamic
  Kyoryuger: Dinosaur + samba music — wild energy
  ToQger: Train motif, imagination power, children as rangers
  Ninninger: Ninja, 3 generations of rangers
  Zyuohger: Animal cube motif, Minecraft-style
  Kyuranger: SPACE — 9 starting rangers, constellation motif
  Lupinranger vs Patranger: Thieves vs Police — TWO TEAMS COMPETING
  Ryusoulger: Knight/dinosaur, Arthurian legend

REIWA ERA (2019-present): Innovation
  Kiramager: Gemstone/crystal motif, creativity theme
  Zenkaiger: 45th anniversary — mechanical rangers, world motif
  Donbrothers: Virtual world, CG rangers, Haruka Kito (female lead)
  King-Ohger: Insect/royalty, fantasy kingdom, SERIOUS tone
  Boonboomger: Vehicle/tire motif, racing + delivery
  Gozyuger: 50th ANNIVERSARY (2025) — animal + number motif
"""

# ═══════════════════════════════════════════════════════
# WHAT THIS MEANS FOR TRENCH BUILDER CINEMATOGRAPHY
# ═══════════════════════════════════════════════════════

APPLICATION = """
1. THE MOTIF SYSTEM
   Sentai: Dinosaur → Ninja → Samurai → Pirate → Space → Knight → Insect
   TRENCH BUILDER: Audio → Automotive → Architectural → Industrial → Civil → EM
   
   Each "season" (domain) gets the same template with a different motif.
   The rendering pipeline is the template. The domain is the motif.

2. THE COMBINATION SEQUENCE
   Sentai: Individual vehicles → combine → giant robot
   TRENCH BUILDER: Individual CAD parts → assemble → complete engine/motor/building
   
   The mecha combination IS the CAD assembly animation.

3. THE 6TH RANGER
   Sentai: New ranger joins mid-season, brings new power
   TRENCH BUILDER: New domain joins the framework (audio joined first, then
   automotive, then architectural, then industrial, then civil). Each new
   domain is a "6th ranger" that expands the team.

4. THE ANNIVERSARY SEASON (Gokaiger/Zenkaiger)
   Sentai: Anniversary rangers can access ALL previous powers
   TRENCH BUILDER: The convergence framework — all domains accessible
   from one unified pipeline. The "pirate rangers" who can become anyone.

5. THE TWO-TEAM SEASON (Lupinranger vs Patranger)
   Sentai: Two competing teams in one show
   TRENCH BUILDER: The isomorphic engineering insight — audio and automotive
   are the same physics but "competing" transducers (cone vs shaft).

6. GOKAIGER — The Ultimate Model
   Pirates who can transform into ALL 34 previous teams.
   This IS the TRENCH BUILDER convergence: one framework that can become
   any domain. The "Gokai Change" is the domain toggle.
"""

# ═══════════════════════════════════════════════════════
# CINEMATOGRAPHY SHOT SEQUENCE — The Sentai Way
# ═══════════════════════════════════════════════════════

SENTAI_SHOT_SEQUENCE = [
    "1. COLD OPEN — monster attacks, civilians flee (DRONE flyover of terrain)",
    "2. TITLE CARD — season logo with theme music (BRAND overlay on establishing shot)",
    "3. CIVILIAN SCENE — rangers in normal life (WIDE shot of full system)",
    "4. MONSTER APPEARS — threat established (THERMAL BLOOM — something is wrong)",
    "5. TRANSFORMATION — suit up sequence (MATERIAL MORPH — wireframe→PBR→EM)",
    "6. ROLL CALL — each ranger announces (HELTA CLOSE-UP on each component)",
    "7. GROUND FIGHT — individual weapons (DOLLY/CAMERA ORBIT around details)",
    "8. MONSTER GROWS — stakes escalate (CAMERA PULLS BACK to reveal full scale)",
    "9. MECHA COMBINATION — vehicles assemble (CAD ASSEMBLY ANIMATION)",
    "10. GIANT BATTLE — city-scale fight (DRONE SHOT of entire simulation running)",
    "11. FINISHER — team cannon / final attack (BUILD SEQUENCE — structure completed)",
    "12. VICTORY POSE — team stands against explosion (FINAL WIDE with all systems active)",
]

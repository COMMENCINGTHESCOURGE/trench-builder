# Proximity Dialogue Inventory

**Date:** 2026-05-28
**Purpose:** Dialogue behaviors organized by zone, type, and example. Feeds Checkpoint 4 (Proximity Dialogue System).

---

## Zone Definitions

| Zone | Range | Description | Audibility |
|------|-------|-------------|------------|
| Intimate | 0-1.5 m | Trust/suspicion threshold — confessions, secrets, threats | Clear |
| Conversation | 1.5-4 m | Default social range — greetings, trade, requests | Normal |
| Calling | 4-10 m | Urgency threshold — threat reports, desperate pleas | Raised voice |
| Distant | 10-30 m | Recognition only — familiar faces, loud calls | Shouting |
| Passing | 5 m (overlap) | NPC self-talk — muttering, ambient flavor | Half-audible |

---

## Dialogue Inventory

### 1. Intimate Zone (0-1.5 m)

| Type | Trigger | Example |
|------|---------|---------|
| Confession | trust > 0.80 + recent_trauma | "I haven't slept since the breach. Every time I close my eyes I see them." |
| Secret | trust > 0.85 + loyalty_bond_active | "There's a cache in the old fire station. Don't tell the others." |
| Threat | trust < 0.15 + aggression > 0.70 | "Get out of my face. Now." |
| Healing | medic_role + player_injured | "This'll sting. Hold still." |
| Trade whisper | trust > 0.50 + surplus_good | "Got something special. Not for the common stores." |
| Combat coordination | group_fight + trusted_ally | "On your left — I'll draw, you flank." |

### 2. Conversation Zone (1.5-4 m)

| Type | Trigger | Example |
|------|---------|---------|
| Greeting — positive | trust > 0.50 + familiarity | "Good to see you standing." |
| Greeting — neutral | no_prior_interaction | "Headed somewhere?" |
| Greeting — hostile | trust < 0.30 + faction_diff | "You're not welcome here." |
| Request — food | blood_sugar < 0.30 | "You got anything edible? I'll trade." |
| Request — medical | health < 0.40 + med_role | "Can you take a look at this?" |
| Request — work | fatigue < 0.50 + idle | "Need a hand with the barricade." |
| Warning | threat > 0.60 | "Been hearing noises from the east wall." |
| Information | curiosity > 0.50 + player_new | "Where you coming from? What's it like?" |
| Rumor | gossip_trait + event_recent | "Heard the depot was hit last night." |
| Argument — dispute | resource_tension > 0.70 | "You took more than your share. Again." |
| Mourning | grief_active + shared_loss | "They were with us since Day 3. Doesn't feel real." |

### 3. Calling Zone (4-10 m)

| Type | Trigger | Example |
|------|---------|---------|
| Alert — threat | threat > 0.80 + line_of_sight | "Contact! East side!" |
| Alert — fire | fire_detected | "FIRE! Everyone grab buckets!" |
| Alert — breach | wall_breach_detected | "They're through! Fall back to the safe room!" |
| Desperate plea | health < 0.15 + alone | "HELP! Someone — anyone!" |
| Recruitment | labor_shortage + player_idle | "Hey — you! Get over here, we need bodies!" |
| Name call | distance > recognition_threshold | "Is that you, Marcus?!" |

### 4. Distant Zone (10-30 m)

| Type | Trigger | Example |
|------|---------|---------|
| Long-range hail | familiar_shape + uncertainty | "Hail! Identify yourself!" |
| Warning shot | unknown_approach + paranoid | "That's close enough! State your business!" |
| Summons | authority_role + urgency | "All able bodies to the main gate. Now." |
| Relief | familiar_face + safe_return | "They made it back! Open the gate!" |
| Signal call | pre_arranged_code | Three short whistles = all clear. Two = danger. One = come now. |

### 5. Passing Comments / Self-Talk (5 m radius)

| Type | Trigger | Example |
|------|---------|---------|
| Hunger | blood_sugar < 0.30 | "{muttering} Should've saved more from last raid..." |
| Bladder | bladder > 0.80 + toilet > 50m | "{fidgets} Gotta hold it..." |
| Fatigue | fatigue > 0.70 | "{rubs eyes, yawns} When's my shift end..." |
| Paranoia | threat > 0.60 | "{scanning} Something's out there..." |
| Loneliness | loneliness > 0.85 | "{staring} Anyone still out there?" |
| Grief | grief_recent | "{pauses} ...they would've known what to do." |
| Satisfaction | all vincs < 0.40 | "{nods} Not bad. Not bad at all." |
| Crafting | in_workshop | "{adjusting tool} Just a little more..." |
| Inventory check | in_armory | "One box of 9mm. Thirty rounds. That's it." |

---

## NPC Role Modifiers

| Role | Override Behavior | Example Dialogue |
|------|-------------------|-----------------|
| Guard | Greets with threat assessment | "Halt. Turn around slow. Keep hands visible." |
| Medic | Addresses health first | "You're limping. Sit." |
| Gatherer | Talks about food constantly | "Roots are thinning out past the creek." |
| Fighter | Scans while talking | "{eyes on perimeter} Did you hear that?" |
| Builder | Comments on structural state | "The north wall needs another two beams. Tomorrow." |
| Leader | Assigns, doesn't ask | "You're on water duty. Report to the pump." |
| Child | Asks questions, states observations | "Are the monsters really dead? My dad says they sleep." |

---

## Reputation Modifiers

| Reputation Level | Dialogue Offset | Examples |
|-----------------|-----------------|----------|
| Hero (≥80) | Positive bias, offers info first | "You saved my kid. Anything you need." |
| Trusted (50-79) | Open, cooperative | "Glad you're here. We're a bit short-handed." |
| Neutral (20-49) | Standard responses | "Don't cause trouble." |
| Suspicious (10-19) | Clipped, guarded | "What." |
| Hostile (<10) | Aggressive, may refuse interaction | "Get lost before I make you lost." |

---

## Faction Modifiers

| Faction Relation | Greeting | Topics Avoided |
|-----------------|----------|----------------|
| Same faction | Familiar, trusting | None |
| Allied faction | Respectful, cautious | Resource allocations, defensive gaps |
| Neutral faction | Formal, guarded | Allegiances, plans, supplies |
| Hostile faction | Aggressive, brief | Everything — interaction is dangerous |

---

## Emotional State → Dialogue Weight

| Emotional State | Most Likely Dialogue Type |
|-----------------|--------------------------|
| Calm | Neutral greeting, passing comment |
| Anxious | Paranoia check, warning |
| Desperate | Plea, request for aid |
| Grieving | Mourning, silence |
| Angry | Threat, argument |
| Paranoid | Distant hail, hostile greeting |
| Hopeful | Offer, positive greeting |
| Resigned | Stoic passing comment, refusal |

---

## Verification Checklist

- [ ] Each zone has at least 3 dialogue types
- [ ] Triggers reference vinculum values or game state
- [ ] Examples sound human, not robotic
- [ ] NPC role override examples present
- [ ] Reputation and faction modifiers documented
- [ ] Emotional state mapping complete

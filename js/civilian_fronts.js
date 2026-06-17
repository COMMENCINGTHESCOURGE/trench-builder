/**
 * CIVILIAN FRONT STRUCTURES
 * Legitimate businesses that mask criminal operations.
 * Every station, corridor, and outpost needs these.
 * Reference: Real-world money laundering typologies (FATF, FinCEN).
 */

// ═══════════════════════════════════════════════════════════
// SECTOR 1: FOOD & HOSPITALITY
// ═══════════════════════════════════════════════════════════

const TRADE_DINERS = [
    {
        name: "The Boiling Point",
        type: "Trade Diner",
        station: "Trench Hub",
        front: "24-hour spacer diner serving synth-eggs and real coffee",
        back: "Neutral ground for deal-making. No weapons. No recordings. Prices are 10% above market — the surcharge buys privacy.",
        npc: "Chef Venn — former syndicate enforcer who retired to flip pancakes. Knows every crew by their order.",
        mechanic: "Order the 'Special.' Venn brings a data slate with today's unlisted jobs. Price: 200 credits or a favor.",
        dialogue: '"Eggs are synth. Coffee is real. Information is priceless. Which one did you come for?"',
    },
    {
        name: "The Grease Trap",
        type: "Mechanic Diner",
        station: "Mecha Station",
        front: "Greasy spoon attached to a repair bay. Food is terrible. Coffee is worse.",
        back: "Ship mechanics moonlight as chop-shop operators. Order the 'full service' — your ship gets repaired AND your cargo gets fenced in one stop.",
        npc: "Wrench — never gives a real name. Has a cybernetic arm with 14 tools. Charges by the minute.",
        mechanic: "Ship repair + cargo fencing bundle. 15% discount if you let them keep the scrap.",
        dialogue: '"I fixed your engine and sold your contraband. Same invoice. Don\'t read the line items."',
    },
    {
        name: "The Void Belly",
        type: "24-Hour Cantina",
        station: "Grief Wastes",
        front: "The only place open in Grief. Serves whatever came off the last freighter.",
        back: "Information exchange. Every crew passes through. Bartender keeps a ledger of who owes who. For 500 credits, you can add an entry.",
        npc: "Bartender Jin — blind but sees everything. Uses echo-location from clinking glasses.",
        mechanic: "Buy a round for the house (300cr) — gain reputation. Buy a specific drink for a specific crew — send a message.",
        dialogue: '"I don\'t need eyes. I hear the way you breathe. You\'re lying about your cargo."',
    },
];

// ═══════════════════════════════════════════════════════════
// SECTOR 2: APPEARANCE & REPUTATION
// ═══════════════════════════════════════════════════════════

const SALONS = [
    {
        name: "The Chrome Comb",
        type: "Salon & Body Shop",
        station: "Dim Mak District",
        front: "High-end salon. Hair, skin, cybernetic detailing, tattoo removal.",
        back: "Identity laundering. New face, new transponder codes, new biometrics. 5,000 credits for a fresh start. 15,000 to become someone specific.",
        npc: "Stylist Mira — former Dim Mak enforcer who 'retired' by erasing her own face. No one knows what she really looks like.",
        mechanic: "Identity change: resets police heat, faction hostility, and debt. One-time use per playthrough.",
        dialogue: '"Who do you want to be? The question is not what face you want. It\'s what face you want to leave behind."',
    },
    {
        name: "The Polished Turret",
        type: "Barbershop",
        station: "Kraken Depths",
        front: "Old-school barbershop. Straight razors. Hot towels. No questions asked.",
        back: "Reputation grooming. The barber is a gossip columnist for the underground. For 200 credits, he spreads a rumor about you. For 500, he spreads one about your rival.",
        npc: "Barber Sol — 82 years old. Has cut the hair of every Galactic Overlord for 40 years. Retired none of them.",
        mechanic: "Rumor planting: +10% reputation with target faction, -5% with their rival. Stackable.",
        dialogue: '"A good haircut and a bad rumor — both grow back. The trick is knowing which one to trim."',
    },
    {
        name: "The Gilded Cage",
        type: "Body Art Parlor",
        station: "Aku Aku Sanctum",
        front: "Tattoo and augmentation studio. Every design is custom. Every ink is imported.",
        back: "Faction marking. Each tattoo is a contract. The Defenders see a shield. The Kraken see a claim. Get marked by the wrong faction and you can't enter certain stations.",
        npc: "Artist Veil — mute. Communicates through sketches. Each tattoo tells a story the client didn't know they had.",
        mechanic: "Faction tattoo: permanent +15% rep with one faction, permanent -15% with their rival. Irreversible.",
        dialogue: '"This symbol means 'protected.' This one means 'hunted.' They look identical to outsiders. Choose carefully."',
    },
];

// ═══════════════════════════════════════════════════════════
// SECTOR 3: FINANCIAL
// ═══════════════════════════════════════════════════════════

const LAUNDROMATS = [
    {
        name: "Spin City Laundry",
        type: "Literal Laundromat",
        station: "Trench Hub",
        front: "Coin-operated laundromat. 2 credits per wash. Dryer is always broken.",
        back: "The owner runs a clean-credit service. Deposit dirty money, collect clean credits 48 hours later, minus 30% commission. The washing machines are the algorithm.",
        npc: "Manager Pell — wears a tie. Always folding towels. Never stops smiling. Terrifying.",
        mechanic: "Launder credits: converts illegal earnings into clean balance. 30% fee. 2-day delay. No audit trail.",
        dialogue: '"Your money is dirty. My machines are clean. Let them spend some time together."',
    },
    {
        name: "Aku Aku Trust & Fiduciary",
        type: "Offshore Bank",
        station: "Aku Aku Sanctum",
        front: "Boutique wealth management for high-net-worth individuals. Mahogany desks. Real plants.",
        back: "The entire bank is a syndicate holding company. Every account is a front. The CEO is a rotating position — whoever holds the most credits this month runs the bank.",
        npc: "'CEO' — changes monthly. Current: a 19-year-old who won the seat in a card game.",
        mechanic: "Deposit credits: earn 3% interest per day. Withdrawal triggers a 24-hour audit. Risk: during audit, police rate doubles.",
        dialogue: '"We don\'t ask where the money came from. We ask where it\'s going. That\'s where the fees are."',
    },
    {
        name: "The Counting House",
        type: "Currency Exchange",
        station: "Kraken Depths",
        front: "Exchange booth. Converts between credit types, barter goods, and faction scrip.",
        back: "The exchange rates ARE the intelligence. Watching the rates tells you which faction is about to move, which station is about to be raided, and who is hoarding what.",
        npc: "Clerk Orin — was a quantum physicist. Got bored. Now applies game theory to currency arbitrage.",
        mechanic: "Exchange currency + receive market intelligence. The spread is the fee. The information is free.",
        dialogue: '"The Kraken scrip is up 12% today. That means someone is buying. That means something is about to happen. That\'ll be 3%."',
    },
];

// ═══════════════════════════════════════════════════════════
// SECTOR 4: REPAIR & MODIFICATION
// ═══════════════════════════════════════════════════════════

const MECHANICS = [
    {
        name: "The Undercarriage",
        type: "Ship Repair Bay",
        station: "Mecha Station",
        front: "Certified repair facility. Logo on the sign. Warranty stickers on every job.",
        back: "Warranty void on purpose. Every repair comes with an undocumented 'enhancement.' Cargo shielding. Transponder spoofing. Weapon hardpoints disguised as sensor arrays.",
        npc: "Chief Mechanic Gears — speaks in torque specifications. Hasn't slept in 6 years.",
        mechanic: "Ship upgrade + illegal modification bundle. Pay in credits (slow, clean) or in cargo (fast, flagged).",
        dialogue: '"This is a cargo hauler. Or it was. Now it\'s a cargo hauler that can outrun police cruisers. Don\'t ask how."',
    },
    {
        name: "The Organ Farm",
        type: "Cybernetics Clinic",
        station: "Dim Mak District",
        front: "Medical clinic specializing in cybernetic replacement and augmentation.",
        back: "The 'donor organs' are sourced from debtors who couldn't pay. The cybernetics are military surplus. The doctor is a former combat surgeon who went AWOL.",
        npc: "Doctor Cutter — calm, precise, completely amoral. Will operate on anyone. Will operate on enemies for the right price.",
        mechanic: "Install augment: bonus to specific stat (speed, cargo, shields). Cost increases with each install. After 5 augments, you appear on the 'cybernetic registry' — police can track you.",
        dialogue: '"I can make you faster. Stronger. Harder to kill. I can also make you easier to find. Every gift has a price."',
    },
    {
        name: "The Chop Dock",
        type: "Salvage & Parts",
        station: "Grief Wastes",
        front: "Salvage yard. Buy and sell used ship parts. Everything is 'refurbished.'",
        back: "Those parts came off ships that 'disappeared.' The serial numbers are filed off. The blood is cleaned. The prices are 60% below market for a reason.",
        npc: "Owner Scrap — lives in a ship chassis behind the yard. Has a pet reactor leak named 'Glow.'",
        mechanic: "Buy cheap parts: 60% discount, but 15% chance of critical failure in combat. Or pay full price for clean parts.",
        dialogue: '"That thruster came off a Dim Mak cruiser. Still has the scorch marks. Still has the warranty sticker. One of those is a lie."',
    },
];

// ═══════════════════════════════════════════════════════════
// SECTOR 5: LOGISTICS & STORAGE
// ═══════════════════════════════════════════════════════════

const WAREHOUSES = [
    {
        name: "Void Storage Solutions",
        type: "Storage Facility",
        station: "Trench Hub",
        front: "Climate-controlled storage units. 50 credits per day. 24/7 access.",
        back: "The storage units are extradimensional pockets. Your cargo exists in a null-space between stations. Police can't scan it. Rivals can't steal it. You can access it from any station — for a premium.",
        npc: "Custodian Null — may or may not exist. Communicates only through the terminal.",
        mechanic: "Store cargo in null-space. Access from any station (3x daily rate). Perfect for hiding goods during police sweeps.",
        dialogue: '"Your cargo is not here. It is not anywhere. That is the point. That is the price."',
    },
    {
        name: "The Nest",
        type: "Courier Service",
        station: "Kraken Depths",
        front: "Same-day delivery anywhere in the sector. Uniformed couriers. Tracking numbers. Insurance available.",
        back: "The couriers are mules. The packages are decoys. The real cargo moves through a parallel network of unmarked drones. The tracking number tracks the decoy — not your goods.",
        npc: "Dispatcher Rook — manages 200 couriers. Can route a package through 14 stations blindfolded.",
        mechanic: "Ship cargo without traveling. Pay per unit. Faster than flying yourself. Risk: 5% chance of 'lost package' (stolen by rival).",
        dialogue: '"Your package will arrive at 1400 hours. Or a package will arrive at 1400 hours. Which one depends on whether anyone is watching."',
    },
    {
        name: "The Deep Freeze",
        type: "Cold Storage",
        station: "Mecha Station",
        front: "Industrial cold storage. For perishable goods. Temperature logs available on request.",
        back: "Some goods degrade over time. The Deep Freeze suspends degradation — but the suspended time accrues interest. Leave goods for 10 days, owe 10 days of storage fees plus a 'preservation surcharge' that compounds.",
        npc: "Operator Frost — never blinks. Core body temperature is 4 degrees below normal. Cybernetic.",
        mechanic: "Pause good degradation (for perishable event goods). Compound interest on storage fees. Can trap you in debt.",
        dialogue: '"Time stops in here. Debt doesn\'t. Your cargo is safe. Your wallet is not."',
    },
];

// ═══════════════════════════════════════════════════════════
// SECTOR 6: LEGAL & INFORMATION
// ═══════════════════════════════════════════════════════════

const FRONT_OFFICES = [
    {
        name: "Carrion & Associates",
        type: "Law Office",
        station: "Trench Hub",
        front: "Full-service legal firm. Contracts. Disputes. Estate planning.",
        back: "The lawyers are fixers. They don't win cases — they make cases disappear. They know every loophole, every judge, every bribe rate in every jurisdiction.",
        npc: "Partner Carrion — has never lost a case. Has never had a case go to trial. Has dirt on everyone.",
        mechanic: "Clear one legal flag per visit. Cost: 10% of net worth. Cannot clear murder or treason flags.",
        dialogue: '"I don\'t argue the law. I argue the price of ignoring it. One is cheaper. Guess which."',
    },
    {
        name: "The Whisper Network",
        type: "Private Intelligence",
        station: "Aku Aku Sanctum",
        front: "Market research firm. Competitive analysis. Trend forecasting.",
        back: "Spy ring. For a fee, they surveil a rival and report their routes, inventory, and current net worth. For a larger fee, they feed false information TO a rival about YOU.",
        npc: "Analyst Thorn — has 40 monitors. Watches all of them simultaneously. Never blinks. Never forgets.",
        mechanic: "Surveil rival: see their inventory, credits, and next destination. Cost: 2,000 credits. OR plant false intel: 5,000 credits. Rival sees fake prices at one station.",
        dialogue: '"Information is a weapon. I sell bullets. I also sell bulletproof vests. Choose your caliber."',
    },
    {
        name: "The Scriptorium",
        type: "Document Forgery",
        station: "Dim Mak District",
        front: "Print shop. Business cards. Menus. Wedding invitations.",
        back: "Forge any document. Cargo manifests. Ship registrations. Crew licenses. Death certificates. The paper is real. The ink is real. The signatures are real — harvested from genuine documents and reassembled.",
        npc: "Scribe Hex — former archivist for the Syndicate Council. Knows every official seal, every watermark, every typo that proves a document is real.",
        mechanic: "Forge documents: clear cargo as 'legal' for one trip. Cost: 1,500 credits. Risk: 8% chance forgery is detected at destination.",
        dialogue: '"A document is a story someone believed. I write very convincing stories. The ink helps."',
    },
];

// ═══════════════════════════════════════════════════════════
// SECTOR 7: VICE & ENTERTAINMENT
// ═══════════════════════════════════════════════════════════

const VICE_DENS = [
    {
        name: "The Gravity Well",
        type: "Casino",
        station: "Dim Mak District",
        front: "Luxury casino. Roulette. Card tables. Zero-G dice. Hostesses in formal wear.",
        back: "The house always wins — but the house is also the syndicate's primary money-laundering pipeline. Every chip is traceable. Every big winner gets a 'courtesy escort' — a tail to their ship.",
        npc: "Pit Boss Lace — runs the floor with absolute precision. Can spot a card counter at 50 meters. Can spot a syndicate plant at 10.",
        mechanic: "Gamble credits. Can double your money (45% chance) or lose it (55%). Winning too much attracts attention — police rate +10% for 3 days.",
        dialogue: '"The odds are 55/45 against you. I tell everyone that. Most people hear '45% chance to win' and think they\'re special."',
    },
    {
        name: "The Pressure Drop",
        type: "Bar / Substance Den",
        station: "Grief Wastes",
        front: "The lowest bar in the sector. Below the water reclamation plant. Damp. Cold. Perfect.",
        back: "Every substance in the game is consumed here openly. The bartender is a confidential informant for 3 different agencies. The patrons know. No one cares — the information he sells is always 48 hours old.",
        npc: "Bartender Dreg — informant. Agent. Double agent. Triple agent. Has forgotten which agency is his real employer.",
        mechanic: "Buy substances at street price (no travel needed for personal use). Overhear rumors (free). Risk: 25% chance of police visit while present.",
        dialogue: '"I work for the police. And the syndicate. And the regulators. One of them is my real job. I forget which."',
    },
    {
        name: "The Echo Chamber",
        type: "Fight Club / Arena",
        station: "Kraken Depths",
        front: "Underground zero-G combat arena. No rules. No referees. No liability waivers.",
        back: "The fights are a proxy market. Syndicates bet on fighters instead of going to war. A fighter's win/loss ratio moves commodity prices.",
        npc: "Announcer Roar — voice like gravel in a blender. Knows every fighter's backstory. Makes up the ones he doesn't know.",
        mechanic: "Place bets on fights (50/50 odds, rigged toward your faction standing). Win: credits + rep. Lose: credits only. OR enter as fighter: risk HP for massive payout.",
        dialogue: '"Two fighters enter. One fighter leaves. The other leaves too, just slower and with more screaming. Place your bets."',
    },
];

// ═══════════════════════════════════════════════════════════
// SECTOR 8: SECURITY & PROTECTION
// ═══════════════════════════════════════════════════════════

const SECURITY_FIRMS = [
    {
        name: "Aegis Solutions",
        type: "Private Security",
        station: "Mecha Station",
        front: "Uniformed security guards. Patrol routes. Incident reports. Very professional.",
        back: "Protection racket. Pay the monthly fee or your cargo gets 'randomly inspected.' The inspectors are Aegis employees working off-duty.",
        npc: "Commander Aegis — retired military. Runs the firm like a battalion. Every guard has a rank, a file, and a loyalty score.",
        mechanic: "Buy protection: 500 credits/month. Reduces police rate and ambush chance at one station. Miss a payment: 2x police rate for 7 days.",
        dialogue: '"Protection is a subscription service. Cancel anytime. The cancellation fee is your cargo."',
    },
    {
        name: "The Armory",
        type: "Weapons Dealer",
        station: "Grief Wastes",
        front: "Licensed firearms dealer. Background checks. Waiting periods. All legal.",
        back: "The legal inventory is for show. The real inventory is in the basement. Military-grade. No serial numbers. Cash only. The owner is a former arms treaty inspector who memorized every loophole.",
        npc: "Armorer Clasp — cheerful. Enthusiastic about calibers. Will describe in detail how each weapon violates interstellar law.",
        mechanic: "Buy weapons: ship combat upgrades. Legal (weak, traceable) or black market (powerful, flagged).",
        dialogue: '"This is illegal in 14 systems. This one is illegal in 27. This one is illegal everywhere — including here. That\'s my favorite."',
    },
    {
        name: "The Panic Room",
        type: "Safe House Network",
        station: "Aku Aku Sanctum",
        front: "Short-term rentals. Furnished. Discreet. No questions asked.",
        back: "Safe houses scattered across all stations. When police heat is too high, you can lay low. Time passes. Heat decays. But your cargo degrades and your contacts forget you.",
        npc: "Landlord Still — never moves. Never speaks above a whisper. Has 200 properties and lives in none of them.",
        mechanic: "Lay low: advance time by 3 days. Police heat -50%. All perishable cargo degrades. All active missions pause. Contacts may find other partners.",
        dialogue: '"Stay as long as you need. The rent is reasonable. The silence is free."',
    },
];

// ═══════════════════════════════════════════════════════════
// STATION MAPPING: WHICH BUSINESSES AT WHICH STATION
// ═══════════════════════════════════════════════════════════

const STATION_DIRECTORY = {
    "Trench Hub": {
        sectors: ["Trade Diner","Laundromat","Warehouse","Law Office"],
        businesses: ["The Boiling Point","Spin City Laundry","Void Storage Solutions","Carrion & Associates"],
        vibe: "Safe haven. Everything is available. Nothing is cheap. The hub where deals are made AND cleaned.",
    },
    "Kraken Depths": {
        sectors: ["Barbershop","Currency Exchange","Courier Service","Fight Club"],
        businesses: ["The Polished Turret","The Counting House","The Nest","The Echo Chamber"],
        vibe: "Where reputation is currency. Information flows through barbers and bookmakers.",
    },
    "Dim Mak District": {
        sectors: ["Salon","Cybernetics Clinic","Document Forgery","Casino"],
        businesses: ["The Chrome Comb","The Organ Farm","The Scriptorium","The Gravity Well"],
        vibe: "Identity is fluid. You can become anyone. It will cost you.",
    },
    "Mecha Station": {
        sectors: ["Mechanic Diner","Ship Repair","Cold Storage","Private Security"],
        businesses: ["The Grease Trap","The Undercarriage","The Deep Freeze","Aegis Solutions"],
        vibe: "Ships and bodies — both get repaired here. Both come out different than they went in.",
    },
    "Grief Wastes": {
        sectors: ["Cantina","Salvage Yard","Substance Den","Weapons Dealer"],
        businesses: ["The Void Belly","The Chop Dock","The Pressure Drop","The Armory"],
        vibe: "Everything is cheap. Everything is dangerous. The two are related.",
    },
    "Aku Aku Sanctum": {
        sectors: ["Body Art","Offshore Bank","Intelligence Firm","Safe House"],
        businesses: ["The Gilded Cage","Aku Aku Trust","The Whisper Network","The Panic Room"],
        vibe: "Mystery market. Secrets are currency. Trust is the most expensive commodity.",
    },
};

// Attach to window for cross-scope module compatibility
window.TRADE_DINERS = TRADE_DINERS;
window.SALONS = SALONS;
window.LAUNDROMATS = LAUNDROMATS;
window.MECHANICS = MECHANICS;
window.WAREHOUSES = WAREHOUSES;
window.FRONT_OFFICES = FRONT_OFFICES;
window.VICE_DENS = VICE_DENS;
window.SECURITY_FIRMS = SECURITY_FIRMS;
window.STATION_DIRECTORY = STATION_DIRECTORY;

console.log(JSON.stringify({
    sectors: 8,
    businesses: 24,
    stations: 6,
    npcs: 24,
    priceRange: "200 credits (rumor) to 15,000 (identity change)",
    totalAssets: 24 * 4, // name, front, back, npc, mechanic, dialogue per business
}, null, 2));

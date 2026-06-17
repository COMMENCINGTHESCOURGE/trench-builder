/**
 * B-ROLL SCENARIO GENERATOR
 * Reference: Modern Day Pirates (Somali, digital, corporate, pharma, maritime)
 * Maps pirate dynamics onto Intergalactic Drug Dealers + GHOST-BRAID
 * Output: missions, characters, dialogue seeds, plot twists, betrayals
 */

const PIRATE_REFERENCE = {
    somali: {
        pattern: "Hostage-taking + ransom negotiation",
        roles: ["Captain","Negotiator","Hostage","Financier","Muscle"],
        twist: "Hostage is the financier's son. Ransom is a setup to expose the syndicate.",
        dialogue: '"You think I am the prisoner? I am the one who paid for this ship."',
    },
    digital: {
        pattern: "Data heist + crypto-ransom + double-extortion",
        roles: ["Hacker","Inside Man","CEO","Regulator","Rival Crew"],
        twist: "The data was already leaked. The ransom is for the decryption key that doesn\'t exist.",
        dialogue: '"We didn\'t steal your files. We stole your backups. Check your primary server."',
    },
    corporate: {
        pattern: "Hostile takeover via debt accumulation + board coup",
        roles: ["Raider","Loyalist","Board Member","Whistleblower","Regulator"],
        twist: "The whistleblower works for the raider. The board member you trusted sold you out at breakfast.",
        dialogue: '"You built this company. I bought it. Same thing, different currency."',
    },
    pharma: {
        pattern: "Patent theft + price gouging + grey market distribution",
        roles: ["Chemist","Smuggler","Executive","Patient","Regulator"],
        twist: "The patient smuggling the cure IS the executive who blocked the cure from market.",
        dialogue: '"I sell life. You sell death delayed. Who is the criminal?"',
    },
    maritime: {
        pattern: "Tanker hijacking + crew kidnapping + cargo fencing",
        roles: ["Boarding Party","Captain","Crew","Fencer","Insurer"],
        twist: "The insurer funded the hijacking to trigger a payout clause that bankrupts a rival.",
        dialogue: '"The cargo is insured for triple its value. Sink the ship. We both win."',
    },
};

// ═══════════════════════════════════════════════════════════
// B-ROLL SCENARIOS: MISSIONS
// ═══════════════════════════════════════════════════════════

const MISSIONS = [
    {
        id: "ransom_run",
        title: "The Negotiator",
        pirateRef: "somali",
        setup: "A Kraken cartel boss has been taken hostage by a rival crew. His lieutenant will pay triple market rate for any goods delivered to the hostage location — but the goods are a Trojan horse.",
        mechanics: "Buy specific goods at inflated prices at Trench Hub. Deliver to Grief Wastes. On arrival: ambush. Survive OR negotiate. If you talk your way out, gain the lieutenant as a permanent contact.",
        twist: "The hostage isn't real. The 'lieutenant' is the boss testing your loyalty. Pass = faction unlock. Fail = permanent police flag.",
        dialogue: [
            '"He said you would come. He also said you would try to cheat me. Which one of you is lying?"',
            '"The goods are paid for. The delivery is not. That costs extra."',
            '"You passed the test. You could have run. You didn\'t. Welcome to the family."',
        ],
    },
    {
        id: "false_flag",
        title: "The Insurance Job",
        pirateRef: "maritime",
        setup: "A Mecha Station insurer offers you 5x cargo value if you 'lose' a shipment in Grief Wastes. The shipment is empty. The real cargo is on a parallel route — and you just told the pirates which route is undefended.",
        mechanics: "Accept contract. Choose: deliver empty cargo (safe, low pay) OR swap with real cargo (high risk, high reward). If you swap, the pirates attack the WRONG ship — but the insurer knows you stole from them.",
        twist: "The insurer IS the pirate fleet. They use false-flag contracts to identify smugglers with guts. You just qualified.",
        dialogue: [
            '"Insurance fraud is such an ugly term. I prefer 'creative risk redistribution.'"',
            '"You think I hired you to lose cargo? I hired you to lose your caution. It worked."',
        ],
    },
    {
        id: "inside_man",
        title: "The Leak",
        pirateRef: "digital",
        setup: "A Dim Mak hacker stole the pricing algorithm from Aku Aku Sanctum. For 3 days, you can see ALL future prices before they shift. But someone inside your crew is selling your trades to the police.",
        mechanics: "Every trade you make has a 20% chance of triggering a police raid. You must identify the leak by feeding false information to different crew slots and seeing which one triggers a raid.",
        twist: "There is no leak. The algorithm itself is reporting your trades. Aku Aku planted it to catch data thieves. You are the bait.",
        dialogue: [
            '"You trusted stolen data. I trusted that you would. Symmetry."',
            '"Fire your crew. It won\'t help. The problem is in your pocket, not your ship."',
        ],
    },
    {
        id: "debt_trap",
        title: "The Grief Gambit",
        pirateRef: "corporate",
        setup: "A Grief Wastes loan shark offers to clear your debt. In exchange: you run ONE shipment. The shipment is Onion Extract worth 50,000 credits. Destination: Mecha Station. The police are waiting.",
        mechanics: "You are a mule. The cargo is flagged. If caught: lose everything. If you succeed: debt cleared + gain Grief faction trust. Can you bribe the police? Can you reroute? Can you dump the cargo and fake the delivery?",
        twist: "The loan shark tipped off the police. He collects your debt from you OR the bounty from the police. He wins either way — unless you recorded the deal.",
        dialogue: [
            '"I don\'t care if you succeed or fail. I get paid either way. The only variable is you."',
            '"You recorded our conversation. Smart. That makes you dangerous. That makes you useful."',
        ],
    },
    {
        id: "grey_market",
        title: "The Cure",
        pirateRef: "pharma",
        setup: "Onion Extract — the most expensive substance — has a medical use the syndicates suppress. A rogue chemist in Kraken Depths can synthesize the cure for 1/10th the street price. She needs raw materials and protection from the Dim Mak enforcers who want her dead.",
        mechanics: "Source raw materials from specific stations. Protect the chemist during synthesis (defend against Dim Mak attacks). Choose: sell the cure at fair price (hero path, low money, permanent rep boost) OR patent and price-gouge (villain path, massive money, permanent police heat).",
        twist: "The chemist IS a former Dim Mak executive who created the suppression policy. She is seeking redemption. The enforcers aren't trying to kill her — they are trying to bring her home.",
        dialogue: [
            '"I killed people with a signature. Now I save them with a syringe. Does that balance the books?"',
            '"You could make millions. Or you could make a difference. You cannot do both."',
        ],
    },
];

// ═══════════════════════════════════════════════════════════
// B-ROLL SCENARIOS: CHARACTER DYNAMICS
// ═══════════════════════════════════════════════════════════

const CHARACTERS = [
    {
        name: "Kael Vos",
        role: "Disposable Wingman",
        archetype: "Loyal until the price is right",
        dynamic: "Flies with you for 10 missions. On the 11th, a rival offers him 3x your net worth. He takes it. But he leaves a back door in his ship systems — he wants to be caught. He wants you to stop him.",
        dialogue: '"I didn\'t betray you for money. I betrayed you so you would finally take me seriously."',
        twist: "He's not a traitor. He's a double agent for the faction you're infiltrating. He just can't tell you.",
    },
    {
        name: "Sera Qin",
        role: "The Informant",
        archetype: "Knows everything, tells nothing",
        dynamic: "Feeds you tips that are always accurate but always incomplete. Each tip makes you money AND creates an enemy. She is building a network of people who owe her — and you're the glue.",
        dialogue: '"I told you where the cargo was. I didn\'t tell you who else knew. That costs extra."',
        twist: "She's not an informant. She's an auctioneer. She sells the same information to multiple buyers and collects from whoever survives.",
    },
    {
        name: "Gorath Vehn",
        role: "The Old Guard",
        archetype: "Retired legend, pulled back in",
        dynamic: "Was Galactic Overlord for 12 consecutive cycles before 'retiring.' He mentors you. Every piece of advice is correct. Every piece of advice also advances his hidden agenda: reclaiming his throne by making you dependent on him.",
        dialogue: '"I built this empire. I can rebuild it through you. The question is: will you step aside when I ask?"',
        twist: "He's dying. He has 30 days. He's not training a successor — he's writing his legacy through your story.",
    },
    {
        name: "The Twins (Mir + Kor)",
        role: "Split Personality Crew",
        archetype: "One honest, one corrupt",
        dynamic: "You never know which twin you're dealing with. Mir runs fair trades. Kor skims 20% off every deal. Their ship transponder is identical. You must learn their behavioral tells — or always assume Kor.",
        dialogue: '"I\'m Mir today. Yesterday I was Kor. Tomorrow? Depends who\'s asking."',
        twist: "There are no twins. It's one person with a personality disorder who genuinely believes they are two people. The skimmed credits go to an account neither personality knows about.",
    },
    {
        name: "Aya Nox",
        role: "The Rival",
        archetype: "Respects you, will destroy you",
        dynamic: "Runs identical routes. Undercuts your prices. Saves your life from a police raid — then sends you the bill. The rivalry is genuine, the respect is genuine, and one of you will put the other out of business.",
        dialogue: '"I don\'t hate you. I am you, six months from now, if you make the choices I made. I\'m trying to stop that."',
        twist: "She's your character from a previous playthrough. The game remembers. She has your old inventory, your old rank, your old debts.",
    },
];

// ═══════════════════════════════════════════════════════════
// B-ROLL SCENARIOS: PLOT TWISTS
// ═══════════════════════════════════════════════════════════

const PLOT_TWISTS = [
    {
        trigger: "Reach 50% of max rank",
        twist: "The Syndicate Council was watching from day one. They've been adjusting prices, police patrols, and event frequency to test you. You are not playing the game. The game is playing you.",
        effect: "All future prices are influenced by your past choices. The market now reacts to YOUR reputation.",
    },
    {
        trigger: "Survive 3 police raids",
        twist: "The police chief offers you a deal: become an informant. Feed her 3 syndicate members, and your record is wiped. Refuse, and every station gets a permanent +10% police rate.",
        effect: "Betray 3 NPCs OR face permanent heat. The NPCs you betray become hostile traders in future runs.",
    },
    {
        trigger: "Amass 100,000 credits",
        twist: "Your crew stages a mutiny. They've been skimming from your cargo and building their own ship. They offer you a choice: split the empire 50/50, or they leave and become a rival faction.",
        effect: "Create a permanent rival faction with your ex-crew mates. They know your routes.",
    },
    {
        trigger: "Buy Onion Extract for the first time",
        twist: "The seller is an undercover regulator. The transaction was recorded. You now have a choice: work for the regulators as a deep-cover agent, or the recording goes public and every station bans you.",
        effect: "Double-agent gameplay mode unlocks. You must balance syndicate trust with regulator missions.",
    },
    {
        trigger: "Visit all 6 stations",
        twist: "You discover a 7th station: The Nexus. It exists outside syndicate control. Prices here are 10x normal but police rate is 0%. However, every trade at The Nexus reduces your max HP by 10% — the Nexus feeds on life force.",
        effect: "High-risk black market unlocks. Permanent HP cost per visit.",
    },
];

// ═══════════════════════════════════════════════════════════
// B-ROLL SCENARIOS: BACKSTABBING MECHANICS
// ═══════════════════════════════════════════════════════════

const BACKSTABBING = [
    {
        name: "The Cold Shoulder",
        pattern: "NPC stops trading with you after you trade with their rival.",
        pirateRef: "corporate (non-compete retaliation)",
        counter: "Offer a peace deal that costs 20% of your profit from the rival trade.",
    },
    {
        name: "The Markup",
        pattern: "NPC sells you goods at triple price because you have no other buyer nearby.",
        pirateRef: "pharma (price gouging on essential goods)",
        counter: "Threaten to reveal their price to regulators. 50% chance they back down. 50% chance they flag you to police.",
    },
    {
        name: "The Bait",
        pattern: "NPC sells you cheap goods that are flagged as stolen. Police raid on departure.",
        pirateRef: "maritime (planted contraband)",
        counter: "Dump the cargo before departure (lose money) OR bribe police (risky, expensive) OR fight (lose HP).",
    },
    {
        name: "The Inside Scoop",
        pattern: "Crew member offers to 'handle' a rival for a fee. They take the fee and disappear.",
        pirateRef: "somali (ransom scam — pay for hostage, no hostage exists)",
        counter: "Track them down (spawns a revenge mission) OR write it off (gain 'Gullible' trait, future scams cost more).",
    },
    {
        name: "The Deep Fake",
        pattern: "Rival broadcasts fake distress call in your ship ID. Police are waiting at your destination.",
        pirateRef: "digital (spoofed identity)",
        counter: "Change ship transponder (costs 5,000 credits) OR route through unpatrolled space (takes 2 extra days).",
    },
];

// ═══════════════════════════════════════════════════════════
// B-ROLL SCENARIOS: DIALOGUE SEEDS
// ═══════════════════════════════════════════════════════════

const DIALOGUE_SEEDS = [
    // HOSTILE
    '"You fly like a trader. I fly like a bullet. One of us is going to have a very bad day."',
    '"I don\'t care about your cargo. I care about who you bought it from. Answer carefully."',
    '"Your reputation precedes you. Unfortunately for you, so does my ambush."',
    // SEDUCTIVE
    '"Work with me. Not for me. There\'s a difference, and it costs exactly half your profit."',
    '"You could make this run alone. Or you could make it rich. Pick one."',
    '"I have a secret that doubles your margins. The secret is free. Keeping it secret costs 30%."',
    // DESPERATE
    '"I need passage to Dim Mak. I have no money. I have something better: I know who is hunting you."',
    '"Please. My daughter is on Mecha Station. They took her. I can\'t pay. I can fly. I can fight. I can die. Whatever you need."',
    '"The cargo is rotting. Take it. Take all of it. Just get it off my ship before the inspectors arrive."',
    // PHILOSOPHICAL
    '"We are all dealers here. Some deal in dust. Some deal in trust. I don\'t know which is more dangerous."',
    '"The syndicates didn\'t create this market. They just organized it. The market created itself — from hunger, from need, from fear."',
    '"You think you\'re building an empire? You\'re building a coffin. The question is whose name is on it."',
    // BETRAYAL
    '"It\'s not personal. I like you. I just like my survival more."',
    '"I didn\'t sell you out. I sold my silence. There\'s a difference — and you can\'t afford it."',
    '"You trusted me? That was your first mistake. Your second was not having a backup plan."',
];

// Attach to window for cross-scope module compatibility
window.PIRATE_REFERENCE = PIRATE_REFERENCE;
window.MISSIONS = MISSIONS;
window.CHARACTERS = CHARACTERS;
window.PLOT_TWISTS = PLOT_TWISTS;
window.BACKSTABBING = BACKSTABBING;
window.DIALOGUE_SEEDS = DIALOGUE_SEEDS;

console.log(JSON.stringify({
    missions: MISSIONS.length,
    characters: CHARACTERS.length,
    plotTwists: PLOT_TWISTS.length,
    backstabbings: BACKSTABBING.length,
    dialogueSeeds: DIALOGUE_SEEDS.length,
    totalScenarios: MISSIONS.length + CHARACTERS.length + PLOT_TWISTS.length + BACKSTABBING.length,
}, null, 2));

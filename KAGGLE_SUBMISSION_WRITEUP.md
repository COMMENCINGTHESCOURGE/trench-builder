# Kaggle Gemma 4 Good Hackathon — Submission Writeup

## TRENCH BUILDER — Democratizing Architectural Engineering with Gemma 4

**Track:** Digital Equity & Inclusivity · Ollama  
**Team:** DaShawn / Guinea Pig Trench LLC  
**Kaggle:** commencethescourge

---

### The Problem

Architectural engineering software costs thousands of dollars per license. Revit, Rhino, AutoCAD — these tools gatekeep who can design, build, and visualize. A community center in a rural area, a disaster-resilient school in a developing region, or a first-time homeowner wanting to understand their structure — all are locked out by cost, hardware requirements, and technical complexity.

The digital divide in construction is widening. The tools that design our world are only available to those who can pay.

### Our Solution

TRENCH BUILDER is a **single-file HTML application** that provides professional-grade 3D construction visualization, topography surveying, interior design, and CAD import — entirely in the browser. No installation. No license. No GPU required. It runs on any device with a web browser.

**Gemma 4 powers the AI design assistant.** Running locally via Ollama on the user's device, Gemma 4 provides:
- Material recommendations based on climate and soil conditions
- Structural suggestions (optimal beam placement, load path analysis)
- Energy efficiency feedback (window placement for daylight, insulation guidance)
- Natural language interaction — "Show me where the plumbing should go"

### How We Use Gemma 4

Gemma 4 2B (`gemma4:2b`) runs locally via Ollama, processing design queries without any API calls or internet connection. This is critical for:
- **Offline communities** — no internet required after initial page load
- **Privacy** — design data never leaves the user's device  
- **Zero cost** — no API fees, no usage limits
- **Accessibility** — functions on a $200 Chromebook

The integration pattern:
1. User places a structure (wall, foundation, window)
2. User asks Gemma 4: "Is this wall thick enough for a two-story load?"
3. Gemma 4 analyzes the current scene state (material, dimensions, position) and responds with recommendations
4. The builder updates the structure based on AI feedback

### Architecture

```
┌──────────────────────────────────────────────┐
│  TRENCH BUILDER (Single HTML File)           │
│  ┌──────────────┐  ┌──────────────────┐     │
│  │ Three.js      │  │ Gemma 4 (Ollama) │     │
│  │ 3D Rendering  │  │ Design Assistant │     │
│  │ PBR + Shadows │  │ Local Inference  │     │
│  └──────────────┘  └──────────────────┘     │
│  ┌──────────────────────────────────────┐   │
│  │ Tool System                          │   │
│  │ Walls · Floors · Foundations · MEP  │   │
│  │ Topography · Interior · CAD Import  │   │
│  └──────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

### Technical Implementation

Gemma 4 integration via Ollama API (local, port 11434):

```javascript
async function askGemma4(question, sceneContext) {
  const response = await fetch('http://localhost:11434/api/generate', {
    method: 'POST',
    body: JSON.stringify({
      model: 'gemma4:2b',
      prompt: `You are an architectural engineering assistant. 
Current scene: ${sceneContext}
User question: ${question}
Provide a concise, actionable recommendation.`,
      stream: false
    })
  });
  return (await response.json()).response;
}
```

The builder sends scene context (structure types, materials, dimensions, topography data) as structured text, and Gemma 4 returns design recommendations rendered directly in the interface.

### Real-World Impact

**Digital Equity:** Anyone with a browser can design and visualize buildings. No $10,000 software license. No $3,000 workstation.

**Education:** Students learn architectural engineering through interactive construction. Place a beam, ask Gemma 4 why it needs to be thicker, understand the physics.

**Disaster Resilience:** In regions vulnerable to earthquakes, floods, or hurricanes, users can survey topography, test structural configurations, and get AI-guided recommendations for resilient design — all offline.

**Global Reach:** The builder has been tested in 5 domains: residential construction, MEP systems, topography surveying, interior design, and CAD import from Onshape engineering models.

### What Makes This Different

Most AI construction tools require cloud APIs, expensive subscriptions, and constant connectivity. TRENCH BUILDER + Gemma 4 runs **entirely locally** — the 3D engine in the browser, the AI assistant via Ollama. This combination of local-first architecture and open-weight models means the tool works anywhere, for anyone, forever.

The same HTML file that helps an architect in New York helps a community builder in rural Kenya. That's digital equity — not as a promise, but as a working product.

### Links

- **Live Demo:** Included in repository
- **Code:** github.com/commencethescourge/trench-builder (submitted separately)
- **Video:** [YouTube — TRENCH BUILDER Demo with Gemma 4]

---

*Built with Three.js, Ollama, Gemma 4 2B, and the conviction that the tools to design our world should belong to everyone.*

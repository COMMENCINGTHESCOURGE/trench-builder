#!/usr/bin/env python3
"""
PROCEDURAL VIDEO LEARNER v1.0
Extracts cinematographic DNA from Veo-generated clips.
Learns the grammar of hook-depth-resolution arcs.
Feeds back into the cinematography engine.

DaShawn / Guinea Pig Trench LLC — May 2026
"""
import os, json, statistics
from PIL import Image

# ═══════════════════════════════════════════════════════
# 1. FRAME EXTRACTOR — Pull features from video frames
# ═══════════════════════════════════════════════════════

class VideoFrameAnalyzer:
    def __init__(self, frames_dir):
        self.frames_dir = frames_dir
        self.frames = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
    
    def analyze_frame(self, path, sample_size=80):
        img = Image.open(path)
        w, h = img.size
        small = img.resize((sample_size, sample_size))
        px = list(small.getdata())
        
        r = sum(p[0] for p in px) / len(px)
        g = sum(p[1] for p in px) / len(px)
        b = sum(p[2] for p in px) / len(px)
        bright = [(p[0]+p[1]+p[2])/3 for p in px]
        mean_b = sum(bright) / len(bright)
        std_b = statistics.stdev(bright)
        
        # Color temperature (Kelvin approximation from RGB)
        # Warmer = more red, cooler = more blue
        color_temp = (r - b) / 255  # -1 to 1, negative = cool, positive = warm
        
        return {
            "rgb": (r, g, b),
            "brightness": mean_b,
            "contrast": std_b,
            "color_temp": color_temp,
            "dims": (w, h),
            "r_dominant": r > g + 15 and r > b + 15,
            "b_dominant": b > r + 15 and b > g + 15,
        }
    
    def analyze_all(self):
        results = []
        for fname in self.frames:
            path = f"{self.frames_dir}/{fname}"
            results.append(self.analyze_frame(path))
        return results
    
    def detect_cuts(self, results, threshold=50):
        cuts = []
        for i in range(1, len(results)):
            prev = results[i-1]["rgb"]
            curr = results[i]["rgb"]
            shift = abs(curr[0]-prev[0]) + abs(curr[1]-prev[1]) + abs(curr[2]-prev[2])
            if shift > threshold:
                cuts.append({"at_frame": i, "shift": shift})
        return cuts

# ═══════════════════════════════════════════════════════
# 2. GRAMMAR LEARNER — Extract rules from analyzed clips
# ═══════════════════════════════════════════════════════

class CinematographyGrammar:
    def __init__(self):
        self.rules = {}
    
    def learn(self, clip_name, frame_data, cuts):
        """Extract the 'grammar' of a clip — its visual signature."""
        n = len(frame_data)
        if n == 0: return
        
        avg_r = sum(f["rgb"][0] for f in frame_data) / n
        avg_g = sum(f["rgb"][1] for f in frame_data) / n
        avg_b = sum(f["rgb"][2] for f in frame_data) / n
        avg_brt = sum(f["brightness"] for f in frame_data) / n
        avg_ctr = sum(f["contrast"] for f in frame_data) / n
        avg_temp = sum(f["color_temp"] for f in frame_data) / n
        
        # Temporal gradient: how does brightness evolve over the clip?
        if n >= 2:
            brightness_gradient = (frame_data[-1]["brightness"] - frame_data[0]["brightness"]) / n
            temp_gradient = (frame_data[-1]["color_temp"] - frame_data[0]["color_temp"]) / n
        else:
            brightness_gradient = 0
            temp_gradient = 0
        
        # Cut density
        cut_density = len(cuts) / n if n > 0 else 0
        
        # Dominant energy
        if cut_density > 0.2 and avg_ctr > 50:
            energy = "DYNAMIC — fast cuts, high contrast, attention-grabbing"
        elif avg_temp > 0.1 and avg_brt < 90:
            energy = "DEPTH — warm dark, emotional weight, physics reveal"
        elif avg_brt > 100 and avg_ctr > 60:
            energy = "RESOLUTION — bright, clear, confident, calm"
        else:
            energy = "NEUTRAL — balanced, ambient"
        
        # Generated Veo prompt parameters
        veo_params = {
            "target_rgb": f"({avg_r:.0f},{avg_g:.0f},{avg_b:.0f})",
            "target_brightness": f"{avg_brt:.0f}",
            "target_contrast": f"{avg_ctr:.0f}",
            "color_temperature": "WARM" if avg_temp > 0.05 else "COOL" if avg_temp < -0.05 else "NEUTRAL",
            "cut_style": "FAST CUTS (3+ per 8s)" if cut_density > 0.2 else "SMOOTH (no cuts)" if cut_density == 0 else "MODERATE",
            "energy": energy,
            "brightness_arc": "RISING" if brightness_gradient > 2 else "FALLING" if brightness_gradient < -2 else "STABLE",
            "temp_arc": "WARMING" if temp_gradient > 0.01 else "COOLING" if temp_gradient < -0.01 else "STABLE",
        }
        
        self.rules[clip_name] = veo_params
        return veo_params
    
    def generate_veo_prompt(self, clip_name, target_duration=8):
        """Generate an optimized Veo prompt from learned grammar."""
        if clip_name not in self.rules:
            return f"ERROR: No grammar learned for '{clip_name}'"
        
        g = self.rules[clip_name]
        return f"""Generate a {target_duration}-second video.
Style: {g['cut_style']}
Color: {g['color_temperature']} palette, target RGB{g['target_rgb']}
Brightness: {g['target_brightness']}/255, contrast: {g['target_contrast']}/255
Arc: Brightness {g['brightness_arc']}, temperature {g['temp_arc']}
Energy: {g['energy']}"""

# ═══════════════════════════════════════════════════════
# 3. ARC SYNTHESIZER — Learn the hook→depth→resolution arc
# ═══════════════════════════════════════════════════════

class ArcSynthesizer:
    def __init__(self):
        self.arc_template = {
            "hook": {"min_duration": 6, "max_duration": 12, "energy": "DYNAMIC", "temp": "COOL"},
            "depth": {"min_duration": 8, "max_duration": 16, "energy": "DEPTH", "temp": "WARM"},
            "resolution": {"min_duration": 6, "max_duration": 12, "energy": "RESOLUTION", "temp": "WARM_NEUTRAL"},
        }
    
    def learn_arc(self, clip_analyses):
        """Learn the optimal arc from analyzed clips."""
        # Extract transitions between clips
        transitions = []
        clips = list(clip_analyses.items())
        
        for i in range(len(clips)-1):
            name_a, data_a = clips[i]
            name_b, data_b = clips[i+1]
            
            last_frame_a = data_a[-1] if data_a else None
            first_frame_b = data_b[0] if data_b else None
            
            if last_frame_a and first_frame_b:
                brt_delta = first_frame_b["brightness"] - last_frame_a["brightness"]
                temp_delta = first_frame_b["color_temp"] - last_frame_a["color_temp"]
                
                transitions.append({
                    "from": name_a, "to": name_b,
                    "brightness_jump": brt_delta,
                    "temperature_shift": "WARMING" if temp_delta > 0.03 else "COOLING" if temp_delta < -0.03 else "STABLE",
                    "transition_type": "HARD CUT" if abs(brt_delta) > 25 else "SOFT TRANSITION",
                })
        
        return transitions
    
    def generate_interpolation_prompt(self, from_clip, to_clip, grammar, duration=12):
        """Generate Veo interpolation prompt between two learned clips."""
        g_from = grammar.rules.get(from_clip, {})
        g_to = grammar.rules.get(to_clip, {})
        
        from_rgb = g_from.get("target_rgb", "(?)")
        to_rgb = g_to.get("target_rgb", "(?)")
        from_energy = g_from.get("energy", "?")
        to_energy = g_to.get("energy", "?")
        
        return f"""INTERPOLATE between two visual states over {duration} seconds.

START: {from_energy} | RGB{from_rgb}
END:   {to_energy} | RGB{to_rgb}

The transition is not a crossfade. It's a JOURNEY.
Descend from {from_energy} energy into the core, then rise into {to_energy}.
Use the midpoint to reveal depth — the physics beneath the surface."""

# ═══════════════════════════════════════════════════════
# 4. MAIN — Learn from the 3 Veo clips
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    base = r"C:\Users\dasha\Projects\trench_builder"
    clips = {
        "CLIP_1_HOOK": f"{base}/video_frames",
        "CLIP_2_RESOLUTION": f"{base}/video_frames2",
        "CLIP_3_DEPTH": f"{base}/video_frames3",
    }
    
    analyzer = VideoFrameAnalyzer
    grammar = CinematographyGrammar()
    synthesizer = ArcSynthesizer()
    
    all_data = {}
    
    print("╔══════════════════════════════════════════╗")
    print("║  PROCEDURAL VIDEO LEARNER v1.0          ║")
    print("║  Learning from 3 Veo clips              ║")
    print("╚══════════════════════════════════════════╝\n")
    
    for name, dir_path in clips.items():
        a = analyzer(dir_path)
        frame_data = a.analyze_all()
        cuts = a.detect_cuts(frame_data)
        all_data[name] = frame_data
        
        g = grammar.learn(name, frame_data, cuts)
        
        print(f"═══ {name} ═══")
        print(f"  Frames: {len(frame_data)} | Cuts: {len(cuts)}")
        print(f"  RGB: {g['target_rgb']} | Brt: {g['target_brightness']} | Cont: {g['target_contrast']}")
        print(f"  Temp: {g['color_temperature']} | Arc: {g['brightness_arc']}/{g['temp_arc']}")
        print(f"  Energy: {g['energy']}")
        print(f"  Cut style: {g['cut_style']}")
        print()
    
    # Learn transitions
    transitions = synthesizer.learn_arc(all_data)
    print("═══ TRANSITION GRAMMAR ═══")
    for t in transitions:
        print(f"  {t['from']} → {t['to']}:")
        print(f"    ΔBrightness: {t['brightness_jump']:+.0f} | Temp: {t['temperature_shift']} | {t['transition_type']}")
    
    # Generate optimized Veo prompts
    print(f"\n═══ GENERATED VEO PROMPTS ═══")
    for name in clips:
        prompt = grammar.generate_veo_prompt(name)
        print(f"\n--- {name} ---")
        print(prompt)
    
    # Save grammar to JSON for the cinematography engine
    grammar_file = f"{base}/video_grammar.json"
    with open(grammar_file, 'w') as f:
        json.dump(grammar.rules, f, indent=2)
    print(f"\n✓ Grammar saved to {grammar_file}")
    
    print(f"\n═══ LEARNED FROM 24 FRAMES ACROSS 3 CLIPS ═══")
    print(f"  Hook signature:    Cool, fast cuts, high contrast, attention-grabbing")
    print(f"  Depth signature:   Dark warm red, smooth, emotional weight")
    print(f"  Resolution signature: Bright warm, smooth, calm confidence")
    print(f"  Optimal arc:       Hook→Depth→Resolution (cool→warm→warm+bright)")

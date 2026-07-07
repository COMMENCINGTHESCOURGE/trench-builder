import os
import http.server
import socketserver

PORT = 8000

class LauncherHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            html_files = [f for f in os.listdir('.') if f.endswith('.html') and f != 'index.html']

            metadata = {
                "VINCULUM_TERRAIN.html": "Unified Substrate Engine — terrain, physics, AI, interiors, motion correction. 5 deltas merged.",
                "VINCULUM_INTERIORS.html": "3D Interior layout and boundary room crawler mapped to motor checkpoints.",
                "TRENCH_BUILDER_v5.html": "Perceptual Physics Subwoofer — thermal bloom, EM decay, caustics, Gemma 4 assistant.",
                "TRENCH_BUILDER_v4.html": "Hyperreal Rendering Pipeline — film grain, god rays, SSAO, physics-based avatar.",
                "TRENCH_BUILDER_v3.html": "Topography Survey + Interior Design + Raytrace — contour maps, room scan.",
                "TRENCH_BUILDER_v2.html": "Post-processing upgrade — UnrealBloom, SSAO pass.",
                "TRENCH_BUILDER_v1.html": "First proof: single HTML scene with materials and lighting.",
                "RESONANCE_HUD.html": "Voxel resonance meter displaying real-time frequency and Braille ASCII HUD.",
                "MECHA_VINCULUM.html": "Mecha joint trajectory debugger — correction delta-learning loops, chroma cascade.",
                "NOVA_HORIZON_3D.html": "Stellar orbital trajectory engine using Three.js projection.",
                "MANIFESTATION_BRIDGE.html": "Electrical-Optical/Acoustic/Thermal transfer. Brownout propagation.",
                "HYPERPOLY_v5.html": "Faceted structural survival — weather, stress, audio, generators, crafting.",
                "CINEMATOGRAPHY_ENGINE.html": "12-beat B-roll system. GameShark Creative Mode. Veo grammar camera paths.",
                "BACKROOMS_MEP.html": "35 infrastructure components — outlets, switches, HVAC, conduit, doors.",
                "CHROMA_CONSTRUCTOR.html": "Chroma cascade constructor — hue/saturation/luminance layer builder.",
                "FACIAL_CITY_GRID.html": "Facial topology mapped to urban grid geometry.",
                "FRAC_DEMO.html": "Fractal geometry demonstration with Three.js.",
                "KIRAGAMI_MECH.html": "Kiragami paper-fold mecha construction.",
                "STACK_CATHEDRAL.html": "Stack-based cathedral geometry generator.",
                "CHINESE_CALCULATOR.html": "Chinese abacus-style calculator interface.",
                "mecha_knee_viewer.html": "Mecha knee joint articulation viewer."
            }

            dashboard_html = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VINCULUM LAUNCHER — 1 Unified Substrate</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a10;
            color: #00d4ff;
            font-family: 'Rajdhani', sans-serif;
            padding: 40px;
            line-height: 1.6;
        }
        .container { max-width: 1100px; margin: 0 auto; }
        header {
            border-bottom: 2px solid rgba(0, 212, 255, 0.2);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .title {
            font-size: 36px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 4px;
            text-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
        }
        .subtitle { color: #5a6b7f; font-size: 14px; margin-top: 5px; letter-spacing: 2px; }
        .launch-count { color: #ff9944; font-size: 12px; margin-top: 4px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
        .card {
            background: #11121d;
            border: 1px solid rgba(0, 212, 255, 0.15);
            border-radius: 4px;
            padding: 20px;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
        }
        .card:hover {
            border-color: #00d4ff;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.25);
            transform: translateY(-2px);
        }
        .card.merged {
            border-color: #ff9944;
            background: #14110d;
        }
        .card.merged .file-name { color: #ff9944; }
        .tag {
            display: inline-block;
            font-size: 8px;
            padding: 2px 6px;
            border-radius: 3px;
            margin-right: 3px;
            letter-spacing: .5px;
            text-transform: uppercase;
        }
        .tag.phys { background: #224422; color: #44aa44; }
        .tag.sim { background: #220033; color: #aa44aa; }
        .tag.vis { background: #002244; color: #4488cc; }
        .tag.meta { background: #222222; color: #888888; }
        .tag.ai { background: #112244; color: #4488ff; }
        .tag.interior { background: #221122; color: #aa44aa; }
        .file-name {
            font-size: 14px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 6px;
            word-break: break-all;
        }
        .file-desc { color: #5a6b7f; font-size: 11px; margin-bottom: 16px; flex-grow: 1; line-height: 1.5; }
        .btn {
            display: inline-block;
            background: rgba(0, 212, 255, 0.05);
            color: #00d4ff;
            border: 1px solid #00d4ff;
            padding: 8px 16px;
            text-decoration: none;
            font-weight: 700;
            text-align: center;
            border-radius: 4px;
            transition: all 0.3s;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 1.5px;
        }
        .btn:hover {
            background: #00d4ff;
            color: #0a0a10;
            box-shadow: 0 0 12px rgba(0, 212, 255, 0.5);
        }
        .empty {
            grid-column: 1 / -1;
            text-align: center;
            padding: 50px;
            color: #5a6b7f;
            border: 1px dashed rgba(0, 212, 255, 0.2);
            border-radius: 4px;
        }
        footer {
            margin-top: 40px;
            border-top: 1px solid rgba(0, 212, 255, 0.1);
            padding-top: 16px;
            color: #3a4b5f;
            font-size: 11px;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="title">VINCULUM LAUNCHER</div>
            <div class="subtitle">Cognitive Compression Substrate: 10-HTML-artifacts → 1 launcher</div>
            <div class="launch-count">""" + str(len(html_files)) + """ modules detected</div>
        </header>
        <div class="grid">"""

            if not html_files:
                dashboard_html += """
            <div class="empty">
                No HTML files detected.<br>
                Place your HTML artifacts in the same directory as this script.
            </div>"""
            else:
                for f in sorted(html_files):
                    desc = metadata.get(f, "Vinculum Framework specialized module.")
                    tags = ""
                    if "TERRAIN" in f: tags += '<span class="tag sim">TERRAIN</span><span class="tag ai">AI</span><span class="tag interior">INTERIOR</span>'
                    elif "INTERIOR" in f: tags += '<span class="tag interior">INTERIOR</span>'
                    elif "TRENCH" in f: tags += '<span class="tag phys">PHYSICS</span>'
                    elif "MECHA" in f: tags += '<span class="tag sim">MECHA</span>'
                    elif "RESONANCE" in f: tags += '<span class="tag vis">HUD</span>'
                    elif "NOVA" in f: tags += '<span class="tag vis">SPACE</span>'
                    else: tags += '<span class="tag meta">MODULE</span>'
                    merged_class = " merged" if "TERRAIN" in f else ""
                    dashboard_html += f"""
            <div class="card{merged_class}">
                <div>
                    <div class="file-name">{f}</div>
                    <div>{tags}</div>
                    <div class="file-desc">{desc}</div>
                </div>
                <a href="/{f}" class="btn" target="_blank">LAUNCH</a>
            </div>"""

            dashboard_html += """
        </div>
        <footer>
            VINCULUM LAUNCHER · 10-HTML-artifacts → 1 launcher · Substrate Engine v1.0
        </footer>
    </div>
</body>
</html>"""
            self.wfile.write(dashboard_html.encode('utf-8'))
        else:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

print(f"[+] Starting VINCULUM LAUNCHER on http://localhost:{PORT}")
print("[+] Press Ctrl+C to terminate the session.")
with socketserver.TCPServer(("", PORT), LauncherHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[-] Server successfully terminated.")

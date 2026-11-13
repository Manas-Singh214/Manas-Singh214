import os
import json
import base64
import subprocess
from xml.sax.saxutils import escape

PALETTE = {
    "bg": "#1C1714", "surface": "#2A231D", "text": "#EAE0D5",
    "accent": "#C49A6C", "grid": "#3A3129"
}
STATIC_MODE = os.environ.get("STATIC") == "1"
OUT_DIR = "cards"
os.makedirs(OUT_DIR, exist_ok=True)


def get_font_base64():
    if not os.path.exists("font.ttf"):
        return ""
    subprocess.run(
        ["pyftsubset", "font.ttf", "--text=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?|&:-/ ", "--flavor=woff", "--output-file=subset.woff"],
        check=False,
    )
    if os.path.exists("subset.woff"):
        with open("subset.woff", "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"@font-face {{ font-family: 'BrandFont'; src: url(data:font/woff;charset=utf-8;base64,{b64}) format('woff'); }}"
    return ""


def get_image_base64(filepath):
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    return ""


FONT_CSS = get_font_base64()
PORTRAIT_B64 = get_image_base64("PF.jpg")


def render_svg(filename, width, height, content, delay_sec):
    anim_css = ".card-container { opacity: 1; }" if STATIC_MODE else f".card-container {{ animation: slideUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; animation-delay: {delay_sec}s; opacity: 0; transform: translateY(20px); }} @keyframes slideUp {{ to {{ opacity: 1; transform: translateY(0); }} }} @media (prefers-reduced-motion: reduce) {{ .card-container {{ animation: none; opacity: 1; transform: none; }} }}"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}"><defs><style>{FONT_CSS} text {{ font-family: 'BrandFont', monospace, sans-serif; fill: {PALETTE['text']}; }} .bg {{ fill: {PALETTE['bg']}; rx: 12px; }} .surface {{ fill: {PALETTE['surface']}; rx: 8px; }} {anim_css}</style><pattern id="dotGrid" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{PALETTE['grid']}"/></pattern></defs><g class="card-container"><rect width="{width}" height="{height}" class="bg"/><rect width="{width}" height="{height}" fill="url(#dotGrid)" rx="12px"/>{content}</g></svg>"""
    with open(os.path.join(OUT_DIR, filename), "w", encoding="utf-8") as f:
        f.write(svg)


render_svg("hero.svg", 800, 160, f"""<circle cx="80" cy="80" r="50" fill="{PALETTE['surface']}"/><image href="{PORTRAIT_B64}" x="30" y="30" width="100" height="100" clip-path="inset(0% round 50px)" /><text x="160" y="70" font-size="32" font-weight="bold" fill="{PALETTE['accent']}">Manas Singh</text><text x="160" y="105" font-size="18">Data Analyst &amp; Software Developer</text><text x="160" y="135" font-size="14" fill="{PALETTE['grid']}">"Where mathematics reveals patterns, design gives them purpose."</text>""", 0.1)

for i, (t, s) in enumerate([("Python | SQL | Tableau", "Data Stack"), ("FastAPI | React | Docker", "Web Stack"), ("BPIT IT '28", "Education")]):
    render_svg(f"tile_{i+1}.svg", 256, 100, f"""<rect x="10" y="10" width="236" height="80" class="surface"/><text x="128" y="45" font-size="16" font-weight="bold" text-anchor="middle" fill="{PALETTE['accent']}">{escape(t)}</text><text x="128" y="70" font-size="12" text-anchor="middle">{escape(s)}</text>""", 0.3 + (i * 0.1))

stats = {"streak": 12, "active_days": 145, "busiest_day": "Tuesday"}
if os.path.exists("github-stats.json"):
    with open("github-stats.json") as f:
        stats = json.load(f)

smil_anim = "" if STATIC_MODE else f"""<animate attributeName="stroke-dashoffset" from="1000" to="0" dur="2s" fill="freeze" />"""
render_svg("contributions.svg", 800, 200, f"""<rect x="20" y="20" width="760" height="160" class="surface"/><text x="40" y="55" font-size="20" font-weight="bold">Contribution Metrics</text><text x="40" y="90" font-size="14">Current Streak: <tspan fill="{PALETTE['accent']}">{escape(str(stats['streak']))} Days</tspan></text><text x="40" y="120" font-size="14">Active Days: <tspan fill="{PALETTE['accent']}">{escape(str(stats['active_days']))}</tspan></text><text x="40" y="150" font-size="14">Busiest Day: <tspan fill="{PALETTE['accent']}">{escape(str(stats['busiest_day']))}</tspan></text><path d="M 250 120 Q 300 50 350 120 T 450 120 T 550 120 T 650 100 T 750 140" fill="none" stroke="{PALETTE['accent']}" stroke-width="4" stroke-dasharray="1000" stroke-dashoffset="1000">{smil_anim}</path>""", 0.6)

for i, (n, d, t) in enumerate([("Exam Duty Scheduler", "Full-stack fair scheduling app with PostgreSQL.", "FastAPI"), ("Cashflow Intelligence", "Banking & cybercrime analytics data pipeline.", "Python"), ("PyLLM", "Local LLM integrations and exploratory tools.", "AI/ML"), ("Hand Gestures", "Computer vision model for spatial hand tracking.", "OpenCV")]):
    render_svg(f"repo_{i}.svg", 392, 120, f"""<rect x="10" y="10" width="372" height="100" class="surface" stroke="{PALETTE['grid']}" stroke-width="2"/><text x="30" y="45" font-size="18" font-weight="bold" fill="{PALETTE['accent']}">{escape(n)}</text><text x="30" y="70" font-size="12">{escape(d)}</text><text x="340" y="45" font-size="12" text-anchor="end" fill="{PALETTE['grid']}">{escape(t)}</text>""", 0.8 + (i * 0.1))

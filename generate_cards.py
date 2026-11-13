"""Generate the README's SVG cards; set STATIC=1 for motion-free screenshots."""

import base64
import json
import mimetypes
import os
import shutil
import subprocess
import tempfile
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape


ROOT_DIR = Path(__file__).resolve().parent
OUT_DIR = ROOT_DIR / "cards"
PALETTE = {
    "bg": "#0B1016",
    "surface": "#111A24",
    "text": "#D6DEE7",
    "accent": "#79AEB8",
    "grid": "#273442",
}
STATIC_MODE = os.environ.get("STATIC") == "1"
IST = timezone(timedelta(hours=5, minutes=30))
USERNAME = "Manas-Singh214"
PROFILE_URL = f"https://github.com/{USERNAME}"
TILES = (
    ("Data & Analytics", "PYTHON | SQL | VISUALIZATION", f"{PROFILE_URL}/Cashflow-Intelligence"),
    ("Machine Learning", "COMPUTER VISION | LLMS", f"{PROFILE_URL}/Hand-Gestures"),
    ("Software & Design", "FASTAPI | REACT | UI/UX", f"{PROFILE_URL}/Duty-Scheduler"),
)
REPOSITORIES = (
    (
        "Duty Scheduler",
        "Fair, full-stack scheduling with PostgreSQL.",
        "FASTAPI",
        f"{PROFILE_URL}/Duty-Scheduler",
    ),
    (
        "Cashflow Intelligence",
        "Banking analytics and financial data pipelines.",
        "PYTHON",
        f"{PROFILE_URL}/Cashflow-Intelligence",
    ),
    (
        "PyLLM",
        "Local LLM integrations and exploratory tools.",
        "AI / ML",
        f"{PROFILE_URL}/PyLLM",
    ),
    (
        "Hand Gestures",
        "Computer vision for spatial hand tracking.",
        "OPENCV",
        f"{PROFILE_URL}/Hand-Gestures",
    ),
)
ASCII_PORTRAIT = (
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "                                                                ",
    "                                    .::.                        ",
    "                               :=*#%%@@%%##*=:                  ",
    "                             =#%%%%%%%%%%%@@@@%*=.              ",
    "                           +%%%%%%%@@@@%%%%%%%@@@%#+-           ",
    "                         .#@%%%%%@@@@@@@@@@%@@@@@@@@@%*:        ",
    "                        -%%%%@@@@@@@@@@@@@@@@@@@@@@@@@@@*.      ",
    "                       :%%%%@@%%#****##%%@@%%%%@@@@%@@@@@*.     ",
    "                       #%%%@#=+-:=++===+**#%%%%%%%####@@%*:     ",
    "                      -%%%@%-===+=+++==-:.-+##%##*+===+#+-      ",
    "                      *%%%@#::-+*::-==-:...-+++=---::-=-.       ",
    "                     :%%%%@+:-+*=   =--:....:=++****+--         ",
    "                     +%%@@%::-:+=. :=-:....::=*##%%%@*-         ",
    "                     %@%@@+.. :-=  ===-..::::::+*#@%##*.        ",
    "                    :@@@%+:  .:-+:=+=+=-:..:::..=***=#%:        ",
    "                    :@@*:    .:-==+=====-:--::...:-:.+:         ",
    "                     --      .:-+++=---==+++++====:.            ",
    "                 =*%#.     ....+%***+=-==**=+***##-:::          ",
    "               .:#@@*     ..::.-*#%##****##**@%*#%@%#+          ",
    "                 *@@%:   .::::--=%@%%%%%%%#######%%#:           ",
    " :-=====++-    .=%@@@%-  :----==-+%@@@@@@@%#+====**:            ",
    "   -****===:  :*+*@@@@@*:.:-==++==+%%@@@@@@#*++##=              ",
    "-:.:---*%%+ ..:-.:%@@@@@@#=-==++**+*#@@@@@@%%*+#-               ",
    ":=+##+--*%-      -#@@@@@@@@@##*######%@@@@@@@%%+                ",
    "  :*%@@%=-.    :+%#%@@@@@@@@@@@@@@@@%%@@@@@@@@@-                ",
    "  --=#%%%+==-=#@@@%+@@@@@@@@@@@@@@@@@@@@@@@@@@*.                ",
    ":--==++=##*#%*%@@@#=@@@@@@@@@@@@@@@@@@#*#*++*+#%*=              ",
    "#%*==++=-.-+#%#%@@*=@@@@@@@@@@@@@@@@@#=-:-+**##*++:..           ",
    "%%%%#*+-   -*+###@*-@@@@@@@@@@@@@@@@%#**#@@@@@%%%*:  .          ",
    "-*%@@@%+    =:=##+-==@@@@@@@@@@@@@@@+:*@@@@%@@@@@@#-.:-.        ",
    ":-*%@@%==-.:=:--*=-:-@@@@@@@@@@@@@@#.+@%%##%%+*@%%#=++*+.       ",
    "-+*+**-:-+***#+=:.-=%@@@@@@@@@@@@@@+-@%#*--+=-+#*+=   =%=       ",
    "=++++:   -%@@@@%=  +@@@@@@@@@@@@@@@++@%**:.:.-*###=    +*       ",
    "%*++=    :*#++#%+=:=@@@@@@@@@@@@@@@*#@@@%=-+++%@@@#-:.:=@+      ",
    "@@%*.   .==----: :-+@@@@@@@@@@@@@@@-%@%@@#*+=%@@@@#+++##%#      ",
    "@@@*-. :-=-::-:    +@@@@@@@@@@@@@@% +%+*#+:  #@%#*- :=#*-*.     ",
    "%@*---*%#+-=+=     %@@@@@@@@@@@@@@*.=*++*=  .*##++.  :+:.#:     ",
    "+-   =%%%%#%%*.   =@@@@@@@@@@@@@@@# +*+**=  -##**=  :== *#:     ",
)
ASCII_TONE_RAMP = "  ..::--==++**##%%@@"


def ascii_tone(index: int) -> str:
    if index <= 3:
        return "#52616D"
    if index <= 8:
        return "#8795A1"
    if index <= 14:
        return "#C0CAD3"
    return PALETTE["accent"]


def render_ascii_line(line: str) -> str:
    spans = []
    current_color = ascii_tone(ASCII_TONE_RAMP.index(line[0]))
    current_run = [line[0]]
    for character in line[1:]:
        color = ascii_tone(ASCII_TONE_RAMP.index(character))
        if color == current_color:
            current_run.append(character)
            continue
        spans.append(f'<tspan fill="{current_color}">{escape("".join(current_run))}</tspan>')
        current_color = color
        current_run = [character]
    spans.append(f'<tspan fill="{current_color}">{escape("".join(current_run))}</tspan>')
    return "".join(spans)


def subset_font() -> str:
    font_path = ROOT_DIR / "font.ttf"
    if not font_path.is_file():
        return ""
    pyftsubset = shutil.which("pyftsubset")
    if pyftsubset is None:
        raise RuntimeError("font.ttf is present, but pyftsubset is not installed.")

    glyphs = "".join(chr(codepoint) for codepoint in range(32, 127))
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "brand.woff"
        subprocess.run(
            [
                pyftsubset,
                str(font_path),
                f"--text={glyphs}",
                "--flavor=woff",
                f"--output-file={output_path}",
            ],
            check=True,
        )
        font_data = base64.b64encode(output_path.read_bytes()).decode("ascii")
    return (
        "@font-face { font-family: 'BrandFont'; "
        f"src: url(data:font/woff;charset=utf-8;base64,{font_data}) format('woff'); }}"
    )


def optional_portrait() -> str:
    portrait_path = ROOT_DIR / "PF.jpg"
    if not portrait_path.is_file():
        return ""
    mime_type = mimetypes.guess_type(portrait_path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(portrait_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


FONT_CSS = subset_font()
PORTRAIT_DATA = optional_portrait()


def render_svg(filename: str, width: int, height: int, content: str, delay: float) -> None:
    if STATIC_MODE:
        animation_css = (
            ".card-container { opacity: 1; transform: none; } "
            ".ascii-row { opacity: 1; }"
        )
    else:
        animation_css = (
            ".card-container { animation: cardIn .75s cubic-bezier(.2,.8,.2,1) "
            f"{delay:.2f}s both; }} "
            "@keyframes cardIn { from { opacity: 0; transform: translateY(18px); } "
            "to { opacity: 1; transform: translateY(0); } } "
            ".ascii-row { opacity: 0; animation: asciiReveal .18s ease-out both; } "
            "@keyframes asciiReveal { to { opacity: 1; } } "
            "@media (prefers-reduced-motion: reduce) { "
            ".card-container { animation: none !important; opacity: 1; transform: none; } "
            ".ascii-row { animation: none !important; opacity: 1; } "
            "animate, animateTransform { display: none !important; } }"
        )
    style = (
        f"{FONT_CSS} text {{ font-family: 'BrandFont', monospace, sans-serif; "
        f"fill: {PALETTE['text']}; }} "
        f".bg {{ fill: {PALETTE['bg']}; }} "
        f".surface {{ fill: {PALETTE['surface']}; }} "
        f".accent {{ fill: {PALETTE['accent']}; }} "
        f".muted {{ fill: {PALETTE['text']}; opacity: .7; }} "
        f".border {{ fill: none; stroke: {PALETTE['grid']}; stroke-width: 1; }} "
        f".ascii-portrait {{ font-family: monospace; fill: {PALETTE['accent']}; }} "
        f"{animation_css}"
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}"><defs><style>{style}</style></defs>'
        f'<g class="card-container"><rect width="{width}" height="{height}" rx="4" '
        f'class="bg"/><rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" '
        f'rx="4" class="border"/>{content}</g></svg>'
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / filename).write_text(svg, encoding="utf-8")


def load_contributions() -> dict[date, int]:
    path = ROOT_DIR / "github-stats.json"
    with path.open(encoding="utf-8-sig") as stats_file:
        payload = json.load(stats_file)
    entries = payload.get("contributions") if isinstance(payload, dict) else None
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{path.name} must contain a non-empty contributions array.")

    counts: dict[date, int] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Each contribution entry must be an object.")
        try:
            day = date.fromisoformat(entry["date"])
            count = entry["count"]
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Invalid contribution entry: {entry!r}") from error
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(f"Invalid contribution count for {day.isoformat()}: {count!r}")
        if day in counts:
            raise ValueError(f"Duplicate contribution date: {day.isoformat()}")
        counts[day] = count
    return counts


def month_sequence(start_day: date, end_day: date) -> list[date]:
    month = start_day.replace(day=1)
    months = []
    while month <= end_day:
        months.append(month)
        month = (month + timedelta(days=32)).replace(day=1)
    return months


def contribution_metrics(counts: dict[date, int]) -> tuple[int, int, str, Counter[str]]:
    today = date.today()
    streak_anchor = today if counts.get(today, 0) else today - timedelta(days=1)
    streak = 0
    while counts.get(streak_anchor, 0) > 0:
        streak += 1
        streak_anchor -= timedelta(days=1)

    active_start = today - timedelta(days=364)
    active_days = sum(
        count > 0 and active_start <= day <= today for day, count in counts.items()
    )
    weekday_totals: Counter[str] = Counter()
    for day, count in counts.items():
        weekday_totals[day.strftime("%A")] += count
    busiest_day = (
        max(weekday_totals, key=weekday_totals.get)
        if any(weekday_totals.values())
        else "No activity"
    )
    monthly_totals: Counter[str] = Counter()
    for day, count in counts.items():
        monthly_totals[day.strftime("%Y-%m")] += count
    return streak, active_days, busiest_day, monthly_totals


def render_hero() -> None:
    portrait = (
        f'<image href="{PORTRAIT_DATA}" x="30" y="30" width="100" height="100" '
        'preserveAspectRatio="xMidYMid slice" clip-path="url(#portraitClip)"/>'
        if PORTRAIT_DATA
        else '<text x="80" y="91" font-size="30" text-anchor="middle" class="accent">MS</text>'
    )
    content = (
        '<circle cx="80" cy="80" r="50" fill="#2A231D"/>'
        '<defs><clipPath id="portraitClip"><circle cx="80" cy="80" r="50"/></clipPath></defs>'
        f"{portrait}"
        '<text x="160" y="73" font-size="34" font-weight="bold" class="accent">Manas Singh</text>'
        '<text x="160" y="111" font-size="17">Data analytics, machine learning, visualization &amp; UI/UX</text>'
        '<text x="160" y="139" font-size="13" class="muted">Ideas to insight, built with purpose.</text>'
    )
    render_svg("hero.svg", 800, 160, content, 0.0)


def render_ascii_art() -> None:
    text_lines = "".join(
        f'<text x="36" y="{80 + index * 11.6}" font-size="12" '
        f'class="ascii-row ascii-portrait" xml:space="preserve" '
        f'style="animation-delay:{0.2 + index * 0.018:.3f}s">'
        f"{render_ascii_line(line)}</text>"
        for index, line in enumerate(ASCII_PORTRAIT)
    )
    content = (
        '<rect x="16" y="16" width="768" height="558" rx="2" class="surface"/>'
        '<rect x="16" y="16" width="768" height="558" rx="2" class="border"/>'
        '<text x="40" y="45" font-size="11" letter-spacing="2" '
        'class="muted">IMAGE STUDY / 01</text>'
        '<line x1="40" y1="58" x2="760" y2="58" class="border"/>'
        f"{text_lines}"
        '<line x1="520" y1="76" x2="520" y2="572" class="border"/>'
        '<text x="548" y="112" font-size="20" font-weight="bold" '
        'letter-spacing="1" class="accent">MANAS SINGH</text>'
        '<line x1="548" y1="128" x2="744" y2="128" stroke="#79AEB8" stroke-width="2"/>'
        '<text x="548" y="166" font-size="11" class="muted">PORTRAIT</text>'
        '<text x="548" y="188" font-size="13">GRAYSCALE STUDY</text>'
        '<text x="548" y="236" font-size="11" class="muted">CHARACTER GRID</text>'
        '<text x="548" y="258" font-size="13">64 x 42</text>'
        '<text x="548" y="306" font-size="11" class="muted">RENDER MODE</text>'
        '<text x="548" y="328" font-size="13">TONAL ASCII</text>'
        '<text x="548" y="376" font-size="11" class="muted">ANIMATION</text>'
        '<text x="548" y="398" font-size="13">ROW REVEAL</text>'
        '<text x="548" y="490" font-size="10" class="muted">DATA / ML / DESIGN</text>'
    )
    if not STATIC_MODE:
        content += (
            '<rect x="36" y="78" width="462" height="1" fill="#79AEB8" opacity=".7">'
            '<animate attributeName="y" from="78" to="566" begin="1.15s" '
            'dur="1.3s" fill="freeze"/>'
            '<animate attributeName="opacity" values="0;.7;.7;0" '
            'keyTimes="0;.08;.8;1" begin="1.15s" dur="1.3s" fill="freeze"/></rect>'
        )
    render_svg("ascii_art.svg", 800, 590, content, 0.15)


def render_tiles() -> None:
    for index, (title, subtitle, _) in enumerate(TILES):
        content = (
            '<rect x="8" y="8" width="240" height="92" rx="4" class="surface"/>'
            f'<text x="128" y="44" font-size="18" font-weight="bold" '
            f'text-anchor="middle" class="accent">{escape(title)}</text>'
            f'<text x="128" y="72" font-size="11" text-anchor="middle">'
            f"{escape(subtitle)}</text>"
        )
        render_svg(f"tile_{index + 1}.svg", 256, 108, content, 0.3 + index * 0.08)


def render_commit_clock() -> None:
    now = datetime.now(IST)
    hour_angle = (now.hour % 12 + now.minute / 60) * 30
    minute_angle = now.minute * 6
    content = (
        '<rect x="16" y="16" width="768" height="88" rx="4" class="surface"/>'
        f'<circle cx="66" cy="60" r="32" fill="none" stroke="{PALETTE["accent"]}" stroke-width="2"/>'
        f'<line x1="66" y1="60" x2="66" y2="43" stroke="{PALETTE["text"]}" stroke-width="3" '
        f'stroke-linecap="round" transform="rotate({hour_angle} 66 60)"/>'
        f'<line x1="66" y1="60" x2="66" y2="35" stroke="{PALETTE["accent"]}" stroke-width="2" '
        f'stroke-linecap="round" transform="rotate({minute_angle} 66 60)"/>'
        f'<circle cx="66" cy="60" r="3" fill="{PALETTE["accent"]}"/>'
        '<text x="120" y="51" font-size="18" font-weight="bold" class="accent">DAILY COMMIT CLOCK</text>'
        f'<text x="120" y="78" font-size="14">Updated {now.strftime("%Y-%m-%d %H:%M")} IST '
        '| Scheduled daily at 05:30 IST</text>'
    )
    render_svg("commit_clock.svg", 800, 120, content, 0.62)


def render_contribution_chart(counts: dict[date, int]) -> None:
    streak, active_days, busiest_day, monthly_totals = contribution_metrics(counts)
    months = month_sequence(min(counts), max(counts))
    values = [monthly_totals[month.strftime("%Y-%m")] for month in months]
    max_value = max(values, default=0)
    baseline = 204
    max_bar_height = 78
    bars = []
    for index, (month, value) in enumerate(zip(months, values)):
        x = 54 + index * 54
        bar_height = round(max_bar_height * value / max_value) if max_value else 0
        y = baseline - bar_height
        animate = (
            ""
            if STATIC_MODE
            else (
                f'<animate attributeName="height" from="0" to="{bar_height}" '
                f'begin="{0.82 + index * 0.05:.2f}s" dur=".55s" fill="freeze"/>'
                f'<animate attributeName="y" from="{baseline}" to="{y}" '
                f'begin="{0.82 + index * 0.05:.2f}s" dur=".55s" fill="freeze"/>'
            )
        )
        bars.append(
            f'<rect x="{x}" y="{y}" width="38" height="{bar_height}" rx="1" '
            f'fill="{PALETTE["accent"]}" opacity=".9">{animate}</rect>'
            f'<text x="{x + 19}" y="{max(y - 7, 115)}" font-size="10" '
            f'text-anchor="middle" class="muted">{value}</text>'
            f'<text x="{x + 19}" y="223" font-size="9" text-anchor="middle">'
            f"{month.strftime('%b')}</text>"
        )
    content = (
        '<rect x="20" y="16" width="760" height="228" rx="4" class="surface"/>'
        '<text x="40" y="47" font-size="20" font-weight="bold" class="accent">'
        "Contribution Metrics</text>"
        f'<text x="40" y="78" font-size="13">Streak: <tspan class="accent">'
        f'{streak} {"day" if streak == 1 else "days"}</tspan></text>'
        f'<text x="246" y="78" font-size="13">Active days: '
        f'<tspan class="accent">{active_days}</tspan></text>'
        f'<text x="490" y="78" font-size="13">Busiest day: '
        f'<tspan class="accent">{escape(busiest_day)}</tspan></text>'
        f'<line x1="48" y1="{baseline}" x2="758" y2="{baseline}" '
        f'stroke="{PALETTE["grid"]}" stroke-width="1"/>'
        f'{"".join(bars)}'
        '<text x="40" y="238" font-size="9" class="muted">Contributions per month</text>'
    )
    render_svg("contributions.svg", 800, 260, content, 0.78)


def render_repositories() -> None:
    for index, (name, description, language, _) in enumerate(REPOSITORIES):
        content = (
            '<rect x="10" y="10" width="372" height="100" rx="4" class="surface" '
            f'stroke="{PALETTE["grid"]}" stroke-width="1"/>'
            f'<text x="28" y="43" font-size="18" font-weight="bold" '
            f'class="accent">{escape(name)}</text>'
            f'<text x="28" y="69" font-size="12">{escape(description)}</text>'
            f'<text x="364" y="91" font-size="11" text-anchor="end" '
            f'class="muted">{escape(language)}</text>'
        )
        render_svg(f"repo_{index}.svg", 392, 120, content, 0.94 + index * 0.1)


def render_contribution_graph(counts: dict[date, int]) -> None:
    first_day = min(counts)
    last_day = max(counts)
    start_day = first_day - timedelta(days=(first_day.weekday() + 1) % 7)
    week_count = (last_day - start_day).days // 7 + 1
    cell_size = 11
    cell_gap = 3
    step = cell_size + cell_gap
    grid_x = 54
    grid_y = 58
    cells = []
    for day, count in sorted(counts.items()):
        week = (day - start_day).days // 7
        weekday = (day.weekday() + 1) % 7
        if count == 0:
            color = PALETTE["grid"]
        else:
            color = PALETTE["accent"]
        opacity = 1 if count == 0 else min(1, 0.3 + 0.22 * (count - 1))
        x = grid_x + week * step
        y = grid_y + weekday * step
        cells.append(
            f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" '
            f'fill="{color}" opacity="{opacity:.2f}"><title>{day.isoformat()}: '
            f'{count} contributions</title></rect>'
        )

    month_labels = []
    month_cursor = first_day
    while month_cursor <= last_day:
        week = (month_cursor - start_day).days // 7
        month_labels.append(
            f'<text x="{grid_x + week * step}" y="47" font-size="10" class="muted">'
            f"{month_cursor.strftime('%b')}</text>"
        )
        month_cursor = (month_cursor + timedelta(days=32)).replace(day=1)

    weekdays = "".join(
        f'<text x="28" y="{grid_y + index * step + 9}" font-size="8" '
        f'text-anchor="middle" class="muted">{label}</text>'
        for index, label in ((1, "M"), (3, "W"), (5, "F"))
    )
    grid_width = week_count * step
    panel_width = max(760, grid_width + 40)
    content = (
        f'<rect x="20" y="12" width="{panel_width}" height="170" rx="4" class="surface"/>'
        '<text x="40" y="32" font-size="16" font-weight="bold" class="accent">'
        "Contribution Graph</text>"
        f'{"".join(month_labels)}{weekdays}{"".join(cells)}'
        f'<text x="54" y="170" font-size="9" class="muted">'
        f"Daily contributions over the past year · {sum(counts.values())} total</text>"
    )
    render_svg("contribution_graph.svg", max(800, grid_width + 80), 190, content, 1.42)


def main() -> None:
    counts = load_contributions()
    render_hero()
    render_ascii_art()
    render_tiles()
    render_commit_clock()
    render_contribution_chart(counts)
    render_repositories()
    render_contribution_graph(counts)


if __name__ == "__main__":
    main()

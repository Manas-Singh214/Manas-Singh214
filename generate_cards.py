"""Generate the README's SVG cards; set STATIC=1 for motion-free screenshots."""

import base64
import json
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
    "paper": "#F3F3F1",
    "paper_deep": "#E2E2DE",
    "ink": "#111111",
    "ink_soft": "#3A3A3C",
    "muted": "#6E6E73",
    "rule": "#DCDCD7",
    "blue": "#2F55FF",
    "red": "#EF3B2D",
    "yellow": "#FFC81A",
    "terminal": "#0D1117",
    "terminal_rule": "#30363D",
}
STATIC_MODE = os.environ.get("STATIC") == "1"
IST = timezone(timedelta(hours=5, minutes=30))
USERNAME = "Manas-Singh214"
PROFILE_URL = f"https://github.com/{USERNAME}"
TILES = (
    (
        "ANALYZE",
        "Data analytics",
        "Python / SQL / visualization",
        PALETTE["blue"],
        "#FFFFFF",
        f"{PROFILE_URL}/Cashflow-Intelligence",
    ),
    (
        "LEARN",
        "Machine learning",
        "Computer vision / local LLMs",
        PALETTE["red"],
        "#FFFFFF",
        f"{PROFILE_URL}/Hand-Gestures",
    ),
    (
        "BUILD",
        "Software & design",
        "FastAPI / React / UI/UX",
        PALETTE["yellow"],
        PALETTE["ink"],
        f"{PROFILE_URL}/Duty-Scheduler",
    ),
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
        return PALETTE["paper_deep"]
    if index <= 8:
        return PALETTE["muted"]
    if index <= 14:
        return PALETTE["blue"]
    return PALETTE["ink"]


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


FONT_CSS = subset_font()


def render_svg(
    filename: str,
    width: int,
    height: int,
    content: str,
    delay: float,
    label: str,
) -> None:
    if STATIC_MODE:
        animation_css = (
            ".card-container { opacity: 1; transform: none; } "
            ".fade { opacity: 1; } .grow { transform: none; }"
        )
    else:
        animation_css = (
            ".card-container { opacity: 0; animation: rise .75s "
            f"cubic-bezier(.2,.8,.2,1) {delay:.2f}s both; }} "
            "@keyframes rise { from { opacity: 0; transform: translateY(14px); } "
            "to { opacity: 1; transform: translateY(0); } } "
            ".fade { opacity: 0; animation: fadeIn .45s ease-out both; } "
            "@keyframes fadeIn { to { opacity: 1; } } "
            ".grow { transform-box: fill-box; transform-origin: bottom; "
            "transform: scaleY(0); animation: growUp .65s cubic-bezier(.2,.8,.2,1) both; } "
            "@keyframes growUp { to { transform: scaleY(1); } } "
            "@media (prefers-reduced-motion: reduce) { "
            ".card-container, .fade, .grow { animation: none !important; "
            "opacity: 1 !important; transform: none !important; } "
            ".ascii-mask { width: 460.8px !important; } "
            ".ascii-cursor, animate, animateTransform { display: none !important; } }"
        )
    style = (
        f"{FONT_CSS} text {{ font-family: 'BrandFont', system-ui, sans-serif; }} "
        ".serif { font-family: Georgia, 'Times New Roman', serif; } "
        ".mono { font-family: 'SFMono-Regular', Consolas, monospace; } "
        f".paper {{ fill: {PALETTE['paper']}; }} "
        f".ink {{ fill: {PALETTE['ink']}; }} "
        f".soft {{ fill: {PALETTE['ink_soft']}; }} "
        f".muted {{ fill: {PALETTE['muted']}; }} "
        f".blue {{ fill: {PALETTE['blue']}; }} "
        f".rule {{ stroke: {PALETTE['rule']}; }} "
        ".ascii-portrait { font-family: 'SFMono-Regular', Consolas, monospace; } "
        f"{animation_css}"
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{escape(label)}">'
        f'<title>{escape(label)}</title><defs><style>{style}</style></defs>'
        f'<g class="card-container">{content}</g></svg>'
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


def render_ascii_portrait() -> tuple[str, str]:
    font_size = 12
    line_height = 11.6
    row_width = 64 * font_size * 0.6
    definitions = []
    rows = []
    for index, line in enumerate(ASCII_PORTRAIT):
        baseline = font_size + index * line_height
        clip_id = f"portrait-row-{index}"
        if STATIC_MODE:
            mask = (
                f'<rect x="0" y="{baseline - font_size}" width="{row_width}" '
                f'height="{line_height}"/>'
            )
            cursor = ""
        else:
            start = 0.42 + index * 0.04
            mask = (
                f'<rect class="ascii-mask" x="0" y="{baseline - font_size}" '
                f'width="0" height="{line_height}">'
                f'<animate attributeName="width" from="0" to="{row_width}" '
                f'begin="{start:.2f}s" dur=".12s" fill="freeze"/></rect>'
            )
            cursor = (
                f'<rect class="ascii-cursor" x="0" y="{baseline - 9}" width="7.2" '
                f'height="9" fill="{PALETTE["blue"]}" opacity="0">'
                f'<animate attributeName="x" from="0" to="{row_width}" '
                f'begin="{start:.2f}s" dur=".12s" fill="freeze"/>'
                f'<set attributeName="opacity" to=".9" begin="{start:.2f}s"/>'
                f'<set attributeName="opacity" to="0" begin="{start + 0.12:.2f}s"/>'
                "</rect>"
            )
        definitions.append(
            f'<clipPath id="{clip_id}" clipPathUnits="userSpaceOnUse">{mask}</clipPath>'
        )
        rows.append(
            f'<g clip-path="url(#{clip_id})"><text x="0" y="{baseline}" '
            f'class="ascii-portrait" font-size="{font_size}" xml:space="preserve" '
            f'textLength="{row_width}" lengthAdjust="spacing">'
            f"{render_ascii_line(line)}</text></g>{cursor}"
        )
    return "".join(definitions), "".join(rows)


def render_hero() -> None:
    portrait_defs, portrait_rows = render_ascii_portrait()
    content = (
        f'<rect width="880" height="420" rx="14" fill="{PALETTE["paper"]}"/>'
        '<text x="48" y="62" class="mono" font-size="12" letter-spacing="1.5" '
        f'fill="{PALETTE["muted"]}">DATA ANALYST / SOFTWARE DEVELOPER</text>'
        '<text x="42" y="192" class="serif" font-size="112" '
        f'fill="{PALETTE["ink"]}">Manas</text>'
        '<text x="42" y="289" class="serif" font-size="104" font-style="italic" '
        f'fill="{PALETTE["blue"]}">Singh</text>'
        '<text x="48" y="341" font-size="17" '
        f'fill="{PALETTE["ink_soft"]}">Data analytics, machine learning &amp; UI/UX.</text>'
        '<text x="48" y="386" class="mono" font-size="12" letter-spacing=".8" '
        f'fill="{PALETTE["muted"]}">PYTHON  /  SQL  /  VISUALIZATION</text>'
        f'<line x1="488" y1="42" x2="488" y2="378" stroke="{PALETTE["rule"]}"/>'
        '<text x="510" y="30" class="mono" font-size="10" letter-spacing="1" '
        f'fill="{PALETTE["muted"]}">PORTRAIT / ASCII</text>'
        f'<defs>{portrait_defs}</defs>'
        f'<g transform="translate(510 35) scale(.74)">{portrait_rows}</g>'
    )
    render_svg(
        "hero.svg",
        880,
        420,
        content,
        0.0,
        "Manas Singh with an animated ASCII portrait",
    )


def render_tiles() -> None:
    for index, (label, title, subtitle, background, foreground, _) in enumerate(TILES):
        content = (
            f'<rect x="4" y="4" width="285" height="204" rx="14" fill="{background}"/>'
            f'<text x="24" y="34" class="mono" font-size="11" letter-spacing="1.2" '
            f'fill="{foreground}">{index + 1:02d} / {escape(label)}</text>'
            f'<text x="24" y="105" class="serif" font-size="31" fill="{foreground}">'
            f'{escape(title)}</text>'
            f'<text x="24" y="157" font-size="13" fill="{foreground}" opacity=".88">'
            f'{escape(subtitle)}</text>'
            f'<path d="M259 24h12v12m0-12-14 14" fill="none" stroke="{foreground}" '
            'stroke-width="1.5"/>'
        )
        render_svg(
            f"tile_{index + 1}.svg",
            293,
            212,
            content,
            5.0 + index * 0.08,
            f"{label.title()}: {title}",
        )


def render_commit_clock() -> None:
    now = datetime.now(IST)
    hour_angle = (now.hour % 12 + now.minute / 60) * 30
    minute_angle = now.minute * 6
    content = (
        f'<rect width="880" height="122" rx="14" fill="{PALETTE["paper"]}"/>'
        f'<circle cx="70" cy="61" r="37" fill="none" stroke="{PALETTE["blue"]}" stroke-width="2"/>'
        f'<line x1="70" y1="61" x2="70" y2="41" stroke="{PALETTE["ink"]}" stroke-width="3" '
        f'stroke-linecap="round" transform="rotate({hour_angle} 70 61)"/>'
        f'<line x1="70" y1="61" x2="70" y2="34" stroke="{PALETTE["blue"]}" stroke-width="2" '
        f'stroke-linecap="round" transform="rotate({minute_angle} 70 61)"/>'
        f'<circle cx="70" cy="61" r="3.5" fill="{PALETTE["blue"]}"/>'
        '<text x="132" y="48" class="mono" font-size="11" letter-spacing="1.5" '
        f'fill="{PALETTE["muted"]}">DAILY COMMIT CLOCK</text>'
        '<text x="132" y="82" class="serif" font-size="25" '
        f'fill="{PALETTE["ink"]}">{now.strftime("%H:%M")} IST</text>'
        f'<text x="838" y="70" text-anchor="end" font-size="14" '
        f'fill="{PALETTE["ink_soft"]}">Updated {now.strftime("%Y-%m-%d")} | '
        "Scheduled daily at 05:30 IST</text>"
    )
    render_svg(
        "commit_clock.svg",
        880,
        122,
        content,
        5.5,
        "Daily commit clock in India Standard Time",
    )


def render_contribution_chart(counts: dict[date, int]) -> None:
    streak, active_days, busiest_day, monthly_totals = contribution_metrics(counts)
    months = month_sequence(min(counts), max(counts))[-12:]
    values = [monthly_totals[month.strftime("%Y-%m")] for month in months]
    max_value = max(values, default=0)
    baseline = 273
    max_bar_height = 115
    bars = []
    for index, (month, value) in enumerate(zip(months, values)):
        x = 40 + index * 47
        bar_height = round(max_bar_height * value / max_value) if max_value else 0
        y = baseline - bar_height
        fill = PALETTE["blue"] if value == max_value and value else PALETTE["ink"]
        bars.append(
            f'<rect class="grow" style="animation-delay:{4.1 + index * 0.04:.2f}s" '
            f'x="{x}" y="{y}" width="31" height="{bar_height}" rx="3" fill="{fill}"/>'
            f'<text x="{x + 15.5}" y="{max(y - 8, 151)}" font-size="9" '
            f'text-anchor="middle" fill="{PALETTE["muted"]}">{value}</text>'
            f'<text x="{x + 15.5}" y="297" class="mono" font-size="9" '
            f'text-anchor="middle" fill="{PALETTE["muted"]}">{month.strftime("%b")}</text>'
        )
    content = (
        f'<rect width="880" height="350" rx="14" fill="{PALETTE["paper"]}"/>'
        '<text x="40" y="44" class="mono" font-size="11" letter-spacing="1.3" '
        f'fill="{PALETTE["muted"]}">GITHUB CONTRIBUTIONS / LAST 12 MONTHS</text>'
        f'<text x="40" y="105" class="serif" font-size="39" '
        f'fill="{PALETTE["ink"]}">{sum(values)} contributions</text>'
        f'<line x1="40" y1="{baseline}" x2="606" y2="{baseline}" '
        f'stroke="{PALETTE["rule"]}" stroke-width="1"/>'
        f'{"".join(bars)}'
        f'<line x1="630" y1="38" x2="630" y2="312" stroke="{PALETTE["rule"]}"/>'
        '<text x="660" y="58" class="mono" font-size="10" letter-spacing="1.2" '
        f'fill="{PALETTE["muted"]}">CURRENT STREAK</text>'
        f'<text x="660" y="103" class="serif" font-size="38" '
        f'fill="{PALETTE["blue"]}">{streak}</text>'
        f'<text x="713" y="102" font-size="13" fill="{PALETTE["ink_soft"]}">'
        f'{"day" if streak == 1 else "days"}</text>'
        '<text x="660" y="151" class="mono" font-size="10" letter-spacing="1.2" '
        f'fill="{PALETTE["muted"]}">ACTIVE DAYS / YEAR</text>'
        f'<text x="660" y="194" class="serif" font-size="34" '
        f'fill="{PALETTE["ink"]}">{active_days}</text>'
        '<text x="660" y="243" class="mono" font-size="10" letter-spacing="1.2" '
        f'fill="{PALETTE["muted"]}">BUSIEST DAY</text>'
        f'<text x="660" y="281" font-size="21" '
        f'fill="{PALETTE["ink"]}">{escape(busiest_day)}</text>'
        '<text x="40" y="329" class="mono" font-size="9" letter-spacing="1" '
        f'fill="{PALETTE["muted"]}">MONTHLY TOTALS</text>'
    )
    render_svg(
        "contributions.svg",
        880,
        350,
        content,
        3.8,
        "Monthly contributions, current streak, active days, and busiest day",
    )


def render_repositories() -> None:
    for index, (name, description, language, _) in enumerate(REPOSITORIES):
        content = (
            f'<rect x="4" y="4" width="432" height="172" rx="14" '
            f'fill="{PALETTE["paper"]}"/>'
            f'<rect x="4" y="4" width="6" height="172" rx="3" '
            f'fill="{PALETTE["blue"] if index % 2 == 0 else PALETTE["red"]}"/>'
            f'<text x="30" y="46" class="serif" font-size="25" '
            f'fill="{PALETTE["ink"]}">{escape(name)}</text>'
            f'<text x="30" y="79" font-size="13" fill="{PALETTE["ink_soft"]}">'
            f'{escape(description)}</text>'
            f'<line x1="30" y1="112" x2="410" y2="112" '
            f'stroke="{PALETTE["rule"]}"/>'
            f'<text x="30" y="148" class="mono" font-size="10" letter-spacing="1" '
            f'fill="{PALETTE["muted"]}">{escape(language.upper())}</text>'
            f'<path d="M398 137h12v12m0-12-14 14" fill="none" '
            f'stroke="{PALETTE["blue"]}" stroke-width="1.5"/>'
        )
        render_svg(
            f"repo_{index}.svg",
            440,
            180,
            content,
            6.4 + index * 0.08,
            f"Featured repository: {name}",
        )


def render_projects_title() -> None:
    content = (
        f'<rect width="880" height="96" rx="14" fill="{PALETTE["paper"]}"/>'
        '<text x="40" y="61" class="serif" font-size="39" '
        f'fill="{PALETTE["ink"]}">Selected work, <tspan font-style="italic" '
        f'fill="{PALETTE["blue"]}">in progress.</tspan></text>'
        '<text x="838" y="57" text-anchor="end" class="mono" font-size="10" '
        f'letter-spacing="1" fill="{PALETTE["muted"]}">FEATURED REPOSITORIES</text>'
    )
    render_svg(
        "projects_title.svg",
        880,
        96,
        content,
        6.0,
        "Selected work and featured repositories",
    )


def render_contribution_graph(counts: dict[date, int]) -> None:
    first_day = min(counts)
    last_day = max(counts)
    start_day = first_day - timedelta(days=(first_day.weekday() + 1) % 7)
    cell_size = 12
    cell_gap = 3
    step = cell_size + cell_gap
    grid_x = 42
    grid_y = 96
    colors = (
        PALETTE["paper_deep"],
        "#C8D3FF",
        "#94A8FF",
        "#6280FF",
        PALETTE["blue"],
        "#1A3BE0",
    )
    cells = []
    for index, (day, count) in enumerate(sorted(counts.items())):
        week = (day - start_day).days // 7
        weekday = (day.weekday() + 1) % 7
        if count == 0:
            level = 0
        elif count <= 2:
            level = 1
        elif count <= 5:
            level = 2
        elif count <= 10:
            level = 3
        elif count <= 20:
            level = 4
        else:
            level = 5
        x = grid_x + week * step
        y = grid_y + weekday * step
        cells.append(
            f'<rect class="fade" style="animation-delay:{2.2 + index * 0.003:.3f}s" '
            f'x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2" '
            f'fill="{colors[level]}"><title>{day.isoformat()}: '
            f'{count} contributions</title></rect>'
        )

    month_labels = []
    for month_cursor in month_sequence(first_day, last_day):
        week = (month_cursor - start_day).days // 7
        month_labels.append(
            f'<text x="{grid_x + week * step}" y="82" class="mono" '
            f'font-size="10" fill="{PALETTE["muted"]}">'
            f"{month_cursor.strftime('%b')}</text>"
        )

    weekdays = "".join(
        f'<text x="24" y="{grid_y + index * step + 9}" class="mono" '
        f'font-size="8" text-anchor="middle" fill="{PALETTE["muted"]}">{label}</text>'
        for index, label in ((1, "M"), (3, "W"), (5, "F"))
    )
    content = (
        f'<rect width="880" height="250" rx="14" fill="{PALETTE["paper"]}"/>'
        '<text x="40" y="47" class="serif" font-size="31" '
        f'fill="{PALETTE["ink"]}">Every day, in blue</text>'
        '<text x="838" y="45" text-anchor="end" class="mono" font-size="10" '
        f'letter-spacing="1.1" fill="{PALETTE["muted"]}">UPDATED DAILY</text>'
        f'{"".join(month_labels)}{weekdays}{"".join(cells)}'
        f'<text x="42" y="226" class="mono" font-size="9" letter-spacing=".6" '
        f'fill="{PALETTE["muted"]}">DAILY CONTRIBUTIONS / {sum(counts.values())} TOTAL</text>'
        f'<text x="744" y="226" text-anchor="end" class="mono" font-size="9" '
        f'fill="{PALETTE["muted"]}">LESS</text>'
        + "".join(
            f'<rect x="{762 + level * 10}" y="216" width="7" height="7" rx="1" '
            f'fill="{colors[level]}"/>'
            for level in range(6)
        )
        + f'<text x="833" y="226" class="mono" font-size="9" '
        f'fill="{PALETTE["muted"]}">MORE</text>'
    )
    render_svg(
        "contribution_graph.svg",
        880,
        250,
        content,
        2.3,
        "GitHub contributions over the past year",
    )


def main() -> None:
    counts = load_contributions()
    render_hero()
    render_contribution_graph(counts)
    render_contribution_chart(counts)
    render_tiles()
    render_commit_clock()
    render_projects_title()
    render_repositories()


if __name__ == "__main__":
    main()

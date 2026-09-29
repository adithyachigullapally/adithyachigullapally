"""Generate about.svg: typing terminal (left) + training neural net and loss curve (right)."""
import math, random, sys

W, H = 820, 428
CW = 9.6            # monospace advance at 16px; textLength forces every font to this grid
X0 = 28             # terminal left margin
PROMPT = "adithya@github:~$"
CMD_X = X0 + (len(PROMPT) + 1) * CW
BG = "#0d1117"
NEON = "#00ffa3"

def y(row):
    return 84 + row * 26

def prompt(row):
    return (f'<text class="t" x="{X0}" y="{y(row)}" textLength="{len(PROMPT) * CW:.1f}" lengthAdjust="spacing">'
            f'<tspan fill="{NEON}">adithya@github</tspan><tspan fill="#e6edf3">:</tspan>'
            f'<tspan fill="#58a6ff">~</tspan><tspan fill="#e6edf3">$</tspan></text>')

def command(row, cmd, show, type_start, type_dur):
    # one <text> per character, each popping in on its own delay: same CSS timeline as everything else
    step = type_dur / len(cmd)
    chars = "".join(
        f'<text class="t ch s" x="{CMD_X + k * CW:.1f}" y="{y(row)}" fill="#e6edf3" '
        f'style="animation-delay:{type_start + k * step:.2f}s">{c}</text>'
        for k, c in enumerate(cmd) if c != " ")
    return f'<g class="s" style="animation-delay:{show}s">{prompt(row)}</g>{chars}'

def output(row, text, show, cls="o", bullet=False):
    body = (f'<tspan fill="{NEON}">[+]</tspan> {text}' if bullet else text)
    n = len(text) + (4 if bullet else 0)
    return (f'<text class="t {cls} s" x="{X0}" y="{y(row)}" textLength="{n * CW:.1f}" lengthAdjust="spacing" '
            f'style="animation-delay:{show}s">{body}</text>')

cmds = [("whoami", 0.3, 0.5, 0.5), ("cat interests.txt", 1.8, 2.0, 1.0), ("cat hobby.txt", 3.9, 4.1, 0.8)]

left = [
    command(0, *cmds[0]),
    output(1, "Adithya Chigullapally", 1.2, cls="name"),
    output(2, "3rd year @ Shiv Nadar University", 1.35),
    command(4, *cmds[1]),
    output(5, "training models", 3.2, bullet=True),
    output(6, "machine learning", 3.35, bullet=True),
    output(7, "solving problems", 3.5, bullet=True),
    command(9, *cmds[2]),
    output(10, "cybersecurity", 5.1, bullet=True),
    f'<g class="s" style="animation-delay:5.5s">{prompt(12)}'
    f'<rect class="cur" x="{CMD_X:.1f}" y="{y(12) - 15}" width="{CW:.1f}" height="19" fill="{NEON}"/></g>',
]

# right panel: a small network doing forward passes
layers = [(490, [125, 165, 205]), (570, [105, 145, 185, 225]), (650, [105, 145, 185, 225]), (730, [145, 185])]
edges, nodes = [], []
for (xa, ya), (xb, yb) in zip(layers, layers[1:]):
    edges += [f'<line class="e" x1="{xa}" y1="{a}" x2="{xb}" y2="{b}"/>' for a in ya for b in yb]
for i, (x, ys) in enumerate(layers):
    nodes += [f'<circle class="n" cx="{x}" cy="{v}" r="7" style="animation-delay:{i * 0.3:.1f}s"/>' for v in ys]

# loss curve: decaying with a little deterministic noise
random.seed(7)
ox, oy, pw, ph = 480, 390, 300, 96
pts = []
for i in range(61):
    t = i / 60
    loss = math.exp(-3.2 * t) * 0.92 + 0.06 + (random.random() - 0.5) * 0.05 * (1 - t * 0.7)
    pts.append((ox + 4 + t * (pw - 8), oy - 4 - min(max(loss, 0.0), 1.0) * (ph - 8)))
curve = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts)
area = curve + f" L{pts[-1][0]:.1f},{oy} L{pts[0][0]:.1f},{oy} Z"
ex, ey = pts[-1]

right = f"""
<text class="lbl" x="480" y="{y(0)}"># model.train()</text>
<g>{''.join(edges)}</g>
<g>{''.join(nodes)}</g>
<path d="M{ox},{oy - ph} V{oy} H{ox + pw}" fill="none" stroke="#30363d" stroke-width="1.5"/>
<text class="lbl" x="{ox}" y="{oy - ph - 8}" fill="{NEON}">loss</text>
<text class="lbl" x="{ox + pw}" y="{oy + 18}" text-anchor="end">epochs</text>
<path class="area s" d="{area}" fill="url(#fade)" style="animation-delay:4.6s"/>
<path class="loss" d="{curve}" pathLength="1"/>
<g class="s" style="animation-delay:4.8s">
  <circle class="dot" cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{NEON}"/>
  <text class="lbl" x="{ex - 10:.1f}" y="{ey - 12:.1f}" text-anchor="end">converged ✓</text>
</g>"""

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title">
<title id="title">whoami: Adithya Chigullapally, 3rd year at Shiv Nadar University. Interests: training models, machine learning, solving problems. Hobby: cybersecurity.</title>
<style>
.t{{font:16px 'Fira Code','JetBrains Mono','Cascadia Code',Consolas,'DejaVu Sans Mono',Menlo,monospace;white-space:pre}}
.o{{fill:#8b949e}} .name{{fill:#ffffff;font-weight:700}}
.lbl{{font:12px 'Fira Code',Consolas,Menlo,monospace;fill:#8b949e}}
.s{{opacity:0;animation:show .25s ease forwards}}
@keyframes show{{to{{opacity:1}}}}
.ch{{animation-duration:.01s}}
.cur{{animation:blink 1s step-end infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.e{{stroke:{NEON};stroke-opacity:.28;stroke-width:1.2;stroke-dasharray:3 7;animation:flow 1s linear infinite}}
@keyframes flow{{from{{stroke-dashoffset:10}}to{{stroke-dashoffset:0}}}}
.n{{fill:{BG};stroke:{NEON};stroke-width:2;animation:fire 2.4s ease-in-out infinite}}
@keyframes fire{{0%,40%,100%{{fill:{BG}}}15%{{fill:{NEON}}}}}
.loss{{fill:none;stroke:{NEON};stroke-width:2.2;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;animation:draw 4s ease-out .8s forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.dot{{animation:pulse 1.6s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.3}}}}
</style>
<defs>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{NEON}" stop-opacity=".25"/><stop offset="1" stop-color="{NEON}" stop-opacity="0"/></linearGradient>
  <filter id="glow" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="4"/></filter>
</defs>
<rect x="6" y="6" width="{W - 12}" height="{H - 12}" rx="12" fill="none" stroke="{NEON}" stroke-opacity=".35" stroke-width="2" filter="url(#glow)"/>
<rect x="6" y="6" width="{W - 12}" height="{H - 12}" rx="12" fill="{BG}" stroke="{NEON}" stroke-opacity=".45"/>
<path d="M6,42 H{W - 6}" stroke="#30363d"/>
<circle cx="26" cy="24" r="6" fill="#ff5f56"/><circle cx="46" cy="24" r="6" fill="#ffbd2e"/><circle cx="66" cy="24" r="6" fill="#27c93f"/>
<text class="lbl" x="{W / 2}" y="28" text-anchor="middle">adithya@github: ~</text>
<path d="M440,58 V{H - 22}" stroke="#30363d" stroke-dasharray="2 4"/>
{''.join(left)}
{right}
</svg>
"""

out = sys.argv[1] if len(sys.argv) > 1 else "assets/about.svg"  # run from the repo root
open(out, "w", encoding="utf-8").write(svg)
print("wrote", out, len(svg), "bytes")

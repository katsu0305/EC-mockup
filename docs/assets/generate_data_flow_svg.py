"""
docs/データフロー図（data-flow.svg）を生成するスクリプト。

アイコンは docs/assets/icons/ に配置した SVG（GitHub / Python / Google Chrome は
simple-icons、その他は Material Design Icons）のパスデータを読み込み、
1枚の自己完結した SVG として出力する。

使い方:
    python docs/assets/generate_data_flow_svg.py

README.md の mermaid フローチャートを変更した場合は、このスクリプト内の
ノード定義・矢印定義も合わせて更新して再実行すること。
"""
import re, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(BASE_DIR, "icons")
OUT_PATH = os.path.join(BASE_DIR, "data-flow.svg")

def load_icon(fname):
    with open(os.path.join(ICON_DIR, fname), encoding="utf-8") as f:
        content = f.read()
    vb_m = re.search(r'viewBox="([^"]+)"', content)
    viewbox = vb_m.group(1) if vb_m else "0 0 24 24"
    paths = re.findall(r'<path\s+d="([^"]+)"', content)
    return viewbox, paths

ICON_FILES = {
    "github": "github.svg",
    "python": "python.svg",
    "chrome": "googlechrome.svg",
    "database": "mdi-database.svg",
    "cloud-download": "mdi-cloud-download.svg",
    "web": "mdi-web.svg",
    "cog": "mdi-cog-outline.svg",
    "api": "mdi-api.svg",
    "console": "mdi-console.svg",
    "server": "mdi-server.svg",
    "folder": "mdi-folder-outline.svg",
    "file-doc": "mdi-file-document-outline.svg",
    "folder-images": "mdi-folder-multiple-image.svg",
    "camera": "mdi-camera-outline.svg",
    "compare": "mdi-compare.svg",
    "auto-fix": "mdi-auto-fix.svg",
    "hammer-wrench": "mdi-hammer-wrench.svg",
    "package": "mdi-package-variant-closed.svg",
}

ICONS = {k: load_icon(v) for k, v in ICON_FILES.items()}

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def icon_symbol(icon_id, key):
    viewbox, paths = ICONS[key]
    inner = "".join(f'<path d="{p}"/>' for p in paths)
    return f'<symbol id="{icon_id}" viewBox="{viewbox}">{inner}</symbol>'

# ---------- layout constants ----------
CANVAS_W = 1640

CARD_W4, CARD_H = 260, 84
GAP4 = 36
LEFT = 70
COL4_X = [LEFT + i * (CARD_W4 + GAP4) for i in range(4)]
RIGHT_EDGE = COL4_X[3] + CARD_W4

CARD_W3, GAP3 = 300, 124
COL3_X = [LEFT + i * (CARD_W3 + GAP3) for i in range(3)]

Y_INPUT = 40
Y_IN = 222
Y_WK = 344
Y_BUILD = 470
Y_OUTPUT = 614

PGM_TOP = 160
PGM_BOTTOM = Y_BUILD + CARD_H + 18

S_X, S_Y, S_W, S_H = 1300, Y_IN - 20, 260, (Y_OUTPUT + CARD_H) - (Y_IN - 20)

ACCENT = {
    "input": ("#2F6FED", "#EAF2FF"),
    "in":    ("#1E9E55", "#EAF9EF"),
    "wk":    ("#D98A11", "#FFF6E6"),
    "build": ("#8A3FE0", "#F5EEFF"),
    "output":("#E0631E", "#FFF1E6"),
    "ctrl":  ("#4C5FD6", "#EEF0FF"),
}

def rrect(x, y, w, h, r, fill, stroke=None, sw=1.5, extra="", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ry="{r}" fill="{fill}"{s}{d} {extra}/>'

def arrow_marker_defs():
    return '''
<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
  <path d="M0,0 L10,5 L0,10 z" fill="#55606e"/>
</marker>
<marker id="arrow-ctrl" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
  <path d="M0,0 L10,5 L0,10 z" fill="#4C5FD6"/>
</marker>
'''

def straight_arrow(x1, y1, x2, y2, color="#55606e", dash=None, marker="arrow", sw=2):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d} marker-end="url(#{marker})"/>'

def elbow_h_then_v(x1, y1, x2, y2, color, dash=None, marker="arrow-ctrl", sw=1.8):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    path = f"M{x1},{y1} L{x2},{y1} L{x2},{y2}"
    return f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{sw}"{d} marker-end="url(#{marker})"/>'

card_id = 0
def node_card(x, y, w, h, badge, title, sub, icon_key, band, title_size=15.5):
    global card_id
    card_id += 1
    accent, light = ACCENT[band]
    icon_id = f"ic{card_id}"
    parts = [icon_symbol(icon_id, icon_key)]
    parts.append(rrect(x, y, w, h, 14, accent))
    parts.append(rrect(x, y + 5, w, h - 5, 14, "#ffffff", stroke="#dfe3ea", sw=1.3,
                        extra='filter="url(#shadow)"'))
    icx, icy = x + 36, y + h / 2 + 3
    parts.append(f'<circle cx="{icx}" cy="{icy}" r="21" fill="{light}"/>')
    parts.append(f'<use href="#{icon_id}" x="{icx-12}" y="{icy-12}" width="24" height="24" fill="{accent}"/>')
    parts.append(f'<circle cx="{x+w-16}" cy="{y+20}" r="11" fill="{light}" stroke="{accent}" stroke-width="1"/>')
    parts.append(f'<text x="{x+w-16}" y="{y+24}" font-size="11" font-weight="700" text-anchor="middle" fill="{accent}" font-family="Segoe UI, sans-serif">{badge}</text>')
    tx = icx + 33
    if sub:
        parts.append(f'<text x="{tx}" y="{icy-4}" font-size="{title_size}" font-weight="700" fill="#1c2430" font-family="Segoe UI, sans-serif">{esc(title)}</text>')
        parts.append(f'<text x="{tx}" y="{icy+16}" font-size="11.5" fill="#66707d" font-family="Segoe UI, sans-serif">{esc(sub)}</text>')
    else:
        parts.append(f'<text x="{tx}" y="{icy+5}" font-size="{title_size}" font-weight="700" fill="#1c2430" font-family="Segoe UI, sans-serif">{esc(title)}</text>')
    return "".join(parts), (x, y, w, h)

def band_label(x, y, text, band):
    accent, light = ACCENT[band]
    w = 15 + len(text) * 8.6
    parts = [rrect(x, y, w, 24, 12, light, stroke=accent, sw=1.2)]
    parts.append(f'<text x="{x+w/2}" y="{y+16.5}" font-size="12.5" font-weight="700" fill="{accent}" text-anchor="middle" font-family="Segoe UI, sans-serif">{esc(text)}</text>')
    return "".join(parts)

nodes = {}
body = []

TITLE_Y = 40
SHIFT = 60  # vertical offset applied to all band/node content, leaves room for the title above
def sy(y): return y + SHIFT

body.append(f'<text x="{CANVAS_W/2}" y="{TITLE_Y}" font-size="21" font-weight="800" fill="#1c2430" text-anchor="middle" font-family="Segoe UI, sans-serif">EC Mockup &#8211; データフロー</text>')

# ---- INPUT band ----
body.append(rrect(LEFT-24, sy(Y_INPUT-30), RIGHT_EDGE-LEFT+48, CARD_H+58, 18, ACCENT["input"][1], stroke=ACCENT["input"][0], sw=1.4, dash="6,5"))
body.append(band_label(LEFT-14, sy(Y_INPUT-24), "入力", "input"))
input_defs = [
    ("A", "GitHub リポジトリ", "テンプレート HTML/CSS/JS", "github"),
    ("C", "EC-database-tang", "商品データ API", "database"),
    ("E", "MakeShop", "公開URL/FTP 画像・運用画像", "cloud-download"),
    ("G", "実ショップサイト", "HTML/CSS/JS 参照", "web"),
]
for i, (badge, title, sub, icon) in enumerate(input_defs):
    svg, box = node_card(COL4_X[i], sy(Y_INPUT), CARD_W4, CARD_H, badge, title, sub, icon, "input")
    body.append(svg); nodes[badge] = box

# ---- PGM outer container ----
body.append(rrect(LEFT-24, sy(PGM_TOP), RIGHT_EDGE-LEFT+48, PGM_BOTTOM-PGM_TOP, 20, "#F4FBF6", stroke="#bfe6cc", sw=1.6))
py_icon_id = "ic_py"
body.append(icon_symbol(py_icon_id, "python"))
body.append(f'<use href="#{py_icon_id}" x="{LEFT-6}" y="{sy(PGM_TOP)+12}" width="20" height="20" fill="#2E7D46"/>')
body.append(f'<text x="{LEFT+20}" y="{sy(PGM_TOP)+27}" font-size="14.5" font-weight="800" fill="#1c2430" font-family="Segoe UI, sans-serif">PGM: Python プログラム</text>')

# IN band
body.append(band_label(LEFT-14, sy(Y_IN-24), "入力取得", "in"))
in_defs = [
    ("B", "Source Fetcher", None, "cog"),
    ("D", "Data Exporter", None, "api"),
    ("F", "Image Fetcher", None, "cloud-download"),
    ("H", "Live Site Inspector", None, "console"),
]
for i, (badge, title, sub, icon) in enumerate(in_defs):
    svg, box = node_card(COL4_X[i], sy(Y_IN), CARD_W4, CARD_H, badge, title, sub, icon, "in", title_size=14)
    body.append(svg); nodes[badge] = box

# WK band
body.append(band_label(LEFT-14, sy(Y_WK-24), "作業データ生成", "wk"))
wk_defs = [
    ("I", "work/source", "作業ディレクトリ", "folder"),
    ("J", "work/data", "中間データ", "file-doc"),
    ("K", "work/images", "ローカル画像", "folder-images"),
    ("L", "work/live-site", "比較用スナップショット", "camera"),
]
for i, (badge, title, sub, icon) in enumerate(wk_defs):
    svg, box = node_card(COL4_X[i], sy(Y_WK), CARD_W4, CARD_H, badge, title, sub, icon, "wk", title_size=14)
    body.append(svg); nodes[badge] = box

# BUILD band (3 cols)
body.append(band_label(LEFT-14, sy(Y_BUILD-24), "モック生成", "build"))
build_defs = [
    ("M", "Normalizer", "データ正規化", "auto-fix"),
    ("N", "Static Builder", "静的サイト生成", "hammer-wrench"),
    ("O", "差分確認", "比較チェック", "compare"),
]
for i, (badge, title, sub, icon) in enumerate(build_defs):
    svg, box = node_card(COL3_X[i], sy(Y_BUILD), CARD_W3, CARD_H, badge, title, sub, icon, "build", title_size=14.5)
    body.append(svg); nodes[badge] = box

# ---- OUTPUT band ----
body.append(rrect(LEFT-24, sy(Y_OUTPUT-30), RIGHT_EDGE-LEFT+48, CARD_H+58, 18, ACCENT["output"][1], stroke=ACCENT["output"][0], sw=1.4, dash="6,5"))
body.append(band_label(LEFT-14, sy(Y_OUTPUT-24), "出力", "output"))
output_defs = [
    ("P", "output/mock-site", "生成物", "package"),
    ("Q", "Preview Server", "ローカル配信", "server"),
    ("R", "ブラウザ確認", "動作確認", "chrome"),
]
for i, (badge, title, sub, icon) in enumerate(output_defs):
    svg, box = node_card(COL3_X[i], sy(Y_OUTPUT), CARD_W3, CARD_H, badge, title, sub, icon, "output", title_size=14.5)
    body.append(svg); nodes[badge] = box

# ---- S node (CLI/GUI control tower) ----
s_x, s_y, s_w, s_h = S_X, sy(S_Y), S_W, S_H
body.append(rrect(s_x, s_y, s_w, s_h, 20, "#232A3B", extra='filter="url(#shadow)"'))
s_icon_id = "ic_s"
body.append(icon_symbol(s_icon_id, "console"))
body.append(f'<circle cx="{s_x+s_w/2}" cy="{s_y+54}" r="26" fill="#323B52"/>')
body.append(f'<use href="#{s_icon_id}" x="{s_x+s_w/2-15}" y="{s_y+39}" width="30" height="30" fill="#8FA6FF"/>')
body.append(f'<text x="{s_x+s_w/2}" y="{s_y+104}" font-size="17" font-weight="800" fill="#ffffff" text-anchor="middle" font-family="Segoe UI, sans-serif">CLI / GUI</text>')
body.append(f'<text x="{s_x+s_w/2}" y="{s_y+124}" font-size="11.5" fill="#a9b4cc" text-anchor="middle" font-family="Segoe UI, sans-serif">操作エントリポイント (S)</text>')
body.append(f'<line x1="{s_x+28}" y1="{s_y+148}" x2="{s_x+s_w-28}" y2="{s_y+148}" stroke="#3c4560" stroke-width="1"/>')
body.append(f'<text x="{s_x+s_w/2}" y="{s_y+170}" font-size="11" fill="#a9b4cc" text-anchor="middle" font-family="Segoe UI, sans-serif">各処理を起動・監視</text>')
nodes["S"] = (s_x, s_y, s_w, s_h)

# ================= arrows =================
arrows = []

def top_center(node, dx=0):
    x, y, w, h = nodes[node]
    return x + w / 2 + dx, y

def bottom_center(node, dx=0):
    x, y, w, h = nodes[node]
    return x + w / 2 + dx, y + h

def left_mid(node, dy=0):
    x, y, w, h = nodes[node]
    return x, y + h / 2 + dy

def right_mid(node, dy=0):
    x, y, w, h = nodes[node]
    return x + w, y + h / 2 + dy

for a, b in [("A", "B"), ("C", "D"), ("E", "F"), ("G", "H")]:
    x1, y1 = bottom_center(a, dx=-24); x2, y2 = top_center(b, dx=-24)
    arrows.append(straight_arrow(x1, y1, x2, y2))

for a, b in [("B", "I"), ("D", "J"), ("F", "K"), ("H", "L")]:
    x1, y1 = bottom_center(a, dx=-24); x2, y2 = top_center(b, dx=-24)
    arrows.append(straight_arrow(x1, y1, x2, y2))

mx, my = top_center("M")
for src in ["I", "J", "K"]:
    x1, y1 = bottom_center(src, dx=-24)
    arrows.append(f'<path d="M{x1},{y1} C{x1},{y1+26} {mx},{my-26} {mx},{my}" fill="none" stroke="#55606e" stroke-width="2" marker-end="url(#arrow)"/>')

lx, ly = bottom_center("L", dx=-24)
ox, oy = top_center("O", dx=40)
arrows.append(f'<path d="M{lx},{ly} C{lx},{ly+40} {ox},{oy-40} {ox},{oy}" fill="none" stroke="#55606e" stroke-width="2" marker-end="url(#arrow)"/>')

x1, y1 = right_mid("M"); x2, y2 = left_mid("N")
arrows.append(straight_arrow(x1, y1, x2, y2))
x1, y1 = right_mid("N"); x2, y2 = left_mid("O")
arrows.append(straight_arrow(x1, y1, x2, y2))

x1, y1 = bottom_center("N"); x2, y2 = top_center("P")
arrows.append(straight_arrow(x1, y1, x2, y2))

x1, y1 = right_mid("P"); x2, y2 = left_mid("Q")
arrows.append(straight_arrow(x1, y1, x2, y2))
x1, y1 = right_mid("Q"); x2, y2 = left_mid("R")
arrows.append(straight_arrow(x1, y1, x2, y2))

# ---- S control arrows ----
sx = nodes["S"][0]
gap_y_row1 = sy(Y_IN) - 18
gap_y_n = sy(Y_BUILD) - 18
gap_y_q = sy(Y_OUTPUT) - 18

for t in ["B", "D", "F", "H"]:
    tx, ty = top_center(t, dx=30)
    arrows.append(elbow_h_then_v(sx, gap_y_row1, tx, ty, "#4C5FD6", dash="5,4"))

for t, gy in [("N", gap_y_n), ("Q", gap_y_q)]:
    tx = nodes[t][0] + nodes[t][2] - 26
    ty = nodes[t][1]
    arrows.append(elbow_h_then_v(sx, gy, tx, ty, "#4C5FD6", dash="5,4"))

# ---- legend ----
# Give the legend clear air both above (from the OUTPUT container's bottom edge)
# and below (before the canvas ends), instead of hugging either edge.
output_container_bottom = sy(Y_OUTPUT - 30) + (CARD_H + 58)
GAP_ABOVE_LEGEND = 44
GAP_BELOW_LEGEND = 34

leg_x, leg_y = LEFT - 24, output_container_bottom + GAP_ABOVE_LEGEND
body.append(f'<line x1="{leg_x}" y1="{leg_y}" x2="{leg_x+46}" y2="{leg_y}" stroke="#55606e" stroke-width="2" marker-end="url(#arrow)"/>')
body.append(f'<text x="{leg_x+56}" y="{leg_y+4}" font-size="12" fill="#4a5361" font-family="Segoe UI, sans-serif">データフロー</text>')
leg_x2 = leg_x + 190
body.append(f'<line x1="{leg_x2}" y1="{leg_y}" x2="{leg_x2+46}" y2="{leg_y}" stroke="#4C5FD6" stroke-width="1.8" stroke-dasharray="5,4" marker-end="url(#arrow-ctrl)"/>')
body.append(f'<text x="{leg_x2+56}" y="{leg_y+4}" font-size="12" fill="#4a5361" font-family="Segoe UI, sans-serif">CLI / GUI からの起動・制御</text>')

TOTAL_H = leg_y + GAP_BELOW_LEGEND

# background goes underneath everything, sized to the actual content height
body.insert(0, rrect(0, 0, CANVAS_W, TOTAL_H, 0, "#fbfcfe"))

# ================= assemble =================
defs = f'''<defs>
<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
  <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#1c2430" flood-opacity="0.12"/>
</filter>
{arrow_marker_defs()}
</defs>'''

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {TOTAL_H}" width="{CANVAS_W}" height="{TOTAL_H}" font-family="Segoe UI, sans-serif">
{defs}
{''.join(body)}
{''.join(arrows)}
</svg>'''

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(svg)

print("written", OUT_PATH, len(svg), "bytes")

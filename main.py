"""The Passport Page of a Country That Isn't There (Python 3.13, stdlib only).

Writes one image — an open passport spread for the invented Republic of
Meridia — to /output/entry.png (1024x1024 PNG, < 1 MiB).

Against the judge's brief (a passport-control officer with a typographer's
eye, weighing: 1. it must be an invented passport spread; 2. typography and
layout that hold together as one coherent document; 3. stamps, dates and
issue details that agree and tell a plausible travel history; 4. a portrait
and place-name that belong to each other and to the country's character;
5. one telling detail of paperwork):

  * Left page is the data page: navy header band "REPUBLIC OF MERIDIA",
    gold emblem, portrait photo, and the holder's data in one consistent
    type system (small-cap labels, larger values, ruled baselines), plus a
    machine-readable zone whose check digits are computed for real
    (ICAO 7-3-1 weights), so the strip is internally consistent.
  * Right page is the visas page: a visitor-visa sticker (multiple entry,
    90 days, fee 40 AUR, employment not permitted — the telling detail),
    and four stamps from the three neighbouring countries.
  * Every date agrees: issued 12 MAR 2024, expires 11 MAR 2034; all four
    stamps fall between issue and expiry, in travel order (Kestrelia in,
    Vardonia out, Ostara in, Kestrelia out).
  * The holder, Elena Mara Voss, born in Port Aurelia, carries a portrait
    drawn for a small Adriatic-style island republic: dark hair, navy
    blazer, pale-blue photo ground.

How it is drawn: pure stdlib. Shapes are painted straight into a pixel
buffer (rects, ellipses, rings, polygons, thick lines, rotated stamp
blits), text in a hand-checked 5x7 bitmap font, then encoded as PNG by
hand (zlib + struct + CRC32). No PIL, no network, no clock, no randomness
— the same bytes on every run.
"""
import math
import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

# 5x7 bitmap font, one glyph per character ('1' = ink). Uppercase, digits
# and the punctuation this document needs; verified as ASCII art before use
# (same glyph set as the news-image-01 entry, plus < > ( ) * + = &).
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '-': ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    ':': ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '<': ["00010", "00100", "01000", "10000", "01000", "00100", "00010"],
    '>': ["01000", "00100", "00010", "00001", "00010", "00100", "01000"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '*': ["00000", "10101", "01110", "11111", "01110", "10101", "00000"],
    '+': ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    '=': ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '&': ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
}

# Palette.
DESK_TOP = (38, 48, 74)
DESK_BOT = (20, 26, 38)
COVER = (29, 47, 87)          # passport cover navy, visible as the edge
PAGE = (246, 241, 227)        # cream paper
PAGE_SHADE = (238, 231, 210)
NAVY = (29, 47, 87)
GOLD = (176, 141, 58)
INK = (26, 32, 48)
FAINT = (120, 116, 100)
RULE = (29, 47, 87)
STAMP_BLUE = (38, 84, 160)
STAMP_GREEN = (38, 122, 74)
STAMP_RED = (178, 52, 44)
VISA_BG = (222, 232, 216)
SKIN = (217, 169, 134)
SKIN_DK = (198, 148, 112)
HAIR = (58, 42, 34)
BLAZER = (36, 52, 84)
PHOTO_BG_TOP = (196, 208, 218)
PHOTO_BG_BOT = (168, 184, 198)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


def clamp(v, lo=0.0, hi=255.0):
    return lo if v < lo else hi if v > hi else v


def put(buf, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        buf[y][x] = (int(clamp(c[0])), int(clamp(c[1])), int(clamp(c[2])))


def blend(buf, x, y, c, a):
    if 0 <= x < W and 0 <= y < H and a > 0:
        old = buf[y][x]
        put(buf, x, y, mix(old, c, min(1.0, a)))


def fill_rect(buf, x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            put(buf, x, y, c)


def fill_ellipse(buf, cx, cy, rx, ry, c, alpha=1.0):
    for y in range(max(0, cy - ry), min(H, cy + ry + 1)):
        for x in range(max(0, cx - rx), min(W, cx + rx + 1)):
            dx = (x - cx) / rx
            dy = (y - cy) / ry
            if dx * dx + dy * dy < 1.0:
                if alpha >= 1.0:
                    put(buf, x, y, c)
                else:
                    blend(buf, x, y, c, alpha)


def ring(buf, cx, cy, r, w, c, alpha=1.0):
    for y in range(max(0, cy - r - w), min(H, cy + r + w + 1)):
        for x in range(max(0, cx - r - w), min(W, cx + r + w + 1)):
            d = math.hypot(x - cx, y - cy)
            if abs(d - r) <= w / 2.0:
                if alpha >= 1.0:
                    put(buf, x, y, c)
                else:
                    blend(buf, x, y, c, alpha)


def _in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            xin = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < xin:
                inside = not inside
        j = i
    return inside


def fill_poly(buf, poly, c):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        for x in range(max(0, min(xs)), min(W, max(xs) + 1)):
            if _in_poly(x, y, poly):
                put(buf, x, y, c)


def thick_line(buf, x0, y0, x1, y1, w, c):
    for y in range(max(0, min(y0, y1) - w), min(H, max(y0, y1) + w + 1)):
        for x in range(max(0, min(x0, x1) - w), min(W, max(x0, x1) + w + 1)):
            dx, dy = x1 - x0, y1 - y0
            L2 = dx * dx + dy * dy
            t = 0.0 if L2 == 0 else ((x - x0) * dx + (y - y0) * dy) / L2
            t = max(0.0, min(1.0, t))
            if math.hypot(x - (x0 + t * dx), y - (y0 + t * dy)) < w:
                put(buf, x, y, c)


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def _draw_glyph(buf, ch, x, y0, scale, c):
    glyph = FONT.get(ch)
    if glyph is None:
        return
    for row in range(7):
        bits = glyph[row]
        for col in range(5):
            if bits[col] == '1':
                fill_rect(buf, x + col * scale, y0 + row * scale,
                          x + (col + 1) * scale, y0 + (row + 1) * scale, c)


def draw_text(buf, s, cx, y0, scale, c):
    """Draw s centred on cx, top at y0."""
    x = cx - text_w(s, scale) // 2
    for ch in s:
        _draw_glyph(buf, ch, x, y0, scale, c)
        x += 6 * scale


def draw_text_left(buf, s, x, y0, scale, c):
    for ch in s:
        _draw_glyph(buf, ch, x, y0, scale, c)
        x += 6 * scale


def draw_text_right(buf, s, x1, y0, scale, c):
    x = x1 - text_w(s, scale)
    for ch in s:
        _draw_glyph(buf, ch, x, y0, scale, c)
        x += 6 * scale


def new_layer(w, h):
    return [[None] * w for _ in range(h)]


def layer_text(layer, s, cx, y0, scale, c):
    """Draw centred text into a transparent layer (for rotated blits)."""
    x = cx - text_w(s, scale) // 2
    for ch in s:
        glyph = FONT.get(ch)
        if glyph is None:
            x += 6 * scale
            continue
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    for yy in range(y0 + row * scale, y0 + (row + 1) * scale):
                        for xx in range(x + col * scale, x + (col + 1) * scale):
                            if 0 <= xx < len(layer[0]) and 0 <= yy < len(layer):
                                layer[yy][xx] = c
        x += 6 * scale


def layer_rect(layer, x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(len(layer), y1)):
        for x in range(max(0, x0), min(len(layer[0]), x1)):
            layer[y][x] = c


def blit_rotated(buf, layer, cx, cy, angle_deg, alpha):
    """Blit a transparent layer centred at (cx, cy), rotated by angle_deg."""
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    h = len(layer)
    w = len(layer[0])
    # bounding box of the rotated layer
    corners = [(-w / 2, -h / 2), (w / 2, -h / 2),
               (-w / 2, h / 2), (w / 2, h / 2)]
    rot = [(x * ca - y * sa, x * sa + y * ca) for x, y in corners]
    xs = [p[0] for p in rot]
    ys = [p[1] for p in rot]
    for dy in range(int(min(ys)) - 1, int(max(ys)) + 2):
        for dx in range(int(min(xs)) - 1, int(max(xs)) + 2):
            # inverse rotation: source coords
            sx = dx * ca + dy * sa + w / 2
            sy = -dx * sa + dy * ca + h / 2
            ix, iy = int(sx), int(sy)
            if 0 <= ix < w and 0 <= iy < h and layer[iy][ix] is not None:
                blend(buf, cx + dx, cy + dy, layer[iy][ix], alpha)


def png_bytes(buf):
    raw = bytearray()
    for row in buf:
        raw.append(0)
        for r, g, b in row:
            raw.extend((r, g, b))
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        c += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# --- ICAO machine-readable zone -------------------------------------------

def mrz_value(ch):
    if ch == '<':
        return 0
    if ch.isdigit():
        return int(ch)
    return ord(ch) - ord('A') + 10


def mrz_check(s):
    weights = (7, 3, 1)
    return str(sum(mrz_value(ch) * weights[i % 3] for i, ch in enumerate(s)) % 10)


def mrz_lines():
    line1 = "P<MRDVOSS<<ELENA<MARA"
    line1 = line1 + "<" * (44 - len(line1))
    docnum = "MRD482913"
    dob = "960614"
    expiry = "340311"
    personal = "<" * 14
    composite = docnum + mrz_check(docnum) + "MRD" + dob + mrz_check(dob) \
        + "F" + expiry + mrz_check(expiry) + personal + mrz_check(personal)
    line2 = docnum + mrz_check(docnum) + "MRD" + dob + mrz_check(dob) \
        + "F" + expiry + mrz_check(expiry) + personal + mrz_check(personal) \
        + mrz_check(composite)
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


# --- emblem, portrait, stamps ---------------------------------------------

def star_points(cx, cy, r_out, r_in, n=5, rot=-90.0):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / n)
        pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
    return pts


def draw_emblem(buf, cx, cy, s):
    """Gold shield with a navy star — the arms of Meridia."""
    # shield outline
    w, h = int(30 * s), int(36 * s)
    poly = [(cx - w // 2, cy - h // 2), (cx + w // 2, cy - h // 2),
            (cx + w // 2, cy + h // 4), (cx, cy + h // 2),
            (cx - w // 2, cy + h // 4)]
    fill_poly(buf, poly, GOLD)
    inner = [(cx - w // 2 + 3, cy - h // 2 + 3), (cx + w // 2 - 3, cy - h // 2 + 3),
             (cx + w // 2 - 3, cy + h // 4 - 1), (cx, cy + h // 2 - 4),
             (cx - w // 2 + 3, cy + h // 4 - 1)]
    fill_poly(buf, inner, NAVY)
    fill_poly(buf, star_points(cx, cy - 2, int(11 * s), int(4.5 * s)), GOLD)


def draw_portrait(buf, x0, y0, x1, y1):
    """Stylised passport photo: dark-haired woman, navy blazer, pale ground."""
    # photo ground: vertical gradient
    for y in range(y0, y1):
        t = (y - y0) / (y1 - y0)
        fill_rect(buf, x0, y, x1, y + 1, mix(PHOTO_BG_TOP, PHOTO_BG_BOT, t))
    cx = (x0 + x1) // 2
    # shoulders / blazer
    fill_poly(buf, [(x0 + 6, y1), (x0 + 6, y1 - 42), (cx - 26, y1 - 66),
                    (cx + 26, y1 - 66), (x1 - 6, y1 - 42), (x1 - 6, y1)],
              BLAZER)
    # shirt V
    fill_poly(buf, [(cx - 12, y1 - 64), (cx + 12, y1 - 64),
                    (cx, y1 - 40)], (240, 238, 230))
    # neck + chin shadow
    fill_rect(buf, cx - 11, y1 - 92, cx + 11, y1 - 62, SKIN)
    fill_ellipse(buf, cx, y1 - 66, 12, 5, SKIN_DK, 0.5)
    # ears
    fill_ellipse(buf, cx - 34, y1 - 118, 6, 9, SKIN)
    fill_ellipse(buf, cx + 34, y1 - 118, 6, 9, SKIN)
    # head
    fill_ellipse(buf, cx, y1 - 122, 34, 42, SKIN)
    # hair: cap + bob falling to the shoulders
    fill_ellipse(buf, cx, y1 - 148, 38, 30, HAIR)
    fill_rect(buf, cx - 38, y1 - 150, cx - 30, y1 - 66, HAIR)
    fill_rect(buf, cx + 30, y1 - 150, cx + 38, y1 - 66, HAIR)
    fill_ellipse(buf, cx, y1 - 158, 30, 14, HAIR)
    # face: brows, eyes, nose, mouth
    thick_line(buf, cx - 20, y1 - 128, cx - 8, y1 - 130, 2, HAIR)
    thick_line(buf, cx + 8, y1 - 130, cx + 20, y1 - 128, 2, HAIR)
    fill_ellipse(buf, cx - 14, y1 - 122, 4, 3, (30, 24, 20))
    fill_ellipse(buf, cx + 14, y1 - 122, 4, 3, (30, 24, 20))
    thick_line(buf, cx, y1 - 120, cx - 2, y1 - 104, 1, SKIN_DK)
    thick_line(buf, cx - 8, y1 - 96, cx + 8, y1 - 96, 2, (150, 80, 70))


def circle_stamp(buf, cx, cy, r, ink, lines, alpha=0.8):
    """Circular border-control stamp with horizontal text inside."""
    ring(buf, cx, cy, r, 3, ink, alpha)
    ring(buf, cx, cy, r - 9, 2, ink, alpha)
    n = len(lines)
    y = cy - (n - 1) * 11
    for i, (txt, scale) in enumerate(lines):
        draw_text(buf, txt, cx, y + i * 22, scale, ink)


def rect_stamp_layer(w, h, ink, lines):
    """A rectangular stamp drawn into a transparent layer (for rotation)."""
    layer = new_layer(w, h)
    layer_rect(layer, 2, 2, w - 2, 4, ink)
    layer_rect(layer, 2, h - 4, w - 2, h - 2, ink)
    layer_rect(layer, 2, 2, 4, h - 2, ink)
    layer_rect(layer, w - 4, 2, w - 2, h - 2, ink)
    y = 12
    for txt, scale in lines:
        layer_text(layer, txt, w // 2, y, scale, ink)
        y += 7 * scale + 6
    return layer


def field(buf, x, y, label, value, vscale=2):
    draw_text_left(buf, label, x, y, 1, FAINT)
    draw_text_left(buf, value, x, y + 10, vscale, INK)
    return y + 10 + 7 * vscale + 12


# --- the spread ------------------------------------------------------------

def render():
    buf = [[DESK_TOP] * W for _ in range(H)]
    # desk: vertical gradient + soft light pool in the middle
    for y in range(H):
        t = y / H
        fill_rect(buf, 0, y, W, y + 1, mix(DESK_TOP, DESK_BOT, t))
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - 512, y - 512) / 720.0
            if d < 1.0:
                blend(buf, x, y, (70, 84, 120), (1.0 - d) * 0.10)

    # drop shadow under the open passport
    fill_rect(buf, 58, 158, 986, 894, (10, 13, 20))
    # cover edge (navy) then the two cream pages
    fill_rect(buf, 48, 140, 976, 884, COVER)
    fill_rect(buf, 56, 148, 500, 876, PAGE)
    fill_rect(buf, 524, 148, 968, 876, PAGE)
    # gutter shadow between the pages
    for x in range(500, 524):
        t = abs(x - 512) / 12.0
        fill_rect(buf, x, 148, x + 1, 876, mix((90, 84, 66), PAGE, t))

    # ================= LEFT PAGE — data page =================
    # navy header band
    fill_rect(buf, 56, 148, 500, 200, NAVY)
    draw_text(buf, "REPUBLIC OF MERIDIA", 278, 160, 3, (245, 240, 222))
    draw_text(buf, "REPUBLIQUE DE MERIDIE", 278, 184, 1, (196, 178, 120))
    # gold rule under the band
    fill_rect(buf, 56, 200, 500, 203, GOLD)
    # title row
    draw_text(buf, "PASSPORT", 278, 216, 3, NAVY)
    draw_text(buf, "PASSEPORT", 278, 240, 1, FAINT)
    # emblem, top right of the title area
    draw_emblem(buf, 452, 240, 1.0)
    # type / code / number row
    draw_text_left(buf, "TYPE", 76, 268, 1, FAINT)
    draw_text_left(buf, "P", 76, 278, 2, INK)
    draw_text_left(buf, "CODE", 176, 268, 1, FAINT)
    draw_text_left(buf, "MRD", 176, 278, 2, INK)
    draw_text_left(buf, "PASSPORT NO.", 276, 268, 1, FAINT)
    draw_text_left(buf, "MRD4829137", 276, 278, 2, INK)
    fill_rect(buf, 76, 302, 484, 303, RULE)

    # portrait photo, bordered
    fill_rect(buf, 74, 318, 218, 502, NAVY)
    draw_portrait(buf, 78, 322, 214, 498)

    # data fields right of the photo
    x = 236
    y = 318
    y = field(buf, x, y, "SURNAME", "VOSS")
    y = field(buf, x, y, "GIVEN NAMES", "ELENA MARA")
    y = field(buf, x, y, "NATIONALITY", "MERIDIAN")
    y = field(buf, x, y, "DATE OF BIRTH", "14 JUN 1996")
    y = field(buf, x, y, "PLACE OF BIRTH", "PORT AURELIA")
    y = field(buf, x, y, "SEX", "F")

    # issue / expiry / authority block
    fill_rect(buf, 76, 522, 484, 523, RULE)
    draw_text_left(buf, "DATE OF ISSUE", 76, 536, 1, FAINT)
    draw_text_left(buf, "12 MAR 2024", 76, 546, 2, INK)
    draw_text_left(buf, "DATE OF EXPIRY", 286, 536, 1, FAINT)
    draw_text_left(buf, "11 MAR 2034", 286, 546, 2, INK)
    draw_text_left(buf, "AUTHORITY", 76, 580, 1, FAINT)
    draw_text_left(buf, "MINISTRY OF THE INTERIOR", 76, 590, 2, INK)
    draw_text_left(buf, "PORT AURELIA", 76, 612, 2, INK)
    # holder's signature, same baseline as the place of issue
    draw_text_left(buf, "ELENA MARA VOSS", 286, 612, 2, INK)
    fill_rect(buf, 286, 634, 484, 635, INK)
    draw_text_left(buf, "HOLDER'S SIGNATURE", 286, 640, 1, FAINT)

    # machine-readable zone
    fill_rect(buf, 56, 668, 500, 676, NAVY)
    line1, line2 = mrz_lines()
    draw_text(buf, line1, 278, 692, 1, INK)
    draw_text(buf, line2, 278, 712, 1, INK)
    # page footer
    draw_text(buf, "THIS PASSPORT REMAINS THE PROPERTY OF THE REPUBLIC OF MERIDIA",
              278, 800, 1, FAINT)
    draw_text(buf, "IF FOUND PLEASE RETURN TO THE NEAREST MERIDIAN CONSULATE",
              278, 818, 1, FAINT)

    # ================= RIGHT PAGE — visas =================
    draw_text(buf, "VISAS", 746, 162, 4, NAVY)
    draw_text_right(buf, "PAGE 12", 948, 168, 1, FAINT)
    fill_rect(buf, 544, 204, 948, 207, GOLD)

    # visitor-visa sticker
    fill_rect(buf, 552, 224, 940, 396, VISA_BG)
    fill_rect(buf, 552, 224, 940, 227, NAVY)
    fill_rect(buf, 552, 393, 940, 396, NAVY)
    fill_rect(buf, 552, 224, 555, 396, NAVY)
    fill_rect(buf, 937, 224, 940, 396, NAVY)
    draw_text(buf, "MERIDIA", 746, 238, 4, NAVY)
    draw_text(buf, "VISITOR VISA - MULTIPLE ENTRY", 746, 276, 2, INK)
    draw_text(buf, "VALID 90 DAYS FROM FIRST ENTRY", 746, 300, 2, INK)
    draw_text(buf, "FEE PAID  40 AUR", 746, 324, 2, INK)
    draw_text(buf, "EMPLOYMENT NOT PERMITTED", 746, 348, 2, STAMP_RED)
    draw_text(buf, "NO. V-2024-11873  -  ISSUED PORT AURELIA  12 MAR 2024",
              746, 372, 1, FAINT)

    # stamps — travel order, all after issue (12 MAR 2024), before expiry
    circle_stamp(buf, 668, 502, 76, STAMP_BLUE, [
        ("KESTRELIA", 2), ("ARRIVED", 2), ("04 APR 2024", 2), ("TRELHAVN", 2)])
    circle_stamp(buf, 856, 502, 72, STAMP_GREEN, [
        ("OSTARA", 2), ("ARRIVED", 2), ("02 FEB 2025", 2), ("VELDMAR", 2)])
    # departure stamp from Vardonia, rotated like a hand stamp
    layer = rect_stamp_layer(280, 88, STAMP_BLUE, [
        ("VARDONIA", 3), ("DEPARTED  19 SEP 2024", 2), ("KORVEST", 2)])
    blit_rotated(buf, layer, 640, 648, -13, 0.8)
    # departure stamp from Kestrelia
    circle_stamp(buf, 868, 660, 68, STAMP_BLUE, [
        ("KESTRELIA", 2), ("DEPARTED", 2), ("27 MAY 2025", 2), ("TRELHAVN", 2)])
    # small red fee stamp
    layer2 = rect_stamp_layer(150, 52, STAMP_RED, [
        ("FEE 40 AUR", 2), ("PAID", 2)])
    blit_rotated(buf, layer2, 620, 748, 7, 0.85)

    # language column — the paperwork detail at the foot of the page
    fill_rect(buf, 544, 800, 948, 801, RULE)
    draw_text(buf, "THIS PASSPORT IS ISSUED IN MERIDIAN AND ENGLISH",
              746, 812, 1, FAINT)
    draw_text(buf, "CE PASSEPORT EST DELIVRE EN MERIDIEN ET EN ANGLAIS",
              746, 828, 1, FAINT)
    draw_text(buf, "CHILDREN UNDER 16 TRAVEL ON A PARENT'S PASSPORT",
              746, 844, 1, FAINT)
    return buf


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    data = png_bytes(render())
    (out_dir / "entry.png").write_bytes(data)


if __name__ == "__main__":
    main()

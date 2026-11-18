#!/usr/bin/env python3
"""THE WORLD TODAY - news-image-20261118 v4.

A one-page newspaper front page summing up Wednesday 18 November 2026:
36 real stories from six continents, three illustrated lead stories,
a numbered world map and a markets strip. Pure Python 3 standard
library: the program draws every pixel itself and writes a
deterministic 1024x1024 PNG to /output/entry.png (or to
$MAKEFUN_OUTPUT_DIR when the kit sets it for a local run).
No network, no randomness, no timestamps in the output.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 227)
INK = (22, 22, 22)
RED = (158, 27, 27)
NAVY = (26, 42, 90)
BLUE = (30, 90, 160)
GREEN = (18, 110, 58)
GOLD = (176, 132, 20)
GREY = (112, 106, 90)
LIGHT = (233, 227, 206)
SKY = (198, 220, 235)
SEA = (64, 124, 168)
DARK = (40, 48, 64)

# 5x7 bitmap font, uppercase + digits + punctuation. '#' is ink, '.' blank.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
}
FONT.update({
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".....", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ':': (".....", ".....", ".##..", ".....", ".....", ".##..", "....."),
    ';': (".....", ".....", ".##..", ".....", ".....", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '(': ("...##", "..#..", "..#..", "..#..", "..#..", "..#..", "...##"),
    ')': ("##...", "..#..", "..#..", "..#..", "..#..", "..#..", "##..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '*': (".....", ".#.#.", ".###.", "#####", ".###.", ".#.#.", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '>': ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
    '<': ("....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"),
    '|': ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
})


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = c
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def hline(self, x, y, w, c):
        self.fill_rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill_rect(x, y, 1, h, c)

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            t = 1.0 - ((yy - cy) / ry) ** 2
            dx = int(rx * (t ** 0.5)) if t > 0 else 0
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c):
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        for yy in range(ay, cy + 1):
            if yy < by:
                xa = ax + (bx - ax) * (yy - ay) / (by - ay) if by != ay else ax
                xb = ax + (cx - ax) * (yy - ay) / (cy - ay) if cy != ay else ax
            else:
                xa = bx + (cx - bx) * (yy - by) / (cy - by) if cy != by else bx
                xb = ax + (cx - ax) * (yy - ay) / (cy - ay) if cy != ay else ax
            lo, hi = sorted([int(xa), int(xb)])
            self.fill_rect(lo, yy, hi - lo + 1, 1, c)

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, s, x, y, scale, c, align="left"):
        if align == "center":
            x -= self.text_width(s, scale) // 2
        elif align == "right":
            x -= self.text_width(s, scale)
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                glyph = FONT['?']
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '#':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx

    def wrap(self, s, max_w, scale):
        """Greedy word wrap; returns list of lines that fit max_w px."""
        words = s.split(" ")
        lines = []
        cur = ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if self.text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def png_bytes(c):
    raw = bytearray()
    stride = c.w * 3
    for y in range(c.h):
        raw.append(0)
        raw += c.px[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- illustrations

def draw_bridge(c, x, y, w, h):
    """Kerch Bridge: deck, towers, a collapsed middle span over waves."""
    c.fill_rect(x, y, w, h, SKY)
    c.fill_rect(x, y + h - 26, w, 26, SEA)
    for wy in range(y + h - 24, y + h - 2, 6):
        for wx in range(x + 4, x + w - 4, 18):
            c.hline(wx, wy, 10, (220, 235, 240))
    deck_y = y + h - 52
    c.fill_rect(x, y + 10, w, 2, (200, 205, 210))
    c.fill_rect(x, deck_y, w, 6, INK)
    for tx in (x + 60, x + w - 90):
        c.fill_rect(tx, y + 22, 5, deck_y - y - 22, INK)
        c.line(tx + 2, y + 22, x + 30, deck_y, INK)
        c.line(tx + 2, y + 22, tx + 55, deck_y, INK)
    gap = w // 2
    c.line(x + gap - 70, deck_y, x + gap - 8, deck_y + 26, RED)
    c.fill_rect(x + gap - 8, deck_y + 24, 26, 5, RED)
    c.fill_rect(x + gap + 34, deck_y + 30, 22, 4, INK)
    cx, cy = x + gap, deck_y - 14
    for ang in range(0, 360, 30):
        import math
        dx = int(16 * math.cos(math.radians(ang)))
        dy = int(16 * math.sin(math.radians(ang)))
        c.line(cx, cy, cx + dx, cy + dy, GOLD)
    c.disc(cx, cy, 6, GOLD)
    c.disc(x + gap - 40, deck_y - 8, 3, INK)
    c.disc(x + gap + 60, deck_y - 8, 3, INK)


def draw_gulf(c, x, y, w, h):
    """Qeshm / Strait of Hormuz: night sky, jets, island, fire on the water."""
    c.fill_rect(x, y, w, h, DARK)
    for sx in range(x + 12, x + w - 8, 34):
        c.fill_rect(sx, y + 8 + (sx * 7) % 26, 2, 2, (220, 220, 200))
    c.fill_rect(x, y + h - 34, w, 34, (24, 60, 92))
    for wy in range(y + h - 30, y + h - 4, 6):
        for wx in range(x + 6, x + w - 6, 22):
            c.hline(wx, wy, 12, (120, 170, 210))
    ix, iy = x + w // 2 - 40, y + h - 44
    c.ellipse(ix + 40, iy + 10, 62, 12, (52, 84, 52))
    c.triangle(ix + 8, iy + 10, ix + 30, iy - 14, ix + 46, iy + 10, (52, 84, 52))
    c.triangle(ix + 48, iy + 10, ix + 66, iy - 8, ix + 80, iy + 10, (52, 84, 52))
    for jx, jy, s in ((x + 40, y + 22, 1), (x + w - 100, y + 12, -1)):
        c.triangle(jx, jy, jx + 34 * s, jy + 8, jx, jy + 16, (210, 210, 210))
        c.line(jx - 26 * s, jy + 8, jx, jy + 8, (240, 200, 90))
        c.line(jx - 42 * s, jy + 8, jx - 26 * s, jy + 8, (240, 140, 60))
    bx, by = x + w // 2 + 52, y + h - 52
    for ang in range(0, 360, 24):
        import math
        dx = int(20 * math.cos(math.radians(ang)))
        dy = int(20 * math.sin(math.radians(ang)))
        c.line(bx, by, bx + dx, by + dy, (240, 120, 30))
    c.disc(bx, by, 7, (250, 190, 60))
    c.disc(bx, by, 3, (255, 240, 180))


def draw_chip(c, x, y, w, h):
    """Nvidia: green chip on a rising chart. Everything stays inside
    the (x, y, w, h) box."""
    c.fill_rect(x, y, w, h, (232, 240, 228))
    base = y + h - 4
    max_bh = h - 14
    bars = [16, 26, 22, 36, 44, 40, 58]
    bw = (w - 130) // len(bars)
    tops = []
    for i, bh in enumerate(bars):
        scaled = max(6, bh * max_bh // 60)
        bx = x + 10 + i * bw
        c.fill_rect(bx, base - scaled, bw - 6, scaled,
                    (120, 190, 90) if i < 5 else GREEN)
        tops.append((bx + (bw - 6) // 2, base - scaled))
    c.line(tops[0][0], tops[0][1], tops[-1][0], tops[-1][1], GREEN)
    c.triangle(tops[-1][0] - 7, tops[-1][1] + 1, tops[-1][0] + 5,
               tops[-1][1] - 6, tops[-1][0] - 7, tops[-1][1] - 11, GREEN)
    cx, cy = x + w - 52, y + h // 2
    half = 16
    for px in range(cx - half - 4, cx + half + 5, 8):
        c.fill_rect(px, cy - half - 5, 3, 5, INK)
        c.fill_rect(px, cy + half, 3, 5, INK)
    for py in range(cy - half - 4, cy + half + 5, 8):
        c.fill_rect(cx - half - 5, py, 5, 3, INK)
        c.fill_rect(cx + half, py, 5, 3, INK)
    c.fill_rect(cx - half, cy - half, 2 * half, 2 * half, (18, 130, 60))
    c.rect(cx - half, cy - half, 2 * half, 2 * half, INK, 2)
    c.fill_rect(cx - 11, cy - 11, 22, 22, (232, 240, 228))
    c.text("NV", cx - 11, cy - 8, 2, GREEN)


# ---------------------------------------------------------------- world map

def draw_map(c, x, y, w, h):
    """Stylised world map: land as soft ellipses, red numbered pins."""
    c.fill_rect(x, y, w, h, (214, 230, 238))
    land = (146, 178, 138)
    c.ellipse(x + 105, y + 34, 92, 26, land)    # North America
    c.ellipse(x + 150, y + 62, 60, 16, land)
    c.ellipse(x + 235, y + 16, 16, 9, land)     # Greenland
    c.ellipse(x + 168, y + 88, 30, 26, land)    # South America
    c.ellipse(x + 330, y + 28, 26, 14, land)    # Europe
    c.ellipse(x + 348, y + 76, 30, 28, land)    # Africa
    c.ellipse(x + 452, y + 34, 108, 26, land)   # Asia
    c.ellipse(x + 470, y + 66, 46, 12, land)    # SE Asia
    c.ellipse(x + 545, y + 96, 34, 13, land)    # Australia
    c.disc(x + 386, y + 20, 4, land)            # UK
    c.disc(x + 556, y + 40, 4, land)            # Japan
    labels = [("N. AMERICA", x + 6, y + 2), ("S. AMERICA", x + 204, y + 102),
              ("EUROPE", x + 300, y + 2), ("AFRICA", x + 322, y + 106),
              ("ASIA", x + 440, y + 2), ("AUSTRALIA", x + 510, y + 110)]
    for txt, lx, ly in labels:
        c.text(txt, lx, ly, 1, GREY)
    pins = [("7", 42, 26), ("1", 372, 34), ("8", 330, 24), ("2", 428, 52),
            ("3", 506, 46), ("4", 522, 60), ("5", 350, 82), ("6", 596, 92)]
    for num, px, py in pins:
        c.disc(x + px, y + py, 8, RED)
        c.text(num, x + px - 3, y + py - 4, 1, (255, 255, 255))


MAP_KEY = [
    "1 KERCH BRIDGE, UKRAINE",
    "2 QESHM ISLAND, IRAN",
    "3 SHENZHEN SUMMIT",
    "4 MANILA: TRUMP + QUAD",
    "5 DR CONGO: EBOLA",
    "6 COOK IS.: CYCLONE XAVIER",
    "7 ALASKA: PELTOLA WINS",
    "8 THE HAGUE: MYANMAR RULING",
]


# ---------------------------------------------------------------- stories
# 36 stories: 3 illustrated leads + 33 briefs (headline + one deck line).

LEADS = [
    ("LEAD STORY - UKRAINE", "KERCH BRIDGE FALLS",
     "UKRAINE'S SEVEN-STAGE STRIKE COLLAPSES THE ROAD ARCH INTO THE "
     "KERCH STRAIT. RUSSIA HITS TWO KYIV BRIDGES; TWO KILLED. PUTIN "
     "MEETS TRUMP AND XI IN SHENZHEN ON THURSDAY."),
    ("THE GULF - WAR IN THE GULF", "US JETS HIT QESHM",
     "US FIGHTERS HIT AN IRGC MISSILE SITE ON QESHM AFTER DRONE ATTACKS."),
    ("MARKETS - CHIPS", "NVIDIA: $115.8BN",
     "REVENUE $115.8BN, GUIDES $130BN; BOARD RULES OUT HUANG'S RETURN."),
]

COLUMNS = [
    ("NORTH AMERICA", [
        ("PELTOLA WINS ALASKA SEAT",
         "DEMOCRATS REACH 56 SENATE SEATS AFTER ALASKA WIN."),
        ("US LOSES MEASLES-FREE TAG",
         "5,400 CASES, 8 DEATHS IN 2026, WORST SINCE 1991."),
        ("NSA NETWORK GOES OFFLINE",
         "EIGHTH MAJOR US OUTAGE IN A WEEK; NO CYBERATTACK SEEN."),
        ("ANTHROPIC PLANS $1.4TN IPO",
         "$1.4TN IPO PRICED ON NASDAQ ON THURSDAY."),
        ("TRUMP MEETS MARCOS, QUAD",
         "TRUMP MEETS MARCOS AND QUAD LEADERS IN MANILA."),
        ("27 YEARS FOR PLOT VS TRUMP",
         "PAKISTANI MAN JAILED OVER IRAN-LINKED PLOT."),
    ]),
    ("SOUTH AMERICA", [
        ("AWA GROUP EMERGES IN AMAZON",
         "ISOLATED GROUP EMERGES FROM THE BRAZILIAN AMAZON."),
        ("BRAZIL REAL FALLS ON BUDGET",
         "LULA FISCAL PLAN DISAPPOINTS INVESTORS."),
        ("POPE LEO HAD CANCER SURGERY",
         "POPE LEO REVEALS SURGERY AFTER SOUTH AMERICA TOUR."),
        ("$12BN VENEZUELA OIL REVENUE",
         "US DETAILS $12BN IN OIL AND MINERAL REVENUE."),
    ]),
    ("EUROPE", [
        ("ZVEREV INTO ATP FINALS",
         "ZVEREV REACHES ATP FINALS KNOCKOUT STAGE IN TURIN."),
        ("MOLDOVA CLOSES AIRSPACE",
         "RUSSIAN DRONES ENTERED AIRSPACE OVER CHISINAU."),
        ("COURT TO RULE ON MYANMAR",
         "ICJ TO RULE ON MYANMAR GENOCIDE CASE ON THURSDAY."),
        ("140,000 MARCH IN FRANCE",
         "FOURTH WEEKEND OF COST-OF-LIVING PROTESTS."),
        ("EU BACKS UKRAINE FUNDS",
         "NEW RUSSIA SANCTIONS AS WELL AS UKRAINE FUNDING."),
        ("'HUMAN' IS WORD OF THE YEAR",
         "CAMBRIDGE DICTIONARY PICKS 'HUMAN' FOR 2026."),
    ]),
    ("AFRICA", [
        ("EBOLA SURGE IN DR CONGO",
         "11,000 CASES AND 5,400 DEATHS, THE UN SAYS."),
        ("EU PLANS RWANDA RETURN HUBS",
         "FIVE EU STATES PLAN RETURN HUBS IN KIGALI."),
        ("ERITREA BORDER CLASHES GROW",
         "CLASHES NEAR THE TIGRAY BORDER RAISE WAR FEARS."),
        ("FELA KUTI JOINS ROCK HALL",
         "FIRST AFRICAN INDUCTED INTO ROCK HALL OF FAME."),
    ]),
    ("MIDDLE EAST", [
        ("GAZA COLD KILLS IN TENTS",
         "BOARD OF PEACE WARNS THE CEASEFIRE MAY COLLAPSE."),
        ("EISENKOT TO FORM GOVERNMENT",
         "KAHANA ELECTED KNESSET SPEAKER AS NETANYAHU LOSES OUT."),
    ]),
    ("ASIA", [
        ("XI OPENS APEC IN SHENZHEN",
         "PUTIN LANDS; TRUMP-XI-PUTIN SUMMIT ON THURSDAY."),
        ("MONGOLIA LEADER TO RESIGN",
         "$25M BRIBERY CLAIMS TIED TO A COAL-RAILWAY DEAL."),
        ("PLANE CRASH KILLS 19",
         "AN-12 CRASHES IN SIBERIA; ALL 19 ABOARD KILLED."),
        ("US CURBS REMOTE CHIP RULES",
         "CHINA OBJECTS TO NEW US EXPORT CURBS."),
        ("KOREA LIFTS GROWTH OUTLOOK",
         "2027 GROWTH FORECAST RAISED TO 3.9%."),
        ("INDIA KEEPS ITS ITU SEAT",
         "RE-ELECTED TO ITU COUNCIL FOR 2027-2030."),
    ]),
    ("OCEANIA", [
        ("XAVIER SLAMS COOK ISLANDS",
         "CATEGORY 5, GUSTS TO 315 KM/H OVER COOK ISLANDS."),
        ("FIJI DROUGHT IS A DISASTER",
         "EL NINO DROUGHT DECLARED A NATIONAL DISASTER."),
        ("AUSSIE PAY GAP BELOW 20%",
         "FIRST TIME BELOW 20%; 54% SAY LIFE GOT WORSE."),
        ("SANDPAPERGATE FORUM OPENS",
         "CRICKET AUSTRALIA OPENS FORUM FOR PLAYERS."),
        ("US BOOSTS PACIFIC ISLE AID",
         "US BOOSTS FUNDING FOR PALAU, FSM, MARSHALLS."),
    ]),
]

# Column grouping: (sections, x, width)
COLUMN_LAYOUT = [
    (["NORTH AMERICA", "SOUTH AMERICA", "EUROPE"], 16, 328),
    (["EUROPE", "AFRICA", "MIDDLE EAST"], 352, 328),
    (["ASIA", "OCEANIA"], 688, 320),
]
# EUROPE appears in two columns by design: Zverev goes with column 1,
# the other five European stories with column 2.
COLUMN_SPLIT = {
    "NORTH AMERICA": 0, "SOUTH AMERICA": 0,
    "EUROPE": 1, "AFRICA": 1, "MIDDLE EAST": 1,
    "ASIA": 2, "OCEANIA": 2,
}
EUROPE_FIRST = 1  # stories 0..0 of EUROPE go to column 1, the rest to column 2


def draw_section(c, x, y, w, title, items):
    c.text(title, x, y, 2, RED)
    c.hline(x, y + 16, w, RED)
    y += 22
    for head, deck in items:
        c.text(head, x, y, 2, INK)
        c.text(deck, x, y + 15, 1, GREY)
        y += 28
    return y


def build():
    c = Canvas(W, H, PAPER)
    c.rect(8, 8, 1008, 1008, INK, 2)
    c.rect(12, 12, 1000, 1000, INK, 1)

    # Masthead.
    c.text("THE WORLD TODAY", 512, 26, 10, INK, align="center")
    c.fill_rect(16, 104, 992, 3, INK)
    c.text("WEDNESDAY, 18 NOVEMBER 2026", 24, 112, 2, INK)
    c.text("36 STORIES - SIX CONTINENTS", 1000, 112, 2, RED, align="right")
    c.fill_rect(16, 134, 992, 2, INK)

    # Markets strip.
    c.fill_rect(16, 140, 992, 40, NAVY)
    c.text("S&P 500 7,341 -1.03%  |  FTSE 10,690 -1.76%  |  DAX 26,045 -2.08%",
           512, 146, 2, (255, 255, 255), align="center")
    c.text("NASDAQ 24,328 -0.74%  |  NIKKEI 59,024 +0.20%  |  BRENT $92.47 -0.72%  |  VIX 27.7",
           512, 162, 2, (255, 255, 255), align="center")

    # Lead stories.
    c.rect(16, 186, 536, 264, INK, 2)
    draw_bridge(c, 20, 190, 528, 104)
    kicker, head, deck = LEADS[0]
    c.text(kicker, 24, 300, 2, RED)
    c.text(head, 24, 318, 4, INK)
    yy = 352
    for ln in c.wrap(deck, 504, 2):
        c.text(ln, 24, yy, 2, INK)
        yy += 16

    right = [(568, 186, LEADS[1], draw_gulf), (568, 320, LEADS[2], draw_chip)]
    for px, py, (kicker, head, deck), drawer in right:
        c.rect(px, py, 440, 130, INK, 2)
        drawer(c, px + 4, py + 4, 432, 44)
        c.text(kicker, px + 8, py + 52, 2, RED)
        c.text(head, px + 8, py + 68, 3, INK)
        yy = py + 94
        for ln in c.wrap(deck, 408, 2):
            c.text(ln, px + 8, yy, 2, INK)
            yy += 16

    # World map strip.
    c.text("THE DAY IN ONE MAP - EIGHT PLACES THAT MADE THE NEWS",
           16, 458, 2, RED)
    c.hline(16, 476, 992, INK)
    draw_map(c, 16, 480, 624, 120)
    c.rect(16, 480, 624, 120, INK, 1)
    yy = 480
    for item in MAP_KEY:
        c.text(item, 656, yy, 2, INK)
        yy += 15

    # Story columns.
    c.hline(16, 606, 992, INK)
    sections = {name: items for name, items in COLUMNS}
    europe = sections["EUROPE"]
    col_items = [[], [], []]
    for name, items in COLUMNS:
        if name == "EUROPE":
            col_items[0].append(("EUROPE", europe[:1]))
            col_items[1].append(("EUROPE", europe[1:]))
        else:
            col_items[COLUMN_SPLIT[name]].append((name, items))
    for (names, x, w), items in zip(COLUMN_LAYOUT, col_items):
        y = 610
        for title, stories in items:
            y = draw_section(c, x, y, w, title, stories)
            y += 4
    c.vline(348, 610, 386, GREY)
    c.vline(684, 610, 386, GREY)

    # Footer.
    c.text("SOURCES: REUTERS - AP - AFP - AL JAZEERA - BBC",
           512, 1003, 1, GREY, align="center")
    return c


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()

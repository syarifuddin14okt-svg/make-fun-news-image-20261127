#!/usr/bin/env python3
"""The World Today - Friday, 27 November 2026.

A pure-stdlib Python program that draws a one-page newspaper front page
summing up the world news of Friday 27 November 2026 and writes it as a
1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Everything is hand-rolled: a pixel buffer, a small 5x7 bitmap font, simple
scene drawing and a minimal PNG encoder. No network, no third-party code,
no clock, no randomness: two runs write byte-identical files.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 227)
INK = (26, 26, 26)
RED = (164, 30, 34)
BLUE = (31, 78, 121)
SKY = (188, 214, 232)
SUN = (242, 196, 66)
GROUND = (96, 104, 64)
GREY = (120, 120, 118)
DARKGREY = (70, 70, 70)
ORANGE = (232, 120, 30)
WHITE = (255, 255, 255)
LIGHTGREY = (210, 210, 205)

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 characters; '#' is ink.
# ---------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "*": (".....", "..#..", "#.#.#", ".###.", "#.#.#", "..#..", "....."),
    "•": (".....", ".....", ".##..", ".##..", ".##..", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}

# Normalise curly quotes and dashes to the glyphs we have.
TRANSLATE = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u00b7": "•",
})


def normalise(text):
    return text.translate(TRANSLATE).upper()


# ---------------------------------------------------------------------------
# Canvas: an RGB pixel buffer with simple drawing primitives.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.pix = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, background)

    def set_pixel(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pix[i] = colour[0]
            self.pix[i + 1] = colour[1]
            self.pix[i + 2] = colour[2]

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = colour
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.pix[i] = r
                self.pix[i + 1] = g
                self.pix[i + 2] = b

    def rect(self, x, y, w, h, colour, thickness=1):
        self.fill_rect(x, y, w, thickness, colour)
        self.fill_rect(x, y + h - thickness, w, thickness, colour)
        self.fill_rect(x, y, thickness, h, colour)
        self.fill_rect(x + w - thickness, y, thickness, h, colour)

    def hline(self, x0, x1, y, colour, thickness=1):
        self.fill_rect(x0, y, x1 - x0, thickness, colour)

    def vline(self, x, y0, y1, colour, thickness=1):
        self.fill_rect(x, y0, thickness, y1 - y0, colour)

    def line(self, x0, y0, x1, y1, colour):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set_pixel(x, y, colour)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def filled_circle(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) * (yy - cy)) ** 0.5)
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, colour)

    def filled_ellipse(self, cx, cy, rx, ry, colour):
        for yy in range(cy - ry, cy + ry + 1):
            t = 1.0 - ((yy - cy) / ry) ** 2
            if t < 0:
                continue
            dx = int(rx * (t ** 0.5))
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, colour)

    def filled_triangle(self, x0, y0, x1, y1, x2, y2, colour):
        # Simple scanline fill for a triangle.
        ys = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = ys
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / (by - ay) if by != ay else 0.0
                xa = ax + (bx - ax) * t1
            else:
                t1 = (y - by) / (cy - by) if cy != by else 0.0
                xa = bx + (cx - bx) * t1
            t2 = (y - ay) / (cy - ay)
            xb = ax + (cx - ax) * t2
            lo, hi = (int(xa), int(xb)) if xa < xb else (int(xb), int(xa))
            self.fill_rect(lo, y, hi - lo + 1, 1, colour)

    # -- text ---------------------------------------------------------------
    def text_width(self, text, scale):
        return len(normalise(text)) * 6 * scale - scale

    def draw_text(self, text, x, y, scale, colour, bold=False):
        text = normalise(text)
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        px = cx + col * scale
                        py = y + row * scale
                        self.fill_rect(px, py, scale, scale, colour)
                        if bold:
                            self.fill_rect(px + scale, py, 1, scale, colour)
            cx += 6 * scale
        return cx

    def draw_text_centred(self, text, cx, y, scale, colour, bold=False):
        w = self.text_width(text, scale)
        self.draw_text(text, cx - w // 2, y, scale, colour, bold)

    def wrap(self, text, max_width, scale):
        """Greedy word wrap; returns a list of lines."""
        words = normalise(text).split(" ")
        lines = []
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if self.text_width(trial, scale) <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw_paragraph(self, text, x, y, max_width, scale, colour,
                       line_height=None, bold=False):
        if line_height is None:
            line_height = 8 * scale
        lines = self.wrap(text, max_width, scale)
        for i, line in enumerate(lines):
            self.draw_text(line, x, y + i * line_height, scale, colour, bold)
        return len(lines)


# ---------------------------------------------------------------------------
# Minimal PNG encoder (RGB, 8-bit, no interlace). Deterministic: fixed
# filter (none) and fixed zlib level, no ancillary chunks, no timestamps.
# ---------------------------------------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.pix[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", comp)
    png += _chunk(b"IEND", b"")
    return png


# ---------------------------------------------------------------------------
# The front page.
# ---------------------------------------------------------------------------
MARGIN = 36
RIGHT = 988


def draw_scene(c, x, y, w, h):
    """A small scene for the lead story: a drone strike on an air-defence
    station at dusk - sky, sun, clouds, a radar dish, a drone, a blast."""
    c.fill_rect(x, y, w, h, SKY)
    # Sun and clouds.
    c.filled_circle(x + w - 52, y + 34, 22, SUN)
    c.filled_ellipse(x + 70, y + 34, 46, 12, WHITE)
    c.filled_ellipse(x + 96, y + 28, 34, 10, WHITE)
    c.filled_ellipse(x + w - 150, y + 62, 40, 10, WHITE)
    # Ground.
    ground_y = y + h - 42
    c.fill_rect(x, ground_y, w, 42, GROUND)
    c.fill_rect(x, ground_y, w, 3, DARKGREY)
    # Radar tower and dish.
    tower_x = x + 78
    c.fill_rect(tower_x - 4, ground_y - 62, 8, 62, DARKGREY)
    c.fill_rect(tower_x - 26, ground_y - 8, 52, 8, DARKGREY)
    c.filled_ellipse(tower_x, ground_y - 66, 36, 18, GREY)
    c.line(tower_x - 30, ground_y - 78, tower_x + 30, ground_y - 54, INK)
    c.line(tower_x - 30, ground_y - 54, tower_x + 30, ground_y - 78, INK)
    # Blast where the drone hits the dish.
    bx, by = tower_x + 6, ground_y - 76
    c.filled_circle(bx, by, 26, ORANGE)
    c.filled_circle(bx, by, 16, SUN)
    c.filled_circle(bx, by, 8, WHITE)
    for dx, dy in ((-34, -14), (30, -22), (-28, 18), (34, 12), (0, -34),
                   (-10, 30), (18, 28)):
        c.line(bx, by, bx + dx, by + dy, ORANGE)
    # Smoke.
    c.filled_circle(bx - 18, by - 34, 10, LIGHTGREY)
    c.filled_circle(bx + 4, by - 42, 12, LIGHTGREY)
    c.filled_circle(bx + 24, by - 34, 9, LIGHTGREY)
    # The drone, banking away.
    dx, dy = x + w - 118, y + 78
    c.fill_rect(dx - 26, dy - 4, 52, 8, INK)
    c.fill_rect(dx - 6, dy - 10, 12, 20, INK)
    c.line(dx - 34, dy - 14, dx - 14, dy - 8, INK)
    c.line(dx + 14, dy - 8, dx + 34, dy - 14, INK)
    c.line(dx - 34, dy + 14, dx - 14, dy + 8, INK)
    c.line(dx + 14, dy + 8, dx + 34, dy + 14, INK)
    # A second, smaller radar post on the right.
    px = x + w - 58
    c.fill_rect(px - 3, ground_y - 34, 6, 34, DARKGREY)
    c.filled_ellipse(px, ground_y - 38, 20, 10, GREY)
    c.rect(x, y, w, h, INK, 2)


def draw_story(c, x, y, width, headline, deck):
    """Headline (scale 3, bold) plus a short deck (scale 2)."""
    lines = c.wrap(headline, width, 3)
    for i, line in enumerate(lines):
        c.draw_text(line, x, y + i * 26, 3, INK, bold=True)
    deck_y = y + len(lines) * 26 + 8
    c.draw_paragraph(deck, x, deck_y, width, 2, INK, line_height=17)
    return deck_y


def build_page():
    c = Canvas(W, H, PAPER)
    c.rect(8, 8, W - 16, H - 16, INK, 3)

    # Masthead.
    c.draw_text_centred("THE WORLD TODAY", W // 2, 26, 7, INK, bold=True)
    c.hline(MARGIN, RIGHT, 88, RED, 4)
    c.draw_text_centred("FRIDAY, 27 NOVEMBER 2026", W // 2, 100, 3, INK,
                        bold=True)
    c.hline(MARGIN, RIGHT, 128, INK, 2)

    # ---- Lead story -------------------------------------------------------
    lead_x = MARGIN
    lead_w = 560
    c.draw_text("LEAD STORY", lead_x, 144, 2, RED, bold=True)
    c.draw_text("KUWAIT DRONE STRIKE", lead_x, 168, 4, INK, bold=True)
    c.draw_text("FALLOUT", lead_x, 202, 4, INK, bold=True)
    n_lead = c.draw_paragraph(
        "Two Italian Rheinmetall technicians were killed when a drone "
        "struck a Kuwait air-defence station. Italy and Kuwait blame Iran. "
        "Tehran denies any role and accuses Zelenskyy of staging a "
        "'false flag'.",
        lead_x, 244, lead_w, 2, INK, line_height=16)
    c.draw_text("REPORTED 26 NOV - REUTERS, BBC, CNN", lead_x,
                244 + n_lead * 16 + 8, 2, RED, bold=True)

    # Lead scene on the right.
    draw_scene(c, 628, 144, 360, 176)
    c.draw_text("DRONE HITS KUWAIT AIR DEFENCE", 628, 328, 2, INK)

    c.hline(MARGIN, RIGHT, 352, INK, 2)

    # ---- Secondary stories, two columns, two rows ------------------------
    col_w = 464
    left_x = MARGIN
    right_x = 524
    c.vline(512, 368, 636, INK, 1)
    c.hline(MARGIN, RIGHT, 500, INK, 1)

    draw_story(c, left_x, 368, col_w, "HOUTHIS ESCALATE",
               "Strikes on Saudi Arabia escalate. Saudi defences intercept "
               "ballistic missiles aimed at Riyadh; Houthi drones target "
               "Red Sea ports.")
    draw_story(c, right_x, 368, col_w, "EU BUDGET DEADLOCK",
               "EU leaders struggle to agree a long-term budget and a $49bn "
               "loan for Ukraine.")
    draw_story(c, left_x, 516, col_w, "BRITAIN CALLS UP RESERVISTS",
               "Britain calls up military reservists for the first time "
               "since the Cold War as the Russia threat grows.")
    draw_story(c, right_x, 516, col_w, "THANKSGIVING STORMS",
               "Severe storms snarl Thanksgiving travel in the US: 800,000+ "
               "homes without power, 1,000+ flights hit, the 100th Macy's "
               "parade postponed.")

    c.hline(MARGIN, RIGHT, 652, INK, 2)

    # ---- Zelenskyy ---------------------------------------------------------
    c.draw_text("ZELENSKYY TO BBC: US 'TOO FOCUSED ON MIDDLE EAST'",
                MARGIN, 668, 3, INK, bold=True)
    c.draw_paragraph(
        "Ukraine's president tells the BBC that Washington is too focused "
        "on the Middle East - and questions the 'strange' Trump-Putin "
        "friendship.",
        MARGIN, 700, RIGHT - MARGIN, 2, INK, line_height=17)

    c.hline(MARGIN, RIGHT, 748, INK, 2)

    # ---- In brief ----------------------------------------------------------
    c.draw_text("IN BRIEF", MARGIN, 762, 3, RED, bold=True)
    briefs = [
        "Myanmar refuses parts of the ICJ genocide ruling.",
        "Bangkok oil refinery explosion injures nine.",
        "Gukesh vs Sindarov: marathon draw in Game 3 of the World Chess "
        "Championship.",
        "Gerard Depardieu to stand trial over alleged 2018 rape.",
        "Diesel tanker capsizes off Ibiza; one dead.",
        "Kim lays out North Korea's nuclear expansion plans.",
    ]
    row_ys = (798, 856, 914)
    for i, item in enumerate(briefs):
        bx = MARGIN if i % 2 == 0 else 524
        by = row_ys[i // 2]
        c.draw_text("•", bx, by, 2, RED, bold=True)
        c.draw_paragraph(item, bx + 20, by, 444, 2, INK, line_height=17)

    # ---- Footer ------------------------------------------------------------
    c.hline(MARGIN, RIGHT, 972, INK, 1)
    c.draw_text_centred("ALL STORIES AS REPORTED ON 27 NOVEMBER 2026",
                        W // 2, 984, 2, INK)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas = build_page()
    data = encode_png(canvas)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()

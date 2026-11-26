#!/usr/bin/env python3
"""Render the front page of THE WORLD IN ONE DAY for 26 November 2026.

A single-file, standard-library-only program. It draws a 1024x1024
newspaper front page with four verified stories from Thursday
26 November 2026 and writes it to entry.png.

Run:  python3 main.py
Output: $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png by default)

The picture is drawn pixel by pixel from a small built-in bitmap
font, then encoded as a PNG by hand with zlib. No network, no
randomness, no clock: two runs produce byte-identical files.
"""

import math
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# Palette: warm newsprint, near-black ink, one brick-red accent.
PAPER = (247, 243, 233)
INK = (28, 28, 26)
SOFT = (74, 72, 66)
RED = (158, 30, 24)
RULE = (120, 116, 106)
PANEL = (238, 232, 219)
SKY = (214, 224, 232)

# ---------------------------------------------------------------------------
# A 5-wide, 7-tall bitmap font, drawn from scratch for this page.
# Each glyph is seven rows; each row is five bits, leftmost pixel first.
# ---------------------------------------------------------------------------

FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
}

FONT.update({
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "a": (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    "b": (0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x1E),
    "c": (0x00, 0x00, 0x0E, 0x11, 0x10, 0x11, 0x0E),
    "d": (0x01, 0x01, 0x0D, 0x13, 0x11, 0x11, 0x0F),
    "e": (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    "f": (0x06, 0x09, 0x08, 0x1E, 0x08, 0x08, 0x08),
    "g": (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "h": (0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x11),
    "i": (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    "j": (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    "k": (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    "l": (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "m": (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    "n": (0x00, 0x00, 0x16, 0x19, 0x11, 0x11, 0x11),
    "o": (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    "p": (0x00, 0x00, 0x16, 0x19, 0x11, 0x1E, 0x10),
    "q": (0x00, 0x00, 0x0D, 0x13, 0x11, 0x0F, 0x01),
    "r": (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    "s": (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    "t": (0x08, 0x08, 0x1C, 0x08, 0x08, 0x09, 0x06),
    "u": (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    "v": (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "w": (0x00, 0x00, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "x": (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    "y": (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    "z": (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1E, 0x01, 0x01, 0x0E, 0x01, 0x01, 0x1E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '"': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
})


# ---------------------------------------------------------------------------
# Canvas: a flat RGB buffer with small shape helpers.
# ---------------------------------------------------------------------------

class Canvas:
    def __init__(self, width, height, background):
        self.w = width
        self.h = height
        self.px = bytearray(background * (width * height))

    def _set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = (yy * self.w + max(0, x)) * 3
            span = min(self.w, x + w) - max(0, x)
            if span > 0:
                self.px[base:base + span * 3] = bytes(color) * span

    def hline(self, x0, x1, y, color, thick=1):
        self.rect(min(x0, x1), y, abs(x1 - x0) + 1, thick, color)

    def vline(self, x, y0, y1, color, thick=1):
        self.rect(x, min(y0, y1), thick, abs(y1 - y0) + 1, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        half = thick // 2
        while True:
            self.rect(x - half, y - half, thick, thick, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            span = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hline(cx - span, cx + span, yy, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for yy in range(cy - ry, cy + ry + 1):
            t = (yy - cy) / ry
            span = int(rx * math.sqrt(max(0.0, 1.0 - t * t)))
            self.hline(cx - span, cx + span, yy, color)

    def triangle(self, ax, ay, bx, by, cx, cy, color):
        top, bot = min(ay, by, cy), max(ay, by, cy)
        for yy in range(top, bot + 1):
            xs = []
            for (x0, y0, x1, y1) in ((ax, ay, bx, by), (bx, by, cx, cy),
                                     (cx, cy, ax, ay)):
                if y0 == y1:
                    continue
                if min(y0, y1) <= yy <= max(y0, y1):
                    t = (yy - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            if len(xs) >= 2:
                self.hline(int(min(xs)), int(max(xs)), yy, color)

    # -- text ---------------------------------------------------------------
    def glyph(self, x, y, ch, scale, color):
        rows = FONT.get(ch)
        if rows is None:
            rows = FONT["?"]
        for r in range(7):
            bits = rows[r]
            for c in range(5):
                if bits & (1 << (4 - c)):
                    self.rect(x + c * scale, y + r * scale,
                              scale, scale, color)

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale if text else 0

    def text(self, x, y, text, scale, color):
        for i, ch in enumerate(text):
            self.glyph(x + i * 6 * scale, y, ch, scale, color)

    def text_center(self, cx, y, text, scale, color):
        self.text(cx - self.text_width(text, scale) // 2, y, text, scale, color)

    def wrap(self, text, max_width, scale):
        """Greedy word wrap; returns a list of lines that fit max_width."""
        words = text.split(" ")
        lines, cur = [], ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if self.text_width(trial, scale) <= max_width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def write_png(canvas, path):
    """Encode the canvas as a plain RGB PNG. Fully deterministic."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    body = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    header = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", header)
    png += chunk(b"IDAT", body)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    os.chmod(path, 0o644)
    return len(png)


# ---------------------------------------------------------------------------
# Pictograms: one small flat drawing per story, inside its own panel.
# ---------------------------------------------------------------------------

def panel(cv, x, y, size):
    cv.rect(x, y, size, size, PANEL)
    cv.rect(x, y, size, 3, RED)
    cv.rect(x, y + size - 3, size, 3, INK)


def draw_rocket(cv, x, y, size):
    """A tactical missile climbing, drawn for the North Korea story."""
    cx, cy = x + size // 2, y + size // 2
    panel(cv, x, y, size)
    cv.rect(x + 14, y + size - 34, size - 28, 4, RULE)          # ground
    cv.triangle(cx, cy - 58, cx - 13, cy - 28, cx + 13, cy - 28, RED)
    cv.rect(cx - 13, cy - 28, 26, 52, INK)                      # body
    cv.rect(cx - 13, cy - 12, 26, 6, PAPER)                     # band
    cv.triangle(cx - 13, cy + 24, cx - 30, cy + 44, cx - 13, cy + 38, INK)
    cv.triangle(cx + 13, cy + 24, cx + 30, cy + 44, cx + 13, cy + 38, INK)
    cv.triangle(cx - 8, cy + 24, cx, cy + 52, cx + 8, cy + 24, RED)
    cv.disc(cx - 34, cy - 44, 4, RED)
    cv.disc(cx + 38, cy - 30, 3, RED)
    cv.disc(cx + 30, cy - 56, 2, INK)


def draw_balloon(cv, x, y, size):
    """A giant parade balloon over a street, for the Macy's story."""
    cx, cy = x + size // 2, y + size // 2
    panel(cv, x, y, size)
    cv.rect(x, y, size, 52, SKY)
    cv.ellipse(cx, cy - 22, 52, 40, RED)                        # balloon
    cv.ellipse(cx - 18, cy - 36, 14, 10, (255, 255, 255))        # shine
    cv.line(cx - 8, cy + 16, cx - 22, cy + 52, INK, 2)           # strings
    cv.line(cx + 8, cy + 16, cx + 22, cy + 52, INK, 2)
    cv.line(cx, cy + 16, cx, cy + 52, INK, 2)
    for bx in (x + 16, x + 52, x + 88, x + 118):
        cv.rect(bx, y + size - 46, 20, 46, INK)                  # buildings
    cv.rect(x + 16, y + size - 52, 20, 6, INK)
    cv.rect(x + 88, y + size - 54, 20, 8, INK)
    cv.line(cx - 26, cy - 66, cx - 18, cy - 74, INK, 3)          # wind
    cv.line(cx + 6, cy - 70, cx + 22, cy - 70, INK, 3)
    cv.line(cx + 26, cy - 62, cx + 40, cy - 66, INK, 3)


def draw_refinery(cv, x, y, size):
    """A refinery tower with flame and smoke, for the Ras Tanura story."""
    cx, cy = x + size // 2, y + size // 2
    panel(cv, x, y, size)
    cv.rect(x + 14, y + size - 34, size - 28, 4, RULE)          # ground
    cv.rect(cx - 34, cy - 6, 12, 40, INK)                       # tower one
    cv.rect(cx - 8, cy - 26, 14, 60, INK)                       # tower two
    cv.rect(cx + 20, cy + 6, 12, 28, INK)                       # tower three
    cv.line(cx - 28, cy - 6, cx - 1, cy - 26, INK, 2)
    cv.line(cx - 1, cy - 26, cx + 26, cy + 6, INK, 2)
    cv.triangle(cx - 1, cy - 56, cx - 13, cy - 26, cx + 11, cy - 26, RED)
    cv.triangle(cx - 1, cy - 48, cx - 8, cy - 26, cx + 6, cy - 26, (232, 126, 32))
    cv.disc(cx - 52, cy - 52, 9, SOFT)                          # smoke
    cv.disc(cx - 38, cy - 62, 12, SOFT)
    cv.disc(cx - 20, cy - 58, 8, SOFT)
    cv.disc(cx + 44, cy - 48, 7, SOFT)


def draw_jet(cv, x, y, size):
    """A fighter jet in profile, for the Savasleyka story."""
    cx, cy = x + size // 2, y + size // 2
    panel(cv, x, y, size)
    cv.rect(x, y, size, 56, SKY)
    cv.triangle(cx + 62, cy - 6, cx + 18, cy - 14, cx + 18, cy + 2, INK)
    cv.rect(cx - 58, cy - 14, 76, 16, INK)                      # fuselage
    cv.triangle(cx - 58, cy - 14, cx - 70, cy - 2, cx - 58, cy + 2, RED)
    cv.triangle(cx - 6, cy + 2, cx - 34, cy + 34, cx + 2, cy + 2, INK)
    cv.triangle(cx + 6, cy - 14, cx + 30, cy - 40, cx + 14, cy - 14, INK)
    cv.triangle(cx - 52, cy - 14, cx - 62, cy - 34, cx - 44, cy - 14, INK)
    cv.ellipse(cx + 34, cy - 10, 12, 4, PAPER)                   # canopy
    cv.disc(cx - 74, cy + 6, 3, RED)
    cv.disc(cx - 82, cy + 12, 2, RED)
    cv.line(cx - 30, cy + 40, cx - 30, cy + 52, INK, 2)
    cv.line(cx + 24, cy + 40, cx + 24, cy + 52, INK, 2)
    cv.rect(x + 14, y + size - 22, size - 28, 4, RULE)          # runway


# ---------------------------------------------------------------------------
# The four stories of Thursday 26 November 2026, as reported that day.
# ---------------------------------------------------------------------------

STORIES = [
    {
        "kicker": "NORTH KOREA - NUCLEAR ARSENAL",
        "headline": "KIM ORDERS WIDER DEPLOYMENT OF TACTICAL NUCLEAR ARMS",
        "deck": (
            "Kim Jong Un, touring nuclear plants on Wednesday, said the "
            "North must deploy battlefield nuclear weapons across more "
            "domains and expand nuclear material output, KCNA reported on "
            "Thursday. He called the North's nuclear status 'absolutely "
            "inviolable'."
        ),
        "art": draw_rocket,
    },
    {
        "kicker": "NEW YORK - THANKSGIVING",
        "headline": "STORM GROUNDS MACY'S PARADE FOR THE FIRST TIME IN 100 YEARS",
        "deck": (
            "The 100th Macy's Thanksgiving Day Parade will march on "
            "Saturday instead, after a nor'easter bearing down on New York "
            "threatened gusts up to 60 mph, too strong for the giant "
            "balloons. It is the first weather postponement in the parade's "
            "100-year history."
        ),
        "art": draw_balloon,
    },
    {
        "kicker": "MIDDLE EAST - OIL",
        "headline": "HOUTHIS CLAIM STRIKE ON SAUDI ARABIA'S BIGGEST REFINERY",
        "deck": (
            "Satellite images showed a huge plume of black smoke over Ras "
            "Tanura after the Houthis said they hit the refinery and "
            "started a fire. Oil loadings at the terminal were suspended, "
            "a shipping source told CNN. The Saudi-led coalition said it "
            "shot down four drones there."
        ),
        "art": draw_refinery,
    },
    {
        "kicker": "UKRAINE WAR - RUSSIA",
        "headline": "UKRAINE SAYS IT HIT FIVE RUSSIAN JETS AT SAVASLEYKA AIRBASE",
        "deck": (
            "Kyiv's General Staff said a long-range strike damaged three "
            "MiG-31 jets used to fire hypersonic missiles and two Su-34 "
            "fighter-bombers, knocking them out of service. Russia did not "
            "immediately comment."
        ),
        "art": draw_jet,
    },
]

MARGIN = 36
TEXT_X = 218
TEXT_W = WIDTH - MARGIN - TEXT_X


def draw_masthead(cv):
    cv.hline(MARGIN, WIDTH - MARGIN, 30, INK, 6)
    cv.hline(MARGIN, WIDTH - MARGIN, 42, INK, 2)
    cv.text_center(WIDTH // 2, 56, "THE WORLD IN ONE DAY", 7, INK)
    cv.text_center(WIDTH // 2, 118, "THURSDAY, 26 NOVEMBER 2026", 3, RED)
    cv.text_center(WIDTH // 2, 146, "FOUR STORIES FROM AROUND THE GLOBE", 2, SOFT)
    cv.hline(MARGIN, WIDTH - MARGIN, 172, INK, 2)
    cv.hline(MARGIN, WIDTH - MARGIN, 178, INK, 6)


def draw_story(cv, story, y, height):
    story["art"](cv, MARGIN, y + 8, 150)
    tx = TEXT_X
    cv.text(tx, y + 10, story["kicker"], 2, RED)
    cv.hline(tx, WIDTH - MARGIN, y + 30, RULE, 1)
    lines = cv.wrap(story["headline"], TEXT_W, 3)
    hy = y + 40
    for line in lines:
        cv.text(tx, hy, line, 3, INK)
        hy += 26
    deck_lines = cv.wrap(story["deck"], TEXT_W, 2)
    dy = hy + 6
    for line in deck_lines:
        cv.text(tx, dy, line, 2, SOFT)
        dy += 17
    cv.hline(MARGIN, WIDTH - MARGIN, y + height - 4, RULE, 1)


def build_page():
    cv = Canvas(WIDTH, HEIGHT, PAPER)
    draw_masthead(cv)
    top = 196
    row_h = 192
    for i, story in enumerate(STORIES):
        draw_story(cv, story, top + i * row_h, row_h)
    cv.text_center(WIDTH // 2, 982, "THE WORLD IN ONE DAY - 26 NOVEMBER 2026",
                   2, RULE)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    page = build_page()
    size = write_png(page, path)
    print(f"wrote {path} ({size} bytes)")


if __name__ == "__main__":
    main()

"""Draw the front page of *The Daily Ledger* for Sunday, 22 November 2026.

Every fact on the page was checked against the morning's reporting before it
was set in type (sources are listed in README.md and BUILD-REPORT.md):

  * NATO / Poland  - PAP via Reuters and AP reporting, 21 November
  * Bitcoin        - CoinGecko prices on Sunday morning; TheStreet / Decrypt
  * Gaza aid call  - The Paris Eye breaking-news page, 22 November 02:48
  * Israel         - The Paris Eye, 22 November
  * Mexico arrest  - Reuters via Google News top stories
  * Peru quake     - AppiSToS world wire, updated 22 November 02:15
  * ATP Finals     - ATP Tour and AFP, 21 November (final played today)
  * UN robots      - Grand-Star news wire, 22 November 00:29
  * France, Kenya, Shenzhen - Paris Eye / C54 News / Reuters, 20-22 November

The page is drawn with Pillow only: a dotted world map rasterised from a
hand-built set of continent blobs, four numbered pins, a dark markets band
with the morning's real numbers, and two rows of story columns under a
broadsheet masthead.  No randomness, no clock, no network: the same code
always produces the same pixels.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Canvas and palette
# --------------------------------------------------------------------------

W, H = 1024, 1024
PAPER = (248, 244, 234)
INK = (18, 19, 24)
BODY = (52, 54, 62)
MUTED = (92, 96, 106)
ACCENT = (163, 22, 33)        # kickers and pins
NAVY = (16, 36, 66)           # markets band
NAVY_TEXT = (240, 238, 228)
NAVY_DIM = (178, 196, 226)
HAIR = (120, 116, 106)

MARGIN = 36
RIGHT = W - MARGIN

# --------------------------------------------------------------------------
# Fonts (Liberation first - it looks like a newspaper's Times - then DejaVu,
# then Pillow's built-in face so the page still draws anywhere)
# --------------------------------------------------------------------------

_FONT_DIRS = (
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/dejavu",
)

_FONT_FILES = {
    "serif_b": ("LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"),
    "serif": ("LiberationSerif-Regular.ttf", "DejaVuSerif.ttf"),
    "serif_i": ("LiberationSerif-Italic.ttf", "DejaVuSerif.ttf"),
    "sans_b": ("LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf"),
    "sans": ("LiberationSans-Regular.ttf", "DejaVuSans.ttf"),
}


def _font(kind, size):
    for name in _FONT_FILES[kind]:
        for folder in _FONT_DIRS:
            path = os.path.join(folder, name)
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# --------------------------------------------------------------------------
# Small text helpers
# --------------------------------------------------------------------------

def text_w(draw, s, font):
    return draw.textlength(s, font=font)


def wrap(draw, s, font, max_w):
    """Greedy word wrap; returns the list of lines."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(draw, x, y, s, font, max_w, leading, fill=INK):
    """Draw wrapped text, return the y just below it."""
    for line in wrap(draw, s, font, max_w):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def fit_font(draw, s, kind, start, max_w, minimum=16):
    """Largest size of `kind` (from `start` down) that fits `s` in max_w."""
    size = start
    while size > minimum:
        font = _font(kind, size)
        if text_w(draw, s, font) <= max_w:
            return font
        size -= 2
    return _font(kind, minimum)


def centered(draw, y, s, font, fill=INK):
    draw.text(((W - text_w(draw, s, font)) / 2, y), s, font=font, fill=fill)


def rule(draw, y, weight=2, fill=INK, x0=MARGIN, x1=RIGHT):
    draw.rectangle([x0, y, x1, y + weight - 1], fill=fill)


# --------------------------------------------------------------------------
# The dotted world map: continents as unions of lon/lat ellipses ("blobs").
# The map window is cropped to 84N..58S so the continents fill the frame.
# --------------------------------------------------------------------------

# (centre lon, centre lat, radius lon, radius lat)
BLOBS = [
    # North America
    (-102, 46, 33, 14), (-88, 36, 16, 8.5), (-152, 64, 12, 5),
    (-42, 73, 12, 5.5), (-84, 15, 8, 4), (-102, 23, 9, 5.5),
    # South America (plus the Central American bridge)
    (-79, 7, 5, 3), (-60, -11, 11.5, 12), (-68, -24, 7.5, 11),
    (-52, -4, 7, 5),
    # Europe
    (12, 49, 17, 7), (13, 61, 11, 6), (30, 54, 12, 7), (-3, 54, 4, 4),
    (-18, 65, 3.5, 2),
    # Africa
    (5, 28, 10, 6), (20, 4, 17, 12), (22, -14, 13, 11), (46, 4, 6, 5),
    (47, -19, 2.8, 4.5),
    # Asia and the Middle East
    (60, 50, 26, 10), (100, 53, 30, 11), (140, 58, 22, 9),
    (44, 27, 10, 6), (33, 39, 8, 5), (78, 21, 8, 7.5), (108, 32, 15, 9),
    (102, 14, 6, 7), (127, 37, 3, 3), (138, 38, 3.5, 4.5), (113, -1, 12, 2.8),
    # Oceania
    (134, -25, 12, 6), (172, -42, 2.5, 3.5), (141, -4, 5.5, 2.5),
]

MAP_LAT_TOP, MAP_LAT_BOT = 84.0, -58.0


def _land(lon, lat):
    for clon, clat, rx, ry in BLOBS:
        dx = (lon - clon) / rx
        dy = (lat - clat) / ry
        if dx * dx + dy * dy <= 1.0:
            return True
    return False


def draw_map(draw, x, y, w, h):
    """Plot the dotted map inside the box (x, y, w, h); return pin plotter."""
    pitch = 5.2
    cols = int(w / pitch)
    rows = int(h / pitch)
    span = MAP_LAT_TOP - MAP_LAT_BOT
    r = 1.6
    for row in range(rows):
        lat = MAP_LAT_TOP - (row + 0.5) * (span / rows)
        for col in range(cols):
            lon = -180.0 + (col + 0.5) * (360.0 / cols)
            if _land(lon, lat):
                cx = x + (col + 0.5) * pitch
                cy = y + (row + 0.5) * pitch
                draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                             fill=(70, 74, 84))

    def pin(lon, lat, number):
        px = x + (lon + 180.0) / 360.0 * w
        py = y + (MAP_LAT_TOP - lat) / span * h
        rad = 11
        draw.ellipse([px - rad, py - rad, px + rad, py + rad],
                     fill=ACCENT, outline=PAPER, width=2)
        font = _font("sans_b", 13)
        s = str(number)
        draw.text((px - text_w(draw, s, font) / 2, py - 8), s,
                  font=font, fill=(255, 255, 255))

    return pin


# --------------------------------------------------------------------------
# Story furniture
# --------------------------------------------------------------------------

def kicker(draw, x, y, s):
    draw.text((x, y), s, font=_font("sans_b", 15), fill=ACCENT)
    return y + 22


def story(draw, x, y, w, head, body, head_size=24, body_size=15):
    """A headline (at most two lines) over a short body; returns end y."""
    font = fit_font(draw, head, "serif_b", head_size, w)
    y = block(draw, x, y, head, font, w, int(head_size * 1.14))
    y += 3
    y = block(draw, x, y, body, _font("sans", body_size), w, 19, fill=BODY)
    return y


# --------------------------------------------------------------------------
# The page
# --------------------------------------------------------------------------

def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # --- top strip ------------------------------------------------------
    rule(draw, 26, 2)
    draw.text((MARGIN, 34), "SUNDAY, 22 NOVEMBER 2026",
              font=_font("sans_b", 16), fill=INK)
    s = "MORNING EDITION"
    draw.text((RIGHT - text_w(draw, s, _font("sans_b", 16)), 34), s,
              font=_font("sans_b", 16), fill=INK)
    rule(draw, 60, 1, fill=HAIR)

    # --- masthead -------------------------------------------------------
    centered(draw, 70, "THE DAILY LEDGER", _font("serif_b", 86))
    rule(draw, 168, 5)
    rule(draw, 178, 1)
    centered(draw, 188, "The whole day, on one page - compiled from "
                        "Reuters, PAP, AP, AFP and the wires on Sunday "
                        "morning", _font("serif_i", 16.5), fill=MUTED)

    # --- lead story (left) ----------------------------------------------
    lead_x, lead_w = MARGIN, 588
    y = kicker(draw, lead_x, 216, "EUROPE  |  NATO")
    head_font = _font("serif_b", 44)
    for line in ("NATO VOWS TO DEFEND", "'EVERY INCH' OF POLAND"):
        draw.text((lead_x, y), line, font=head_font, fill=INK)
        y += 51
    y += 6
    y = block(draw, lead_x, y,
              "Russian missiles come down on alliance soil - and the "
              "North Atlantic Council meets in Brussels on Monday",
              _font("serif_i", 19), lead_w, 25, fill=BODY)
    y += 8
    block(draw, lead_x, y,
          "WARSAW - NATO secretary general Mark Rutte guaranteed in "
          "Warsaw on Saturday that the alliance would defend every inch "
          "of Polish territory, after Poland said two Russian missiles "
          "and a suspected jet-powered drone fell in the south-east "
          "during Russia's mass attack on Ukraine. A Swedish Gripen "
          "pilot, cleared to fire on a suspected cruise missile, was "
          "beaten by the weather.",
          _font("sans", 16), lead_w, 20.5)

    # --- map (right) ------------------------------------------------------
    map_x, map_y, map_w, map_h = 644, 238, 344, 200
    draw.text((map_x, 216), "THE DAY IN PLACES",
              font=_font("sans_b", 15), fill=INK)
    draw.rectangle([map_x - 8, map_y - 6, map_x + map_w + 8,
                    map_y + map_h + 8], outline=HAIR, width=1)
    pin = draw_map(draw, map_x, map_y, map_w, map_h)
    pin(19, 52, 1)      # Poland
    pin(34, 31, 2)      # Gaza
    pin(-107, 25, 3)    # Sinaloa, Mexico
    pin(-72, -13, 4)    # Peru
    ly = map_y + map_h + 16
    for line in ("1  Poland - NATO pledge      2  Gaza - aid call",
                 "3  Mexico - cartel arrest    4  Peru - earthquake"):
        draw.text((map_x - 4, ly), line, font=_font("sans", 13.5), fill=BODY)
        ly += 19

    # --- markets band -----------------------------------------------------
    band_y = 512
    draw.rectangle([0, band_y, W, band_y + 88], fill=NAVY)
    draw.text((MARGIN, band_y + 10), "MARKETS - A BRUISING WEEK",
              font=_font("sans_b", 15), fill=(150, 178, 224))
    stats = (
        ("BITCOIN", "$59,977", "+1.9%"),
        ("ETHER", "$1,683", "+3.7%"),
        ("BNB", "$548", "+1.9%"),
        ("SOLANA", "$70", "+2.2%"),
        ("FEAR & GREED", "11", "EXTREME FEAR"),
    )
    sx = MARGIN
    for name, value, delta in stats:
        draw.text((sx, band_y + 32), value, font=_font("serif_b", 29),
                  fill=NAVY_TEXT)
        draw.text((sx, band_y + 64), name + "  " + delta,
                  font=_font("sans", 12), fill=NAVY_DIM)
        sx += 192
    block(draw, MARGIN, band_y + 100,
          "Bitcoin under $60,000 for the first time since July - 52% "
          "below October's record - after a record $541m one-day ETF "
          "outflow.", _font("sans", 14.5), RIGHT - MARGIN, 19, fill=BODY)

    # --- story columns: row one -------------------------------------------
    col_w = 300
    col1, col2, col3 = MARGIN, MARGIN + 326, MARGIN + 652
    row1 = 652
    rule(draw, row1 - 12, 1, fill=HAIR)
    for cx in (col2 - 13, col3 - 13):
        draw.line([cx, row1, cx, 928], fill=HAIR, width=1)

    yy = kicker(draw, col1, row1, "MIDDLE EAST")
    story(draw, col1, yy, col_w,
          "Four nations press Israel on Gaza aid",
          "Australia, Canada, Italy and the United Kingdom jointly "
          "called on Israel to grant immediate, unrestricted "
          "humanitarian access across Gaza, where flooding has "
          "deepened the suffering.")

    yy = kicker(draw, col2, row1, "AMERICAS")
    story(draw, col2, yy, col_w,
          "Mexico seizes 'El Chapo Isidro'",
          "Mexican forces captured Fausto Isidro Meza Flores, a "
          "cartel boss on the FBI's most-wanted list, in Sinaloa - "
          "the latest in a string of arrests, Reuters reported.")

    yy = kicker(draw, col3, row1, "SPORT")
    story(draw, col3, yy, col_w,
          "Turin final: Zverev meets Alcaraz",
          "World No. 1 Alexander Zverev, yet to drop a set all week, "
          "faces Carlos Alcaraz for the ATP Finals title today. "
          "Zverev chases a third crown; Alcaraz his first.")

    # --- story columns: row two -------------------------------------------
    row2 = 838
    story(draw, col1, row2, col_w,
          "Israel's president turns to Eisenkot",
          "President Herzog asked Gadi Eisenkot, the former army "
          "chief, to try to form the next government - passing over "
          "prime minister Benjamin Netanyahu.", head_size=22)
    story(draw, col2, row2, col_w,
          "Quake of 6.7 strikes Peru's Andes",
          "A revised official inventory counted 152 homes left "
          "uninhabitable by the tremor, as officials kept checking "
          "the region for casualties.", head_size=22)
    story(draw, col3, row2, col_w,
          "'Killer robot' talks fall short at UN",
          "Talks on lethal autonomous weapons ended without binding "
          "rules; governments agreed to work out detailed rules "
          "by 2028.", head_size=22)

    # --- in brief -----------------------------------------------------------
    brief_y = 942
    rule(draw, brief_y, 2)
    draw.text((MARGIN, brief_y + 9), "IN BRIEF",
              font=_font("sans_b", 14), fill=ACCENT)
    block(draw, MARGIN + 92, brief_y + 9,
          "SHENZHEN FALLOUT - Allies stay uneasy at the US-China-Russia "
          "peace declaration, which omitted Ukraine and Iran.",
          _font("sans", 13.5), RIGHT - MARGIN - 92, 16.5, fill=BODY)
    block(draw, MARGIN + 92, brief_y + 30,
          "FRANCE - Living-cost protests fill the streets for another "
          "weekend.   HEALTH - Kenya discharges its last Ebola patient; "
          "Congo's outbreak toll passes 5,300.",
          _font("sans", 13.5), RIGHT - MARGIN - 92, 16.5, fill=BODY)

    img.save(path, format="PNG")
    return path


if __name__ == "__main__":
    render(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "entry.png"))

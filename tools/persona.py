# -*- coding: utf-8 -*-
"""
Persona 5 styled README banners for github.com/ALLEXCEED360.

Design language: pure black ground, crimson red, bone white. Heavy condensed
display type set oblique, double-layered with a red offset and a black outline.
Torn-paper plates, halftone fields, diagonal slashes, starbursts.

Everything is deterministic: no webfonts (GitHub will not load them inside an
<img>), no external resources, CSS animation only, reduced-motion honoured.

    python -I tools/persona.py assets
"""
import html
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"

# ── palette ────────────────────────────────────────────────────────────────
BLACK, BLACK2, BLACK3 = "#050505", "#0e0e0e", "#171717"
WHITE, BONE, GREY = "#ffffff", "#ece9e4", "#7d7d7d"
RED, RED_DEEP, RED_HOT = "#e4002b", "#9e0020", "#ff2b50"

# ── type stacks (system fonts only) ────────────────────────────────────────
DISP = 'Impact,Haettenschweiler,"Franklin Gothic Heavy","Arial Narrow Bold","Arial Black",sans-serif'
HEAVY = '"Arial Black","Helvetica Neue",Helvetica,Arial,sans-serif'
SANS = '"Helvetica Neue",Helvetica,Arial,sans-serif'
MONO = 'ui-monospace,"IBM Plex Mono",SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace'

CSS = """
    .disp{font-family:%s;font-weight:400}
    .hv{font-family:%s;font-weight:900}
    .sn{font-family:%s}
    .mn{font-family:%s}
    .rise{animation:rise .85s cubic-bezier(.16,1,.3,1) both}
    .slam{animation:slam .55s cubic-bezier(.2,1.3,.3,1) both}
    .cut{animation:cut .6s cubic-bezier(.2,.9,.1,1) both}
    .d1{animation-delay:.04s}.d2{animation-delay:.12s}.d3{animation-delay:.2s}.d4{animation-delay:.3s}
    .d5{animation-delay:.4s}.d6{animation-delay:.5s}.d7{animation-delay:.6s}.d8{animation-delay:.7s}
    .draw{stroke-dasharray:1400;stroke-dashoffset:1400;animation:draw 1.3s cubic-bezier(.65,0,.35,1) .25s forwards}
    .flick{animation:flick 5s steps(1,end) infinite}
    @keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
    @keyframes slam{from{opacity:0;transform:translate(-34px,0) scale(1.06)}to{opacity:1;transform:none}}
    @keyframes cut{from{opacity:0;transform:translateX(-120px)}to{opacity:1;transform:none}}
    @keyframes draw{to{stroke-dashoffset:0}}
    @keyframes flick{0%%,92%%,96%%{opacity:1}94%%,98%%{opacity:.45}}
    @media (prefers-reduced-motion:reduce){
      .rise,.slam,.cut,.flick{animation:none}
      .draw{animation:none;stroke-dashoffset:0}
    }
""" % (DISP, HEAVY, SANS, MONO)


def e(t):
    return html.escape(t, quote=True)


def doc(w, h, label, defs, body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
            'role="img" aria-label="%s">\n  <defs>%s</defs>\n  <style>%s  </style>\n%s</svg>\n'
            % (w, h, w, h, e(label), defs, CSS, body))


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print("%-26s %6d bytes" % (name, len(content.encode("utf-8"))))


# ── deterministic jitter ───────────────────────────────────────────────────
class Rnd(object):
    def __init__(self, seed):
        self.s = seed * 1103515245 + 12345

    def nxt(self):
        self.s = (self.s * 1103515245 + 12345) & 0x7FFFFFFF
        return self.s / float(0x7FFFFFFF)

    def span(self, a, b):
        return a + (b - a) * self.nxt()


def torn(x, y, w, h, seed=1, amp=7, step=26, top=True, bottom=True):
    """Polygon with ragged top and/or bottom edges, Persona's cut-paper look."""
    r = Rnd(seed)
    pts = []
    if top:
        cx = x
        while cx < x + w:
            pts.append((cx, y + r.span(-amp, amp)))
            cx += step * r.span(.6, 1.4)
        pts.append((x + w, y + r.span(-amp, amp)))
    else:
        pts += [(x, y), (x + w, y)]
    if bottom:
        cx = x + w
        while cx > x:
            pts.append((cx, y + h + r.span(-amp, amp)))
            cx -= step * r.span(.6, 1.4)
        pts.append((x, y + h + r.span(-amp, amp)))
    else:
        pts += [(x + w, y + h), (x, y + h)]
    return " ".join("%.1f,%.1f" % p for p in pts)


def burst(cx, cy, r_out, r_in, spikes=12, rot=0.0):
    pts = []
    for i in range(spikes * 2):
        ang = rot + math.pi * i / spikes
        rad = r_out if i % 2 == 0 else r_in
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    return " ".join("%.1f,%.1f" % p for p in pts)


def p5text(x, y, text, fs, fill=WHITE, tl=None, anchor="start", skew=-9,
           shadow=RED, outline=BLACK, ow=7, cls="disp", ls=None, op=None):
    """Oblique heavy display text with a red offset copy and a black outline."""
    tlen = tl if tl is not None else len(text) * fs * 0.46
    extra = ''
    if ls is not None:
        extra += ' letter-spacing="%g"' % ls
    if op is not None:
        extra += ' fill-opacity="%s"' % op
    common = ('class="%s" font-size="%g" textLength="%g" lengthAdjust="spacingAndGlyphs" '
              'text-anchor="%s"%s' % (cls, fs, tlen, anchor, extra))
    off = min(8.0, max(2.0, round(fs * 0.075)))
    g = '<g transform="translate(0,%g) skewX(%g) translate(0,%g)">' % (y, skew, -y)
    if shadow:
        g += '<text %s x="%g" y="%g" fill="%s">%s</text>' % (common, x + off, y + off, shadow, e(text))
    if outline:
        g += ('<text %s x="%g" y="%g" fill="%s" stroke="%s" stroke-width="%g" '
              'stroke-linejoin="round" paint-order="stroke">%s</text>'
              % (common, x, y, fill, outline, ow, e(text)))
    else:
        g += '<text %s x="%g" y="%g" fill="%s">%s</text>' % (common, x, y, fill, e(text))
    return g + '</g>', tlen


HALFTONE = ('<pattern id="ht" width="9" height="9" patternUnits="userSpaceOnUse" '
            'patternTransform="rotate(20)">'
            '<circle cx="2" cy="2" r="1.5" fill="%s" fill-opacity=".30"/></pattern>' % RED)

GROUND = ('<linearGradient id="gd" x1="0" y1="0" x2=".6" y2="1">'
          '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
          '<linearGradient id="rd" x1="0" y1="0" x2="1" y2="0">'
          '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
          % (BLACK2, BLACK, RED_DEEP, RED))


def ground(w, h, ht=True):
    s = '  <rect width="%d" height="%d" fill="url(#gd)"/>\n' % (w, h)
    if ht:
        s += '  <rect width="%d" height="%d" fill="url(#ht)" opacity=".5"/>\n' % (w, h)
    return s


def chip(x, y, text, fs=11):
    w = len(text) * fs * 0.605 + 22
    s = ('<g><polygon points="%g,%g %g,%g %g,%g %g,%g" fill="%s" stroke="%s" stroke-opacity=".5"/>'
         '<text class="mn" x="%g" y="%g" font-size="%g" letter-spacing=".5" fill="%s">%s</text></g>'
         % (x + 4, y, x + w, y, x + w - 4, y + 23, x, y + 23,
            BLACK3, WHITE, x + 11, y + 15.5, fs, BONE, e(text)))
    return s, w + 9


def chiprow(x, y, items, fs=11):
    out, cx = "", x
    for it in items:
        s, adv = chip(cx, y, it, fs)
        out += s
        cx += adv
    return out


def tag(xr, y, text, bg=RED, fg=WHITE):
    """Slanted status plate, right-aligned to xr."""
    w = len(text) * 11 * 0.64 + 30
    x = xr - w
    return ('<g><polygon points="%g,%g %g,%g %g,%g %g,%g" fill="%s"/>'
            '<text class="hv" x="%g" y="%g" font-size="10.5" letter-spacing="1.8" '
            'text-anchor="middle" fill="%s">%s</text></g>'
            % (x + 9, y, x + w, y, x + w - 9, y + 25, x, y + 25, bg,
               x + w / 2, y + 17, fg, e(text)))


# ── hero ───────────────────────────────────────────────────────────────────
def make_hero():
    W, H = 1200, 486
    defs = GROUND + HALFTONE
    b = ground(W, H)
    # diagonal slashes
    b += '  <g class="cut d1" opacity=".9">\n'
    b += '    <polygon points="812,-10 938,-10 668,496 542,496" fill="%s" fill-opacity=".16"/>\n' % RED
    b += '    <polygon points="958,-10 1002,-10 732,496 688,496" fill="%s" fill-opacity=".30"/>\n' % RED
    b += '  </g>\n'
    # starburst + sigil
    b += '  <g class="rise d4">\n'
    b += '    <polygon class="flick" points="%s" fill="%s" fill-opacity=".9"/>\n' % (burst(1008, 232, 168, 112, 14, .18), RED_DEEP)
    b += '    <polygon points="%s" fill="%s"/>\n' % (burst(1008, 232, 132, 92, 14, .18), BLACK)
    b += ('    <path d="M928 232c22-36 50-54 80-54s58 18 80 54c-22 36-50 54-80 54s-58-18-80-54z" '
          'fill="none" stroke="%s" stroke-width="3"/>\n' % WHITE)
    b += '    <circle cx="1008" cy="232" r="24" fill="%s"/>\n' % RED
    b += '    <circle cx="1008" cy="232" r="24" fill="none" stroke="%s" stroke-width="3"/>\n' % WHITE
    b += '    <circle cx="999" cy="223" r="6" fill="%s"/>\n' % WHITE
    b += '  </g>\n'
    # eyebrow
    b += '  <g class="rise d1">\n'
    b += ('    <polygon points="56,30 70,30 66,46 52,46" fill="%s"/>\n' % RED)
    b += ('    <text class="hv" x="82" y="44" font-size="13" letter-spacing="6" fill="%s">ALLEXCEED360</text>\n' % WHITE)
    b += ('    <text class="mn" x="1144" y="44" font-size="12" letter-spacing="4" text-anchor="end" '
          'fill="%s">EST. DHAKA</text>\n' % GREY)
    b += '  </g>\n'
    b += '  <line class="draw" x1="56" y1="62" x2="1144" y2="62" stroke="%s" stroke-opacity=".45" stroke-width="2"/>\n' % WHITE
    # name, stacked and staggered
    t1, _ = p5text(56, 196, "ARYAN", 126, tl=330)
    t2, _ = p5text(104, 310, "ALAM", 126, tl=268)
    b += '  <g class="slam d2">%s</g>\n' % t1
    b += '  <g class="slam d3">%s</g>\n' % t2
    # torn white plate with the role line
    b += '  <g class="rise d5">\n'
    b += '    <polygon points="%s" fill="%s"/>\n' % (torn(50, 342, 690, 44, seed=7, amp=5, step=30), WHITE)
    b += ('    <text class="hv" x="70" y="372" font-size="15.5" letter-spacing="2.6" textLength="634" '
          'lengthAdjust="spacing" fill="%s">SOFTWARE ENGINEER / GAME DEVELOPER / VISUAL STORYTELLER</text>\n' % BLACK)
    b += '  </g>\n'
    b += ('  <text class="sn rise d6" x="56" y="420" font-size="19" font-style="italic" fill="%s">'
          'I build systems, and tell the stories around them.</text>\n' % BONE)
    # bottom strip
    b += '  <g class="rise d7">\n'
    b += '    <line x1="56" y1="444" x2="1144" y2="444" stroke="%s" stroke-opacity=".2" stroke-width="1.5"/>\n' % WHITE
    b += '    <g class="mn" font-size="12.5" letter-spacing="3" fill="%s">\n' % GREY
    b += '      <text x="56" y="470">BRAC UNIVERSITY / CSE</text>\n'
    b += '      <text x="416" y="470">UNITY &#183; UNREAL 5 &#183; PYTORCH</text>\n'
    b += '      <text x="836" y="470">SHIPPED ON STEAM</text>\n'
    b += '    </g>\n'
    b += '    <polygon points="388,458 400,458 396,472 384,472" fill="%s"/>\n' % RED
    b += '    <polygon points="808,458 820,458 816,472 804,472" fill="%s"/>\n' % RED
    b += '  </g>\n'
    return doc(W, H, "Aryan Alam. Software engineer, game developer and visual storyteller. "
                     "I build systems and tell the stories around them. BRAC University CSE; Unity, "
                     "Unreal 5 and PyTorch; shipped on Steam.", defs, b)


write("hero.svg", make_hero())

# ── section titles ─────────────────────────────────────────────────────────
TITLES = [
    ("title-profile.svg",   "01", "PROFILE",   "Who is holding the pen.",      "Profile. Who is holding the pen."),
    ("title-quests.svg",    "02", "QUESTS",    "What left the workshop.",      "Quests. What left the workshop."),
    ("title-abilities.svg", "03", "ABILITIES", "The tools I reach for.",       "Abilities. The tools I reach for."),
    ("title-journey.svg",   "04", "JOURNEY",   "Where the road has gone.",     "Journey. Where the road has gone."),
    ("title-chronicle.svg", "05", "CHRONICLE", "A year of commits.",           "Chronicle. A year of commits."),
    ("title-contact.svg",   "06", "CONTACT",   "Say something worth answering.", "Contact. Say something worth answering."),
]


def make_title(num, word, tagline, label):
    W, H = 1200, 132
    defs = GROUND + HALFTONE
    b = ground(W, H)
    b += '  <polygon class="cut d1" points="-10,-10 150,-10 96,142 -10,142" fill="%s"/>\n' % RED
    b += '  <polygon class="cut d1" points="150,-10 176,-10 122,142 96,142" fill="%s" fill-opacity=".45"/>\n' % RED
    n, _ = p5text(34, 96, num, 72, tl=74, shadow=None, outline=BLACK, ow=5)
    b += '  <g class="slam d2">%s</g>\n' % n
    t, tl = p5text(208, 92, word, 64, tl=len(word) * 30)
    b += '  <g class="slam d3">%s</g>\n' % t
    b += ('  <text class="sn rise d5" x="1152" y="88" font-size="17" font-style="italic" '
          'text-anchor="end" fill="%s" fill-opacity=".62">%s</text>\n' % (BONE, e(tagline)))
    b += ('  <line class="draw" x1="208" y1="112" x2="1152" y2="112" stroke="%s" stroke-opacity=".35" '
          'stroke-width="2"/>\n' % WHITE)
    return doc(W, H, "%s %s" % (num, label), defs, b)


for fn, num, word, tagsub, lbl in TITLES:
    write(fn, make_title(num, word, tagsub, lbl))


# ── card shell ─────────────────────────────────────────────────────────────
def shell(W, H, cut=24):
    p = "%d,0 %d,0 %d,%d %d,%d 0,%d 0,%d" % (cut, W, W, H - cut, W - cut, H, H, cut)
    s = '  <polygon points="%s" fill="%s" stroke="%s" stroke-opacity=".22" stroke-width="1.5"/>\n' % (p, BLACK2, WHITE)
    s += '  <polygon points="2,30 14,22 14,%d 2,%d" fill="%s"/>\n' % (H - 22, H - 12, RED)
    return s


# ── profile panel ──────────────────────────────────────────────────────────
ABOUT = [
    "I'm a Computer Science graduate from BRAC University working across software",
    "engineering, game development, and visual storytelling. Currently developing",
    "games at Dragon Drop LLC and supporting people and operations as an HR",
    "Assistant at Imprint Resources & Management LLC.",
    "",
    "I like turning ideas into things people can actually use, play, or experience.",
    "That means engineering reliable systems, building interactive worlds, and",
    "finding the details that make a project feel complete.",
    "",
    "From tracing a story across the Final Fantasy VII timeline to bringing a game",
    "to life, I enjoy the challenge of connecting technical precision with creative",
    "vision.",
]

MARKS = [
    ("EDUCATION", "BSc Computer Science, BRAC University"),
    ("GAMES", "Game Developer, Dragon Drop LLC"),
    ("PEOPLE & OPS", "HR Assistant, Imprint Resources & Management LLC"),
]

QUEST_LINE = "BUILD SOMETHING WORTH REMEMBERING."


def make_profile():
    W, H = 1200, 492
    defs = GROUND + HALFTONE
    b = ground(W, H) + shell(W, H)

    b += '  <g class="rise d1">\n'
    b += '    <polygon points="%s" fill="%s"/>\n' % (torn(38, 34, 172, 30, seed=3, amp=4, step=22), RED)
    b += ('    <text class="hv" x="52" y="55" font-size="12" letter-spacing="4.5" fill="%s">PROFILE</text>\n'
          % WHITE)
    b += '  </g>\n'

    h1, _ = p5text(44, 132, "BUILDING SYSTEMS.", 40, tl=374, ow=5)
    h2, _ = p5text(44, 184, "CREATING WORLDS.", 40, tl=350, ow=5)
    b += '  <g class="slam d2">%s</g>\n' % h1
    b += '  <g class="slam d3">%s</g>\n' % h2

    y = 232
    for i, (lab, val) in enumerate(MARKS):
        b += '  <g class="rise d%d">\n' % (4 + i)
        b += '    <polygon points="%g,%g %g,%g %g,%g %g,%g" fill="%s"/>\n' % (
            46, y - 12, 52, y - 12, 46, y + 26, 40, y + 26, RED)
        b += ('    <text class="mn" x="62" y="%g" font-size="10" letter-spacing="3" fill="%s">%s</text>\n'
              % (y, RED_HOT, e(lab)))
        b += ('    <text class="sn" x="62" y="%g" font-size="14.5" fill="%s" fill-opacity=".88">%s</text>\n'
              % (y + 22, BONE, e(val)))
        b += '  </g>\n'
        y += 54

    b += '  <polygon points="470,48 476,48 458,386 452,386" fill="%s" fill-opacity=".45"/>\n' % RED

    ty = 76
    for i, line in enumerate(ABOUT):
        if line:
            b += ('  <text class="sn rise d%d" x="518" y="%g" font-size="15.5" fill="%s" '
                  'fill-opacity=".9">%s</text>\n' % (2 + min(i, 6), ty, BONE, e(line)))
        ty += 25

    b += '  <g class="rise d8">\n'
    b += '    <polygon points="%s" fill="%s"/>\n' % (torn(40, 410, 1120, 54, seed=21, amp=5, step=34), RED)
    b += '    <polygon points="%g,%g %g,%g %g,%g %g,%g" fill="%s"/>\n' % (
        64, 420, 236, 420, 228, 452, 56, 452, BLACK)
    b += ('    <text class="hv" x="146" y="441" font-size="11" letter-spacing="3" '
          'text-anchor="middle" fill="%s">CURRENT QUEST</text>\n' % WHITE)
    b += ('    <text class="hv" x="262" y="443" font-size="21" letter-spacing="1.4" fill="%s">%s</text>\n'
          % (WHITE, e(QUEST_LINE)))
    b += '  </g>\n'

    return doc(W, H, "Profile. Building systems, creating worlds. A Computer Science graduate from "
                     "BRAC University working across software engineering, game development and visual "
                     "storytelling. Currently developing games at Dragon Drop LLC and supporting people "
                     "and operations as an HR Assistant at Imprint Resources and Management LLC. "
                     "Education: BSc Computer Science, BRAC University. Current quest: build something "
                     "worth remembering.", defs, b)


write("profile-panel.svg", make_profile())

# ── quests, in the order Aryan asked for ───────────────────────────────────
QUESTS = [
 dict(file="quest-dragondrop.svg", idx="I", name="DRAGONDROP", tl=232,
      sub="NETWORKED MULTIPLAYER PARTY GAME", status=("LIVE ON STEAM", RED),
      desc=["Physics-driven party game with a custom stage editor, cross-platform play and full Steam",
            "integration. The game I now develop and optimize at Dragon Drop LLC."],
      metric="SHIPPED ON STEAM  /  PC + MOBILE  /  CUSTOM STAGE EDITOR",
      chips=["Unity", "C#", "Photon Fusion", "Steamworks"],
      label="Quest I. DragonDrop, a networked multiplayer party game, live on Steam. Physics-driven "
            "play with a custom stage editor, cross-platform on PC and mobile and full Steam "
            "integration, and the game Aryan now develops and optimizes at Dragon Drop LLC. "
            "Unity, C sharp, Photon Fusion, Steamworks."),
 dict(file="quest-ffvii.svg", idx="II", name="FFVII TIMELINE", tl=322,
      sub="INTERACTIVE NARRATIVE ANALYSIS", status=("LIVE", RED_DEEP),
      desc=["An interactive analysis of the Final Fantasy VII universe across its major versions. Every",
            "retelling, remake and divergence laid against the others on one timeline."],
      metric="CROSS-VERSION CANON  /  INTERACTIVE TIMELINE  /  DEPLOYED",
      chips=["TypeScript", "React", "Vercel"],
      label="Quest II. FFVII Timeline Analyzer, live. An interactive analysis of the Final Fantasy VII "
            "universe across its major versions, laying every retelling, remake and divergence against "
            "the others on one timeline. TypeScript, React, Vercel."),
 dict(file="quest-omniplay.svg", idx="III", name="OMNIPLAY", tl=186,
      sub="ONE IDENTITY. EVERY GAME.", status=("IN DEVELOPMENT", BLACK3),
      desc=["Unifies what you own, played and finished across Steam, Xbox and PlayStation into one",
            "canonical record. Queue-backed ingestion, resumable syncs, every fact traceable to its source."],
      metric="3 PLATFORMS  /  RESUMABLE SYNC  /  PROVENANCE ON EVERY FIELD",
      chips=["TypeScript", "Prisma", "PostgreSQL", "Redis", "BullMQ", "Turborepo"],
      label="Quest III. OmniPlay, one identity for every game, in development. Unifies what you own, "
            "played and finished across Steam, Xbox and PlayStation into one canonical record with "
            "queue-backed ingestion, resumable syncs and provenance on every field. TypeScript, Prisma, "
            "PostgreSQL, Redis, BullMQ, Turborepo."),
 dict(file="quest-beforeyoupost.svg", idx="IV", name="BEFORE YOU POST", tl=346,
      sub="PRIVACY, BEFORE YOU HIT SHARE", status=("ON-DEVICE", RED_DEEP),
      desc=["Finds faces, sensitive text and QR codes in a photo entirely on-device, then lets you review",
            "and redact them before sharing. No backend, no accounts, nothing leaves the phone."],
      metric="100% ON-DEVICE  /  NO BACKEND  /  NO UPLOADS",
      chips=["Flutter", "Dart", "Google ML Kit"],
      label="Quest IV. Before You Post, privacy before you hit share, fully on-device. Finds faces, "
            "sensitive text and QR codes in a photo entirely on the phone, then lets you review and "
            "redact them before sharing, with no backend, no accounts and nothing leaving the device. "
            "Flutter, Dart, Google ML Kit."),
 dict(file="quest-echolens.svg", idx="V", name="ECHOLENS", tl=186,
      sub="MULTIMODAL VIDEO INTELLIGENCE", status=("IN DEVELOPMENT", BLACK3),
      desc=["Makes hours of video searchable. Ask a question and get an answer welded to the exact",
            "moment it came from. Timestamps the model cannot fabricate."],
      metric="7.9× REALTIME TRANSCRIPTION  /  SINGLE GPU  /  HYBRID SEMANTIC SEARCH",
      chips=["Python", "FastAPI", "pgvector", "faster-whisper", "PyTorch"],
      label="Quest V. EchoLens, multimodal video intelligence, in development. Makes hours of video "
            "searchable with answers welded to the exact timestamp the model cannot fabricate. "
            "7.9 times realtime transcription on a single GPU with hybrid semantic search. "
            "Python, FastAPI, pgvector, faster-whisper, PyTorch."),
]


def make_quest(q):
    W, H = 1200, 262
    defs = GROUND + HALFTONE
    b = ground(W, H) + shell(W, H)
    wm, _ = p5text(1164, 232, q["idx"], 182, fill=WHITE, tl=len(q["idx"]) * 66,
                   anchor="end", shadow=None, outline=None, op=".05")
    b += '  %s\n' % wm
    b += '  <g class="rise d1">\n'
    b += '    <polygon points="%s" fill="%s"/>\n' % (torn(38, 28, 128, 28, seed=len(q["name"]), amp=4, step=20), RED)
    b += ('    <text class="hv" x="52" y="48" font-size="11.5" letter-spacing="3.6" fill="%s">QUEST %s</text>\n'
          % (WHITE, q["idx"]))
    b += '    %s\n' % tag(1158, 28, q["status"][0], bg=q["status"][1],
                          fg=WHITE if q["status"][1] != BLACK3 else BONE)
    b += '  </g>\n'
    t, _ = p5text(40, 112, q["name"], 46, tl=q["tl"], ow=5)
    b += '  <g class="slam d2">%s</g>\n' % t
    b += ('  <text class="sn rise d3" x="%g" y="112" font-size="15" font-style="italic" fill="%s" '
          'fill-opacity=".55">%s</text>\n' % (40 + q["tl"] + 26, BONE, e(q["sub"])))
    b += ('  <line class="draw" x1="40" y1="132" x2="1158" y2="132" stroke="%s" stroke-opacity=".2" '
          'stroke-width="1.5"/>\n' % WHITE)
    for i, line in enumerate(q["desc"]):
        b += ('  <text class="sn rise d%d" x="40" y="%g" font-size="16" fill="%s" fill-opacity=".9">%s</text>\n'
              % (4 + i, 160 + i * 25, BONE, e(line)))
    b += ('  <text class="mn rise d6" x="40" y="208" font-size="10.5" letter-spacing="2.2" fill="%s">%s</text>\n'
          % (RED_HOT, e(q["metric"])))
    b += '  <g class="rise d7">%s</g>\n' % chiprow(40, 222, q["chips"])
    return doc(W, H, q["label"], defs, b)


for q in QUESTS:
    write(q["file"], make_quest(q))


# ── archive grid ───────────────────────────────────────────────────────────
ARCHIVE = [
 ("AOT PATHS", ["A temporal knowledge graph of", "the Attack on Titan manga."], "TYPESCRIPT"),
 ("YOLOV8 VISION", ["Turns a webcam into a real-time", "object detection system."], "PYTHON / OPENCV"),
 ("GESTURE PAINT", ["Draw, hover and erase in the air", "with nothing but your hands."], "PYTHON / MEDIAPIPE"),
 ("INVISIBILITY CLOAK", ["Real-time colour masking that", "makes you vanish on camera."], "PYTHON / OPENCV"),
 ("DAILY REPORTS", ["Automates lottery, shift and sales", "reporting for real-world ops."], "PYTHON / EXCEL"),
 ("UE5 PLUGINS", ["Blueprint HTTP nodes and a weighted", "character spawner for Unreal 5."], "C++ / UNREAL 5"),
 ("SENTIMENT CHATBOT", ["Reads the mood of a conversation", "while it is happening."], "REACT / FLASK"),
 ("DUAL-HERO SITE", ["A portfolio that switches between", "two comic-book identities."], "REACT / TAILWIND"),
]


def make_archive():
    W, H = 1200, 342
    CW, CH, GAP, M = 268, 122, 16, 40
    defs = GROUND + HALFTONE
    b = ground(W, H) + shell(W, H)
    for i, (name, lines, tg) in enumerate(ARCHIVE):
        cx = M + (i % 4) * (CW + GAP)
        cy = M + (i // 4) * (CH + GAP)
        b += '  <g class="rise d%d">\n' % (1 + (i % 4) + (i // 4) * 2)
        b += ('    <polygon points="%g,%g %g,%g %g,%g %g,%g" fill="%s" stroke="%s" '
              'stroke-opacity=".16"/>\n'
              % (cx + 12, cy, cx + CW, cy, cx + CW - 12, cy + CH, cx, cy + CH, BLACK3, WHITE))
        b += '    <polygon points="%g,%g %g,%g %g,%g %g,%g" fill="%s"/>\n' % (
            cx + 12, cy, cx + 44, cy, cx + 38, cy + 5, cx + 6, cy + 5, RED)
        tl = min(len(name) * 19 * 0.48, CW - 40)
        t, _ = p5text(cx + 18, cy + 42, name, 22, tl=tl, ow=4, skew=-7)
        b += '    %s\n' % t
        for j, ln in enumerate(lines):
            b += ('    <text class="sn" x="%g" y="%g" font-size="12.5" fill="%s" fill-opacity=".62">%s</text>\n'
                  % (cx + 18, cy + 68 + j * 18, BONE, e(ln)))
        b += ('    <text class="mn" x="%g" y="%g" font-size="9" letter-spacing="1.8" fill="%s">%s</text>\n'
              % (cx + 18, cy + CH - 14, RED_HOT, e(tg)))
        b += '  </g>\n'
    return doc(W, H, "The archive: AOT Paths, a temporal knowledge graph of the Attack on Titan manga, "
                     "TypeScript. YOLOv8 Vision, real-time object detection from a webcam, Python and "
                     "OpenCV. Gesture Paint, drawing in the air with your hands, Python and MediaPipe. "
                     "Invisibility Cloak, real-time colour masking, Python and OpenCV. Daily Reports, "
                     "automated lottery, shift and sales reporting, Python and Excel. UE5 Plugins, "
                     "Blueprint HTTP nodes and a weighted character spawner, C++ and Unreal 5. Sentiment "
                     "Chatbot, reads the mood of a conversation live, React and Flask. Dual-Hero Site, a "
                     "portfolio switching between two comic-book identities, React and Tailwind.",
               defs, b)


write("archive-grid.svg", make_archive())

# ── abilities ──────────────────────────────────────────────────────────────
ABILITIES = [
 ("LANGUAGES",      ["Python", "C++", "C#", "TypeScript", "JavaScript", "Java", "Dart", "SQL"]),
 ("FRONTEND",       ["React", "Next.js", "Tailwind CSS", "Flutter"]),
 ("BACKEND & DATA", ["Node.js", "FastAPI", ".NET", "PostgreSQL", "MongoDB", "Redis", "Prisma"]),
 ("AI & VISION",    ["PyTorch", "OpenCV", "YOLO", "scikit-learn", "ONNX", "NumPy", "Pandas"]),
 ("GAME DEV",       ["Unity", "Unreal Engine 5", "Photon Fusion", "Steamworks"]),
 ("OPS & TOOLS",    ["Docker", "Git", "GitHub Actions", "Git LFS", "Linux", "Bash", "Postman"]),
]


def make_abilities():
    W = 1200
    H = 46 + len(ABILITIES) * 58 + 26
    defs = GROUND + HALFTONE
    b = ground(W, H) + shell(W, H)
    for i, (lab, items) in enumerate(ABILITIES):
        y = 46 + i * 58
        if i:
            b += ('  <line x1="40" y1="%g" x2="1158" y2="%g" stroke="%s" stroke-opacity=".09"/>\n'
                  % (y - 17, y - 17, WHITE))
        b += '  <g class="rise d%d">\n' % (1 + i)
        w = len(lab) * 9 + 26
        b += ('    <polygon points="%g,%g %g,%g %g,%g %g,%g" fill="%s"/>\n'
              % (46, y, 40 + w, y, 34 + w, y + 23, 40, y + 23, RED))
        b += ('    <text class="hv" x="%g" y="%g" font-size="10.5" letter-spacing="2.2" '
              'text-anchor="middle" fill="%s">%s</text>\n' % (40 + w / 2, y + 16, WHITE, e(lab)))
        b += '    %s\n' % chiprow(216, y, items)
        b += '  </g>\n'
    return doc(W, H, "Abilities. Languages: Python, C++, C#, TypeScript, JavaScript, Java, Dart, SQL. "
                     "Frontend: React, Next.js, Tailwind CSS, Flutter. Backend and data: Node.js, "
                     "FastAPI, .NET, PostgreSQL, MongoDB, Redis, Prisma. AI and vision: PyTorch, OpenCV, "
                     "YOLO, scikit-learn, ONNX, NumPy, Pandas. Game development: Unity, Unreal Engine 5, "
                     "Photon Fusion, Steamworks. Ops and tools: Docker, Git, GitHub Actions, Git LFS, "
                     "Linux, Bash, Postman.", defs, b)


write("abilities-grid.svg", make_abilities())

# ── journey ────────────────────────────────────────────────────────────────
JOURNEY = [
 ("GAME DEVELOPER", "Dragon Drop LLC", "NOW", True, 196,
  "Developing and optimizing game applications: gameplay implementation, cross-platform "
  "compatibility and overall player experience."),
 ("HUMAN RESOURCES ASSISTANT", "Imprint Resources & Management LLC", "NOW", True, 318,
  "Supporting daily HR operations: employee communications and email documentation, records, "
  "workplace inspections and administrative tasks."),
 ("ICT INTERN", "NRBC Bank", "PAST", False, 136,
  "Built dynamic, database-driven web systems in production."),
 ("UNDERGRADUATE TA", "BRAC University", "PAST", False, 216,
  "Taught Discrete Mathematics and programming. Led sessions, mentored students, designed "
  "evaluations."),
 ("ASST. DIRECTOR, CREATIVE", "BRAC University Computer Club", "PAST", False, 310,
  "Branding, motion graphics and content for hackathons and developer conferences."),
]


def make_journey():
    W, ROW = 1200, 72
    H = 46 + len(JOURNEY) * ROW + 24
    defs = GROUND + HALFTONE
    b = ground(W, H) + shell(W, H)
    b += ('  <line class="draw" x1="70" y1="52" x2="70" y2="%d" stroke="%s" stroke-opacity=".28" '
          'stroke-width="2"/>\n' % (H - 52, WHITE))
    for i, (role, org, period, now, rl, detail) in enumerate(JOURNEY):
        y = 76 + i * ROW
        col = RED if now else BLACK3
        b += '  <g class="rise d%d">\n' % (1 + i)
        b += '    <polygon points="%s" fill="%s"/>\n' % (burst(70, y, 13, 6, 6, .3), RED if now else GREY)
        t, _ = p5text(104, y + 7, role, 22, tl=rl, ow=4, skew=-7)
        b += '    %s\n' % t
        b += ('    <text class="sn" x="%g" y="%g" font-size="15" font-style="italic" fill="%s" '
              'fill-opacity=".58">%s</text>\n' % (104 + rl + 20, y + 7, RED_HOT, e(org)))
        b += ('    <text class="sn" x="104" y="%g" font-size="14.5" fill="%s" fill-opacity=".6">%s</text>\n'
              % (y + 32, BONE, e(detail)))
        b += '    %s\n' % tag(1158, y - 14, period, bg=col, fg=WHITE if now else BONE)
        b += '  </g>\n'
    return doc(W, H, "Journey. Now: Game Developer at Dragon Drop LLC, developing and optimizing game "
                     "applications across gameplay implementation, cross-platform compatibility and "
                     "overall player experience; and Human Resources Assistant at Imprint Resources and "
                     "Management LLC, supporting daily HR operations, employee communications and email "
                     "documentation, records, workplace inspections and administrative tasks. Previously: "
                     "ICT Intern at NRBC Bank building dynamic database-driven web systems in production; "
                     "Undergraduate Teaching Assistant at BRAC University teaching Discrete Mathematics "
                     "and programming; and Assistant Director of the Creative Department at BRAC "
                     "University Computer Club handling branding, motion graphics and content for "
                     "hackathons and developer conferences.", defs, b)


write("journey-timeline.svg", make_journey())

# ── the portfolio, as the closing feature ──────────────────────────────────
def make_portfolio():
    W, H = 1200, 336
    defs = GROUND + HALFTONE
    b = ground(W, H) + shell(W, H)
    b += '  <g class="rise d1" opacity=".85">\n'
    b += '    <polygon class="flick" points="%s" fill="%s"/>\n' % (burst(1012, 168, 158, 104, 16, .1), RED_DEEP)
    b += '    <polygon points="%s" fill="%s"/>\n' % (burst(1012, 168, 122, 82, 16, .1), BLACK)
    b += '  </g>\n'
    b += '  <g class="rise d2">\n'
    pe, _ = p5text(1012, 150, "PLAY", 56, tl=118, anchor="middle", ow=5)
    b += '    %s\n' % pe
    pi, _ = p5text(1012, 206, "IT", 56, tl=58, anchor="middle", ow=5)
    b += '    %s\n' % pi
    b += '  </g>\n'
    b += '  <g class="rise d1">\n'
    b += '    <polygon points="%s" fill="%s"/>\n' % (torn(38, 34, 232, 30, seed=11, amp=4, step=22), RED)
    b += ('    <text class="hv" x="52" y="55" font-size="12" letter-spacing="4.2" fill="%s">'
          'THE PORTFOLIO</text>\n' % WHITE)
    b += '  </g>\n'
    t1, _ = p5text(42, 124, "METAPHOR:", 50, tl=256, ow=5)
    t2, _ = p5text(42, 180, "REFANTAZIO", 50, tl=292, ow=5)
    b += '  <g class="slam d2">%s</g>\n' % t1
    b += '  <g class="slam d3">%s</g>\n' % t2
    b += ('  <text class="sn rise d4" x="44" y="218" font-size="17" font-style="italic" fill="%s" '
          'fill-opacity=".72">A portfolio you play, not scroll.</text>\n' % BONE)
    b += ('  <text class="sn rise d5" x="44" y="250" font-size="15.5" fill="%s" fill-opacity=".72">'
          'Boot screen, quest log, archetypes and slab-wipe transitions. The game&#8217;s UI language</text>\n' % BONE)
    b += ('  <text class="sn rise d5" x="44" y="272" font-size="15.5" fill="%s" fill-opacity=".72">'
          'rebuilt in React to carry one developer&#8217;s journey.</text>\n' % BONE)
    b += '  <g class="rise d7">%s</g>\n' % chiprow(44, 292, ["React", "TypeScript", "Vite", "CSS"])
    return doc(W, H, "The portfolio: Metaphor ReFantazio. A portfolio you play, not scroll. Boot "
                     "screen, quest log, archetypes and slab-wipe transitions, the game's UI language "
                     "rebuilt in React to carry one developer's journey. React, TypeScript, Vite, CSS.",
               defs, b)


write("portfolio-feature.svg", make_portfolio())

# ── footer ─────────────────────────────────────────────────────────────────
def make_footer():
    W, H = 1200, 214
    defs = GROUND + HALFTONE
    b = ground(W, H)
    b += '  <polygon class="cut d1" points="482,-10 560,-10 458,224 380,224" fill="%s" fill-opacity=".2"/>\n' % RED
    b += '  <polygon class="cut d1" points="700,-10 740,-10 638,224 598,224" fill="%s" fill-opacity=".2"/>\n' % RED
    b += '  <g class="rise d2">\n'
    b += '    <polygon class="flick" points="%s" fill="%s"/>\n' % (burst(600, 62, 46, 28, 12, .26), RED)
    b += ('    <path d="M568 62c10-17 23-25 32-25s22 8 32 25c-10 17-23 25-32 25s-22-8-32-25z" fill="%s"/>\n' % BLACK)
    b += '    <circle cx="600" cy="62" r="9" fill="%s"/>\n' % WHITE
    b += '  </g>\n'
    t, _ = p5text(600, 142, "NO FINAL FORM.", 44, tl=346, anchor="middle", ow=5)
    b += '  <g class="slam d3">%s</g>\n' % t
    t2, _ = p5text(600, 186, "JUST THE NEXT LEVEL.", 44, tl=492, anchor="middle", ow=5)
    b += '  <g class="slam d4">%s</g>\n' % t2
    b += ('  <text class="mn rise d6" x="1158" y="204" font-size="10.5" letter-spacing="4" '
          'text-anchor="end" fill="%s">ARYAN ALAM &#183; ALLEXCEED360</text>\n' % GREY)
    return doc(W, H, "No final form. Just the next level. Aryan Alam, ALLEXCEED360.", defs, b)


write("footer-signature.svg", make_footer())

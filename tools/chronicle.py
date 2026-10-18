# -*- coding: utf-8 -*-
"""
Renders assets/chronicle-panel.svg from live GitHub data, in the same Persona 5
language as the rest of the profile. Run by .github/workflows/snake.yml daily so
the numbers never go stale.

    GH_TOKEN=... python -I tools/chronicle.py assets/chronicle-panel.svg
"""
import collections
import io
import json
import os
import subprocess
import sys

os.environ["PERSONA_NO_EMIT"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import persona as P  # noqa: E402  (design helpers: palette, type, shapes)

USER = os.environ.get("PROFILE_USER", "ALLEXCEED360")
DEST = sys.argv[1] if len(sys.argv) > 1 else "assets/chronicle-panel.svg"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def gh(args):
    p = subprocess.run(["gh"] + args, capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode()[:400])
    return json.loads(p.stdout.decode() or "{}")


def pretty(datestr):
    y, m, d = datestr.split("-")
    return "%d %s %s" % (int(d), MONTHS[int(m) - 1].upper(), y)


def commas(n):
    return "{:,}".format(n)


# ── data ───────────────────────────────────────────────────────────────────
def contributions():
    q = ("query($login:String!){user(login:$login){contributionsCollection"
         "{contributionCalendar{totalContributions weeks{contributionDays"
         "{date contributionCount}}}}}}")
    d = gh(["api", "graphql", "-f", "query=" + q, "-F", "login=" + USER])
    cal = d["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [x for w in cal["weeks"] for x in w["contributionDays"]]
    best = max(days, key=lambda x: x["contributionCount"])
    run = longest = 0
    for x in days:
        run = run + 1 if x["contributionCount"] > 0 else 0
        longest = max(longest, run)
    return dict(
        total=cal["totalContributions"],
        span=len(days),
        active=sum(1 for x in days if x["contributionCount"] > 0),
        longest=longest,
        best=best["contributionCount"],
        best_day=best["date"],
        first=days[0]["date"],
        last=days[-1]["date"],
    )


def languages():
    repos = gh(["api", "users/%s/repos?per_page=100&type=owner" % USER, "--paginate"])
    agg = collections.Counter()
    for r in repos:
        if r.get("fork"):
            continue
        try:
            agg.update(gh(["api", "repos/%s/%s/languages" % (USER, r["name"])]))
        except RuntimeError:
            continue
    total = sum(agg.values()) or 1
    top = agg.most_common(6)
    shown = sum(v for _, v in top)
    rows = [(k, 100.0 * v / total) for k, v in top]
    if total - shown > 0:
        rows.append(("Other", 100.0 * (total - shown) / total))
    return rows


# ── render ─────────────────────────────────────────────────────────────────
RAMP = None  # filled at render time from the shared palette


def render(stats, langs):
    W, H = 1200, 322
    # hot red down to muted bone: the tail stays readable on black, unlike a
    # straight fade to near-black.
    ramp = ["#ff2b50", "#e4002b", "#b00022", "#7a1526", "#9b6f77", "#7a7077", "#5d5760"]
    defs = P.GROUND + P.HALFTONE
    b = P.ground(W, H) + P.shell(W, H)

    # header
    b += '  <g class="rise d1">\n'
    b += '    <polygon points="%s" fill="%s"/>\n' % (
        P.torn(38, 32, 186, 30, seed=13, amp=4, step=22), P.RED)
    b += ('    <text class="hv" x="52" y="53" font-size="12" letter-spacing="4.2" fill="%s">'
          'COMMIT LOG</text>\n' % P.WHITE)
    b += ('    <text class="mn" x="1158" y="52" font-size="10.5" letter-spacing="3" '
          'text-anchor="end" fill="%s">REAL ACTIVITY &#183; RE-RENDERED DAILY</text>\n' % P.GREY)
    b += '  </g>\n'

    # four stat blocks
    blocks = [
        (commas(stats["total"]), "CONTRIBUTIONS",
         "%s TO %s" % (pretty(stats["first"])[-8:], pretty(stats["last"])[-8:])),
        (commas(stats["active"]), "ACTIVE DAYS", "OF %d DAYS" % stats["span"]),
        (commas(stats["longest"]), "LONGEST STREAK", "CONSECUTIVE DAYS"),
        (commas(stats["best"]), "BUSIEST DAY", pretty(stats["best_day"])),
    ]
    for i, (num, lab, sub) in enumerate(blocks):
        x = 46 + i * 282
        if i:
            b += ('  <line x1="%d" y1="86" x2="%d" y2="186" stroke="%s" stroke-opacity=".12"/>\n'
                  % (x - 26, x - 26, P.WHITE))
        b += '  <g class="slam d%d">\n' % (2 + i)
        t, _ = P.p5text(x, 146, num, 52, tl=min(len(num) * 27, 214), ow=5)
        b += '    %s\n' % t
        b += '  </g>\n'
        b += '  <g class="rise d%d">\n' % (3 + i)
        b += ('    <text class="hv" x="%d" y="172" font-size="11" letter-spacing="2.4" fill="%s">%s</text>\n'
              % (x, P.RED_HOT, P.e(lab)))
        b += ('    <text class="mn" x="%d" y="190" font-size="10" letter-spacing="1.8" fill="%s">%s</text>\n'
              % (x, P.GREY, P.e(sub)))
        b += '  </g>\n'

    # language bar
    b += '  <line x1="46" y1="216" x2="1154" y2="216" stroke="%s" stroke-opacity=".12"/>\n' % P.WHITE
    b += ('  <text class="mn rise d6" x="46" y="242" font-size="10.5" letter-spacing="3" fill="%s">'
          'LANGUAGES BY VOLUME</text>\n' % P.GREY)
    bw, bx, by = 1108, 46, 252
    b += '  <g class="rise d7">\n'
    cx = float(bx)
    for i, (name, pct) in enumerate(langs):
        seg = max(6.0, bw * pct / 100.0)
        if cx + seg > bx + bw:
            seg = bx + bw - cx
        b += ('    <polygon points="%.1f,%g %.1f,%g %.1f,%g %.1f,%g" fill="%s"/>\n'
              % (cx + 5, by, cx + seg, by, cx + seg - 5, by + 20, cx, by + 20,
                 ramp[min(i, len(ramp) - 1)]))
        cx += seg + 2
    b += '  </g>\n'

    # legend
    lx = 46
    b += '  <g class="rise d8">\n'
    for i, (name, pct) in enumerate(langs):
        txt = "%s %.1f%%" % (name, pct)
        b += ('    <polygon points="%g,%g %g,%g %g,%g %g,%g" fill="%s"/>\n'
              % (lx + 2, 288, lx + 11, 288, lx + 9, 298, lx, 298,
                 ramp[min(i, len(ramp) - 1)]))
        b += ('    <text class="mn" x="%g" y="298" font-size="10.5" letter-spacing=".8" fill="%s" '
              'fill-opacity=".8">%s</text>\n' % (lx + 18, P.BONE, P.e(txt)))
        lx += 22 + len(txt) * 6.5 + 18
    b += '  </g>\n'

    label = ("Commit log, re-rendered daily. %s contributions between %s and %s, across %d active "
             "days of %d. Longest streak %d consecutive days. Busiest day %s contributions on %s. "
             "Languages by volume: %s."
             % (commas(stats["total"]), pretty(stats["first"]), pretty(stats["last"]),
                stats["active"], stats["span"], stats["longest"], commas(stats["best"]),
                pretty(stats["best_day"]),
                ", ".join("%s %.1f percent" % (n, p) for n, p in langs)))
    return P.doc(W, H, label, defs, b)


def main():
    stats = contributions()
    langs = languages()
    svg = render(stats, langs)
    d = os.path.dirname(DEST)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    io.open(DEST, "w", encoding="utf-8").write(svg)
    print("%s  %d bytes  (%s contributions, %d active, streak %d)"
          % (DEST, len(svg.encode("utf-8")), commas(stats["total"]),
             stats["active"], stats["longest"]))


if __name__ == "__main__":
    main()

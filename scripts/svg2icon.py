#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robust .icon -> .svg converter
- รองรับ:
  CANVAS_DIMENSIONS,W[,H]
  NEW_PATH / CLOSE
  MOVE_TO x y / R_MOVE_TO dx dy
  LINE_TO x y / R_LINE_TO dx dy
  HLINE_TO x / VLINE_TO y
  R_H_LINE_TO dx / R_V_LINE_TO dy
  CUBIC_TO x1 y1 x2 y2 x y / CUBIC_TO_SHORTHAND x2 y2 x y
  R_CUBIC_TO dx1 dy1 dx2 dy2 dx dy
  R_QUADRATIC_TO dx1 dy1 dx dy
  ARC_TO rx ry rot laf sf x y / R_ARC_TO rx ry rot laf sf dx dy
  CIRCLE cx cy r
  FILL color(optional) / STROKE color(optional) / STROKE_WIDTH w(optional)
- ข้ามคอมเมนต์ (# หรือ //) และบรรทัดว่าง
- อ่านตัวเลขที่ลงท้ายด้วย 'f' ได้
"""

import sys, re, math
from pathlib import Path

NUM = r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?f?'
TOKEN = re.compile(r'\s*,\s*|\s+')
NUMCLEAN = re.compile(r'f$', re.I)

def f(v):  # to float
    return float(NUMCLEAN.sub('', v))

# format numbers for crisp SVG output: strip .0, round to 5 decimals (higher precision to avoid jagged paths)
_def_epsilon = 1e-9

def fmt(v, prec: int = 5):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return str(v)
    if abs(x - round(x)) < _def_epsilon:
        return str(int(round(x)))
    s = f"{x:.{prec}f}"
    s = s.rstrip('0').rstrip('.')
    return s

def parse_line(line):
    # remove comments
    line = re.split(r'(?://|#)', line, 1)[0].strip()
    if not line:
        return None, []
    parts = [p for p in re.split(TOKEN, line) if p]
    cmd = parts[0].upper()
    args = parts[1:]
    return cmd, args

def icon_to_svg(lines):
    width = height = None
    paths = []               # list of dicts {d, fill, stroke, stroke_width, fill_rule, fill_opacity}
    cur = {"d": [], "fill": "none", "stroke": "currentColor", "stroke_width": "1", "fill_rule": None, "fill_opacity": None}
    cx = cy = 0.0            # current point (for relative ops)
    started = False
    last_cubic_ctrl2 = None  # absolute coordinates of the last cubic's second control point
    last_cmd = None

    def ensure_path_started():
        nonlocal started
        if not started:
            cur["d"].append("M0 0")
            started = True

    for idx, raw in enumerate(lines, 1):
        cmd, args = parse_line(raw)
        if not cmd:
            continue
        try:
            if cmd == "CANVAS_DIMENSIONS":
                width = f(args[0])
                height = f(args[1]) if len(args) > 1 else width

            elif cmd == "NEW_PATH":
                # push previous
                if cur["d"]:
                    paths.append(cur.copy())
                cur = {"d": [], "fill": "none", "stroke": "currentColor", "stroke_width": "1", "fill_rule": None, "fill_opacity": None}
                started = False

            elif cmd == "CLOSE":
                if started:
                    cur["d"].append("Z")
                last_cubic_ctrl2 = None
                last_cmd = "Z"

            elif cmd == "MOVE_TO":
                x, y = f(args[0]), f(args[1])
                cur["d"].append(f"M{fmt(x)} {fmt(y)}")
                cx, cy = x, y
                started = True
                last_cubic_ctrl2 = None
                last_cmd = "M"

            elif cmd == "R_MOVE_TO":
                dx, dy = f(args[0]), f(args[1])
                cx, cy = cx + dx, cy + dy
                cur["d"].append(f"m{fmt(dx)} {fmt(dy)}")
                started = True
                last_cubic_ctrl2 = None
                last_cmd = "m"

            elif cmd == "LINE_TO":
                x, y = f(args[0]), f(args[1])
                cur["d"].append(f"L{fmt(x)} {fmt(y)}")
                cx, cy = x, y
                started = True
                last_cubic_ctrl2 = None
                last_cmd = "L"

            elif cmd == "R_LINE_TO":
                ensure_path_started()
                dx, dy = f(args[0]), f(args[1])
                cur["d"].append(f"l{fmt(dx)} {fmt(dy)}")
                cx, cy = cx + dx, cy + dy
                last_cubic_ctrl2 = None
                last_cmd = "l"

            elif cmd == "HLINE_TO":
                x = f(args[0])
                cur["d"].append(f"H{fmt(x)}")
                cx = x
                started = True
                last_cubic_ctrl2 = None
                last_cmd = "H"

            elif cmd == "VLINE_TO":
                y = f(args[0])
                cur["d"].append(f"V{fmt(y)}")
                cy = y
                started = True
                last_cubic_ctrl2 = None
                last_cmd = "V"

            elif cmd == "R_CUBIC_TO":
                ensure_path_started()
                dx1, dy1, dx2, dy2, dx, dy = map(f, args[:6])
                cur["d"].append(f"c{fmt(dx1)} {fmt(dy1)} {fmt(dx2)} {fmt(dy2)} {fmt(dx)} {fmt(dy)}")
                # set last control2 as absolute before updating cx, cy
                last_cubic_ctrl2 = (cx + dx2, cy + dy2)
                cx, cy = cx + dx, cy + dy
                last_cmd = "c"

            elif cmd == "R_QUADRATIC_TO":
                ensure_path_started()
                dx1, dy1, dx, dy = map(f, args[:4])
                cur["d"].append(f"q{fmt(dx1)} {fmt(dy1)} {fmt(dx)} {fmt(dy)}")
                cx, cy = cx + dx, cy + dy
                last_cubic_ctrl2 = None
                last_cmd = "q"

            elif cmd == "R_ARC_TO":
                # Relative elliptical arc: rx ry xAxisRotation largeArcFlag sweepFlag dx dy
                ensure_path_started()
                rx, ry, rot, laf, sf, dx, dy = map(f, args[:7])
                laf_s = "1" if int(round(laf)) != 0 else "0"
                sf_s = "1" if int(round(sf)) != 0 else "0"
                cur["d"].append(f"a{fmt(rx)} {fmt(ry)} {fmt(rot)} {laf_s} {sf_s} {fmt(dx)} {fmt(dy)}")
                cx, cy = cx + dx, cy + dy
                last_cubic_ctrl2 = None
                last_cmd = "a"

            elif cmd == "CIRCLE":
                ccx, ccy, r = map(f, args[:3])
                # draw as two arcs; start with absolute move to circle rightmost point
                cur["d"].append(f"M{fmt(ccx + r)} {fmt(ccy)}")
                cur["d"].append(f"A{fmt(r)} {fmt(r)} 0 1 0 {fmt(ccx - r)} {fmt(ccy)}")
                cur["d"].append(f"A{fmt(r)} {fmt(r)} 0 1 0 {fmt(ccx + r)} {fmt(ccy)}")
                cx, cy = ccx + r, ccy
                started = True
                last_cubic_ctrl2 = None
                last_cmd = "A"

            elif cmd == "FILL":
                cur["fill"] = args[0] if args else "currentColor"

            elif cmd == "STROKE":
                cur["stroke"] = args[0] if args else "none"

            elif cmd == "STROKE_WIDTH":
                cur["stroke_width"] = args[0] if args else "1"

            elif cmd == "FILL_RULE_NONZERO":
                cur["fill_rule"] = "nonzero"

            elif cmd == "FILL_RULE_EVENODD":
                cur["fill_rule"] = "evenodd"

            elif cmd == "PATH_COLOR_ARGB":
                # PATH_COLOR_ARGB, A, R, G, B where each is 0x.. hex (or decimal). Sets fill color for current path.
                def parse_argb_component(v):
                    v = v.strip()
                    if v.lower().startswith("0x"):
                        return int(v, 16)
                    # fall back to float->int for decimal-like inputs
                    try:
                        return int(round(float(NUMCLEAN.sub('', v))))
                    except Exception:
                        raise ValueError(f"Invalid ARGB component: {v}")
                a = parse_argb_component(args[0]) if len(args) > 0 else 255
                r = parse_argb_component(args[1]) if len(args) > 1 else 0
                g = parse_argb_component(args[2]) if len(args) > 2 else 0
                b = parse_argb_component(args[3]) if len(args) > 3 else 0
                r = max(0, min(255, r)); g = max(0, min(255, g)); b = max(0, min(255, b)); a = max(0, min(255, a))
                cur["fill"] = f"#{r:02X}{g:02X}{b:02X}"
                cur["stroke"] = "none"
                cur["fill_opacity"] = None if a == 255 else fmt(a/255.0, 3)
                # color changes do not affect cubic reflection state

            elif cmd == "ARC_TO":
                # Absolute elliptical arc: rx ry xAxisRotation largeArcFlag sweepFlag x y
                ensure_path_started()
                rx, ry, rot, laf, sf, x, y = map(f, args[:7])
                laf_s = "1" if int(round(laf)) != 0 else "0"
                sf_s = "1" if int(round(sf)) != 0 else "0"
                cur["d"].append(f"A{fmt(rx)} {fmt(ry)} {fmt(rot)} {laf_s} {sf_s} {fmt(x)} {fmt(y)}")
                cx, cy = x, y
                last_cubic_ctrl2 = None
                last_cmd = "A"

            elif cmd == "R_H_LINE_TO":
                ensure_path_started()
                dx = f(args[0])
                cur["d"].append(f"h{fmt(dx)}")
                cx = cx + dx
                last_cubic_ctrl2 = None
                last_cmd = "h"

            elif cmd == "R_V_LINE_TO":
                ensure_path_started()
                dy = f(args[0])
                cur["d"].append(f"v{fmt(dy)}")
                cy = cy + dy
                last_cubic_ctrl2 = None
                last_cmd = "v"

            elif cmd == "CUBIC_TO":
                # Absolute cubic Bezier: x1 y1 x2 y2 x y
                ensure_path_started()
                x1, y1, x2, y2, x, y = map(f, args[:6])
                cur["d"].append(f"C{fmt(x1)} {fmt(y1)} {fmt(x2)} {fmt(y2)} {fmt(x)} {fmt(y)}")
                cx, cy = x, y
                last_cubic_ctrl2 = (x2, y2)
                last_cmd = "C"

            elif cmd == "CUBIC_TO_SHORTHAND":
                # Absolute shorthand cubic (S): x2 y2 x y
                ensure_path_started()
                x2, y2, x, y = map(f, args[:4])
                if last_cmd in ("C", "c", "S", "s") and last_cubic_ctrl2 is not None:
                    x1 = 2 * cx - last_cubic_ctrl2[0]
                    y1 = 2 * cy - last_cubic_ctrl2[1]
                else:
                    x1, y1 = cx, cy
                cur["d"].append(f"C{fmt(x1)} {fmt(y1)} {fmt(x2)} {fmt(y2)} {fmt(x)} {fmt(y)}")
                cx, cy = x, y
                last_cubic_ctrl2 = (x2, y2)
                last_cmd = "S"

            else:
                # unrecognized -> ignore softly
                pass

        except Exception as e:
            raise RuntimeError(f"Parse error at line {idx}: '{raw.strip()}': {e}") from e

    # push last
    if cur["d"]:
        paths.append(cur)

    if not width or not height:
        # default square 24
        width = width or 24
        height = height or width

    # build svg
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(width)}" height="{fmt(height)}" viewBox="0 0 {fmt(width)} {fmt(height)}" shape-rendering="crispEdges">'
    ]
    for p in paths:
        d = " ".join(p["d"])
        fill_rule_attr = f' fill-rule="{p["fill_rule"]}"' if p.get("fill_rule") else ""
        fill_opacity_attr = f' fill-opacity="{p["fill_opacity"]}"' if p.get("fill_opacity") not in (None, "") else ""
        # Auto-thin default stroke for small icons to improve visual lightness without altering explicit STROKE_WIDTH
        sw = p.get("stroke_width", "1")
        try:
            small = float(width) <= 16 and float(height) <= 16
        except Exception:
            small = False
        sw_out = "0.75" if sw == "1" and small else sw
        parts.append(
            f'  <path d="{d}" fill="{p["fill"]}" stroke="{p["stroke"]}" stroke-width="{sw_out}" vector-effect="non-scaling-stroke" stroke-linecap="round" stroke-linejoin="round"{fill_rule_attr}{fill_opacity_attr}/>'
        )
    parts.append("</svg>")
    return "\n".join(parts)

def svg_to_icon(svg_text: str) -> str:
    import xml.etree.ElementTree as ET
    # Parse SVG
    root = ET.fromstring(svg_text)
    # handle namespaces
    tag = root.tag
    if tag.endswith('svg'):
        pass
    width = root.get('width') or ''
    height = root.get('height') or ''
    # helper to parse dimension strings like '256', '256px', '10.5em', '100%'
    def _parse_dim(val: str):
        if not val:
            return None
        s = val.strip()
        # percentages are ambiguous without viewBox; treat as None to fall back to viewBox
        if s.endswith('%'):
            return None
        # strip common units
        m = re.match(r'^([+-]?[0-9]*\.?[0-9]+)(px|pt|pc|mm|cm|in)?$', s, re.I)
        if m:
            try:
                return float(m.group(1))
            except Exception:
                return None
        # last resort try float on the raw string (may work if unrecognized unit isn't present)
        try:
            return float(s)
        except Exception:
            return None
    w = _parse_dim(width)
    h = _parse_dim(height)
    # If dimensions missing or unparseable, try viewBox
    vb = root.get('viewBox')
    if (w is None or h is None) and vb:
        parts = vb.replace(',', ' ').split()
        if len(parts) == 4:
            try:
                vw = float(parts[2]); vh = float(parts[3])
                if w is None:
                    w = vw
                if h is None:
                    h = vh
            except Exception:
                pass
    # Fallback defaults if still None
    if w is None:
        w = 24.0
    if h is None:
        h = w
    # helpers
    def numtok(v):
        try:
            x = float(v)
        except Exception:
            return str(v)
        if abs(x - round(x)) < 1e-9:
            return str(int(round(x)))
        s = f"{x:.2f}".rstrip('0').rstrip('.')
        if '.' not in s:
            return s
        return s + 'f'
    def color_to_argb(cval, opacity_attr=None):
        a = 255
        if opacity_attr:
            try:
                a = max(0, min(255, int(round(float(opacity_attr) * 255))))
            except Exception:
                pass
        if not cval or cval.lower() == 'none':
            return None
        c = cval.strip()
        if c.startswith('#') and len(c) in (7, 4):
            if len(c) == 4:
                r = int(c[1]*2, 16); g = int(c[2]*2, 16); b = int(c[3]*2, 16)
            else:
                r = int(c[1:3], 16); g = int(c[3:5], 16); b = int(c[5:7], 16)
            return a, r, g, b
        # rgb(r,g,b)
        m = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", c, re.I)
        if m:
            r, g, b = map(int, m.groups())
            return a, r, g, b
        # rgba(r,g,b,a)
        m = re.match(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)", c, re.I)
        if m:
            r, g, b = map(int, m.groups()[:3])
            try:
                a = max(0, min(255, int(round(float(m.group(4)) * 255))))
            except Exception:
                a = 255
            return a, r, g, b
        return None
    # Path data parser
    def parse_path_d(dstr):
        # returns list of (cmd, args_list) where args_list is list of float strings as in SVG
        tokens = []
        i = 0
        s = dstr.strip()
        num_re = re.compile(r"^[+-]?(?:\d*\.\d+|\d+)(?:[eE][+-]?\d+)?")
        while i < len(s):
            ch = s[i]
            if ch.isalpha():
                tokens.append(ch)
                i += 1
            elif ch in ', \t\r\n':
                i += 1
            else:
                m = num_re.match(s[i:])
                if not m:
                    i += 1
                    continue
                tokens.append(m.group(0))
                i += len(m.group(0))
        # map of param counts
        param_counts = {
            'M': 2, 'm': 2,
            'L': 2, 'l': 2,
            'H': 1, 'h': 1,
            'V': 1, 'v': 1,
            'C': 6, 'c': 6,
            'S': 4, 's': 4,
            'Q': 4, 'q': 4,
            'A': 7, 'a': 7,
            'Z': 0, 'z': 0,
        }
        out = []
        i = 0
        cur_cmd = None
        while i < len(tokens):
            t = tokens[i]
            if re.match(r'^[A-Za-z]$', t):
                cur_cmd = t
                i += 1
                if param_counts[cur_cmd] == 0:
                    out.append((cur_cmd, []))
                continue
            if cur_cmd is None:
                break
            n = param_counts[cur_cmd]
            if i + n > len(tokens):
                break
            args = tokens[i:i+n]
            out.append((cur_cmd, args))
            i += n
            # commands like M/m can be followed by multiple pairs implying L/l
            if cur_cmd in ('M','m'):
                cur_cmd = 'L' if cur_cmd == 'M' else 'l'
        return out
    # Build .icon text
    lines = []
    lines.append(f"CANVAS_DIMENSIONS, {numtok(w)}, {numtok(h)},")
    # iterate path elements
    # handle namespaces in tag names
    def localname(t):
        return t.split('}',1)[-1]
    first = True
    for elem in root.iter():
        if localname(elem.tag) != 'path':
            continue
        if not first:
            lines.append("NEW_PATH,")
        first = False
        fill = elem.get('fill')
        fill_opacity = elem.get('fill-opacity')
        argb = color_to_argb(fill, fill_opacity)
        if argb:
            a,r,g,b = argb
            lines.append(f"PATH_COLOR_ARGB, 0x{a:02X}, 0x{r:02X}, 0x{g:02X}, 0x{b:02X},")
        d = elem.get('d') or ''
        for cmd, args in parse_path_d(d):
            if cmd == 'M':
                lines.append(f"MOVE_TO, {numtok(args[0])}, {numtok(args[1])},")
            elif cmd == 'L':
                lines.append(f"LINE_TO, {numtok(args[0])}, {numtok(args[1])},")
            elif cmd == 'H':
                lines.append(f"HLINE_TO, {numtok(args[0])},")
            elif cmd == 'V':
                lines.append(f"VLINE_TO, {numtok(args[0])},")
            elif cmd == 'C':
                a = [numtok(x) for x in args]
                lines.append(f"CUBIC_TO, {a[0]}, {a[1]}, {a[2]}, {a[3]}, {a[4]}, {a[5]},")
            elif cmd == 'S':
                a = [numtok(x) for x in args]
                lines.append(f"CUBIC_TO_SHORTHAND, {a[0]}, {a[1]}, {a[2]}, {a[3]},")
            elif cmd == 'A':
                a = [numtok(x) for x in args]
                # flags should be integers
                laf = '1' if float(args[3]) != 0 else '0'
                sf = '1' if float(args[4]) != 0 else '0'
                lines.append(f"ARC_TO, {a[0]}, {a[1]}, {a[2]}, {laf}, {sf}, {a[5]}, {a[6]},")
            elif cmd == 'm':
                lines.append(f"R_MOVE_TO, {numtok(args[0])}, {numtok(args[1])},")
            elif cmd == 'l':
                lines.append(f"R_LINE_TO, {numtok(args[0])}, {numtok(args[1])},")
            elif cmd == 'h':
                lines.append(f"R_H_LINE_TO, {numtok(args[0])},")
            elif cmd == 'v':
                lines.append(f"R_V_LINE_TO, {numtok(args[0])},")
            elif cmd == 'c':
                a = [numtok(x) for x in args]
                lines.append(f"R_CUBIC_TO, {a[0]}, {a[1]}, {a[2]}, {a[3]}, {a[4]}, {a[5]},")
            elif cmd == 's':
                a = [numtok(x) for x in args]
                # no direct relative shorthand; convert to absolute shorthand not possible without state; skip
                # Fallback: treat as relative cubic with first control as 0,0 (approximate)
                lines.append(f"R_CUBIC_TO, {a[0]}, {a[1]}, {a[0]}, {a[1]}, {a[2]}, {a[3]},")
            elif cmd == 'a':
                a = [numtok(x) for x in args]
                laf = '1' if float(args[3]) != 0 else '0'
                sf = '1' if float(args[4]) != 0 else '0'
                lines.append(f"R_ARC_TO, {a[0]}, {a[1]}, {a[2]}, {laf}, {sf}, {a[5]}, {a[6]},")
            elif cmd in ('Z','z'):
                lines.append("CLOSE,")
        # Done one path
    return "\n".join(lines) + ("\n" if lines else "")


def main():
    if len(sys.argv) != 3:
        print("Usage: svg2icon.py input.icon output.svg OR svg2icon.py input.svg output.icon", file=sys.stderr)
        sys.exit(2)
    inp, outp = Path(sys.argv[1]), Path(sys.argv[2])
    if inp.suffix.lower() == '.icon' and outp.suffix.lower() == '.svg':
        svg = icon_to_svg(inp.read_text(encoding='utf-8').splitlines())
        outp.write_text(svg, encoding='utf-8')
    elif inp.suffix.lower() == '.svg' and outp.suffix.lower() == '.icon':
        icon_txt = svg_to_icon(inp.read_text(encoding='utf-8'))
        outp.write_text(icon_txt, encoding='utf-8')
    else:
        print("Unrecognized conversion. Expected .icon->.svg or .svg->.icon", file=sys.stderr)
        sys.exit(2)
    print(f"✅ Wrote {outp}")

if __name__ == "__main__":
    main()
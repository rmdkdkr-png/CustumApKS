"""palette variant formulas (12-bit 0x0BGR) + ROM-overlay builders"""
import rs
def split(c): return c & 15, (c >> 4) & 15, (c >> 8) & 15
def join(r, g, b):
    cl = lambda v: max(0, min(15, int(round(v))))
    return cl(r) | cl(g) << 4 | cl(b) << 8
def lum(r, g, b): return 0.3 * r + 0.59 * g + 0.11 * b
def night(c):
    r, g, b = split(c); l = lum(r, g, b)
    return join(r * 0.35 + l * 0.05, g * 0.45 + l * 0.08, b * 0.55 + l * 0.25 + 2.2)
def sunset(c):
    r, g, b = split(c); l = lum(r, g, b)
    return join(r * 0.75 + l * 0.35 + 1.5, g * 0.65 + l * 0.12, b * 0.35 + l * 0.05)
def snow(c):
    r, g, b = split(c); l = lum(r, g, b)
    m = 0.35
    return join((r * m + l * (1 - m)) * 0.75 + 4.0, (g * m + l * (1 - m)) * 0.75 + 4.2, (b * m + l * (1 - m)) * 0.75 + 5.0)
def bloodmoon(c):
    r, g, b = split(c); l = lum(r, g, b)
    return join(l * 1.05 + r * 0.15 + 1.0, l * 0.30, l * 0.28 + b * 0.05)
def marker(c):   # gating test: obvious magenta-ish shift, keeps detectability
    r, g, b = split(c)
    return join(15 - (15 - r) // 2, g // 3, 15 - (15 - b) // 2)
FN = dict(night=night, sunset=sunset, snow=snow, bloodmoon=bloodmoon, marker=marker)
def lut(fn): return [fn(c) for c in range(4096)]
def overlay_for_entries(entries, fn):
    """list of (cart_addr, bytes): tinted palettes (colours 1..3; colour 0 kept) + tinted bg colour in each palset list header"""
    out = []; done = set()
    for e in entries:
        st = rs.stage(e)
        for v in st['palidx']:
            a = rs.PALTAB + v
            if a in done: continue
            done.add(a)
            cols = [rs.r16(a + 2 * j) for j in range(4)]
            nc = [cols[0]] + [fn(c & 0xFFF) | (c & 0xF000) for c in cols[1:]]
            out.append((a, b''.join(bytes((x & 0xFF, x >> 8)) for x in nc)))
        bga = st['psaddr'] - 2; bg = rs.r16(bga)
        out.append((bga, bytes(((fn(bg & 0xFFF) | (bg & 0xF000)) & 0xFF, (fn(bg & 0xFFF) | (bg & 0xF000)) >> 8))))
    return out
BOUT_ENTRIES = {0: (0, 1), 1: (6, 7), 2: (2, 3), 3: (5,), 4: (4,), 5: (10,), 6: (12,), 7: (13,)}

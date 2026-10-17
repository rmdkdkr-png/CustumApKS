"""Pose record parser (ROM): record = layout[(flags, cell)] (last has flags&0x80) + u32 bankref + u16 tile index * N.
Bank table at CPU 0x2ecbd2 (u32 per character 0..14, plus extras)."""
import os, struct, collections
BANKTAB = 0x2ecbd2
def load(path=None):
    return open(path or os.environ['ROM_KO'], 'rb').read()
def u32(rom, a): return struct.unpack_from('<I', rom, a - 0x200000)[0]
def u16(rom, a): return struct.unpack_from('<H', rom, a - 0x200000)[0]
def banks(rom):
    out = []
    for k in range(19): out.append(u32(rom, BANKTAB + 4 * k))
    return out
def valid_cell(f, c):
    return (c & 15) <= 7 and (c >> 4) <= 7
def find_refs(rom, k):
    pat = struct.pack('<I', BANKTAB + 4 * k)
    out = []; s = 0
    while True:
        o = rom.find(pat, s)
        if o < 0: break
        out.append(o + 0x200000); s = o + 1
    return out
def back_walk(rom, r):
    """layout entries before ref r: last at r-2 has 0x80; walk back while valid & no 0x80"""
    o = r - 0x200000
    f, c = rom[o - 2], rom[o - 1]
    if not (f & 0x80) or not valid_cell(f, c): return None
    n = 1
    while n < 40:
        f, c = rom[o - 2 * (n + 1)], rom[o - 2 * (n + 1) + 1]
        if (f & 0x80) or not valid_cell(f, c): break
        n += 1
    return n
def parse(rom, k):
    """-> list of records dict(ref, start, layout=[(f,cell)], idx=[...])"""
    refs = find_refs(rom, k); recs = []
    prev_end = None
    nb = (banks(rom)[k + 1] - banks(rom)[k]) // 16 if k < 18 else 1
    for r in refs:
        n = None
        if prev_end is not None and 0 < r - prev_end <= 80 and (r - prev_end) % 2 == 0:
            n = (r - prev_end) // 2
            o = prev_end - 0x200000
            ents = [(rom[o + 2*j], rom[o + 2*j + 1]) for j in range(n)]
            if not (ents[-1][0] & 0x80) or any(e[0] & 0x80 for e in ents[:-1]) or not all(valid_cell(*e) for e in ents): n = None
        if n is None: n = back_walk(rom, r)
        if n is None: continue
        start = r - 2 * n; o = start - 0x200000
        lay = [(rom[o + 2*j], rom[o + 2*j + 1]) for j in range(n)]
        idx = [u16(rom, r + 4 + 2*j) for j in range(n)]
        if max(idx) >= nb: prev_end = None; continue
        recs.append(dict(ref=r, start=start, layout=lay, idx=idx))
        prev_end = r + 4 + 2 * n
    return recs
if __name__ == '__main__':
    import sys
    rom = load()
    B = banks(rom)
    tot = 0
    for k in range(15):
        recs = parse(rom, k)
        used = set(i for rc in recs for i in rc['idx'])
        nb = (B[k + 1] - B[k]) // 16
        flags = collections.Counter(f & 0x7F for rc in recs for f, c in rc['layout'])
        ns = [len(rc['idx']) for rc in recs]
        print('char %2d bank %06x tiles %4d  poses %4d  tiles referenced %4d (%.0f%%)  sprites/pose avg %.1f max %d  flags %s' % (
            k, B[k], nb, len(recs), len(used), 100.0 * len(used) / nb, sum(ns) / max(1, len(ns)), max(ns or [0]), dict(flags)))
        tot += nb
    print('total tiles', tot)

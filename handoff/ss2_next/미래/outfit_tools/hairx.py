"""offline pose-level pixel processing -> per-tile replacement table.
'hair' transform: thick regions of the dark index (3) (3x3 core + 1px geodesic dilation) -> index 2 (thin outlines stay 3)."""
import poses, posrender, collections
def pose_pixels(rom, ch, rec):
    """-> dict (x,y) -> (v, idx, tile-local (r,c) in ROM orientation)"""
    bank = poses.banks(rom)[ch]; out = {}
    for (f, cell), idx in zip(rec['layout'], rec['idx']):
        r0, c0 = (cell >> 4) * 8, (cell & 15) * 8
        rows = posrender.tile_rows(rom, bank, idx)
        hf, vf = f & 0x40, f & 0x20
        for r in range(8):
            for c in range(8):
                rr = 7 - r if vf else r; cc = 7 - c if hf else c
                v = (rows[rr] >> (14 - 2 * cc)) & 3
                out[(c0 + c, r0 + r)] = (v, idx, rr, cc)
    return out
def comps(S):
    S = set(S); out = []
    while S:
        st = [S.pop()]; c = set(st)
        while st:
            x, y = st.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    k = (x + dx, y + dy)
                    if k in S: S.remove(k); c.add(k); st.append(k)
        out.append(c)
    return out
def hair_mask(px, dark=3, core_n=8, dil=1, minsz=0):
    D = {k for k, v in px.items() if v[0] == dark}
    core = set()
    for (x, y) in D:
        n = sum(1 for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy) and (x + dx, y + dy) in D)
        if n >= core_n: core.add((x, y))
    if minsz: core = set().union(*([c for c in comps(core) if len(c) >= minsz] or [set()]))
    reg = set(core)
    for _ in range(dil):
        reg |= {(x + dx, y + dy) for (x, y) in reg for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (x + dx, y + dy) in D}
    return reg
def build(rom, ch, src=3, dst=2, core_n=8, dil=1, recs=None, minsz=0):
    """-> repl: idx -> 16 bytes ; conflicts count"""
    bank = poses.banks(rom)[ch]
    recs = recs or [r for r in poses.parse(rom, ch) if not any(f & 0x1F for f, c in r['layout'])]
    votes = collections.defaultdict(lambda: collections.Counter())   # (idx, rr, cc) -> Counter(newv)
    for rec in recs:
        px = pose_pixels(rom, ch, rec)
        m = hair_mask(px, src, core_n, dil, minsz)
        for k, (v, idx, rr, cc) in px.items():
            votes[(idx, rr, cc)][dst if k in m else v] += 1
    tiles = {}
    conflicts = 0
    for (idx, rr, cc), cnt in votes.items():
        nv = cnt.most_common(1)[0][0]
        if len(cnt) > 1: conflicts += 1
        tiles.setdefault(idx, posrender.tile_rows(rom, bank, idx))
        w = tiles[idx][rr]; sh = 14 - 2 * cc
        tiles[idx][rr] = (w & ~(3 << sh)) | (nv << sh)
    repl = {}
    for idx, rows in tiles.items():
        if rows != posrender.tile_rows(rom, bank, idx):
            repl[idx] = bytes(b for w in rows for b in (w & 0xFF, w >> 8))
    return repl, conflicts, tiles

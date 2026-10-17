"""design probe 4 (JP ROM): (a) with the timer at infinity, does the game rewrite the timer-digit tiles 0x2F-0x32?
(b) where does the game draw 'N HITS' (plane cells / tiles) — CPU attacks an idle P1 with HP kept up."""
import sys, os, ctypes as C
sys.path.insert(0, '/home/user/CustumApKS/handoff/ss2_league')
import ss2probe
ss2probe.OPTIONS[b'ngp_framegen'] = b'disabled'
CORE = '/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
PR = '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice'
HERE = os.path.dirname(os.path.abspath(__file__))
p = ss2probe.Probe(CORE, '/home/user/rom/ss2.ngc', HERE + '/_wd')
L = p.lib
for fn in ('retro_ngp_charram', 'retro_ngp_scrollram'):
    getattr(L, fn).restype = C.c_void_p
chr_ = (C.c_uint8 * 8192).from_address(L.retro_ngp_charram())
scr = (C.c_uint8 * 4096).from_address(L.retro_ngp_scrollram())
def cells(pl, rows):
    return {(r, c): scr[pl*0x800 + (r*32 + c)*2] | (scr[pl*0x800 + (r*32 + c)*2 + 1] << 8) for r in rows for c in range(20)}
p.load(PR + '/kit/fight_jp.st'); p.release()
PAT = bytes([0xFF, 0x00] * 8)
over = 0; frames = 0
base_cells = cells(0, range(0, 6)); base_tiles = bytes(chr_[0:0x40*16])
seen_cells = {}; seen_tiles = set(); shot_done = False
for f in range(2400):
    p.poke(0x582F, 0xFF); p.poke(0x5830, 0xFF)
    if p.peek(0x5A46) < 60: p.poke(0x5A46, 128)
    if p.peek(0x5C46) < 60: p.poke(0x5C46, 128)
    for t in range(0x2F, 0x33):
        for i in range(16): chr_[t*16 + i] = PAT[i]
    p.run(1); frames += 1
    if any(bytes(chr_[t*16:(t+1)*16]) != PAT for t in range(0x2F, 0x33)): over += 1
    c1, c2 = p.peek(0x5A97), p.peek(0x5C97)
    cur = cells(0, range(0, 6))
    for k, v in cur.items():
        if v != base_cells[k]: seen_cells.setdefault(k, set()).add((v, c1, c2))
    for t in range(0x2B, 0x2F):
        if bytes(chr_[t*16:(t+1)*16]) != base_tiles[t*16:(t+1)*16]: seen_tiles.add((t, c1, c2))
    if c1 >= 3 and not shot_done:
        p.run(2); p.shot(HERE + '/shots/v4_hits.png'); shot_done = True
        print('combo on P1 >=3 at f', f, 'plane0 rows 3-5 changed:', {k: hex(v) for k, v in cells(0, range(3, 6)).items() if v != base_cells[k]})
print('timer tiles overwritten by the game in %d of %d frames' % (over, frames))
print('plane0 rows 0-5 cells that changed (cell: {(entry, comboP1, comboP2)} first 6):')
for k in sorted(seen_cells):
    s = sorted(seen_cells[k])
    print(' ', k, [(hex(a), b, c) for a, b, c in s[:6]], '... n=%d' % len(s))
print('tiles 2B-2E changed with combo values:', sorted(set((hex(t), c1 >= 3, c2 >= 3) for t, c1, c2 in seen_tiles)))
p.shot(HERE + '/shots/v4_end.png')

"""design probe 2 (JP ROM): (a) tiles the fight never touches, across several matchups/stages with specials,
(b) pause flag, (c) a window drawn on the FRONT plane (plane 0) while paused: does it cover the fighters, does char RAM move."""
import sys, os, random, ctypes as C
sys.path.insert(0, '/home/user/CustumApKS/handoff/ss2_league')
import ss2probe
ss2probe.OPTIONS[b'ngp_framegen'] = b'disabled'
CORE = '/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
PR = '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice'
HERE = os.path.dirname(os.path.abspath(__file__))
p = ss2probe.Probe(CORE, '/home/user/rom/ss2.ngc', HERE + '/_wd')
L = p.lib
for fn in ('retro_ngp_charram', 'retro_ngp_scrollram', 'retro_ngp_spriteram'):
    getattr(L, fn).restype = C.c_void_p
chr_ = (C.c_uint8 * 8192).from_address(L.retro_ngp_charram())
scr = (C.c_uint8 * 4096).from_address(L.retro_ngp_scrollram())
spr = (C.c_uint8 * 256).from_address(L.retro_ngp_spriteram())
def tile(pl, r, c):
    o = pl * 0x800 + (r * 32 + c) * 2; return (scr[o] | (scr[o + 1] << 8)) & 0x1FF
def runs(lst):
    out = []; s = None
    for t in lst:
        if s is None: s = e = t
        elif t == e + 1: e = t
        else: out.append((s, e)); s = e = t
    if s is not None: out.append((s, e))
    return ' '.join('%03X-%03X' % r if r[0] != r[1] else '%03X' % r[0] for r in out)
STATES = [PR + '/kit/fight_jp.st', PR + '/re_input/fight_jp_c4.st', PR + '/re_hit/fight_jp_hao.st',
          PR + '/re_state/st_nakoruru.st', PR + '/re_state/st_stage7.st', PR + '/re_state/st_realmax.st',
          PR + '/re_state/st_stage3.st']
SEQ = [(['D', 'DR', 'R'], 'A'), (['D', 'DL', 'L'], 'A'), (['R', 'D', 'DR'], 'A'), (['L', 'R'], 'A'), (['D', 'DR', 'R'], 'B'),
       (['L', 'DL', 'D', 'DR', 'R'], 'A'), (['R', 'L', 'D'], 'A')]
U_changed = set(); U_ref = set(); U_nonzero = set(); prio = {}
for st in STATES:
    p.load(st); p.release(); p.run(2)
    prev = bytes(chr_); changed = set(); ref = set()
    random.seed(hash(st) & 0xFFFF)
    f = 0
    while f < 1500:
        r = random.random()
        if r < 0.08:
            seq, btn = random.choice(SEQ)
            for s in seq:
                p.release(); p.hold(*s); p.run(3); f += 3
            p.hold(btn); p.run(3); p.release(); f += 3
        else:
            if f % 10 == 0:
                p.release(); c = random.choice(['', 'R', 'L', 'A', 'DA', 'B', 'UR', 'U'])
                if c: p.hold(*c)
            p.run(1); f += 1
        for a in (0x5A46, 0x5C46):
            if p.peek(a) < 50: p.poke(a, 128)
        cur = bytes(chr_)
        if cur != prev:
            for t in range(512):
                if cur[t*16:(t+1)*16] != prev[t*16:(t+1)*16]: changed.add(t)
            prev = cur
        for t in range(512):
            if t not in U_nonzero and any(cur[t*16:(t+1)*16]): U_nonzero.add(t)
        for pl in (0, 1):
            for i in range(1024): ref.add((scr[pl*0x800 + i*2] | (scr[pl*0x800 + i*2 + 1] << 8)) & 0x1FF)
        for s in range(64):
            a = spr[s*4 + 1]
            if a & 0x18:
                ref.add(spr[s*4] | ((a & 1) << 8)); prio[(a >> 3) & 3] = prio.get((a >> 3) & 3, 0) + 1
    p.release()
    print(os.path.basename(st), 'P1', p.peek(0x5B51) >> 4, 'P2', p.peek(0x5D51) >> 4, 'live', p.peek(0x411A),
          'changed', runs(sorted(changed)))
    U_changed |= changed; U_ref |= ref
free = [t for t in range(512) if t not in U_changed and t not in U_ref]
print('sprite priority counts (1 back,2 mid,3 front):', prio)
print('UNION changed:', runs(sorted(U_changed)))
print('UNION FREE (never changed/referenced in any state):', len(free), runs(free))
print('  of which never nonzero:', runs([t for t in free if t not in U_nonzero]))
# ---- (b) pause flag + (c) front-plane window while paused ----
p.load(PR + '/kit/fight_jp.st'); p.release(); p.run(30)
cand = {}
snaps = []
for k in range(3):
    a = p.ram(); p.press('O', 4, 20); b = p.ram(); p.press('O', 4, 20); c = p.ram()
    snaps.append((a, b, c))
for i in range(16384):
    ok = all(s[0][i] != s[1][i] and s[2][i] == s[0][i] for s in snaps) or all((s[0][i] == 0) != (s[1][i] == 0) and (s[2][i] == 0) == (s[0][i] == 0) for s in snaps)
    if ok: cand[0x4000 + i] = [(s[0][i], s[1][i], s[2][i]) for s in snaps]
print('pause flag candidates:', {('%04X' % k): v for k, v in cand.items()})
p.press('O', 4, 20)
print('paused? row18 tiles', [hex(tile(0, 18, c)) for c in range(2, 7)])
chr_before = bytes(chr_); spr_before = bytes(spr)
T = 0x0F0
for i in range(16): chr_[T*16 + i] = 0xFF if i % 2 else 0xAA   # color 3/2 stripes
for r in range(5, 16):
    for c in range(3, 17):
        o = (r*32 + c)*2; scr[o] = T & 0xFF; scr[o+1] = (0x0A << 1) | (T >> 8)   # palette 5 (bits 9-12)
p.run(20)
ch = [t for t in range(512) if t != T and chr_[t*16:(t+1)*16] != chr_before[t*16:(t+1)*16]]
print('char tiles changed by the game during 20 paused frames:', runs(ch), 'sprite RAM changed:', bytes(spr) != spr_before)
p.shot(HERE + '/shots/v2_window_paused.png')
for r in range(5, 16):
    for c in range(3, 17):
        o = (r*32 + c)*2; scr[o] = 0; scr[o+1] = 0
p.press('O', 4, 30)
p.shot(HERE + '/shots/v2_after.png')
print('after unpause: plane0 row10 tiles', [hex(tile(0, 10, c)) for c in range(3, 8)], 'live', p.peek(0x411A))

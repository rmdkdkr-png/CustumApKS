"""design probe 1: fight-screen VRAM layout (planes, HUD, free tiles) + the game's own pause.
usage: python3 v1_vram.py [ko|jp]"""
import sys, os, random, ctypes as C
sys.path.insert(0, '/home/user/CustumApKS/handoff/ss2_league')
import ss2probe
ss2probe.OPTIONS[b'ngp_framegen'] = b'disabled'
CORE = '/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
KIT = '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice/kit'
HERE = os.path.dirname(os.path.abspath(__file__))
which = sys.argv[1] if len(sys.argv) > 1 else 'ko'
ROM = {'jp': '/home/user/rom/ss2.ngc',
       'ko': '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/legacito/ss2_ko_bundled.ngc'}[which]
os.makedirs(HERE + '/_wd', exist_ok=True)
p = ss2probe.Probe(CORE, ROM, HERE + '/_wd')
p.load(KIT + '/fight_%s.st' % which); p.release()
L = p.lib
for fn in ('retro_ngp_charram', 'retro_ngp_scrollram', 'retro_ngp_spriteram', 'retro_ngp_palram'):
    getattr(L, fn).restype = C.c_void_p
chr_ = (C.c_uint8 * 8192).from_address(L.retro_ngp_charram())
scr = (C.c_uint8 * 4096).from_address(L.retro_ngp_scrollram())
spr = (C.c_uint8 * 256).from_address(L.retro_ngp_spriteram())
regs = (C.c_uint8 * 14).from_address(L.retro_ngp_scrollram() - 14)
def ent(pl, r, c):
    o = pl * 0x800 + (r * 32 + c) * 2; return scr[o] | (scr[o + 1] << 8)
def tile(pl, r, c): return ent(pl, r, c) & 0x1FF
def dump_plane(pl, rows=range(0, 20), cols=range(0, 21)):
    print('plane', pl)
    for r in rows: print('%2d: ' % r + ' '.join('%03X' % tile(pl, r, c) for c in cols))
def regs_s():
    return 'scroll1 (%d,%d) scroll2 (%d,%d) spr(%d,%d) planeSwap %02X' % tuple(regs[4:11])
p.run(2)
print('regs', regs_s())
dump_plane(0); dump_plane(1)
# palette bits of HUD rows
print('plane1 row0 entries', ' '.join('%04X' % ent(1, 0, c) for c in range(20)))
print('plane0 row0 entries', ' '.join('%04X' % ent(0, 0, c) for c in range(20)))
p.shot(HERE + '/shots/v1_start.png')
# ---- free tiles over a busy stretch (CPU fight + random P1 input, both sides attack) ----
chr0 = bytes(chr_)
changed = [False] * 512; ref_scr = [set(), set()]; ref_spr = set(); nonzero = [any(chr0[t*16:(t+1)*16]) for t in range(512)]
random.seed(1)
prev = bytes(chr_)
for f in range(1800):
    if f % 12 == 0:
        p.release(); c = random.choice(['', 'R', 'L', 'A', 'DA', 'D', 'B', 'RA', 'UR', 'DRA'])
        if c: p.hold(*c)
    if p.peek(0x5A46) < 40: p.poke(0x5A46, 128)
    if p.peek(0x5C46) < 40: p.poke(0x5C46, 128)
    p.run(1)
    cur = bytes(chr_)
    if cur != prev:
        for t in range(512):
            if cur[t*16:(t+1)*16] != prev[t*16:(t+1)*16]: changed[t] = True
        prev = cur
    for t in range(512):
        if not nonzero[t] and any(cur[t*16:(t+1)*16]): nonzero[t] = True
    for pl in (0, 1):
        for i in range(1024):
            ref_scr[pl].add((scr[pl*0x800 + i*2] | (scr[pl*0x800 + i*2 + 1] << 8)) & 0x1FF)
    for s in range(64):
        a = spr[s*4 + 1]
        if spr[s*4 + 3] or spr[s*4 + 2] or spr[s*4] or a: ref_spr.add(spr[s*4] | ((a & 1) << 8))
p.release()
print('after 1800f regs', regs_s(), 'hp', p.peek(0x5A46), p.peek(0x5C46), 'live', p.peek(0x411A), p.peek(0x5824))
free = [t for t in range(512) if not changed[t] and t not in ref_scr[0] and t not in ref_scr[1] and t not in ref_spr]
zero_free = [t for t in free if not nonzero[t]]
def runs(lst):
    out = []; s = None
    for t in lst:
        if s is None: s = e = t
        elif t == e + 1: e = t
        else: out.append((s, e)); s = e = t
    if s is not None: out.append((s, e))
    return ' '.join('%03X-%03X' % r if r[0] != r[1] else '%03X' % r[0] for r in out)
print('changed tiles:', sum(changed), 'ref plane0', len(ref_scr[0]), 'ref plane1', len(ref_scr[1]), 'ref spr', len(ref_spr))
print('changed runs:', runs([t for t in range(512) if changed[t]]))
print('sprite tile range:', runs(sorted(ref_spr))[:600])
print('FREE (never changed, never referenced):', len(free), runs(free))
print('FREE and always zero:', len(zero_free), runs(zero_free))
p.shot(HERE + '/shots/v1_busy.png')
# ---- the game's own pause ----
p.run(60)
r0 = p.ram(); s0 = bytes(scr)
p.press('O', 4, 30)
r1 = p.ram(); s1 = bytes(scr)
print('pause regs', regs_s())
diff = [(0x4000 + i, r0[i], r1[i]) for i in range(16384) if r0[i] != r1[i]]
print('RAM diff before/after Option (%d):' % len(diff), ' '.join('%04X:%02X>%02X' % d for d in diff[:80]))
sd = [(i // 0x800, (i % 0x800) // 64, (i % 64) // 2) for i in range(0, 4096, 2) if s0[i:i+2] != s1[i:i+2]]
print('scroll cells changed by pause:', sd[:40])
p.shot(HERE + '/shots/v1_pause.png')
# does the game react to dirs/A/B while paused?
r2 = p.ram()
for b in ('R', 'L', 'U', 'D', 'A', 'B'):
    p.press(b, 6, 6)
r3 = p.ram()
diff2 = [(0x4000 + i, r2[i], r3[i]) for i in range(16384) if r2[i] != r3[i]]
print('RAM diff during paused button presses (%d):' % len(diff2), ' '.join('%04X:%02X>%02X' % d for d in diff2[:80]))
# write our own tiles into a field area while paused and check they persist
pl_front = 1
T = 0x1F0
saved_t = bytes(chr_[T*16:(T+1)*16])
for i in range(16): chr_[T*16 + i] = 0x55
cells = [(8, c) for c in range(5, 15)]
saved = {}
for (r, c) in cells:
    for pl in (0, 1):
        o = pl*0x800 + (r*32 + c)*2; saved[(pl, r, c)] = (scr[o], scr[o+1])
    o = pl_front*0x800 + (r*32 + c)*2; scr[o] = T & 0xFF; scr[o+1] = (scr[o+1] & 0xFE) | (T >> 8)
p.run(10)
keep = sum(1 for (r, c) in cells if tile(pl_front, r, c) == T)
print('our cells still there after 10 paused frames:', keep, '/', len(cells))
p.shot(HERE + '/shots/v1_pause_ours.png')
p.press('O', 4, 20)
keep2 = sum(1 for (r, c) in cells if tile(pl_front, r, c) == T)
print('after unpause +20f: still ours', keep2, 'regs', regs_s())
p.shot(HERE + '/shots/v1_unpaused_ours.png')

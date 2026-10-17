"""design probe 3 (JP ROM): does the game rewrite the front plane (plane 0) every frame during a fight / pause?
Is there a work-RAM shadow of plane 0?  Is char RAM stable while paused?"""
import sys, os, ctypes as C
sys.path.insert(0, '/home/user/CustumApKS/handoff/ss2_league')
import ss2probe
ss2probe.OPTIONS[b'ngp_framegen'] = b'disabled'
CORE = '/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
PR = '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice'
HERE = os.path.dirname(os.path.abspath(__file__))
p = ss2probe.Probe(CORE, '/home/user/rom/ss2.ngc', HERE + '/_wd')
L = p.lib
for fn in ('retro_ngp_charram', 'retro_ngp_scrollram', 'retro_ngp_spriteram', 'retro_ngp_palram'):
    getattr(L, fn).restype = C.c_void_p
chr_ = (C.c_uint8 * 8192).from_address(L.retro_ngp_charram())
scr = (C.c_uint8 * 4096).from_address(L.retro_ngp_scrollram())
pal = (C.c_uint8 * 512).from_address(L.retro_ngp_palram())
def ent(pl, r, c):
    o = pl * 0x800 + (r * 32 + c) * 2; return scr[o] | (scr[o + 1] << 8)
def put(pl, r, c, v):
    o = pl * 0x800 + (r * 32 + c) * 2; scr[o] = v & 0xFF; scr[o + 1] = v >> 8
p.load(PR + '/kit/fight_jp.st'); p.release(); p.run(3)
# 1) shadow of plane 0 in work RAM?
row0 = bytes(scr[0:40]); ram = p.ram()
k = ram.find(row0[:16])
print('plane0 row0 bytes', row0[:16].hex(), 'found in RAM at', hex(0x4000 + k) if k >= 0 else None)
row17 = bytes(scr[17*64:17*64+40]); k2 = ram.find(row17[:16]); print('row17 in RAM at', hex(0x4000 + k2) if k2 >= 0 else None)
# 2) write a cell in plane 0 field area while running; read back next frames
T = 0x0E0
for i in range(16): chr_[T*16 + i] = 0xFF if i % 2 else 0xAA
put(0, 9, 9, (5 << 9) | T)
seen = []
for f in range(4):
    p.run(1); seen.append(hex(ent(0, 9, 9)))
print('running: plane0 (9,9) after each frame', seen)
# 3) same while paused
p.press('O', 4, 20)
print('paused flag 61D4', p.peek(0x61D4), '5645', hex(p.peek(0x5645)))
put(0, 9, 9, (5 << 9) | T)
seen = []
for f in range(4):
    p.run(1); seen.append(hex(ent(0, 9, 9)))
print('paused: plane0 (9,9) after each frame', seen)
# 4) char RAM stable while paused?
c0 = bytes(chr_); p.run(30); c1 = bytes(chr_)
print('char tiles changed in 30 paused frames:', [hex(t) for t in range(512) if c0[t*16:(t+1)*16] != c1[t*16:(t+1)*16]][:20])
# 5) a window: fill rows 5..15 cols 1..18 on plane 0 every frame for 10 frames, then screenshot
for f in range(10):
    for r in range(5, 16):
        for c in range(1, 19):
            put(0, r, c, (5 << 9) | T)
    p.run(1)
p.shot(HERE + '/shots/v3_window_paused.png')
print('scroll palettes (SCR1 0x8280..):')
for k in range(16):
    o = 0x80 + k * 8
    print(' pal %2d' % k, ' '.join('%03X' % (pal[o + 2*j] | (pal[o + 2*j + 1] << 8)) for j in range(4)))
# HUD palettes used on plane0
pals = {}
for r in list(range(0, 4)) + [17, 18]:
    for c in range(20):
        e = ent(0, r, c); pals[(e >> 9) & 15] = pals.get((e >> 9) & 15, 0) + 1
print('plane0 HUD palette use', pals)
for r in range(5, 16):
    for c in range(1, 19): put(0, r, c, 0)
p.press('O', 4, 30)
print('unpaused: 61D4', p.peek(0x61D4), 'plane0 (9,9)', hex(ent(0, 9, 9)))
p.shot(HERE + '/shots/v3_after.png')

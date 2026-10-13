"""design probe 6 (JP ROM): write a front-plane window ONCE while paused and watch whether / when the game clears it.
Also: does PAUSE blink, and which cells does the game rewrite during pause?"""
import sys, os, ctypes as C
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
p.load(PR + '/kit/fight_jp.st'); p.release(); p.run(30)
p.press('O', 4, 2)
T = 0x0F0
for i in range(16): chr_[T*16 + i] = 0xFF if i % 2 else 0xAA
for r in range(5, 16):
    for c in range(3, 17):
        o = (r*32 + c)*2; scr[o] = T & 0xFF; scr[o+1] = (0x0A << 1) | (T >> 8)
prev = bytes(scr[0:0x800]); sp0 = bytes(spr)
events = []
for f in range(240):
    p.run(1)
    cur = bytes(scr[0:0x800])
    if cur != prev:
        ch = sorted(set((i // 64) for i in range(0, 0x800, 2) if cur[i:i+2] != prev[i:i+2]))
        events.append((f, ch, sum(1 for i in range(0, 0x800, 2) if cur[i:i+2] != prev[i:i+2])))
        prev = cur
    if f == 3: p.shot(HERE + '/shots/v6_f3.png')
print('paused', p.peek(0x61D4))
print('plane0 changes during 240 paused frames (frame, rows, ncells):', events[:30])
win = sum(1 for r in range(5, 16) for c in range(3, 17) if (scr[(r*32+c)*2] | (scr[(r*32+c)*2+1] << 8)) & 0x1FF == T)
print('window cells still ours after 240 frames:', win, '/', 11 * 14, ' sprite VRAM changed:', bytes(spr) != sp0)
p.shot(HERE + '/shots/v6_f240.png')

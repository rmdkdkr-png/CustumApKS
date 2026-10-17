"""design probe 7: save fight-start char RAM + plane0 rows 0-3,17-18 for a ROM (compare JP vs KO HUD tiles)."""
import sys, os, ctypes as C
sys.path.insert(0, '/home/user/CustumApKS/handoff/ss2_league')
import ss2probe
ss2probe.OPTIONS[b'ngp_framegen'] = b'disabled'
CORE = '/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
HERE = os.path.dirname(os.path.abspath(__file__))
rom, st, out = sys.argv[1:4]
p = ss2probe.Probe(CORE, rom, HERE + '/_wd')
for fn in ('retro_ngp_charram', 'retro_ngp_scrollram'):
    getattr(p.lib, fn).restype = C.c_void_p
chr_ = (C.c_uint8 * 8192).from_address(p.lib.retro_ngp_charram())
scr = (C.c_uint8 * 4096).from_address(p.lib.retro_ngp_scrollram())
p.load(st); p.release(); p.run(3)
a = bytes(chr_)
p.press('O', 4, 10)
b = bytes(chr_); s = bytes(scr)
p.press('O', 4, 10)
open(out, 'wb').write(a + b + s)
print('saved', out)

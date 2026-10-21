"""design probe 5 (JP ROM): dump HUD tiles 0x001-0x03A as ascii (find the game's own digit / HITS glyphs),
and check whether the game rewrites timer-box CELLS each tick (point them at our own tile and read back)."""
import sys, os, ctypes as C
sys.path.insert(0, '/home/user/CustumApKS/handoff/ss2_league')
import ss2probe
ss2probe.OPTIONS[b'ngp_framegen'] = b'disabled'
CORE = '/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
PR = '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice'
HERE = os.path.dirname(os.path.abspath(__file__))
rom = sys.argv[1] if len(sys.argv) > 1 else '/home/user/rom/ss2.ngc'
st = sys.argv[2] if len(sys.argv) > 2 else PR + '/kit/fight_jp.st'
p = ss2probe.Probe(CORE, rom, HERE + '/_wd')
L = p.lib
for fn in ('retro_ngp_charram', 'retro_ngp_scrollram'):
    getattr(L, fn).restype = C.c_void_p
chr_ = (C.c_uint8 * 8192).from_address(L.retro_ngp_charram())
scr = (C.c_uint8 * 4096).from_address(L.retro_ngp_scrollram())
p.load(st); p.release(); p.run(3)
def art(t):
    rows = []
    for y in range(8):
        w = chr_[t*16 + y*2] | (chr_[t*16 + y*2 + 1] << 8)
        rows.append(''.join(' .o#'[(w >> (14 - 2*x)) & 3] for x in range(8)))
    return rows
for base in range(0x001, 0x03B, 10):
    ts = list(range(base, min(base + 10, 0x03B)))
    print('   '.join('%03X     ' % t for t in ts))
    for y in range(8): print('   '.join(art(t)[y] for t in ts))
    print()
for t in (0x049, 0x04A, 0x03B, 0x03C):
    print('%03X' % t); print('\n'.join(art(t)))
# timer box cells -> our tile; does the game rewrite the cells?
T = 0x0E0
for i in range(16): chr_[T*16 + i] = 0x55
CELLS = [(1, 9), (1, 10), (2, 9), (2, 10), (3, 9), (3, 10)]
def ent(r, c): return scr[(r*32 + c)*2] | (scr[(r*32 + c)*2 + 1] << 8)
orig = {k: ent(*k) for k in CELLS}
print('timer box cells', {k: hex(v) for k, v in orig.items()})
lost = 0
for f in range(120):
    p.poke(0x582F, 0xFF); p.poke(0x5830, 0xFF)
    for (r, c) in CELLS:
        o = (r*32 + c)*2; v = (orig[(r, c)] & 0xFE00) | T; scr[o] = v & 0xFF; scr[o+1] = v >> 8
    p.run(1)
    lost += sum(1 for k in CELLS if ent(*k) & 0x1FF != T)
print('cells rewritten by game: %d cell-frames of %d' % (lost, 120 * len(CELLS)))
p.shot(HERE + '/shots/v5_cells.png')

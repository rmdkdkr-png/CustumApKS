"""re_state common helpers (practice-mode state RE)."""
import sys, os
sys.path.insert(0, '/home/user/CustumApKS/handoff/ss2_league')
import ss2probe
# ss2probe passes ngp_framegen='off' which the core does not know -> force 'disabled' so 1 retro_run = 1 real frame
ss2probe.OPTIONS[b'ngp_framegen'] = b'disabled'
CORE = '/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
ROM_JP = '/home/user/rom/ss2.ngc'
ROM_KO = '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/legacito/ss2_ko_bundled.ngc'
KIT = '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice/kit'
HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = HERE + '/shots'
ST_JP = KIT + '/fight_jp.st'
WCORE = '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice/re_input/wcore/mednafen_ngp_libretro.so'
_p = None
def probe(rom=ROM_JP, core=CORE):
    global _p
    if _p is None:
        _p = ss2probe.Probe(core, rom, HERE + '/_wd')
    return _p
def fresh(state=ST_JP, **kw):
    p = probe(**kw); p.load(state); p.release(); return p
def s16(v): return v - 0x10000 if v & 0x8000 else v
def hexdump(p, a0, a1, label=''):
    if label: print(label)
    for a in range(a0, a1, 16):
        print('%04X: ' % a + ' '.join('%02X' % p.peek(a+i) for i in range(16)))
def shot(p, name): p.shot(os.path.join(SHOTS, name + '.png'))
# watch core helpers
import ctypes as C
def wsetup(p):
    L = p.lib
    L.retro_ss2w_watch.argtypes = [C.c_uint32, C.c_int]
    L.retro_ss2w_read.argtypes = [C.POINTER(C.c_uint32), C.c_uint32]; L.retro_ss2w_read.restype = C.c_uint32
    p._wbuf = (C.c_uint32 * (262144 * 4))()
def watch(p, addrs, mode=1):
    for a in addrs: p.lib.retro_ss2w_watch(a, mode)
def wclear(p): p.lib.retro_ss2w_clear()
def wread(p):
    n = p.lib.retro_ss2w_read(p._wbuf, 262144); b = p._wbuf
    return [(b[4*k], b[4*k+1], b[4*k+2], b[4*k+3]) for k in range(n)]
def p1pad(p):
    m = p.mask; return ((m>>4)&1)*1 | ((m>>5)&1)*2 | ((m>>6)&1)*4 | ((m>>7)&1)*8 | (m&1)*0x10 | ((m>>8)&1)*0x20
def dummy_p2(p, p2pad=0):
    """sibling agent's (re_input) recipe: VS input path; P2 = idle human, P1 pad mirrored to 0x570D. Call every frame."""
    if p.peek(0x40A7) == 241 and p.peek(0x411A) == 1 and p.peek(0x5824) == 0:
        p.poke(0x57D4, 1); p.poke(0x5BCB, p.peek(0x5BCB) & ~1); p.poke(0x570D, p1pad(p)); p.poke(0x5715, p2pad)
HOOKS = []
_orig_run = ss2probe.Probe.run
def _hooked_run(self, n=1):
    for _ in range(n):
        for h in HOOKS: h(self)
        _orig_run(self, 1)
ss2probe.Probe.run = _hooked_run
def runf(p, n, hook=None):
    for _ in range(n):
        if hook: hook(p)
        p.run(1)
def setw(p,a,v): p.poke(a,v&0xFF); p.poke(a+1,(v>>8)&0xFF)

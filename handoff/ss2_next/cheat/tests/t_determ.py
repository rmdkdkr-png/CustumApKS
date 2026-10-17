"""H-3 결정성 — 치트 모두 끔이면 cheat_tick 이 한 바이트도 안 쓴다: 같은 입력 6000프레임, cheat_tick 있음/없음 램 해시 비교"""
import os, sys, hashlib, ctypes as C
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cx
from ph import *
lg.cheat_tick.argtypes = [C.c_void_p, C.c_size_t, C.c_int]
with_cheat = sys.argv[1] == 'on'
W = os.path.join(cx.D, 'det_' + sys.argv[1])
os.makedirs(W, exist_ok=True)
h = PH(cx.ROMS['ko'], W)
lg.cheat_reset_all(); lg.league_practice_hub(1, 0); lg.league_hub_dual(1)
if with_cheat: h.post_hook = lambda hh: lg.cheat_tick(hh.p._ramp, hh.p._rams, hh.user)
script = {420: 'A', 600: 'A', 760: 'A', 900: 'A'}
out = []
for f in range(6000):
    if f in script: h.user = bits(script[f])
    elif f - 4 in script: h.user = 0
    if f > 3000: h.user = bits('R') if (f // 50) % 2 else bits('A') if f % 40 < 4 else 0
    h.run(1); out.append(hashlib.md5(h.p.ram()).hexdigest()[:8])
open(os.path.join(cx.D, 'det_%s.txt' % sys.argv[1]), 'w').write('\n'.join(out))
print(sys.argv[1], 'MODE', h.p.peek(0x40A7), 'prog %02X' % h.p.peek(0x57C6))

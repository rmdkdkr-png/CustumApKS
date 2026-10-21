"""활성 프레임 실측: 멀리서 헛친 기술의 j 프레임째에 더미를 앞으로 순간이동 → 닿는 프레임"""
from tr import *
import sys
h = mk(sys.argv[1] if len(sys.argv) > 1 else 'ko'); fight(h, 9, int(sys.argv[2]) if len(sys.argv) > 2 else 2); p = h.p
base = snap(h)
def setx(pl, x):
    b = 0x5980 + pl*0x200
    for a in (b+0x54, b+0x64): p.poke(a, 0); p.poke(a+1, 0)
    for a in (b+0x56, b+0x66, 0x4E38 + pl*0x40): p.poke(a, x & 0xFF); p.poke(a+1, x >> 8)
def probe_move(name, script, near=26, n=160):
    restore(h, base); g = approach(h, 150)
    x1 = p.peek16(0x59D6); dirn = 1 if p.peek16(0x5BD6) > x1 else -1
    s0 = snap(h)
    R = rec(h, script, n)
    st = [i for i, x in enumerate(R) if x['ram'][0x19CE] != 0]
    start = st[0]
    end = next((i for i, x in enumerate(R) if i > start and x['ram'][0x19CE] == 0), None)
    box = [i for i, x in enumerate(R) if x['ram'][0x0E4C] != 0xFF]
    acts = []
    for x in R:
        a = x['ram'][0x0E3E] | x['ram'][0x0E3F] << 8
        if not acts or acts[-1][1] != a: acts.append((R.index(x), a))
    res = []
    for j in range(start - 1, (end or n - 6) + 1):
        restore(h, s0)
        cf = None
        for f in range(j + 6):
            if f in script: h.user = bits(rl(h, script[f])) if script[f] else 0
            h.run(1)
            if f == j: setx(1, p.peek16(0x59D6) + dirn * near)
            if f > j and cf is None and (p.peek(0x5DC7) or p.peek(0x5C97)): cf = f
        h.user = 0
        res.append((j, cf))
    hits = sorted(set(cf for j, cf in res if cf is not None))
    print('%-8s start %3d end %s  box %s  contact-at %s  acts %s' % (name, start, end, (box[0], box[-1]) if box else None, hits, ' '.join('%d:%X' % a for a in acts)))
    if hits and end:
        su = hits[0] - start + 1; act = hits[-1] + 2 - hits[0]; rec_ = end - (hits[-1] + 2)
        print('          => startup %dF  active %dF  recovery %dF  total %dF' % (su, act, rec_, end - start))
    return start, end, hits
probe_move('A', {0: 'A', 2: ''})
probe_move('A-hold', {0: 'A', 14: ''})
probe_move('B', {0: 'B', 2: ''})
probe_move('dA', {0: 'D', 4: 'DA', 8: 'D', 30: ''})
probe_move('dB', {0: 'D', 4: 'DB', 8: 'D', 30: ''})
probe_move('236A', {0: 'D', 4: 'Df', 8: 'f', 12: 'fA', 16: ''}, n=200)
probe_move('623A', {0: 'f', 4: 'D', 8: 'Df', 12: 'DfA', 16: ''}, n=200)

"""판정 없는 동작·점프·튕겨내기 칸 모양"""
from tr import *
import fd_ref
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
TR = [None]
def post(hh):
    if TR[0] is not None and p.peek(0x40A7) == 241 and p.peek(0x411A) == 1 and p.peek(0x61D4) == 0: TR[0].step(p.peek)
h.post_hook = post
def go(name, gapv, sc, n, guard=0):
    restore(h, base); lg.practice_set(1, guard); approach(h, gapv); TR[0] = fd_ref.FrameData(); h.run(2)
    for f in range(n):
        if f in sc: h.user = bits(rl(h, sc[f])) if sc[f] else 0
        h.run(1)
    h.user = 0; h.run(40)
    t = TR[0]
    def m(q):
        out = ''
        for c in t.cell[q]:
            if c == 0xFF: out += ' '; continue
            ch = fd_ref.KCH[c & 0x0F]
            if c & fd_ref.F_PARRY: ch = ch.lower() if ch.isalpha() else 'p'
            if c & fd_ref.F_PROJ: ch = '*'
            out += ch
        return out.rstrip()
    print('%-12s %s\n%-12s %s\n%-12s %s' % (name, m(0), '', m(1), '', t.line(0)))
    return t
go('B', 150, {0: 'B', 3: ''}, 60)
go('↓B 튕겨내기', 150, {0: 'DB', 3: ''}, 70)
go('→B', 150, {0: 'fB', 3: ''}, 70)
go('점프', 150, {0: 'U', 3: ''}, 70)
go('점프 A', 60, {0: 'Uf', 3: '', 22: 'A', 25: ''}, 90)
go('대시?', 150, {0: 'f', 2: '', 4: 'f', 8: ''}, 50)

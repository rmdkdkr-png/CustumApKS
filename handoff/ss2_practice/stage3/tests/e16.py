from tr import *
P2PAD = [0]
def p1pad(m): return ((m>>4)&1)*1 | ((m>>5)&1)*2 | ((m>>6)&1)*4 | ((m>>7)&1)*8 | (m&1)*0x10 | ((m>>8)&1)*0x20
def dump(h, label):
    b = 0x4E30 + 4*0x40 - 0x4000
    r = h.p.ram()
    print(label, ' '.join('%02X' % v for v in r[b:b+0x40]))
# P1 하오마루 장풍
h = mk('ko'); fight(h, 9, 2); p = h.p
lg.practice_set(7, 0); h.run(40)
rec(h, {0: 'D', 4: 'Df', 8: 'f', 12: 'fA', 16: ''}, 30); dump(h, 'P1 proj')
# P2 하오마루 장풍
h2 = mk('ko', os.path.join(T.WORK, 'e16b')); fight(h2, 2, 9); p2 = h2.p
lg.practice_set(7, 0); h2.run(40)
def vs(hh):
    if p2.peek(0x40A7) == 241 and p2.peek(0x411A) == 1:
        p2.poke(0x57D4, 1); p2.poke(0x5BCB, p2.peek(0x5BCB) & ~1); p2.poke(0x570D, p1pad(hh.user)); p2.poke(0x5715, P2PAD[0])
h2.post_hook = vs
seq = {0: 0x02, 4: 0x06, 8: 0x04, 12: 0x14, 16: 0}
for f in range(32):
    if f in seq: P2PAD[0] = seq[f]
    h2.run(1)
dump(h2, 'P2 proj')

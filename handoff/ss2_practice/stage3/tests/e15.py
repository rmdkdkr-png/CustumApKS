"""P2(하오마루) 장풍 — VS 경로로 P2 가 236A. 물체 칸 주인 필드 찾기"""
from tr import *
h = mk('ko'); fight(h, 2, 9); p = h.p
base = snap(h)
P2PAD = [0]
def p1pad(m): return ((m>>4)&1)*1 | ((m>>5)&1)*2 | ((m>>6)&1)*4 | ((m>>7)&1)*8 | (m&1)*0x10 | ((m>>8)&1)*0x20
def vs(hh):
    if p.peek(0x40A7) == 241 and p.peek(0x411A) == 1 and p.peek(0x5824) == 0:
        p.poke(0x57D4, 1); p.poke(0x5BCB, p.peek(0x5BCB) & ~1); p.poke(0x570D, p1pad(hh.user)); p.poke(0x5715, P2PAD[0])
restore(h, base); lg.practice_set(7, 0); h.run(40)
h.post_hook = vs
R = []
seq = {0: 0x02, 4: 0x06, 8: 0x04, 12: 0x14, 16: 0}
for f in range(80):
    if f in seq: P2PAD[0] = seq[f]
    R += rec(h, {}, 1)
h.post_hook = None
print('c2   ' + ' '.join('%02X' % x['ram'][0x1BCE] for x in R))
print('act2 ' + ' '.join('%03X' % (x['ram'][0x0E7E] | x['ram'][0x0E7F] << 8) for x in R[:40]))
print('objn ' + ' '.join('%02X' % x['ram'][0x01C2] for x in R))
for k in range(4, 8):
    b = 0x4E30 + k*0x40 - 0x4000
    for off in (0x05, 0x06, 0x07, 0x0E, 0x0F, 0x24, 0x25, 0x26, 0x30, 0x31):
        col = [x['ram'][b+off] for x in R]
        if len(set(col)) > 1: print('obj%d +%02X ' % (k, off) + ' '.join('%02X' % c for c in col))

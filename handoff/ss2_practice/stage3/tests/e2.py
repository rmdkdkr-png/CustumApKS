from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
g = approach(h, 40); print('gap', g, 'frame parity', h.frames & 1)
s0 = snap(h)
R = rec(h, {0: 'A', 2: ''}, 90)
# 바뀌는 블록 바이트 표
def show(R, who, rng):
    for off in rng:
        vals = [x['b'][who][off] for x in R]
        if len(set(vals)) > 1:
            print('P%d +%03X %04X: ' % (who+1, off, 0x5980 + who*0x200 + off) + ' '.join('%02X' % v for v in vals[:70]))
print('hs   ' + ' '.join('%02X' % x['g'][0x5DC7] for x in R[:70]))
for who in (0, 1):
    show(R, who, range(0x200))
for who in (0, 1):
    for off in range(0x40):
        vals = [x['o'][who][off] for x in R]
        if len(set(vals)) > 1: print('O%d +%02X: ' % (who, off) + ' '.join('%02X' % v for v in vals[:70]))

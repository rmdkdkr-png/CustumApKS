from tr import *
import sys
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
SEL = [('hs',0x5DC7),('c1',0x59CE),('act1',0x4E3E),('an1',0x4E40),('rt1',0x4E41),('1A',0x4E4A),('1C',0x4E4C),('1D',0x4E4D),('14',0x4E44),
       ('5B48',0x5B48),('5B49',0x5B49),('5AF9',0x5AF9),('5A56',0x5A56),('c2',0x5BCE),('st2',0x5BC9),('hsn2',0x5BD1),('act2',0x4E7E)]
def run(gapv, btn='A', hold=2, n=70, guard=0):
    restore(h, base); lg.practice_set(1, guard)
    g = approach(h, gapv)
    R = rec(h, {0: btn, hold: ''}, n)
    print('--- gap %d btn %s hold %d guard %d' % (g, btn, hold, guard))
    for name, a in SEL:
        print('%-5s ' % name + ' '.join('%02X' % x['ram'][a-0x4000] for x in R))
for g in (60, 36, 24, 120):
    run(g)

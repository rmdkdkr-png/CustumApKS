from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
def show(sc, gapv, guard, n=80, who=1):
    restore(h, base); lg.practice_set(1, guard)
    g = approach(h, gapv)
    R = rec(h, sc, n)
    print('=== %s gap %d guard %d' % (sc, g, guard))
    print('hs    ' + ' '.join('%02X' % x['g'][0x5DC7] for x in R))
    for w in (0, 1):
        for off in range(0x200):
            vals = [x['b'][w][off] for x in R]
            if len(set(vals)) > 1 and off not in (0x55, 0x56, 0x65, 0x66, 0x54, 0x64):
                print('P%d %04X ' % (w+1, 0x5980 + w*0x200 + off) + ' '.join('%02X' % v for v in vals))
show({0: 'A', 2: ''}, 30, 1)

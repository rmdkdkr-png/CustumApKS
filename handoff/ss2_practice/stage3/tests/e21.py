from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
def dumpk(label, sc, n, ks=range(4, 8), every=4):
    restore(h, base); approach(h, 60)
    for f in range(n):
        if f in sc: h.user = bits(rl(h, sc[f])) if sc[f] else 0
        h.run(1)
        if f % every == 0:
            for k in ks:
                o = 0x4E30 + k * 0x40
                if p.peek16(o + 0xE): print('%s f%-3d k%d %s' % (label, f, k, p.peek(o, 0x40).hex(' ')))
    h.user = 0
dumpk('5A ', {0: 'A', 2: ''}, 30, every=6)
dumpk('5A+', {0: 'A', 14: ''}, 40, every=8)
dumpk('236', {0: 'D', 4: 'Df', 8: 'f', 12: 'fA', 16: ''}, 44, every=6)

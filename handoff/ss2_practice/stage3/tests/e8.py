from tr import *
import sys
h = mk('ko'); fight(h, 9, int(sys.argv[1]) if len(sys.argv) > 1 else 2); p = h.p
base = snap(h)
def run(gapv, sc, n=90):
    restore(h, base)
    g = approach(h, gapv)
    R = rec(h, sc, n)
    acts = []
    for i, x in enumerate(R):
        a = x['ram'][0x0E3E] | x['ram'][0x0E3F] << 8
        if not acts or acts[-1][1] != a: acts.append((i, a))
    hit = any(x['ram'][0x1DC7] or x['ram'][0x1C97] for x in R)
    box = sum(x['ram'][0x0E4C] != 0xFF for x in R)
    return g, acts, hit, box
for g in (14, 30, 60):
    for sc in ('B', 'DB', 'fB', 'bB', 'DfB', 'DbB', 'UB'):
        r = run(g, {0: sc, 3: ''})
        print('gap %3d %-4s acts %-40s hit %d box %d' % (r[0], sc, ' '.join('%d:%X' % a for a in r[1]), r[2], r[3]))

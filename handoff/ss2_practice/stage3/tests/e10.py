from tr import *
import crop, glob
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
W = os.path.join(T.WORK, 'shots')
for nm, sc in (('B', 'B'), ('bB', 'bB'), ('DB', 'DB'), ('fB', 'fB'), ('AB', 'AB')):
    restore(h, base); approach(h, 40)
    for f in glob.glob(W + '/v_*.png'): os.unlink(f)
    for f in range(40):
        if f == 0: h.user = bits(rl(h, sc))
        if f == 3: h.user = 0
        h.run(1)
        if f % 5 == 2: p.shot(os.path.join(W, 'v_%02d.png' % f), scale=1)
    crop.montage(sorted(glob.glob(W + '/v_*.png')), os.path.join(W, 'm_%s.png' % nm), 30, 70, 130, 140, 2)

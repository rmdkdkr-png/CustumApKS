from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
restore(h, base); approach(h, 40)
W = os.path.join(T.WORK, 'shots'); os.makedirs(W, exist_ok=True)
h.user = bits('B'); 
for f in range(24):
    if f == 2: h.user = 0
    h.run(1)
    if f % 4 == 1: h.p.shot(os.path.join(W, 'B_%02d.png' % f), scale=1)

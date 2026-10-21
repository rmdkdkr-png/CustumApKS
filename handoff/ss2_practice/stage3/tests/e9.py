import os, sys
import ss2probe
if os.environ.get('NOSP'): ss2probe.OPTIONS[b'ngp_ss2sp'] = b'disabled'
from tr import *
h = mk(sys.argv[1], os.path.join(T.WORK, 'e9_' + sys.argv[1] + ('_nosp' if os.environ.get('NOSP') else ''))); fight(h, 9, 2); p = h.p
base = snap(h)
for sc in ('B', 'bB', 'DB', 'A'):
    restore(h, base); g = approach(h, 30)
    R = rec(h, {0: sc, 3: ''}, 70)
    acts = []
    for i, x in enumerate(R):
        a = x['ram'][0x0E3E] | x['ram'][0x0E3F] << 8
        if not acts or acts[-1][1] != a: acts.append((i, a))
    print(sys.argv[1], 'nosp' if os.environ.get('NOSP') else 'sp', sc, ' '.join('%d:%X' % a for a in acts), 'pad', ' '.join('%02X' % x['ram'][0x1A6B] for x in R[:5]))

from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
P2PAD = [0]; VS = [False]
def p1pad(m): return ((m>>4)&1)*1 | ((m>>5)&1)*2 | ((m>>6)&1)*4 | ((m>>7)&1)*8 | (m&1)*0x10 | ((m>>8)&1)*0x20
def post(hh):
    if VS[0] and p.peek(0x40A7) == 241 and p.peek(0x411A) == 1 and p.peek(0x5824) == 0:
        p.poke(0x57D4, 1); p.poke(0x5BCB, p.peek(0x5BCB) & ~1); p.poke(0x570D, p1pad(hh.p.mask)); p.poke(0x5715, P2PAD[0])
h.post_hook = post
def C(v): return '.' if v == 0 else {0x02:'2',0x04:'4',0x06:'6',0x08:'8',0x0A:'a',0x0C:'c',0x10:'D',0x12:'g',0x14:'e',0xFF:'F'}.get(v, '?')
sc = {0: 'f', 4: 'D', 8: 'Df', 12: 'DfA', 16: ''}
for vs, pad, lab in ((False, 0, 'no VS'), (True, 0, 'VS idle'), (True, 0x02, 'VS hold D'), (True, 0x01, 'VS hold U'), (True, 0x10, 'VS hold A'), (True, 0x08, 'VS hold R')):
    restore(h, base); lg.practice_set(1, 0); approach(h, 30); h.run(2)
    VS[0] = vs; P2PAD[0] = 0
    s2 = ''; a2 = []
    for f in range(240):
        if f in sc: h.user = bits(rl(h, sc[f])) if sc[f] else 0
        if f >= 30: P2PAD[0] = pad
        h.run(1)
        s2 += C(p.peek(0x5BCE)); a2.append(p.peek16(0x4E7E))
    VS[0] = False; h.user = 0
    acts = []
    for i, a in enumerate(a2):
        if not acts or acts[-1][1] != a: acts.append((i, a))
    free = s2.rfind('F'); 
    print('%-10s %s' % (lab, s2))
    print('%-10s %s' % ('', ' '.join('%d:%X' % t for t in acts)))

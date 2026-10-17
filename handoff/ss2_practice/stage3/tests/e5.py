from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
SEL = [('in',None),('hs',0x5DC7),('c1',0x59CE),('act1',0x4E3E),('an1',0x4E40),('1C',0x4E4C),('pad',0x5A6B),('c2',0x5BCE),('cb2',0x5C97),('act2',0x4E7E)]
def run(gapv, sc, n=60, guard=0):
    restore(h, base); lg.practice_set(1, guard)
    g = approach(h, gapv)
    print('--- gap', g, sc, 'c1 at start', p.peek(0x59CE), 'act', hex(p.peek16(0x4E3E)))
    R = rec(h, sc, n)
    for name, a in SEL:
        if a is None: print('%-5s ' % name + ' '.join('%02X' % (x['inp'] & 0xFF if not x['inp'] >> 8 else 0xBB) for x in R)); continue
        print('%-5s ' % name + ' '.join('%02X' % x['ram'][a-0x4000] for x in R))
run(150, {0: 'B', 2: ''})
run(30, {0: 'B', 2: ''})
run(30, {0: 'D', 4: 'DB', 8: 'D', 30: ''})

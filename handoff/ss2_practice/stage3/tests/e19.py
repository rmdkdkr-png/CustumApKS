from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
def C(v): return '.' if v == 0 else {0x02:'2',0x04:'4',0x06:'6',0x08:'8',0x0A:'a',0x0C:'c',0x10:'D',0x12:'g',0x14:'e',0xFF:'F'}.get(v, '?')
def run(label, gapv, sc, n=200, guard=0):
    restore(h, base); lg.practice_set(1, guard)
    g = approach(h, gapv)
    R = rec(h, sc, n)
    print('%s gap %d' % (label, g))
    print(' c1  ' + ''.join(C(x['ram'][0x19CE]) for x in R))
    print(' bx1 ' + ''.join('#' if x['ram'][0x0E4C] != 0xFF else '.' for x in R))
    print(' hs  ' + ''.join('h' if x['ram'][0x1DC7] else '.' for x in R))
    print(' c2  ' + ''.join(C(x['ram'][0x1BCE]) for x in R))
    print(' cb2 ' + ''.join(('%X' % min(15, x['ram'][0x1C97])) if x['ram'][0x1C97] else '.' for x in R))
    print(' y2  ' + ''.join('^' if (x['ram'][0x1BDA] | x['ram'][0x1BDB] << 8) < 128 else '_' for x in R))
    print(' st2 ' + ''.join({0x20:'s',0x40:'c',0x80:'a'}.get(x['ram'][0x1BC9] & 0xE0, '?') for x in R))
    print(' a2  ' + ' '.join('%d:%X' % t for t in acts(R, 0x0E7E)))
def acts(R, a):
    out = []
    for i, x in enumerate(R):
        v = x['ram'][a-0x4000] | x['ram'][a-0x4000+1] << 8
        if not out or out[-1][1] != v: out.append((i, v))
    return out
run('throw fA', 17, {0: 'fA', 16: ''}, 160)
run('heavy hit', 30, {0: 'A', 14: ''}, 220)
run('heavy block', 30, {0: 'A', 14: ''}, 120, guard=1)
run('623A hit', 30, {0: 'f', 4: 'D', 8: 'Df', 12: 'DfA', 16: ''}, 220)
run('236A block', 40, {0: 'D', 4: 'Df', 8: 'f', 12: 'fA', 16: ''}, 120, guard=1)
run('dA hit', 30, {0: 'D', 4: 'DA', 8: 'D', 30: ''}, 80)

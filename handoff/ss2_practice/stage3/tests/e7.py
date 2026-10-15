from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
def run(gapv, sc, n=60, label=''):
    restore(h, base)
    g = approach(h, gapv)
    R = rec(h, sc, n)
    acts = []
    for i, x in enumerate(R):
        a = x['ram'][0x0E3E] | x['ram'][0x0E3F] << 8
        if not acts or acts[-1][1] != a: acts.append((i, a))
    c = ''.join('%X' % min(15, x['ram'][0x19CE] >> 4) if x['ram'][0x19CE] else '.' for x in R)
    box = ''.join('#' if x['ram'][0x0E4C] != 0xFF else '.' for x in R)
    hs = ''.join('h' if x['ram'][0x1DC7] else ('c' if x['ram'][0x1C97] else '.') for x in R)
    print('%-10s gap %3d acts %s' % (label, g, ' '.join('%d:%X' % a for a in acts)))
    print('   ctrl ' + c + '\n   box  ' + box + '\n   hit  ' + hs)
run(30, {0: 'B', 12: ''}, 80, 'B hold12')
run(30, {0: 'fB', 4: ''}, 80, 'fB')
run(30, {0: 'bB', 4: ''}, 80, 'bB')
run(30, {0: 'AB', 4: ''}, 80, 'AB')
run(20, {0: 'fA', 16: ''}, 120, 'fA close')
run(20, {0: 'bA', 16: ''}, 120, 'bA close')
run(14, {0: 'bA', 16: ''}, 120, 'bA close14')
run(30, {0: 'Uf', 4: '', 30: 'A', 34: ''}, 120, 'jump A')

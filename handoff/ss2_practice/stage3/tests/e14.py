from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
restore(h, base); g = approach(h, 100)
R = rec(h, {0: 'D', 4: 'Df', 8: 'f', 12: 'fA', 16: ''}, 90)
print('gap', g)
print('objn ' + ' '.join('%02X' % x['ram'][0x01C2] for x in R))
print('c1   ' + ' '.join('%02X' % x['ram'][0x19CE] for x in R))
print('hs   ' + ' '.join('%02X' % x['ram'][0x1DC7] for x in R))
print('cb2  ' + ' '.join('%02X' % x['ram'][0x1C97] for x in R))
for k in range(2, 12):
    o = 0x0E30 + k * 0x40 - 0x4000 + 0x4000 - 0x4000
    base_o = 0x4E30 + k*0x40 - 0x4000
    vals = [x['ram'][base_o:base_o+0x40] for x in R]
    for off in range(0x40):
        col = [v[off] for v in vals]
        if len(set(col)) > 1 and off in (0x0E, 0x0F, 0x1A, 0x1B, 0x1C, 0x1D, 0x08, 0x09, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x24, 0x25, 0x26, 0x27, 0x30, 0x31):
            print('obj%-2d +%02X ' % (k, off) + ' '.join('%02X' % c for c in col))

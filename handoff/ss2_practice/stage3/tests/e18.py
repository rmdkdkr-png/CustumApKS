from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
MV = [('A', {0: 'A', 2: ''}), ('A-hold', {0: 'A', 14: ''}), ('dA', {0: 'D', 4: 'DA', 8: 'D', 30: ''}), ('bB', {0: 'bB', 3: ''}),
      ('B', {0: 'B', 3: ''}), ('DB', {0: 'DB', 3: ''}), ('fB', {0: 'fB', 3: ''}), ('236A', {0: 'D', 4: 'Df', 8: 'f', 12: 'fA', 16: ''}),
      ('623A', {0: 'f', 4: 'D', 8: 'Df', 12: 'DfA', 16: ''}), ('jA', {0: 'Uf', 4: '', 30: 'A', 34: ''}), ('AB', {0: 'AB', 3: ''})]
for nm, sc in MV:
    restore(h, base); approach(h, 120)
    R = rec(h, sc, 60)
    st = next(i for i, x in enumerate(R) if x['ram'][0x19CE] and x['ram'][0x19CE] != 0x08)
    x = R[st]['ram']; y = R[min(st + 6, 59)]['ram']
    stances = sorted(set(z['ram'][0x19C9] for z in R[st:st+40]))
    ctrls = []
    for z in R[st:]:
        if not ctrls or ctrls[-1] != z['ram'][0x19CE]: ctrls.append(z['ram'][0x19CE])
    print('%-7s st %2d act %03X 59CC %02X%02X 59CF %02X 5A56 %s 5A7E %02X 5B48 %02X%02X | +6: act %03X 5A56 %s | stance %s ctrl seq %s' % (nm, st, x[0x0E3E] | x[0x0E3F] << 8, x[0x19CD], x[0x19CC], x[0x19CF],
          x[0x1A56:0x1A5A].hex(), x[0x1A7E], x[0x1B48], x[0x1B49], y[0x0E3E] | y[0x0E3F] << 8, y[0x1A56:0x1A5A].hex(), ['%02X' % s for s in stances], ' '.join('%02X' % c for c in ctrls[:6])))

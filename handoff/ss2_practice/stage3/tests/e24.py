from tr import *
h = mk('ko', os.path.join(T.WORK, 'e23_7')); fight(h, 9, 7); p = h.p
restore_s = snap(h)
approach(h, 150)
def objs():
    out = []
    for k in range(0, 32):
        o = 0x4E30 + k * 0x40
        if p.peek16(o + 0xE) and p.peek(o + 6) != 0xFF and (p.peek(o + 0x1E) != 0xFF or p.peek(o + 0x1C) != 0xFF):
            out.append('k%d a%03X 06=%02X 1C=%02X 1E=%02X 27=%d' % (k, p.peek16(o + 0xE), p.peek(o + 6), p.peek(o + 0x1C), p.peek(o + 0x1E), p.peek(o + 0x27)))
    return out
print('objn', p.peek(0x41C2), objs())
print('4180:', p.peek(0x4180, 0x48).hex(' '))
for f in range(14):
    h.user = bits('A') if f < 2 else 0
    h.run(1)
    print(f, 'c1 %02X' % p.peek(0x59CE), 'n', p.peek(0x41C2), p.peek(0x4180, 2 * p.peek(0x41C2)).hex(' '), objs())

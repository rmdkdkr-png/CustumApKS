from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
restore(h, base); approach(h, 150)
for f in range(30):
    h.user = bits('A') if f < 2 else 0
    h.run(1)
    objs = []
    for k in range(4, 32):
        o = 0x4E30 + k * 0x40
        if p.peek16(o + 0xE) and p.peek(o + 6) != 0xFF:
            objs.append('k%d act%X b6=%02X o27=%d 00..07=%s' % (k, p.peek16(o + 0xE), p.peek(o + 6), p.peek(o + 0x27), p.peek(o, 8).hex()))
    print(f, p.peek(0x41C2), objs)

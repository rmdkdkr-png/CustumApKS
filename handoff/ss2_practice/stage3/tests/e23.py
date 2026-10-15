from tr import *
import sys
ME, DUM = int(sys.argv[1]), int(sys.argv[2])
h = mk('ko', os.path.join(T.WORK, 'e23_%d' % ME)); fight(h, DUM, ME); p = h.p
base = snap(h)
def scan(label, sc, n, every=4):
    restore(h, base); approach(h, 150)
    print('==', label)
    for f in range(n):
        if f in sc: h.user = bits(rl(h, sc[f])) if sc[f] else 0
        h.run(1)
        if f % every == 0:
            objs = []
            for k in range(4, 12):
                o = 0x4E30 + k * 0x40
                if p.peek16(o + 0xE):
                    objs.append('k%d a%03X 06=%02X 1C=%02X 1E=%02X%02X 27=%d 05=%02X 14=%02X' % (k, p.peek16(o + 0xE), p.peek(o + 6), p.peek(o + 0x1C), p.peek(o + 0x1E), p.peek(o + 0x1F), p.peek(o + 0x27), p.peek(o + 5), p.peek(o + 0x14)))
            print('f%-3d c1 %02X act %03X n%d %s' % (f, p.peek(0x59CE), p.peek16(0x4E3E), p.peek(0x41C2), ' | '.join(objs)))
    h.user = 0
scan('idle', {}, 9)
scan('5A', {0: 'A', 2: ''}, 30, 6)
scan('236A', {0: 'D', 4: 'Df', 8: 'f', 12: 'fA', 16: ''}, 90, 4)

from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
lg.practice_set(5, 1); lg.practice_set(7, 0); h.run(40)
print('P1 X', p.peek16(0x59D6), 'P2 X', p.peek16(0x5BD6), 'face', p.peek(0x4E54))
rec(h, {0: 'D', 4: 'Df', 8: 'f', 12: 'fA', 16: ''}, 30)
b = 0x4E30 + 4*0x40
print('obj4 +24 dir %d +27 owner? %d  box %02X%02X' % (p.peek(b+0x24), p.peek(b+0x27), p.peek(b+6), p.peek(b+7)))

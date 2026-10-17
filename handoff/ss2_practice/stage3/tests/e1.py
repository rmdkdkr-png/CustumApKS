import time
from fdh import *
t=time.time()
h = mk('ko'); fight(h, 9, 2)
p = h.p
print('entered', h.frames, 'sec', round(time.time()-t,1))
print('P1 char %02X P2 char %02X' % (p.peek(0x5B51), p.peek(0x5D51)), 'X', p.peek16(0x59D6), p.peek16(0x5BD6), 'pst', pst())
s = snap(h)
pickle.dump(s, open(os.path.join(T.WORK,'e1_fight.pkl'),'wb'))
# 리셋 가운데 후 걸어 붙기
lg.practice_set(7, 0); h.run(30)
print('after reset X', p.peek16(0x59D6), p.peek16(0x5BD6))

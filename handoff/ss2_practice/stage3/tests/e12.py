"""«움직일 수 있음»(0x59CE==0) 이 실제로 다음 동작이 나오는 첫 프레임과 맞나 — 공격 뒤 계속 쥔 입력으로"""
from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
def test(sc, follow, gapv=30, guard=0, n=90, phase=0):
    restore(h, base); lg.practice_set(1, guard)
    approach(h, gapv); h.run(phase)
    s = dict(sc); 
    R = rec(h, s, n)
    c1 = [x['ram'][0x19CE] for x in R]
    a1 = [x['ram'][0x0E3E] | x['ram'][0x0E3F] << 8 for x in R]
    start = next(i for i in range(n) if c1[i])
    free = next(i for i in range(start, n) if c1[i] == 0)
    return start, free, c1, a1
# 1) 다음 동작 = 앉기(↓ 쥠): 첫 0x14 프레임
for guard in (0, 1):
    for phase in (0, 1):
        st, fr, c1, a1 = test({0: 'A', 2: '', 5: 'D'}, None, guard=guard, phase=phase)
        crouch = next((i for i in range(st, len(a1)) if a1[i] == 0x14), None)
        st2, fr2, c2, a2 = test({0: 'A', 2: ''}, None, guard=guard, phase=phase)
        # 2) 다음 동작 = 약베기(A 를 1프레임 간격으로 연타)
        sc = {0: 'A', 2: ''}
        for k in range(6, 80, 4): sc[k] = 'A'; sc[k + 2] = ''
        st3, fr3, c3, a3 = test(sc, None, guard=guard, phase=phase)
        second = next((i for i in range(fr2 - 8, len(c3)) if i > st3 + 4 and c3[i] and not c3[i-1]), None)
        print('guard %d phase %d: start %d free(ctrl0) %d | hold-D crouch at %s | mash-A 2nd start at %s (no-input free %d)' % (guard, phase, st, fr, crouch, second, fr2))

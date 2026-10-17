"""선입력(버퍼): 약베기 경직 중 t 프레임에 다음 입력 — 둘째 동작이 언제 나오나(움직일 수 있는 첫 프레임 F 기준)"""
from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
restore(h, base); approach(h, 150)
s0 = snap(h)
# 기준: 약베기 한 번 — 시작 st, 움직일 수 있는 첫 프레임 F
R = rec(h, {0: 'A', 2: ''}, 60)
c = [x['ram'][0x19CE] for x in R]
st = next(i for i in range(60) if c[i]); F = next(i for i in range(st, 60) if c[i] == 0)
print('5A: start', st, 'free', F)
def second(sc, n=120):
    restore(h, s0)
    R = rec(h, sc, n)
    c = [x['ram'][0x19CE] for x in R]; a = [x['ram'][0x0E3E] | x['ram'][0x0E3F] << 8 for x in R]
    s2 = next((i for i in range(F, n) if c[i] and not c[i - 1]), None)
    return s2, (a[s2] if s2 is not None else None)
for name, mk_sc in (
    ('A 탭(2F)', lambda t: {0: 'A', 2: '', F + t: 'A', F + t + 2: ''}),
    ('A 탭(1F)', lambda t: {0: 'A', 2: '', F + t: 'A', F + t + 1: ''}),
    ('236A', lambda t: {0: 'A', 2: '', F + t - 12: 'D', F + t - 8: 'Df', F + t - 4: 'f', F + t: 'fA', F + t + 4: ''}),
    ('↓ 쥠(앉기)', lambda t: {0: 'A', 2: '', F + t: 'D'}),
):
    out = []
    for t in range(-14, 3):
        if F + t - 12 <= 3 and name == '236A': out.append('%+d:-' % t); continue
        if F + t <= 2: continue
        s2, a2 = second(mk_sc(t))
        out.append('%+d:%s' % (t, ('%+d/%X' % (s2 - F, a2)) if s2 is not None else 'x'))
    print('%-10s' % name, ' '.join(out))

"""연습 대전 1단계 리뷰 고침 시험 — (1) 방향을 쥔 채 연 메뉴는 그 방향을 뗄 때까지 안 친다
(2) Option 과 같은 프레임에 누른 A 는 게임에 안 간다(practice_opt_mask — ph.py 입력이 native.c 입력 콜백과 같게 막음)

사용: t_practice.py 와 같은 환경 변수, python3 t_fix1.py <롬>
"""
import os, sys
from ph import *
ROM = sys.argv[1]; tag = os.path.splitext(os.path.basename(ROM))[0]
W = T.work('fx_' + tag); os.makedirs(W, exist_ok=True)
fails = 0
def ok(c, what):
    global fails
    print(('PASS ' if c else 'FAIL ') + what, flush=True); fails += (not c)

h = PH(ROM, W); p = h.p
to_title(h)
lg.league_hub(0, None, None); lg.league_practice_hub(1, 0); h.run(3)
to_fight(h)
h.run(60)
ok(pst()[0] == 1, '연습 경기 시작')

# (1) 앉은 채(↓) Option 탭 → 메뉴가 열려도 줄·설정이 그대로
before = pst()[3:10]
h.hold('D'); h.run(20)
h.hold('DO'); h.run(4)
h.hold('D'); h.run(100)
s = pst()
ok(s[1] == 2, '↓ 를 쥔 채 Option 탭 → 메뉴 열림 [메뉴 %d]' % s[1])
ok(s[2] == 0 and s[3:10] == before, '쥔 ↓ 는 메뉴에서 안 침 — 줄 0·설정 그대로 [줄 %d · %s → %s]' % (s[2], before, s[3:10]))
h.user = 0; h.run(4); h.press('D', 4, 6)
ok(pst()[2] == 1, '뗀 뒤 새로 누른 ↓ 는 침 [줄 %d]' % pst()[2])
h.press('B', 4, 40)
ok(pst()[1] == 0 and p.peek(0x61D4) != 1, '메뉴 닫힘 [메뉴 %d]' % pst()[1])

# (2) Option+A 를 같은 프레임에 — A 가 게임에 안 간다(아무것도 안 누른 것과 P1 이 같다)
h.run(60)
s0 = h.serialize(); ps0 = h.pstate()
h.user = bits('OA'); h.run(1); h.user = 0; h.run(30)
a = bytes(p.peek(0x5980 + i) for i in range(0x100))
h.unserialize(s0); h.pstate_set(ps0)
h.user = 0; h.run(31)
b = bytes(p.peek(0x5980 + i) for i in range(0x100))
ok(a == b, 'Option+A 같은 프레임 — P1 이 아무것도 안 누른 것과 같음(A 가 게임에 안 감) [다른 바이트 %d]' % sum(x != y for x, y in zip(a, b)))
# 대조: A 만 누르면 P1 이 달라진다(시험이 A 를 볼 수 있는가)
h.unserialize(s0); h.pstate_set(ps0)
h.user = bits('A'); h.run(1); h.user = 0; h.run(30)
c = bytes(p.peek(0x5980 + i) for i in range(0x100))
ok(c != b, '대조: A 만 누르면 P1 이 달라짐 [다른 바이트 %d]' % sum(x != y for x, y in zip(c, b)))

print('%s: %s' % (tag, 'ALL PASS' if not fails else '%d FAIL' % fails), flush=True)
sys.exit(1 if fails else 0)

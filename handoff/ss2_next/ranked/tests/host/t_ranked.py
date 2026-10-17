"""랭크 매치(끝없는 매칭) 허브 시제품 시험 — proto/league.c 를 실제 코어 옆에서(앱 native.c 와 같은 순서: ph.PH).
타이틀 «리그 대전» A → 상대 찾기(H_SEARCH, 메뉴 그대로·입력 막힘·누름 모음) → 5초 기다림 → 취소·다시 → 상대 정함(league_hub_match)
→ «상대 선택» 없이 내 캐릭터 고르기(대진·손잡이 무장) → 경기(대진·단계·상한·배율·배경 확인) → 결판 → «다음 상대»(−3: 리셋 뒤 바로 찾기)
→ 재대결(−4: 같은 상대·같은 손잡이로 내 캐릭터 고르기) → 갈아탄 리그 판(league_hub_go) 바로 찾기 → 예전 흐름(랭크 끔)은 상대 선택 그대로.
사용: python3 t_ranked.py <롬>  (PYTHONPATH 앞에 이 폴더 — 고친 hosttest·ph(상태 칸 수), LEAGUE_HOST_SO=host_proto.so)"""
import os, sys, ctypes as C
import ph
from ph import PH, hub, to_title
import hosttest as T
ROM = sys.argv[1]; tag = os.path.splitext(os.path.basename(ROM))[0]
lg = ph.lg
lg.league_hub_match.argtypes = [C.c_int] * 10; lg.league_hub_match.restype = C.c_int
lg.league_hub_take_ev.restype = C.c_int
W = os.environ.get('LEAGUE_WORK', '/tmp/league_work')
fails = 0
def ok(c, what):
    global fails
    print(('PASS ' if c else 'FAIL ') + what, flush=True); fails += (not c)
def shot(h, name): h.p.shot(os.path.join(W, 'ranked_%s_%s.png' % (tag, name)))
def to_round1(h, limit=6000):
    """내 캐릭터 고르기 뒤 첫 라운드 조작 가능까지 — 카드 화면은 «안 받음»(→ A), 이야기·대사는 A 로 넘김"""
    p = h.p; f = 0
    while f < limit and not T.status()[3]:
        md, sc = p.peek(0x40A7), p.peek(0x41C0)
        if md == 240 and sc == 6 and f % 60 == 0: h.press('R', 4, 10); h.press('A', 4, 30); f += 48; continue
        if f % 30 == 0 and ((md == 241 and sc == 0 and p.peek(0x411A) == 0) or (md == 240 and sc == 8) or (md != 241 and sc not in (2, 4, 6))): h.press('A', 4); f += 4
        else: h.run(1); f += 1
def pick_me(h):
    h.run(30); h.press('A', 4, 200); h.press('A', 4, 200); h.run(240)
def menu_at_row3(h): return h.p.peek(0x40A7) == 240 and h.p.peek(0x41C0) == 0 and h.p.peek(0x624B) == 2
NONE = (C.c_byte * 15)(*([-1] * 15)); ONE = (C.c_byte * 15)(*([1] * 15))

h = PH(ROM, os.path.join(W, 'ranked_' + tag)); p = h.p
lg.league_hub(1, NONE, ONE); lg.league_hub_ranked(1)
to_title(h)
s = hub(); ok(s[0] == 1 and s[14] == 1 and menu_at_row3(h), '리그 판 허브 + 랭크 매치 켬 · 타이틀 셋째 줄')
h.press('A', 4, 30); s = hub()
ok(s[0] == 6 and menu_at_row3(h) and T.status()[0] == 0, '«리그 대전» A → 상대 찾기(허브 6) · 게임 메뉴 그대로 · 무장 없음')
ok(s[12] == 0, '찾기를 시작한 A 는 누름으로 안 셈 (ev %d)' % s[12])
h.press('D', 4, 20); h.press('U', 4, 20); h.press('A', 4, 20); h.press('B', 4, 20); h.press('O', 4, 20); h.press('L', 4, 20); h.press('R', 4, 20)
s = hub(); ok(s[0] == 6 and menu_at_row3(h), '찾는 동안 ↓↑·A·B·OPTION·←→ 를 게임이 안 받음(메뉴 커서·화면 그대로)')
ev = lg.league_hub_take_ev(); ok(ev == 1 | 2 | 4 | 8 | 16 | 32 | 64, '누름은 모두 모임 (ev 0x%02X)' % ev)
ok(lg.league_hub_take_ev() == 0, '가져가면 비움')
h.run(300); s = hub(); ok(s[0] == 6 and menu_at_row3(h), '5초(300프레임) 찾는 중 — 데모로 안 넘어가고 메뉴 그대로')
shot(h, '1_search')
lg.league_hub_search(0); h.run(5); s = hub(); ok(s[0] == 1 and menu_at_row3(h), '취소 → 타이틀 상태(셋째 줄 그대로)')
h.press('A', 4, 30); ok(hub()[0] == 6, '다시 A → 찾기')
# 상대 정함: 나코루루 수라(4,0) · 난도 보통 · 배경 3(화염 사원) · 손잡이 단계 9 · 상한 12 · 배율 0x0119 / 0x00F3
K = (9, 12, 0x0119, 0x00F3)
FLOOR = 7
ok(lg.league_hub_match(4, 0, 1, 3, *K, FLOOR, 1) == 1, 'league_hub_match 받음')
f = 0
while f < 600 and not (p.peek(0x40A7) == 240 and p.peek(0x41C0) == 2 and hub()[7] == 0): h.run(1); f += 1
s = hub(); st = T.status()
ok(s[0] == 3 and s[2] == 4 and s[13] == 4 and st[0] == 1, '상대 선택 없이 1인 대전 캐릭터 고르기 = 내 캐릭터 차례(허브 3, 고른 상대 4) · 무장 (%d프레임)' % f)
ok(s[5] == 0, '머리말은 «캐릭터 선택» 그대로(상대 선택으로 안 바꿈)')
shot(h, '2_pickme')
pick_me(h); to_round1(h)
h.run(30); shot(h, '3_fight')
st = T.status(); s = hub()
ok(st[3] == 1 and (st[12] & 0xF8) == (4 << 4) and s[0] == 4, '경기 시작 · P2 = 나코루루 수라 · 허브 경기')
ok((p.peek(0x5814), p.peek(0x5815), p.peek16(0x57E2), p.peek16(0x57E4)) == K, '손잡이가 램에: 단계 %d · 상한 %d · 배율 %04X/%04X' % (p.peek(0x5814), p.peek(0x5815), p.peek16(0x57E2), p.peek16(0x57E4)))
ok(p.peek(0x5827) == 3, '배경 3(화염 사원) (%d)' % p.peek(0x5827))
ok(p.peek(0x5CF5) == K[0], '첫 라운드 CPU 실시간 단계 = 시작 단계 (%d)' % p.peek(0x5CF5))
lvs = []
for i in range(1500):                                   # P1 가만히 — 맞을수록 게임은 단계를 내린다(E2: 10 → 8 → 6). 바닥 7 아래로는 안 가야
    h.run(1)
    if p.peek(0x40A7) == 241: lvs.append(p.peek(0x5CF5))
    if p.peek(0x5A46) < 40: p.poke(0x5A46, 128)
ok(lvs and min(lvs) >= FLOOR and max(lvs) <= K[1], '실시간 단계 바닥: 1500프레임 동안 %d~%d (바닥 %d · 상한 %d)' % (min(lvs), max(lvs), FLOOR, K[1]))
f = 0; wait = None
while f < 30000 and not T.status()[4]:
    if p.peek(0x40A7) == 241 and p.peek(0x5824) == 0 and p.peek(0x5A46) > 0 and p.peek(0x5C46) > 0:
        if wait is None: wait = f + 120
        if f >= wait: p.poke(0x5C46, 0); wait = None
    if f % 60 == 0 and p.peek(0x40A7) != 241: h.press('A', 2)
    else: h.run(1)
    f += 1
st = T.status()
ok(st[4] == 1 and st[5] & 0x40 and (st[6], st[7]) == (2, 0) and st[9] == 2 and st[17] == 60, '결판 P1 승 2:0 · 2선승 · 60초')
ok((st[18], st[21], st[19], st[20]) == K, '결판 기록의 손잡이 = 요청(단계 %d · 상한 %d · %04X/%04X) — 정산의 «난도 확인»을 이것으로' % (st[18], st[21], st[19], st[20]))
# 다음 상대: 리셋 뒤 바로 찾기
p.lib.retro_reset(); lg.league_hub_return(-3)
f = 0
while f < 1500 and hub()[0] != 6: h.run(1); f += 1
h.run(10); s = hub()
ok(s[0] == 6 and menu_at_row3(h) and T.status()[0] == 0 and s[8] == 1, '«다음 상대»(−3): 리셋 뒤 타이틀 셋째 줄에서 바로 찾기(%d프레임) · 무장 풀림' % f)
shot(h, '4_next_search')
# 재대결: 정해 둔 상대(나코루루)·손잡이 그대로
p.lib.retro_reset(); lg.league_hub_return(-4)
f = 0
while f < 1800 and not (hub()[0] == 3 and p.peek(0x41C0) == 2 and hub()[7] == 0): h.run(1); f += 1
s = hub(); ok(s[0] == 3 and s[2] == 4 and T.status()[0] == 1, '재대결(−4): 리셋 뒤 같은 상대로 내 캐릭터 차례까지 자동(%d프레임)' % f)
pick_me(h); to_round1(h)
ok(T.status()[3] == 1 and (T.status()[12] & 0xF8) == (4 << 4) and (p.peek(0x5814), p.peek(0x5815), p.peek16(0x57E2), p.peek16(0x57E4)) == K,
   '재대결 경기: 같은 상대·같은 손잡이')
# 대진 전에 취소(타이틀로) 뒤 랭크 아닌 무장에 손잡이가 새지 않음
p.lib.retro_reset(); lg.league_hub_return(-1)
f = 0
while f < 1500 and hub()[0] != 1: h.run(1); f += 1
p.poke(0x5814, 0x33); p.poke(0x57E2, 0x44)
lg.league_arm(11, 0, 1, 2, 60, 2)        # 예전 리그 경기(2단계 화면에서 시작하는 경기와 같은 무장) — league_cpu 를 안 불렀다
h.run(5); ok(p.peek(0x5814) == 0x33 and p.peek(0x57E2) == 0x44, '손잡이 없이 무장하면 손잡이 바이트를 안 씀(앞 경기 값이 안 샘)')
lg.league_cpu(2, 5, 0xC0, 0x140, 0); lg.league_arm(11, 0, 1, 2, 60, 2); h.run(5)
ok((p.peek(0x5814), p.peek(0x5815), p.peek16(0x57E2), p.peek16(0x57E4)) == (2, 5, 0xC0, 0x140), 'league_cpu 다음 무장은 그 손잡이(체크포인트 이어 하기 길)')
p.poke(0x5814, 0x33); lg.league_arm(11, 0, 1, 2, 60, 2); h.run(5); ok(p.peek(0x5814) == 0x33, 'league_cpu 는 한 번만(그다음 무장엔 안 샘)')
lg.league_disarm()
# 갈아탄 리그 판: 로고·메뉴 넘겨 바로 찾기
p.lib.retro_reset(); lg.league_hub(1, NONE, ONE); lg.league_hub_ranked(1); lg.league_hub_go()
f = 0
while f < 1500 and hub()[0] != 6: h.run(1); f += 1
ok(hub()[0] == 6 and menu_at_row3(h), '갈아탄 리그 판(league_hub_go): 전원 → 셋째 줄에서 바로 찾기 (%d프레임)' % f)
# 상태 저장 직전 되돌리기(찾는 중에도 셋째 줄 글자를 원래대로)
lg.league_hub_before_save(); kind = 1 if h.ent(1, 14, 7) & 0x1FF == 0x1BB else 2
ok((h.ent(1, 14, 5) & 0x1FF) == 0x1BF if kind == 2 else True, '찾는 중 저장 직전: 셋째 줄 원래 글자')
h.run(2)
# 둘 다(dual): 리그 쪽이면 찾기, 연습 쪽이면 갈아타기 요청
lg.league_hub_search(0); h.run(2); lg.league_hub_dual(1); h.run(2)
h.press('A', 4, 30); ok(hub()[0] == 6, '둘 다 켬 · 셋째 줄 «리그 대전» A → 찾기')
lg.league_hub_search(0); h.run(5); h.press('R', 4, 20); h.press('A', 4, 20)
v = (C.c_int * 6)(); lg.league_hub_dual_status(v)
ok(hub()[0] == 1 and v[2] == 2, '둘 다 · ▶ «연습 대전» A → 찾기 아님, 갈아타기 요청(연습)')
lg.league_hub_handoff_clear(); lg.league_hub_dual(0)
# 예전 흐름(랭크 끔): 상대 선택
p.lib.retro_reset(); lg.league_hub(1, (C.c_byte * 15)(*([-1] * 8 + [1] + [-1] * 6)), ONE)
f = 0
lg.league_hub_return(-1)
while f < 1500 and hub()[0] != 1: h.run(1); f += 1
h.press('A', 4, 240); ok(hub()[0] == 2 and p.peek(0x41C0) == 2, '랭크 끔: 예전처럼 «리그 대전» A → 상대 선택(허브 2)')
print('%s: %s' % (tag, 'ALL PASS' if not fails else '%d FAIL' % fails))

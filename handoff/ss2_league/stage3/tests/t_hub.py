"""게임 속 리그(허브) 흐름 시험 — league.c 를 실제 코어 옆에서, 앱 native.c 와 같은 순서로(입력 콜백에서 허브가 받는 A 를 지우고,
retro_run 뒤 league_vram + league_tick_hub) 돌린다.
타이틀 «리그 대전» 글자 → 그 칸 A → 1인 대전 캐릭터 고르기(머리말 «상대 선택») → 상대 고르기 → 머리말 원래대로 → 내 캐릭터·검질·카드
→ 경기(대진·규칙·난도 확인) → 결판 → 리셋 뒤 타이틀 «리그 대전» 칸으로 돌아오기(+ 재대결 자동 진입)까지.
사용: python3 t_hub.py <롬>   (PYTHONPATH: handoff/ss2_league · stage1/tests, LEAGUE_HOST_SO=league.c 호스트 .so)"""
import os, sys, ctypes as C, hosttest as T
ROM = sys.argv[1]; tag = os.path.splitext(os.path.basename(ROM))[0]
lg = T.lg
lg.league_tick_hub.argtypes = [C.c_void_p, C.c_size_t, C.c_int]
lg.league_vram.argtypes = [C.c_void_p, C.c_void_p]
ROSTER = {11: (0, 1), 3: (1, 1), 4: (0, 0), 2: (0, 1), 9: (1, 1), 5: (0, 0), 6: (0, 0), 7: (0, 0), 0: (1, 2), 8: (1, 2), 13: (0, 2), 14: (1, 2)}
sty = (C.c_byte * 15)(*[ROSTER[c][0] if c in ROSTER else -1 for c in range(15)])
dif = (C.c_byte * 15)(*[ROSTER[c][1] if c in ROSTER else 1 for c in range(15)])

class Hub(T.Harness):
    def __init__(self, rom, wd):
        super().__init__(rom, wd)
        L = self.p.lib
        for f in ('retro_ngp_charram', 'retro_ngp_scrollram'): getattr(L, f).restype = C.c_void_p
    def run(self, n=1):
        for _ in range(n):
            on = C.c_int.in_dll(lg, 'league_ovr_on').value
            blk = C.c_int.in_dll(lg, 'league_in_block').value
            self.p.mask = C.c_int.in_dll(lg, 'league_ovr_mask').value if on else (self.user & ~blk)
            self.p.run(1)
            lg.league_vram(self.p.lib.retro_ngp_charram(), self.p.lib.retro_ngp_scrollram())
            lg.league_tick_hub(self.p._ramp, self.p._rams, self.user)
def hub():
    v = (C.c_int * 9)(); lg.league_hub_status(v); return list(v)
ST = ['꺼짐', '타이틀', '상대 고르기', '내 캐릭터', '경기', '타이틀로']
fails = 0
def ok(c, what):
    global fails
    print(('PASS ' if c else 'FAIL ') + what, flush=True); fails += (not c)

h = Hub(ROM, T.work('hub_' + tag)); p = h.p
lg.league_hub(1, sty, dif)
h.run(420); h.press('A', 4, 150)                       # 타이틀 → 메뉴(사람이 누른 A)
h.press('D', 4, 30); h.press('D', 4, 30)                # 셋째 칸(원래 2인 대전)
h.run(10); p.shot(T.work('hub_%s_1_menu.png' % tag))
s = hub(); ok(s[0] == 1 and p.peek(0x624B) == 2, '타이틀 메뉴 셋째 칸에 커서 · 허브 타이틀 상태 (글자 바꿈 %d)' % s[4])
h.press('A', 4, 240)                                    # «리그 대전» 선택
s = hub(); ok(s[0] == 2 and p.peek(0x40A7) == 240 and p.peek(0x41C0) == 2, '리그 대전 → 1인 대전 캐릭터 고르기 · 상대 고르기 상태')
h.run(30); p.shot(T.work('hub_%s_2_pickopp.png' % tag))
HT = [0x150 + i for i in range(10)] + [0x15A + i for i in range(10)]   # 머리말 타일(윗줄 10 · 아랫줄 10)
def hdr_tiles(): return [C.string_at(p.lib.retro_ngp_charram() + t * 16, 16) for t in HT]
kind = 1 if '_ko' in tag else 2                         # 한글판 «캐릭터 선택» · 순정판 «十五士選択»
s = hub(); mid = hdr_tiles()
ok(s[5] == kind, '상대 고르기 머리말을 «상대 선택» 으로 바꿈 (판 %d, 기대 %d)' % (s[5], kind))
h.press('A', 4, 60)                                     # 가운데 아수라(8) — 리그 상대(검은달)
s = hub(); ok(s[0] == 3 and s[2] == 8 and p.peek(0x41C0) == 2, '상대 고르기에서 A → 아수라(8) 상대 고름, 화면은 캐릭터 고르기 그대로(내 캐릭터 차례)')
aft = hdr_tiles(); chg = [i for i in range(20) if mid[i] != aft[i]]
want = list(range(6)) + list(range(10, 16)) if kind == 1 else list(range(20))   # 한글판 «캐릭터» 만 · 순정판 열 칸 전부
ok(chg == want, '상대를 고른 뒤 머리말 타일 원래대로 (되돌린 칸 %d개, 기대 %d개)' % (len(chg), len(want)))
st = T.status(); ok(st[0] == 1, '고른 상대로 대진 무장')
p.shot(T.work('hub_%s_3_pickme.png' % tag))
h.press('D', 4, 30); h.press('D', 4, 30); h.press('R', 4, 30); h.press('R', 4, 30)   # 내 캐릭터: 우쿄(11)
h.press('A', 4, 200); h.press('A', 4, 200)             # 캐릭터·유파
h.run(240); h.press('A', 4, 240); h.press('R', 4, 30); h.press('A', 4, 200)   # 카드 안 받음
f = 0
while f < 6000 and not T.status()[3]:
    if f % 60 == 0 and p.peek(0x40A7) != 241: h.press('A', 2)
    else: h.run(1)
    f += 1
h.run(60); p.shot(T.work('hub_%s_4_fight.png' % tag))
s = hub(); st = T.status()
ok(s[0] == 4 and st[3] == 1 and (st[12] & 0xF8) == (8 << 4 | 1 << 3) and p.peek(0x57D5) == 11, '경기 시작 · P2 = 아수라 나찰 · 내 캐릭터 우쿄 · 허브 경기 상태')
f = 0; wait = None
while f < 30000 and not T.status()[4]:
    if p.peek(0x40A7) == 241 and p.peek(0x5824) == 0 and p.peek(0x5A46) > 0 and p.peek(0x5C46) > 0:
        if wait is None: wait = f + 120
        if f >= wait: p.poke(0x5C46, 0); wait = None
    if f % 60 == 0 and p.peek(0x40A7) != 241: h.press('A', 2)
    else: h.run(1)
    f += 1
st = T.status()
ok(st[4] == 1 and st[5] & 0x40 and (st[6], st[7]) == (2, 0) and st[9] == 2 and st[17] == 60 and st[18] == 7, '결판 P1 승 2:0 · 2선승 · 60초 · CPU 단계 7(어려움)')
# 결과 카드를 닫은 뒤: 리셋 + 타이틀로(native.c nativeLeagueHubReturn 과 같은 순서)
p.lib.retro_reset(); lg.league_hub_return(-1)
f = 0
while f < 1500 and hub()[0] != 1: h.run(1); f += 1
h.run(20); p.shot(T.work('hub_%s_5_back.png' % tag))
s = hub(); ok(s[0] == 1 and p.peek(0x624B) == 2 and T.status()[0] == 0 and s[8] == 1, '리셋 뒤 타이틀 메뉴 «리그 대전» 칸으로 돌아옴(%d프레임) · 무장 풀림 · 돌려보낸 횟수 %d' % (f, s[8]))
# 리그 상대가 없는 캐릭터는 안 골라짐 — 가운데 아수라(8)에서 오른쪽 모로즈미(10)
h.press('A', 4, 0); f = 0
while f < 400 and not (p.peek(0x40A7) == 240 and p.peek(0x41C0) == 2): h.run(1); f += 1
h.press('A', 4, 30); s = hub()                            # 캐릭터 고르기가 뜨자마자 한 번 더(두 번 누름) — 머리말이 바뀌기 전이라 안 골라짐
ok(s[0] == 2 and p.peek(0x41C0) == 2 and T.status()[0] == 0, '다시 리그 대전 → 상대 고르기 · 뜨자마자 누른 A(머리말 바뀌기 전)는 안 골라짐')
h.run(30); h.press('R', 4, 30); h.run(10); hv = hub()[1]
h.press('A', 4, 60); s = hub(); ok(hv == 10 and s[0] == 2 and T.status()[0] == 0 and p.peek(0x41C0) == 2, '리그 상대가 없는 모로즈미(10)에서 A → 안 골라짐(상대 고르기 그대로, 게임도 그대로) [커서 %d · 상태 %d · 무장 %d · SCR %d]' % (hv, s[0], T.status()[0], p.peek(0x41C0)))
h.press('D', 4, 30); h.press('L', 4, 30); h.run(10); hv = hub()[1]
h.press('A', 4, 60); s = hub(); ok(hv == 14 and s[0] == 3 and s[2] == 14 and T.status()[0] == 1, '가운데 무작위 칸 = 숨은 상대 유가(14, 고르기 판에 없음)에서 A → 유가 상대로 무장 [커서 %d · 상태 %d · 고름 %d]' % (hv, s[0], s[2]))
# 이 게임은 캐릭터 고르기에서 B 로 타이틀에 못 간다 — 그만두기는 앱이 리셋해서(league_hub_return(-1)) 타이틀로
p.lib.retro_reset(); lg.league_hub_return(-1)
f = 0
while f < 1500 and hub()[0] != 1: h.run(1); f += 1
h.run(20); s = hub(); ok(s[0] == 1 and p.peek(0x624B) == 2 and T.status()[0] == 0, '상대를 고른 뒤 대진 전에 그만두기(리셋) → 무장 풀리고 타이틀 «리그 대전» 칸(%d프레임)' % f)
h.press('A', 4, 240); h.run(30); h.press('A', 4, 60); s = hub()
ok(s[0] == 3 and s[2] == 8 and T.status()[0] == 1, '다시 리그 대전 → 아수라 골라 내 캐릭터 차례')
# 재대결: 결판 뒤 같은 상대로 바로
p.lib.retro_reset(); lg.league_hub_return(8)            # (경기 없이) 재대결 경로만 확인
f = 0
while f < 1800 and not (hub()[0] == 3 and p.peek(0x41C0) == 2 and hub()[7] == 0): h.run(1); f += 1
s = hub(); ok(s[0] == 3 and s[2] == 8 and p.peek(0x41C0) == 2 and T.status()[0] == 1, '재대결: 리셋 뒤 메뉴 → 리그 대전 → 같은 상대(아수라)로 내 캐릭터 차례까지 자동(%d프레임)' % f)
print('%s: %s' % (tag, 'ALL PASS' if not fails else '%d FAIL' % fails))

"""게임 속 리그(허브) 흐름 시험 — league.c 를 실제 코어 옆에서, 앱 native.c 와 같은 순서로(입력 콜백에서 허브가 받는 A 를 지우고,
retro_run 뒤 league_vram + league_tick_hub) 돌린다.
타이틀 «리그 대전» 글자 → 그 칸 A → 1인 대전 캐릭터 고르기(머리말 «상대 선택») → 상대 고르기 → 머리말 원래대로 → 내 캐릭터·검질·카드
(오른쪽 세로 이름 칸 = 배경 이름 → 내 컬러 이름, 미리보기 그림 색, B = 2P색으로 확정) → 경기(대진·규칙·난도·배경·컬러 확인) → 결판 → 리셋 뒤 타이틀 «리그 대전» 칸으로 돌아오기(+ 재대결 자동 진입)까지.
사용: python3 t_hub.py <롬>   (PYTHONPATH: handoff/ss2_league · stage1/tests, LEAGUE_HOST_SO=league.c 호스트 .so)"""
import os, sys, ctypes as C, hosttest as T
ROM = sys.argv[1]; tag = os.path.splitext(os.path.basename(ROM))[0]
lg = T.lg
lg.league_tick_hub.argtypes = [C.c_void_p, C.c_size_t, C.c_int]
lg.league_vram.argtypes = [C.c_void_p, C.c_void_p, C.c_void_p]
lg.league_hub_look.argtypes = [C.c_void_p, C.c_int, C.c_int]
lg.league_palremap_fn.argtypes = [C.c_void_p]
ROSTER = {11: (0, 1), 3: (1, 1), 4: (0, 0), 2: (0, 1), 9: (1, 1), 5: (0, 0), 6: (0, 0), 7: (0, 0), 0: (1, 2), 8: (1, 2), 13: (0, 2), 14: (1, 2)}
sty = (C.c_byte * 15)(*[ROSTER[c][0] if c in ROSTER else -1 for c in range(15)])
dif = (C.c_byte * 15)(*[ROSTER[c][1] if c in ROSTER else 1 for c in range(15)])
HOME = {11: 2, 3: 3, 4: 1, 2: 0, 9: 4, 5: 1, 6: 5, 7: 0, 0: 5, 8: 6, 13: 6, 14: 7}   # League.HOME_STAGE 와 같게(캐릭터 → 기본 배경)
home = (C.c_byte * 15)(*[HOME.get(c, -1) for c in range(15)])
STAGE_ID = {0: 0, 1: 6, 2: 2, 3: 5, 4: 4, 5: 10, 6: 12, 7: 13}   # 배경 번호(R_BOUT) → 게임이 고른 배경 id(0x5778, 실측)
UKYO_SURA = ((0xBDF, 0xE60, 0x500), (0xBBF, 0x40A, 0x005))      # 우쿄 수라 기본 · 2P색(팔레트 0 의 색 1~3)

class Hub(T.Harness):
    def __init__(self, rom, wd):
        super().__init__(rom, wd)
        L = self.p.lib
        for f in ('retro_ngp_charram', 'retro_ngp_scrollram', 'retro_ngp_palram'): getattr(L, f).restype = C.c_void_p
        # 코어 팔레트 바꿔 쓰기(retro_ngp_palremap) — 앱 native.c 처럼 있으면 넘기고, 옛 코어면 NULL(프레임 뒤 고쳐 쓰기만)
        self.prf = C.cast(L.retro_ngp_palremap, C.c_void_p).value if hasattr(L, 'retro_ngp_palremap') else None
        self.reverts = None                               # 세면: 프레임 뒤(허브가 고치기 전) 팔레트 0 이 기본 색이었던 프레임 수
    def run(self, n=1):
        for _ in range(n):
            on = C.c_int.in_dll(lg, 'league_ovr_on').value
            blk = C.c_int.in_dll(lg, 'league_in_block').value
            self.p.mask = C.c_int.in_dll(lg, 'league_ovr_mask').value if on else (self.user & ~blk)
            self.p.run(1)
            if self.reverts is not None and self.p.peek(0x40A7) == 241 and pal0() == self.base: self.reverts += 1
            lg.league_vram(self.p.lib.retro_ngp_charram(), self.p.lib.retro_ngp_scrollram(), self.p.lib.retro_ngp_palram())
            lg.league_palremap_fn(self.prf)
            lg.league_tick_hub(self.p._ramp, self.p._rams, self.user)
def hub():
    v = (C.c_int * 12)(); lg.league_hub_status(v); return list(v)
def pal0():
    b = C.string_at(p.lib.retro_ngp_palram(), 8); return tuple(b[2 + j * 2] | (b[3 + j * 2] << 8) for j in range(3))
VT = [0x130 + i for i in range(18)]                     # 오른쪽 세로 이름 칸(둘째 판 3~11줄 × 17·18칸)이 가리킬 우리 글자 타일
def vp_cells():
    scr = C.string_at(p.lib.retro_ngp_scrollram() + 0x800, 0x800)
    return [(scr[((3 + i // 2) * 32 + 17 + (i & 1)) * 2] | scr[((3 + i // 2) * 32 + 17 + (i & 1)) * 2 + 1] << 8) & 0x1FF for i in range(18)]
def vp_glyph(): return C.string_at(p.lib.retro_ngp_charram() + 0x130 * 16, 18 * 16)
def ink(g): return sum(1 for k in range(0, len(g), 2) for x in range(8) if (((g[k] | g[k + 1] << 8) >> (14 - 2 * x)) & 3) == 1)   # 글자 칠(색 1) 점 수
def px(png, c, tol=12):                                 # 찍힌 화면에서 12비트 색 c(0x0BGR, 4비트 × 17)인 점 수
    from PIL import Image
    r0, g0, b0 = (c & 15) * 17, ((c >> 4) & 15) * 17, ((c >> 8) & 15) * 17
    return sum(1 for (r, g, b) in Image.open(png).convert('RGB').getdata() if abs(r - r0) <= tol and abs(g - g0) <= tol and abs(b - b0) <= tol)
ST = ['꺼짐', '타이틀', '상대 고르기', '내 캐릭터', '경기', '타이틀로']
fails = 0
def ok(c, what):
    global fails
    print(('PASS ' if c else 'FAIL ') + what, flush=True); fails += (not c)

h = Hub(ROM, T.work('hub_' + tag)); p = h.p
lg.league_hub(1, sty, dif); lg.league_hub_look(home, -1, 0)
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
s = hub(); st0 = s[9]
g_home = vp_glyph()                                     # 커서 = 아수라(8) — 상대 기본 배경 6(마계 제단)
ok(vp_cells() == VT and ink(g_home) > 60, '상대 고르기 오른쪽 세로 칸 = 우리 글자 타일 0x130~0x141(배경 이름, 칠 점 %d)' % ink(g_home))
gl = {}
for k in [-2] + list(range(8)) + [-1]:                  # B 열 번: 무작위 → 0 … 7 → 상대 기본(한 바퀴)
    h.press('B', 4, 20); gl[k] = vp_glyph()
ok(len(set(gl[k] for k in range(-2, 8) if k != -1)) == 9 and gl[6] == g_home and gl[-1] == g_home and vp_cells() == VT,
   'B 한 바퀴: 배경 8개·무작위 글자가 모두 다르고, «상대 기본» = 아수라 기본 배경(마계 제단) 글자 · 다시 상대 기본으로 돌아옴')
for i in range(3): h.press('B', 4, 20)                 # B: 배경 — 상대 기본 → 무작위 → 0 → 1(숲속 호숫가)
s = hub(); ok(st0 == -1 and s[9] == 1 and s[0] == 2 and p.peek(0x41C0) == 2 and vp_glyph() == gl[1], '상대 고르기에서 B 세 번 → 배경 «상대 기본» → 무작위 → 0 → 1(숲속 호숫가), 오른쪽 칸 글자도 1, 게임 화면 그대로 [%d → %d]' % (st0, s[9]))
h.user = 1 << 1; h.run(20); h.user = 0; h.run(40); s = hub()   # 패드 «A+B»(libretro Y — 코어가 A+B 로 접음): 게임이 A 로 받아 허브를 건너뛰면 안 됨
ok(s[0] == 2 and p.peek(0x41C0) == 2 and T.status()[0] == 0, '상대 고르기에서 패드 «A+B» 버튼 → 게임이 안 받음(상대 고르기 그대로, 무장 없음) [상태 %d · SCR %d]' % (s[0], p.peek(0x41C0)))
h.press('A', 4, 60)                                     # 가운데 아수라(8) — 리그 상대(검은달)
s = hub(); ok(s[0] == 3 and s[2] == 8 and p.peek(0x41C0) == 2, '상대 고르기에서 A → 아수라(8) 상대 고름, 화면은 캐릭터 고르기 그대로(내 캐릭터 차례)')
aft = hdr_tiles(); chg = [i for i in range(20) if mid[i] != aft[i]]
want = list(range(6)) + list(range(10, 16)) if kind == 1 else list(range(20))   # 한글판 «캐릭터» 만 · 순정판 열 칸 전부
ok(chg == want, '상대를 고른 뒤 머리말 타일 원래대로 (되돌린 칸 %d개, 기대 %d개)' % (len(chg), len(want)))
st = T.status(); ok(st[0] == 1, '고른 상대로 대진 무장')
p.shot(T.work('hub_%s_3_pickme.png' % tag))
s = hub(); ok(s[11] == 1, '고른 상대로 무장할 때 배경 1 을 함께 (%d)' % s[11])
gc0 = vp_glyph()
ok(vp_cells() == VT and gc0 not in gl.values() and ink(gc0) > 30, '내 캐릭터 고르기 오른쪽 세로 칸 = 컬러 이름(«기본», 배경 글자와 다름)')
h.press('D', 4, 30); h.press('D', 4, 30); h.press('R', 4, 30); h.press('R', 4, 30)   # 내 캐릭터: 우쿄(11)
h.run(4); pv0 = pal0()
h.press('O', 4, 20); s = hub()                           # 옵션: 컬러 1(2P색)
h.run(2); p.shot(T.work('hub_%s_3b_color1.png' % tag)); gc1 = vp_glyph()
ok(s[10] == 1 and p.peek(0x41C0) == 2 and gc1 != gc0, '내 캐릭터 고르기에서 옵션 → 컬러 1(2P색), 오른쪽 칸 글자 바뀜, 게임 화면 그대로 [컬러 %d · SCR %d]' % (s[10], p.peek(0x41C0)))
ok(pv0 == UKYO_SURA[0] and pal0() == UKYO_SURA[1] and px(T.work('hub_%s_3b_color1.png' % tag), UKYO_SURA[1][1]) >= 20,
   '미리보기 그림 = 우쿄 2P색으로 바로 바뀜(팔레트 0 %s → %s, 화면에 2P색 점 %d)' % ('/'.join('%03x' % c for c in pv0), '/'.join('%03x' % c for c in pal0()), px(T.work('hub_%s_3b_color1.png' % tag), UKYO_SURA[1][1])))
h.press('O', 4, 20); s = hub(); c2 = pal0()             # 컬러 2(만든 색)
ok(s[10] == 2 and c2 not in UKYO_SURA and c2[0] == UKYO_SURA[0][0] and vp_glyph() not in (gc0, gc1), '옵션 한 번 더 → 컬러 2: 미리보기 = 만든 색(가장 밝은 색은 그대로) [%s]' % '/'.join('%03x' % c for c in c2))
h.press('B', 40, 160); s = hub()                        # B(길게 눌러도): 2P색으로 확정 → 검질 고르기(B 가 «뒤로» 로 새지 않음)
ok(s[10] == 1 and p.peek(0x41C0) == 4 and pal0() == UKYO_SURA[1] and vp_cells() == VT and vp_glyph() == gc1,
   'B → 2P색으로 캐릭터 확정 · 검질 고르기(B 를 길게 눌러도 뒤로 안 감) · 미리보기 2P색 · 오른쪽 칸 «2P색» [컬러 %d · SCR %d]' % (s[10], p.peek(0x41C0)))
h.press('A', 4, 200)                                    # 유파
h.run(240); h.press('A', 4, 240); h.press('R', 4, 30); h.press('A', 4, 200)   # 카드 안 받음
f = 0
while f < 6000 and not T.status()[3]:
    if f % 60 == 0 and p.peek(0x40A7) != 241: h.press('A', 2)
    else: h.run(1)
    f += 1
h.run(60); p.shot(T.work('hub_%s_4_fight.png' % tag))
h.base = UKYO_SURA[0]; h.reverts = 0                    # 여기부터 결판까지: 게임이 몸 팔레트를 다시 써도 원래 색이 안 새는가
ok(p.peek(0x5827) == 1 and p.peek(0x5778) == STAGE_ID[1], '경기 배경 = 고른 배경 1(숲속 호숫가): 판 번호 %d · 배경 id %d' % (p.peek(0x5827), p.peek(0x5778)))
n2p = px(T.work('hub_%s_4_fight.png' % tag), UKYO_SURA[1][1])
w2p = 0                                                 # 맞을 때 번쩍임처럼 게임이 잠깐 다른 색을 쓰는 중일 수 있어 몇 프레임 안에 보면 된다
while w2p < 120 and pal0() != UKYO_SURA[1]: h.run(1); w2p += 1
ok(pal0() == UKYO_SURA[1] and n2p >= 20, '내 컬러 = 우쿄 수라 2P색 (팔레트 0 = %s, %d프레임 뒤 · 찍힌 경기 화면에 2P색 점 %d)' % (' '.join('%03x' % c for c in pal0()), w2p, n2p))
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
nrev = h.reverts; h.reverts = None
if h.prf: ok(nrev == 0, '경기 내내 내 컬러가 원래 색으로 안 샘 — 코어 팔레트 바꿔 쓰기(retro_ngp_palremap): 원래 색 프레임 %d' % nrev)
else: print('INFO 옛 코어(retro_ngp_palremap 없음) — 프레임 뒤 고쳐 쓰기만: 원래 색이 보인 프레임 %d' % nrev)
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

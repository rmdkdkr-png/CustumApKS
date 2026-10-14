"""연습 대전 1단계 시험 — league.c + practice.c 를 실제 코어 옆에서, 앱 native.c 와 같은 순서로 돌린다
(입력 콜백 = ovr ? mask : (사용자 & ~(league_in_block | practice_in_block)) | league_in_or | practice_in_or,
 retro_run 뒤 league_vram → league_tick_hub → practice_vram → practice_tick → 나가기 요청이면 retro_reset + league_practice_return).
런어헤드 2 · 프레임 생성 켬(앱과 같게 — hosttest.Harness).  설계 0단계 5-가 P-1 … P-15 (P-16 은 2단계).

사용: PYTHONPATH=<handoff/ss2_league>:<handoff/ss2_league/stage1/tests>:<이 폴더> LEAGUE_HOST_SO=<league.c+practice.c 호스트 .so>
      LEAGUE_WORK=<작업 폴더(찍힌 화면은 여기 — 롬에서 나온 그림이라 저장소 밖)> python3 t_practice.py <롬> [빠르게]
"""
import os, sys, random, re, ctypes as C
from ph import *
ROM = sys.argv[1]; tag = os.path.splitext(os.path.basename(ROM))[0]
QUICK = len(sys.argv) > 2
KO = '_ko' in tag
KIND = 1 if KO else 2
W = T.work('pr_' + tag); os.makedirs(W, exist_ok=True)
CPP = os.environ.get('PRACTICE_CPP', '')
fails = 0; notes = []
def ok(c, what):
    global fails
    print(('PASS ' if c else 'FAIL ') + what, flush=True); fails += (not c)
def info(s): print('INFO ' + s, flush=True)
def shot(name): h.p.shot(os.path.join(W, '%s_%s.png' % (tag, name)))
def carray(path, name):
    t = open(path).read(); m = re.search(r'%s\[\d+\] = \{([^}]*)\}' % name, t)
    return bytes(int(x, 16) for x in re.findall(r'0x([0-9A-Fa-f]{2})', m.group(1)))
YEONSEUP = carray(os.path.join(CPP, 'practice_glyphs.h'), 'PG_MENU_YEONSEUP') if CPP else None
RIGEU = carray(os.path.join(CPP, 'hub_glyphs.h'), 'HUB_MENU_RIGEU') if CPP else None
PRACTICE_IDS = [0x1C1, 0x1B9, 0x1B5, 0x1C5, 0x1CB, 0x1CC, 0x1CA, 0x1C9]
LEAGUE_IDS = [0x1C2, 0x1C9, 0x1C3, 0x1CF, 0x1B8, 0x1D2, 0x1B0]

h = PH(ROM, W); p = h.p
pk = p.peek; pk16 = p.peek16
def plane_tiles(scr, pl, r, c0, n): return [(scr[pl * 0x800 + (r * 32 + c) * 2] | scr[pl * 0x800 + (r * 32 + c) * 2 + 1] << 8) & 0x1FF for c in range(c0, c0 + n)]
def wait_until(cond, limit):
    for f in range(limit):
        if cond(): return f
        h.run(1)
    return None if not cond() else limit
def live(): return pk(0x40A7) == 241 and pk(0x411A) == 1 and pk(0x5824) == 0
def reset_wait(pos=-1, limit=260):
    n0 = pst()[11]; lg.practice_set(7, pos)
    return wait_until(lambda: pst()[11] > n0, limit)
def gap(): return pk16(0x4E78) - pk16(0x4E38)
def approach(g):
    reset_wait(0); h.run(4)
    h.hold('R'); k = 0
    while gap() > g and k < 400: h.run(1); k += 1
    h.user = 0; h.run(10)
PRE = {}
def pre_hook(hh):
    PRE['hp1'] = pk(0x5A46); PRE['hp2'] = pk(0x5C46); PRE['c1'] = pk(0x5A97); PRE['c2'] = pk(0x5C97)
    PRE['st2'] = pk(0x5BC9); PRE['ctrl2'] = pk(0x5BCE); PRE['hs'] = pk(0x5DC7); PRE['pause'] = pk(0x61D4)
h.pre_hook = pre_hook
def scenario(script, n):
    """script: {프레임: 버튼(F/B 상대 방향)}. 돌려줌: 닿음·맞음·가드·실제 대미지(바닥 전)·콤보 최대"""
    r = dict(contact=0, hit=0, block=0, dmg=0, cmax=0, hs_prev=0)
    post_hp = pk(0x5C46); c_prev = pk(0x5C97)
    for f in range(n):
        if f in script: h.user = bits(rel(h, script[f])) if script[f] else 0
        h.run(1)
        if PRE['hs'] and not r['hs_prev']:
            r['contact'] += 1
            if PRE['c2'] <= c_prev and PRE['st2'] & 0x18: r['block'] += 1
        if PRE['c2'] > c_prev: r['hit'] += PRE['c2'] - c_prev
        r['hs_prev'] = PRE['hs']; c_prev = PRE['c2']; r['cmax'] = max(r['cmax'], PRE['c2'])
        if PRE['hp2'] < post_hp: r['dmg'] += post_hp - PRE['hp2']
        post_hp = pk(0x5C46)
    h.user = 0
    return r
def finish_select(limit=5000):
    """내 캐릭터 A · 유파 A → (카드 화면이 뜨면 → 로 «안 받음» + A — 카드는 사용자가 고르는 화면이라 허브는 안 누른다) → 연습 시작까지. 돌려줌: (프레임, 카드 화면 손댄 수)"""
    h.press('A', 4, 160); h.press('A', 4, 0)
    f = 0; cards = 0
    while f < limit and not pst()[0]:
        if pk(0x40A7) == 240 and pk(0x41C0) == 6 and f % 60 == 30: h.press('R', 4, 0); h.press('A', 4, 0); f += 8; cards += 1; continue
        h.run(1); f += 1
    return (f if pst()[0] else None), cards
def open_menu():
    h.press('O', 3, 0)
    return wait_until(lambda: pst()[1] == 2, 40)
def close_menu():
    h.press('B', 2, 0)
    return wait_until(lambda: pk(0x61D4) == 0 and pst()[1] == 0, 60)
def menu_go(row):
    while pst()[2] != row: h.press('D', 2, 3)
VR = ('chr', 'scr', 'spr', 'pal')
def win_shown():
    """찍힌 그림에 창 바탕(검남)이 보이나 — 창 안 빈칸 세 곳(줄 6·11·15 의 10칸 = 이름과 값 사이)"""
    fb = p.fb; n = 0
    for (x, y) in ((84, 52), (84, 92), (84, 124)):
        v = fb[(y * 160 + x) * 2] | fb[(y * 160 + x) * 2 + 1] << 8
        r, g, b = (v >> 11) & 31, (v >> 5) & 63, v & 31
        n += (r <= 3 and g <= 6 and 6 <= b <= 12)
    return n == 3
def vdiff(a, b): return {VR[i]: [k for k in range(len(a[i])) if a[i][k] != b[i][k]] for i in range(4)}
OVERLAP = []; OPENS = [0]
def refs_of(v):
    """화면 램 사본 v 에서 두 판 칸·스프라이트가 가리키는 타일 · 첫째 판 칸이 쓰는 팔레트"""
    scr, spr = v[1], v[2]; t = set(); pals = set()
    for pl in (0, 1):
        for i in range(1024):
            e = scr[pl * 0x800 + i * 2] | scr[pl * 0x800 + i * 2 + 1] << 8
            t.add(e & 0x1FF)
            if pl == 0: pals.add((e >> 9) & 15)
    for k in range(64): t.add(spr[k * 4] | ((spr[k * 4 + 1] & 1) << 8))
    return t, pals
def check_open(pre_v):
    """메뉴가 막 열린 프레임: 창이 빌린 타일·팔레트가 열기 직전 화면에서 어디서도 안 쓰이던 것인가"""
    OPENS[0] += 1
    t0, p0 = refs_of(pre_v); scr = h.scr_(); mine = set(); mp = set()
    for band in (4, 19):
        for r in range(band, band + 13):
            for c in range(3, 17):
                e = scr[(r * 32 + c) * 2] | scr[(r * 32 + c) * 2 + 1] << 8
                if e & 0x1FF != 0x001: mine.add(e & 0x1FF)
                mp.add((e >> 9) & 15)
    bad_t = mine & t0; bad_p = mp & p0
    if bad_t or bad_p: OVERLAP.append((sorted(bad_t)[:6], sorted(bad_p)))

# ════ P-1 타이틀 글자 · P-14 새지 않기 ══════════════════════════════════
to_title(h)                                              # 허브 꺼진 채로 메뉴(커서 셋째 줄)
plain = h.vram(); shot('0_menu_plain'); s_menu = h.serialize()
sty = (C.c_byte * 15)(*([0, 1, 0, 1, 0, 0, 0, 0, 1, 1, -1, 0, -1, 0, 1]))
dif = (C.c_byte * 15)(*([1] * 15))
lg.league_hub(1, sty, dif); h.run(3)                      # 리그 세션: «리그 대전» 그대로
lv = h.vram()
if KO: ok(lv[0][0x1BB * 16:0x1BD * 16] == RIGEU, '리그 세션 타이틀 셋째 줄 = «리그 대전»(0x1BB·0x1BC = 리그 글자)')
else: ok(plane_tiles(lv[1], 1, 14, 5, 7) == LEAGUE_IDS and plane_tiles(lv[1], 1, 14, 12, 1) == plane_tiles(plain[1], 1, 14, 12, 1), '리그 세션 타이틀 셋째 줄 = «LEAGUE»(7칸, 12칸 그대로)')
shot('1a_menu_league')
lg.league_hub(0, None, None); lg.league_practice_hub(1, 0); h.run(3)
pv = h.vram(); d = vdiff(plain, pv); shot('1_menu')
if KO:
    chg_t = sorted(set(k // 16 for k in d['chr']))
    ok(pv[0][0x1BB * 16:0x1BD * 16] == YEONSEUP and set(chg_t) <= {0x1BB, 0x1BC} and not d['scr'] and not d['spr'] and not d['pal'],
       '연습 세션 타이틀 셋째 줄 = «연습 대전»: 바뀐 것은 타일 0x1BB·0x1BC 그림뿐 (바뀐 타일 %s)' % [hex(t) for t in chg_t])
else:
    cells = sorted(set((k // 2) for k in d['scr']))
    want = {(0x800 + (14 * 32 + c) * 2) // 2 for c in range(5, 13)}
    ok(plane_tiles(pv[1], 1, 14, 5, 8) == PRACTICE_IDS and set(cells) <= want and not d['chr'] and not d['pal'],
       '연습 세션 타이틀 셋째 줄 = «PRACTICE»(5~12칸 메뉴 글자 P·R·A·C·T·I·C·E): 바뀐 것은 둘째 판 14줄 5~12칸뿐 (%d칸)' % len(cells))
ok(hub()[0] == 1 and hub()[4] == KIND, '허브 = 연습 타이틀 상태, 메뉴 판 %d' % hub()[4])
# P-14: 연습을 안 고른 1인 대전 = 원래 게임과 작업 램이 같음
SCRIPT = [('U', 4, 30), ('U', 4, 30), ('A', 4, 240), ('R', 4, 30), ('A', 4, 200), ('A', 4, 100)]
SCRIPT2 = [('', 0, 300), ('R', 30, 0), ('A', 4, 30), ('DA', 6, 60), ('', 0, 300)]
def play_script():
    """메뉴 1번째 줄 → 캐릭터·유파 → (카드 화면·이야기는 → A 를 라운드가 시작될 때까지 — 게임 상태로 정하니 두 번 돌려도 입력이 같다.
    롬 판·내장 시계에 따라 카드 화면·이야기 길이가 다르다) → 경기 동작. 단계마다 작업 램 16KB"""
    cps = []
    for b, n, a in SCRIPT:
        h.press(b, n, a); cps.append(p.ram())
    for k in range(150):
        if pk(0x40A7) == 241 and pk(0x411A) == 1: break
        h.press('R', 4, 10); h.press('A', 4, 16); cps.append(p.ram())
    for b, n, a in SCRIPT2:
        if b: h.press(b, n, a)
        else: h.run(a)
        cps.append(p.ram())
    return cps
h.unserialize(s_menu); lg.league_hub(0, None, None); lg.practice_forget()
base = play_script(); base_com = h.tile(0x049) + h.tile(0x04A); base_mul = (pk16(0x57E2), pk16(0x57E4)); base_57d4 = pk(0x57D4)
def r16(r, a): return r[a - 0x4000] | r[a - 0x4000 + 1] << 8
base_t = (r16(base[-2], 0x582F), r16(base[-1], 0x582F))   # 원래 게임 경기의 타이머(300프레임 사이) — 순정 ss2_h1 판은 기본 옵션이 시간 ∞(0x636C=0x80)
base_runs = base_t[1] < base_t[0]
info('원래 게임 1인 대전: 타이머 %d → %d (%s) · 옵션 0x636A~E %s' % (base_t[0], base_t[1], '흐름' if base_runs else '∞', ' '.join('%02X' % base[-1][a - 0x4000] for a in range(0x636A, 0x636F))))
base_fight = pk(0x40A7) == 241
h.unserialize(s_menu); lg.league_practice_hub(1, 0); h.run(0)
test = play_script()
same = [i for i in range(min(len(base), len(test))) if base[i] == test[i]]
ok(base_fight and len(test) == len(base) and len(same) == len(base) and pst()[0] == 0,
   '연습을 안 고른 일반 세션의 1인 대전(메뉴 1번째 줄 → 캐릭터·유파 → 경기 300프레임) = 허브 꺼진 원래 게임과 작업 램 16KB 같음 (점검 %d/%d곳, 경기 %d)' % (len(same), len(base), base_fight))
diff_at = [i for i in range(min(len(base), len(test))) if base[i] != test[i]]
if diff_at:
    i = diff_at[0]; dd = [(0x4000 + k, base[i][k], test[i][k]) for k in range(16384) if base[i][k] != test[i][k]]
    info('첫 차이 점검 %d: %s' % (i, ' '.join('%04X:%02X/%02X' % x for x in dd[:20])))

# ════ P-2 들어가기 ══════════════════════════════════════════════════════
h.unserialize(s_menu); lg.practice_forget(); lg.league_practice_hub(1, 0); h.run(3)
h.press('A', 4, 240)
s = hub(); ok(s[0] == 2 and pk(0x40A7) == 240 and pk(0x41C0) == 2, '«연습 대전» A → 1인 대전 캐릭터 고르기 = 상대 고르기 상태')
h.run(30); shot('2_pickopp')
s = hub(); ok(s[5] == KIND, '상대 고르기 머리말 «상대 선택» (판 %d)' % s[5])
VT = [0x130 + i for i in range(18)]
def vp_cells():
    scr = h.scr_(); return [(scr[0x800 + ((3 + i // 2) * 32 + 17 + (i & 1)) * 2] | scr[0x800 + ((3 + i // 2) * 32 + 17 + (i & 1)) * 2 + 1] << 8) & 0x1FF for i in range(18)]
def vp_glyph(): return C.string_at(h.chr + 0x130 * 16, 18 * 16)
g0 = vp_glyph(); ok(vp_cells() == VT and s[9] == -2, '오른쪽 세로 칸 = 스테이지 이름(처음 «무작위»)')
seq = []; gl = []
for i in range(9): h.press('O', 4, 20); seq.append(hub()[9]); gl.append(vp_glyph())
ok(seq == [0, 1, 2, 3, 4, 5, 6, 7, -2] and len(set(gl)) == 9 and gl[-1] == g0 and pk(0x41C0) == 2,
   '옵션 아홉 번: 스테이지 0 … 7 → 무작위, 글자 9개가 모두 다름, 게임 화면 그대로 %s' % seq)
for i in range(4): h.press('O', 4, 20)                   # 0 1 2 3
shot('2b_pickopp_stage3')
h.user = 1 << 1; h.run(20); h.user = 0; h.run(30)        # 패드 «A+B»(Y) — 게임이 A 로 받으면 안 됨
ok(hub()[0] == 2 and pk(0x41C0) == 2 and T.status()[0] == 0, '상대 고르기에서 패드 «A+B» 버튼 → 게임이 안 받음')
for m in move_seq(pk(0x4E3C) >> 2, 9): h.press(m, 4, 30)
h.run(10); hd0 = h.tile(0x150)
h.press('A', 4, 60)
s = hub(); ok(s[0] == 3 and s[2] == 9 and T.status()[0] == 1 and s[11] == 3, 'A → 샬럿(9) 수라 더미 · 스테이지 3 으로 무장 · 내 캐릭터 차례 [상태 %d · 고름 %d · 배경 %d]' % (s[0], s[2], s[11]))
ok(h.tile(0x150) != hd0, '더미를 고른 뒤 머리말 타일 원래대로(«캐릭터 선택»)')
shot('3_pickme')
for m in move_seq(pk(0x4E3C) >> 2, 8): h.press(m, 4, 30)
h.run(10); nf, ncard = finish_select()
ok(nf is not None and nf < 1500, '검질 고르기 A → 이야기·대사 넘기고 연습 시작까지 %s프레임 (A 대신 누르기 없으면 2600 안팎%s)' % (nf, ' · 카드 화면은 사용자가 넘김(→ A %d번)' % ncard if ncard else ''))
h.run(30)
ok(pk(0x5D51) == (9 << 4) and pk(0x5B51) >> 4 == 8 and pk(0x5827) == 3, '경기: 더미 = 샬럿 수라(0x5D51 %02X) · 나 = 아수라 · 스테이지 3' % pk(0x5D51))
ok(pk(0x57E6) == 0xFF and pk(0x57E7) == 0xFF and pk16(0x57E2) == 0x100 and pk16(0x57E4) == 0x100 and pk16(0x582F) == 0xFFFF and pk(0x5812) == 0x80,
   'CPU 카드 없음(0xFF) · 배율 0x100 · 타이머 ∞ · 다음 라운드 ∞')
ok(hub()[0] == 4 and pst()[22] == 9 and pst()[23] == 0 and pst()[19] in (4, 5), '허브 = 연습 경기 · 연습 켜짐(더미 %d/%d · 라운드 시작 물체 수 %d)' % (pst()[22], pst()[23], pst()[19]))
ok(pk(0x5BCB) & 1 == 0 and h.tile(0x049) + h.tile(0x04A) != base_com, '더미 서기(0x5BCB bit0 = 0) · HUD «COM» → «2P» 그림')
shot('4_fight')

# ════ P-12 Option 탭 · 조합 / P-10 한 번 ══════════════════════════════
reset_wait(0); h.run(10)
last_pre = {}
def pre2(hh):
    pre_hook(hh); last_pre['v'] = hh.vram()
h.pre_hook = pre2
h.press('O', 3, 0)
opened = None; f = 0
while f < 40:
    st_before = pst()[1]; h.run(1); f += 1
    if st_before != 2 and pst()[1] == 2: opened = last_pre['v']; break
ok(opened is not None and pk(0x61D4) == 1, 'Option 탭(누르는 동안 다른 버튼 없음) → 뗄 때 일시정지(0x61D4=1) + 메뉴 창 (%s프레임)' % f)
if opened is not None: check_open(opened)
vis = []
for k in range(12): h.run(1); vis.append((win_shown(), pk(0x41F5)))
ok(all(v[0] for v in vis[1:]) and {v[1] for v in vis} == {0, 0x78}, '창이 매 프레임 보임(게임이 틱마다 첫째 판 가운데를 줄 4~16 ↔ 19~31 로 번갈아 보여도 — 0x41F5 %s) %s' % (sorted({v[1] for v in vis}), ''.join('O' if v[0] else '.' for v in vis)))
shot('6_menu')
# 상태 저장 직전(native.c nativeSaveState 와 같은 순서): 우리 그림을 모두 되돌리고 → 다음 프레임에 다시 그린다
lg.practice_before_save(); lg.league_hub_before_save(); sv = h.vram()
dd = vdiff(opened, sv)
com_ok = sv[0][0x049 * 16:0x04B * 16] == base_com
dig_ok = plane_tiles(sv[1], 0, 3, 8, 3) == [0x001, 0x001, 0x001]
other = [k for k in dd['chr'] if not (0x049 * 16 <= k < 0x04B * 16)] + [k for k in dd['scr'] if not (3 * 64 + 16 <= k < 3 * 64 + 22)]
h.run(2)
ok(com_ok and dig_ok and not other and not dd['pal'] and not dd['spr'] and win_shown() and pst()[1] == 2,
   '상태 저장 직전 되돌림: 창·대미지 숫자·«2P» 를 원래대로(저장되는 화면 램 = 메뉴 열기 전 + «COM»·빈 띠) → 다음 프레임에 창 다시 그림')
sc = h.scr_()
win_t = [plane_tiles(sc, 0, r, 3, 14) for r in range(4, 17)]
ok(all(t != 0 for row in win_t for t in row), '첫째 판 줄 4~16 × 칸 3~16 이 창 칸으로 채워짐 (빌린 타일 %d · 빈 후보 중 쓰이던 것 %d)' % (pst()[16], pst()[17]))
for b in 'DRDDRDRR': h.press(b, 2, 4)
h.run(2); shot('7_menu_vals'); s = pst()
ok(s[3:8] == [0, 1, 0, 1, 2], '메뉴: ↓→↓↓→↓→→ → 가드 «전부» · 상대 분노 MAX · 리셋 위치 «오른쪽 벽» [%s]' % s[3:8])
for b in 'LLULUULU': h.press(b, 2, 4)
ok(pst()[3:10] == [0, 0, 0, 0, 0, 0, 0] and pst()[2] == 0, '←↑ 로 되돌림(모든 값 처음대로, 커서 첫 줄)')
closed = None
def post_close(hh):
    global closed
    if closed is None and pst()[1] == 3: closed = hh.vram()
h.post_hook = post_close
h.press('B', 2, 0); h.post_hook = None
wait_until(lambda: pst()[1] == 0, 60)
dd = vdiff(opened, closed) if closed else None
ok(closed is not None and not any(dd.values()), 'B 로 닫음: 되돌린 순간 문자 램·두 판·스프라이트 램·팔레트 램 = 열기 직전과 바이트까지 같음 %s' % ({k: len(v) for k, v in dd.items()} if dd else '-'))
ok(pk(0x61D4) == 0 and pst()[1] == 0, '닫은 뒤 Option 대신 눌러 일시정지 풀림')
h.pre_hook = pre_hook
h.run(10); open_menu(); h.run(6); op0 = pst()[20]
h.press('O', 40, 0); h.run(40)                           # Option 으로 닫고 풀린 뒤까지 쥐고 있다가 뗌 — 다시 열리면 안 됨
ok(pk(0x61D4) == 0 and pst()[1] == 0 and pst()[20] == op0, 'Option 으로 닫기(풀린 뒤까지 쥐고 있다 떼어도 다시 안 열림 · 메뉴 연 횟수 %d → %d)' % (op0, pst()[20]))
h.run(20); shot('8_after')
# Option + 방향 = 리셋 · 그동안 게임 패드(0x56ED)에 Option·방향 없음
pads = []
def pad_watch(hh): pads.append(pk(0x56ED))
reset_ok = {}
for dname, pos, want in (('L', 1, (24, 104, 0)), ('R', 2, (216, 296, 159)), ('U', 0, (120, 200, 80)), ('D', 0, (120, 200, 80))):
    h.hold('R'); h.run(20); h.user = 0; h.run(20)        # 조금 옮겨 둔 뒤
    n0 = pst()[11]; pads.clear(); h.post_hook = pad_watch
    h.hold('O'); h.run(4); h.hold('O' + dname); h.run(5); h.hold('O'); h.run(4); h.user = 0
    h.post_hook = None
    wait_until(lambda: pst()[11] > n0, 200); h.run(8)
    x1, x2, cams = pk16(0x59D6), pk16(0x5BD6), (pk16(0x5FA0), pk16(0x576C), pk16(0x4880))
    reset_ok[dname] = (x1, x2) == want[:2] and cams == (want[2] << 8,) * 3 and pk(0x59D2) == 0 and pk(0x5BD2) == 1
    ok(reset_ok[dname] and all((v & 0x4F) == 0 for v in pads[1:]) and pst()[7] == pos,
       'Option+%s → 리셋 (X %d·%d · 카메라 %s · 리셋 위치 %d) · 누르는 동안 0x56ED 에 Option·방향 비트 0 (%d프레임)' % (dname, x1, x2, '/'.join('%04X' % c for c in cams), pst()[7], len(pads)))
    shot('9_reset_%s' % {'L': 'left', 'R': 'right', 'U': 'center', 'D': 'down'}[dname])
h.run(30)

# ════ P-4 더미 서기 · CPU ══════════════════════════════════════════════
lg.practice_set(0, 0); reset_wait(0)
hp1min = 128; act2max = 0
for f in range(1200 if QUICK else 2400):
    h.run(1); hp1min = min(hp1min, PRE['hp1']); act2max = max(act2max, pk16(0x4E7E))
ok(hp1min == 128 and act2max < 0x50, '더미 서기 %d프레임: P1 체력 그대로 128 · 더미 ACT < 0x50 (최대 %X)' % (1200 if QUICK else 2400, act2max))
lg.practice_set(0, 1); dmg1 = 0; post = pk(0x5A46)
for f in range(1500):
    h.run(1)
    if PRE['hp1'] < post: dmg1 += post - PRE['hp1']
    post = pk(0x5A46)
ok(dmg1 > 0 and pk(0x5BCB) & 1 == 1 and h.tile(0x049) + h.tile(0x04A) == base_com, '더미 CPU 로 바꾸면 바로 싸움(P1 이 받은 대미지 %d) · bit0 = 1 · HUD «COM» 원래 그림' % dmg1)
lg.practice_set(0, 0); h.run(120); dmg1b = 0; dmg1s = 0; post = pk(0x5A46)
# 바꾸는 순간 더미가 하던 동작은 CPU 비트(0x5BCB bit0)와 상관없이 끝까지 간다 — CPU 가 막 낸 MAX 비오의(샬럿 ACT 0x1C8)는
# 두 사람을 묶은 채(0x59CE·0x5BCE = 0xFF) 360프레임 넘게 이어지고, bit0 을 켜 두든 끄든 그동안 램이 같다(게임 연출).
# 그래서 그 동작이 끝나 더미가 처음 움직일 수 있게 된(0x5BCE == 0) 다음 프레임부터 대미지를 센다(프레임 수는 그대로 — 뒤 시험 박자 같게)
free = 0 if pk(0x5BCE) == 0 else None
for f in range(1200):
    h.run(1)
    if PRE['hp1'] < post:
        if free is None: dmg1s += post - PRE['hp1']
        else: dmg1b += post - PRE['hp1']
    if free is None and PRE['ctrl2'] == 0: free = f + 1
    post = pk(0x5A46)
ok(free is not None and free <= 600 and dmg1b == 0 and pk(0x5BCB) & 1 == 0 and h.tile(0x049) + h.tile(0x04A) != base_com,
   '다시 서기 → 하던 동작이 끝나면(120 + %s프레임, 그사이 대미지 %d) 멈춤(남은 %s프레임 P1 대미지 %d) · «2P»'
   % (free, dmg1s, None if free is None else 1200 - free, dmg1b))

# ════ P-5 가드 «전부» ══════════════════════════════════════════════════
SC = {
    'sA':     (36, {0: 'A', 4: ''}, 90),
    'strong': (36, {0: 'A', 20: ''}, 110),
    'cA':     (36, {0: 'D', 6: 'DA', 10: ''}, 90),
    'jA':     (80, {0: 'UF', 4: '', 38: 'A', 42: ''}, 120),
    'qcf':    (36, {0: 'D', 4: 'DF', 8: 'F', 12: 'FA', 16: ''}, 140),
    'throw':  (22, {0: 'BA', 16: ''}, 200),
}
lg.practice_set(0, 0); lg.practice_set(1, 1)
res = {}
for nm, (g, sc, n) in SC.items():
    approach(g); res[nm] = scenario(sc, n)
info('가드 전부: ' + ' · '.join('%s 닿음%d 맞음%d 가드%d 대미지%d' % (k, v['contact'], v['hit'], v['block'], v['dmg']) for k, v in res.items()))
blocked_all = all(res[k]['hit'] == 0 and res[k]['dmg'] == 0 and res[k]['block'] >= 1 for k in ('sA', 'strong', 'cA', 'jA'))
ok(blocked_all, '가드 «전부»: 약·강·앉아 약(하단)·점프 공격(상단) 모두 가드 · 대미지 0')
ok(res['qcf']['hit'] == 0 and res['qcf']['block'] >= 1 and res['qcf']['dmg'] > 0, '가드 «전부»: 필살(236A)은 가드 + 깎임만 (깎임 %d)' % res['qcf']['dmg'])
ok(res['throw']['hit'] >= 1 and res['throw']['dmg'] > 0, '가드 «전부»: 잡기는 못 막음(맞음 %d · 대미지 %d)' % (res['throw']['hit'], res['throw']['dmg']))
# 공중에선 가드 비트를 안 씀 — CPU 더미가 뛰고 맞는 동안
lg.practice_set(0, 1); reset_wait(0); air = 0; bad_air = 0; random.seed(5)
for f in range(1500 if QUICK else 3000):
    if f % 10 == 0: h.user = bits(random.choice(['', 'R', 'L', 'A', 'DA', 'UR', 'UL', 'B', 'U']))
    h.run(1); st2 = pk(0x5BC9)
    if st2 & 0x80:
        air += 1
        if st2 & 0x18: bad_air += 1
h.user = 0
ok(air > 0 and bad_air == 0, '가드 «전부» + CPU 더미: 공중(0x80)인 프레임 %d 중 가드 비트가 선 프레임 %d' % (air, bad_air))

# ════ P-6 «첫 타 뒤» ══════════════════════════════════════════════════
COMBO = {0: 'D', 6: 'DA', 10: 'D', 22: 'DF', 26: 'F', 30: 'FA', 34: ''}
LATE = {0: 'D', 6: 'DA', 10: 'D', 32: 'DF', 36: 'F', 40: 'FA', 44: ''}
lg.practice_set(0, 0); lg.practice_set(1, 0)
approach(36); c_none = scenario(LATE, 200)
lg.practice_set(1, 2)
h.run(80); approach(36); c_combo = scenario(COMBO, 200)
h.run(80); approach(36); c_late = scenario(LATE, 200)
info('첫 타 뒤: 가드 안 함 늦게 %s · 이어진 콤보 %s · 늦게 넣은 콤보 %s' % ((c_none['hit'], c_none['block']), (c_combo['hit'], c_combo['block'], c_combo['cmax']), (c_late['hit'], c_late['block'])))
ok(c_none['hit'] >= 1 and c_none['block'] == 0, '(대조) 가드 «안 함»: 같은 늦은 콤보에서 가드 0 (맞음 %d · 가드 %d — 둘째 타는 거리에 따라 맞거나 헛침)' % (c_none['hit'], c_none['block']))
ok(c_combo['hit'] >= 2 and c_combo['cmax'] >= 2 and c_combo['block'] == 0, '«첫 타 뒤»: 이어지는 콤보(앉아 A > 236A)는 둘 다 맞음 (맞음 %d · 콤보 %d)' % (c_combo['hit'], c_combo['cmax']))
ok(c_late['hit'] == 1 and c_late['block'] >= 1, '«첫 타 뒤»: 늦게 넣은 콤보는 첫 타만 맞고 둘째는 가드 (맞음 %d · 가드 %d)' % (c_late['hit'], c_late['block']))

# ════ P-7 «랜덤» ══════════════════════════════════════════════════════
lg.practice_set(1, 3)
approach(36)
open_menu(); menu_go(4)
while pst()[7] != 3: h.press('R', 2, 3)                  # 리셋 위치 «지난 위치» = 메뉴를 연 자리
close_menu()
NATK = 50 if QUICK else 100
blk = hit = other = 0; flips = 0
def guard_watch(hh):
    global flips
    if PRE['ctrl2'] == 0x12 and pst()[14] == 0: flips += 1
for i in range(NATK):
    reset_wait(-1); h.run(2)
    h.post_hook = guard_watch
    r = scenario({0: 'A', 3: ''}, 34)
    h.post_hook = None
    if r['hit']: hit += 1
    elif r['block']: blk += 1
    else: other += 1
reset_wait(-1); g_last = gap()
ok(pst()[7] == 3 and abs(g_last - 36) <= 12, '«지난 위치» 리셋 = 메뉴를 연 자리(간격 %d)' % g_last)
ok(0.3 * NATK <= blk <= 0.7 * NATK and other <= NATK // 10, '«랜덤»: 공격 %d번 중 가드 %d · 맞음 %d · 안 닿음 %d (30~70%%)' % (NATK, blk, hit, other))
ok(flips == 0, '«랜덤»: 가드 경직(0x5BCE=0x12) 중 가드가 풀린 프레임 %d' % flips)

# ════ P-11 대미지 숫자 ════════════════════════════════════════════════
lg.practice_set(1, 0); lg.practice_set(4, 0)
sys.path.insert(0, '/home/user/CustumApKS/handoff/ss2_practice/stage0/ref')
import combat_ref
dm = {}
for nm, (g, sc, n) in (('sA', SC['sA']), ('combo', (36, COMBO, 200)), ('throw', SC['throw']), ('qcf', SC['qcf'])):
    h.run(60); approach(g)
    tr = combat_ref.CombatTracker(); fr = [0]
    def tr_hook(hh): fr[0] += 1; tr.step(pk, fr[0])
    h.post_hook = tr_hook
    r = scenario(sc, n); h.run(200)
    h.post_hook = None
    ends = [e for e in tr.events if e['type'] == 'combo_end' and e['defender'] == 1]
    dm[nm] = (r['dmg'], pst()[10], ends[-1]['damage'] if ends else None)
info('대미지 (실제 · 화면 · combat_ref 콤보 끝): ' + ' · '.join('%s %s' % (k, v) for k, v in dm.items()))
ok(all(v[0] > 0 and v[0] == v[1] == v[2] for v in dm.values()), '대미지 숫자 = 콤보 대미지(combat_ref 콤보 끝과 같음, 잡기 포함) %s' % dm)
# 바닥 64 가 걸린 콤보 — 더미 체력 70 에서 콤보
h.run(60); approach(36); lg.practice_set(8, 70); h.run(1)
r = scenario(COMBO, 200); h.run(20)
ok(r['dmg'] > 6 and pst()[10] == r['dmg'] and pk(0x5C46) >= 64, '바닥 64 가 걸린 콤보도 실제 대미지 그대로 (체력 70 → 실제 %d · 화면 %d)' % (r['dmg'], pst()[10]))
sc_ = h.scr_(); digs = plane_tiles(sc_, 0, 3, 8, 3)
v = pst()[10]; want = [((v // 100) if v >= 100 else None), ((v // 10) % 10 if v >= 10 else None), v % 10]
ok(all(w is None or digs[i] == 0x002 + w for i, w in enumerate(want)), 'HUD 셋째 줄 가운데 = 게임 숫자 타일 %s (값 %d)' % ([hex(t) for t in digs], v))
shot('5_dmg')
lg.practice_set(6, 1); h.run(3); off = plane_tiles(h.scr_(), 0, 3, 8, 3)
lg.practice_set(6, 0); h.run(3)
ok(off == [0x001, 0x001, 0x001], '숫자 «끔» → 셋째 줄 원래 칸(0x001) %s' % [hex(t) for t in off])

# ════ P-9 분노 MAX 유지 ════════════════════════════════════════════════
lg.practice_set(0, 0); reset_wait(0); lg.practice_set(2, 1); lg.practice_set(3, 1); h.run(10)
ok(all(pk(0x59CA + 0x200 * q) & 4 and pk(0x5A47 + 0x200 * q) == 0x30 and pk(0x5A4B + 0x200 * q) == 0x30 and pk16(0x5A48 + 0x200 * q) >= 0x1000 for q in (0, 1)),
   'MAX 유지(나·상대): 0x59CA bit2 · 분노 0x30 · 표시 분노 0x30 · 타이머 ≥ 0x1000')
ts = []
for i in range(20): h.run(1); ts.append(pk16(0x5A48))
p.poke(0x5A48, 0x01); p.poke(0x5A49, 0x10); p.poke(0x5C48, 0x01); p.poke(0x5C49, 0x10); h.run(12)
ok(ts[-1] < ts[0] and pk16(0x5A48) > 0x2000 and pk16(0x5C48) > 0x2000, '타이머는 게임이 줄이고(%X → %X), 0x1000 아래로 가면 0x3000 으로' % (ts[0], ts[-1]))
acts = set(); spent = False; rearm = None
motion(h, ['B', 'F', 'D'], 'A')
for f in range(400):
    h.run(1); acts.add(pk16(0x4E3E))
    if not pk(0x59CA) & 4: spent = True
    elif spent and rearm is None: rearm = f
ok(spent and rearm is not None, 'MAX 기술(←→↓+A) 쓴 뒤 MAX 비트가 꺼졌다가 움직일 수 있게 되면 다시 켬(%s프레임) · ACT %s' % (rearm, ' '.join('%X' % a for a in sorted(acts) if a >= 0x1C0)))
if 0x1CC in acts: info('아수라 MAX 비오의 ACT 0x1CC 확인')
# 효과를 쓴 뒤엔 게임이 첫째 판 효과 층(줄 19~31)의 가로 스크롤(0x41F8)을 옮겨 둔다 — 창은 그래도 매 프레임 제자리에
h.run(60); fx = pk(0x41F8)
open_menu(); vis = []
for k in range(10): h.run(1); vis.append(win_shown())
close_menu(); h.run(4)
ok(all(vis[1:]) and pk(0x41F8) == fx, 'MAX 비오의 뒤(효과 층 가로 스크롤 0x41F8 = %02X)에도 창이 매 프레임 제자리 %s · 닫은 뒤 0x41F8 원래 값 %02X' % (fx, ''.join('O' if v else '.' for v in vis), pk(0x41F8)))
lg.practice_set(2, 0); lg.practice_set(3, 0); h.run(40)
ok(not pk(0x59CA) & 4 and not pk(0x5BCA) & 4, 'MAX 유지 끄면 움직일 수 있을 때 MAX 를 거둠')

# ════ P-3 끝나지 않는 라운드 · P-8 리셋 · P-10 메뉴 열고 닫기 (함께) ══════
lg.practice_set(0, 1); lg.practice_set(1, 3); reset_wait(0)
NF = 8000 if QUICK else 20000
random.seed(11)
st = dict(hidden=0, res_nz=0, notlive=0, hpmin=128, timer_bad=0, resets=0, reset_bad=[], push=[], menus=0, menu_bad=[], states={'air': 0, 'hitstop': 0, 'object': 0, 'max': 0})
TGT = {0: (120, 200, 80), 1: (24, 104, 0), 2: (216, 296, 159)}
cyc = 0; f = 0; shots_done = set()
h.pre_hook = pre2
while f < NF:
    # 무작위 입력 100프레임
    for k in range(100):
        if k % random.choice((6, 10, 14)) == 0: h.user = bits(random.choice(['', 'R', 'L', 'A', 'B', 'DA', 'D', 'UR', 'UL', 'RA', 'DB', 'LA']))
        h.run(1); f += 1
        if pk(0x5824): st['res_nz'] += 1
        if pk(0x411A) != 1 or pk(0x40A7) != 241: st['notlive'] += 1
        st['hpmin'] = min(st['hpmin'], PRE['hp1'], PRE['hp2'])
        if not pk(0x61D4) and pk16(0x582F) != 0xFFFF: st['timer_bad'] += 1
    h.user = 0
    cyc += 1
    if cyc % 2 == 0:                                      # 리셋 요청(무작위 자리 · 좌우)
        pos = random.choice((0, 1, 2)); sw = random.random() < 0.3
        lg.practice_set(5, 1 if sw else 0)
        n0 = pst()[11]; lg.practice_set(7, pos); w = 0; h.user = 0    # 기다리는 동안 P1 은 손을 뗀다(걷던 관성이 리셋 뒤 2px 로 남지 않게)
        trace = []
        while pst()[11] == n0 and w < 240:
            trace.append((pk16(0x59D6), pk16(0x5BD6), pk(0x59CE), pk(0x5BCE)))
            h.run(1); w += 1; f += 1
        if pst()[11] > n0:
            st['resets'] += 1
            x1, x2, cam = TGT[pos]
            if sw: x1, x2 = x2, x1
            got = (pk16(0x59D6), pk16(0x5BD6), pk16(0x5FA0), pk16(0x576C), pk16(0x4880), pk(0x5A46), pk(0x5A4A), pk(0x5C46), pk(0x5C4A))
            if got != (x1, x2, cam << 8, cam << 8, cam << 8, 128, 128, 128, 128): st['reset_bad'].append((pos, sw, got))
            xs = []
            for k in range(10): h.run(1); f += 1; xs.append(pk16(0x59D6))
            if any(x != x1 for x in xs): st['push'].append((pos, sw, xs, 'wait %d' % w, trace[-6:]))
            key = (pos, sw)
            if key not in shots_done and len(shots_done) < 6: shots_done.add(key); shot('10_reset_%d%s' % (pos, '_swap' if sw else ''))
        lg.practice_set(5, 0)
    # 메뉴 열고 닫기(무작위 순간 — 공중·히트스톱·장풍 중 포함)
    for k in range(random.randint(0, 12)): h.run(1); f += 1
    y_air = pk16(0x59DA) != 128 or pk16(0x5BDA) != 128; hs = pk(0x5DC7) != 0; obj = pk(0x41C2) > pst()[19]; mx = bool(pk(0x59CA) & 4 or pk(0x5BCA) & 4)
    opened = None; closed = None
    h.press('O', 2, 0); w = 0
    while w < 40:
        sb = pst()[1]; h.run(1); w += 1; f += 1
        if sb != 2 and pst()[1] == 2: opened = last_pre['v']; break
    if opened is None: continue
    check_open(opened)
    st['menus'] += 1
    for nm, c in (('air', y_air), ('hitstop', hs), ('object', obj), ('max', mx)):
        if c: st['states'][nm] += 1
    for k in range(random.randint(2, 8)):
        h.run(1); f += 1
        if k >= 1 and not win_shown():
            st['hidden'] += 1
            if st['hidden'] <= 3:
                spr = h.spr_(); fr = [(i, spr[i * 4 + 2], spr[i * 4 + 3]) for i in range(64) if (spr[i * 4 + 1] >> 3) & 3 == 3]
                shot('dbg_hidden_%d' % st['hidden'])
                info('창 안 보임: 메뉴 %d · k %d · 0x41F5 %d · 일시정지 %d · 메뉴 상태 %d · 앞 우선순위 스프라이트 %s · 칸(8,10)=%04X (23,10)=%04X · 팔레트 %s' % (
                    st['menus'], k, pk(0x41F5), pk(0x61D4), pst()[1], fr[:4], h.ent(0, 8, 10), h.ent(0, 23, 10), C.string_at(h.pal + 0x80 + 13 * 8, 24).hex()))
    h.post_hook = post_close; closed = None
    h.press('B', 2, 0); h.post_hook = None
    wait_until(lambda: pst()[1] == 0, 60)
    if closed is None or any(vdiff(opened, closed).values()): st['menu_bad'].append((st['menus'], {k: len(v) for k, v in vdiff(opened, closed).items()} if closed else None))
h.pre_hook = pre_hook
ok(st['res_nz'] == 0 and st['notlive'] == 0 and st['hpmin'] > 0 and st['timer_bad'] == 0,
   '무작위 입력 + CPU 더미 %d프레임: 0x5824 늘 0 (어긋남 %d) · 0x411A 늘 1 (%d) · 체력 최소 %d > 0 · 타이머 0xFFFF (어긋남 %d)' % (f, st['res_nz'], st['notlive'], st['hpmin'], st['timer_bad']))
ok(st['resets'] >= (15 if QUICK else 40) and not st['reset_bad'], '무작위 순간 리셋 요청 → 중립 뒤 실행 %d번: 위치·카메라 셋·체력·표시 체력 = 목표 (어긋남 %s)' % (st['resets'], st['reset_bad'][:3]))
ok(not st['push'], '리셋 뒤 10프레임 동안 P1 X 밀림 없음 (밀림 %s)' % st['push'][:3])
ok(st['menus'] >= (30 if QUICK else 100) and not st['menu_bad'], '메뉴 열고 닫기 %d번(공중 %d · 히트스톱 %d · 장풍/효과 %d · MAX %d): 닫은 뒤 문자 램·두 판·스프라이트·팔레트 = 열기 전과 바이트까지 같음 (어긋남 %s)' % (
   st['menus'], st['states']['air'], st['states']['hitstop'], st['states']['object'], st['states']['max'], st['menu_bad'][:3]))
ok(st['hidden'] == 0, '메뉴가 열린 동안 창이 안 보인 프레임 %d (런어헤드 2 · 프레임 생성 켬)' % st['hidden'])
info('버린 리셋 요청 %d' % pst()[21])

# ════ P-10 결정성 — 메뉴 열고 닫기 = 그냥 일시정지·풀기 ═══════════════
lg.practice_set(0, 1); lg.practice_set(1, 0)
det = []
for trial, prep in enumerate(('', 'UF', 'A', 'MAX')):
    h.run(40)
    if prep == 'MAX':                                     # 아수라 MAX 비오의 뒤 — 효과 층 가로 스크롤이 0 이 아닌 채로
        lg.practice_set(0, 0); lg.practice_set(2, 1); h.run(20); motion(h, ['B', 'F', 'D'], 'A'); h.run(240); lg.practice_set(2, 0)
        info('결정성 넷째(MAX 비오의 뒤): 0x41F8 = %02X' % pk(0x41F8))
    elif prep: h.hold(rel(h, prep)); h.run(6 if prep == 'UF' else 3); h.user = 0
    s0 = h.serialize(); ps0 = h.pstate()
    h.rec = []
    h.press('O', 3, 0); wait_until(lambda: pst()[1] == 2, 40); h.run(8)
    h.press('D', 2, 3); h.press('U', 2, 3); h.press('B', 2, 0)
    while len(h.rec) < 240: h.run(1)
    rec = h.rec; h.rec = None
    ra, va = p.ram(), h.vram()
    h.unserialize(s0); h.pstate_set(ps0); h.passive = True; h.replay = list(rec)
    h.run(len(rec)); h.replay = None; h.passive = False
    rb, vb = p.ram(), h.vram()
    det.append((ra == rb, not any(vdiff(va, vb).values()), sum(1 for k in range(16384) if ra[k] != rb[k])))
ok(all(d[0] and d[1] for d in det), '같은 입력으로 «메뉴 열고 닫기» = «그냥 일시정지·풀기»: 240프레임 뒤 작업 램·화면 램 같음 (4번: 서서·공중·공격 중·MAX 비오의 뒤) %s' % det)
lg.practice_set(0, 1)

# ════ P-13 나가기 — 다시 고르기 ════════════════════════════════════════
open_menu(); menu_go(8); h.press('A', 2, 0)
nf = wait_until(lambda: hub()[0] == 2 and pk(0x40A7) == 240 and pk(0x41C0) == 2 and hub()[7] == 0, 2000)
ok(nf is not None and pst()[0] == 0 and T.status()[0] == 0, '«다시 고르기» → 리셋 → 상대 선택 (%s프레임) · 연습·무장 꺼짐' % nf)
h.run(30)
while hub()[9] != 7: h.press('O', 4, 20)
for m in move_seq(pk(0x4E3C) >> 2, 15): h.press(m, 4, 30)
h.run(10); hv = hub()[1]
h.press('B', 4, 60)
s = hub(); ok(hv == 14 and s[0] == 3 and s[2] == 14, '가운데 무작위 칸 = 유가(14) · B = 나찰 더미 · 스테이지 7')
for m in move_seq(pk(0x4E3C) >> 2, 4): h.press(m, 4, 30)
h.run(10); nf, ncard = finish_select(); h.run(30)
ok(nf is not None and pk(0x5D51) == (14 << 4 | 1 << 3) and pk(0x5B51) >> 4 == 4 and pk(0x5827) == 7 and live(), '유가 나찰 더미 vs 나코루루 · 스테이지 7 경기 시작 (%s프레임 · 0x5D51 %02X)' % (nf, pk(0x5D51)))
shot('11_stage7_yuga')
lg.practice_set(0, 0); lg.practice_set(1, 0); h.run(10)
# 나코루루 매 — 리셋하면 바로 옆
hk = []
for pos in (1, 2, 0):
    h.hold('R'); h.run(30); h.user = 0; h.run(30)
    reset_wait(pos); hk.append((pk16(0x59D6), pk16(0x4F38), pk16(0x4F3E)))
    h.run(2)
    if pos == 1: shot('12_nakoruru_reset_left')
ok(all(a[2] != 0 and abs(a[1] - a[0]) <= 20 for a in hk) and pst()[19] == 5, '나코루루(P1)의 매(물체 4번 칸): 리셋하면 바로 옆 (나코루루 X · 매 X %s) · 라운드 시작 물체 수 %d' % ([a[:2] for a in hk], pst()[19]))
# 다시 고르기 없이 «타이틀로»
open_menu(); menu_go(9); h.press('A', 2, 0)
nf = wait_until(lambda: hub()[0] == 1 and pk(0x624B) == 2 and hub()[7] == 0, 2000)
ok(nf is not None and pst()[0] == 0, '«타이틀로» → 리셋 → 타이틀 메뉴 셋째 줄에 커서 (%s프레임)' % nf)
h.run(10); shot('13_back_title')
# 그 뒤 고른 1인 대전은 원래 게임과 같음
h.press('U', 4, 30); h.press('U', 4, 30); h.press('A', 4, 240); h.press('R', 4, 30); h.press('A', 4, 200); h.press('A', 4, 100)
f = 0
while f < 4000 and not live():
    if f % 60 == 0 and pk(0x40A7) != 241: h.press('A', 2); f += 2
    else: h.run(1); f += 1
h.run(60); t0 = pk16(0x582F); h.run(120)
timer_ok = (pk16(0x582F) < t0 and pk16(0x582F) != 0xFFFF) if base_runs else (t0 == pk16(0x582F) == 0xFFFF)
ok(live() and pk(0x57D4) == base_57d4 and pk(0x5BCB) & 1 == 1 and timer_ok and h.tile(0x049) + h.tile(0x04A) == base_com
   and (pk16(0x57E2), pk16(0x57E4)) == base_mul and pst()[0] == 0,
   '그 뒤 고른 1인 대전은 원래 게임과 같음: 0x57D4=%d · P2 CPU(bit0) · 타이머 %d → %d(원래 게임 %s) · 배율 %s · «COM» 그림' % (pk(0x57D4), t0, pk16(0x582F), '흐름' if base_runs else '∞', (hex(pk16(0x57E2)), hex(pk16(0x57E4)))))

# ════ P-15 빈 타일 + 더미 15명(싸우지 않는 조합은 CPU 못 고름) · 자동 진입 ═══════════
p.lib.retro_reset(); lg.practice_forget(); lg.league_practice_hub(1, 1)   # 링크로 연 판처럼 — 로고·메뉴를 넘겨 상대 선택까지
nf = wait_until(lambda: hub()[0] == 2 and pk(0x41C0) == 2 and hub()[7] == 0, 2500)
ok(nf is not None, '자동 진입(실행 창 «연습 대전으로»): 리셋 뒤 로고·메뉴를 넘겨 상대 선택까지 %s프레임' % nf)
BAD = {(1, 0), (4, 1), (5, 1), (6, 1), (10, 1), (12, 1)}
refs = {}; cpu_block = []; entries = 0; ndum = 6 if QUICK else 15
FREE = set(range(0x0D8, 0x106))
def free_watch(hh):
    if hh.frames % 2: return
    scr = hh.scr_(); spr = hh.spr_()
    if pst()[1] == 0:
        for pl in (0, 1):
            for i in range(1024):
                hi = scr[pl * 0x800 + i * 2 + 1] & 1
                if not hi and scr[pl * 0x800 + i * 2] < 0xD8: continue
                t = (scr[pl * 0x800 + i * 2] | hi << 8)
                if t in FREE: refs.setdefault(t, set()).add(('plane%d' % pl, cur_dummy[0]))
    for s_ in range(64):
        t = spr[s_ * 4] | ((spr[s_ * 4 + 1] & 1) << 8)
        if t in FREE and (spr[s_ * 4 + 1] & 0x18): refs.setdefault(t, set()).add(('sprite', cur_dummy[0]))
cur_dummy = [None]
for k in range(ndum):
    dmy = k if k < 14 else 14; sty_ = k % 2
    me = [8, 9, 2, 11, 3, 0, 7, 6, 13, 12, 1, 5, 4, 10, 8][k]
    if k > 0:
        h.run(30)
    target = 15 if dmy == 14 else dmy
    for m in move_seq(pk(0x4E3C) >> 2, target): h.press(m, 4, 24)
    h.run(8); h.press('B' if sty_ else 'A', 4, 50)
    for m in move_seq(pk(0x4E3C) >> 2, me): h.press(m, 4, 24)
    h.run(8); nf, ncard = finish_select()
    if nf is None: info('더미 %d 경기 못 들어감' % dmy); break
    entries += 1; cur_dummy[0] = (dmy, sty_, me)
    lg.practice_set(0, 1); lg.practice_set(2, 1); h.run(4)
    if (dmy, sty_) in BAD and (pst()[3] != 0 or pk(0x5BCB) & 1): cpu_block.append((dmy, sty_))
    if (dmy, sty_) not in BAD and (pst()[3] != 1): cpu_block.append(('cpu?', dmy, sty_))
    if (dmy, sty_) in BAD:                                  # 메뉴에서도 CPU 로 못 바꿈
        open_menu(); menu_go(0); h.press('R', 2, 3); h.press('A', 2, 3)
        if pst()[3] != 0: cpu_block.append(('menu', dmy, sty_))
        close_menu()
    h.post_hook = free_watch; random.seed(100 + k)
    for f in range(400 if QUICK else 900):
        r = random.random()
        if r < 0.04: motion(h, random.choice([['D', 'DF', 'F'], ['B', 'F', 'D'], ['F', 'DF', 'D', 'DB', 'B'], ['D', 'DB', 'B']]), random.choice(['A', 'B']))
        elif f % 12 == 0: h.user = bits(random.choice(['', 'R', 'L', 'A', 'B', 'DA', 'UR']))
        h.run(1)
    h.post_hook = None; h.user = 0
    lg.practice_set(2, 0)
    h.pre_hook = pre2; h.press('O', 3, 0); w = 0; op = None
    while w < 40:
        sb = pst()[1]; h.run(1); w += 1
        if sb != 2 and pst()[1] == 2: op = last_pre['v']; break
    h.pre_hook = pre_hook
    if op is not None: check_open(op)
    menu_go(8); h.press('A', 2, 0)                         # 다시 고르기
    if wait_until(lambda: hub()[0] == 2 and pk(0x41C0) == 2 and hub()[7] == 0, 2500) is None: info('다시 고르기 실패 %d' % k); break
ok(entries == ndum, '더미 %d명(15명 = 유가 포함, 수라·나찰 번갈아) 모두 경기 들어가고 «다시 고르기»로 돌아옴 (%d)' % (ndum, entries))
ok(not cpu_block, '싸우지 않는 6조합(소게츠 수라·나코루루/리무루루/한조/모로즈미/주베이 나찰)은 CPU 를 못 고르고(메뉴에서도), 나머지는 CPU 됨 %s' % cpu_block)
used_by = {}
for t, v in refs.items():
    for where, who in v: used_by.setdefault(who[2], set()).add(t)
info('P-15 측정: 0x0D8~0x105 중 게임이 쓴 타일 %d개 — 내 캐릭터별(첫째 판 효과 층) %s' % (len(refs), {k: '%03X~%03X(%d)' % (min(v), max(v), len(v)) for k, v in sorted(used_by.items())}))
ok(not any(w_[0] != 'plane0' for v in refs.values() for w_ in v), '0x0D8~0x105 를 쓴 것은 첫째 판(효과 층)뿐 — 스프라이트·둘째 판은 안 씀')
ok(OPENS[0] >= (20 if QUICK else 110) and not OVERLAP, '메뉴를 연 %d번 모두: 창이 빌린 타일·팔레트는 열기 직전 두 판·스프라이트 어디서도 안 쓰이던 것 (겹침 %s)' % (OPENS[0], OVERLAP[:3]))
print('%s: %s' % (tag, 'ALL PASS' if not fails else '%d FAIL' % fails))

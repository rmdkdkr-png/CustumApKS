"""리그·연습 «둘 다»(실행 창 옵션 하나) 시험 — league.c 허브의 셋째 줄 ◀▶ 고르기·갈아타기 요청·갈아탄 판 바로 상대 선택·4배속 로고 넘기기·
상태 저장 전 되돌리기를 실제 코어 옆에서(앱 native.c 와 같은 순서: ph.PH) 본다.
사용: python3 t_dual.py <롬>   (PYTHONPATH: handoff/ss2_league · ss2_league/stage1/tests · ss2_practice/stage1/tests, LEAGUE_HOST_SO=league.c+practice.c 호스트 .so,
      PRACTICE_CPP=<앱>/app/src/main/cpp — practice_glyphs.h·hub_glyphs.h 에서 메뉴 글자 그림을 읽는다)"""
import os, re, sys, ctypes as C
import ph
from ph import PH, hub, pst, to_title
ROM = sys.argv[1]; tag = os.path.splitext(os.path.basename(ROM))[0]
lg = ph.lg
CPP = os.environ.get('PRACTICE_CPP', '')
def carr(path, name):
    s = open(os.path.join(CPP, path), encoding='utf-8').read()
    m = re.search(r'%s\[\d+\]\s*=\s*\{([^}]*)\}' % name, s)
    return bytes(int(x, 16) for x in re.findall(r'0x[0-9A-Fa-f]{2}', m.group(1)))
YEON = carr('practice_glyphs.h', 'PG_MENU_YEONSEUP'); RIGEU = carr('hub_glyphs.h', 'HUB_MENU_RIGEU')
AR_L, AR_R = 0x12E, 0x12F
def dual():
    v = (C.c_int * 6)(); lg.league_hub_dual_status(v); return list(v)
fails = 0
def ok(c, what):
    global fails
    print(('PASS ' if c else 'FAIL ') + what, flush=True); fails += (not c)
ROSTER = {11: (0, 1), 3: (1, 1), 4: (0, 0), 2: (0, 1), 9: (1, 1), 5: (0, 0), 6: (0, 0), 7: (0, 0), 0: (1, 2), 8: (1, 2), 13: (0, 2), 14: (1, 2)}
sty = (C.c_byte * 15)(*[ROSTER[c][0] if c in ROSTER else -1 for c in range(15)])
dif = (C.c_byte * 15)(*[ROSTER[c][1] if c in ROSTER else 1 for c in range(15)])
W = os.environ.get('LEAGUE_WORK', '/tmp/league_work')
def shot(h, name): h.p.shot(os.path.join(W, 'dual_%s_%s.png' % (tag, name)))
def t14(h, c): return h.ent(1, 14, c) & 0x1FF
def blank(h, t): return h.tile(t) == bytes(16)

h = PH(ROM, os.path.join(W, 'dual_' + tag)); p = h.p
kind = None
# ── 1. 연습 판(일반 세션) + 둘 다 ──────────────────────────────────────────
lg.league_practice_hub(1, 0); lg.league_hub_dual(1)
d = dual(); ok(d[:3] == [1, 1, 0] and d[4] == 1, '연습 판에 둘 다 켬 — 셋째 줄은 연습부터 (%s)' % d)
to_title(h)                                             # 커서 셋째 줄
kind = 1 if t14(h, 7) == 0x1BB else 2
shot(h, '1_yeon')
d = dual(); ok(d[3] == 1 and d[5] == 0, '셋째 줄 커서 = 화살표 표시 상태 · 메뉴 화면 0(타이틀)')
if kind == 1:
    ok(h.tile(0x1BB) + h.tile(0x1BC) == YEON, '한글판: 셋째 줄 글자 «연습»')
    ok(t14(h, 6) == AR_L and t14(h, 12) == AR_R and not blank(h, AR_L) and not blank(h, AR_R), '한글판: 6칸 ◀ · 12칸 ▶ (타일 0x12E·0x12F 그림)')
else:
    ok([t14(h, c) for c in range(5, 15)] == [AR_L, 0x1C1, 0x1B9, 0x1B5, 0x1C5, 0x1CB, 0x1CC, 0x1CA, 0x1C9, AR_R], '순정판: ◀PRACTICE▶ (5~14칸)')
mcur0 = p.peek(0x624B)
h.press('R', 4, 20); d = dual()
ok(d[1] == 0 and p.peek(0x624B) == mcur0 and p.peek(0x41C0) == 0, '→ 로 리그로 바뀜 · 게임 메뉴 커서·화면 그대로')
if kind == 1: ok(h.tile(0x1BB) + h.tile(0x1BC) == RIGEU and t14(h, 6) == AR_L, '한글판: 글자 «리그» · 화살표 그대로')
else: ok([t14(h, c) for c in range(5, 15)] == [AR_L, 0x1C2, 0x1C9, 0x1C3, 0x1CF, 0x1B8, 0x1D2, AR_R, 0x17F, 0x17F], '순정판: ◀LEAGUE▶ · 13·14칸은 창 바탕으로')
shot(h, '2_rigeu')
h.press('L', 4, 20); ok(dual()[1] == 1, '← 로 다시 연습')
h.press('R', 4, 20); h.press('R', 4, 20); ok(dual()[1] == 1, '→ 두 번 = 한 바퀴(둘뿐)')
h.press('U', 4, 30); d = dual()
ok(p.peek(0x624B) == 1 and d[3] == 0 and (t14(h, 6) == 0x1B0 if kind == 1 else t14(h, 5) != AR_L), '커서를 위로 — 화살표 숨김 (글자는 그대로)')
h.press('D', 4, 30); ok(dual()[3] == 1, '다시 셋째 줄 — 화살표')
# 상태 저장 직전 되돌리기
lg.league_hub_before_save()
if kind == 1: ok(h.tile(0x1BB) + h.tile(0x1BC) not in (YEON, RIGEU) and t14(h, 6) == 0x1B0 and t14(h, 12) == 0x1B0 and blank(h, AR_L) and blank(h, AR_R),
                 '저장 직전: 원래 «2 인» 그림 · 화살표 칸·타일 비움')
else: ok(t14(h, 5) == 0x1BF and blank(h, AR_L), '저장 직전: 순정판 셋째 줄 «VS PLAY» 첫 글자로 되돌림')
h.run(2); ok(dual()[3] == 1 and t14(h, 6 if kind == 1 else 5) == AR_L, '다음 프레임에 다시 바꿔 그림')
# 같은 판(연습)에서 A → 연습 흐름
h.press('A', 4, 240); h.run(30); s = hub()
ok(s[0] == 2 and p.peek(0x41C0) == 2 and dual()[5] == 2, '연습 쪽에서 A — 상대 선택으로(허브 상태 %d · 메뉴 화면 2)' % s[0])
ok(blank(h, AR_L) and blank(h, AR_R), '타이틀을 떠나면 화살표 타일을 비움')
# ── 2. 연습 판에서 리그를 고르면 갈아타기 요청 ───────────────────────────
p.lib.retro_reset(); lg.league_practice_return(0); lg.practice_forget()
f0 = h.frames
while hub()[0] != 1 and h.frames - f0 < 1500: h.run(1)
ok(hub()[0] == 1 and p.peek(0x624B) == 2 and h.frames - f0 < 300, '리셋 뒤 타이틀 셋째 줄로 돌아옴 (%d프레임)' % (h.frames - f0))
ok(dual()[1] == 1, '돌아오면 셋째 줄은 이 판의 종류(연습)')
h.press('R', 4, 20); h.press('A', 4, 20); d = dual()
ok(d[2] == 1, '리그 쪽에서 A — 갈아타기 요청 1(리그) (%s)' % d)
h.press('A', 4, 60); h.press('D', 4, 30); h.run(60)
ok(hub()[0] == 1 and p.peek(0x41C0) == 0 and p.peek(0x624B) == 2, '요청 중엔 메뉴가 그대로(A·↑↓ 막음)')
lg.league_hub_handoff_clear(); h.run(2); d = dual()
ok(d[2] == 0 and d[1] == 1, '요청 지우기 — 셋째 줄 연습으로')
del h
# ── 3. 갈아탄 리그 판: 전원 → 바로 상대 선택 ─────────────────────────────
h = PH(ROM, os.path.join(W, 'dual2_' + tag)); p = h.p
lg.league_hub(1, sty, dif); lg.league_hub_dual(1); lg.league_hub_go()
f0 = h.frames
while not (hub()[0] == 2 and p.peek(0x41C0) == 2) and h.frames - f0 < 2000: h.run(1)
ok(hub()[0] == 2 and p.peek(0x40A7) == 240 and p.peek(0x41C0) == 2 and h.frames - f0 < 400, '리그 판 새로 켜기 → 로고·메뉴를 넘겨 상대 선택까지 (%d프레임)' % (h.frames - f0))
h.run(40); s0 = hub()[9]
h.press('O', 4, 20); s1 = hub()[9]
ok(s1 != s0, 'OPTION = 스테이지 (연습과 같게) (%d → %d)' % (s0, s1))
h.press('B', 4, 20); ok(hub()[9] != s1, 'B 도 스테이지(예전 그대로)')
shot(h, '3_league_pick')
# 리셋 → 타이틀 → 리그 판에서 연습 고르기 = 요청 2
p.lib.retro_reset(); lg.league_hub_return(-1)
f0 = h.frames
while hub()[0] != 1 and h.frames - f0 < 1500: h.run(1)
d = dual(); ok(hub()[0] == 1 and d[1] == 0 and d[3] == 1, '리그 판 타이틀 — 셋째 줄 리그 · 화살표 (%s)' % d)
if kind == 1: ok(h.tile(0x1BB) + h.tile(0x1BC) == RIGEU, '한글판: «리그»')
h.press('L', 4, 20); h.press('U', 4, 30); d = dual()
ok(d[1] == 0 and d[3] == 0 and (h.tile(0x1BB) + h.tile(0x1BC) == RIGEU if kind == 1 else t14(h, 6) == 0x1C2), '← 연습으로 바꾼 뒤 커서를 떠나면 이 판의 종류(리그)로 되돌아감')
h.press('D', 4, 30)
h.press('L', 4, 20); h.press('A', 4, 20); d = dual()
ok(d[1] == 1 and d[2] == 2, '← 연습 → A — 갈아타기 요청 2(연습) (%s)' % d)
lg.league_hub_handoff_clear(); h.run(2)
# «다른 상대»(−2): 리셋 뒤 타이틀에서 멈추지 않고 상대 선택까지
p.lib.retro_reset(); lg.league_hub_return(-2)
f0 = h.frames
while not (hub()[0] == 2 and p.peek(0x41C0) == 2) and h.frames - f0 < 2000: h.run(1)
ok(hub()[0] == 2 and p.peek(0x41C0) == 2, '«다른 상대» — 리셋 뒤 바로 상대 선택 (%d프레임)' % (h.frames - f0))
del h
# ── 4. 둘 다 안 켠 옛 허브는 그대로(화살표 없음 · ←→ 안 막음) ───────────────
h = PH(ROM, os.path.join(W, 'dual3_' + tag)); p = h.p
lg.league_practice_hub(1, 0)
to_title(h)
ok(dual()[0] == 0 and (t14(h, 6) == 0x1B0 if kind == 1 else t14(h, 5) == 0x1C1), '둘 다 끔: 화살표 없이 «연습 대전»/«PRACTICE» (예전 자리)')
h.press('R', 4, 20); ok(dual()[1] == 1, '둘 다 끔: → 는 아무 일 없음')
del h
# ── 5. 앞 판(내부 134)이 남긴 연습 이어하기 파일 — 허브 뒤 새 칸(72바이트)이 없는 636바이트 덩어리도 받는다 ──
h = PH(ROM, os.path.join(W, 'dual4_' + tag)); p = h.p
lg.league_practice_hub(1, 0)
to_title(h); ph.to_fight(h)
lg.league_practice_blob.restype = C.c_size_t; lg.league_practice_blob.argtypes = [C.c_void_p, C.c_size_t]
buf = C.create_string_buffer(4096); n = lg.league_practice_blob(buf, 4096); blob = buf.raw[:n]
dm = C.c_int(); st = C.c_int(); on0 = lg.league_practice_match(C.byref(dm), C.byref(st)); d0 = dm.value
ok(on0 == 1 and n > 636, '연습 경기 중 허브 덩어리 %d바이트(지금 판)' % n)
LN = 132 + 28                                          # 랭크 시제품: L 에 7칸(손잡이 5 · cap_seen · from_ckpt = 28바이트)이 붙었다
hn = n - LN - 8                                        # 지금 허브 크기(덩어리 = 허브 + L + 배경·컬러 8)
old = blob[:496] + blob[hn:hn + 132] + blob[-8:]       # 앞 판 모양: 허브 496바이트(둘 다 칸 앞까지) + 옛 L 132 + 배경·컬러
lg.league_practice_title(); on1 = lg.league_practice_match(None, None)
lg.league_practice_resume.argtypes = [C.c_void_p, C.c_size_t]
ob = C.create_string_buffer(old, len(old)); lg.league_practice_resume(ob, len(old))
on2 = lg.league_practice_match(C.byref(dm), C.byref(st))
ok(on1 == 0 and on2 == 1 and dm.value == d0 and dual()[0] == 0, '앞 판 636바이트 덩어리로 연습 경기 되돌림(더미 %d · 둘 다 칸은 0)' % dm.value)
# ── 6. (랭크 시제품) 내부 136·137 이 남긴 덩어리 — 허브 랭크 칸(56바이트)·L 손잡이 칸(24바이트)이 없는 크기
h137 = hn - 56
b137 = blob[:h137] + blob[hn:hn + 132] + blob[-8:]
lg.league_practice_title(); on1 = lg.league_practice_match(None, None)
bb = C.create_string_buffer(b137, len(b137)); lg.league_practice_resume(bb, len(b137))
on2 = lg.league_practice_match(C.byref(dm), C.byref(st))
ok(on1 == 0 and on2 == 1 and dm.value == d0, '내부 137 덩어리 %d바이트로 연습 경기 되돌림(더미 %d)' % (len(b137), dm.value))
print('DONE fails=%d' % fails)

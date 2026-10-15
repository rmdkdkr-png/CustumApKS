"""모든 모드 컬러(look.c) × 허브 — 연습 대전·리그 대전에서 상대 선택(허브가 OPTION 을 씀)엔 손대지 않고, 내 캐릭터에서만 컬러를 쥔다.
사용: python3 t_look_hub.py <ROM 환경변수 이름> [fast]"""
import os, sys, json, ctypes as C
import lh, ph, cx
from lh import lg, lst, mem, set_mem, tri, vp_label
from ph import hub, pst
rom_key = sys.argv[1] if len(sys.argv) > 1 else 'ROM_KO'; rom = os.environ[rom_key]
fast = len(sys.argv) > 2 and sys.argv[2] == 'fast'
VL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'look_vlab.json')))
LABS = [bytes(VL[i * 288:(i + 1) * 288]) for i in range(18)]
res = []; tag = rom_key.lower()
def ok(c, msg): res.append(c); print(('PASS ' if c else 'FAIL ') + msg, flush=True)
def pal(h, k): return cx.pal(h, k)[1:]
def hx(t): return '/'.join('%03x' % c for c in t)
def fight_wait(h, limit=6000):
    p = h.p; g = 0
    while not (p.peek(0x40A7) == 241 and p.peek(0x411A) == 1) and g < limit:
        if p.peek(0x40A7) == 240 and p.peek(0x41C0) == 6 and g % 60 == 30: h.press('R', 4, 0); h.press('A', 4, 0); g += 8; continue
        h.run(1); g += 1
    return g

# ── 연습 대전 ──
h = lh.mk(rom, 'tlh_pr_' + tag, fast); p = h.p
lg.look_forget(); lg.look_enable(1); set_mem([0] * 16)
lg.league_practice_hub(1, 0)
ph.to_title(h)                                            # 셋째 줄 «연습 대전»
h.press('A', 4, 240); h.run(30)
s = hub(); m0 = mem()
ok(s[0] == 2 and lst()[1] == 0 and lh.gi('look_in_block') == 0, '연습 상대 선택: 허브가 고르기 화면을 씀 → look 은 안 쥠(막는 비트 0)')
lab0 = vp_label(h); st0 = s[9]
h.press('O', 4, 20); s = hub()
ok(s[9] != st0 and mem() == m0 and vp_label(h) is not None and vp_label(h) not in LABS,
   '연습 상대 선택 OPTION = 스테이지(%d → %d), 컬러 기억 그대로, 세로 칸 = 스테이지 이름(컬러 글자 아님)' % (st0, s[9]))
hov = p.peek(0x4E3C) >> 2
ok(pal(h, 0) == tri(hov, 0, 0), '상대 선택 미리보기(상대 캐릭터) 색은 원래대로 %s' % hx(pal(h, 0)))
h.press('A', 4, 60)                                       # 더미 = 커서 캐릭터 수라
s = hub(); h.run(4)
ok(s[0] == 3 and lst()[1] == 1 and vp_label(h) == LABS[0], '더미를 고름 → 내 캐릭터: look 이 쥠, 세로 칸 «기본»')
cur = p.peek(0x4E3C) >> 2
for m in ph.move_seq(cur, 9): h.press(m, 4, 20)          # 내 캐릭터 샬럿
for i in range(5): h.press('O', 4, 6)                    # → 다홍(5)
s = hub()
ok(lst()[3] == 5 and s[10] == 5 and pal(h, 0) == tri(9, 0, 5) and vp_label(h) == LABS[5],
   '내 캐릭터 샬럿 OPTION 다섯 번 → «다홍»(허브 상태 v[10] 도 %d) 미리보기 %s' % (s[10], hx(pal(h, 0))))
h.press('A', 4, 100); h.press('A', 4, 0)
g = 0
while not pst()[0] and g < 6000:
    if p.peek(0x40A7) == 240 and p.peek(0x41C0) == 6 and g % 60 == 30: h.press('R', 4, 0); h.press('A', 4, 0); g += 8; continue
    h.run(1); g += 1
h.run(30)
ok(pst()[0] == 1 and p.peek(0x5B51) == 0x90 and pal(h, 0) == tri(9, 0, 5), '연습 경기: P1 샬럿 수라 «다홍» %s' % hx(pal(h, 0)))
cx.fb_img(h).save(os.path.join(cx.W, 'tlh_%s_practice.png' % tag))
# 연습 메뉴(OPTION)는 경기 중 그대로 — look 은 경기 중 입력을 안 막는다
ok(lh.gi('look_in_block') == 0, '연습 경기 중 look 이 막는 입력 없음(OPTION = 연습 메뉴 그대로)')
del h

# ── 리그 대전 ──
ROSTER = {11: (0, 1), 3: (1, 1), 4: (0, 0), 2: (0, 1), 9: (1, 1), 5: (0, 0), 6: (0, 0), 7: (0, 0), 0: (1, 2), 8: (1, 2), 13: (0, 2), 14: (1, 2)}
sty = (C.c_byte * 15)(*[ROSTER[c][0] if c in ROSTER else -1 for c in range(15)])
dif = (C.c_byte * 15)(*[ROSTER[c][1] if c in ROSTER else 1 for c in range(15)])
home = (C.c_byte * 15)(*[6 if c in ROSTER else -1 for c in range(15)])
h = lh.mk(rom, 'tlh_lg_' + tag, fast); p = h.p
lg.look_forget(); lg.look_enable(1); set_mem([0] * 16)
lg.league_hub(1, sty, dif); lg.league_hub_look(home, -1, 0)
ph.to_title(h)
h.press('A', 4, 240); h.run(30)
s = hub(); st0 = s[9]
h.press('O', 4, 20); s = hub()
ok(s[0] == 2 and s[9] != st0 and lst()[1] == 0 and mem() == [0] * 16, '리그 상대 선택 OPTION = 스테이지(%d → %d), look 안 쥠' % (st0, s[9]))
h.press('A', 4, 60); s = hub(); h.run(4)                  # 가운데 아수라 상대
ok(s[0] == 3 and s[2] == 8 and lst()[1] == 1 and vp_label(h) == LABS[0], '리그 상대 아수라 고름 → 내 캐릭터: look 이 쥠, 세로 칸 «기본»')
cur = p.peek(0x4E3C) >> 2
for m in ph.move_seq(cur, 11): h.press(m, 4, 20)
h.press('B', 40, 160); s = hub()
ok(p.peek(0x41C0) == 4 and lst()[3] == 1 and s[10] == 1 and vp_label(h) == LABS[1], '리그 내 캐릭터 우쿄 B → 2P색으로 결정·검질 고르기(B 길게도 안 샘)')
h.press('A', 4, 0); fight_wait(h); h.run(30)
st = ph.T.status()
ok(st[0] == 1 and st[3] == 1 and p.peek(0x5B51) == 0xB0 and p.peek(0x5D51) >> 4 == 8 and pal(h, 0) == tri(11, 0, 1),
   '리그 경기: 무장·경기 시작, P1 우쿄 수라 2P색 %s, 상대 아수라' % hx(pal(h, 0)))
cx.fb_img(h).save(os.path.join(cx.W, 'tlh_%s_league.png' % tag))
# 체크포인트 이어 하기 길(league_look → look_set_match): 상태 저장 → 새 판 → 불러오기 → league_look(stage, 컬러)
lg.league_hub_before_save(); lg.look_before_save(); raw = h.serialize()
del h
h2 = lh.mk(rom, 'tlh_lg2_' + tag, fast)
lg.look_forget(); lg.look_enable(1); lg.league_hub(0, None, None)
h2.unserialize(raw); lg.league_look(1, 9); lg.league_arm(8, 1, 2, 2, 60, 2 | 8); h2.run(3)
ok(lst()[4] == 9 and pal(h2, 0) == tri(11, 0, 9), '체크포인트 이어 하기(league_look(배경, 9)): 0x57D5(%d) 캐릭터로 «황금» %s' % (h2.p.peek(0x57D5), hx(pal(h2, 0))))
print('== %d/%d 통과 (%s)' % (sum(res), len(res), rom_key))

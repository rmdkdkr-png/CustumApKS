"""연습 경기 이어가기 시험 — 상태 저장 옆 .prac(native.c)이 담는 허브(league_practice_blob)·설정(practice_settings_get)을
불러온 뒤 되돌리면(league_practice_resume / practice_settings_set) 연습 경기가 그대로 이어지는가.
native.c 의 순서를 그대로 흉내 낸다:
  옵션 바꾸기(applyLive)·이어하기: load_locked(league_disarm · league_hub(0) · practice_forget · resume(NULL)) → 상태 불러오기
                                    (practice_forget · league_practice_title · 설정 · resume(허브)) → Java practiceSetup → league_practice_hub(1, 0)
  슬롯 불러오기(같은 판): 상태 불러오기만 — 허브가 켜져 있으니 바로 되돌린다
  .prac 없는 상태: 예전처럼 타이틀 상태(연습 꺼짐)

사용: PYTHONPATH=<handoff/ss2_league>:<handoff/ss2_league/stage1/tests>:<이 폴더> LEAGUE_HOST_SO=<league.c+practice.c 호스트 .so>
      LEAGUE_CORE=<코어> LEAGUE_WORK=<작업 폴더> python3 t_resume.py <롬>
"""
import os, sys, ctypes as C
from ph import *
ROM = sys.argv[1]; tag = os.path.splitext(os.path.basename(ROM))[0]
W = T.work('rs_' + tag); os.makedirs(W, exist_ok=True)
lg.league_practice_blob.argtypes = [C.c_void_p, C.c_size_t]; lg.league_practice_blob.restype = C.c_size_t
lg.league_practice_resume.argtypes = [C.c_void_p, C.c_size_t]
lg.practice_settings_get.argtypes = [C.c_void_p, C.c_size_t]; lg.practice_settings_get.restype = C.c_size_t
lg.practice_settings_set.argtypes = [C.c_void_p, C.c_size_t]
fails = 0
def ok(c, what):
    global fails
    print(('PASS ' if c else 'FAIL ') + what, flush=True); fails += (not c)
def blob():
    b = C.create_string_buffer(4096); n = lg.league_practice_blob(b, 4096); return b.raw[:n]
def settings():
    b = C.create_string_buffer(256); n = lg.practice_settings_get(b, 256); return b.raw[:n]
def resume(raw):
    if raw: b = C.create_string_buffer(raw, len(raw)); lg.league_practice_resume(b, len(raw))
    else: lg.league_practice_resume(None, 0)
def set_settings(raw):
    b = C.create_string_buffer(raw, len(raw)); lg.practice_settings_set(b, len(raw))
def save():
    """nativeSaveState 처럼 — 저장 직전 되돌리기 → 상태 · 같은 순간의 허브·설정"""
    lg.practice_before_save(); lg.league_hub_before_save()
    return h.serialize(), blob(), settings()
def load_state(st, hb, ss):
    """nativeLoadState 처럼"""
    h.unserialize(st); lg.practice_forget(); lg.league_practice_title()
    if hb: set_settings(ss); resume(hb)
    else: resume(b'')
def load_core():
    """load_locked 처럼(코어 다시 올림) — 프로세스가 새로 떴을 때처럼 설정도 처음 값으로"""
    lg.league_disarm(); lg.league_hub(0, None, None); lg.practice_forget(); resume(b'')
    for k in range(7): lg.practice_set(k, 0)
def timer(): return h.p.peek16(0x582F)

h = PH(ROM, W); p = h.p
to_title(h)
lg.league_hub(0, None, None); lg.league_practice_hub(1, 0); h.run(3)
ok(len(blob()) == 0, '타이틀(연습 경기 아님)에서는 허브를 안 담는다')
to_fight(h)
h.run(30)
ok(pst()[0] == 1 and hub()[0] == 4, '연습 경기 시작 [연습 %d · 허브 %d]' % (pst()[0], hub()[0]))
lg.practice_set(1, 1); lg.practice_set(2, 1); lg.practice_set(4, 2); h.run(20)
st, hb, ss = save()
ok(len(hb) > 0 and len(ss) > 0, '연습 경기 중엔 허브·설정을 담는다 [%d · %d 바이트]' % (len(hb), len(ss)))
h.run(120)

# ── 1. 옵션 바꾸기·이어하기(코어 다시 올림 → 상태 불러오기 → 허브 켜기)
load_core()
load_state(st, hb, ss)
lg.league_practice_hub(1, 0)
h.run(30)
s = pst()
ok(s[0] == 1 and hub()[0] == 4, '다시 올린 판: 연습 경기로 이어짐 [연습 %d · 허브 %d]' % (s[0], hub()[0]))
ok(s[4] == 1 and s[5] == 1 and s[7] == 2, '다시 올린 판: 설정 그대로(가드 전부 · 내 분노 MAX · 리셋 오른쪽 벽) %s' % s[4:8])
ok(timer() == 0xFFFF, '다시 올린 판: 시간 ∞ 유지 [%04x]' % timer())
h.press('O', 4, 12)
ok(pst()[1] == 2, '다시 올린 판: 연습 메뉴가 열린다 [메뉴 %d]' % pst()[1])
h.press('B', 4, 30)
ok(pst()[1] == 0 and p.peek(0x61D4) != 1, '다시 올린 판: 메뉴 닫힘·일시정지 풀림 [메뉴 %d · 정지 %d]' % (pst()[1], p.peek(0x61D4)))
n0 = pst()[11]; lg.practice_set(7, -1); h.run(240)
ok(pst()[11] > n0, '다시 올린 판: 리셋 된다 [%d → %d]' % (n0, pst()[11]))

# ── 2. 같은 판에서 슬롯 불러오기(허브가 켜진 채 — 바로 되돌림)
h.run(60)
load_state(st, hb, ss)
h.run(30)
ok(pst()[0] == 1 and hub()[0] == 4, '슬롯 불러오기: 연습 경기 그대로 [연습 %d · 허브 %d]' % (pst()[0], hub()[0]))

# ── 3. .prac 없는 상태(연습 아님) — 예전처럼 타이틀 상태, 연습 꺼짐
load_state(st, b'', b'')
h.run(30)
ok(pst()[0] == 0 and hub()[0] == 1, '.prac 없는 불러오기: 연습 꺼짐·허브 타이틀 [연습 %d · 허브 %d]' % (pst()[0], hub()[0]))

# ── 4. 기다리던 되돌리기는 코어를 다시 올리면 버린다(새로 연 판이 옛 경기로 가지 않게)
load_core()
load_state(st, hb, ss)          # 허브 꺼진 채 — 기다림
load_core()                     # 상태 없이 다시 올림(이어하기 없음)
p.lib.retro_reset(); lg.league_practice_hub(1, 0); h.run(30)
ok(hub()[0] == 1 and pst()[0] == 0, '상태 없이 다시 올린 판: 옛 연습 경기로 안 감 [허브 %d · 연습 %d]' % (hub()[0], pst()[0]))

print('%s: %s' % (tag, 'ALL PASS' if not fails else '%d FAIL' % fails), flush=True)
sys.exit(1 if fails else 0)

"""H-2 — 기존 시험(연습 t_practice·t_fix1·t_resume·t_dual, 리그 t_hub)을 시험 파일은 그대로 두고 cheat_tick 을 끼워 돌린다.
앱 native.c 와 같은 자리: practice_tick 바로 뒤(연습 하네스 ph.PH) · league_tick_hub 바로 뒤(리그 t_hub — 연습 없음).
앱처럼: 코어를 새로 올리면(하네스 생성) cheat_reset_all + 값 넣기, 리셋·불러오기 뒤 cheat_forget(practice_forget·unserialize 옆), 상태 저장 직전·직후 cheat_before_save·cheat_after_save.
사용: with_cheat.py <off|on> <시험.py> [인자…]
  off = 치트 모두 끔(결과가 치트 없을 때와 같아야 — cheat_tick 이 한 바이트도 안 씀)
  on  = 모두 켬(올카드 이번만·시간 무한·한 방 둘 다·분노 MAX 둘 다·상대 가만히·CPU 최강·공격력 3배·유가 나찰) — 연습·리그가 막으니 연습·리그 항목은 그대로,
        «연습을 안 고른 1인 대전 = 원래 게임» 같은 일반 판 비교만 달라진다"""
import os, sys, runpy, ctypes as C
mode = sys.argv[1]; script = os.path.abspath(sys.argv[2]); sys.argv = [script] + sys.argv[3:]
sys.path.insert(0, os.path.dirname(script))
import hosttest as T
lg = T.lg
VALS = [0] * 10 if mode == 'off' else [1, 1, 2, 2, 1, 1, 1, 5, 3, 2]
lg.cheat_tick.argtypes = [C.c_void_p, C.c_size_t, C.c_int]
lg.cheat_before_save.argtypes = [C.c_void_p]
lg.league_tick_hub.argtypes = [C.c_void_p, C.c_size_t, C.c_int]
lg.practice_tick.argtypes = [C.c_void_p, C.c_size_t, C.c_int]
_hub, _prac, _pforget = lg.league_tick_hub, lg.practice_tick, lg.practice_forget
USE_PRAC = [False]                       # 연습 하네스(ph.PH)면 practice_tick 뒤, 아니면(리그 t_hub) league_tick_hub 뒤
TICKS = [0]
def hub_tick(ram, n, inp):
    _hub(ram, n, inp)
    if not USE_PRAC[0]: lg.cheat_tick(ram, n, inp); TICKS[0] += 1
def prac_tick(ram, n, inp):
    _prac(ram, n, inp)
    lg.cheat_tick(ram, n, inp); TICKS[0] += 1
def pforget():
    _pforget(); lg.cheat_forget()
lg.league_tick_hub = hub_tick; lg.practice_tick = prac_tick; lg.practice_forget = pforget
_init = T.Harness.__init__
def init(self, *a, **k):
    _init(self, *a, **k)
    lg.cheat_reset_all()                 # 코어 올리기 = 모두 끔 → 일반 세션이면 Java 가 값을 넣는다
    for i, v in enumerate(VALS): lg.cheat_set(i, v)
T.Harness.__init__ = init
try:
    import ph
    USE_PRAC[0] = True
    _ser, _unser = ph.PH.serialize, ph.PH.unserialize
    lg.cheat_after_save.argtypes = [C.c_void_p]
    def ser(self):
        lg.cheat_before_save(self.p._ramp); r = _ser(self); lg.cheat_after_save(self.p._ramp); return r
    def unser(self, raw): _unser(self, raw); lg.cheat_forget()
    ph.PH.serialize = ser; ph.PH.unserialize = unser
except Exception:
    pass                                 # 리그 t_hub 는 ph 없이도(PYTHONPATH 에 연습 폴더가 없을 때)
if os.path.basename(script) == 't_hub.py': USE_PRAC[0] = False
import atexit
atexit.register(lambda: print('[with_cheat %s] cheat_tick %d번' % (mode, TICKS[0]), flush=True))
runpy.run_path(script, run_name='__main__')

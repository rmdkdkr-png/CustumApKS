"""league.c 를 실제 코어 옆에서 돌리는 호스트 하네스 — 앱 native.c 의 nativeFrame 과 같은 자리(retro_run 뒤)에서 league_tick 을 부르고,
메뉴 자동 진입 중엔 입력 콜백처럼 league_ovr_mask 를 입력으로 준다.

준비:  gcc -O2 -shared -fPIC -I<jni.h 가 있는 폴더> -o libleague_host.so <Legacito>/app/src/main/cpp/league.c
       (NDK 의 sysroot/usr/include/jni.h 하나만 따로 복사한 폴더를 -I 로 — sysroot 통째로 주면 호스트 gcc 가 깨진다)
환경:  LEAGUE_CORE=<ss2-sp-core>/cores/mednafen_ngp_libretro.linux-x86_64.so · PYTHONPATH 에 handoff/ss2_league(ss2probe)와 이 폴더
"""
import os, ctypes as C, ss2probe
H = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get('LEAGUE_WORK', '/tmp/league_work'); os.makedirs(WORK, exist_ok=True)
def work(name): return os.path.join(WORK, name)
CORE = os.environ.get('LEAGUE_CORE', '/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so')
lg = C.CDLL(os.environ.get('LEAGUE_HOST_SO', os.path.join(H, 'libleague_host.so')))
lg.league_tick.argtypes = [C.c_void_p, C.c_size_t]
def status():
    v = (C.c_int * 22)(); lg.league_status(v); return list(v)
class Harness:
    def __init__(self, rom, wd, runahead=True):
        if runahead:   # Legacito 기본(런어헤드 2·프레임 생성 켬)과 같게
            ss2probe.OPTIONS[b'ngp_runahead'] = b'2'; ss2probe.OPTIONS[b'ngp_framegen'] = b'on'
        self.p = ss2probe.Probe(CORE, rom, wd)
        self.user = 0
    def run(self, n=1):
        for _ in range(n):
            on = C.c_int.in_dll(lg, 'league_ovr_on').value
            self.p.mask = C.c_int.in_dll(lg, 'league_ovr_mask').value if on else self.user
            self.p.run(1); lg.league_tick(self.p._ramp, self.p._rams)
    def press(self, b, frames=6, after=0):
        self.p.mask = 0; self.p.hold(*b); self.user = self.p.mask; self.run(frames); self.user = 0; self.run(after)

"""framedata 실험 공용 — 연습 경기 상태 만들기·되돌리기·프레임 기록.
환경: LEAGUE_HOST_SO · LEAGUE_CORE · LEAGUE_WORK · PYTHONPATH(ss2_league, ss2_league/stage1/tests, ss2_practice/stage1/tests)
FD_MODE=clean(기본: 런어헤드 0 · 프레임 생성 disabled — retro_run 1번 = 진짜 1프레임) | app(런어헤드 2 · 프레임 생성 on — 앱 기본과 같게)"""
import os, sys, ctypes as C, pickle
import ss2probe, hosttest as T
MODE = os.environ.get('FD_MODE', 'clean')
if MODE == 'clean':
    T.Harness.__init__.__defaults__ = (False,)
    ss2probe.OPTIONS[b'ngp_framegen'] = b'disabled'; ss2probe.OPTIONS[b'ngp_runahead'] = b'0'
import ph
from ph import PH, pst, hub, lg, bits, to_title, to_fight, move_seq, rel
HERE = os.path.dirname(os.path.abspath(__file__))
ROMS = {
 'ko': '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/legacito/ss2_ko_bundled.ngc',
 'ko101': '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/legacito/ss2_ko101.ngc',
 'h1ko': '/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/legacito/ss2h1_ko101.ngc',
 'jp': '/root/.claude/uploads/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/ee972d92-Samurai_Shodown_2_JUE_.ngc',
}
NAMES = ['카즈키','소게츠','하오마루','겐쥬로','나코루루','리무루루','한조','갈포드','아수라','샬럿','모로즈미','우쿄','주베이','시키','유가']
def mk(rom='ko', wd=None):
    wd = wd or os.path.join(T.WORK, 'fd_' + rom + '_' + MODE)
    h = PH(ROMS.get(rom, rom), wd); return h
def fight(h, dummy, me, opp_btn='A', my_btn='A', style_btn='A'):
    """전원 → 연습 대전 → 더미 dummy · 나 me → 라운드 진행 첫 프레임 뒤 60프레임"""
    lg.league_practice_hub(1, 0)
    to_title(h)
    h.press('A', 4, 240); h.run(30)
    for m in move_seq(h.p.peek(0x4E3C) >> 2, dummy): h.press(m, 4, 30)
    h.run(10); h.press(opp_btn, 4, 60)
    for m in move_seq(h.p.peek(0x4E3C) >> 2, me): h.press(m, 4, 30)
    h.run(10); h.press(my_btn, 4, 160); h.press(style_btn, 4, 0)
    f = 0
    while f < 6000 and not pst()[0]:
        p = h.p
        if p.peek(0x40A7) == 240 and p.peek(0x41C0) == 6 and f % 60 == 30: h.press('R', 4, 0); h.press('A', 4, 0); f += 8; continue
        h.run(1); f += 1
    k = 0
    while k < 2000 and not (h.p.peek(0x40A7) == 241 and h.p.peek(0x411A) == 1): h.run(1); k += 1
    h.run(60)
    assert pst()[0] == 1, 'practice not active'
    return h
def snap(h):
    return (h.serialize(), h.pstate(), h.frames)
def restore(h, s):
    h.unserialize(s[0]); h.pstate_set(s[1]); h.user = 0
def cache_fight(h, key, dummy, me, **kw):
    fn = os.path.join(T.WORK, 'fd_%s.pkl' % key)
    if os.path.exists(fn):
        # 경기 상태로 가려면 허브가 경기 중이어야 한다 — 매번 실제로 들어간다(허브 상태는 직렬화에 없다)
        pass
    fight(h, dummy, me, **kw)
    return snap(h)

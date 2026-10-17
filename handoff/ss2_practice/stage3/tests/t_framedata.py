"""프레임 데이터 호스트 시험 — practice.c(시제품, proto/) 의 fd_tick 을 실제 코어 옆에서 돌려
(1) 참조 구현 fd_ref.py 와 프레임마다 같음(미터 160칸·요약·유불리) (2) 실측 표 값 (3) 결정성 (4) 메뉴 «표시» 줄·설정 저장.
사용: LEAGUE_HOST_SO=<proto 로 만든 .so> ... python3 t_framedata.py <롬키> [빠르게]"""
import sys, random, ctypes as C
from tr import *
import fd_ref
ph.pst.__code__ = (lambda: (lambda v: (lg.practice_status(v), list(v))[1])((C.c_int * 26)())).__code__   # PRACTICE_NSTAT 26
lg.practice_fd_get.argtypes = [C.c_void_p, C.c_void_p]; lg.practice_fd_get.restype = C.c_uint32
ROM = sys.argv[1] if len(sys.argv) > 1 else 'ko'; QUICK = len(sys.argv) > 2
fails = 0
def ok(c, what):
    global fails
    print(('PASS ' if c else 'FAIL ') + what, flush=True); fails += (not c)
def fdget():
    cells = (C.c_uint8 * 160)(); s = (C.c_int * 40)(); v = lg.practice_fd_get(cells, s); return list(cells), list(s), v
NONE = 0x7FFF
def ref_view(t):
    cells = t.cell[0] + t.cell[1]
    out = dict(cells=[c if c is not None else 0xFF for c in cells], seq_id=t.seq_id, len=t.len, seq_on=int(t.seq_on), focus=t.focus)
    for p in (0, 1):
        ds = [d for d in t.done if d['p'] == p]
        if not ds: out['sum%d' % p] = (0,); continue
        d = ds[-1]
        st = -1 if d['startup'] is None else d['startup']
        ac = -1 if d['startup'] is None else (-2 if d['proj'] else d['active'])
        rc = -1 if d['startup'] is None else d['recovery']
        pa = d.get('parry') or (-1, 0)
        m = t.mem.get(d['key'], {}) if d['startup'] is not None else t.mem.get(d['key'], None)
        m = m or {}
        mv = (m.get('active', -1) if m.get('active') is not None else (-2 if 'active' in m else -1), m.get('recovery', -1))
        advs = tuple(m.get(k, NONE) for k in ('hit', 'down', 'block', 'throw'))
        out['sum%d' % p] = (len(ds), st, ac, rc, d['total'], d['contact'], pa[0], pa[1]) + mv + advs
    e = t.events[-1] if t.events else None
    out['adv'] = (NONE, 0, 0, 0) if e is None else (e['adv'], e['kind'], e['att'], len(t.events))
    return out
def c_view(cells, s):
    out = dict(cells=cells, seq_id=s[1], len=s[2], seq_on=s[3], focus=s[7])
    for p in (0, 1):
        o = s[8 + 14 * p: 22 + 14 * p]
        out['sum%d' % p] = (0,) if o[0] == 0 else tuple(o)
    out['adv'] = (s[36], s[37], s[38], s[39]) if s[39] else (NONE, 0, 0, 0)
    return out

h = mk(ROM, os.path.join(T.WORK, 'tfd_' + ROM)); p = h.p
lg.practice_set(9, 1)
fight(h, 9, 2)
base = snap(h)
REF = [None]; PRE = {}; MIS = []; NFR = [0]; LASTRES = [0]; SYNC = [False]
def pre(hh): PRE['ram'] = p.ram()
def post(hh):
    ps = ph.pst()
    if not ps[0]: REF[0] = None; return
    r = PRE['ram']; pk = lambda a: r[a - 0x4000]
    ran = pk(0x40A7) == 241 and pk(0x411A) == 1 and pk(0x5824) == 0 and pk(0x61D4) != 1
    if REF[0] is None: REF[0] = fd_ref.FrameData()
    reset_now = ps[11] != LASTRES[0]; LASTRES[0] = ps[11]
    if ran:
        REF[0].step(pk)
        if reset_now: REF[0].reset_keep_mem()                    # 이 프레임에 리셋(순간이동) — practice.c 도 fd_reset(1)
    if reset_now: SYNC[0] = True                                 # 되돌린 상태의 FD 는 참조 구현과 다를 수 있다 — 첫 리셋부터 견준다
    if not SYNC[0]: return
    NFR[0] += 1
    cells, s, v = fdget()
    a, b = ref_view(REF[0]), c_view(cells, s)
    if a != b and len(MIS) < 5:
        diff = {k: (a[k], b[k]) for k in a if a[k] != b[k] and k != 'cells'}
        if a['cells'] != b['cells']:
            i = next(i for i in range(160) if a['cells'][i] != b['cells'][i]); diff['cells@%d' % i] = (a['cells'][i], b['cells'][i])
        MIS.append((NFR[0], diff))
h.pre_hook = pre; h.post_hook = post
def scen(gapv, guard, sc, n, dummy_cpu=0):
    restore(h, base); REF[0] = None; LASTRES[0] = ph.pst()[11]; SYNC[0] = False
    lg.practice_set(1, guard); lg.practice_set(0, dummy_cpu)
    approach(h, gapv); h.run(2)
    for f in range(n):
        if f in sc: h.user = bits(rl(h, sc[f])) if sc[f] else 0
        h.run(1)
    h.user = 0; h.run(60)
    return fdget()
# ── FD-1 참조 구현과 프레임마다 같음 ──
SC = [
 ('5A 헛침', 150, 0, {0: 'A', 2: ''}, 80), ('5A 히트', 24, 0, {0: 'A', 2: ''}, 80), ('5A 가드', 24, 1, {0: 'A', 2: ''}, 80),
 ('5A+ 히트', 24, 0, {0: 'A', 14: ''}, 120), ('2A+ 다운', 24, 0, {0: 'D', 4: 'DA', 18: 'D', 22: ''}, 260),
 ('236A 가드', 40, 1, {0: 'D', 4: 'Df', 8: 'f', 12: 'fA', 16: ''}, 200), ('잡기', 15, 0, {0: 'fA', 16: ''}, 200),
 ('2A>236A', 30, 0, {0: 'D', 6: 'DA', 10: 'D', 22: 'Df', 26: 'f', 30: 'fA', 34: ''}, 300),
 ('↓B 튕겨내기', 150, 0, {0: 'DB', 3: ''}, 70), ('점프 A', 60, 0, {0: 'Uf', 3: '', 22: 'A', 25: ''}, 90),
]
got = {}
for name, g, gd, sc, n in SC:
    MIS.clear(); NFR[0] = 0
    cells, s, v = scen(g, gd, sc, n)
    got[name] = (cells, s)
    ok(not MIS, 'FD-1 %s: 참조 구현과 %d프레임 모두 같음%s' % (name, NFR[0], '' if not MIS else ' — 첫 차이 %s' % (MIS[0],)))
# 무작위(CPU 더미 · 랜덤 가드 · 가끔 리셋)
MIS.clear(); NFR[0] = 0
restore(h, base); REF[0] = None; LASTRES[0] = ph.pst()[11]; SYNC[0] = False; lg.practice_set(0, 1); lg.practice_set(1, 3); lg.practice_set(7, 0)
random.seed(11); f = 0; N = 1500 if QUICK else 6000
while f < N:
    a = random.choice(['', 'f', 'b', 'A', 'DA', 'Uf', 'B', 'bB', 'D', 'fA', 'DB']); d = random.choice((3, 6, 10, 16, 24))
    h.user = bits(rl(h, a)); h.run(min(d, 3)); h.user = 0; h.run(max(0, d - 3)); f += d
    if random.random() < 0.02: lg.practice_set(7, random.choice((0, 1, 2)))
lg.practice_set(0, 0); lg.practice_set(1, 0)
ok(not MIS, 'FD-1 무작위 %d프레임(CPU 더미·랜덤 가드·리셋): 참조 구현과 같음%s' % (NFR[0], '' if not MIS else ' — 첫 차이 %s' % (MIS[0],)))
with open(os.path.join(HERE, 'results', 'fd_sums_%s.txt' % ROM), 'w') as fo:     # JVM 시험(FrameMeterTest)이 읽는 실제 sum
    for name, (cells, s) in got.items(): fo.write('%s|%s\n' % (name, ' '.join(map(str, s))))
# ── FD-2 실측 값(하오마루 vs 샬럿 더미) ──
def P1(s): return s[8:22]
c, s = got['5A 헛침']; ok(P1(s)[1:5] == [7, 6, 14, 26] and P1(s)[5] == 0, 'FD-2 5A 헛침 = 발동 7 · 지속 6 · 경직 14 · 전체 26 %s' % P1(s)[1:6])
ok(bytes(c[:26]) == bytes([2] * 6 + [3] * 6 + [4] * 14) and c[26] == 0xFF, 'FD-2 5A 헛침 미터 = 발동 6칸 · 지속 6칸 · 경직 14칸')
c, s = got['5A 히트']; ok(s[36] == -2 and s[37] == 1 and P1(s)[1] == 7 and s[4] == 9, 'FD-2 5A 히트 = −2 · 발동 7 · 얼린 프레임 9 (%d %d %d %d)' % (s[36], s[37], P1(s)[1], s[4]))
c, s = got['5A 가드']; ok(s[36] == -6 and s[37] == 2 and s[4] == 5, 'FD-2 5A 가드 = −6 · 얼린 5 (%d %d)' % (s[36], s[4]))
c, s = got['5A+ 히트']; ok(s[36] == -8 and P1(s)[1] == 9, 'FD-2 5A+ 히트 = −8 · 발동 9 (%d %d)' % (s[36], P1(s)[1]))
c, s = got['2A+ 다운']; ok(s[36] == 120 and s[37] == 5, 'FD-2 2A+ = 다운 +120 (가만히 있는 더미) (%d %d)' % (s[36], s[37]))
c, s = got['236A 가드']; ok(s[36] == -20 and P1(s)[1] == 11 and P1(s)[2] == -2, 'FD-2 236A 장풍 가드 = −20 · 발동 11 · 지속 «장풍» (%d %d %d)' % (s[36], P1(s)[1], P1(s)[2]))
c, s = got['잡기']; ok(s[36] == 26 and s[37] == 3 and P1(s)[1] == 3, 'FD-2 잡기 = +26 · 발동 3 (%d %d %d)' % (s[36], s[37], P1(s)[1]))
c, s = got['↓B 튕겨내기']; ok(P1(s)[1] == -1 and P1(s)[6:8] == [5, 16] and P1(s)[4] == 52 and 0x45 in c[:52], 'FD-2 ↓B = 판정 없는 동작 52F · 튕겨내기 5F부터 16F (%s)' % P1(s)[1:8])
c, s = got['점프 A']; ok(P1(s)[1:4] == [7, 16, 6] and c[0] == 1, 'FD-2 점프 A = 점프 칸(움직임) 뒤 발동 7 · 지속 16 · 경직 6 (%s)' % P1(s)[1:4])
# 기억: 5A 히트·가드 유불리가 둘 다 남는다(같은 열쇠)
c, s = got['5A 가드']
# ── FD-3 결정성: 상태 되돌리기 후 같은 입력 = 같은 미터 ──
restore(h, base); lg.practice_set(1, 1); approach(h, 24); s0 = snap(h)
def run_once():
    restore(h, s0)
    for f in range(120):
        h.user = bits('A') if f < 2 else 0; h.run(1)
    return fdget()
x1 = run_once(); x2 = run_once()
ok(x1[0] == x2[0] and x1[1][1:] == x2[1][1:], 'FD-3 같은 상태·같은 입력 두 번 → 미터·요약 같음(practice_state 에 FD 포함)')
# ── FD-4 메뉴 «표시» 줄 · practice_set 9 · 설정 저장 ──
vals = []
for v in range(4):
    lg.practice_set(6, [0, 1, 0, 1][v]); lg.practice_set(9, [0, 1, 1, 0][v]); vals.append((ph.pst()[9], ph.pst()[24]))
ok(vals == [(0, 0), (1, 1), (0, 1), (1, 0)], 'FD-4 표시 값 4개 = (숫자, 미터) %s' % vals)
lg.practice_settings_get.restype = C.c_size_t; lg.practice_settings_get.argtypes = [C.c_void_p, C.c_size_t]; lg.practice_settings_set.argtypes = [C.c_void_p, C.c_size_t]
lg.practice_set(9, 1); buf = C.create_string_buffer(256); n = lg.practice_settings_get(buf, 256)
lg.practice_set(9, 0); lg.practice_settings_set(buf, n); on1 = ph.pst()[24]
lg.practice_set(9, 1); lg.practice_settings_set(buf, n - 4); on2 = ph.pst()[24]
ok(n == 44 and on1 == 1 and on2 == 0, 'FD-4 설정 저장 %d바이트(fd 포함) 되돌림 · 옛 40바이트 .prac → 미터 끔 (%d %d)' % (n, on1, on2))
# 미터 끔이어도 추적은 같고(읽기만) 게임 램은 미터 켬/끔과 무관
restore(h, base); lg.practice_set(9, 0); approach(h, 24); s1 = snap(h)
def ramrun(fd):
    restore(h, s1); lg.practice_set(9, fd); rams = []
    for f in range(150):
        h.user = bits('A') if f < 2 else 0; h.run(1); rams.append(p.ram())
    return rams
ok(ramrun(0) == ramrun(1), 'FD-5 미터 켬/끔 150프레임 작업 램 16KB 같음(추적은 읽기만)')
print('FAILS', fails)

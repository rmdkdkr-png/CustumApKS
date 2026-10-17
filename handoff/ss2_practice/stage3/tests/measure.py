"""프레임 데이터 실측 표 — 캐릭터 × 기술 × (헛침·히트·가드) × 위상(0·1) × 거리 두 가지.
교차 확인: 발동 = 순간이동 탐침(헛친 기술 j프레임째 더미를 앞에 두면 닿는 첫 프레임) · 유불리 = VS 경로로 두 사람이 ↓ 를 쥐고 «실제로 앉는 첫 프레임» 차.
사용: python3 measure.py <롬키> <내캐릭 id> <더미 id> [빠르게]"""
import sys, json
from tr import *
import fd_ref
ROM = sys.argv[1]; ME = int(sys.argv[2]); DUM = int(sys.argv[3]); QUICK = len(sys.argv) > 4
h = mk(ROM, os.path.join(T.WORK, 'ms_%s_%d_%d_%s' % (ROM, ME, DUM, MODE))); fight(h, DUM, ME); p = h.p
base = snap(h)
TR = [None]
def trk(hh):
    if TR[0] is not None and p.peek(0x40A7) == 241 and p.peek(0x411A) == 1 and p.peek(0x61D4) == 0: TR[0].step(p.peek)
P2PAD = [0]; VS = [False]
def p1pad(m): return ((m>>4)&1)*1 | ((m>>5)&1)*2 | ((m>>6)&1)*4 | ((m>>7)&1)*8 | (m&1)*0x10 | ((m>>8)&1)*0x20
def post(hh):
    trk(hh)
    if VS[0] and p.peek(0x40A7) == 241 and p.peek(0x411A) == 1 and p.peek(0x5824) == 0:
        p.poke(0x57D4, 1); p.poke(0x5BCB, p.peek(0x5BCB) & ~1); p.poke(0x570D, p1pad(hh.p.mask)); p.poke(0x5715, P2PAD[0])
h.post_hook = post
def setx(pl, x):
    b = 0x5980 + pl*0x200
    for a in (b+0x54, b+0x64): p.poke(a, 0); p.poke(a+1, 0)
    for a in (b+0x56, b+0x66, 0x4E38 + pl*0x40): p.poke(a, x & 0xFF); p.poke(a+1, x >> 8)
MOVES = [
    ('5A',  '약베기',     {0: 'A', 2: ''}, 24),
    ('5A+', '강베기',     {0: 'A', 14: ''}, 24),
    ('2A',  '앉아 약베기', {0: 'D', 4: 'DA', 6: 'D', 10: ''}, 24),
    ('2A+', '앉아 강베기', {0: 'D', 4: 'DA', 18: 'D', 22: ''}, 24),
    ('4B',  '뒤+B',       {0: 'bB', 3: ''}, 24),
    ('236A', '236A',      {0: 'D', 4: 'Df', 8: 'f', 12: 'fA', 16: ''}, 40),
    ('623A', '623A',      {0: 'f', 4: 'D', 8: 'Df', 12: 'DfA', 16: ''}, 30),
    ('214A', '214A',      {0: 'D', 4: 'Db', 8: 'b', 12: 'bA', 16: ''}, 40),
    ('잡기', '→+강베기(붙어서)', {0: 'fA', 16: ''}, 15),
]
def setup(gapv, guard, phase):
    restore(h, base); lg.practice_set(1, guard); lg.practice_set(0, 0)
    g = approach(h, gapv); h.run(phase)
    TR[0] = fd_ref.FrameData(); h.run(2)
    return g
def play(sc, n, hold_d=False):
    last = max(sc)
    started = False
    for f in range(n):
        if f in sc: h.user = bits(rl(h, sc[f])) if sc[f] else 0
        if hold_d and f > last and p.peek(0x59CE) != 0: started = True
        if hold_d and started: h.user = bits('D')
        h.run(1)
    h.user = 0
def whiff(sc):
    setup(150, 0, 0)
    play(sc, 200)
    d = [x for x in TR[0].done if x['p'] == 0]
    return d[0] if d else None, TR[0]
def probe(sc, near=24):
    setup(150, 0, 0); s0 = snap(h)
    TR[0] = None
    R = rec(h, sc, 160)
    c1 = [x['ram'][0x19CE] for x in R]
    st = next((i for i in range(160) if c1[i]), None)
    end = next((i for i in range(st or 0, 160) if c1[i] == 0), 150) if st is not None else None
    if st is None: return None
    x1 = None; hits = []
    for j in range(st - 1, end + 1):
        restore(h, s0); cf = None
        for f in range(j + 6):
            if f in sc: h.user = bits(rl(h, sc[f])) if sc[f] else 0
            h.run(1)
            if f == j:
                x1 = p.peek16(0x59D6); dirn = 1 if p.peek(0x4E54) == 0 else -1
                setx(1, x1 + dirn * near)
            if f > j and cf is None and (p.peek(0x5DC7) or p.peek(0x5C97)): cf = f
        h.user = 0
        if cf is not None: hits.append(cf)
    return (min(hits) - st + 1) if hits else None
def contact_run(sc, gapv, guard, phase):
    g = setup(gapv, guard, phase)
    play(sc, 320)
    ev = TR[0].events
    k = [e for e in ev if e['att'] == 0]
    return g, (k[-1]['adv'], k[-1]['kind']) if k else (None, None), TR[0]
def vs_run(sc, gapv, guard, phase):
    g = setup(gapv, guard, phase); TR[0] = None
    VS[0] = True; P2PAD[0] = 0
    act1 = []; act2 = []; c2 = []; c1 = []
    last = max(sc); started = False; hit_at = None
    for f in range(320):
        if f in sc: h.user = bits(rl(h, sc[f])) if sc[f] else 0
        if f > last and p.peek(0x59CE) != 0: started = True
        if started: h.user = bits('D')
        if hit_at is not None: P2PAD[0] = 0x02
        h.run(1)
        if hit_at is None and (p.peek(0x5DC7) or p.peek(0x5C97) > 0): hit_at = f
        act1.append(p.peek16(0x4E3E)); act2.append(p.peek16(0x4E7E)); c1.append(p.peek(0x59CE)); c2.append(p.peek(0x5BCE))
    VS[0] = False; P2PAD[0] = 0; h.user = 0
    if hit_at is None: return None
    a = next((i for i in range(hit_at, 320) if act1[i] == 0x14 and c1[i] == 0), None)
    b = next((i for i in range(hit_at, 320) if act2[i] == 0x14 and c2[i] == 0), None)
    return (b - a) if a is not None and b is not None else None
SPECIALS = {2: ('236A', '623A'), 9: ('236A', '623A'), 7: ('236A', '214A'), 4: ('236A', '623A'), 11: ('236A', '623A')}
rows = []
for code, name, sc, gapv in MOVES:
    if code in ('236A', '623A', '214A') and code not in SPECIALS.get(ME, ('236A', '623A')): continue
    row = dict(char=NAMES[ME], dummy=NAMES[DUM], move=code, name=name)
    if code != '잡기':
        d, tr = whiff(sc)
        row['whiff'] = None if d is None else {k: d[k] for k in ('startup', 'active', 'recovery', 'total', 'proj')}
        row['whiff_meter'] = tr.meter(0).rstrip()
        row['probe_startup'] = probe(sc)
    for kind, guard in (('hit', 0), ('block', 1)):
        if code == '잡기' and guard: continue
        res = []
        for gp in ((gapv, 0), (gapv, 1)) + (() if QUICK else ((gapv - 6, 0), (gapv - 6, 1))):
            g, (adv, kd), tr = contact_run(sc, gp[0], guard, gp[1])
            dd = [x for x in tr.done if x['p'] == 0 and x['contact']]
            st = dd[0]['startup'] if dd else None
            ca = (dd[0]['contact_at'] - dd[0]['startup'] + 2) if dd and dd[0].get('contact_at') is not None and dd[0]['startup'] else None
            res.append(dict(gap=g, phase=gp[1], adv=adv, kind=fd_ref.KIND_NAME.get(kd, kd), startup=st, contact_nth_active=ca))
        row[kind] = res
        row[kind + '_meter'] = (tr.meter(0).rstrip(), tr.meter(1).rstrip())
        row[kind + '_line'] = tr.line(0)
        row[kind + '_vs'] = [vs_run(sc, gapv, guard, ph) for ph in (0, 1)]
    rows.append(row)
    w = row.get('whiff') or {}
    def advs(k): return '/'.join('%s%s' % (r['adv'], '' if r['kind'] in ('히트', '가드', '잡기') else r['kind']) for r in row.get(k, []))
    print('%-6s %-5s whiff S%s A%s R%s T%s%s probe %s | hit %s (vs %s) | block %s (vs %s)' % (NAMES[ME], code, w.get('startup'), w.get('active'), w.get('recovery'), w.get('total'),
          ' proj' if w.get('proj') else '', row.get('probe_startup'), advs('hit'), row.get('hit_vs'), advs('block'), row.get('block_vs')), flush=True)
json.dump(rows, open(os.path.join(HERE, 'results', 'ms_%s_%d_%d_%s.json' % (ROM, ME, DUM, MODE)), 'w'), ensure_ascii=False, indent=1)

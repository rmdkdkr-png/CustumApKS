"""랭크 경기 체크포인트 이어 하기 — 앱이 경기 중 내려갔다가 다시 열려 체크포인트를 불러온 뒤(EmuActivity.leagueStart 와 같은 순서:
league_hub 새로 → 상태 불러오기 → league_cpu(경기에 적힌 손잡이) → league_arm(…, 올카드 | FROM_CKPT)) 손잡이·바닥이 그대로 먹고 결판이 잡히나.
사용: python3 t_ranked_ckpt.py <롬>"""
import os, sys, ctypes as C
import ph
from ph import PH, hub, to_title
import hosttest as T
ROM = sys.argv[1]; tag = os.path.splitext(os.path.basename(ROM))[0]
lg = ph.lg
lg.league_hub_match.argtypes = [C.c_int] * 10
W = os.environ.get('LEAGUE_WORK', '/tmp/league_work')
fails = 0
def ok(c, what):
    global fails
    print(('PASS ' if c else 'FAIL ') + what, flush=True); fails += (not c)
NONE = (C.c_byte * 15)(*([-1] * 15)); ONE = (C.c_byte * 15)(*([1] * 15))
K = (6, 13, 0x010C, 0x00F3); FLOOR = 8                 # 바닥 > 시작 단계 — 바닥이 실제로 단계를 끌어올려야 통과
h = PH(ROM, os.path.join(W, 'rck_' + tag)); p = h.p
lg.league_hub(1, NONE, ONE); lg.league_hub_ranked(1)
to_title(h); h.press('A', 4, 30)
lg.league_hub_match(9, 1, 2, 5, *K, FLOOR, 1)            # 샬럿 나찰 · 배경 5
f = 0
while f < 600 and not (p.peek(0x40A7) == 240 and p.peek(0x41C0) == 2 and hub()[7] == 0): h.run(1); f += 1
h.run(30); h.press('A', 4, 200); h.press('A', 4, 200); h.run(240)
f = 0
while f < 6000 and not T.status()[3]:
    md, sc = p.peek(0x40A7), p.peek(0x41C0)
    if md == 240 and sc == 6 and f % 60 == 0: h.press('R', 4, 10); h.press('A', 4, 30); f += 48; continue
    if f % 30 == 0 and ((md == 241 and sc == 0 and p.peek(0x411A) == 0) or (md == 240 and sc == 8) or (md != 241 and sc not in (2, 4, 6))): h.press('A', 4); f += 4
    else: h.run(1); f += 1
ok(T.status()[3] == 1 and (T.status()[12] & 0xF8) == (9 << 4 | 1 << 3), '경기 시작 · P2 = 샬럿 나찰')
lv0 = []
for i in range(200):
    h.run(1)
    if p.peek(0x40A7) == 241: lv0.append(p.peek(0x5CF5))
ok(lv0 and min(lv0) >= FLOOR, '새 경기: 시작 단계 %d 이지만 바닥 %d 로 끌어올림 (%d~%d)' % (K[0], FLOOR, min(lv0), max(lv0)))
p.poke(0x5CF5, K[0]); h.p.run(1)                         # 체크포인트 순간엔 바닥 아래 값이 들어 있게(앱이 바닥을 모르는 판에서 저장한 경우까지)
ck = h.serialize()                                       # 앱이 내려가며 남기는 체크포인트
# ── 다시 연 판(코어를 새로 올린 것과 같게: 허브·무장 비움) ──
lg.league_disarm(); lg.league_hub(0, None, None)
p.lib.retro_reset(); h.run(30)
lg.league_hub(1, NONE, ONE); lg.league_hub_ranked(1)
h.unserialize(ck)
lg.league_cpu(*K, FLOOR); lg.league_look(5, 0); lg.league_arm(9, 1, 2, 2, 60, 2 | 8)
lvs = []
for i in range(1500):
    h.run(1)
    if p.peek(0x40A7) == 241: lvs.append(p.peek(0x5CF5))
    if p.peek(0x5A46) < 40: p.poke(0x5A46, 128)
ok((p.peek(0x5814), p.peek(0x5815), p.peek16(0x57E2), p.peek16(0x57E4)) == K, '이어 한 경기: 손잡이 그대로 (%d %d %04X %04X)' % (p.peek(0x5814), p.peek(0x5815), p.peek16(0x57E2), p.peek16(0x57E4)))
ok(lvs and min(lvs) >= FLOOR, '이어 한 경기: 실시간 단계 바닥 %d 아래로 안 감 (%d~%d)' % (FLOOR, min(lvs) if lvs else -1, max(lvs) if lvs else -1))
f = 0; wait = None
while f < 30000 and not T.status()[4]:
    if p.peek(0x40A7) == 241 and p.peek(0x5824) == 0 and p.peek(0x5A46) > 0 and p.peek(0x5C46) > 0:
        if wait is None: wait = f + 120
        if f >= wait: p.poke(0x5A46, 0); wait = None
    if f % 60 == 0 and p.peek(0x40A7) != 241: h.press('A', 2)
    else: h.run(1)
    f += 1
st = T.status()
ok(st[4] == 1 and st[5] & 0x20 and st[7] == 2 and (st[18], st[21], st[19], st[20]) == K, '이어 한 경기 결판 P2 승 · 결판 기록 손잡이 = 요청 (%d %d %04X %04X)' % (st[18], st[21], st[19], st[20]))
print('%s: %s' % (tag, 'ALL PASS' if not fails else '%d FAIL' % fails))

"""견고성 — CPU 더미 + 무작위 P1 입력 N 프레임: 칸 규칙(불변식)·combat_ref 유불리 사건과 같음·예외 없음"""
import sys, random
sys.path.insert(0, '/home/user/CustumApKS/handoff/ss2_practice/stage0/ref')
from tr import *
import fd_ref, combat_ref
ROM = sys.argv[1] if len(sys.argv) > 1 else 'ko'; ME = int(sys.argv[2]) if len(sys.argv) > 2 else 2; DUM = int(sys.argv[3]) if len(sys.argv) > 3 else 9
N = int(sys.argv[4]) if len(sys.argv) > 4 else 6000
h = mk(ROM, os.path.join(T.WORK, 'rb_%s_%d_%d' % (ROM, ME, DUM))); fight(h, DUM, ME); p = h.p
lg.practice_set(0, 1); lg.practice_set(1, 3)        # CPU 더미 · 가드 랜덤
fd = fd_ref.FrameData(); cr = combat_ref.CombatTracker(); F = [0]; bad = []; seqs = [0]
prev_seq = [0]
def post(hh):
    if not (p.peek(0x40A7) == 241 and p.peek(0x411A) == 1 and p.peek(0x61D4) == 0): return
    F[0] += 1
    fd.step(p.peek); cr.step(p.peek, F[0])
    # 불변식: 방금 쌓인 칸
    if fd.seq_on and fd.len and not fd.gap_open:
        for q in (0, 1):
            c = fd.cell[q][(fd.len - 1) % fd_ref.VIEW] & 0x0F
            ctrl = p.peek(0x5980 + q * 0x200 + 0x4E)
            if c == fd_ref.K_IDLE and ctrl != 0: bad.append((F[0], q, 'idle but ctrl %02X' % ctrl))
            if c in (fd_ref.K_HITSTUN, fd_ref.K_BLOCKSTUN, fd_ref.K_DOWN, fd_ref.K_STARTUP, fd_ref.K_ACTIVE, fd_ref.K_RECOVERY, fd_ref.K_ACTION) and ctrl == 0:
                bad.append((F[0], q, 'busy cell %d but ctrl 0' % c))
    if fd.seq_id != prev_seq[0]: seqs[0] += 1; prev_seq[0] = fd.seq_id
h.post_hook = post
random.seed(7)
ACTS = ['', 'f', 'b', 'A', 'DA', 'Uf', 'B', 'bB', 'D', 'fA']
f = 0
while f < N:
    a = random.choice(ACTS); d = random.choice((3, 6, 10, 16, 24))
    h.user = bits(rl(h, a)); h.run(min(d, 3)); h.user = 0; h.run(max(0, d - 3)); f += d
    if random.random() < 0.02: lg.practice_set(7, random.choice((0, 1, 2)))
fd_adv = [(e['f'], e['adv']) for e in fd.events]
cr_adv = [(e['frame'], e['adv_p1']) for e in cr.events if e['type'] == 'advantage']
same = fd_adv == cr_adv
print('frames %d seqs %d fd_events %d cr_events %d same %s bad %d' % (F[0], seqs[0], len(fd_adv), len(cr_adv), same, len(bad)))
if not same:
    for i, (x, y) in enumerate(zip(fd_adv, cr_adv)):
        if x != y: print(' first diff', i, x, y); break
    print(' len', len(fd_adv), len(cr_adv))
for b in bad[:10]: print(' BAD', b)
att = {}
for e in fd.events: att[e['att']] = att.get(e['att'], 0) + 1
kinds = {}
for e in fd.events: kinds[fd_ref.KIND_NAME.get(e['kind'], e['kind'])] = kinds.get(fd_ref.KIND_NAME.get(e['kind'], e['kind']), 0) + 1
print('attackers', att, 'kinds', kinds, 'P2 actions', sum(1 for d in fd.done if d['p'] == 1), 'P1 actions', sum(1 for d in fd.done if d['p'] == 0))

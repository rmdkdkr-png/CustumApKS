"""결정성·판 비교 — 같은 시나리오 묶음을 돌려 미터 칸·요약·유불리 사건을 한 줄 요약(해시)으로.
사용: [FD_MODE=app] [FIXT=…] python3 dt.py <롬키> [내캐릭 더미]"""
import sys, hashlib, json
from tr import *
import fd_ref
ROM = sys.argv[1]; ME = int(sys.argv[2]) if len(sys.argv) > 2 else 2; DUM = int(sys.argv[3]) if len(sys.argv) > 3 else 9
h = mk(ROM, os.path.join(T.WORK, 'dt_%s_%s_%s' % (ROM, MODE, os.environ.get('FIXT', 'rtc')))); fight(h, DUM, ME); p = h.p
base = snap(h)
TR = [None]
def post(hh):
    if TR[0] is not None and p.peek(0x40A7) == 241 and p.peek(0x411A) == 1 and p.peek(0x61D4) == 0: TR[0].step(p.peek)
h.post_hook = post
SC = [
 ('5A whiff', 150, 0, {0: 'A', 2: ''}, 80), ('5A hit', 24, 0, {0: 'A', 2: ''}, 80), ('5A block', 24, 1, {0: 'A', 2: ''}, 80),
 ('5A+ hit', 24, 0, {0: 'A', 14: ''}, 120), ('2A+ hit', 24, 0, {0: 'D', 4: 'DA', 18: 'D', 22: ''}, 260),
 ('236A whiff', 150, 0, {0: 'D', 4: 'Df', 8: 'f', 12: 'fA', 16: ''}, 200), ('236A block', 40, 1, {0: 'D', 4: 'Df', 8: 'f', 12: 'fA', 16: ''}, 200),
 ('throw', 15, 0, {0: 'fA', 16: ''}, 200),
 ('2A>236A', 30, 0, {0: 'D', 6: 'DA', 10: 'D', 22: 'Df', 26: 'f', 30: 'fA', 34: ''}, 300),
]
out = {}
for name, gapv, guard, sc, n in SC:
    restore(h, base); lg.practice_set(1, guard); lg.practice_set(0, 0)
    approach(h, gapv); TR[0] = fd_ref.FrameData(); h.run(2)
    for f in range(n):
        if f in sc: h.user = bits(rl(h, sc[f])) if sc[f] else 0
        h.run(1)
    h.user = 0; h.run(60)
    t = TR[0]
    rec_ = dict(m0=t.meter(0).rstrip(), m1=t.meter(1).rstrip(), done=[{k: v for k, v in d.items() if k != '_act' and k != 'key'} for d in t.done],
                ev=[(e['adv'], e['kind'], e['att']) for e in t.events], line=t.line(0), frozen=t.frozen_n, gap=t.gap_n)
    out[name] = rec_
    print('%-11s %-34s | %s' % (name, rec_['line'], rec_['m0'][:60]))
dig = hashlib.sha1(json.dumps(out, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
print('DIGEST', ROM, MODE, os.environ.get('FIXT', 'rtc'), dig)
json.dump(out, open(os.path.join(HERE, 'results', 'dt_%s_%s_%s_%d.json' % (ROM, MODE, os.environ.get('FIXT', 'rtc'), ME)), 'w'), ensure_ascii=False, indent=1)

"""더미(P2) 쪽 «움직일 수 있음» 확인 — VS 경로(0x57D4=1 · 0x5715 = P2 패드 · 0x570D = P1 패드)로 P2 가 ↓ 를 쥐고 있게"""
from tr import *
h = mk('ko'); fight(h, 9, 2); p = h.p
base = snap(h)
P2PAD = [0]
def p1pad(m): return ((m>>4)&1)*1 | ((m>>5)&1)*2 | ((m>>6)&1)*4 | ((m>>7)&1)*8 | (m&1)*0x10 | ((m>>8)&1)*0x20
def vs(hh):
    if p.peek(0x40A7) == 241 and p.peek(0x411A) == 1 and p.peek(0x5824) == 0:
        p.poke(0x57D4, 1); p.poke(0x5BCB, p.peek(0x5BCB) & ~1); p.poke(0x570D, p1pad(hh.user)); p.poke(0x5715, P2PAD[0])
for guard in (0, 1):
    for phase in (0, 1):
        restore(h, base); lg.practice_set(1, guard); approach(h, 30); h.run(phase)
        h.post_hook = vs; P2PAD[0] = 0; h.run(4)
        R = rec(h, {0: 'A', 2: '', 4: ''}, 6)
        P2PAD[0] = 0x02          # 더미 ↓ 쥠(맞는 동안 계속)
        R += rec(h, {}, 70)
        h.post_hook = None; P2PAD[0] = 0
        c2 = [x['ram'][0x1BCE] for x in R]; a2 = [x['ram'][0x0E7E] | x['ram'][0x0E7F] << 8 for x in R]
        c1 = [x['ram'][0x19CE] for x in R]
        hit = next((i for i in range(len(R)) if c2[i]), None)
        fr2 = next((i for i in range(hit, len(R)) if c2[i] == 0), None) if hit is not None else None
        fr1 = next((i for i in range(hit, len(R)) if c1[i] == 0), None) if hit is not None else None
        cr = next((i for i in range(hit or 0, len(R)) if a2[i] == 0x14), None)
        print('guard %d phase %d: P2 stun from %s ctrl0 at %s crouch at %s | P1 free %s  adv(P1) %s' % (guard, phase, hit, fr2, cr, fr1, None if fr1 is None else fr2 - fr1))

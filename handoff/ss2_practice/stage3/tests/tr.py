"""프레임 기록 — 한 프레임마다 (입력, 두 블록 512B씩, 물체 0·1 각 64B, 전역 몇 개)"""
from fdh import *
def rl(h, seq):
    """f = 앞 · b = 뒤 (P1 이 보는 쪽 기준) · 나머지 U D L R A B 그대로"""
    face_left = h.p.peek(0x4E54) == 1
    F, K = ('L', 'R') if face_left else ('R', 'L')
    return seq.replace('f', F).replace('b', K) if seq else seq
G = [0x5DC7, 0x61D4, 0x41C2, 0x411A, 0x40A7]
def rec(h, script, n):
    """script: {프레임: 버튼 문자열(F/B 상대) 또는 ''} — 그 프레임부터 쥠. 돌려줌: 기록 목록"""
    out = []
    p = h.p
    for f in range(n):
        if f in script: h.user = bits(rl(h, script[f])) if script[f] else 0
        h.run(1)
        r = p.ram()
        out.append(dict(f=f, inp=h.p.mask, b=(r[0x1980:0x1B80], r[0x1B80:0x1D80]), o=(r[0x0E30:0x0E70], r[0x0E70:0x0EB0]),
                        g={a: r[a-0x4000] for a in G}, ram=r))
    h.user = 0
    return out
def gap(h): return abs(h.p.peek16(0x5BD6) - h.p.peek16(0x59D6))
def approach(h, g, settle=20):
    lg.practice_set(7, 0); h.run(40)
    k = 0
    while gap(h) > g and k < 400:
        h.hold(rl(h, 'f')); h.run(1); k += 1
    h.user = 0; h.run(settle)
    return gap(h)

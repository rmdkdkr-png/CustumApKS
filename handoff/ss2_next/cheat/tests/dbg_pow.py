"""0x57D8(P1 공격 배율)이 언제 누가 바꾸나 — 카드 받기 + 공격력 3배, 치트 없음 대조(인자 off)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
mode = sys.argv[2] if len(sys.argv) > 2 else 'on'
sys.argv = ['t_cheat.py', sys.argv[1], '__none__']
exec(open(os.path.join(HERE, 't_cheat.py'), encoding='utf-8').read().split('# ════ C-1')[0])
h = new_h('dbgpow_' + mode); p = h.p
cset(cards=1, pow=3 if mode == 'on' else 0); to_menu(h); to_char(h)
log = []; prev = [None]
def pre(hh):
    k = (p.peek16(0x57D8), p.peek(0x40A7), p.peek(0x41C0), p.peek(0x411A))
    if k[0] != (prev[0] or (None,))[0]: log.append(('pre ', hh.frames) + k)
    prev[0] = k
def post(hh):
    lg.cheat_tick(hh.p._ramp, hh.p._rams, 0 if hh.passive else hh.user)
    k = (p.peek16(0x57D8), p.peek(0x40A7), p.peek(0x41C0), p.peek(0x411A))
    if k[0] != prev[0][0]: log.append(('post', hh.frames) + k + (cst()[8], cst()[9]))
    prev[0] = k
h.pre_hook = pre; h.post_hook = post
had, f = pick_and_go(h, want_card=True)
lg.cheat_set(3, 2)    # 상대 한 방 — 판을 빨리 넘긴다
def bot(h, f):
    g = abs(p.peek16(0x4E78) - p.peek16(0x4E38)); fw = 'L' if p.peek(0x4E54) == 1 else 'R'
    return bits(fw) if g > 40 else (bits('A') if f % 40 < 4 else 0)
ff = 0
while ff < 9000 and p.peek(0x57FE) < 2:
    lvv = live(h); h.user = bot(h, ff) if lvv else (bits('A') if ff % 30 < 3 else 0); h.run(1); ff += 1
h.user = 0; print('장', p.peek(0x57FE), ff)
for l in log: print(l[0], l[1], '57D8 %04X MODE %d SCR %d F %d' % l[2:6], ('last %X base %X' % (l[6] & 0xffff, l[7]) if len(l) > 6 else ''))

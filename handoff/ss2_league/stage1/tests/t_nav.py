import sys, hosttest as T
ROM=sys.argv[1]; mode=sys.argv[2]   # card: 카드 하나 고르기 / nocard: 안받음
h=T.Harness(ROM, T.work('w_nav_')+mode)
T.lg.league_arm(11, 0, 1, 2, 60, 2|4)        # 올카드 + 메뉴 자동 진입
log=[]; prev=None; seen6=False
for f in range(600):
    h.run(1); p=h.p
    cur=(p.peek(0x40A7), p.peek(0x41C0))
    if cur!=prev: log.append((f,cur)); prev=cur
    if T.C.c_int.in_dll(T.lg,'league_ovr_on').value==0 and f>70: break
print('autonav done at', f, 'mode/scr', cur, 'trace', log[:8])
h.p.shot(T.work('nav_csel.png'))
# 사용자: 캐릭터 선택 화면에서 오른쪽 두 번(모로즈미→하오마루?) 후 A
h.press('R',4,20); h.press('A',4,200)        # 캐릭터 확정
h.press('A',4,200)                            # 유파(수라)
st=T.status()
print('after style: scr', h.p.peek(0x41C0), 'own0', h.p.peek(0x63BA), 'started', st[3])
for i in range(400):
    h.run(1)
    if h.p.peek(0x41C0)==6: seen6=True
print('card screen seen', seen6)
h.p.shot(T.work('nav_card.png'))
if seen6:
    if mode=='card':
        for b in "w240,A,w200,A,w120,A,w60,A,w200,A,w120,R,A,w60,A,w60".split(','):
            if b.startswith('w'): h.run(int(b[1:]))
            else: h.press(b, 8, 60)
        print('after pick: scr', h.p.peek(0x41C0), 'cards %02X %02X' % (h.p.peek(0x57DC), h.p.peek(0x57DD)))
    else: h.run(240); h.press('A',4,240); h.press('R',4,30); h.press('A',4,200)
f=0; wait=None
while f<30000:
    st=T.status()
    if st[4]: break
    p=h.p
    if p.peek(0x40A7)==241 and p.peek(0x5824)==0 and p.peek(0x5A46)>0 and p.peek(0x5C46)>0:
        if wait is None: wait=f+240
        if f>=wait: p.poke(0x5C46,0); wait=None
    if f%60==0 and p.peek(0x40A7)!=241: h.press('A',2)
    else: h.run(1)
    f+=1
st=T.status()
print('status', st)
h.p.shot(T.work('nav_end_')+mode+'.png'); print('start_frame', st[13], 'p2@start %02X' % st[12], 'p1 %02X' % st[10], 'cards', '%02X %02X' % (h.p.peek(0x57DC), h.p.peek(0x57DD)), 'mult %04X' % h.p.peek16(0x57D8), 'cpu cards %02X %02X' % (h.p.peek(0x57E6), h.p.peek(0x57E7)))

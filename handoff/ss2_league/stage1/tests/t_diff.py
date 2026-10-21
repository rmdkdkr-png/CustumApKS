import sys, hosttest as T
ROM=sys.argv[1]; diff=int(sys.argv[2])
h=T.Harness(ROM, T.work('w_diff%d') % diff)
T.lg.league_arm(11, 0, diff, 2, 60, 2|4)
for f in range(200):
    h.run(1)
    if T.C.c_int.in_dll(T.lg,'league_ovr_on').value==0 and f>70: break
h.press('A',4,200); h.press('A',4,200)
for i in range(400):
    h.run(1)
    if h.p.peek(0x41C0)==6: break
h.run(240); h.press('A',4,240); h.press('R',4,30); h.press('A',4,200)
# 전투 시작까지 대사 넘기기, P1 은 가만히
f=0
while f<20000:
    st=T.status()
    if st[3]: break
    if f%60==0 and h.p.peek(0x40A7)!=241: h.press('A',2)
    else: h.run(1)
    f+=1
p=h.p
print('diff', diff, 'start@', st[13], 'opt636A', p.peek(0x636A), 'need', p.peek(0x5813), 'time', p.peek(0x5812), 'cpu_mult atk %04X def %04X' % (p.peek16(0x57E2), p.peek16(0x57E4)), '5814', p.peek(0x5814))
hp=[]; 
for k in range(6):
    h.run(300); hp.append(p.peek(0x5A46))
    if p.peek(0x5824): break
print('  P1 HP every 300f (idle):', hp, 'res', p.peek(0x5824))

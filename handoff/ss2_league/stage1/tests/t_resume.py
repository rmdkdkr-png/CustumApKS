import sys, os, hosttest as T
ROM=sys.argv[1]; phase=sys.argv[2]; CK=T.work('ckpt_test.state')
h=T.Harness(ROM, T.work('w_res_')+phase)
def fight(target_rounds, who_list, stop_after=None):
    f=0; wait=None; k=0
    while f<30000:
        st=T.status()
        if st[4]: return st
        p=h.p
        if stop_after is not None and k>=stop_after and p.peek(0x40A7)==241 and p.peek(0x5824)==0 and p.peek(0x5C46)>0:
            return None
        if p.peek(0x40A7)==241 and p.peek(0x5824)==0 and p.peek(0x5A46)>0 and p.peek(0x5C46)>0:
            if wait is None: wait=f+240
            if f>=wait:
                (p.poke(0x5C46,0) if who_list[min(k,len(who_list)-1)]=='w' else p.poke(0x5A46,0)); k+=1; wait=None
        if f%60==0 and p.peek(0x40A7)!=241: h.press('A',2)
        else: h.run(1)
        f+=1
    return T.status()
if phase=='a':
    T.lg.league_arm(4, 1, 1, 2, 60, 0)    # 나코루루 나찰
    h.run(420); h.press('A',4,120); h.press('A',4,180); h.press('A',4,180); h.press('A',4,180)
    r=fight(3, ['l'], stop_after=1)        # 첫 라운드 지고, 둘째 라운드 시작에서 멈춤
    h.run(300)
    print('before ckpt: w1 w2', h.p.peek(0x5821), h.p.peek(0x5822), 'status', T.status()[:5])
    h.p.save(CK)                           # 앱이 내려가는 순간의 체크포인트
elif phase=='c':                           # 결판까지 간 뒤(정산 전) 체크포인트 — 앱이 정산 직전에 내려간 경우
    T.lg.league_arm(4, 1, 1, 2, 60, 2|4)
    h.run(420); h.press('A',4,180); h.press('A',4,180)
    for i in range(400):
        h.run(1)
        if h.p.peek(0x41C0)==6: break
    h.run(240); h.press('A',4,240); h.press('R',4,30); h.press('A',4,200)
    st=fight(3, ['l','l'])
    h.run(30)
    print('decided before ckpt: winner', 'P1' if st[5]&0x40 else 'P2', 'score %d-%d' % (st[6], st[7]), 'bit7', h.p.peek(0x5824)>>7)
    h.p.save(CK+'.post')
elif phase=='d':                           # 정산 전 체크포인트로 재개 → 첫 틱에 같은 결과
    h.p.load(CK+'.post')
    T.lg.league_arm(4, 1, 1, 2, 60, 2|8)   # 올카드 + 체크포인트 재개
    h.run(1); st=T.status()
    print('resume-after-decide: done', st[4], 'winner', 'P1' if st[5]&0x40 else 'P2' if st[5]&0x20 else 'D', 'score %d-%d' % (st[6], st[7]), 'p2 %02X' % st[11], 'need', st[9], 'time', st[17])
    h.run(3000); print('again?', T.status()[4], T.status()[14]==st[14])
    # 대조: 옛 방식(FROM_CKPT 없음)이면 첫 틱에 안 잡힘
    h2=T.Harness(ROM, T.work('w_res_d2')); h2.p.load(CK+'.post')
    T.lg.league_arm(4, 1, 1, 2, 60, 2); h2.run(1); print('without FROM_CKPT: done', T.status()[4])
else:
    h.p.load(CK)                           # 새 프로세스 = 앱 재시작 → 재개
    T.lg.league_arm(4, 1, 1, 2, 60, 2|8)
    st=fight(3, ['w','w'])
    print('resumed result', st, 'winner', 'P1' if st[5]&0x40 else 'P2' if st[5]&0x20 else 'D', 'score %d-%d' % (st[6], st[7]), 'p2 %02X' % st[11])
    h.run(2000); print('again?', T.status()[4], T.status()[14]==st[14])

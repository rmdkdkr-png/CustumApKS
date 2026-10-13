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
else:
    h.p.load(CK)                           # 새 프로세스 = 앱 재시작 → 재개
    T.lg.league_arm(4, 1, 1, 2, 60, 0)
    st=fight(3, ['w','w'])
    print('resumed result', st, 'winner', 'P1' if st[5]&0x40 else 'P2' if st[5]&0x20 else 'D', 'score %d-%d' % (st[6], st[7]), 'p2 %02X' % st[11])
    h.run(2000); print('again?', T.status()[4], T.status()[14]==st[14])

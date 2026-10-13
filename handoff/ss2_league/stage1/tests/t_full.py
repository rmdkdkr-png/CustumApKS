import sys, hosttest as T
ROM=sys.argv[1]; who=sys.argv[2]  # P1 이 이기게 'w' / 지게 'l' / 무승부 라운드 섞기 'd'
h=T.Harness(ROM, T.work('w_')+who)
T.lg.league_arm(11, 0, 1, 2, 60, 0)      # (자동 진입 없이 직접 밟는 경로) 칼끝노인 = 우쿄(11) 修羅, ふつう, 포인트 2, 60초
h.run(420); h.press('A',4,120)           # 타이틀 메뉴
h.press('A',4,180)                       # 1P PLAY → 캐릭터 고르기
h.press('A',4,180)                       # 캐릭터 확정
h.press('A',4,180)                       # 유파 확정
f=0; wait=None; rounds=0
while f<30000:
    st=T.status()
    if st[4]: break
    p=h.p
    if p.peek(0x40A7)==241 and p.peek(0x5824)==0 and p.peek(0x5A46)>0 and p.peek(0x5C46)>0:
        if wait is None: wait=f+240
        if f>=wait:
            if who=='w': p.poke(0x5C46,0)
            elif who=='l': p.poke(0x5A46,0)
            else:
                if rounds==0: p.poke(0x5A46,0); p.poke(0x5C46,0)   # 첫 라운드 더블 KO
                else: p.poke(0x5C46,0)
            rounds+=1; wait=None
    if f%60==0 and p.peek(0x40A7)!=241: h.press('A',2)
    else: h.run(1)
    f+=1
st=T.status()
print('status', st)
print('p1blk %02X p2blk %02X first %02X  winner %s  score %d-%d need %d' % (st[10], st[11], st[12],
      'P1' if st[5]&0x40 else 'P2' if st[5]&0x20 else 'DRAW', st[6], st[7], st[9]))
h.p.shot(T.work('end_')+who+'.png')
# 결판 뒤 더 돌려도 다시 안 잡히는지
h.run(3000); st2=T.status(); print('after 3000: done', st2[4], 'done_frame same', st2[14]==st[14])

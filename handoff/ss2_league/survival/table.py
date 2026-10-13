# 무한 대전 상대 뽑기 표(롬 0x22F952, 32칸) 읽기 — 사용: python3 table.py 롬파일...
import sys, hashlib
N=['카즈키','소게츠','하오마루','겐쥬로','나코루루','리무루루','한조','갈포드','아수라','샬럿','모로즈미','우쿄','주베이','시키','유가','15']
for f in sys.argv[1:]:
    d=open(f,'rb').read(); t=d[0x2F952:0x2F972]
    print(hashlib.md5(d).hexdigest()[:8], f, ' '.join('%02X'%b for b in t))
    for i,b in enumerate(t):
        c,s=i//2,i%2
        if c<15: print('  %2d %-5s %s : %s' % (c,N[c],'나찰' if s else '수라', '막힘(FF)' if b==0xFF else '%02X' % b))

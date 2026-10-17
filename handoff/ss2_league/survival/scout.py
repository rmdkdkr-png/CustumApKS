import sys, ss2probe
import os
# 무한 대전(SURVIVAL) 첫 판 직전 상태 — 타이틀에서 무한 대전 → 캐릭·유파 고르기 직전에 저장한 것
ST=os.environ.get('SV_STATE','SV_pre.st')
WORK=os.environ.get('SV_WORK','/tmp/sv_work')
ROM=os.environ.get('SS2_ROM','/home/user/rom/ss2_h1.ngc')
CORE=os.environ.get('SS2_CORE','/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so')
p=ss2probe.Probe(CORE,ROM,WORK)
p.load(ST)
N=['카즈키','소게츠','하오마루','겐쥬로','나코루루','리무루루','한조','갈포드','아수라','샬럿','모로즈미','우쿄','주베이','시키','유가','15']
seen=[]; f=0; prev_rs=1; target=int(sys.argv[1]) if len(sys.argv)>1 else 40
while len(seen)<target and f<400000:
    rs = p.peek(0x40A7)==241 and p.peek(0x411A)==1 and p.peek(0x5824)==0
    if rs and not prev_rs:
        o,s,b2=p.peek(0x57DF),p.peek(0x57E0),p.peek(0x5D51)
        p.poke(0x5A46,128); hp0=128; hits=0; prev=hp0
        for k in range(600):
            p.run(1); f+=1
            h=p.peek(0x5A46)
            if h<prev: hits+=1
            prev=h
        dmg=hp0-p.peek(0x5A46)
        seen.append((o,s,b2,dmg,hits,p.peek(0x580B),p.peek(0x5814),p.peek(0x5CF5),p.peek16(0x57E2)))
        print('#%2d streak %2d opp %s%s (57DF=%d 57E0=%d B2=%02X) idle600 dmg %3d hits %2d | 5814=%d 5CF5=%d 57E2=%04X' % (len(seen),p.peek(0x580B),N[o&15],'수나'[s&1] if s<2 else '?',o,s,b2,dmg,hits,p.peek(0x5814),p.peek(0x5CF5),p.peek16(0x57E2)), flush=True)
        p.poke(0x5A46,128); p.poke(0x5C46,0)
    prev_rs=rs
    if p.peek(0x40A7)!=241 and f%50==0: p.press('A',2)
    else: p.run(1)
    f+=1

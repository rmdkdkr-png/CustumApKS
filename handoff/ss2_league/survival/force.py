import sys, ss2probe
import os
# 무한 대전(SURVIVAL) 첫 판 직전 상태 — 타이틀에서 무한 대전 → 캐릭·유파 고르기 직전에 저장한 것
ST=os.environ.get('SV_STATE','SV_pre.st')
WORK=os.environ.get('SV_WORK','/tmp/sv_work')
ROM=os.environ.get('SS2_ROM','/home/user/rom/ss2_h1.ngc')
CORE=os.environ.get('SS2_CORE','/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so')
rom=sys.argv[1] if len(sys.argv)>1 else ROM
opps=[(1,0),(4,1),(5,1),(6,1),(10,1),(12,1),(1,1),(4,0),(5,0),(6,0),(10,0),(12,0),(14,0),(14,1)]
p=ss2probe.Probe(CORE,rom,WORK)
for oc,os_ in opps:
  p.load(ST)
  ok=False
  for f in range(3000):
    if p.peek(0x40A7)!=241: p.poke(0x57DF,oc); p.poke(0x57E0,os_)
    if p.peek(0x40A7)!=241 and f%50==0: p.press('A',2)
    else: p.run(1)
    if p.peek(0x40A7)==241 and p.peek(0x411A)==1 and p.peek(0x5824)==0: ok=True; break
  b2=p.peek(0x5D51); st=p.peek(0x580B)
  # idle 2400f: P1 does nothing, refill P1 HP
  hp0=p.peek(0x5A46); prev=hp0; dmg=0; hits=0
  for f in range(2400):
    p.mask=0; p.run(1); h=p.peek(0x5A46)
    if h<prev: hits+=1; dmg+=prev-h
    if h<64: p.poke(0x5A46,128); h=128
    prev=h
    if p.peek(0x5824): break
  idle=(dmg,hits)
  # attack bot from the same start
  p.load(ST)
  for f in range(3000):
    if p.peek(0x40A7)!=241: p.poke(0x57DF,oc); p.poke(0x57E0,os_)
    if p.peek(0x40A7)!=241 and f%50==0: p.press('A',2)
    else: p.run(1)
    if p.peek(0x40A7)==241 and p.peek(0x411A)==1 and p.peek(0x5824)==0: break
  hp1=p.peek(0x5A46); hp2=p.peek(0x5C46); h1=h2=0; pa,pb=hp1,hp2
  for f in range(2400):
    p.mask=0; p.hold('R')
    if f%24<4: p.hold('A')
    p.run(1); a=p.peek(0x5A46); b=p.peek(0x5C46)
    if a<pa: h1+=1
    if b<pb: h2+=1
    pa,pb=a,b
    if p.peek(0x5824): break
  print('SURV opp %2d/%d B2=%02X streak %d start=%s | idle2400 dmg %3d hits %2d | bot: CPU->P1 hits %2d dmg %3d, P1->CPU hits %2d, res %02X' % (oc,os_,b2,st,ok,idle[0],idle[1],h1,hp1-p.peek(0x5A46),h2,p.peek(0x5824)), flush=True)

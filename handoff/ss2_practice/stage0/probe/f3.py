import sys, os
sys.path.insert(0,'/home/user/CustumApKS/handoff/ss2_league'); import ss2probe
CORE='/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
ROM='/home/user/rom/ss2.ngc'
ST='/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice/kit/fight_jp.st'
HERE=os.path.dirname(os.path.abspath(__file__))
p=ss2probe.Probe(CORE, ROM, os.path.join(HERE,'wd'))
p.load(ST); p.release()
r0=p.ram()
for f in range(400):
    p.run(1)
    if p.peek(0x5A46)<128: break
p.run(40); r1=p.ram()
p.poke(0x5A46,128); p.run(60); r2=p.ram()
p.shot(os.path.join(HERE,'hp_after60.png'))
# bytes: r0==128-ish start, r1 changed, r2 still == r1 (not caught up)
c=[(0x4000+i,r0[i],r1[i],r2[i]) for i in range(16384) if r0[i]!=r1[i] and r1[i]==r2[i] and r0[i]==r2[i]-0 or (r0[i]==128 and r1[i]==117)]
print('HP-like (128->117):', [(hex(a),x,y,z) for a,x,y,z in c if x==128 and y==117])
d=[(hex(0x4000+i),r0[i],r1[i],r2[i]) for i in range(0x1A00,0x1B00) if r0[i]!=r1[i]]
print('P1 block 5A00-5AFF changed on hit:', d)

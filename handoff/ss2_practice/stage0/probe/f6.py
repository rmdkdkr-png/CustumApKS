import sys, os
sys.path.insert(0,'/home/user/CustumApKS/handoff/ss2_league'); import ss2probe
CORE='/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
ROM='/home/user/rom/ss2.ngc'
ST='/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice/kit/fight_jp.st'
HERE=os.path.dirname(os.path.abspath(__file__))
p=ss2probe.Probe(CORE, ROM, os.path.join(HERE,'wd'))
def w16(a,v): p.poke(a,v&255); p.poke(a+1,(v>>8)&255)
for tag,(x1,x2,cam) in {'cornerL':(60,110,None),'cornerL_cam':(60,110,50),'cornerR':(240,283,None)}.items():
    p.load(ST); p.release()
    for f in range(40):
        p.poke(0x5C6A,0)
        if f==0:
            for a in (0x59D6,0x59E6): w16(a,x1)
            for a in (0x5BD6,0x5BE6): w16(a,x2)
            if cam is not None: p.poke(0x576D,cam)
        p.run(1)
        if f in (1,39): print(tag,f,'x',p.peek16(0x4E38),p.peek16(0x4E78),'master',p.peek16(0x59D6),p.peek16(0x5BD6),'cam',p.peek(0x576D), 'facing', p.peek(0x4E54), p.peek(0x4E94))
    p.shot(os.path.join(HERE,'%s.png'%tag))

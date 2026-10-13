import sys, os
sys.path.insert(0,'/home/user/CustumApKS/handoff/ss2_league'); import ss2probe
CORE='/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
ROM='/home/user/rom/ss2.ngc'
ST='/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice/kit/fight_jp.st'
HERE=os.path.dirname(os.path.abspath(__file__))
p=ss2probe.Probe(CORE, ROM, os.path.join(HERE,'wd'))
for tag,btn,hold in (('A',('A',),4),('B',('B',),4),('Bhold',('B',),14),('AB',('A','B'),4),('O',('O',),4)):
    p.load(ST); p.release()
    seq=[]
    for f in range(50):
        p.poke(0x5C6A,0)
        if f==2: p.hold(*btn)
        if f==2+hold: p.release()
        p.run(1); seq.append(p.peek16(0x4E3E))
    ch=[]; prev=None
    for i,a in enumerate(seq):
        if a!=prev: ch.append('%d:%X'%(i,a)); prev=a
    print(tag, ' '.join(ch), 'mode', p.peek(0x40A7))
    if tag=='AB': p.shot(os.path.join(HERE,'ab.png'))

# Quick feasibility: can P2 be made a passive / pad-driven dummy? (sibling agent explores this in depth)
import sys, os
sys.path.insert(0,'/home/user/CustumApKS/handoff/ss2_league'); import ss2probe
CORE='/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
ROM='/home/user/rom/ss2.ngc'
ST='/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice/kit/fight_jp.st'
HERE=os.path.dirname(os.path.abspath(__file__))
p=ss2probe.Probe(CORE, ROM, os.path.join(HERE,'wd'))
def run(tag, pre=(), post=(), n=600):
    p.load(ST); p.release()
    acts=set(); x0=p.peek16(0x4E78)
    for f in range(n):
        for a,v in pre: p.poke(a,v)
        p.run(1)
        for a,v in post: p.poke(a,v)
        acts.add(p.peek16(0x4E7E))
    print(tag, 'P1HP', p.peek(0x5A46), 'P2HP', p.peek(0x5C46), 'P2x', x0, '->', p.peek16(0x4E78), 'acts', sorted(hex(a) for a in acts)[:12], '5C6A', p.peek(0x5C6A))
    p.shot(os.path.join(HERE, 'p2_%s.png'%tag))
run('cpu')
run('flag0', pre=[(0x5C6A,0)])
run('flag0_padL', pre=[(0x5C6A,0)], post=[(0x5C6B,0x04)])
run('flag0_padR', pre=[(0x5C6A,0)], post=[(0x5C6B,0x08)])

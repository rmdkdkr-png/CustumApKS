import sys, os
sys.path.insert(0,'/home/user/CustumApKS/handoff/ss2_league'); import ss2probe
CORE='/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
ROM='/home/user/rom/ss2.ngc'
ST='/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice/kit/fight_jp.st'
HERE=os.path.dirname(os.path.abspath(__file__))
p=ss2probe.Probe(CORE, ROM, os.path.join(HERE,'wd'))
def fresh(): p.load(ST); p.release()
def r(): return (p.peek(0x5A46),p.peek(0x5A47),p.peek16(0x5A48))
# (a) direct poke rage + timer
fresh(); p.poke(0x5A47,0x30); p.poke(0x5A48,0x00); p.poke(0x5A49,0x30)
out=[]
for f in range(40): p.run(1); out.append(r())
print('direct', out[0], out[10], out[39])
p.shot(os.path.join(HERE,'rage_direct.png'))
# (b) organic route
fresh(); p.poke(0x5A47,0x2F)
for f in range(300):
    p.run(1)
    if p.peek16(0x5A48): break
print('organic at', f, r()); p.run(60); print('organic +60', r(), hex(p.peek16(0x4E3E)))
p.shot(os.path.join(HERE,'rage_organic.png'))
# (c) HP refill after being hit
fresh()
for f in range(400):
    p.run(1)
    if p.peek(0x5A46)<128: break
p.run(40); print('hit at', f, 'HP now', p.peek(0x5A46)); p.shot(os.path.join(HERE,'hp_before.png'))
p.poke(0x5A46,128); p.run(2); print('after poke', p.peek(0x5A46)); p.shot(os.path.join(HERE,'hp_after.png'))
# (d) P2 HP to 1 then stays? and timer freeze
fresh(); p.poke16=None
p.poke(0x582F,0xFF); p.poke(0x5830,0xFF); p.run(30); print('timer', p.peek16(0x582F)); p.shot(os.path.join(HERE,'timer_inf.png'))

# Position reset feasibility: stage bounds, camera follow after X poke.
import sys, os
sys.path.insert(0,'/home/user/CustumApKS/handoff/ss2_league'); import ss2probe
CORE='/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
ROM='/home/user/rom/ss2.ngc'
ST='/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice/kit/fight_jp.st'
HERE=os.path.dirname(os.path.abspath(__file__))
p=ss2probe.Probe(CORE, ROM, os.path.join(HERE,'wd'))
def fresh(): p.load(ST); p.release()
CPUOFF=(0x5C6A,0)
# 1) walk P1 to left wall with CPU off; log X and camera candidates
fresh(); r0=p.ram(); p.hold('L')
xs=[]
logs=[]
for f in range(360):
    p.poke(*CPUOFF); p.run(1); xs.append(p.peek16(0x4E38)); logs.append(p.ram())
p.release()
print('P1 x walk-left', xs[0], xs[60], xs[120], xs[240], xs[359], 'P2x', p.peek16(0x4E78))
# camera candidates: 16-bit values that decreased over the walk and then went constant
cands=[]
for i in range(0,16383):
    v=[l[i]|(l[i+1]<<8) for l in logs]
    if v[0]!=v[-1] and all(b<=a for a,b in zip(v,v[1:])) and len(set(v))>10: cands.append((hex(0x4000+i), v[0], v[180], v[-1]))
print('decreasing 16-bit:', cands[:20])
p.shot(os.path.join(HERE,'leftwall.png'))
# 2) walk right to find right bound
fresh(); p.hold('R')
for f in range(500): p.poke(*CPUOFF); p.run(1)
p.release(); print('P1 x walk-right end', p.peek16(0x4E38), 'P2x', p.peek16(0x4E78))
# 3) X poke from fresh: place P1 near left, P2 a bit right; does camera follow?
for tag,(x1,x2) in {'pokeL':(40,100),'pokeC':(150,190)}.items():
    fresh()
    for f in range(60):
        p.poke(*CPUOFF)
        if f<2: p.poke(0x4E38,x1&255); p.poke(0x4E39,x1>>8); p.poke(0x4E78,x2&255); p.poke(0x4E79,x2>>8)
        p.run(1)
    print(tag, 'x after 60', p.peek16(0x4E38), p.peek16(0x4E78), '59D6', p.peek16(0x59D6), p.peek16(0x5BD6))
    p.shot(os.path.join(HERE,'%s.png'%tag))

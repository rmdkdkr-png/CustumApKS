import sys, os
sys.path.insert(0,'/home/user/CustumApKS/handoff/ss2_league'); import ss2probe
CORE='/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
ROM='/home/user/rom/ss2.ngc'
ST='/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/practice/kit/fight_jp.st'
HERE=os.path.dirname(os.path.abspath(__file__))
p=ss2probe.Probe(CORE, ROM, os.path.join(HERE,'wd'))
def fresh(): p.load(ST); p.release()
# C: X candidates in fight struct
fresh(); a=p.peek(0x4E30,0x60)
p.hold('R'); p.run(20); p.release(); b=p.peek(0x4E30,0x60)
print('struct 4E30..4E8F before/after R20')
for i in range(0,0x60,16):
    print('%04X'%(0x4E30+i), ' '.join('%02x'%x for x in a[i:i+16]), '|', ' '.join('%02x'%x for x in b[i:i+16]))
print('59D6/5BD6', p.peek(0x59D6), p.peek(0x5BD6))
# A: HP on hit: walk in, B
fresh()
p.hold('R')
for f in range(200):
    p.run(1)
    if abs(p.peek16(0x4E38)-p.peek16(0x4E78))<40: break
p.release(); print('closed in', f, 'x', p.peek16(0x4E38), p.peek16(0x4E78))
p.hold('B'); 
seq=[]
for f in range(70):
    if f==3: p.release()
    p.run(1); seq.append((f,p.peek(0x5C46),p.peek(0x5C47),p.peek16(0x4E7E),p.peek(0x5DC7)))
prev=None
for s in seq:
    if s[1:]!=prev: print('A', s); prev=s[1:]
# B: rage 0x2F then get hit
fresh(); p.poke(0x5A47,0x2F)
prev=None
for f in range(900):
    p.run(1)
    r=(p.peek(0x5A46),p.peek(0x5A47),p.peek(0x5A48),p.peek(0x5A49))
    if r!=prev: print('B', f, r, hex(p.peek16(0x4E3E))); prev=r
    if f>0 and r[1]==0 and prev and f>50 and r[2]==0 and r[3]==0 and 'seen' in globals(): break
    if r[2] or r[3]: globals()['seen']=1
p.shot(os.path.join(HERE,'rage.png'))

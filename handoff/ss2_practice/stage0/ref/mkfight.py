"""연습 모드 조사용: 1인 대전 첫 판이 시작된 순간(라운드 1, 타이머가 막 돌기 시작) 상태를 만든다.
사용: python3 mkfight.py <롬> <출력.st> [캐릭터 오른쪽 이동 수]"""
import sys, os
sys.path.insert(0, '/home/user/CustumApKS/handoff/ss2_league')
import ss2probe
CORE = '/home/user/ss2-sp-core/cores/mednafen_ngp_libretro.linux-x86_64.so'
rom, out = sys.argv[1], sys.argv[2]; nr = int(sys.argv[3]) if len(sys.argv) > 3 else 0
wd = os.path.splitext(out)[0] + '_wd'; os.makedirs(wd, exist_ok=True)
p = ss2probe.Probe(CORE, rom, wd)
p.run(420); p.press('A', 4, 150)                 # 타이틀 → 메뉴(커서 0 = 1인 대전)
p.press('A', 4, 240)                             # 캐릭터 고르기
for _ in range(nr): p.press('R', 4, 30)
p.press('A', 4, 200); p.press('A', 4, 200)       # 캐릭터 · 유파(수라)
f = 0
while f < 8000:
    if p.peek(0x40A7) == 241 and p.peek(0x5A46) == 128 and p.peek(0x5C46) == 128 and p.peek(0x5824) == 0 and p.peek16(0x582F) not in (0, 0xFFFF):
        t0 = p.peek16(0x582F); p.run(1)
        if p.peek16(0x582F) != t0: break         # 타이머가 도는 중 = 조작 가능
        continue
    if f % 60 == 0 and p.peek(0x40A7) != 241:
        if p.peek(0x40A7) == 240 and p.peek(0x41C0) == 6: p.press('R', 4, 30)   # 카드 화면: 안 받음
        p.press('A', 2)
    else: p.run(1)
    f += 1
p.save(out); p.shot(os.path.splitext(out)[0] + '.png')
print('frames', f, 'P1', hex(p.peek(0x5B51)), 'P2', hex(p.peek(0x5D51)), 'timer', p.peek16(0x582F), 'mode', p.peek(0x40A7))

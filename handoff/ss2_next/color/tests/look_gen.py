#!/usr/bin/env python3
"""컬러 표 생성기 — look_tab.h(프리셋 16개 × 캐릭터 14명+쿠로코 × 검질 2 · 겹침 표 · 이름)
사용: python3 look_gen.py <앱>/app/src/main/cpp
표는 여기서 한 번 계산해 C 에 박는다(기기마다 float 결과가 갈리지 않게 · 리뷰·시험이 표 하나를 본다).
프리셋 정의는 colorgen.py 의 FINAL(같은 폴더). 세로 이름 칸 글자(LOOK_VLAB)는 hub_glyphs.py 가 hub_glyphs.h 에 만든다."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import colorgen as G
KUROKO = ((0xEEE, 0x666, 0x000), (0xEEE, 0x666, 0x000))   # 가운데 무작위 칸 미리보기(쿠로코) — 실측 eee/666/000, 2P색 없음
out = sys.argv[1]
rows = [G.PAL1[c] for c in range(14)] + [(KUROKO, KUROKO)]
tab = []; dup = []
for r, row in enumerate(rows):
    tr = []; dr = []
    for sty in range(2):
        B, A = row[sty]
        t = [f(B, A) for n, f in G.FINAL]
        ok = []
        for i, x in enumerate(t):
            ok.append(i < 2 or all(G.dist(x, t[j]) > 6 for j in range(i) if ok[j]))
        if r == 14: ok[1] = False                      # 쿠로코: 2P색 없음
        tr.append(t); dr.append(sum(1 << i for i in range(16) if not ok[i]))
    tab.append(tr); dup.append(dr)
names = [n for n, f in G.FINAL] + ['내 색 1', '내 색 2']
s = ['/* look_gen.py 로 만든 컬러 표 — 고치지 말고 생성기를 고친다. 12비트 0x0BGR, [캐릭터 0~13 · 14 = 쿠로코(무작위 칸 미리보기)][검질][프리셋][색 1~3] */',
     '#define LOOK_NPRE 16', '#define LOOK_ROW_KUROKO 14',
     'static const uint16_t LOOK_TAB[15][2][LOOK_NPRE][3] = {']
for r in range(15):
    s.append('   { /* %d */' % r)
    for sty in range(2):
        s.append('      { ' + ', '.join('{0x%03X,0x%03X,0x%03X}' % t for t in tab[r][sty]) + ' },')
    s.append('   },')
s.append('};')
s.append('/* 같은 캐릭터·검질에서 앞 프리셋과 거의 같은 색(채널 차 합 ≤ 6) — 옵션으로 돌릴 때 건너뛴다(캐릭터 고르기에선 두 검질 모두 같을 때만) */')
s.append('static const uint16_t LOOK_DUP[15][2] = { ' + ', '.join('{0x%04X,0x%04X}' % tuple(d) for d in dup) + ' };')
s.append('/* 이름(앱 띠·기록과 같은 순서 — Java Look.NAMES) */')
s.append('static const char *const LOOK_NAME[LOOK_NPRE + 2] = { ' + ', '.join('"%s"' % n for n in names) + ' };')
open(os.path.join(out, 'look_tab.h'), 'w').write('\n'.join(s) + '\n')
print('rows', len(tab), 'names', len(names))
for r in range(15): print(r, ['%04x' % d for d in dup[r]])

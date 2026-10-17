#!/usr/bin/env python3
"""regress.py — 기록된 화면들을 두 롬으로 오프라인 재렌더해 픽셀 비교.
에뮬레이터를 돌리지 않는다. 기록 1회 -> 이후 무한 회귀검사.

사용: python3 regress.py <기록폴더> <구판.ngc> <신판.ngc> [차이이미지폴더]
"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tilemap as TM
from PIL import Image

def main(recdir, oldp, newp, imgdir=None):
    A = open(oldp, 'rb').read(); B = open(newp, 'rb').read()
    bad = 0
    for fp in sorted(glob.glob(os.path.join(recdir, '*.json'))):
        if fp.endswith('_coverage.json'): continue
        name, maps, s2r = TM.load_record(fp)
        changed = [s for s, a in s2r.items() if A[a:a+16] != B[a:a+16]]
        ia = TM.render(maps, TM.tiles_from_rom(A, s2r))
        ib = TM.render(maps, TM.tiles_from_rom(B, s2r))
        nd = int((ia != ib).any(2).sum())
        flag = '' if nd == 0 else '  <-- 차이'
        if nd: bad += 1
        print('%-14s 픽셀차 %6d  바뀐타일 %3d%s' % (name, nd, len(changed), flag))
        if nd and imgdir:
            os.makedirs(imgdir, exist_ok=True)
            cv = Image.new('RGB', (ia.shape[1], ia.shape[0] * 2 + 8), (15, 15, 15))
            cv.paste(Image.fromarray(ia), (0, 0)); cv.paste(Image.fromarray(ib), (0, ia.shape[0] + 8))
            cv.save(os.path.join(imgdir, name + '.png'))
    print('차이난 화면 %d개' % bad)

if __name__ == '__main__':
    main(*sys.argv[1:])

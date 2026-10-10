#!/usr/bin/env python3
"""observe.py — 게임을 돌리며 화면별 타일 관측 기록을 남긴다.

사용: python3 observe.py <롬> <출력폴더> [화면목록.json]
화면목록: [{"name":..,"sav":..,"steps":[["B",90],["run",60]]}, ...]
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/root/ss2_work')
from ngp_state import NGP5
import tilemap as TM

def run(rom_path, outdir, screens):
    rom = open(rom_path, 'rb').read()
    idx = TM.rom_index(rom)
    cov = set()
    for s in screens:
        n = NGP5(rom_path); n.load_state(s['sav']); n.run(2)
        for k, a in s['steps']:
            if k == 'run': n.run(a)
            else: n.press(k, 8); n.run(a)
        v = TM.dump_vram(n)
        maps, s2r = TM.observe(v, idx)
        TM.save_record(outdir, s['name'], maps, s2r)
        cov |= set(s2r.values())
        print('%-14s 슬롯 %3d  ROM타일 %3d' % (s['name'], len(s2r), len(set(s2r.values()))))
    json.dump(sorted(cov), open(os.path.join(outdir, '_coverage.json'), 'w'))
    print('합집합 고유 ROM 타일 주소 %d개 -> %s/_coverage.json' % (len(cov), outdir))

if __name__ == '__main__':
    scr = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else json.load(open('screens.json'))
    run(sys.argv[1], sys.argv[2], scr)

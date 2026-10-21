#!/bin/bash
# 동봉 한글판 — 앱과 같은 런어헤드 2 · 프레임 생성(fast 없이)
cd "$(dirname "$0")"; source env.sh
for t in t_look t_look2 t_look_hub; do
  mkdir -p work_A_$t
  LEAGUE_WORK=$T/work_A_$t timeout 4000 python3 $t.py ROM_KO > res_${t}_ROM_KO_app.txt 2>&1
done

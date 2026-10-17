#!/bin/bash
# 다른 롬 판 3개 × 시험 3개(fast — 런어헤드 없이)
cd "$(dirname "$0")"; source env.sh
for r in ROM_KO101 ROM_H1 ROM_JUE ROM_KO; do
  for t in t_look t_look_hub t_look2; do
    mkdir -p work_B_${t}_$r
    LEAGUE_WORK=$T/work_B_${t}_$r timeout 4000 python3 $t.py $r fast > res_${t}_$r.txt 2>&1
  done
done

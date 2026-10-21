#!/bin/bash
# t_hub(컬러 하네스 사본) — 롬 판 둘 더
cd "$(dirname "$0")"; source env.sh
for r in ROM_H1 ROM_JUE; do
  mkdir -p work_D_$r
  LEAGUE_WORK=$T/work_D_$r timeout 5000 python3 t_hub_look.py ${!r} > res_t_hub_look_$r.txt 2>&1; echo "EXIT $?" >> res_t_hub_look_$r.txt
done

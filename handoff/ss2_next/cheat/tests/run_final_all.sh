#!/bin/bash
# 마지막 코드로 전부 — 단계마다 동시에 3개까지. 결과: results/<태그>_*
cd "$(dirname "$0")"; source env.sh
P=3 ./run_reg.sh reg2 > results/run_reg2.log 2>&1                     # 필수 회귀(시험 파일 그대로)
P=3 ./run_tc.sh tc2 "ko ko101 h1 jp" > results/run_tc2.log 2>&1       # t_cheat 16묶음 × 롬 4판
P=3 ./run_extra.sh fx2 "ko jp" > results/run_fx2.log 2>&1             # t_extra(H-4·H-5b·H-6·H-7·H-8·연습 흐름·싸움 중 저장·세이브에 남기기 끄기)
( export LD_PRELOAD=$S/clkwrap/ftenv.so FIXT=1791974914
  for g in determ_on determ_off yugasurv13; do LEAGUE_WORK=$PWD/work_det2 timeout 3600 python3 t_extra.py ko $g > results/det2_ko_$g.txt 2>&1 & done; wait
  LEAGUE_WORK=$PWD/work_det2 python3 t_extra.py ko determ_cmp > results/det2_ko_determ_cmp.txt 2>&1 )
P=3 ./run_reg.sh h2off2 off > results/run_h2off2.log 2>&1              # H-2 치트 모두 끔으로 cheat_tick 끼움
P=3 ./run_reg.sh h2on2 on > results/run_h2on2.log 2>&1                 # H-2 모두 켬
echo ALLDONE > results/final_all_done.txt

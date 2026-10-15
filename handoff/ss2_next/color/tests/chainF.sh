#!/bin/bash
# 마지막 코드(host.so = 968ea51 의 league.c practice.c look.c vpanel.c)로 필수 회귀 다시
cd "$(dirname "$0")"; source env.sh
TT=/home/user/CustumApKS/handoff/ss2_practice/stage1/tests
run_fixt() { mkdir -p work_F_$1; env LD_PRELOAD=$S/clkwrap/ftenv.so FIXT=1791974914 LEAGUE_WORK=$T/work_F_$1 timeout 7000 python3 $TT/$1.py $ROM_KO > final_$1_914.txt 2>&1; echo "EXIT $?" >> final_$1_914.txt; }
run_fixt t_practice &
( run_fixt t_fix1; run_fixt t_resume;
  mkdir -p work_F_dual; LEAGUE_WORK=$T/work_F_dual timeout 5000 python3 /home/user/CustumApKS/handoff/ss2_practice/stage2/tests/t_dual.py $ROM_KO > final_t_dual.txt 2>&1; echo "EXIT $?" >> final_t_dual.txt ) &
( mkdir -p work_F_hub; LEAGUE_WORK=$T/work_F_hub timeout 5000 python3 t_hub_look.py $ROM_KO > final_t_hub_look.txt 2>&1; echo "EXIT $?" >> final_t_hub_look.txt ) &
wait

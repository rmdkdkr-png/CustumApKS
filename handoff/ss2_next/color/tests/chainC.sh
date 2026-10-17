#!/bin/bash
# 컬러 켬 회귀 — 기존 시험 넷을 look 이 켜진 하네스로. 스크립트 폴더가 sys.path 맨 앞이라 t_practice·t_fix1·t_resume 는
# lookph/ 에 복사한 것(내용 그대로)을 돌려 lookph/ph.py 가 잡히게, t_dual(다른 폴더)은 PYTHONPATH 맨 앞 lookph 로
cd "$(dirname "$0")"; source env.sh
export PYTHONPATH=$T/lookph:$PYTHONPATH
for t in t_fix1 t_resume t_practice; do
  mkdir -p work_C_$t
  env LD_PRELOAD=$S/clkwrap/ftenv.so FIXT=1791974914 LEAGUE_WORK=$T/work_C_$t timeout 7000 python3 $T/lookph/$t.py $ROM_KO > lookon_${t}_914.txt 2>&1; echo "EXIT $?" >> lookon_${t}_914.txt
done
mkdir -p work_C_dual
LEAGUE_WORK=$T/work_C_dual timeout 5000 python3 /home/user/CustumApKS/handoff/ss2_practice/stage2/tests/t_dual.py $ROM_KO > lookon_t_dual.txt 2>&1; echo "EXIT $?" >> lookon_t_dual.txt

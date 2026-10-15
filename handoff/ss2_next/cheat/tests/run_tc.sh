#!/bin/bash
# t_cheat.py 묶음마다 따로 프로세스(같은 코어 .so 를 한 프로세스에서 여러 번 올리지 않게) — 동시에 3개까지(4코어를 다른 작업과 나눠 씀)
# 사용: run_tc.sh <태그> "<롬키들>" "<묶음들>"
cd "$(dirname "$0")"; source env.sh
export LD_PRELOAD=$S/clkwrap/ftenv.so FIXT=1791974914
TAG=$1; ROMS=${2:-"ko ko101 h1 jp"}; G=${3:-"cards perm time hp ko rage cpu diff pow yuga prac league save surv clear yugasurv"}
mkdir -p results
for r in $ROMS; do for g in $G; do echo "$r $g"; done; done | \
  xargs -P ${P:-3} -L 1 bash -c 'LEAGUE_WORK='"$PWD"'/work_tc_$0 timeout 2400 python3 t_cheat.py $0 $1 > results/'"$TAG"'_$0_$1.txt 2>&1'
for r in $ROMS; do
  P=$(cat results/${TAG}_${r}_*.txt | grep -c '^PASS'); F=$(cat results/${TAG}_${r}_*.txt | grep -c '^FAIL')
  E=$(grep -L '^== ' results/${TAG}_${r}_*.txt | wc -l)
  echo "$TAG $r: PASS $P FAIL $F (끝 못 본 파일 $E)"
done | tee results/${TAG}_summary.txt

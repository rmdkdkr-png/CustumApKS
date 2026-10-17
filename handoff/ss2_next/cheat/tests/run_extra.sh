#!/bin/bash
# t_extra.py 묶음을 롬별로 — 동시에 3개까지. 사용: run_extra.sh <태그> "<롬키들>" "<묶음들>"
cd "$(dirname "$0")"; source env.sh
export LD_PRELOAD=$S/clkwrap/ftenv.so FIXT=1791974914
TAG=$1; ROMS=${2:-ko}; G=${3:-"stload pow3 pracyuga autosave pracblock stfight permoff tempperm yugastory"}
mkdir -p results
for r in $ROMS; do for g in $G; do echo "$r $g"; done; done | \
  xargs -P ${P:-3} -L 1 bash -c 'LEAGUE_WORK='"$PWD"'/work_ex_$0 timeout 3600 python3 t_extra.py $0 $1 > results/'"$TAG"'_$0_$1.txt 2>&1'
for r in $ROMS; do
  echo "$TAG $r: PASS $(cat results/${TAG}_${r}_*.txt | grep -c '^PASS') FAIL $(cat results/${TAG}_${r}_*.txt | grep -c '^FAIL') (끝 못 본 파일 $(grep -L '^== ' results/${TAG}_${r}_*.txt | wc -l))"
done | tee results/${TAG}_summary.txt

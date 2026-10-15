#!/bin/bash
# 필수 회귀(시험 파일 그대로, host.so = league.c + practice.c + cheat.c) — 동시에 3개까지
# 사용: run_reg.sh <태그> [wrap 모드 off|on — 주면 with_cheat.py 로 cheat_tick 을 끼움]
cd "$(dirname "$0")"; source env.sh
TAG=$1; WRAP=$2
T1=/home/user/CustumApKS/handoff/ss2_practice/stage1/tests
R=$ROMKO
run() {   # 이름 FIXT 시험 인자…
  local name=$1 fixt=$2; shift 2
  local pre=""; [ -n "$WRAP" ] && pre="with_cheat.py $WRAP"
  if [ "$fixt" = 1 ]; then
    LEAGUE_WORK=$PWD/work_${TAG}_$name LD_PRELOAD=$S/clkwrap/ftenv.so FIXT=1791974914 timeout 3600 python3 $pre "$@" > results/${TAG}_$name.txt 2>&1
  else
    LEAGUE_WORK=$PWD/work_${TAG}_$name timeout 3600 python3 $pre "$@" > results/${TAG}_$name.txt 2>&1
  fi
}
export -f run; export TAG WRAP R T1
printf '%s\n' "t_practice 1 $T1/t_practice.py $R" "t_fix1 1 $T1/t_fix1.py $R" "t_resume 1 $T1/t_resume.py $R" \
  "t_hub 0 /home/user/CustumApKS/handoff/ss2_league/stage3/tests/t_hub.py $R" "t_dual 0 /home/user/CustumApKS/handoff/ss2_practice/stage2/tests/t_dual.py $R" | \
  xargs -P ${P:-3} -L 1 bash -c 'run "$@"' _
for n in t_practice t_fix1 t_resume t_hub t_dual; do
  echo "$TAG $n: PASS $(grep -c '^PASS' results/${TAG}_$n.txt) FAIL $(grep -c '^FAIL' results/${TAG}_$n.txt) · $(tail -1 results/${TAG}_$n.txt)"
done | tee results/${TAG}_summary.txt

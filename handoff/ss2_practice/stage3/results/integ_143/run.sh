#!/bin/bash
# 컬러 + 치트 + 프레임 데이터 합친 코드 회귀(t_framedata 한패·순정·앱 모드 더함) — host.so 하나로 두 갈래 시험과 기존 시험 모두. 동시에 3개.
S=/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad; I=$S/integ2
BASE=/home/user/CustumApKS/handoff/ss2_league:/home/user/CustumApKS/handoff/ss2_league/stage1/tests:/home/user/CustumApKS/handoff/ss2_practice/stage1/tests
TT=/home/user/CustumApKS/handoff/ss2_practice/stage1/tests
CT=$S/impl/color-tests; HT=$S/impl/cheat-tests
export LEAGUE_HOST_SO=$I/host.so LEAGUE_CORE=$S/prac1/core/core_89860fe.so PRACTICE_CPP=$S/impl/framedata/app/src/main/cpp
export ROM_KO=$S/legacito/ss2_ko_bundled.ngc ROMKO=$S/legacito/ss2_ko_bundled.ngc ROMKO101=$S/legacito/ss2_ko101.ngc ROMH1=$S/legacito/ss2h1_ko101.ngc ROMJP=/root/.claude/uploads/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/ee972d92-Samurai_Shodown_2_JUE_.ngc ROM_JUE=$ROMJP
FX="LD_PRELOAD=$S/clkwrap/ftenv.so FIXT=1791974914"
job() { n=$1; shift; mkdir -p $I/w_$n; (cd $I && env LEAGUE_WORK=$I/w_$n "$@" > $I/res/$n.txt 2>&1; echo "EXIT $?" >> $I/res/$n.txt); }
export -f job; export I S
{
echo "prac env $FX PYTHONPATH=$BASE timeout 7000 python3 $TT/t_practice.py $ROM_KO"
echo "fix1 env $FX PYTHONPATH=$BASE timeout 3000 python3 $TT/t_fix1.py $ROM_KO"
echo "resume env $FX PYTHONPATH=$BASE timeout 3000 python3 $TT/t_resume.py $ROM_KO"
echo "dual env PYTHONPATH=$BASE timeout 3000 python3 /home/user/CustumApKS/handoff/ss2_practice/stage2/tests/t_dual.py $ROM_KO"
echo "hublook env PYTHONPATH=$BASE:$CT timeout 4000 python3 $CT/t_hub_look.py $ROM_KO"
echo "look env PYTHONPATH=$BASE:$CT timeout 4000 python3 $CT/t_look.py ROM_KO"
echo "lookhub env PYTHONPATH=$BASE:$CT timeout 4000 python3 $CT/t_look_hub.py ROM_KO"
echo "look2 env PYTHONPATH=$BASE:$CT timeout 4000 python3 $CT/t_look2.py ROM_KO"
for g in cards perm time hp ko rage cpu diff pow yuga prac league save surv clear yugasurv; do echo "tc_$g env $FX PYTHONPATH=$BASE:$HT timeout 2400 python3 $HT/t_cheat.py ko $g"; done
for g in pracyuga stload autosave pow3 stfight pracblock tempperm permoff yugastory; do echo "fx_$g env $FX PYTHONPATH=$BASE:$HT timeout 3000 python3 $HT/t_extra.py ko $g"; done
echo "det_off env $FX PYTHONPATH=$BASE:$HT timeout 3000 python3 $HT/t_determ.py off"
X=$S/next/framedata/x
echo "fd_ko env $FX PYTHONPATH=$X:$BASE timeout 4000 python3 $X/t_framedata.py ko"
echo "fd_jp env $FX PYTHONPATH=$X:$BASE timeout 4000 python3 $X/t_framedata.py jp"
echo "fd_app env $FX FD_MODE=app PYTHONPATH=$X:$BASE timeout 5000 python3 $X/t_framedata.py ko"
echo "det_on env $FX PYTHONPATH=$BASE:$HT timeout 3000 python3 $HT/t_determ.py on"
} | xargs -P 3 -L 1 bash -c 'job "$@"' _
for f in $I/res/*.txt; do echo "$(basename $f .txt) PASS $(grep -c '^PASS' $f) FAIL $(grep -c '^FAIL' $f) | $(tail -n 2 $f | head -1 | cut -c1-70) | $(tail -n 1 $f)"; done > $I/summary.txt
cat $I/summary.txt

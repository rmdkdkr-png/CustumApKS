#!/bin/sh
# 예전 리그·룩 JVM 시험(../../../color/tests/jvm 의 LeagueTest·LookTest)을 랭크 판(내부 144) 소스로 — League 가 RankCore·ProfileGen·AvatarGen 을 부르니
# 이 폴더의 스텁(Context·AssetManager 포함)으로 컴파일한다.
# 사용: sh run_old.sh <앱 java 폴더> <json.jar> <앱 assets 폴더>
J=$(cd "$(dirname "$0")" && pwd); CT=$J/../../../color/tests/jvm
SRC=${1:-/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/impl/ranked/app/src/main/java/com/dudu/pocketcore}
JAR=${2:-/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/legacito/jtest/json.jar}; AS=${3:-$SRC/../../../../assets}
O=$J/old; rm -rf "$O"; mkdir -p "$O/out" "$O/r_main" "$O/r_mig" "$O/r_look"
javac -encoding UTF-8 -cp "$JAR" -d "$O/out" $(find "$J/stub" -name '*.java') "$SRC/League.java" "$SRC/Look.java" "$SRC/RankCore.java" "$SRC/AvatarGen.java" "$SRC/ProfileGen.java" "$CT/LeagueTest.java" "$CT/LookTest.java" || exit 1
for t in "main:LeagueTest" "mig:LeagueTest migrate" "look:LookTest"; do
  n=${t%%:*}; c=${t#*:}
  java -Dstdout.encoding=UTF-8 -Dfile.encoding=UTF-8 -Dleague.root="$O/r_$n" -Dassets.dir="$AS" -cp "$O/out:$JAR" com.dudu.pocketcore.$c > "$O/res_$n.txt" 2>&1
  echo "$n exit $? PASS $(grep -c '^PASS' "$O/res_$n.txt") FAIL $(grep -c '^FAIL' "$O/res_$n.txt")"
done

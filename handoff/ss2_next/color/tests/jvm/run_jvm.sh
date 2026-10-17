#!/bin/sh
# JVM 시험 — League.java·Look.java(앱 소스 그대로) + 스텁(MainActivity·Settings·Emu·Log). 사용: sh run_jvm.sh <앱 java 폴더> <json.jar>
J=$(cd "$(dirname "$0")" && pwd); SRC=${1:-/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/impl/color/app/src/main/java/com/dudu/pocketcore}
JAR=${2:-/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/legacito/jtest/json.jar}
rm -rf "$J/out" "$J/r_main" "$J/r_mig" "$J/r_look"; mkdir -p "$J/out" "$J/r_main" "$J/r_mig" "$J/r_look"
javac -encoding UTF-8 -cp "$JAR" -d "$J/out" "$J"/stub/android/util/Log.java "$J"/stub/com/dudu/pocketcore/*.java "$SRC/League.java" "$SRC/Look.java" "$J/LeagueTest.java" "$J/LookTest.java" || exit 1
java -Dstdout.encoding=UTF-8 -Dfile.encoding=UTF-8 -Dleague.root="$J/r_main" -cp "$J/out:$JAR" com.dudu.pocketcore.LeagueTest > "$J/res_jvm_main.txt" 2>&1; echo "LeagueTest main exit $?"
java -Dstdout.encoding=UTF-8 -Dfile.encoding=UTF-8 -Dleague.root="$J/r_mig" -cp "$J/out:$JAR" com.dudu.pocketcore.LeagueTest migrate > "$J/res_jvm_migrate.txt" 2>&1; echo "LeagueTest migrate exit $?"
java -Dstdout.encoding=UTF-8 -Dfile.encoding=UTF-8 -Dleague.root="$J/r_look" -cp "$J/out:$JAR" com.dudu.pocketcore.LookTest > "$J/res_jvm_look.txt" 2>&1; echo "LookTest exit $?"

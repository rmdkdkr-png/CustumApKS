#!/bin/sh
# 랭크 매치 JVM 시험 — 앱 소스(League·Look·RankCore·AvatarGen·ProfileGen) + 스텁(Context·AssetManager·MainActivity·Settings·Emu·Log).
# 사용: sh run_jvm.sh <앱 java 폴더> <json.jar> <앱 assets 폴더>
J=$(cd "$(dirname "$0")" && pwd); SRC=${1:-/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/impl/ranked/app/src/main/java/com/dudu/pocketcore}; JAR=${2:-/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/legacito/jtest/json.jar}; AS=${3:-$SRC/../../../../assets}
rm -rf "$J/out" "$J/r_main" "$J/r_mig" "$J/r_core"; mkdir -p "$J/out" "$J/r_main" "$J/r_mig"
javac -encoding UTF-8 -cp "$JAR" -d "$J/out" $(find "$J/stub" -name '*.java') "$SRC/League.java" "$SRC/Look.java" "$SRC/RankCore.java" "$SRC/AvatarGen.java" "$SRC/ProfileGen.java" "$J/LeagueRankedTest.java" "$J/RankCoreTest.java" || exit 1
java -Dstdout.encoding=UTF-8 -Dfile.encoding=UTF-8 -cp "$J/out" com.dudu.pocketcore.RankCoreTest > "$J/res_rankcore.txt" 2>&1; echo "RankCoreTest exit $?"
java -Dstdout.encoding=UTF-8 -Dfile.encoding=UTF-8 -Dleague.root="$J/r_main" -Dassets.dir="$AS" -cp "$J/out:$JAR" com.dudu.pocketcore.LeagueRankedTest > "$J/res_ranked_main.txt" 2>&1; echo "LeagueRankedTest main exit $?"
java -Dstdout.encoding=UTF-8 -Dfile.encoding=UTF-8 -Dleague.root="$J/r_mig" -Dassets.dir="$AS" -cp "$J/out:$JAR" com.dudu.pocketcore.LeagueRankedTest migrate > "$J/res_ranked_migrate.txt" 2>&1; echo "LeagueRankedTest migrate exit $?"

#!/bin/sh
# 148 이 쓴 league.json 을 147(7b35ba2) League 가 읽고 다시 써도 148 칸(시즌 2·seasons·pending.miss·시작한 뒤 무효·pref.last_rom)이 남나 — spec §4.4 · §7 «run_old.sh» 항목.
# 1) 148 소스 + Compat148Make 로 파일을 쓰고  2) 147 소스(git show 7b35ba2) + Compat147Check 로 읽고 다시 써서 본다. 결과 = res_compat147.txt
# 사용: sh run_compat147.sh <앱 java 폴더> <json.jar> <앱 assets 폴더> [147 소스 폴더 — 없으면 앱 저장소에서 git show 7b35ba2]
J=$(cd "$(dirname "$0")" && pwd); SRC=$1; JAR=$2; AS=${3:-$SRC/../../../../assets}; OLD=$4
C=$J/compat; rm -rf "$C"; mkdir -p "$C/o148" "$C/o147" "$C/root" "$C/src147"
if [ -z "$OLD" ]; then
  G=$(cd "$SRC" && git rev-parse --show-toplevel) || exit 1
  for f in League RankCore Look AvatarGen ProfileGen; do (cd "$G" && git show 7b35ba2:app/src/main/java/com/dudu/pocketcore/$f.java) > "$C/src147/$f.java" || exit 1; done
  OLD=$C/src147
fi
javac -encoding UTF-8 -cp "$JAR" -d "$C/o148" $(find "$J/stub" -name '*.java') "$SRC/League.java" "$SRC/Look.java" "$SRC/RankCore.java" "$SRC/AvatarGen.java" "$SRC/ProfileGen.java" "$J/Compat148Make.java" || exit 1
javac -encoding UTF-8 -cp "$JAR" -d "$C/o147" $(find "$J/stub" -name '*.java') "$OLD/League.java" "$OLD/Look.java" "$OLD/RankCore.java" "$OLD/AvatarGen.java" "$OLD/ProfileGen.java" "$J/Compat147Check.java" || exit 1
java -Dstdout.encoding=UTF-8 -Dfile.encoding=UTF-8 -Dleague.root="$C/root" -Dassets.dir="$AS" -cp "$C/o148:$JAR" com.dudu.pocketcore.Compat148Make > "$J/res_compat147.txt" 2>&1 || { echo "Compat148Make 실패"; exit 1; }
java -Dstdout.encoding=UTF-8 -Dfile.encoding=UTF-8 -Dleague.root="$C/root" -Dassets.dir="$AS" -cp "$C/o147:$JAR" com.dudu.pocketcore.Compat147Check >> "$J/res_compat147.txt" 2>&1; echo "Compat147Check exit $?"

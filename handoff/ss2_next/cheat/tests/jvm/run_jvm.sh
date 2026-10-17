#!/bin/bash
# J-1·J-2 — Cheats.java + 앱 Settings.java 를 스텁(MainActivity·Theme·AppIcon·Games·Emu)과 함께 호스트 JVM 에서
cd "$(dirname "$0")"
A=${1:-/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/impl/cheat/app/src/main/java/com/dudu/pocketcore}
rm -rf out root
javac -encoding UTF-8 -nowarn -cp json.jar -d out stub/com/dudu/pocketcore/*.java $A/Settings.java $A/Cheats.java CheatsTest.java || exit 1
java -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 -Dcheat.root=$PWD/root -cp out:json.jar com.dudu.pocketcore.CheatsTest

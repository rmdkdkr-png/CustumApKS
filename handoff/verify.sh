set -uo pipefail
ROOT=/home/user/emu-ex-plus-alpha
export ANDROID_HOME=/home/user/android-sdk
export PATH=$ANDROID_HOME/build-tools/36.0.0:$ANDROID_HOME/platform-tools:$PATH
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
cd "$ROOT"
APK=NGP.emu/build/android/build/outputs/apk/release/NgpEmu-release.apk
FAIL=0
ok(){ [ "$2" = "$3" ] && printf '  OK   %-28s %s\n' "$1" "$2" || { printf '  FAIL %-28s got=%s want=%s\n' "$1" "$2" "$3"; FAIL=1; }; }

echo "===== 4) 검증 기준표 ====="
B=$(aapt2 dump badging "$APK" | head -1)
echo "  badging: $B"
ok package     "$(grep -oE "^package: name='[^']*'" <<<"$B" | cut -d"'" -f2)"        com.rmdkdkr.ngpemu.ss2
ok versionCode "$(sed -n "s/.*versionCode='\([^']*\)'.*/\1/p" <<<"$B")" 16010590
ok versionName "$(sed -n "s/.*versionName='\([^']*\)'.*/\1/p" <<<"$B")" 1.5.85-SS2-1.0.0

echo "--- ABI 4종"
LIST=$(unzip -l "$APK")          # pipefail + grep -q 가 unzip 에 SIGPIPE 를 내므로 먼저 담는다
for a in arm64-v8a armeabi-v7a x86 x86_64; do
  case "$LIST" in *"lib/$a/libmain.so"*) echo "  OK   $a";; *) echo "  FAIL $a"; FAIL=1;; esac
done

rm -rf /tmp/chk && mkdir -p /tmp/chk && cd /tmp/chk
unzip -o -q "$ROOT/$APK" 'lib/*/libmain.so' assets/gpOverlay.png
echo "--- assets/gpOverlay.png md5"
ok gpOverlay.png "$(md5sum < assets/gpOverlay.png | cut -d' ' -f1)" 24bed154fbd45b774a8410e90aaf8483

echo "--- libmain.so 안 문자열 개수 (LC_ALL=C grep -a -o -F)"
# 주의: 「승부!」「한 판!」 같은 8바이트짜리 구령 리터럴은 컴파일러가 명령어
# 즉치값으로 인라인해서 .so 에서 grep 이 안 된다 (x86 코어의 movabs 로 확인).
# 그래서 짧은 구령은 표에 못 올린다 — 「한 판!|3
cnt(){ LC_ALL=C grep -a -o -F "$1" lib/arm64-v8a/libmain.so | wc -l | tr -d ' '; }
while IFS='|' read -r s want; do ok "$s" "$(cnt "$s")" "$want"; done <<'T'
SS2 Commentator|1
SS2 Commentary Vibration|1
SS2 Side Art|1
겐주로|47
하오마루|52
리쿠도렛카|1
마를 봉하는 사람|1
유파는 달라도 저분처럼|2
한조는 잘 있으려나|1
자아 — 정정당당히!|1
%d회전!|1
한 판!|2
%s가 크게 맞았다! 핫하!|1
%s의 다리가 풀렸다, 지금이다!!|1
%s에게 베였다… 다음엔 내가 벤다|1
%s는 손도 못 대는군, 핫핫하!|1
승부 결정!|1
훌륭하오|2
첫 판 — 정정당당히|0
네가 남자 그릇이다|1
간다라는 내가 지었다. 시체 수천을 꿰매서|1
진조니|0
오미고토|0
하오마루라. 그저 검을 휘두르는 인간이군|0
등의 흉터는 제 어미가 낸 것이다|1
붓 안에 창이 숨어 있다. 묵혈필창이지|1
두 자루의 무게를 아는 손이다|1
허, 둘 다 하오마루냐! 어느 쪽이 진짜 술꾼이지|1
뭐냐 저건. 사람이 아니잖아|1
간다라다. 내가 지은 것이지|1
허, 나를 쓰는군! 술은 내가 산다|1
너, 술은 하나?|1
키바가미 겐주로다|1
모로즈미 타이잔|2
니코친 밑에서 겐주로와 한솥밥 먹던 몸이다, 핫핫하!|1
시키 씨는 제 뜻이 어디 있는지 저도 모른대요… 슬퍼요|1
유가… 그 목소리가, 머리에서 안 나가|1
타무리키|0
한조 님께 배운|0
카프카미|0
저 검은 주인을 먹는다|1
빨간 냄새가 나|1
첫 피다|0
붓 한 자루로 싸우는 화가|0
딸들|0
붓 한 자루로 싸우는 화가|0
T

echo
echo "===== 대조용 두 줄 ====="
ls -l "$ROOT/$APK"
md5sum lib/arm64-v8a/libmain.so
echo "--- .so 크기 (참고: 경로 때문에 달라도 됨)"
for a in arm64-v8a armeabi-v7a x86 x86_64; do printf '  %-12s %s\n' "$a" "$(stat -c%s lib/$a/libmain.so)"; done

echo
echo "===== 11) 서명 v1+v2+v3 ====="
cd "$ROOT"
apksigner sign --ks ~/.android/debug.keystore --ks-pass pass:android --key-pass pass:android \
  --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
  --out "$ROOT/NgpEmu-signed.apk" "$APK" && apksigner verify -v "$ROOT/NgpEmu-signed.apk"

echo
echo "===== 17) 롬 혼입 ====="
find "$ROOT" \( -name '*.ngc' -o -name '*.ngp' -o -name 'st_*.bin' \) -not -path '*/.git/*' | head
echo "(위가 비었으면 깨끗)"
echo
[ "$FAIL" = 0 ] && echo "===== 기준표 전항 통과 =====" || echo "===== 기준표 불일치 있음 ====="
echo "===== VERIFY DONE ====="

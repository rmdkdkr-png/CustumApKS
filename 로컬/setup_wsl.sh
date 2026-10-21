#!/bin/bash
# PC(WSL Ubuntu)에서 클라우드 시험 하네스를 고치지 않고 그대로 돌리게 길만 맞춘다.
#   root 로(wsl -u root) · /tmp 가 비면(WSL 다시 켬) 한 번 더 · 같은 묶음이 이미 풀려 있으면 풀기는 건너뜀
#   POCKETCORE=<pocketcore 클론> ANDROID_HOME=<SDK> [SS2CORE=<ss2-sp-core 클론>] [ROM_JUE_SRC=<원판 JUE 롬>] [H=<풀 곳, 기본 ~/pcs>] bash setup_wsl.sh
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
H=${H:-$HOME/pcs}
POCKETCORE=${POCKETCORE:?pocketcore 클론 경로(feat/framegen-art)}
ANDROID_HOME=${ANDROID_HOME:?Android SDK 경로}
SS2CORE=${SS2CORE:-}; ROM_JUE_SRC=${ROM_JUE_SRC:-}
CUSTUM=$(cd "$HERE/.." && pwd)
SP=/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad
UP=/root/.claude/uploads/e6c46352-6bb9-5a9d-8b3a-f2da7447674e
NEW=$(sha256sum "$HERE/pc_harness.tar.gz" | cut -c1-16); STAMP=$H/scratchpad/.pc_harness.sha     # 묶음이 바뀌면(새 판) 위에 덮어 풂
[ "$(cat "$STAMP" 2>/dev/null)" = "$NEW" ] || { mkdir -p "$H/scratchpad"; tar --overwrite --keep-directory-symlink -xzf "$HERE/pc_harness.tar.gz" -C "$H/scratchpad" && echo "$NEW" > "$STAMP"; }
mkdir -p "$(dirname "$SP")" /home/user "$UP"
ln -sfn "$H/scratchpad" "$SP"
ln -sfn "$POCKETCORE" /home/user/pocketcore
ln -sfn "$CUSTUM" /home/user/CustumApKS
[ -z "$SS2CORE" ] || ln -sfn "$SS2CORE" /home/user/ss2-sp-core
[ -e /root/android-sdk ] || ln -sfn "$ANDROID_HOME" /root/android-sdk
W=$H/scratchpad/w182                                        # 하네스의 «지금 판 트리» = pocketcore 클론
[ -L "$W" ] || { [ ! -e "$W" ] || mv "$W" "$W.from_tarball.$$"; }    # 옛 묶음(1판)엔 진짜 w182/ 가 있었음 — 비켜 두고 링크
ln -sfn "$POCKETCORE" "$W"
mkdir -p "$H/scratchpad/u182/bin" "$H/scratchpad/u182r/h/bin" "$H/scratchpad/u187/bin"   # 링크(u182r/bin → u182/bin 등)가 가리키는 빌드 자리
# round1.st(첫 라운드 세이브스테이트 4개 — t_hold · 리그 장면 · GapSim 이 읽음): 롬에서 나온 것이라 지금 묶음엔 없음 → 1판 묶음(커밋 c5efba4) 기록에서 하네스 안으로만 꺼냄
if [ ! -f "$H/scratchpad/u157/impl/merge/native/r1/jue/round1.st" ]; then
  git -C "$CUSTUM" show c5efba4:로컬/pc_harness.tar.gz | tar -xzf - -C "$H/scratchpad" --wildcards '*/round1.st' || echo "round1.st 못 꺼냄 — README 3절"
fi
[ -z "$ROM_JUE_SRC" ] || ln -sfn "$ROM_JUE_SRC" "$UP/ee972d92-Samurai_Shodown_2_JUE_.ngc"
cd "$SP"; sed "s#ROOT_UPLOADS/#$UP/#" "$HERE/roms.md5" | md5sum -c 2>/dev/null | sed 's/^/롬: /' || true
echo "됨 — $SP → $H/scratchpad · 빌드 확인: bash \$SP/u187/build.sh · 짧은 시험: bash \$SP/u187/test.sh"

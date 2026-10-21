# 로컬(PC · WSL)에서 PocketCore 작업하기 — Claude·GPT 같이

클라우드 세션이 쓰던 빌드·시험 환경을 PC 로 옮기는 안내. 저장소 코드는 GitHub 에 다 있고, **클라우드 임시 폴더에만 있던 시험 하네스**를 여기 `pc_harness.tar.gz` 로 묶어 둠(2026-10-20, 내부 187 기준).

## 자리
**WSL Ubuntu** 에서(하네스가 리눅스 전용: gcc 로 .so 빌드 · Python ctypes · /tmp 경로). 윈도우 쪽엔 아무것도 안 깔아도 됨.
클라우드와 똑같이 root 로 돌리는 게 제일 쉬움: `wsl -u root`.

## 1. 깔 것 (WSL, 한 번)
```bash
apt update && apt install -y openjdk-21-jdk unzip gcc make python3-numpy python3-pil cmake
# Android SDK (cmdline-tools → 필요한 것만)
mkdir -p /opt/android-sdk/cmdline-tools && cd /tmp
curl -LO https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip -q commandlinetools-linux-*_latest.zip -d /opt/android-sdk/cmdline-tools && mv /opt/android-sdk/cmdline-tools/cmdline-tools /opt/android-sdk/cmdline-tools/latest
export ANDROID_HOME=/opt/android-sdk; yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --licenses >/dev/null
$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager "platforms;android-34" "build-tools;34.0.0" "cmake;3.22.1" "platform-tools"
# NDK 27.2.12479018 — 이미 받아 둔 게 있으면 링크만
mkdir -p $ANDROID_HOME/ndk && ln -sfn /home/dudu/android-ndk $ANDROID_HOME/ndk/27.2.12479018
# gradle 8.14.3 (저장소에 wrapper 없음)
curl -LO https://services.gradle.org/distributions/gradle-8.14.3-bin.zip && unzip -q gradle-8.14.3-bin.zip -d /opt && ln -sfn /opt/gradle-8.14.3/bin/gradle /usr/local/bin/gradle
```
클라우드에서 쓰던 판: JDK 21 · Gradle 8.14.3 · SDK platform 34 · build-tools 34.0.0 · CMake 3.22.1 · NDK 27.2.12479018 · Python 3 + numpy · PIL.

## 2. 저장소
- `rmdkdkr-png/pocketcore` 갈래 **feat/framegen-art** — 앱. 다른 세션과 같이 씀.
- `rmdkdkr-png/ss2-sp-core` — 코어 소스(CI 는 1cb33c9 + `pocketcore/tools/core_patches/*.patch` 이름 차례). 코어 다시 빌드할 때만.
- `rmdkdkr-png/CustumApKS` 갈래 claude/emu-ex-plus-alpha-build-9yqxli — 인계 문서 `handoff/ss2_next/<판>/README.md`, 이 폴더.

APK 빌드 확인: `cd pocketcore && echo "sdk.dir=$ANDROID_HOME" > local.properties && gradle :app:assembleDebug` → `app/build/outputs/apk/debug/`.

## 3. 시험 하네스 풀기
```bash
POCKETCORE=<pocketcore 클론> ANDROID_HOME=/opt/android-sdk SS2CORE=<ss2-sp-core 클론> ROM_JUE_SRC=<원판 JUE 롬> bash 로컬/setup_wsl.sh
```
- 하네스 스크립트엔 클라우드 경로(`/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad`)가 박혀 있어서, 고치지 않고 그 자리에 심볼릭 링크를 건다(`/home/user/pocketcore` · `/root/android-sdk` 도). WSL 을 다시 켜면 /tmp 가 비니 setup 을 한 번 더.
- `w182` = 지금 판 트리 → pocketcore 클론을 가리킴.
- 들어 있는 것(2판): 스크립트·소스 11 099개(117 MB, 목록 `pc_harness_files.txt`) · 하네스 안 심볼릭 링크 44개(`u182r/core181 → u182/core182`, `u182r/bin → u182/bin`, `…/nat/bin → ../../h/bin`, `…/render/mockdump → u157/impl/render/mockdump` 등) ·
  시험용 호스트 코어 .so(core182 = core181 + snd_only 등 — 리눅스 x86_64, WSL 에서 그대로 돎) · host_base.so(381ece9 기준, 미리 구움) · 효과음 비교용 게임 소리 6개(`u182r/s/ref/game_*.wav` 등, t_uisfx 용 짧은 녹음).
  sim 껍데기 `u182/sim/stub/android/app/Activity.java` 등(1판에서 `app/`·`src/` 폴더가 빠졌던 것) 포함 — android.jar 는 공식 platform 34 그대로, 껍데기가 클래스패스 앞이라 덮음.
  **안 넣은 것**: 롬 · 세이브스테이트(.st) · 시험 결과(out/logs) · 옛 작업 트리(w149·w153 …, `w182` 도 — setup 이 pocketcore 클론으로 링크. 옛 비교 시험 몇 개만 씀, 필요하면 `git worktree add` 로 그 커밋을).
- setup 은 묶음 sha 를 기억해서, 새 묶음을 당기면 다시 실행할 때 위에 덮어 푼다(3판부터 링크 폴더 아래 겹친 항목 없음 → tar 오류 없음). 1판을 푼 자리에 덮으면 진짜 폴더/링크가 엇갈리니 1판 자리는 비켜 두고 새로 풀 것.
- **round1.st**(첫 라운드 세이브스테이트 — `u157/impl/merge/native/r1/{jue,ko}`, `u157/impl/native/final/r1/{jue,ko}`): t_hold · 리그 장면 · GapSim 카드가 읽음. 롬에서 나온 것이라 지금 묶음엔 없고, setup 이 1판 커밋(c5efba4) 기록에서 하네스 안으로만 꺼냄(저장소엔 다시 안 올림). 원래 만든 길: `u157/impl/native/run_ov_tests.sh` 21~26줄(`q_common.prep`, 옛 트리 host.so · core149) — 코어 판에 묶인 상태지만 core182 에서 그대로 읽힘.
- 효과음 시험(t_uisfx) 소리 16개: 게임 녹음 7개(game_* · jue_nat_* · ko_nat_*) + 우리 Python 합성 9개(refsynth_*, `u176s/tools/synth_ref.py` 결과).
- 롬: `roms.md5` 의 md5 와 같은 파일을 그 자리에(원판 JUE · 한글 bundled/101 · h1 · 소리 끈 _mute 판). setup 이 맞는지 찍어 줌. 없는 롬을 쓰는 시험만 실패.

## 4. 빌드·짧은 시험 (187 때 돌린 그대로)
- `bash $SP/u187/build.sh` — 호스트 .so · libnh · NDK 3 ABI · gradle 컴파일 (경고 0 이어야)
- `bash $SP/u187/test.sh` — 소리 붙듦 t_hold · 메뉴 JVM 9종 · oppjvm · uisfx · jvm 415 · t_view · 리그 장면 14 · GapSim 카드(`AJ_ASK=-Daskreal=true` 꼭 `=true`)
- 결과 기준: `u187/README.txt`(187: 전부 통과, GapSim 카드 30/0). 큰 묶음: `u182r/chain182.sh`(STEPS=…, state/ 의 .done 은 건너뜀 — 다시 돌리려면 지움).
- 코어 3 ABI 직접 빌드: `u182/ndk_core.sh`(ss2-sp-core 1cb33c9 + 패치 60개 → jniLibs 에 넣는 것).

**PC 재현 확인(2026-10-21, 3판 edceddd · pocketcore 8dc945f)**: 빌드 경고 0 · t_hold 12/12/16/8 · 메뉴 9종·oppjvm 39·jvm 415·tview 통과 · 리그 장면 14개 310/0 · GapSim 카드 30/0 · t_uisfx 57/0 — 클라우드와 전부 같음.
PC 실행: `wsl -d Ubuntu -u root bash /root/work/run187.sh [build|test|both|uisfx]`. 다음 판을 넘길 때는 판 번호 · 커밋 · 돌릴 시험만 적으면 됨.

## 5. 같이 일할 때 규칙 (Claude·GPT 공통)
- **feat/framegen-art 는 여러 세션이 같이 씀.** 올리기 전에 `git fetch origin +refs/heads/feat/framegen-art:refs/remotes/origin/feat/framegen-art` → 합치고 → `app/build.gradle` versionCode 를 비어 있는 다음 번호로(주석 끝 목록에도 추가). versionName 은 0.9 그대로. 강제 푸시 금지.
- CI: `.github/workflows/build-test-apk.yml`(APK → 릴리즈 fgtest · ci-release, 코어 → ci-core). 올린 뒤 성공 확인.
- 코어 패치는 `tools/core_patches/` 이름 차례 — `zzzzzzzzzzzzz_snd_only.patch` 가 맨 끝. 패치를 바꾸면 jniLibs 의 libretro_ss2.so 3개도 다시 빌드해 넣기.
- 판마다 인계: CustumApKS `handoff/ss2_next/<판>/README.md`(유저가 보게 될 것 · 시험 · 다음).
- 계약 문서: pocketcore `docs/157_contract.md`(§25 = 187 소리 규칙).
- 유저 취향: 한국어 짧게 · 알림 글(토스트) 싫어함 · 재현 자료 달라고 하지 않기 · 자주 저장(커밋).
- 롬·토큰은 저장소에 올리지 않음.

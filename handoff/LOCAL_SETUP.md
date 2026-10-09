# 로컬에서 이어가기

지금 작업은 클라우드 컨테이너에서 돌고 있다. 컨테이너는 일정 시간 놀면 반납되고
그 안의 임시 파일은 사라진다. 이 문서는 **본인 PC 에서 같은 작업을 이어가는 법**이다.

---

## 1. 지금 무엇이 어디 있나

| 무엇 | 어디 | 안전한가 |
|---|---|---|
| 엔진·코어 소스, APK, 릴리즈, 문서, 아이콘 | GitHub 세 저장소 | ✅ 영구 |
| 검증 도구 13종 (하네스·실측기) | `ss2-sp-core/tools/` | ✅ 영구 |
| SvC 실측 결과·램 오프셋 | `ss2-sp-core/tools/svc/` | ✅ 영구 |
| **세이브스테이트** (SS2 508개 + SvC 29개) | 전달 파일뿐 | ⚠️ 본인이 보관 |
| **캡처 이미지** (홍보 9장 등) | 전달 파일뿐 | ⚠️ 본인이 보관 |
| **롬** | 본인 PC | ⚠️ 애초에 저장소 금지 |

세이브스테이트와 캡처는 **롬에서 파생된 것**이라 저장소에 넣을 수 없다.
받은 압축 파일을 잃어버리면 다시 만들어야 한다 (SvC 세이브는 도구로 재생성 가능,
SS2 실플레이 세이브는 직접 플레이해야 함).

---

## 2. 어떤 방식으로 할 것인가 — 네 가지

### 한눈에

| | 클라우드(지금) | **WSL2** | MSYS2/Git Bash | 리눅스·맥 |
|---|---|---|---|---|
| 설치 수고 | 없음 | 적음 | 중간 | 이미 됨 |
| 작업 보존 | ❌ 사라짐 | ✅ | ✅ | ✅ |
| 리눅스 코어 빌드 | ✅ | ✅ | ❌ (윈도우 DLL 은 가능) | ✅ |
| 안드로이드 코어 | ✅ | ✅ | 어려움 | ✅ |
| APK 빌드 | ✅ | ✅ | 매우 어려움 | ✅ |
| 실측 하네스 | ✅ | ✅ | ✅ | ✅ |
| 롬 다루기 | 매번 업로드 | 로컬 그대로 | 로컬 그대로 | 로컬 그대로 |
| 빌드 속도 | 보통 | 빠름 | 빠름 | 빠름 |
| 디스크 | 세션당 제한 | 20 GB+ 권장 | 10 GB+ | — |

### 각각 무엇이 다른가

**클라우드 (지금 방식)**
설치가 없고 어디서든 붙는다. 폰으로도 지시를 내릴 수 있다.
대신 **세션이 끝나면 임시 파일이 사라지고**, 롬·세이브를 매번 올려야 한다.
빌드 결과물도 매번 받아야 한다. 지금까지 이 방식으로 해 왔다.

**WSL2 (윈도우 권장)**
윈도우 안에 진짜 우분투가 들어간다. **지금 이 환경과 사실상 같아진다** —
지금까지 쓴 명령을 그대로 복붙해도 돌아간다. 파일은 윈도우 탐색기에서도 보인다.
단점은 처음 한 번 설치와 디스크 20 GB 정도. 윈도우면 이걸 권한다.

**MSYS2 / Git Bash (윈도우 네이티브)**
윈도우에 리눅스 명령어만 얹는 방식. 가볍다.
그런데 **안드로이드 NDK·SDK 조합이 까다롭고 APK 빌드는 사실상 막힌다.**
실측 하네스처럼 순수 C 도구만 돌릴 거면 충분하지만, 코어·앱까지 만들 거면 부족하다.
※ Git Bash 단독으로는 **C 컴파일러가 없다.** MSYS2 를 따로 깔아야 gcc 가 생긴다.

**리눅스·맥**
가장 매끄럽다. 추가 설명이 필요 없다. 맥은 Android NDK 가 arm64 판으로 잘 돈다.

### 결론

- 윈도우 + 계속 개발할 생각 → **WSL2**
- 윈도우 + 가끔 실측만 → MSYS2
- 리눅스·맥 → 그냥 하면 된다
- 어쩌다 한 번, 설치하기 싫다 → 클라우드 유지 (대신 작업물 매번 챙기기)

---

## 3. WSL2 설치 (윈도우)

관리자 권한 PowerShell 에서 한 줄:

```powershell
wsl --install
```

재부팅하고 우분투가 열리면 사용자 이름·암호를 정한다. 끝이다.
이후로는 시작 메뉴에서 **Ubuntu** 를 열면 리눅스 터미널이 뜬다.

윈도우 파일은 `/mnt/c/Users/이름/` 으로 보이고,
반대로 리눅스 파일은 탐색기 주소창에 `\\wsl$\Ubuntu\home\이름` 으로 들어간다.

> **성능 주의**: 작업 폴더는 `/home/이름/` (리눅스 쪽)에 두어야 빠르다.
> `/mnt/c/...` 에 두고 빌드하면 몇 배 느려진다.

---

## 4. 필요한 것 설치

우분투(WSL2 포함) 기준:

```bash
sudo apt update
sudo apt install -y build-essential git python3 python3-pip nodejs npm \
                    unzip zip openjdk-21-jdk
pip3 install pillow py7zr
```

| 무엇 | 왜 |
|---|---|
| `build-essential` | gcc·make — 코어와 하네스 빌드 |
| `python3` + pillow | 실측기·이미지 처리 |
| `nodejs` | 대사표·글꼴 생성기 |
| `openjdk-21-jdk` | APK 빌드 (안 만들 거면 생략) |

### 안드로이드 (코어 5 ABI 또는 APK 를 만들 때만)

```bash
# NDK
cd ~ && wget https://dl.google.com/android/repository/android-ndk-r27c-linux.zip
unzip -q android-ndk-r27c-linux.zip && mv android-ndk-r27c android-ndk

# SDK (APK 용, 코어만 만들 거면 불필요)
mkdir -p ~/android-sdk/cmdline-tools && cd ~/android-sdk/cmdline-tools
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip -q commandlinetools-linux-*.zip && mv cmdline-tools latest
yes | ~/android-sdk/cmdline-tools/latest/bin/sdkmanager --licenses
~/android-sdk/cmdline-tools/latest/bin/sdkmanager "platform-tools" \
    "platforms;android-36" "build-tools;36.0.0"
```

버전은 바뀔 수 있다. NDK 는 r27 계열이면 된다.

---

## 5. 저장소 가져오기

```bash
mkdir -p ~/ss2 && cd ~/ss2
git clone https://github.com/rmdkdkr-png/ss2-sp-core
git clone https://github.com/rmdkdkr-png/emu-ex-plus-alpha     # APK 만들 때만 (무겁다)
git clone https://github.com/rmdkdkr-png/CustumApKS
```

`emu-ex-plus-alpha` 는 몇 GB 다. 코어만 만들 거면 안 받아도 된다.

### 롬과 세이브 놓을 자리

```bash
mkdir -p ~/rom ~/saves
# 롬을 ~/rom/ 에 둔다 (윈도우에서 복사: cp /mnt/c/Users/이름/Downloads/*.ngc ~/rom/)
# 받은 압축을 ~/saves/ 에 푼다
tar xzf svc-savestates.tar.gz  -C ~/saves
tar xzf ss2-savestates.tar.gz  -C ~/saves
```

> 롬과 세이브는 **저장소 폴더 안에 두지 말 것.** 실수로 커밋된다.
> 굳이 안에 둬야 하면 `.gitignore` 에 먼저 넣는다.

---

## 6. 빌드해 보기

### 리눅스 코어

```bash
cd ~/ss2/ss2-sp-core/build
make -f Makefile -j4
#  → mednafen_ngp_libretro.so
```

> ⚠️ **make 가 헤더 의존성을 추적하지 않는다.** `ss2comm_lines.h` 같은 헤더만
> 고쳤다면 `.o` 가 남아 옛 코드가 링크된다. 헤더를 손댔으면 먼저 지운다:
> ```bash
> rm -f ss2comm.o ss2sp.o libretro.o
> ```
> 실제로 이것 때문에 리눅스판만 구버전으로 나간 적이 있다.

### 안드로이드 코어 5종

```bash
~/android-ndk/ndk-build \
  NDK_PROJECT_PATH=$HOME/ss2/ss2-sp-core/build \
  APP_BUILD_SCRIPT=$HOME/ss2/ss2-sp-core/build/jni/Android.mk \
  NDK_APPLICATION_MK=$HOME/ss2/ss2-sp-core/build/jni/Application.mk -j4
#  → build/libs/{arm64-v8a,armeabi-v7a,riscv64,x86,x86_64}/libretro.so
```

> 경로는 **반드시 절대경로**로. 상대경로면 `jni/jni/...` 를 찾다 실패한다.

### APK

```bash
export ANDROID_NDK_PATH=$HOME/android-ndk
export ANDROID_HOME=$HOME/android-sdk
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
export IMAGINE_PATH=$HOME/ss2/emu-ex-plus-alpha/imagine
export EMUFRAMEWORK_PATH=$HOME/ss2/emu-ex-plus-alpha/EmuFramework
export IMAGINE_SDK_PATH=$HOME/ss2/emu-ex-plus-alpha/imagine-sdk
cd ~/ss2/emu-ex-plus-alpha/NGP.emu
make -f android.mk android-apk CONFIG=Release -j$(nproc)
```

서명까지:
```bash
export PATH=$ANDROID_HOME/build-tools/36.0.0:$PATH
IN=build/android/build/outputs/apk/release/NgpEmu-release.apk
zipalign -p -f 4 "$IN" /tmp/aligned.apk
apksigner sign --ks ~/.android/debug.keystore --ks-pass pass:android \
  --key-pass pass:android --out NGPcustumSP.apk /tmp/aligned.apk
```

디버그 키스토어가 없으면 만든다:
```bash
keytool -genkey -v -keystore ~/.android/debug.keystore -storepass android \
  -alias androiddebugkey -keypass android -keyalg RSA -validity 10000 \
  -dname "CN=Android Debug,O=Android,C=US"
```
> 같은 키로 서명해야 기존 설치 위에 업데이트된다. **이 키스토어는 잃어버리면 안 된다.**

---

## 7. 도구 돌려 보기

### SvC 실측기

```bash
cd ~/ss2/ss2-sp-core/tools/svc
gcc -O1 -std=gnu99 -o svcrun svcrun.c -ldl
cp ~/saves/svc_*.st .
python3 probe.py svc_f2.st 3
```
`probe.py` 안의 `CORE`·`ROM` 경로를 본인 것으로 고쳐야 한다.

### SS2 하네스

```bash
cd ~/ss2/ss2-sp-core/tools/harness
gcc -O1 -DSS2SP_RAM_POINTER -DSS2COMM_TEST -I../../src \
    -o promoshot promoshot.c ../../src/ss2comm.c ../../src/ss2sp.c -lm
```
`-DSS2COMM_TEST` 를 빼면 `CPUExRAM` 을 못 찾아 링크가 깨진다.

---

## 8. 제대로 됐는지 확인

```bash
# 코어가 열리고 신원을 제대로 말하는가
cd ~/ss2/ss2-sp-core/src && bash test_flow.sh        # 20종 통과해야 함

# 빌드한 코어 6종이 같은 커밋인가
strings mednafen_ngp_libretro.so | grep "SS2 v0.6"

# 롬 혼입 검사 (커밋 전 습관)
cd ~/ss2/ss2-sp-core
find . \( -name '*.ngc' -o -name '*.ngp' -o -name '*.ngf' -o -name '*.st' \) -not -path './.git/*'
```

---

## 9. Claude Code 를 로컬에서

```bash
npm install -g @anthropic-ai/claude-code
cd ~/ss2/ss2-sp-core
claude
```

클라우드와 다른 점:

- **롬·세이브를 올릴 필요가 없다.** 로컬 파일을 바로 읽는다
- **빌드 결과가 남는다.** 매번 받지 않아도 된다
- 대신 **폰에서 시킬 수 없다.** PC 앞에 있어야 한다
- 인터넷 접근 제약이 없다 (클라우드는 프록시가 일부 사이트를 막는다 — 디시가 그랬다)

---

## 9-1. 두 방이 직접 연락하기 — 되는 길과 안 되는 길 (2026-10-09, 문서 확인)

### 왜 데스크톱 앱에서 열어도 안 되나
- 「커스텀 apk」방은 **클라우드 VM 에서 돈다.** 데스크톱 앱이나 브라우저는 그 방을 보는 창일 뿐이라,
  앱에서 열어도 방이 PC 로 옮겨 오지 않는다 (앱을 닫거나 PC 를 꺼도 방은 계속 돈다).
  기존 클라우드 방을 PC 로 옮기는 기능은 없다 (`claude --teleport` 는 복사본을 터미널에 만드는 것).
- 방끼리 직접 메시지(ListAgents / SendMessage)는 **같은 기계에서 도는 방끼리**가 기본이다.
  컨테이너 ↔ 호스트, WSL ↔ 네이티브 윈도우도 서로 못 본다. 그래서 클라우드 방에서는
  PC 의 방이 「연락 가능한 방 없음」으로 나온다.
- 다른 기계·클라우드 방과의 메시지는 **Remote Control 에 연결된 방**에서만 목록에 뜬다
  (문서: cross-session-messaging). 즉 PC 쪽 방이 Remote Control 을 켜면 클라우드 방을 보고 메시지를 보낼 수 있다.
- 「패치 포팅」방은 Claude Desktop **Cowork 탭** 방이다. Cowork 방은 문서상 peer 목록 대상이 아니다
  (목록 대상: 서브에이전트·팀메이트·로컬 Code 세션·클라우드 세션·Remote Control 세션).

### 되는 길 (문서로 확인된 것)
**A. PC 에 Code 탭 로컬 방을 하나 만들고 Remote Control 을 켠다 → 이 방(클라우드)에 직접 메시지 가능**
1. 그 윈도우 PC 의 Claude Desktop → 위 가운데 **Code** 탭 → `+ New session` (Ctrl+N).
2. 입력창의 환경 드롭다운을 **Local** 로, `Select folder` 로 `CustumApKS` 클론 폴더 선택
   (없으면 아래 「저장소 넷」으로 받는다).
3. 툴바의 노트북 아이콘(Remote Control 스위치)을 켜거나 `/remote-control` 입력.
   (설정 > Claude Code > 「새 세션을 Remote Control 에 연결」을 켜 두면 매번 안 눌러도 된다.)
4. 첫 메시지로 `HANDOFF.md` 0절의 첫 마디를 붙여넣는다. 그 방에서 `/list-agents` 를 치면
   클라우드 방 「커스텀 apk」(`custumapks-a4`)가 떠야 하고, 거기로 메시지를 보내면 이 방이 받는다.
- 요구: 네이티브 윈도우는 Claude Code 2.1.234 이상(데스크톱 앱은 자체 번들 — `/status` 로 확인,
  Help > Check for Updates 로 갱신). Pro/Max/Team/Enterprise 플랜. Remote Control 은 Trusted Devices 가
  켜진 계정이면 기기 등록이 먼저 필요할 수 있다.
- 터미널 대안: PC 터미널에서 `cd CustumApKS && claude remote-control` (서버 모드, 그 창에서는 타이핑 못 함;
  claude.ai/code 와 폰 앱 목록에 PC 아이콘으로 뜬다). 대화형으로 쓰려면 `claude --remote-control "커스텀 apk 로컬"`.

**B. 「패치 포팅」방을 Cowork 가 아니라 Code 탭 로컬 방으로 옮기면 A 와 같은 길로 이 방과 직통**
- Cowork 의 Dispatch 로 Code 탭 세션을 만들거나, Code 탭에서 Local + PocketCore 폴더로 새 방을 열고
  Remote Control 을 켠다. 그 방이 이 방에 먼저 메시지를 보내면 이 방은 답장할 수 있다.

**C. 한 줄 전달 — PC 터미널에서 클라우드 방으로**
```sh
claude auth login                      # 처음 한 번, claude.ai 계정으로
claude -p "전할 말" --cloud session_01GDwDYMfa1F3dPZy4FHQ2Nc
```
- 이 방에 사용자 메시지로 들어온다. 조직 설정 `allow_remote_sessions` 가 켜져 있어야 한다.

### 그 전까지의 통로 (지금 열려 있음)
- **PocketCore PR #2** (https://github.com/rmdkdkr-png/PocketCore/pull/2) — 코어 쪽 계약 문서를 담은 PR.
  댓글이 달리면 「커스텀 apk」방이 구독으로 즉시 받는다. 그쪽 방에 「PR #2 읽고 댓글로 답해」한 줄이면 된다.
- 왜 다른 길이 막혔나: 세션 이름/ID 전송은 Cowork 방이 목록에 안 뜸, Routine 주입은
  「그 방은 자기 컴퓨터에 묶인 작업만 받는다」고 거부, 프로젝트 채팅엔 주소가 없음.

### 저장소 넷
```sh
git clone https://github.com/rmdkdkr-png/ss2-sp-core          # 코어(main 에 프레임 생성 포함)
git clone https://github.com/rmdkdkr-png/emu-ex-plus-alpha    # 앱판(framegen 가지)
git clone https://github.com/rmdkdkr-png/CustumApKS           # 릴리즈·문서(가지 claude/emu-ex-plus-alpha-build-9yqxli)
git clone https://github.com/rmdkdkr-png/PocketCore           # 다른 방의 앱(feat/framegen-art)
```

## 10. 하지 말 것 (지금까지 지킨 선)

1. **롬·세이브스테이트를 저장소·릴리즈·문서에 넣지 않는다.** 커밋 전 위 검사 실행
2. **SNK 그림을 배포물에 넣지 않는다.** 주소표만 싣고 실행 중 유저 롬에서 굽는다
   (릴리즈 글의 스크린샷은 별개 — 관행상 허용, 저작권 고지 한 줄 붙인다)
3. **글꼴 파일(BDF) 자체를 재배포하지 않는다.** 쓰는 글자만 비트맵으로 뽑아 넣는다
4. **한글패치가 적용된 롬을 배포하지 않는다.** 패치 파일만 배포하고
   「원본 롬 + 패치 적용」 경로를 안내한다

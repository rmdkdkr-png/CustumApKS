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

## 10. 하지 말 것 (지금까지 지킨 선)

1. **롬·세이브스테이트를 저장소·릴리즈·문서에 넣지 않는다.** 커밋 전 위 검사 실행
2. **SNK 그림을 배포물에 넣지 않는다.** 주소표만 싣고 실행 중 유저 롬에서 굽는다
   (릴리즈 글의 스크린샷은 별개 — 관행상 허용, 저작권 고지 한 줄 붙인다)
3. **글꼴 파일(BDF) 자체를 재배포하지 않는다.** 쓰는 글자만 비트맵으로 뽑아 넣는다
4. **한글패치가 적용된 롬을 배포하지 않는다.** 패치 파일만 배포하고
   「원본 롬 + 패치 적용」 경로를 안내한다

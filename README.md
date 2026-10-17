# NGPcustumSP

네오지오 포켓 컬러 『**사무라이 쇼다운!2**』 전용 커스텀 에뮬레이터입니다.
한국어 캐릭터 해설, 원버튼 필살기, 양옆 일러스트 기둥을 게임에 얹습니다.

**안드로이드 앱**과 **레트로아크 코어**, 두 가지로 나옵니다. 기능은 같습니다.

> 롬은 들어 있지 않습니다. 본인이 소유한 『사무라이 쇼다운!2』 롬이 있어야 작동합니다.

---

## 무엇을 하는 물건인가

| | |
|---|---|
| 🎙 **한국어 해설** | 15인이 각자 말투로 경기를 읽습니다 — 대사 4,200여 줄. 심판 쿠로코가 판정을 외칩니다 |
| 🏛 **일러스트 기둥** | 화면 좌우에 대전 상대의 카드 대형 일러가 섭니다. 맞으면 흔들리고, 몰리면 붉어지고, KO 나면 흑백이 됩니다 |
| ⚡ **원버튼 필살기** | `623` 같은 커맨드를 버튼 하나로. 어느 기술을 어느 방향에 둘지 게임 안에서 직접 배치합니다 |
| ⏸ **빠른 설정** | 아래+옵션으로 설정창을 엽니다. 열려 있는 동안 게임과 소리가 완전히 멈춥니다 |

일러스트도 초상화도 **배포물에 들어 있지 않습니다.** 코어가 들고 있는 것은 타일 주소표뿐이고,
그림은 실행 중에 **당신의 롬에서 그 자리에서 구워집니다.** 롬이 없으면 아무 그림도 안 나옵니다.

---

## 어느 것을 받나

### 안드로이드 앱 — 이것만 깔면 끝

| 파일 | |
|---|---|
| [`NGPcustumSP-v1.0.2.apk`](release/ss2-v1.0.2/NGPcustumSP-v1.0.2.apk) | 4.7 MB · [릴리즈 노트](release/ss2-v1.0.2/RELEASE_NOTES.md) |

레트로아크를 따로 깔 필요가 없습니다. 스토어판 NGP.emu 와 앱 ID 가 달라
(`com.rmdkdkr.ngpemu.ss2`) 나란히 설치되고 세이브도 겹치지 않습니다.

### 레트로아크 코어 — 이미 레트로아크를 쓰고 있다면

기기에 맞는 파일 **하나만** 받으시면 됩니다.

| 쓰시는 기기 | 파일 |
|---|---|
| **안드로이드 폰·태블릿** (요즘 기기 대부분) | `…-android-arm64-v8a.so` |
| 안드로이드 (오래된 32비트) | `…-android-armeabi-v7a.so` |
| 안드로이드 (에뮬레이터·일부 태블릿) | `…-android-x86_64.so` · `…-android-x86.so` |
| 안드로이드 (RISC-V) | `…-android-riscv64.so` |
| 리눅스 PC · 스팀덱 | `…-linux-x86_64.so` |

넣는 법은 [해설 엔진 저장소](https://github.com/rmdkdkr-png/ss2-sp-core)에 적어 두었습니다.

---

## 조작

### 코어 (레트로아크)

NGPC 는 버튼이 A·B·Option 셋뿐입니다. 여기에 셋을 더합니다.

| 패드 | 하는 일 |
|---|---|
| B (아래) | **A** — 베기 |
| A (오른쪽) | **B** — 발차기 |
| **X** 또는 **R** | **SP** — 원버튼 필살기 |
| **Y** 또는 **L** | **A+B 동시** (뒤를 잡고 누르면 **비오의**) |
| **L2** | 해설자 교대 |
| Start | Option |
| **아래 + Start** | 빠른 설정 열기 / 닫기 |

### 앱

버튼은 전부 EmuEx 키 설정에서 원하는 대로 바꾸실 수 있습니다.
기본 가상 키는 **SP**(원버튼 필살기) · **A+B** · **해설자 교대** · **빠른 설정** 넷입니다.

### 필살기 = SP + 방향

SP 를 그냥 누르면 중립 자리, 방향을 같이 잡으면 그 자리의 기술이 나갑니다.
자리는 일곱입니다 — 기본 · →앞 · ←뒤 · ↓아래 · ↘ · ↙ · 공중.

**빠른 설정 → SP 기술 배치**에서 캐릭터·유파를 고르고, 자리마다 **A 로 기술 목록에서** 고릅니다.
커맨드는 화살표로 보여 줍니다(`↓↘→ + A`). 공중 전용기는 `(공중)` 이 붙습니다.
공중기를 지상 자리에 두면 커맨드 뒤에 `↗+버튼` 을 자동으로 넣어 **저공에서 나갑니다**.

B 는 한 겹씩 돌아갑니다: 기술 고르기 → SP 배치 → 빠른 설정 → 닫기.

---

## 코어 옵션

퀵 메뉴 → **Core Options**.

| 항목 | 기본값 | 값 |
|---|---|---|
| SS2 One-button Specials | 켜짐 | 켜짐 / 꺼짐 |
| SS2 Character Commentary | 켜짐 | 켜짐 / 꺼짐 |
| SS2 Commentary Speaker | 하오마루 | 15인 전원 |
| SS2 Commentary Partner | 켜짐 | 켜짐 / 꺼짐 (두 사람이 주고받는 대사) |
| SS2 Commentary Display | **화면 밖 위** | 위 / 아래 / 화면 안 위 / 화면 안 아래 / 프론트엔드 알림 |
| SS2 Side Art Pillars | 켜짐 | 켜짐 / 꺼짐 |
| Language | english | english / japanese |

기둥과 해설을 어떻게 두느냐에 따라 화면 크기가 바뀝니다 —
전부 켜면 **288×184**, 전부 끄면 **160×152**(원본 그대로)입니다.

---

## 다른 게임에는 아무 일도 없습니다

**앱**은 『사무라이 쇼다운!2』 전용으로 잠겨 있습니다. 다른 롬은 열리지 않습니다.
범용 에뮬레이터로 쓰여 원작자의 유료 앱을 갉아먹지 않으려는 것입니다.

**코어**는 그런 잠금이 없습니다. 사쇼!2 가 아니면 SS2 층이 잠자코 있고,
평범한 Beetle NeoPop 코어로 그대로 쓰실 수 있습니다.

---

## 저장소 지도

| 저장소 | 무엇 |
|---|---|
| **CustumApKS** (여기) | 릴리즈·문서 — APK, 릴리즈 노트, [변경 이력](handoff/CHANGELOG.md), [배포 조사](handoff/DISTRIBUTION.md) |
| [ss2-sp-core](https://github.com/rmdkdkr-png/ss2-sp-core) | 해설·필살기 엔진 + 레트로아크 코어 전체 소스 |
| [emu-ex-plus-alpha](https://github.com/rmdkdkr-png/emu-ex-plus-alpha) | 안드로이드 앱 포크 (NGP.emu 개조) |
| [KrPatch](https://github.com/rmdkdkr-png/KrPatch) | 한글 번역 패치 v0.99b |

---

## 저작권·라이선스

이 프로젝트는 **GPL v3**(emu-ex-plus-alpha)·**GPL v2**(Mednafen NGP 코어)를 따르는
자유 소프트웨어 개조판입니다. 위 저장소들이 곧 대응 소스입니다.

- 바탕: Robert Broglia 의 [emu-ex-plus-alpha](https://github.com/Rakashazi/emu-ex-plus-alpha)(NGP.emu) ·
  [Mednafen](https://mednafen.github.io/) NGP 코어 · [Beetle NeoPop](https://github.com/libretro/beetle-ngp-libretro)
- 글꼴: [갈무리(Galmuri)](https://github.com/quiple/galmuri) © Lee Minseo — SIL Open Font License 1.1.
  대사에 실제로 쓰이는 글자만 비트맵으로 뽑아 담았고, 글꼴 파일 자체는 재배포하지 않습니다
- 한글 번역 패치 v0.99b 는 **이 프로젝트 제작자 본인의 작업**입니다.
  패치는 [KrPatch](https://github.com/rmdkdkr-png/KrPatch) 에서 받아 본인 소유의 원본 롬에
  직접 적용하십시오 — 패치가 적용된 롬 자체는 배포하지 않습니다
- 게임 『사무라이 쇼다운!2』의 그래픽·음악·상표는 **SNK CORPORATION** 소유입니다.
  본 프로젝트는 비공식 팬 제작물이며 SNK · Robert Broglia 와 무관합니다

원작 NGP.emu 와 NEO.emu 는 Robert Broglia 가 스토어에서 파는 앱입니다.
그 앱들을 대체하려는 물건이 아니고, 이름도 일부러 다르게 붙였습니다.

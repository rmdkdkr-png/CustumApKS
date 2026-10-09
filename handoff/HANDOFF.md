# 인수인계 — 새 방에서 이어받기

2026-08-26 기준(아래 본문). **2026-10-09 추가분은 바로 아래 「0-1」에 있다.**
새 세션·새 계정에서 이 문서부터 읽으면 바로 이어갈 수 있다.

---

## 0-1. 2026-10-09 추가 — 프레임 생성(120Hz) · 그 사이 다른 방이 한 일

### 그 사이(8/29~9/8) 다른 세션이 한 일 — main 에 +76 커밋
- `ss2-sp-core` main: 해설 음성/더빙(CAST_v4), 대사 재작성 v3/v4, **SvC 원버튼 구현**(0x092C bit7 페이싱),
  **9/7 유저 지시로 코어에서 기둥·해설 계통 폐기**(0d6bd17, d17fcc5 — 옵션표·오버레이에서 뺌, 코드는 남아 있음).
- 가지 `svc-core`(9/8, main 대비 +124/-49): 라스트블레이드 전캐릭 6320/6320 + KOF R-2 초필 "SP 4.06", PR #1·#2 병합.
  merge-base 35efe91(8/28) → **기둥 폐기 커밋을 안 담고 있다.** `sp-supers-followups`, `lb-allchars` 도 있다.
- `emu-ex-plus-alpha` master 26d905f0: 롬 게이트 SS2→SS2+SvC, SVC 모던 조작.
- 미해결: svc-core 와 main 의 합치기, 127식 팔청 안 나감, SvC P1 HP 오프셋.

### 이번(10/9) 작업 — 프레임 생성
유저 요청: 「프레임 제네레이션, 내 폴드6에서 120Hz 로 되게」 + 「DLSS 같은 거 어떻게 안 되나」.

| 저장소 | 브랜치 | 커밋 | 내용 |
|---|---|---|---|
| `ss2-sp-core` | **main** (framegen 을 fast-forward 로 병합, 10/9) | ce62f19 (소스 a11e3ad·5a8000d·a8499f6·83c909f·a7e6585·4e225a0, 코어 5종 재빌드 포함; 10/9 저녁 호출 속도 차단을 10·20·40초 재시도로, 복원은 옵션 값 변경 때만) | `src/ss2fg.c/.h` 캡처·합성, libretro 배관, 옵션 2개, 검증 하네스 2개, `docs/프레임생성.md` |
| `emu-ex-plus-alpha` | **`framegen`** (master 에서 가지) | 6f77174 | EmuFramework 빈 vsync 슬롯 훅 `EmuSystem::interFrame`, NGP.emu 예측 합성, 옵션 「프레임 생성」, 1.5.85-SS2-1.1.0 → `release/ss2-v1.1.0/` APK |
| `CustumApKS` | `claude/emu-ex-plus-alpha-build-9yqxli` | 이 커밋 | CHANGELOG 1.1.0, 이 절 |

- 방식: 픽셀을 섞지 않는다. K2GE 스프라이트표·스크롤 레지스터를 스캔라인별로 캡처해 위치만 반 옮긴
  자리에 **같은 타일**을 원본 렌더러 규칙으로 다시 그린다. 기본은 **예측**(상태 저장→한 프레임 미리→합성→
  복원, 추가 지연 0). 세부·설정 절차·DLSS 답은 코어 `docs/프레임생성.md`.
- 검증은 롬 없이(합성 상태·합성 롬) 1,546 + 55 건 통과. **실제 롬 화면 실측은 아직** — 롬을 올려
  `tools/svc/svcrun.c` 류 하네스로 돌리거나 폰에서 직접 봐야 한다. 폴백(60Hz 로 보이는 순간)이 잦으면
  `SS2FG_SPR_MAX_STEP`(24)·더티 정책(`ss2fg.c`)을 손본다.
- RetroArch 쪽: 안정판엔 「Screen Resolution」120Hz 모드 항목이 없다(2026-09-26 이후 nightly). 안정판이면
  Threaded Video 끄고 Vertical Refresh Rate 120 을 직접. 삼성 게임 부스터가 60Hz 로 묶을 수 있다.
- 앱 쪽: 「프레임 타이밍 옵션 → 화면 주사율 덮어쓰기 = 120Hz」로 둬야 빈 슬롯이 생긴다(기본은 60Hz 요청).
- 코어 `framegen` → **main 에 병합 완료**(fast-forward, 충돌 0). **svc-core 에는 합치지 않는다** — svc-core 는 main 과 원래
  갈라져 있어(+124/-49) 시험 병합 시 13개 파일 충돌(svcsp.c·svcsp_moves.h·ss2sp.patch·SVC_MEMO.md 등, framegen 탓 아님).
  svc-core 에 프레임 생성이 필요하면 main 과 먼저 맞추거나 ss2fg.c + gfx.c·mem.c·system.c·sound.cpp 의 캡처 지점만 직접 이식.
- **PocketCore 앱**(패치 포팅 프로젝트 쪽, 별도 저장소 — native.c·framegen.c·Java): 사무쇼2는 `libretro_ss2.so`, 나머지는 svc 코어.
  그쪽 PR #1(feat/framegen-art → main, 시험판 APK 자동 빌드 `build-test-apk.yml` → 릴리즈 태그 `fgtest`)이 그쪽 창구.
  이쪽 PR #2(계약 문서, 아직 열림)·**PR #3(jniLibs 의 libretro_ss2.so 세 ABI 를 main ce62f19 빌드로 교체) — 10/9 22:56Z 병합됨(42e4b8b)**.
  병합 뒤 그쪽이 9a4288c(설정 화면에 코어 옵션 ngp_framegen 자동/켬/끔·ngp_framegen_mode 예측/보간 노출)를 더 올렸고
  Actions 가 시험판을 다시 구웠다(run 38002186680 성공, 23:01Z) → 릴리즈 `fgtest` 의
  https://github.com/rmdkdkr-png/PocketCore/releases/download/fgtest/PocketCore-fgtest.apk 가 코어 4e225a0 을 담고 있다
  (패키지 com.dudu.pocketcore.fgtest, 정식판과 나란히 설치, 디버그 서명). 폴드6 실기 확인은 이 APK 로.
  PR #1 의 지적(차단이 영구)으로 코어가 83c909f·a7e6585·4e225a0 으로 바뀌었다.
  코어가 120.5 를 선언하면 앱의 픽셀 보간은 저절로 꺼져 이중 보간은 없다. 단 PocketCore 는 GET_TARGET_REFRESH_RATE 에
  답하지 않아 코어 옵션 「자동」이 안 켜진다 → 코어 옵션을 「켬」으로 두거나 앱이 실측 주사율로 답하게 고친다(그쪽이 몇 줄이면 된다고 함).
  역할 분담: 사무쇼2 = 코어 방식(레지스터 보간·예측 지연 0), 그 외 게임 = 앱의 픽셀 보간.
- 이 방의 빌드 환경: NDK r27(코어), 앱은 `emu-ex-plus-alpha/BUILD.md` 그대로(NDK r30-beta1, CMake 4.3.4).
  `makeAll-android-arm64.sh` 만 돌리면 `android.sh config` 가 armv7 SDK 를 못 찾아 죽는다 — **전 ABI
  `makeAll-android.sh`** 를 돌려야 한다.

---

---

## 0. 새 방에 붙여넣을 첫 마디

> NGPcustumSP 프로젝트를 이어받는다. 저장소 네 개(ss2-sp-core, emu-ex-plus-alpha,
> CustumApKS, PocketCore)를 받고 `CustumApKS/handoff/HANDOFF.md` 와 `LOCAL_SETUP.md` 를 먼저 읽어라.
> 롬과 세이브스테이트는 내가 따로 갖고 있다. 저장소에는 절대 넣지 마라.
> PocketCore 를 만지는 다른 방과는 PocketCore PR #1(그쪽)·#2·#3(이쪽) 댓글로 주고받는다(LOCAL_SETUP 9-1).
> 네가 PC 의 로컬 방이면 Remote Control 을 켜고 `/list-agents` 로 클라우드 방 「커스텀 apk」를 찾아 직접 말해도 된다.

---

## 1. 이 프로젝트가 뭔가

네오지오 포켓 컬러 『사무라이 쇼다운!2』 전용 커스텀 에뮬레이터 **NGPcustumSP**.
게임에 세 가지를 얹는다.

- **한국어 캐릭터 해설** — 15인 + 심판 쿠로코, 대사 4,232줄
- **원버튼 필살기(SP)** — 커맨드를 버튼 하나로
- **양옆 일러스트 기둥** — 상대 카드 일러 + 전황 연출

**안드로이드 앱**과 **레트로아크 코어** 두 갈래로 나온다. 같은 엔진(`ss2comm.c`)을 쓴다.

한글패치 v0.99b 는 **제작자 본인 저작**이다 (repo: rmdkdkr-png/KrPatch).

---

## 2. 저장소 (전부 푸시 완료)

| 저장소 | 브랜치 | 커밋 | 무엇 |
|---|---|---|---|
| `ss2-sp-core` | main | `517b9ca` | 해설·SP 엔진 + libretro 코어 전체 + 도구 |
| `emu-ex-plus-alpha` | master | `049b4c9` | 안드로이드 앱 포크 (NGP.emu 개조) |
| `CustumApKS` | `claude/emu-ex-plus-alpha-build-9yqxli` | `a558791` | 릴리즈·문서 |

> `CustumApKS` 는 **main 이 아니라 저 브랜치**가 최신이다.

### 읽어야 할 문서
| 문서 | 내용 |
|---|---|
| `handoff/LOCAL_SETUP.md` | 로컬 환경 구축 (WSL2 등), 빌드, 함정 |
| `handoff/BUILD.md` | APK 빌드 전 과정 실측 기록 |
| `handoff/CHANGELOG.md` | 버전별 변경 이력 |
| `handoff/DISTRIBUTION.md` | 배포 조사 — GPL·상표·저작권 판단 근거 |
| `handoff/자료의자리.md` | 자료가 어디 있는지 지도 |
| `handoff/SVC기획.md` | 다음 게임(SvC) 기획 |
| `handoff/배포문안/` | 릴리즈 본문·커뮤니티 글 완성본 |
| `ss2-sp-core/tools/README.md` | 검증 도구 13종 설명 |

---

## 3. 지금 상태

### 나온 것
- **앱 v1.0.2** — `release/ss2-v1.0.2/NGPcustumSP-v1.0.2.apk` (서명 완료)
- **코어 6종** — 안드로이드 5 ABI + 리눅스 x86_64, 전부 커밋 `493cd27` 에서 빌드

### 유저가 손으로 해야 남은 것
- [ ] GitHub 릴리즈 게시 — 앱 `NGPcustumSP-v1.0.2`, 코어 `core-v1.0.2`
      (본문은 `handoff/배포문안/` 에 완성돼 있음)
- [ ] 디시 글 게시 (`배포문안/DC글.md`, 사진 6장 첨부)
- [ ] 폰에서 간다라전 들어가 기둥 확인

### 마지막 판에서 고친 것
- **간다라 인식** — 보스 플래그를 믿던 게 원인. 같은 간다라전이 플래그 1/0 둘 다로 온다.
  개체 19 + 스테이지 7 두 값만으로 가르게 바꿨다
- 「개체 8 + 보스기 = 간다라」 오독 제거 — 그건 직전 장 스테이지 6 보스전이었다
- 빌드 버전 스탬프가 호출 셸의 작업 디렉터리를 따라가던 문제 (`git -C` 로 고정)

### 되돌린 것 (주의)
`493cd27` 에서 **「다른 게임에서 SS2 층 끄기」를 revert 했다** (유저 지시).
지금 코어는 사쇼!2 가 아닌 롬을 띄워도 좌우에 빈 기둥이 서고 288×184 로 잡힌다.
리드미·릴리즈 노트의 "사쇼!2 가 아니면 잠자코 있습니다" 문장은 **현재 사실이 아니다.**
되살리려면 커밋 `62bba02` 를 보면 된다 (롬 헤더 `SAMURAI2` 판별).

---

## 4. 다음 게임 — SNK vs Capcom MotM

정찰이 상당히 진행됐다. 상세는 `ss2-sp-core/tools/svc/SVC_MEMO.md`.

### 확인된 핵심
- **커맨드 주입으로 필살기가 나온다.** SS2 방식이 통한다
- **가로채기 문제가 없다** — SS2 의 램 리셋 트릭이 필요 없다
- **입력 규칙**: 마지막 방향을 버튼보다 먼저 잡고, 방향 간격 2~4프레임
- **ABLE 은 이 롬에 없다** — 유파 셋 전부에서 간이입력 불가. 정식 커맨드만 먹는다
  (FAQ 의 ABLE 열은 이 판본과 무관하니 쓰지 말 것)

### 램 오프셋 (SYSTEM_RAM 기준)
| 오프셋 | 뜻 |
|---|---|
| `0x08A0` | P1 캐릭터 ID (쿄0 … 가일17) |
| `0x08BE` | P1 유파 (반격0 / 균형1 / 속공2) |
| `0x08CF` | P2 체력 (최대 48) |
| `0x08EE` | 라운드 타이머 |
| `0x092E` / `0x0934` | P1 / P2 화면 X — **방향은 이 둘 비교로 계산** |
| `0x0930` | P1 Y (지상 128, 점프 정점 86) |
| `0x09AD` | P1 애니메이션 뱅크 |
| `0x0C7E` | P1 애니 카운터 — **0 리셋 = 새 동작 시작 (발동 판정)** |

### 도구
`tools/svc/svcrun.c` (입력 주입·램 관찰·상태 저장) + `probe.py` (커맨드 84종 전수 실측).
18명 전원 결과가 `SWEEP2.txt` 에 있고 유저 제공 가이드와 어긋난 항목이 없었다.

### 다음 할 일
1. **쿄 하나로 SP 버튼을 끝까지 붙여 본다** — 재료는 다 모였다
2. 되면 나머지 17명 기술표를 채운다 (`SWEEP2.txt` 가 출발점)
3. 엔진은 `ss2sp.c` 를 거의 그대로 쓴다 — 리셋 트릭 빼고 간격 2~4 로

숨김 8명은 미해금이라 못 잡았다 (해금하려면 Versus 포인트 필요).

---

## 5. 저장소에 없는 것 (유저가 보관)

| | 왜 |
|---|---|
| 롬 (사쇼2 한글판, SvC 한글판 v17.2, 원본) | 저작물 |
| 세이브스테이트 537개 | 롬 파생물 |
| 캡처 이미지 (홍보 9장 등) | SNK 아트 |
| 서명 키스토어 `~/.android/debug.keystore` | **잃으면 업데이트 설치 불가** |

세이브는 압축으로 전달됨: `ss2-savestates.tar.gz`, `svc-savestates.tar.gz`, `ss2-captures.tar.gz`

---

## 6. 지켜 온 선 (계속 지킬 것)

1. **롬·세이브스테이트를 저장소·릴리즈·문서에 넣지 않는다.** 커밋 전 검사:
   ```bash
   find . \( -name '*.ngc' -o -name '*.ngp' -o -name '*.ngf' -o -name '*.st' \) -not -path './.git/*'
   ```
2. **SNK 그림을 배포물에 넣지 않는다.** 타일 주소표만 싣고 실행 중 유저 롬에서 굽는다
3. **글꼴 파일(BDF) 자체를 재배포하지 않는다.** 쓰는 글자만 비트맵으로
4. **한글패치가 적용된 롬을 배포하지 않는다.** 패치 파일만
5. 앱은 **사쇼2 전용 잠금** 유지 — 범용 에뮬이 되면 원작자 유료 앱과 부딪친다
6. 커밋 트레일러에 모델 이름을 넣지 않는다

### 해설 문서에 쓰지 않는 것 (설정 오류·미확인)
쥬베이의 딸 · 한조의 「카게로」 · 갈포드=한조의 제자 · 파피 성별 · 쥬베이 눈 잃은 경위 ·
엔딩 내용 · 미코토 · 유다 · **나코루루의 레라/이중인격/나찰 말투**
(기술명 「레라 무츠베」·「레라 오 치키리」는 공식 표기라 유지)

---

## 7. 빌드 함정 셋 (실제로 밟았음)

1. **`make` 가 헤더 의존성을 추적하지 않는다.** 헤더만 고치면 옛 `.o` 가 링크된다.
   → `rm -f build/ss2comm.o build/ss2sp.o build/libretro.o` 후 재빌드
2. **`ndk-build` 는 절대경로 필수.** 상대경로면 `jni/jni/...` 를 찾다 실패
3. **서명 키스토어를 잃으면** 기존 설치 위에 업데이트가 안 된다

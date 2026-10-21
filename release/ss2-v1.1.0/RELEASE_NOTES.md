# NGPcustumSP v1.1.0 — 프레임 생성 (120Hz)

60fps 게임을 120Hz 화면에 맞춰 **중간 프레임을 합성**합니다. 갤럭시 Z 폴드6 같은 120Hz 폰에서
캐릭터·배경의 움직임이 두 배 촘촘해집니다.

## 어떻게 만드나
픽셀을 섞지 않습니다. 그래픽 칩(K2GE)의 스프라이트표와 스크롤 레지스터를 두 프레임에서 캡처해,
위치만 반 옮긴 자리에 **같은 타일을 원본 렌더러와 같은 규칙으로 다시 그립니다.** 그래서 픽셀아트가
번지거나 고스트가 생기지 않습니다. 추가 지연은 없습니다 — 상태를 저장한 채 다음 프레임을 미리 돌려
현재↔다음 중간을 그리고 되돌리는 「예측」방식(런어헤드와 같은 원리)입니다.

## 켜는 법 (앱)
1. 시스템 옵션 → **프레임 생성 (120Hz)** = 켬 (기본 켬)
2. **프레임 타이밍 옵션 → 화면 주사율 덮어쓰기 = 120Hz** ← 이걸 두어야 폰이 120Hz 로 돌고 빈 슬롯이 생깁니다
3. 삼성 설정 → 디스플레이 → 모션 부드럽게 = 적응형. 게임 부스터가 60Hz 로 묶으면 그 제한을 풉니다

합성하지 않는 순간(그때만 60Hz 와 같음): 표시 도중 스프라이트표를 고쳐 쓴 프레임, 24px 넘는 점프·
32px 넘는 스크롤 점프(순간이동·장면 전환), 타일이 바뀐 조각(같은 그룹의 다른 조각이 한 방향이면 같이 이동).

## 레트로아크 코어판
같은 기능이 코어에도 있습니다 — `ss2-sp-core` 가지 `framegen`, `docs/프레임생성.md` 에 RetroArch
안드로이드 120Hz 설정 절차(Threaded Video 끄기 · Vertical Refresh Rate 120 · 런어헤드 끄기)가 있습니다.

## 판올림
- versionName `1.5.85-SS2-1.1.0` · versionCode 16010593 · 앱 소스 가지 `framegen` (6f77174)
- 전체 이력: `handoff/CHANGELOG.md`

## 설치
- **롬은 포함되어 있지 않습니다.** 본인 소유의 롬이 있어야 작동합니다
- v1.0.x 위에 업데이트로 설치됩니다. 설정과 세이브는 그대로 유지됩니다
- 스토어판 NGP.emu 와 나란히 설치됩니다 (별도 앱 ID `com.rmdkdkr.ngpemu.ss2`)

## 저작권·라이선스 고지
- 본 앱은 **GPL v3**(emu-ex-plus-alpha)·**GPL v2**(Mednafen NGP 코어)를 따르는
  자유 소프트웨어 개조판입니다. 전체 소스:
  - 앱: https://github.com/rmdkdkr-png/emu-ex-plus-alpha
  - 해설 엔진·코어: https://github.com/rmdkdkr-png/ss2-sp-core
  - 릴리즈·문서: https://github.com/rmdkdkr-png/CustumApKS
- 글꼴 Galmuri © Lee Minseo — SIL Open Font License 1.1
- 게임 『사무라이 쇼다운!2』『SNK vs. Capcom』의 그래픽·음악·상표는 **SNK** 소유입니다.
  본 앱은 팬 프로젝트이며 SNK·Robert Broglia 와 무관합니다
- 한글 번역 패치는 **이 프로젝트 제작자 본인의 작업**입니다 —
  패치는 https://github.com/rmdkdkr-png/KrPatch 에서 받아 본인 소유의 원본 롬에
  직접 적용하세요 (패치가 적용된 롬 자체는 배포하지 않습니다)

■ 올리는 자리
  https://github.com/rmdkdkr-png/CustumApKS/releases/new

■ 채울 칸
  Tag        : NGPcustumSP-v1.0.2
               ※ 입력하면 아래에 뜨는 "Create new tag: … on publish" 줄을 **꼭 탭**하세요.
                 안 누르면 발행할 때 "tag name can't be blank" 로 막힙니다.
  Target     : claude/emu-ex-plus-alpha-build-9yqxli
  Title      : NGPcustumSP v1.0.2 — 간다라 인식 정정
  첨부       : release/ss2-v1.0.2/NGPcustumSP-v1.0.2.apk
  체크박스   : "Set as the latest release" 켜기

■ 본문 — 아래 줄부터 전부 복사
────────────────────────────────────────────────────────────

네오지오 포켓 컬러 『사무라이 쇼다운!2』 전용 커스텀 에뮬레이터입니다.
**v1.0.1 의 버그 수정판이며, 기능 추가는 없습니다.**

## 고친 것

### 🗿 간다라를 못 알아보던 문제

간다라전인데 기둥에 엉뚱한 그림이 서고, 해설도 간다라로 말하지 않던 문제를 고쳤습니다.

상대를 가릴 때 **보스 플래그**를 보고 있었는데, 같은 간다라전이 플래그 1 로도 0 으로도
들어온다는 것이 제보해 주신 세이브로 드러났습니다. 그 14장은 전부 플래그가 0 이라
하나도 걸리지 않았습니다. 이제 **개체 번호와 스테이지 두 값만으로** 가릅니다 —
실측 세이브 23장을 대조해 보니 이 조합은 간다라전에서만 나옵니다.

### ⚔ 아수라 보스전을 간다라로 오인하던 문제

같은 판별표에 있던 「개체 8 + 보스 플래그 = 간다라」 규칙이 오독이었습니다.
그 판은 **직전 장(스테이지 6)의 보스전**이고, 간다라는 그 다음 장에 나옵니다.
이제 로스터대로 제 이름을 부릅니다.

## v1.0.1 에서 들어온 것 (그대로 있습니다)

- **일러스트 기둥** — 화면 좌우에 상대의 카드 대형 일러가 섭니다.
  맞으면 흔들리고, 강타는 하얗게 번쩍이고, 몰리면 붉어지고, KO 나면 흑백이 됩니다
- **SP 기술 배치** — 빠른 설정에서 캐릭터·유파를 고르고 7슬롯마다 기술을 직접 배치합니다.
  커맨드는 화살표 표기(↓↘→+A), 공중 전용기를 지상 슬롯에 두면 저공에서 나갑니다
- **빠른 설정 = 일시정지** — 창이 열려 있는 동안 게임과 소리가 완전히 멈춥니다
- **한국어 해설 15인 + 심판 쿠로코** — 대사 4,200여 줄
- **SS2 전용 잠금** — 다른 롬은 열리지 않습니다

## 판올림

- versionName `1.5.85-SS2-1.0.2` · versionCode 16010592 · 해설 엔진 SS2comm v1.0.2
- SHA-256: `668c38168ec281c2bfbd5fc807614d43d22ffca0672207ee475eab6e7fbd2099`
- 전체 이력: [handoff/CHANGELOG.md](https://github.com/rmdkdkr-png/CustumApKS/blob/claude/emu-ex-plus-alpha-build-9yqxli/handoff/CHANGELOG.md)

## 설치

- **롬은 포함되어 있지 않습니다.** 본인 소유의 사무라이 쇼다운!2 롬이 있어야 작동합니다
- v1.0.1 위에 그대로 업데이트됩니다. 설정과 세이브는 유지됩니다
- 스토어판 NGP.emu 와 나란히 설치됩니다 (별도 앱 ID `com.rmdkdkr.ngpemu.ss2`)
- 레트로아크를 쓰신다면 앱 대신 [코어판](https://github.com/rmdkdkr-png/ss2-sp-core/releases)도 있습니다

## 저작권·라이선스 고지

본 앱은 **GPL v3**(emu-ex-plus-alpha)·**GPL v2**(Mednafen NGP 코어)를 따르는
자유 소프트웨어 개조판입니다. 전체 소스:

- 앱: https://github.com/rmdkdkr-png/emu-ex-plus-alpha
- 해설 엔진: https://github.com/rmdkdkr-png/ss2-sp-core
- 릴리즈·문서: https://github.com/rmdkdkr-png/CustumApKS

바탕이 된 NGP.emu 는 Robert Broglia 의 저작물이며, 원작 NGP.emu·NEO.emu 는
그분이 스토어에서 파는 앱입니다. 이 앱은 그 앱들을 대체하려는 물건이 아니고,
이름도 일부러 다르게 붙였으며, 사쇼!2 롬이 아니면 아예 열리지 않도록 잠가 두었습니다.

- 글꼴 Galmuri © Lee Minseo — SIL Open Font License 1.1
- 게임 『사무라이 쇼다운!2』의 그래픽·음악·상표는 **SNK** 소유입니다.
  본 앱은 팬 프로젝트이며 SNK·Robert Broglia 와 무관합니다
- **일러스트와 초상화는 앱에 들어 있지 않습니다.** 앱은 타일 주소표만 들고 있고,
  그림은 실행 중 여러분의 롬에서 그 자리에서 그려집니다
- 한글 번역 패치(v0.99b)는 **이 프로젝트 제작자 본인의 작업**입니다 —
  패치는 https://github.com/rmdkdkr-png/KrPatch 에서 받아 본인 소유의 원본 롬에
  직접 적용하세요 (패치가 적용된 롬 자체는 배포하지 않습니다)

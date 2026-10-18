# 168 설계 — 리그 166 묶음 10가지 (나중에 · 게임 안 메뉴 · «리그라 안 돼요» 없애기 · 2P색 · 커스텀 컬러 · 캐릭터 바꾸기 순서 · 연습 순서 · 나/상대 구분 · 치트 알약 · 경기 중 설정)

기준 코드: **up164 = c5b26ba**(내부 164 = 163 `8e0a1a4` 앱 코드 + 코어만 바꿈). `app/src/main` 은 두 커밋이 같다(`git diff --stat 8e0a1a4 c5b26ba` = jniLibs 3개 + `tools/core_patches/zzzzz_fg_walk3.patch` 뿐 — 확인함).
그래서 아래 `파일:줄` 은 모두 참고 트리 `scratchpad/w160`(8e0a1a4) 기준이고 c5b26ba 에서도 같은 줄이다. 코드는 한 줄도 안 고쳤다(읽기 설계).
`java/...` = `app/src/main/java/com/dudu/pocketcore/`, `cpp/...` = `app/src/main/cpp/`.

진행 중(손대지 않음): `w165`(branch w165-ship, 커밋 안 된 고침 — EmuActivity 208줄 · LeagueMenu 23 · LgmPages 68 · docs/157_contract 30),
`w165fx`(branch w165-fx, 커밋 3개 `378d980 → ff36649 → 5e33641` — look/league/slash/vpanel native + Java 소량). u166 설계(치트 바 칸·프레임 표시·대미지)는 아직 코드 없음.

## 0. 유저 요청 → 결론 한눈에

| # | 요청(원문) | 결론(새 동작) | 주 파일 |
|---|---|---|---|
| 1 | «나중에로 나오고 나면 봐지는 순위표랑 홈페이지 창은 빼자» | «나중에» = 체크포인트 저장 → **게임 타이틀(리그 켠 채)**. 게임 흐름 어디서도 LeagueActivity 로 안 나감(런처 카드에서만) | EmuActivity · MenuModel · LgmPages |
| 2 | «내부 메뉴를 통해 순위표 확인, 리그 메뉴 접근 및 시즌 초기화도 되도록» | 157-B «대기» 칼집(타이틀 OPTION·멈춤 바 «리그 메뉴») + 서랍 4탭(순위·전적·**리그**·설정). 리그 탭 = 시즌·새 시즌·처음부터·규칙·보류/무효·내 캐릭터 | LeagueMenu · MenuModel · LgmPages · EmuActivity · League |
| 3 | «리그 상태라 안 돼요는 내가 안 보고 싶거든» + 3b «저장 불러오기만 안 되게, 리셋은 리그 상태 저장 후 타이틀로» | 리그 판에선 저장·불러오기·슬롯 칸을 **숨김**(눌러도 조용히 아무 일 없음). 리셋 = 1번과 같은 «경기 저장 → 타이틀». 설정·치트·그 밖은 다 됨. «리그라…» 토스트·창 글 전부 없앰 | EmuActivity · PadView · LaunchSheet · Cheats |
| 4 | «2P 컬러 좀 다 빼 주시고» | **w165fx 가 거의 다 함**(B=결정(보통 색), 2P색 번호 건너뜀, b2p 기록 무시). 남은 것 점검표만 · 게임이 CPU 거울전에 주는 2P 팔레트는 그대로 | (w165fx) |
| 5 | «커스텀 컬러 시 나찰 컬러 수라 컬러 선택 시 바뀌지 않도록» | 프리셋 색을 검질과 무관하게(캐릭터 고르기 미리보기 = 수라 판 색이 곧 그 색). 내 색 1·2 는 이미 공통 | look_gen.py → look_tab.h · look.c |
| 6 | «캐릭터 변경 시 변경 선택 후 상대를 결정해라 리그 중» | «새 캐릭터»·첫 판 = **내 캐릭터만 고르는 판(상대 없음)** → 고른 걸 남김 → 그다음 «상대 찾는 중» → 자동 진행 → VS → 경기 | league.c · EmuActivity |
| 7 | «연습 모드 시 내 캐릭터 수라나찰 선택 후 상대 캐릭터 선택하게» | 연습 = 내 캐릭터 → **게임 검질 고르기 화면에서 내 검질** → (B 로 되돌아와) 상대 선택 → 내 캐릭터·검질은 자동 확정 → 카드 | league.c · look.c(소폭) · EmuActivity |
| 8 | «나랑 상대 캐릭터 선택 자체가 구분이 안 가니 구분 가게 해라» | 머리말 «내 캐릭터» / «상대 선택»(빨강) · 문양 칸 빨간 «상대» 도장 · 상대 화면 들어갈 때 머리말 3번 깜빡 · 띠 ①②③ | league.c · hub_glyphs.h · vpanel.c |
| 9 | «치트 버튼 추가해 줘 화면에, 리그 때도 쓸 수 있게» | OPTION 같은 **«치트» 알약**(패드) → 치트 창 바로. 리그에서도 먹음 · 그 판은 기록에 «치트» · `rankedKnobWhy`/규칙 검사는 치트가 설명하는 것만 면제 | PadView · LaunchSheet · cheat.c · League · EmuActivity |
| 10 | «리그 경기 불러오기가 되는데 왜 그게 안 됨?»(경기 중 설정) | 리그에서 설정 창 열림. 바로 먹는 것(화면·코어 옵션·치트)은 닫을 때, «적용하고 이어하기»는 **체크포인트 → 리그 판 다시 올림 → 그 자리부터**. 언어는 그 경기 판으로 고정(경기 끝나면 새 언어) | EmuActivity · League |

1·3b·10·대기 메뉴는 같은 기계 하나(§A «멈춘 경기»)를 쓴다. 6·7·8 은 고르기 화면(league.c 허브)을 같이 고친다.

---

## A. 공통 기계 — 멈춘 경기(체크포인트로 멈추고 타이틀로 · 게임 안에서 이어 하기)

### A-1. 지금
- 체크포인트 쓰기 `EmuActivity.java:1231-1238 leagueSaveCkpt()` (임시 파일 → 이름 바꿈, GL 스레드).
- 게임 안에서 «이어 하기»는 **허브를 새로 켤 때만** 된다: `hubStart :1894-1897` — `League.openMatch()` 가 준비가 아니면 `leagueId = …; leagueStart()` → `leagueStart :1109-1194` 가 체크포인트를 불러(`:1129-1142`, 한 번 쓰면 지움) `LEAGUE_FROM_CKPT` 로 무장. 허브는 타이틀 상태인 채 싸운다(`:1957` 주석).
- 그래서 지금 «나중에»는 LeagueActivity 로 나가 거기서 «멈춘 경기 이어서 하기» → 허브를 새로 여는 길밖에 없다.

### A-2. 새 함수 (EmuActivity)
```java
/** 168: 점수가 걸린 경기를 체크포인트로 멈추고 타이틀로(리그는 켠 채 — A 로 이어서). 경기 밖이면 그냥 타이틀로.
 *  결판이 이미 섰으면 정산 길(poll → 결판 메뉴). 저장 실패면 경기를 계속(토스트 한 줄 — 저장소 문제, 리그 탓 글 아님) */
private void leagueSuspend(final String why, final Runnable after) {
    if (!leagueHub) { /* 옛 한 판(EXTRA_LEAGUE — 지금 안 씀): 예전처럼 체크포인트 → leagueExit(null) */ ... return; }
    if (leagueId == null || !leagueArmed || leagueDone) { closeOverlaysForTitle(); hubReturn(-1); if (after != null) after.run(); return; }
    leagueSyncStarted();
    if (!leagueStarted) { hubReturn(-1); if (after != null) after.run(); return; }        /* 대진 전 — 준비 기록은 hubReturn 이 무효로(점수 없음) */
    if (leagueSettleNow()) return;                                                       /* 결판 프레임이 이미 — poll 이 결과로 */
    leagueChoosing = true;
    Emu.nativeSetPaused(true);
    final String id = leagueId;
    gl.queueEvent(() -> {
        final boolean ok = leagueSaveCkpt();
        h.post(() -> {
            leagueChoosing = false;
            if (leagueDone || !id.equals(leagueId)) return;
            if (!ok) { toast("저장하지 못했어요 — 경기를 계속해요"); Emu.nativeSetPaused(pad.isBarOpen()); return; }
            League.orCheat(id, cheatBitsNow());                                          /* §9 — 멈추기 전까지 먹은 치트 */
            League.setStatus(id, "resume", why);
            League.note(id, "suspend", "user");                                          /* §위험 R1 — 사용자가 멈춘 판은 «무효로 닫기» 없음 */
            leagueDone = true; Emu.nativeLeagueDisarm();
            lgmCloseNow();
            hubReturn(-1);
            toast("경기를 저장했어요 — A 로 이어서");
            if (after != null) after.run();
        });
    });
}

/** 168: 열린 경기(진행·복귀 대기)를 지금 판에서 이어 한다 — 타이틀 «리그 대전» A(허브 찾기 6)·대기 메뉴. 없거나 준비면 false(평소처럼 찾기) */
private boolean hubResumeOpen() {
    org.json.JSONObject open = League.openMatch();
    if (open == null || "ready".equals(open.optString("status")) || leaving || !loaded) return false;
    rankQClose(false); Emu.nativeHubSearch(false);                                       /* H_SEARCH → H_TITLE(허브는 타이틀인 채 싸운다 — hubStart 길과 같은 상태) */
    Emu.nativeSetPaused(true);                                                           /* hubStartAgain(:1434) 과 같은 까닭: 불러오기 → 배경·CPU → 무장이 프레임 사이에 갈라지지 않게 */
    leagueId = open.optString("id"); leagueArmed = false; leagueDone = false; leagueStarted = false; leagueRetry = 0;
    leagueStart();                                                                       /* 체크포인트 불러오기 · FROM_CKPT · 이름표 · poll — 막히면 기존 막힘 카드 */
    if (!leaving && hubCard == null && !lgmShown && ask == null) Emu.nativeSetPaused(pad.isBarOpen());
    return true;
}
```
- `rankTick :2334-2340` 의 찾기 시작 앞에 `if (hubResumeOpen()) return;` — 타이틀에서 A 를 누르면 멈춘 경기가 있으면 찾기 대신 그 경기로(유저 3b «A 로 이어서»).
- `rankNewMatch :2662-2670` «끝나지 않은 경기가 있어요» 카드의 «이어 하기»(지금 `switchSession(true,false)` = 판 다시 열기) → `hubResumeOpen()`.
- `hubStart` 의 기존 이어 하기(`:1894-1897`)는 그대로(앱을 새로 켠 때).

### A-3. 정합성(왜 되감기가 안 되나)
- 저장하는 순간의 자리를 그대로 이어 간다(체크포인트는 한 번 쓰면 지움 `:1141`). 멈춘 동안 다른 랭크 경기는 못 만든다(`League.newRankedMatch` 가 열린 경기가 있으면 null) → 진 판을 묻어 두고 새 판을 할 수 없음.
- onPause/onResume 체크포인트 규칙(`:1013-1021`, `:1033`)은 그대로 — 멈춘 뒤엔 `leagueId == null` 이라 안 건드린다.

---

## 1. «나중에» 뒤 순위표·리그 화면 빼기

### 지금
| 길 | 자리 | 하는 일 |
|---|---|---|
| 쉼(덧판) «나중에» | `LeagueMenu.java:605` → `EmuActivity.java:3207-3226 lgmLater` | 체크포인트 → «resume» → `leagueExit(null)` |
| 옛 나가기 카드 «나중에 이어하기» | `EmuActivity.java:1480-1499 leagueLeave` | 같음 |
| `leagueExit(null)` | `:1531-1549` | 코어 내리고 **LeagueActivity**(순위표 탭이 첫 화면 = 유저가 본 «순위표·홈페이지») 열고 끝 |
| 쉼 줄 설명 | `MenuModel.java:358` | «저장하고 리그 화면으로» |

같은 LeagueActivity 로 새는 길(게임 흐름 안): `lgmQuit QUIT_BOARD :3199`(→ `leagueExitBoard :2934`) · 옛 결과 카드 «순위표» `:2113` · 타이틀에서 뒤로 `hubLeaveTo(0) :2843-2844`(게임에서 안 왔으면 `leagueExitBoard`) ·
막힘 카드 «리그 화면으로» `:1309`(기록 사라짐) `:1333`(못 이음) `:1389`(A·B 카드) `:1458`(저장소).

### 새 동작
- `lgmLater`·`leagueLeave` 의 «나중에» → `leagueSuspend("사용자가 나중에 이어하기", null)`(§A). 설명 글 «저장하고 타이틀로 · A 로 이어서»(`MenuModel.java:358`, 오른쪽 «저장» 그대로).
- `QUIT_BOARD` 를 «그만할까요?» 목록에서 뺌(`LgmPages.java:196` rows) — 순위표는 서랍(§2). `lgmQuit` 의 case 도 지움.
- 옛 결과 카드 «순위표» 알약(`:2113`, 예전 12명 판에서만) → «리그 메뉴»(대기 서랍 순위 탭 — `lgmOpenLobby(TAB_BOARD)`).
- 타이틀에서 뒤로(`hubLeaveTo(0)`): 게임에서 왔으면 그대로 그 게임, **아니면 대기 메뉴를 연다**(§2 — 거기 «리그 나가기 › 내 게임 / 게임 목록»). → 게임 흐름 안에서 LeagueActivity 로 가는 길이 없어진다. (열린 결정 D2)
- 막힘 카드의 «리그 화면으로»: 리그 판(허브)이면 «타이틀로»(`hubReturn(-1)`; 저장소 카드는 «게임 목록»(`goList`)). 옛 한 판(`!leagueHub`)만 예전 글.
- LeagueActivity 자체는 남긴다 — 런처 «리그 순위표»(`MainActivity.java:592 openLeague`)에서만.

### 파일
- `EmuActivity.java`: `lgmLater`, `leagueLeave` 버튼 몸통, `lgmQuit`, `hubResult :2113`, `hubLeaveTo :2836-2845`, 막힘 카드 4곳, + §A 두 함수.
- `MenuModel.java:358`, `LgmPages.java:196`.

---

## 2. 게임 안 메뉴로 리그 화면 전부 — 157-B «대기» + 서랍 «리그» 탭 + 시즌 초기화

기획서 `handoff/ss2_next/157_인게임메뉴_기획/기획서_리그_인게임메뉴.md` §4.5 «대기 — 리그 타이틀(157-B)» 그대로 + 리그 탭.

### 지금
- 덧판 메뉴는 결판(`K_RESULT`)·쉼(`K_PAUSE`, 경기 중만 — `lgmEligible :3010-3018`)뿐. `MenuModel.java:27 // 157-B: K_LOBBY = 3` 자리만.
- 서랍 탭 3개 고정: `LeagueMenu.java:736-740 firstTab/nextTab(… % 3)`, `LgmPages.java:1229 tabRow`(«157-A 는 순위·전적·설정 셋만»), `MenuModel.Prefs TAB_BOARD 0·RECORD 1·SETTINGS 2`.
- 시즌 도구는 LeagueActivity 에만(`LeagueActivity.java:581-676 seasonSection·askNewSeason·askRestart`), 그것도 `League.resetBlockedWhy :1570-1575` 가 `liveHub` 면 막는다(«게임 속 리그를 닫은 뒤에»).

### LeagueActivity → 게임 안 자리 표
| LeagueActivity | 게임 안 |
|---|---|
| 내 카드(티어·LP·전국 순위·시즌·통산·최고) `:281-317` | 대기 칼집 머리 패(«리그 · 무사★4 1935 LP» · «오늘 4승 1패 · 첫 승 +30 남음») + 전적 탭(이미 `MenuModel.Record`) |
| 내 캐릭터 · [바꾸기] `:319-339` | 대기 줄 «내 캐릭터 바꾸기 · 하오마루 수라» → §6 «내 캐릭터 먼저 고르기» |
| 하러 가기 / 멈춘 경기 이어서 `:224-231` | 대기 첫 줄 «▶ 상대 찾기»(= A) / «▶ 멈춘 경기 이어서»(§A) |
| 열린 경기 카드 [기권하고 찾기][무효로 닫기] `:747-808` | 대기 줄 «기권 −n LP»(쉼과 같은 두 번 묻기) · «무효로 닫기»(`League.voidKind` 일 때만) |
| 순위표(위 100·내 주변)·프로필 | 서랍 순위(있음) |
| 최근 경기 `:485` · 라이벌 `:514` | 서랍 전적에 목록 층(L) 추가: 최근 20판(승패·점수·±LP·상대·치트 표) + 라이벌 줄 |
| 규칙 `:556-577` · 보류·무효 `:252-270` · 시즌·기록 `:581-620` | **서랍 리그 탭**(새) |

### 2-1. MenuModel (`java/.../MenuModel.java`)
```java
static final int K_RESULT = 1, K_PAUSE = 2, K_LOBBY = 3;
static final int ROW_SEARCH = 10, ROW_RESUME_OPEN = 11, ROW_MAIN = 12, ROW_OPEN_FORFEIT = 13, ROW_OPEN_VOID = 14, ROW_LEAVE = 15, ROW_BACK = 16;
/* Prefs — 저장 값(pref.lgm.lastTab)은 번호 그대로, 보이는 차례만 TAB_ORDER */
static final int TAB_BOARD = 0, TAB_RECORD = 1, TAB_SETTINGS = 2, TAB_LEAGUE = 3;
static final int[] TAB_ORDER = { TAB_BOARD, TAB_RECORD, TAB_LEAGUE, TAB_SETTINGS };
/** 리그 탭 사본(UI 스레드에서 한 번 — 불변) */
static final class LeagueInfo {
    int season; String since, wld; String[] pastRows;            // «시즌 2 · 처음부터 다시 · 최고 검호★1 · 마지막 무사★4 · 31승 22패»
    boolean placement; int lp0, lp1; String label0, label1;       // 새 시즌 미리보기(League.newSeasonPreview — 배치 중이면 placement)
    String blockWhy;                                              // null 이면 시즌 도구 됨 · 아니면 «멈춘 경기를 먼저 끝내요»(시작한 경기 열림)
    String[] holds; String mainLabel; String[] rules;             // 보류·무효 5줄 · «하오마루 수라 · 쪽빛» · 규칙 문단(줄바꿈은 LgmPages)
}
static MenuModel lobby(Context c, Ctx ctx, org.json.JSONObject open, String voidKind, League.Main main, boolean atTitle);
```
대기 줄: 타이틀이면 `[ROW_SEARCH 또는 ROW_RESUME_OPEN, ROW_DRAWER(«순위·전적·리그 ›»), ROW_MAIN, (열린 경기면 ROW_OPEN_FORFEIT, voidKind 면 ROW_OPEN_VOID), ROW_LEAVE]`,
타이틀이 아니면(고르기·찾기 겹창 뒤 — 경기 전) 첫 줄이 `ROW_BACK`(«▶ 돌아가기»). 흐린 줄 없음 — 못 쓰는 줄은 아예 안 넣는다(유저 «안 돼요» 싫음).

### 2-2. LeagueMenu (`java/.../LeagueMenu.java`)
- 상태 `ST_LOBBY = 9`(`:22` 끝에). `openLobby(MenuModel m, LgmPages.Scene sc)` — `openPause`(`:199`)와 같은 모양(층 올리기·대본·커서).
- 입력(`:538-575` switch): `ST_LOBBY` — ▲▼ 고르기 · A 결정 · B/OPTION 닫기(`close()` — 코어 멈춤 풂). `select()`(`:579`)에
  `ROW_SEARCH → closeThen(act::lgmSearch)` · `ROW_RESUME_OPEN → closeThen(act::lgmResumeOpen)` · `ROW_DRAWER → openDrawer(firstTab())` · `ROW_MAIN → closeThen(act::lgmMain)` ·
  `ROW_OPEN_FORFEIT → openConfirm()`(쉼 기권과 같은 맥박 · 둘째 A → `act.lgmOpenForfeit`) · `ROW_OPEN_VOID → setBusy(); post(act::lgmOpenVoid)` · `ROW_LEAVE → toQuit(0)` · `ROW_BACK → close()`.
- 타이틀 OPTION 탭: `setLobbyEligible(boolean)` 추가, `feed :285` 를 `if (pauseEligible || lobbyEligible) game = optionGate(in, game);` 로, `optionGate :453-473` 탭이 잡히면 `pauseEligible ? act::lgmWantPause : act::lgmWantLobby`.
  (`ov.hold(true)` 그대로 — 타이틀 연출도 멈춘 채 메뉴)
- 서랍: `firstTab()` 은 0~3 범위, `nextTab(tab, d)` 은 `TAB_ORDER` 안에서 돈다. `closeDrawer :760` 의 «부른 화면»에 `ST_LOBBY`(`sLobby`) 추가.
- 리그 탭 두 번 묻기: 서랍 `select` 의 `LgmPages.LG_NEW_SEASON / LG_RESTART` 는 첫 A → 그 줄 맥박(«A 한 번 더 = 새 시즌» — `confirmAt`·`CONFIRM_MIN :37` 재사용, 장면은 `lgmWantDrawer(TAB_LEAGUE)` 로 다시 그려 받음), 둘째 A → `post(() -> act.lgmSeason(kind))`.
- Actions(`:94-106`) 추가: `lgmWantLobby() · lgmSearch() · lgmResumeOpen() · lgmMain() · lgmSeason(int kind) · lgmOpenForfeit() · lgmOpenVoid()`.

### 2-3. LgmPages (`java/.../LgmPages.java`)
- `Scene lobby(MenuModel m)` — 쉼 장면(`pause :736`)의 칼집·정보 패를 그대로 쓰고 머리 글만 바꿈. SC_LOBBY = 8.
- `Scene league(MenuModel m, LeagueInfo li, int confirmRow)` — SC_LEAGUE = 9, `tabRow(s, TAB_LEAGUE)`; 줄(rows): `LG_NEW_SEASON 301`(«새 시즌 시작 · LP 2410→1900», 배치 중이면 줄 대신 글 «배치 경기를 마치면 새 시즌»), `LG_RESTART 302`(«처음부터 다시 · 배치 5판부터 · 기록은 보관»), `LG_MAIN 303`(«내 캐릭터 바꾸기»);
  `blockWhy` 면 시즌 두 줄 대신 그 글 한 줄(경기 이야기 — 리그 탓 글 아님). 목록 층(L, 순위 목록과 같은 스크롤): 시즌 줄들 · 보류·무효 · 규칙 문단(156px 줄바꿈).
- `record(...)`(`:1050`): 아래 남는 줄에 L 목록(최근 20판 «승 2:1 +95 칼끝노인 · 치트») — 줄이 없는 탭이라 ▲▼ = `scrollList`(이미 그렇게 감 `LeagueMenu :567-569`).
- `tabRow :1229` 4칩(«순위 · 전적 · 리그 · 설정» — 2글자 넷이면 160px 에 듦).
- `quit(...)`(`:196`): `QUIT_BOARD` 뺌.
- 타일·팔레트 예산(W ≤ 496 타일 · 팔레트 ≤ 16) — `u165/fuzz LgmFuzz` 에 새 장면 셋을 넣어 검사.

### 2-4. EmuActivity
- `lgmLobbySync()` — `lgmEligibleSync :3019` 옆, `hubTick` 마다: `lgm.setLobbyEligible(leagueHub && hubRanked && hubLastState == 1 && leagueId == null && rankQ == null && !lgmShown && hubCard == null && ask == null && lookEditor == null && !(sheet != null && sheet.isShowing()) && !(pad != null && pad.isBarOpen()))`.
- `lgmWantLobby()`: `MenuModel.lobby(...)`(열린 경기·`League.voidKind`·`League.main()`) → `lgmRender` 로 `lgmPages().lobby(model)` → `gl.queueEvent(() -> mm.openLobby(model, sc))` → `lgmOpenUi(true)`. 못 쓰면(덧판 없음) 조용히 `mm.cancelPause()`(옛 길 없음 — 대기는 새것).
- `lgmSearch()` = `rankTick` 과 같은 찾기 시작(`hubResumeOpen()` 먼저 → 아니면 main 이 없으면 §6 내 캐릭터 먼저, 있으면 `rankSearchStart()` 는 허브 6 이 필요하므로 `Emu.nativeHubSearch(true)` 로 허브를 찾기로).
- `lgmResumeOpen()` = `hubResumeOpen()`. `lgmMain()` = `hubPickOnly(false)`(§6).
- `lgmOpenForfeit()`: `League.forfeit(open.id)` → `leagueId = id; leagueExit(id)` → `hubResult` → w165 의 `lgmOpenNow`(지금 그려 열기)로 기권패 결판. `lgmOpenVoid()`: `League.voidStarted(id, vk)` → 대기 다시 그림.
- `lgmDrawer :3292` 에 `TAB_LEAGUE` 갈래: `MenuModel.LeagueInfo li = League.leagueInfo(this)` → `lgmPages().league(model, li, confirmRow)`.
- `lgmSeason(kind)`:
  ```java
  String why = League.resetBlockedWhy(true);                       // 게임 안에서 부름 — liveHub 는 안 봄
  if (why == null) {
      cancelReady("시즌 도구 — 대진 전");
      boolean ok = kind == 1 ? League.newSeason(true) : League.restartRanked(true);
      if (ok) { BoardCache.invalidate(); League.sessionStart(); pushMain(); toast(kind == 1 ? "시즌 " + League.season() + " 시작!" : "배치 경기부터 시작해요"); }
      else toast("저장하지 못했어요 — 기록은 그대로예요");
  }
  lgmDrawer(MenuModel.Prefs.TAB_LEAGUE);                            // 새 값으로 다시
  ```
- 멈춤 바 «리그 메뉴» 칸: 리그 판에서도 `UTIL_LEAGUE` 칸을 보인다(`leagueCellSetup :2912` — 지금은 `!ranked()` 일 때만). 글자만 «리그 메뉴»(PadView `setLeagueCell(on, label)`).
  `handleAction ACT_LEAGUE :585-587` 리그 판 갈래: 경기 중(`lgmEligible(true)`) → `requestPause` · 결판 메뉴가 떠 있으면 그 서랍 · 그 밖 → `lgmWantLobby()`(찾기 겹창이면 `rankQBack()` 먼저).

### 2-5. League (`java/.../League.java`)
- `resetBlockedWhy(boolean inGame)` — `inGame` 이면 `liveHub` 검사(`:1572`)를 건너뛴다(부르는 쪽이 그 허브이고, 준비 경기는 `cancelReadyMem` 이 닫음). `startedOpen()`(시작·멈춘 경기)은 그대로 막고 글을 «멈춘 경기를 먼저 끝내요»로.
- `newSeason(boolean inGame)` · `restartRanked(boolean inGame)` — 몸통 그대로, 막힘 검사만 위 함수로(보관 파일 먼저 쓰기·되돌리기 `:1586-1640` 그대로).
- `leagueInfo(Context)` → `MenuModel.LeagueInfo`(season·seasonStart·seasons·newSeasonPreview·holds(5)·main·rules — rules 글은 LeagueActivity `rulesTab :556-576` 글을 `League.rulesText()` 로 옮겨 두 화면이 같이 씀).

---

## 3. «리그 상태라 안 돼요» 없애기 + 3b(저장·불러오기만 없음 · 리셋 = 저장 후 타이틀)

### 지금 — 리그라서 막는 곳과 글
| 자리 | 지금 |
|---|---|
| `EmuActivity.java:499-505 handleAction` | ACT_LOAD·UNDO·RESET·CFG·SAVE·QSAVE → 토스트 «리그 경기 중엔 저장·불러오기·리셋·설정을 못 써요…» / «리그 판에선 … 막혀요…» |
| `:572` ACT_CFG | `sheet.cheatOff = "리그 대전에선 치트가 꺼져요"` (지금은 창 자체가 위에서 막혀 안 옴) |
| `:3392-3396 cheatSetup` | `nativeCheatLock(true)` + 토스트 «리그 대전에선 치트가 꺼져요» |
| `:3406-3412 pushCheats` · `:3415-3417 cheatPoll` | `ranked()` 면 안 넣음·안 봄 |
| `:1919-1922 hubTick` 셋째 줄 ◀▶ «연습 대전» | 경기 기록이 있으면 «지금은 연습 대전으로 못 가요 — 뒤로 가기로 나간 뒤 다시» |
| `cpp/cheat.c:240` | `own == 1`(리그) → why 2 → 아무것도 안 씀 |
| `LaunchSheet.java:686-687` · `Cheats.java:55 WARN` | «리그 대전엔 안 먹어요» |
| `MenuModel.java:284-286` ROW_NEWCHAR | 저장한 캐릭터 판이 아니면 흐림 «직접 고르는 판이라 그대로예요» |
| `LeagueActivity.java:559-560` 규칙 글 | «랭크 경기 중에는 불러오기·되돌리기·리셋을 쓸 수 없고» |

### 새 표(리그 판 = `ranked()`)
| 동작 | 새 동작 | 글 |
|---|---|---|
| 저장(ACT_SAVE)·로드(ACT_LOAD)·슬롯(ACT_SLOT) | **칸을 숨김**(`PadView.setRankedBar(true)` → `utilVisible :352` 에서 `UTIL_SLOT 0·SAVE 1·LOAD 2` 를 뺌 — 바 배치가 개수로 다시 잡힘 `:517`) | 없음 |
| 빠른 저장(메뉴 알약 길게 `:275-280` → ACT_QSAVE) · 되돌리기 칩(ACT_UNDO) | 받아도 조용히 return(되돌리기 칩은 리그에서 아예 안 띄움 — 리셋이 `withUndo` 를 안 씀) | 없음 |
| 리셋(ACT_RESET) | `leagueReset()` = 열린 덧판·결과 카드·찾기 겹창을 닫고 `leagueSuspend("사용자가 리셋 — 타이틀로", null)`(§A). 경기 밖이면 그냥 타이틀로 | 칸 아래 줄 `utilSub[UTIL_RESET] = "저장 후 타이틀"` · 멈췄을 때만 «경기를 저장했어요 — A 로 이어서» |
| 설정(ACT_CFG) | 창 열림 — §10 | 없음 |
| 치트 | 먹음 — §9 | 창 글 «리그에서 먹은 판은 기록에 «치트»로 남아요» |
| 셋째 줄 «연습 대전»(`:1919`) | 준비 기록이면 `cancelReady` 후 갈아타기 · 시작한 경기면 `leagueSuspend(…, () -> switchSession(false, true))` · 결과가 떠 있으면 닫고 갈아타기 | 없음(토스트 지움) |
| 목록·종료(`:506-517`) | 그대로(157 post — 경기 중이면 쉼, 아니면 바로) | — |
| 새 캐릭터 줄 | 늘 켬(§6) | — |

`handleAction :499-505` 를 이걸로:
```java
if (ranked()) {
    switch (action) {
    case PadView.ACT_SAVE: case PadView.ACT_QSAVE: case PadView.ACT_LOAD: case PadView.ACT_UNDO: case PadView.ACT_SLOT:
        return;                                         /* 168(3b): 리그 판엔 저장·불러오기가 없다 — 칸은 숨겼고 남은 길(길게 누르기)은 조용히 */
    case PadView.ACT_RESET:
        h.post(this::leagueReset); return;              /* 바가 닫히며 멈춤을 푼 뒤(ACT_PICK 갈래와 같은 까닭) */
    default: break;                                     /* 설정(§10)·치트(§9)·나머지는 아래 평소 길 */
    }
}
```
- `PadView`: `setRankedBar(boolean)` 추가(값만 바꾸고 `layoutBar`). EmuActivity 가 코어를 올린 뒤(`leagueCellSetup` 옆)·`ranked()` 로 부름.
- 남는 거절 글은 **리그 탓이 아닌 것**만: 저장소 실패, «상대를 찾지 못했어요», 체크포인트 저장 실패 — 그대로.

---

## 4. 2P 컬러 전부 빼기

### w165fx 가 이미 한 것(합치면 끝)
- look.c: 캐릭터 고르기 B = 결정(보통 색, 검질 화면 B 는 게임 «뒤로») · OPTION 돌리기에서 번호 1(2P색) 늘 건너뜀(`LOOK_DUP` 비트 1) · 미러 P2(팔레트 5) 바꾸기 없앰 → **게임이 같은 캐릭터 거울전에서 CPU 에 주는 2P 팔레트만 남음**(w165fx `look.c:22`) · 기억 칸 옛 1 → 0(`:384`) · `look_set_match` 1 무시(`:418`).
- league.c: `MY.b2p`·`APC.b2p` 없앰, 연습 `H.me_b2p` 늘 0, `look_set_pick(rnd)` 서명.
- Java: `League.Main.b2p` 없음(읽을 때 무시·쓸 때 false), `Look.parse` 옛 1 → 0, `LookEditor usable[1]=false`, `Settings` 컬러 설명, `myPickKeys` 글 «A 결정 · OPTION 컬러 · A+B 베기 색», autopick `b2p=false`, `LeagueActivity.mainColour` 1 → 0.
- grep(w165fx, «2P색|b2p») 남은 것 = 옛 기록 이름·JNI 서명 자리 설명뿐(확인함 — Java 의 다른 «2P» 는 0건).

### 168 에서 할 것(점검표)
1. 옛 경기 기록의 `look.color == 1` 을 화면에 보일 때(최근 경기 목록·결판 머리) «기본»으로(`League.COLORS[1]` 를 직접 쓰는 자리 — 새 전적 목록 §2-3 이 처음 씀).
2. `Look.NAMES[1]`·`LOOK_VLAB` 1번 글자·`LOOK_NAME[1]` 은 남김(번호 자리 — 고를 수 없음). 문서만 «옛 기록용».
3. 연습 HUD «2P» 글자(practice.c COM→2P)는 **플레이어 표시**라 그대로(컬러 아님).
4. handoff 문서(color/CHANGES.md 등)의 «B = 2P색» 줄 고침.
- 시험: w165fx `reg/color`(t_look·t_look2·t_look_hub·t_hub_look·x8·x9) · JVM `StringsTest` · grep 문(«2P색»은 위 2번 자리만).

---

## 5. 커스텀 컬러가 수라·나찰을 골라도 안 바뀌게

### 지금(원인)
- 프리셋 표가 **검질마다 따로 계산**된다: `look_gen.py`(u165fx/impl/gen — 원본 handoff/ss2_next/color/tests) `for sty in range(2): B, A = row[sty]; t = [f(B, A) …]` → `look_tab.h LOOK_TAB[캐릭터][검질][프리셋][3]`.
  예: 하오마루 «쪽빛»(2) 수라 `{0xBDF,0xD53,0x521}` / 나찰 `{0x9BF,0x942,0x521}` · 겐쥬로 «다홍» 수라·나찰도 다름.
- 캐릭터 고르기 미리보기는 늘 수라 그림(w165fx `look.c:337` 주석) → 거기서 본 색 = 수라 판 색. 검질 화면에서 ←→ 로 나찰에 가면 `tri(row, sty, K.cur, t)`(w165fx `look.c:339-351`, 자리 두 개)가 나찰 판 색을 넣고,
  경기도 `match_want` 의 `tri(ch, sty, K.sel, t)` → **나찰을 고르면 색이 바뀐다**(유저 보고).
- 내 색 1·2(16·17)는 `K.cus[14][2][3]` — 캐릭터마다 두 검질 공통(`tri :87-93` 이 16·17 에선 sty 를 안 봄) → 이미 안 바뀜.

### 새 동작
- 프리셋(2~15) 세 색 = **검질과 무관하게 그 캐릭터의 수라 판 값**(캐릭터 고르기에서 보이는 그 색). «기본»(0)만 검질마다 원래 게임 색(게임 정체성).
- 생성기: `tab[r][1][i] = tab[r][0][i] for i >= 2`, 겹침 표(`LOOK_DUP`)는 합친 값으로 다시 셈(두 검질 같아짐) → `look_tab.h` 다시 만듦(쿠로코 줄은 그대로).
- 런타임 보증(표가 옛것이어도): `look.c tri()` 첫 줄 `if (idx >= 2 && idx < LOOK_NPRE) sty = 0;` · `idx_ok` 는 sty 를 안 보는 쪽으로(합친 DUP).
- Java `Look`·`LookEditor`(시작 색 `look_triples`)는 native 값을 받으니 저절로 같아짐.
- 기록은 번호만 남기므로 옛 기록 그대로.

### 위험·확인
- 나찰 그림에서 세 칸의 역할(피부·옷·그림자)이 수라와 같다는 전제(내 색이 이미 그 전제로 공통 — `look.c` `cus` 주석) — **14명 × 14프리셋 × 나찰 미리보기를 찍어 눈으로 확인**(u165fx `previews.py`·`pgrender.py` 꼴). 어긋나는 캐릭터가 있으면 그 캐릭터만 «나찰 줄 = 수라 줄의 색 대응표 적용»으로 생성기에서 예외.
- 153 의 «나찰 경기 색 12가지» 시험 기대값이 바뀜 → 새 정답으로 고침.

---

## 6. 리그 «캐릭터 바꾸기»: 내 캐릭터를 먼저 고르고, 그다음 상대

### 지금
- `rankNext(true)` `EmuActivity.java:2350-2360`: `League.clearMain()` → `pushMain()`(자동 끔 → tail, rankAuto 1) → **`League.rankedPick` 으로 상대를 바로 정함** → `rankPrepare` → 겹창 «상대 발견!»(`rankQOpen(Q_RUN)`, 직접 고르는 판은 `Q_FLASH_TAIL` 1.1초 보이고 내려감) → `rankArmNext :2380-2390`(`nativeHubMatch` → `hubReturn(-4)`) →
  native 리셋 → `hub_go_fixed`(`league.c:647-654`, 상대 무장) → `H_PICK_ME` tail: 상대가 정해진 채 사용자가 고름 → 이야기 자동 → VS → 경기. 고른 것은 `rankCapTick :2622-2640` 이 `League.setMain`.
- 처음 들어온 판(main 없음)도 같은 tail 길(`rankSearchStart :2342-2348`).
- 부르는 곳: 덧판 «새 캐릭터» `LeagueMenu.java:588 → lgmNext(true) :3179`, 옛 카드 «캐릭터 바꾸기» `:2784`. «새 캐릭터» 줄은 rankAuto==2 일 때만 켬(`MenuModel.java:284-286`).

### 새 흐름 «내 캐릭터 먼저 고르기(pick-only)»
1. Java `hubPickOnly(boolean viaReset)`: `rankQClose(false)`; `rankPickOnly = true`; **main 은 아직 안 지움**(고르다 뒤로 나가면 예전 캐릭터 그대로).
   결판 뒤(«새 캐릭터»)는 `hubReturn(-5)`(리셋 → 타이틀 → 바로 고르기 — −4 처럼 로고 빨리 넘김), 타이틀·찾기에서는 `Emu.nativeHubPickOnly()`(리셋 없이 메뉴 → 1인 대전 고르기).
2. native: 상대 **없이**(L 무장 안 함) `H_PICK_ME` — 머리말 «내 캐릭터»(§8), 고르는 동안 카드 소유 120칸 = 8(지금 L.allcards 가 하는 일 — 무장이 없으니 허브가 대신), 컬러·베기 색은 look 그대로(ctx FREE — 게임이 결정),
   카드 화면까지 사용자가 고름. 이야기가 시작되면(`story_start`) `my_commit(ram, 0)` → `PO.done = 1` → 게임 입력 모두 막고 이야기는 넘기지 않음(序章 ≥ 1700프레임 — Java 가 그 안에 리셋).
   고르기에서 뒤로(타이틀이 보이면) → `H_TITLE`, PO 비움.
3. Java `hubTick`(150ms): `rankPickOnly && hs[0] == 3 && nativeHubPickOnlyStatus()[1] == 1` → `mp = myPick()` → `League.setMain(mp)` → `pushMain()`(이제 자동 · rankAuto 2) → `rankPickOnly = false` → **`rankNext(false)`**
   = 평소 «다음 상대»: 겹창 «상대 찾는 중» → 상대 정함 → −4 → 4배속·무음 자동 진행(겹창 뒤) → VS 띠(내 검질 표시 — main 이 있으니) → 경기. 타이틀로 돌아왔으면(`hs[0]==1`) `rankPickOnly=false`.
4. main 이 없을 때(첫 판): `rankTick` 의 찾기 시작 = `hubResumeOpen()` → 아니면 `League.main() == null ? hubPickOnly(false) : rankSearchStart()`. `hubStart` 의 `EXTRA_HUB_GO`(`:1898-1901`)도 허브가 찾기(6)에 닿으면 같은 갈래.
5. «새 캐릭터» 줄 늘 켬, 설명 «내 캐릭터부터 다시 고르고 상대를 찾아요». 옛 카드 버튼도 늘.
6. tail 첫 판 길(`rankCap`·`rankCapRefine`)은 **자동 진행이 막혔을 때의 대비**로만 남는다(AP_FAIL → 상대가 정해진 채 직접 — 지금 그대로).

### native (cpp/league.c) — H 밖에 둔다(.prac 아님)
```c
/* 168 내 캐릭터만 고르는 판 — 상대 없음(L 무장 안 함). H 밖(리그 판 전용 · .prac 크기 무관) */
static struct { int req, on, done; unsigned f0; } PO;
static void hub_go_pick_only(uint8_t *ram)           /* 메뉴·커서 2 에서만 — hub_go_fixed 와 같은 자리 */
{
   ram[R_MCUR] = 0; H.nav = 1; H.nav_f = H.f; H.st = H_PICK_ME; H.picked = -1; H.seen_csel = 0; H.go = 0; H.ev = 0;
   L.armed = 0; auto_clear(); vs_reset_locked(1);
   memset(&MY, 0, sizeof MY); MY.r_cell = -1; MY.r_sty = -1;
   PO.req = 0; PO.on = 1; PO.done = 0; PO.f0 = H.f;
}
static int pick_only_tick(uint8_t *ram)              /* H_PICK_ME(종류 0)에서 PO.on 이면 pick_me_153 대신 */
{
   if (ram[R_MODE] == 240 && (ram[R_SCR] == 2 || ram[R_SCR] == 4)) memset(ram + R_OWN, 8, 120);   /* 올카드(무장의 allcards 와 같은 창) */
   hdr_mine(ram);                                    /* §8 «내 캐릭터» 머리말 */
   if (PO.done) { league_in_or = 0; return IN_GAME_ALL; }
   my_track(ram);
   if (!MY.done && story_start(ram)) { my_commit(ram, 0); PO.done = MY.valid; }
   return 0;
}
void league_hub_pick_only(void);                     /* Java — PO.req = 1(H_TITLE·H_SEARCH 에서 메뉴·커서 2 면 hub_go_pick_only) */
void league_hub_pick_only_status(int v[3]);          /* [on, done, 프레임] — LEAGUE_NHUB(15) 는 안 늘린다 */
```
- `league_hub_return(-5)`: `H.rematch = -5` → nav 3 끝(`:711-738`)에 `else if (H.rematch == -5 && menu && ram[R_MCUR] == 2) hub_go_pick_only(ram);`, `auto_fast_boot :513` 에 `|| H.rematch == -5`(로고 빨리) — 빠른 길(`:694`)에서도 `-5` 면 `hub_go_pick_only`.
- 커서 조건: `hub_go_fixed`·`H_SEARCH` 의 go(`:775`)는 «메뉴 커서 2»일 때만 부른다. 대기 메뉴(§2)는 타이틀 커서가 다른 줄일 때도 열리므로 «상대 찾기»·«내 캐릭터 바꾸기»가 멈추지 않게,
  `H_SEARCH` go 와 `PO.req` 는 «타이틀 메뉴가 떠 있고 nav 없음»이면 받는다(두 함수 다 `R_MCUR = 0` 을 직접 쓰고 A 를 대신 누르니 커서 자리는 상관없음 — 실측으로 확인).
- `H_PICK_ME`(`:865-892`) 대진 전 타이틀로: `PO` 비움. `L.fight_seen` 은 무장이 없어 안 섬(그래도 안전: 무장 없는 싸움은 기록 없음).
- `my_commit :604-621`: 무작위 칸(`r_cell == 15`)인데 유가 치트로 `0x57D5 == 14` 면 `ch = -1`(칸 15 로 남김 — 자동 진행이 다시 굴림, 유가 치트면 다시 유가) — 안 그러면 `ch > 13 → return` 이라 PO 가 영영 안 끝남.
- `league_hub_look_ctx :1627`: PO 중엔 FREE(지금 식에서 `H.nav != 0` 일 때만 BUSY — 그대로 맞음).
- JNI `nativeHubPickOnly()` · `nativeHubPickOnlyStatus()`(Emu.java). 옛 native(없음) → `UnsatisfiedLinkError` 면 예전 tail 길.

---

## 7. 연습: 내 캐릭터 → 내 검질(수라·나찰) → 상대

### 지금
`H_PICK_ME1`(`league.c:781-804`, w165fx: look HOLD · `look_take_confirm`) — 내 칸만 받고 같은 화면에서 → `H_PICK_OPP`(`:805-834`: A 수라·B 나찰 더미 · OPTION 스테이지) → 무장 + `nav_to(내 칸, A)` → `H_PICK_ME`(게임 검질 고르기·카드 — 사용자) → 경기.
즉 순서가 «나 → 상대 → 내 검질». Java 띠 `practiceText :3543-3560`(7 · 2 · 3).

### 새 순서
`H_PICK_ME1`(내 캐릭터) → 게임이 캐릭터 확정 → **`H_PICK_STY1`(새, 8) 게임 검질 고르기 화면에서 내 검질** → 허브가 B(게임 «뒤로»)를 대신 눌러 캐릭터 고르기로 → `H_PICK_OPP`(상대 — 머리말 빨강 §8) → 무장 + `nav_to(내 칸, A)` → `H_PICK_ME` 가 검질 화면에서 **고른 검질을 자동 확정** → 카드(사용자) → 이야기 넘김 → 경기.
게임의 진짜 검질 화면(검질 그림·이름)을 그대로 쓴다 — 같은 화면에서 A/B 로 검질을 정하는 길은 w165fx 가 B 를 «결정(보통 색)»으로 써서 안 됨.

### native (cpp/league.c)
- `enum { …, H_PICK_ME1, H_PICK_STY1 }`(`:177` 끝에 — 다른 번호 그대로, .prac 은 H_MATCH 만 저장하니 새 번호 무관).
- `H_PICK_ME1` 결정(w165fx 의 `conf`): 지금 `H.me_go = 1`(같은 화면 유지) 대신 → `H.me1 = hover+1; H.me_pin = 0; H.st = H_PICK_STY1; pr_inj = IN_A`(다음 프레임부터 4프레임 A — look 이 HOLD 라 스스로 안 누름) .
- `H_PICK_STY1`(새 case):
  ```c
  case H_PICK_STY1:                                   /* 게임 검질 고르기 — 결정은 look(HOLD)이 넘김: A = 이 검질 · B = 캐릭터 다시 */
     if (ram[R_MODE] == 240 && ram[R_SCR] == 4 && ram[R_PHASE] == 8) {
        int t = look_take_confirm();                  /* 168: 1 A · 2 B (w165fx 는 1 만 — 단추를 돌려주게 넓힘) */
        if (t == 1) {
           H.me_pad = (ram[R_STYC] & 1) + 1;          /* 내 검질 + 1 — 옛 «남는 칸»(sizeof H 그대로, 옛 덩어리는 0 = 모름) */
           if (H.me1 == 16) { int hv = ram[R_HOVER] >> 2; if (hv < 14) H.me_pin = (signed char)(hv + 1); }   /* 무작위 칸 — 이 화면에서 멈춘 캐릭터로 고정 */
           pr_back = 1;                               /* 다음 프레임부터 B 4프레임(게임 «뒤로») → 캐릭터 고르기 */
        } else if (t == 2) { pr_back = 2; }           /* 캐릭터부터 다시 */
     }
     if (pr_back && csel && ram[R_PHASE] == 6) {      /* 캐릭터 고르기로 돌아옴 */
        if (pr_back == 1) { H.st = H_PICK_OPP; H.picked = -1; H.csel_f = 10; H.prepos = 0; }
        else { H.st = H_PICK_ME1; H.csel_f = 0; H.prepos = 1; }
        pr_back = 0;
     } else if (H.f - H.nav_f > 900 && !pr_back) { H.st = H_PICK_OPP; ... }   /* 검질 화면을 못 봄(이상) — 예전 순서로(검질은 나중에 사용자) */
     break;
  ```
  (`pr_inj`·`pr_back`·`pr_sty_auto` 는 H 밖 static — 연습 흐름 한 판 동안만, `pr_apply`·`league_practice_hub` 가 0 으로)
- `H_PICK_OPP` 연습 결정(`:813-834`): 무장·`nav_to(pin 또는 me1, A)` 그대로 + `pr_sty_auto = H.me_pad`(0 이면 예전처럼 사용자가 검질).
- `H_PICK_ME` 연습(`:869-876`): `pr_sty_auto && SCR 4 && PHASE 8 && R_CSUB == 4` → `ram[R_STYC] = pr_sty_auto - 1` · 16프레임마다 A(랭크 `auto_tick AP_STYLE :558-566` 와 같은 수) · PHASE ≥ 10 이면 끝.
  그동안 `league_hub_look_ctx` = AUTO(미리보기 색은 맞게, 사용자 OPTION·A+B 는 안 봄).
- 연습 메뉴 «상대 고르기»(repick, `league_practice_return(1)`) → `H_PICK_OPP` 바로 → 내 캐릭터·검질 자동. 검질을 바꾸려면 «타이틀로» → 연습 대전(내 칸 미리 옮김 `:788-791` 그대로 · 검질 화면 다시).
- `pr_me_check :940-946`: `me_pad` 0~2 아니면 0(표지 `PR_ME_TAG` 같은 조건). `_Static_assert(sizeof H == 628)` 그대로.
- `look.c look_take_confirm()`(w165fx): `return K.conf_pend ? (K.g_first == IN_B ? 2 : 1) : 0` 로(지금 1 만). H_PICK_ME1 은 `!= 0` 으로 보면 그대로.
- `league_hub_look_ctx`: `H.st == H_PICK_ME1 || H.st == H_PICK_STY1 ? HOLD : …` · `pr_sty_auto` 중 AUTO.

### Java
- `practiceText`: `case 7: "① 내 캐릭터  ·  " + myPickKeys(2)` · `case 8: "② 내 검질  ·  " + myPickKeys(4)` · `case 2: "③ 상대  ·  A 수라 · B 나찰 · OPTION 스테이지"` · case 3(자동 확정 뒤) 그대로. 허브 상태 v[0] 은 8 이 새로 올 수 있음(LEAGUE_NHUB 그대로).

### 위험
- 검질 화면 B «뒤로» 타이밍(R_CSUB 04 일 때만 받음 — 확인 연출 41~187프레임) → 하네스로 롬 6판 × 14명 × 2검질 + 무작위 칸.
- 무작위 칸 뜻 바뀜: 첫 검질 화면에서 멈춘 캐릭터로 고정(두 번째 확정에서 다시 굴리면 본 캐릭터와 달라짐). 열린 결정 D3.
- 153 «순서 12 변형» 시험·t_practice(68) 의 기대 순서가 바뀜 → 새 순서로 고쳐 씀.

---

## 8. 나 / 상대 고르기 화면 구분

### 지금
- 내 화면(연습 `H_PICK_ME1` · 랭크 첫 판/tail): 게임 머리말 «캐릭터 선택» 그대로 · 오른쪽 세로 칸 = 컬러 이름(look) · 그 위 문양 칸 = 베기 색 아이콘(w165fx).
- 상대 화면(`H_PICK_OPP`): 머리말 앞 6칸만 «상대»(`hdr_put :373-388`, `HUB_HDR_SANGDAE`; 순정판은 «선택»까지) · 세로 칸 = 배경 이름. **팔레트·커서·틀이 같아** 한눈에 안 갈림.

### 새 표시(모두 게임 화면 안 — 앱 뷰 아님)
| 단서 | 내 화면 | 상대 화면 | 구현 |
|---|---|---|---|
| 머리말 글 | **«내 캐릭터»**(10칸 × 2줄 통째) | «상대 선택»(있음) | `hub_glyphs.py` 로 `HUB_HDR_NAECHAR`(같은 글꼴·칠) · `hdr_put(kind, mode)` 의 mode 0 원래 · 1 상대 · 2 나. 한글판은 19타일(1줄 14칸 0x163 은 머리말이 아님 — 쓰면 남의 그림을 깸), 순정판 20타일. `hdr_orig[20*16]`(H 안, 이미 320바이트) 그대로 |
| 머리말 색 | 금빛(기본) | **빨강** | 둘째 판 빈 팔레트 하나를 빌려(w165fx `vpanel_icon_put` 의 할당기 — 7·6·5·4·3·2·13 중 둘째 판 칸이 안 쓰는 첫 번째) 머리말 칸의 팔레트 비트를 그 번호로. 원래 칸 값 20개는 H 밖 static 에 보관 · `league_hub_before_save :1075` 에서 되돌림 |
| 문양 칸(세로 칸 위 2×2) | 베기 색 아이콘(w165fx) | **빨간 «상대» 도장**(4타일) | `vpanel_icon_put(HUB_SEAL_SANGDAE, red)` — 같은 빌린 팔레트(머리말과 한 팔레트) |
| 들어가는 순간 | — | 머리말 3번 깜빡(36프레임, 글 ↔ 빈칸) | `H.csel_f` 10~46 동안 6프레임마다 |
| 앱 띠 | ① 내 캐릭터 · ② 내 검질 | ③ 상대 | §7 practiceText · 랭크 pick-only 띠 «내 캐릭터 고르기 — 고르면 상대를 찾아요»(`hubText case 3 :2036` 의 rankCap 갈래 자리에 `rankPickOnly`) |
| VS 띠 | 내 이름 옆 검질 | — | pick-only 뒤엔 main 이 있어 `rankVsArm(p, true)`(이미 rankAuto==2 갈래) |
| (선택) 커서 색 | 그대로 | 빨강 | 고르기 커서 스프라이트 팔레트 실측 후 — look 의 바꿔 쓰기 자리(0~11)와 안 겹칠 때만. 2단계 |

- 측정 먼저: 머리말 타일의 잉크 색 번호(1~3)와 빌릴 팔레트가 고르기 화면·검질 화면에서 정말 비는지(롬 6판) — w165fx `t_slash_icon.py` 꼴 하네스로. 못 빌리면 글·도장 없이 글자만(안전).
- 파일: `cpp/league.c`(hdr_put 모드·색·깜빡·before_save), `cpp/hub_glyphs.h`(새 배열 둘 — 생성기 `hub_glyphs.py` 에 «내 캐릭터»·«상대» 도장), `cpp/vpanel.c/.h`(`int vpanel_pal_borrow(const uint16_t c[3])` 를 아이콘 할당기에서 떼어 공용 — 한 화면에 하나만),
  `java/.../EmuActivity.java`(띠 글).

---

## 9. 화면에 «치트» 버튼 + 리그에서도 치트

### 지금
- 치트 창 입구: 실행 창 «치트 ›»(`LaunchSheet.java:388-392`) · 게임 안 «설정» 창 안 고리(`EmuActivity.java:560-577`) — 두 단계. 리그 판에선 설정 자체가 막힘(§3).
- 리그 판 치트 잠금 두 겹: Java `cheatSetup :3392-3396`(`nativeCheatLock(true)` + 토스트) · native `cheat.c:240`(`own == 1` → why 2 → 안 씀).
- 정산 검사: `League.settle :733`(규칙: 실효 시간 ≠ 60 이면 보류) · `:753 rankedKnobWhy :1310-1319`(CPU 단계·상한·배율이 손잡이와 다르면 «난도 불일치» 보류).
  치트 «CPU 세기»(`cheat.c fight_tick` 이 0x5814·0x5815·0x57E2·0x57E4 를 리그 손잡이 **뒤에** 매 프레임 씀 — cheat_tick 이 league_tick 다음)와 «시간 무한»(0x5812 = 0x80)이 리그에서 먹으면 그대로 보류된다.

### 9-1. 패드 «치트» 알약 (`java/.../PadView.java`)
- `ACT_CHEAT = 19`(`:51` 뒤). 컨트롤 표 `P_SS2 :72-80` 에 `{ "CHEAT", "치트", -5, 0.36f, 0.955f, 0.90f }`, 가로 `LAND :192-197` 에 `{ "CHEAT", 0.38f, 0.96f }` — OPTION 알약 왼쪽 아래 줄(십자 0.22/0.76 과 안 겹침).
- 그림: OPTION 과 같은 알약(`:790-794 skin.pill(c, "opt", …, "치트")`), 누르는 자리 48dp 이상(`:840` 같은 규칙). 게임 비트 아님 — 손을 뗄 때 안이면 `listener.onAction(ACT_CHEAT)`.
- `setCheatPill(boolean show)` — 사무쇼2이고 치트를 넣을 수 있는 판(`cheatOk`)일 때만. 배치 편집에서 끌기·크기(이름으로 저장 — 옛 `pad_ss2*.txt` 에 없으면 기본 자리). 터치 숨김 모드(`hidesTouch`)는 다른 버튼과 같게.
- u166 의 바 «치트» 칸은 이 알약으로 대체(입구 하나로 — 바 칸은 안 만든다).

### 9-2. 치트 창 바로 (`EmuActivity` · `LaunchSheet`)
- `handleAction case ACT_CHEAT`: 덧판 메뉴·확인 카드·컬러 만들기 창이 떠 있으면 무시. `padMask = 0; releasePhysical(); Emu.nativeSetPaused(true); sheet = LaunchSheet.showCheats(this, game, new File(orig));`
  `sheet.onClose = () -> { Emu.nativeSetPaused(pad.isBarOpen()); if (sheet.cheatsChanged() && pushCheats()) toast("치트 적용"); };`
  (`sheet` 칸을 쓰니 키 넘김·멈춤 조건 `:186`·`lgmEligible :3016` 이 따라옴 — 리그 경기 중 창이 떠 있으면 쉼 자격 없음)
- `LaunchSheet.showCheats()` — u166 §2-3 그대로(`cheatsOnly` · `open()` 갈래 · `closeCheats()` 가 창 닫기 · 안내 «킥 버튼 닫기»).

### 9-3. 리그에서 치트가 먹게
- Java: `cheatSetup`: `ranked()` 면 `cheatOk = game != null && Cheats.GAME.equals(game.id) && hubVersionProblem() == null`(리그 사본은 허브가 이미 판 확인) → `pushCheats()` · 폴. 잠금·토스트 없앰. `pushCheats :3406` 의 `|| ranked()`, `cheatPoll :3416` 의 `ranked()` 지움. `:572` cheatOff 는 모르는 롬일 때만.
- native `cheat.c:240`: `int why = locked ? 1 : own == 2 ? 3 : own == 1 ? 4 : 0;` — 4(리그) = **쓴다**(0 과 같은 갈래), 상태 v[7] 로만 «리그에서 먹음». 연습 흐름(3)은 예전처럼 경기 치트 쉼.
  `cheat_lock` 함수·JNI 는 시험용으로 남김(Java 는 안 부름). `cheat.h` 머리 주석 고침.
- 판마다 먹은 치트 비트(새):
  ```c
  static unsigned MB;                               /* 168: 마지막 표시 뒤 실제로 쓴 치트(1 << CH_*) — 경기 치트는 라운드 중(live) 쓴 것만, 올카드·유가는 쓴 순간 */
  unsigned cheat_match_bits(int clear);             /* C_mu — clear 면 0 으로 */
  ```
  `fight_tick` 안 쓰는 자리마다 `MB |= 1u << CH_*`, `cards_tick`(inwin·perm 쓰기)·`yuga_tick`(14 씀)도. `league.c arm_locked :1424` 끝에서 `cheat_match_bits(1)`(L_mu → C_mu — 허용된 순서, cheat_tick 은 C_mu 잡기 전에 `league_session_owner()` 를 부름).
  JNI `nativeCheatMatch(boolean clear)`. `CHEAT_NSTAT 16` 은 안 늘림(t_cheat.py 가 `c_int * 16`).
- Java 경기 쪽: `leaguePoll :1240` 마다 `int cb = Emu.nativeCheatMatch(false); if ((cb & ~leagueCheatSeen) != 0) { leagueCheatSeen |= cb; League.orCheat(leagueId, cb); }` · 멈추기(§A)·설정 다시 올리기(§10)·onPause 체크포인트 때도 `orCheat`.
- `League.settle(matchId, st)` → `settle(matchId, st, cheatBits)`(옛 서명은 0 으로 감쌈):
  ```java
  int cb = cheatBits | m.optInt("cheat_bits");
  boolean cTime = (cb & (1 << Cheats.TIME)) != 0, cDiff = (cb & (1 << Cheats.DIFF)) != 0;
  ...
  else if (need != rule.optInt("points") || (time != rule.optInt("time") && !(cTime && time == 0x80)))   // :733 — 시간 무한 치트가 설명하는 것만
  ...
  else if (rk && !cDiff) why2 = rankedKnobWhy(rule, st);                                               // :753 — CPU 세기 치트가 손잡이를 덮은 판만 면제
  if (cb != 0) { m.put("cheat", cb); res.put("cheat", Cheats.names(cb)); }                            // «시간·CPU 세기·상대 체력»
  ```
  LP·전적은 평소처럼 반영(기본 — 열린 결정 D1). 대진(P2 블록)·포인트·결판 비트 검사는 그대로.
  `forfeit :813` 도 `cheat_bits` 가 있으면 `cheat` 표.
- 표시: `MenuModel.result` 도장 `Tag('치', "치트", E_CHEAT)`(띠에 못 든 사건과 같은 아래 띠), 전적 탭 «치트 판 n», 새 최근 경기 목록 « · 치트», LeagueActivity 최근 탭 줄 끝, 옛 카드 한 줄.
- 글: `Cheats.WARN :55` «… 리그 대전에서도 먹어요 — 그 판은 기록에 «치트»로 남아요.», `LaunchSheet :686-687` 같게, `Cheats.java:8-18` 주석.
- 유가 치트 + 랭크: P1 = 유가(14) — 정산은 P2 만 보니 무관, 내 캐릭터 기록은 §6 `my_commit` 고침으로 칸 15.
- u166 «보기»(프레임 표시·대미지)를 나중에 넣으면 리그에선 계속 끔(HUD 이름표와 같은 줄 — u166 §6 «상호 배제 필수»).

---

## 10. 리그 경기 중 설정 — 체크포인트 길

### 지금
- 리그 판 ACT_CFG 는 `:499-505` 에서 막힘. 일반 판 «적용하고 이어하기» = `applyLive :702-724`(live.state 저장 → 코어 내림 → 새 EmuActivity 가 `resume` 상태를 되읽음) — 리그에선 이 길이 리그 확인(롬 md5·체크포인트 한 번 쓰기·무장)을 건너뛰므로 쓰면 안 된다.
- 유저: «리그 경기 불러오기(= 체크포인트 이어 하기)가 되는데 왜 그게 안 됨?» — 같은 체크포인트 길로 하면 된다.

### 새 동작
- 리그 판 ACT_CFG = 같은 창(`LaunchSheet.showInGame`). 창을 닫을 때 바로 먹는 것(`onClose`: `applyDisplay(); pushCoreOpts();` + 치트 `:573-576`)은 그대로 — 화면·필터·프레임 패치·런어헤드 등.
  «적용하고 이어하기»(onApply)만 `ranked() ? () -> applyLiveLeague(orig) : () -> applyLive(orig)`.
```java
/** 168: 리그 판 «적용하고 이어하기» — 점수가 걸린 경기면 체크포인트 → 리그 판을 다시 올림(새 창의 hubStart 가 그 경기를 체크포인트로 이어 함),
 *  경기 밖이면 그냥 다시 올림(준비 기록은 무효 — 점수 없음). 롬은 그 경기의 언어로 고정(아래) */
private void applyLiveLeague(final String orig) {
    if (!leagueHub) { leagueSuspend("설정 다시 올리기", null); return; }               /* 옛 한 판 — 쓰이지 않음 */
    final boolean live = hubMatchLive();                                              /* 결판이 막 섰으면 여기서 정산 → false */
    final String id = leagueId;
    gl.queueEvent(() -> {
        if (live && !leagueSaveCkpt()) { toast("저장하지 못했어요 — 그대로 둡니다"); Emu.nativeSetPaused(false); return; }
        Emu.nativeLeagueDisarm(); Emu.nativeSaveSram(); Emu.nativeUnload(); loaded = false;
        runOnUiThread(() -> {
            if (live) League.orCheat(id, cheatBitsSeen()); else cancelReady("설정 다시 올리기 — 대진 전");
            leaving = true; liveHubOff(); MainActivity.forgetLast(this);
            Intent i = new Intent(this, EmuActivity.class).putExtra("rom", orig).putExtra(EXTRA_LEAGUE_HUB, true);
            if (fromGame()) i.putExtra(EXTRA_FROM_GAME, true);
            startActivity(i); finish();
        });
    });
}
```
- 상태는 «playing» 그대로 — 새 창 `hubStart :1894-1897` 이 «준비가 아닌 열린 경기»로 보고 `leagueStart`(새 판 아님 → 체크포인트 불러오기 → `FROM_CKPT`, 토스트 «멈춘 자리부터 이어 해요» 그대로). 그 사이 앱이 죽어도 체크포인트가 있어 다음에 이어짐.
- 옛 창 onPause 는 `loaded == false` 라 체크포인트를 다시 안 씀(`:1007`), 새 창 onResume 의 지우기(`:1033`)는 `leagueStart` 가 이미 지운 뒤.
- **언어 고정(중요)**: 언어를 바꾸면 리그 사본 md5 가 달라져 `leagueVersionProblem :1078-1099`(`:1087` 롬 다름) → BLK_ROM(«기권만») 이 된다. 그래서
  `rankNewMatch :2675` 에서 `League.note(id, "lang", lang)`, `onCreate :84-96` 리그 판은 `lang = League.matchLang(League.openMatch(), readLang())`(열린 시작 경기에 적힌 언어가 있으면 그것)로 `Patcher.resolveLeague`.
  → 그 경기는 원래 판으로 이어지고, 새 언어는 다음 리그 판부터(글 없음). 언어를 적지 않은 옛 경기는 지금처럼.
- 조작 패치(mods)·빠른 롬은 리그 사본에 원래 안 들어감(`resolveLeague`) — 무관.
- «전체 설정 ›»(SettingsActivity) 고리: 지금 백그라운드 규칙(onPause 체크포인트 → onResume 지움) 그대로 — 코어는 안 내려감.

---

## B. 진행 중 작업과 합치기

| 순서 | 무엇 | 왜 그 순서 | 겹침 |
|---|---|---|---|
| 1 | **w165 마무리·커밋** | 168 의 1·2·3·6·9·10 이 같은 `EmuActivity` lgm 쪽(`lgmActions :3177-3290`·`lgmDrawer`·`lgmOnSettle` 둘레)·`LeagueMenu`·`LgmPages`·`docs/157_contract.md` 를 고친다. w165 는 그 둘레에 `lgmWhy`·`lgmOpenNow`·`lgmSettleId`·이름표 살핌·보드 MR 표를 넣었다 | 168 이 w165 의 `lgmOpenNow` 를 기권(대기 «기권»)에 쓴다 → w165 가 먼저여야 |
| 2 | **w165fx 합치기** | 4(2P색)는 거의 w165fx 몫, 5·7·8 이 w165fx API(`look_take_confirm` · `vpanel_icon_put`/팔레트 할당기 · 새 `LOOK_DUP` 생성기 · `me_b2p` 정리)를 딛는다 | w165 와 w165fx 의 EmuActivity 덩어리는 **안 겹침**(w165: 1248~3434 · w165fx: 2278·2326·3531~3633 — 이 폴더 `w165_emu.diff`·`w165fx_emu.diff` 로 확인). League.java·LeagueActivity 는 w165fx 만 |
| 3 | 168(이 설계) | 위 둘 위에 | — |
| — | u166(치트 바 칸·보기) | 코드 없음. 바 칸은 9번 알약이 대체. «보기»를 나중에 하면 168 뒤, 리그에선 끔 | `Cheats.java`(KEYS 끝에 붙이기)·`cheat.h`(CH_N) — 168 의 `MB` 비트는 `1 << CH_*` 라 칸이 늘어도 됨 |

합칠 때 손볼 것: w165 의 `MenuModel`/`LgmPages` 시험(h/run_jvm.sh menu·render)이 탭 3개를 가정 → 4개로. w165fx `reg/` 의 t_look 정답(나찰 프리셋)·연습 순서 시험이 5·7 로 바뀜.

---

## C. 위험

| # | 위험 | 막는 법 |
|---|---|---|
| R1 | **기록 정합성 — 멈춘 경기 되감기·무효 빠져나가기**: 리셋 한 번으로 멈출 수 있게 됐다. 체크포인트 파일이 사라지면 지금은 `voidKind` → «crash» → 허브가 묻지 않고 무효(157 post `:1371-1378`) — 지는 판을 멈추고 파일을 지우면 LP 없이 빠짐 | `League.voidKind :596`: `suspend == "user"` 이고 «resume» 이면 null(무효 없음 — 이어 하기·기권만). 멈출 때 체크포인트를 쓴 게 확인된 판만 그 표지를 단다(§A) |
| R2 | 시즌 도구를 경기 중·멈춘 경기 위에서 → 진 판 지우기 | `resetBlockedWhy(true)` 도 `startedOpen()` 이면 막음(글은 경기 이야기). 준비 기록은 무효(점수 없음) |
| R3 | 치트 면제가 진짜 버그를 가림 | 치트가 **실제로 쓴**(MB) 항목만, 그 항목이 설명하는 검사만(DIFF → 손잡이, TIME → 시간 0x80). 대진·포인트·결판 비트는 그대로 |
| R4 | 체크포인트 정확성 — 게임 안 이어 하기에서 불러오기와 무장 사이에 프레임이 돔 | `hubResumeOpen` 은 멈춘 채(`hubStartAgain` 과 같게) · 허브는 H_TITLE(기존 «타이틀인 채 싸움» 불변) · 불러오기가 걸쇠·덧판·이름표를 지우고(`native.c:1323-1345`) `leagueStart` 가 이름표를 다시 걺 · 치트 값은 `cheat_before_save` 가 체크포인트에서 빼 둠 |
| R5 | 설정 다시 올리기에서 언어가 바뀌어 롬이 달라짐 | 경기 언어 고정(§10). 고정 실패(옛 경기)면 지금 막힘 카드 그대로 — 그때만 기존 글 |
| R6 | `.prac`/H 크기 628 | H 에 새 칸 없음: 연습 검질 = 옛 `me_pad`(pr_me_check 가 0~2 확인), 새 허브 번호 8 은 저장 안 됨(H_MATCH 만), PO·pr_inj·pr_back·pr_sty_auto·머리말 칸 원래 값은 H 밖. `_Static_assert` 그대로 |
| R7 | `LEAGUE_NHUB 15` · `LEAGUE_NSTAT 26` · `CHEAT_NSTAT 16` · `LEAGUE_NMYPICK 8` · `LEAGUE_NAUTO 5` | 하나도 안 늘림 — 새 상태는 새 JNI(`nativeHubPickOnlyStatus` · `nativeCheatMatch`) |
| R8 | 잠금 순서 | L_mu → K_mu(`look_take_confirm`) · L_mu → C_mu(`cheat_match_bits` from `arm_locked`)만. C_mu 안에서 L_mu 안 잡음(cheat_tick 은 그 전에 owner) |
| R9 | 덧판 타일·팔레트 예산(새 장면 셋) | LgmFuzz(20000판) + 새 장면 — W 타일 ≤ 496 · 팔레트 ≤ 16 · 예외 0 |
| R10 | 둘째 판 팔레트 빌리기 충돌(머리말 빨강 + 도장 + w165fx 아이콘) | 상대 화면은 한 팔레트를 머리말·도장이 같이, 내 화면은 w165fx 아이콘만. 못 빌리면 글자만(색 없음) |
| R11 | pick-only 에서 Java 가 늦으면(백그라운드) 무장 없는 싸움이 시작될 수 있음 | 무장이 없어 기록 0 · 돌아오면 그대로 리셋(−4). 序章을 안 넘기므로 30초 가까이 여유 |
| R12 | 옛 시험이 옛 동작을 정답으로 가짐(t_cheat 리그 잠금 V-6 · t_practice 순서 · 153 순서 12 · t_look 나찰 색 · JVM 탭 3) | 고칠 시험을 목록으로 따로 커밋(«정답이 바뀐 것» — 설명 한 줄씩) |
| R13 | PadView 배치 파일에 새 이름 | 이름으로 찾으므로 옛 파일 무해(없으면 기본 자리) |

---

## D. 시험

### 호스트 하네스(ctypes .so — `u153/impl-nat/build.sh` · w165fx `env.sh` 꼴, 롬 6판 · 시계 고정 FIXT)
- **t_po.py**(6): 타이틀 → `league_hub_pick_only` → 머리말 «내 캐릭터» 타일 · 고르는 동안 R_OWN 8 · 캐릭터·검질·카드 대본 → 이야기 시작에 MY 있음 · L 무장 0 · PO.done 뒤 입력 0 · 고르기에서 B → H_TITLE · −5 리셋 길 · 무작위 칸 · 유가 치트 + 무작위 칸(칸 15·ch −1) · 그다음 −4 자동 진행이 같은 캐릭터·검질·카드로 경기(P1 블록).
- **t_prac_order.py**(7): 14명 × 2검질 × 롬 6판 — 나 → 검질 화면 A → 캐릭터 고르기로 돌아옴 → «상대 선택»(빨강) → 더미 A/B → 내 칸 자동 확정 → 검질 자동 → 카드 → 경기: P1 = (나, 고른 검질) · P2 = (더미, A/B).
  검질 화면 B → 나부터 다시 · 연습 메뉴 «상대 고르기» = 검질까지 자동 · 무작위 칸 고정 · 연습 경기 중 저장/불러오기(.prac — `me_pad` 남음) · 옛 .prac(me_pad 0) → 검질은 사용자 · `sizeof H == 628`.
- **t_hdr.py**(8): 한글판 19타일·순정판 20타일 · 0x163 안 건드림(한글판) · 빌린 팔레트가 그 화면 칸에 안 쓰임 · 깜빡 36프레임 · `league_hub_before_save` 뒤 원래 타일·칸 값(저장 상태 해시 = 허브 끈 쌍둥이) · 떠날 때 되돌림.
- **t_cheat_league.py**(9): 랭크 무장(손잡이) + CPU 세기 최강·시간 무한·내 공격력·상대 한 방 → 쓰기 확인 · `cheat_match_bits` 비트 · 무장 때 비움 · 연습 흐름은 여전히 쉼(why 3) · 치트 없는 판 결정성(t_determ 그대로). 기존 `t_cheat.py` V-6(리그면 안 씀)은 «리그면 씀 · why 4»로 정답 고침.
- **t_look_sty.py**(5): 14명 × 프리셋 14 × 내 색 2 — 검질 화면 STYC 0↔1 에서 팔레트 0 세 색 같음 · 경기(수라·나찰 판) P1 팔레트 같음 · «기본»은 다름(원래대로) · 미리보기 그림 저장(눈 확인).
- **t_suspend.py**(A·1·3b): 2라운드 도중 체크포인트 → 타이틀 리셋 → 불러오기 + FROM_CKPT → 같은 입력이면 결판·결과 비트가 멈추지 않은 쌍둥이와 같음 · 결판 프레임에 멈추기 → 정산 길.

### JVM (`u165/h/run_jvm.sh` · `u165/fuzz`)
- MenuModel.lobby 줄(타이틀/고르기/열린 경기/무효 가능/main 없음) · LeagueMenu ST_LOBBY 입력 · 서랍 4탭 돌기·기억(옛 lastTab 0~2) · 리그 탭 두 번 묻기(첫 A 맥박 · CONFIRM_MIN · ▲▼ 거둠) · LgmFuzz 새 장면 셋.
- League: `settle(…, cheatBits)` — DIFF 면 손잡이 면제·TIME 이면 0x80 만 면제·그 밖은 그대로 보류 · `cheat` 표 · `voidKind`(suspend user → null) · `resetBlockedWhy(true)`(liveHub 무시 · 시작 경기면 막음) · `newSeason(true)/restartRanked(true)` 보관 파일·되돌리기 · `matchLang`.
- 문자열 반사(w165fx `StringsTest` 꼴): 리그 판 길에 «리그»+«못/막/꺼져/안 먹» 글 0.

### 기기 흉내(`u165/sim` — 진짜 EmuActivity 바이트코드 + native.c JNI + 164 코어)
새 장면: `later`(쉼 → 나중에 → **LeagueActivity 시작 0** → 타이틀 → A → 이어서 → 결판) · `reset`(바 리셋 = 같음 · 저장·로드 칸 없음 · 길게 누르기 무반응) · `cfg`(리그 경기 중 설정 → 적용 → 새 창이 체크포인트로 이어 함, 언어 바꿔도) ·
`newchar`(결판 → 새 캐릭터 → 고르기만 → 겹창 → 자동 → VS → 경기 · 뒤로 나가면 main 그대로) · `lobby`(타이틀 OPTION → 대기 → 리그 탭 → 새 시즌 두 번 A → 시즌+1, 처음부터) · `cheat`(알약 → 창 → CPU 세기·시간 무한 → 정산 보류 없음 · `cheat` 표 · 결판 «치» 도장) ·
기존 12장면(w165 `run_sim_all.sh`) 회귀.

### 에뮬레이터·기기
세로·가로: 치트 알약 자리·배치 편집 · 대기 메뉴 손가락 · 나/상대 화면 빨강·도장 · 연습 순서 · 리그 설정 다시 올리기 · 언어 바꾼 뒤 이어 하기 · 120Hz.

---

## E. 합친 구현 순서

| 단계 | 일 | 시험 | 대략 |
|---|---|---|---|
| P0 | w165 마무리·커밋 → w165fx 합치기(겹침 없음 — 확인) → 둘의 시험 묶음 | w165 sim 12 · u165fx t_slash_* · reg | 0.5일 |
| P1 native | ① cheat.c 리그 허용 + `MB`/`cheat_match_bits` + league.c `arm_locked` 비움 ② league.c pick-only(PO · −5 · status JNI · my_commit 유가) ③ 연습 H_PICK_STY1 + look_take_confirm 단추 ④ 머리말 «내 캐릭터»·빨강·도장·깜빡(hub_glyphs.py · vpanel 공용 할당기) ⑤ look_gen 프리셋 합치기 + tri 보증 | t_cheat_league · t_po · t_prac_order · t_hdr · t_look_sty + 기존 t_practice·t_cheat·t_look·153 묶음(정답 고친 것 따로) | 2.5일 |
| P2 Java 흐름 | §A `leagueSuspend`·`hubResumeOpen` · §1 «나중에»·LeagueActivity 길 정리 · §3 handleAction·PadView `setRankedBar`·셋째 줄 · §10 `applyLiveLeague` + 언어 고정 · §9 Java(cheatSetup·poll·orCheat·settle 면제·표시) · §6 Java(pick-only·rankTick·«새 캐릭터» 늘) · §7·8 띠 글 | JVM League · sim later/reset/cfg/newchar/cheat | 2일 |
| P3 게임 안 메뉴 | MenuModel K_LOBBY·LeagueInfo · LeagueMenu ST_LOBBY·OPTION 탭·4탭·두 번 묻기 · LgmPages lobby/league/전적 목록·quit · EmuActivity lgm 동작·멈춤 바 «리그 메뉴» · League.resetBlockedWhy(true)·leagueInfo·rulesText | JVM menu/render/fuzz · sim lobby | 2.5일 |
| P4 | PadView «치트» 알약 + LaunchSheet.showCheats | 에뮬 · ui_shots | 0.5일 |
| P5 | 글·문서(Cheats/LaunchSheet/LeagueActivity 규칙·157_contract·handoff) · 미리보기 · CI 빌드 · 기기 | 전 묶음 | 1일 |
| | **합** | | **약 9일** |

P1 ①~⑤ 는 서로 독립이라 나눠 돌려도 됨(같은 league.c 를 ②③④ 가 고치므로 한 가지에서 차례로 합치기). P2 의 §9 는 P1 ① 다음, §6 Java 는 P1 ② 다음.

---

## F. 열린 결정(기본안으로 진행 — 유저가 바꾸면 한 곳만 고침)

| # | 물음 | 기본안 |
|---|---|---|
| D1 | 치트 판도 LP 를 반영? | 반영 + «치트» 표(유저 «리그 때도 쓸 수 있게»). 바꾸려면 `applyRanked` 앞에서 `cb != 0` 이면 «치트 판 — LP 그대로» 갈래 하나 |
| D2 | 리그 타이틀에서 뒤로 | 대기 메뉴(거기서 «리그 나가기 › 내 게임 / 게임 목록»). LeagueActivity 는 런처에서만 |
| D3 | 연습 무작위 칸 | 첫 검질 화면에서 멈춘 캐릭터로 고정 |
| D4 | 고르기 커서 빨강 | 실측 뒤 2단계(없어도 머리말·도장·깜빡으로 충분) |
| D5 | 연습 «상대 고르기» 때 검질 | 유지(바꾸려면 타이틀로 → 연습 대전) |

---

## G. 검토 (코드와 맞춰 봄 · 읽기만 · 코드 안 고침)

대조한 코드: `w160`(8e0a1a4 — 줄 번호 기준), `w165fx`(5e33641 — native 줄 번호는 이쪽), `w165`(**이제 커밋됨 df1f509** — 같은 4파일: EmuActivity·LeagueMenu·LgmPages·docs/157_contract). 위 B 표의 «커밋 안 된 고침»·P0 «w165 마무리·커밋»은 «df1f509 합치기»로 고친다.
아래 K 는 **설계대로 짜면 깨지는 것**(꼭 고침), M 은 빠진 경우, S 는 더 단순한 길, 그 밖은 작은 것.

### G-0. 한눈에

| # | 어디 | 문제 | 고침(요약) |
|---|---|---|---|
| K1 | §6 pick-only | 허브 3(H_PICK_ME)에 닿으면 hubTick 이 **랭크 경기 기록을 만들려 함** → 첫 판은 바로 타이틀로 튕기고, 결판 뒤 «새 캐릭터»는 지난 상대와 쓰레기 «준비» 기록 | 새 허브 상태 `H_PICK_SOLO`(9) 또는 Java `!rankPickOnly` 가드 |
| K2 | §A hubResumeOpen | 허브가 돌려보내는 중(H_RETURN·nav 2)에 부르면 체크포인트 경기 입력을 **15초 동안 대신 누르기가 덮음** | 허브 1/6·nav 0 일 때만 · 아니면 미뤘다가 |
| K3 | §C R1 | voidKind 만 고치면 EmuActivity 의 «crash» 대체 줄이 **그대로 자동 무효** | voidStarted 한 곳 + 대체 두 줄 + 표지 지우기 규칙 |
| K4 | §A·3b | 앱을 다시 켜면 hubStart 가 **멈춘 경기를 바로 이어 함**(«타이틀에서 A 로»와 어긋남) | 사용자 멈춤 표지가 있으면 타이틀에서 기다림 |
| K5 | §2 대기 자격 | `hubLastState == 1` 은 데모 중에도 참 → 데모 중 «상대 찾기»가 겹창만 남음 | 메뉴 화면(hubDualV[5]==0) 조건 · 커서 2 는 기존 `R_MCUR = 2` 길 |
| K6 | §1·D2 | 덧판(lgm)을 못 쓰는 판에선 «타이틀 뒤로 = 대기»가 막다른 길 | 못 열면 예전 갈래(게임/목록) |
| M1 | §2 시즌 | 멈춘 경기가 있으면 «멈춘 경기를 먼저 끝내요» 글 = 유저가 싫다는 «안 돼요» · 새 시즌 뒤 «오늘» 세션 안 바뀜 | 두 번 묻기 글에 «기권패로 닫고» · `sessionReset` |
| M2 | LeagueActivity | 리그 판을 홈으로 내려 둔 채 런처로 들어오면 «게임 속 리그를 닫은 뒤에…» 3곳 | liveHub 면 줄을 숨기고 «게임으로» 하나 |
| M3 | §1 | LeagueActivity 로 새는 길 하나 더(leagueLeave 1468) | 허브면 hubReturn(−1) |
| M4~M11 | 여러 곳 | 아래 G-2 | — |
| S1 | §10 | 리그 사본에서 다시 올려야 먹는 옵션은 언어·원버튼·컬러 고르기 셋뿐 | 그 셋이 바뀐 때만 체크포인트 길 · 경기 언어는 rom_md5 로 |
| S2 | §7 | 검질 화면 왕복(B 타이밍·뽑기·유가) 위험 | 실측 실패 시 2안: 내 화면 A 수라·B 나찰 |

### G-1. 꼭 고칠 것

**K1. pick-only 화면이 hubTick 의 «허브 3 → 랭크 경기 기록»에 걸린다**
- 근거: `EmuActivity.java:1936` `if (hubRanked && st == 3 && leagueId == null && hubCard == null && !lgmShown …) { if (!(rankQ != null && !rankQRevealed) && !rankNewMatch()) return; }`.
  pick-only 는 설계상 `H.st = H_PICK_ME`(= 3)이고 `hubPickOnly` 가 `rankQClose(false)` 하므로 겹창도 없다 → 바로 `rankNewMatch()`.
- 결과 ① 첫 판(rankOppV null): `rankNewMatch` 가 `hubReturn(-1)` + 토스트 «경기를 만들지 못했어요 — 상대 정보가 없어요» → 고르기 화면이 열리자마자 타이틀로.
  ② 결판 뒤 «새 캐릭터»(hubReturn 은 rankOppV 를 안 지움): **지난 상대·지난 손잡이로 새 «준비» 기록**이 생기고 `leagueArmed = true`(native 는 무장 없음)·`leaguePoll`·`lgmMatchStart` 가 돈다 → 다음 −4 의 hubReturn 이 무효로 닫아 기록에 «취소» 한 줄씩 쌓임. `hubText case 3` 도 «vs 지난 상대» 띠.
- 고침(권함): native 에 새 허브 상태 **`H_PICK_SOLO`(enum 끝 — v[0] = 9, .prac 은 H_MATCH 만 저장하니 무관)**. Java 의 `st == 3` 쓰는 곳(1936 경기 만들기 · `hubText case 3` · `rankCapTick` 의 `st == 3 || st == 4` · `hubPickBack` 의 `hubLastState == 2 || 3`)이 저절로 비켜 간다.
  Java 가 더할 것: `hubPickBack` 에 9(뒤로 = 바로 타이틀), `hubText`·`hubBannerNeeded` 에 9(«내 캐릭터 고르기 — 고르면 상대를 찾아요»), 완료 감지 `hs[0] == 9`.
  native 가 더할 것: H_PICK_ME 를 보는 곳 — `league_hub_look_ctx`(FREE), «대진 전 타이틀로»(PO 비움), `hdr` 되돌리기 — 을 9 에도. 위 설계의 `pick_only_tick` 은 `case H_PICK_SOLO:` 몸통으로.
  (대안: H_PICK_ME 그대로 두고 1936·hubText·rankCapTick·hubPickBack 모두에 `!rankPickOnly`/`rankPickOnly` 갈래 — 빠뜨리기 쉬워 비권장)

**K2. hubResumeOpen 을 허브 1·6·nav 0 밖에서 부르면 경기 입력이 덮인다**
- 근거: «끝나지 않은 경기가 있어요» 카드(`EmuActivity.java:2663-2675`)는 `rankNewMatch` 가 `hubReturn(-1)` 한 **뒤**에 뜬다 → native 는 `H_RETURN · nav 2`.
  nav 2 는 `league_ovr_on = 1`(league.c w165fx `:689-697`)이고 `native.c:446` 이 `league_ovr_on ? league_ovr_mask : (사용자 입력…)` 이라 **입력을 통째로 갈아 끼운다**. 체크포인트(경기 화면)를 불러오면 메뉴가 안 떠서 `d > 900`(15초)까지 손이 안 먹고 200·380 프레임째 A 가 눌린다.
  pick-only 끝에서 이어 하기를 붙여도(M5) 같은 일.
- 고침: hubResumeOpen 첫머리
  ```java
  int[] hs = Emu.nativeLeagueHubStatus();
  if (hs == null || hs.length < 8 || !(hs[0] == 1 || hs[0] == 6) || hs[7] != 0) { hubResumePending = true; return true; }   /* 허브가 타이틀·찾기에 서면 hubTick 이 소비 */
  ```
  hubTick: `if (hubResumePending && (st == 1 || st == 6) && hs[7] == 0 && hs[8] >= hubWaitGen && !leaving) { hubResumePending = false; hubResumeOpen(); }`. 카드 «이어 하기»·대기·M5 모두 이 한 길.
  (hubStart 길은 `nativeLeagueHub(true)` 직후라 H_TITLE·nav 0 — 지금도 맞음)

**K3. R1(사용자가 멈춘 판의 «무효로 닫기» 막기)은 voidKind 만으론 안 막힌다**
- 근거: `leagueBlocked(kind)` `:1352` `if (vk == null && kind != BLK_ROM) vk = kind == BLK_BADCKPT ? "ckpt" : "crash";` → 허브면 `:1372-1377` 이 **묻지 않고 자동 무효**. `leagueResolve :1397` 도 같은 대체.
  체크포인트를 지우면 `leagueStart` 가 `nockpt` → `BLK_NOCKPT` → voidKind 가 null 을 돌려도 여기서 «crash» → LP 없이 빠진다(R1 이 막으려던 바로 그 길).
- 고침:
  1. 마지막 관문 `League.voidStarted()` 에 «`suspend == "user"` 이고 `m.app == appVer`(앱 판이 그대로)면 false». voidKind 도 같은 조건이면 null.
  2. EmuActivity 대체 두 줄(`:1352`·`:1397`)에 `&& !League.userSuspended(m)`. 그 판이 못 이어지면 카드는 **«기권하고 계속»만**(자동 무효 없음).
  3. 표지는 **이어 하기에 성공하면 지운다**(`leagueStart` 의 `fromCk` 뒤 — 그 뒤 진짜 앱 멈춤은 예전 규칙). 앱을 업데이트해 체크포인트를 못 읽는 판(`app`·판이 다름)은 사용자 탓이 아니므로 무효 허용.
  4. `League.note(id,"suspend","user")` 를 `setStatus(resume)` 와 **같은 저장 한 번**으로(`League.suspendUser(id, why, cheatBits)`) — 두 저장 사이에 죽으면 표지 없는 resume 이 남는다.
  5. LeagueActivity `voidKindNow`·열린 경기 카드도 같은 함수로.

**K4. 앱을 다시 켜면 «저장 후 타이틀»로 멈춘 경기가 곧바로 이어진다**
- 근거: `hubStart :1895-1897` 은 «준비가 아닌 열린 경기»면 무조건 `leagueStart`. 리셋·«나중에»로 멈추고 앱을 끈 뒤 리그를 다시 열면(런처·셋째 줄 갈아타기 모두) 로고 직후 싸우던 화면이 뜬다 — 3b «타이틀로 · A 로 이어서»와 어긋남.
- 고침: hubStart 는 **사용자 멈춤 표지가 있으면 이어 하지 않고 타이틀**(A · 대기 «▶ 멈춘 경기 이어서» = hubResumeOpen). 표지 없는 것(onPause 체크포인트 · §10 설정 다시 올리기 · 앱 멈춤)은 지금처럼 바로.
  `EXTRA_HUB_GO`(갈아타 온 판)도 표지가 있으면 `rankSearchStart` 대신 타이틀에서 멈춤(st 6 에서 hubResumeOpen). LeagueActivity «멈춘 경기 이어서 하기»(`:224-231 goHub`)는 새 extra `EXTRA_RESUME_NOW` 로 바로 이어 하게.

**K5. 대기 자격 — 타이틀 메뉴가 정말 떠 있어야 한다**
- 근거: league.c `case H_TITLE` 은 `if (menu)` 안에서만 일하고 메뉴가 사라져도(타이틀 방치 → 데모·인트로) `H_TITLE` 그대로 → `hubLastState == 1`. 반면 `H_SEARCH` 는 메뉴가 없으면 바로 `H_TITLE`(`:776`) → 데모 중 대기 «상대 찾기»는 겹창만 뜨고 go 를 못 함.
- 고침: `lgmLobbySync` 에 `hubDualV != null && hubDualV.length >= 6 && hubDualV[5] == 0`(메뉴 화면 0 = 타이틀). 대기가 열린 동안엔 코어가 멈춰 데모로 안 넘어간다.
- 커서 2 문제(설계 §6 «커서 조건»): 조건을 풀어 «실측으로 확인»하기보다 **지금 코드가 이미 쓰는 길**을 쓴다 — «대신 누른 A 를 게임이 안 받았다» 때 `ram[R_MCUR] = 2`(`:808`·`:867`). H_SEARCH 의 go·`PO.req` 가 «메뉴 · nav 0 · R_MCUR ≠ 2»면 그 프레임에 `R_MCUR = 2` 를 쓰고 다음 프레임에 `hub_go_fixed`/`hub_go_pick_only`(둘 다 거기서 `R_MCUR = 0` 을 쓰고 A).

**K6. 덧판을 못 쓰는 판에서 D2 가 막다른 길**
- 근거: 설계 §2-4 `lgmWantLobby` «못 쓰면 조용히 cancelPause(옛 길 없음)». lgm 은 옛 native·게임 사각형 못 찾음·그림 실패면 못 연다 → 타이틀에서 뒤로가 아무 일도 안 함.
- 고침: 대기를 못 열면 뒤로 = 예전 `hubLeaveTo(0)` 의 앞 두 갈래(게임에서 왔으면 그 게임 · 아니면 **게임 목록** `goList`). 순위표·시즌 도구는 그때만 런처 «리그 순위표»(LeagueActivity 는 남아 있음). 대기는 `Prefs.fx`(결판 연출 끄기)와 무관하게 연다.

### G-2. 빠진 경우

**M1. 시즌 초기화 + 멈춘 경기 / 세션**
- §2-5 는 시작한 경기가 열려 있으면 리그 탭에 «멈춘 경기를 먼저 끝내요»를 띄운다 — 경기 이야기라도 유저가 싫다는 «안 돼요» 꼴. 리셋 한 번으로 멈춘 경기가 생기므로 자주 마주침.
- 고침: 줄은 그대로 두고 **두 번 묻기 글에** «멈춘 경기(vs 칼끝노인)는 기권패로 닫고 새 시즌 · A 한 번 더». 확정이면 `League.newSeason(true, forfeitOpen=true)` / `restartRanked(true, true)` 가 **한 저장 안에서** 기권 반영 → 보관 파일(기권 뒤 상태) → 리셋. 진 판을 지우는 길이 아니다(기권패는 지난 시즌에 남음 · 처음부터는 어차피 LP 0·배치부터라 피할 이득 없음). 기권 미리보기 LP 는 `forfeitPreview` 로 같은 줄에.
- 새 시즌 뒤 «오늘 4승 1패 +152 LP»·rank0 이 그대로: `sessionStart :1407-1414` 는 같은 날이면 아무것도 안 함. 새 시즌·처음부터 뒤엔 **`League.sessionReset()`**(새 — 무조건 새 줄). restartRanked 는 ranked 를 통째로 바꿔 session 이 없어지므로 지금도 새로 됨.

**M2. LeagueActivity 의 liveHub 글 3곳** — `:714 hubWhy`·`:758` 열린 경기 카드·`:876` «다시 읽기» 토스트 «게임 속 리그를 닫은 뒤에 할 수 있어요». 리그 판을 홈 버튼으로 내려 둔 채(liveHub 켜짐) 런처 «리그 순위표»로 오면 보인다. liveHub 면 그 줄·버튼을 숨기고(글 없이) «게임으로 돌아가기»(`FLAG_ACTIVITY_REORDER_TO_FRONT` 로 떠 있는 EmuActivity 앞으로) 하나만. 같은 까닭으로 `resetBlockedWhy()`(인자 없는 옛 것)의 liveHub 글도 LeagueActivity 에선 숨김.

**M3. LeagueActivity 로 새는 길 하나 더** — `leagueLeave() :1468` `if (leagueDone || !leagueArmed) { leagueExit(null); return; }`(onBackPressed 가 lgmEligible 거짓인 판에서 여기로 옴). 허브면 `hubReturn(-1)`. §1 표에 추가.

**M4. 승리 대사 중 리셋·나중에** — leagueSuspend 첫 갈래(`leagueDone` → `hubReturn(-1)`)가 결판 화면을 건너뛴다(LP 가 말없이 바뀜). `leagueDone` 이고 정산된 판이면 `leagueLeave` 의 ps 갈래(`postSkip`/`leagueExit(id)` → 결판 메뉴)로 보내고, 결판 메뉴의 «그만»이 타이틀.

**M5. 대기 «내 캐릭터 바꾸기» + 멈춘 경기** — pick-only 끝 → `rankNext(false)` → `rankNewMatch` 가 열린 경기 때문에 null → «끝나지 않은 경기» 카드(쓸데없이 상대 찾기 연출까지 다 봄). pick-only 끝에서 `League.openMatch()` 가 시작된 경기면 **setMain 만 하고 hubReturn(−1)**(타이틀 — 대기 첫 줄이 «▶ 멈춘 경기 이어서»). 내 캐릭터는 다음 새 경기부터(멈춘 경기는 체크포인트의 캐릭터 그대로).

**M6. 연습 static 비우기 자리** — 설계는 `pr_inj·pr_back·pr_sty_auto` 를 `pr_apply·league_practice_hub` 에서만 0 으로. `league_practice_title`(불러오기·앱 리셋 뒤 — league.c `:1066`)·`league_practice_return` 에서도 비운다. 안 그러면 검질 화면에서 슬롯 불러오기 → 남은 `pr_back` 이 다음 고르기 화면에 B 를 넣음.

**M7. 연습 무작위 칸 + 유가 치트** — STY1 에서 핀을 박으면(D3) H_PICK_OPP 가 그 캐릭터 칸을 직접 고르므로(`nav_to(pin)`) cheat.c `yuga_tick` 의 «가운데 칸 확정»(`hover == 60`)이 안 서서 **유가가 안 나온다**(지금은 첫 판 pin 0 → 칸 15 → 유가). 유가 치트가 켜져 있으면 핀을 안 박는다 — cheat.c 에 `int cheat_yuga_on(void)`(C_mu 만, L_mu → C_mu 순서 허용).

**M8. STY1 들어가는 A 가 안 먹을 때** — 사용자가 고르기 화면이 받기 전(R_CSUB ≠ 04)에 결정하면 대신 누른 A 가 버려진다. 설계는 900프레임(15초) 뒤 예전 순서로 — 너무 길다. `auto_tick AP_CHAR` 처럼 `csel && R_CSUB == 4` 면 16프레임마다 A 다시(3번), 그래도 안 되면 `H_PICK_ME1` 로 돌아가 사용자가 다시 결정.

**M9. look_take_confirm 의 A/B** — 가져갈 때 `K.g_first` 를 읽지 말고 `gate_confirm` 에서 `K.conf_pend = first == IN_B ? 2 : 1` 로 넣어 둔다(그 사이 새 누름이 g_first 를 바꾸는 틈 없음). H_PICK_ME1 은 `!= 0` 그대로.

**M10. §10 정산이 막 선 판** — `applyLiveLeague` 에서 `hubMatchLive()` 가 정산까지 했으면(leagueDone) 다시 올리지 말고 결판 메뉴부터. 바뀐 옵션은 결판 뒤 «타이틀로»에서 한 번 다시 올림(S1 의 셋 중 바뀐 게 있을 때만).

**M11. 무작위 칸 STY1 핀의 뜻** — 무작위 칸을 A 로 확정하면 검질 화면에서 뽑기가 ~370프레임 돌고 그동안 결정이 안 받힌다(`AP_STYLE` 의 900 여유가 그 까닭). 핀 = «뽑기가 끝나 받기(CSUB 04)가 된 뒤의 R_HOVER». 설계 §7 «이 화면에서 멈춘 캐릭터» 글을 그렇게 고치고, t_prac_order 의 무작위 칸 대본에 뽑기 기다림을 넣는다.

### G-3. 더 단순한 길

**S1. §10 — 다시 올려야 먹는 옵션은 셋뿐**
- 리그 사본은 `Patcher.resolveLeague :56-85` 가 원본 + 한글패치만 굽는다(조작 패치·빠른 롬·배경음악 없음 — `musicNote = null`). 화면·필터·프레임 패치·런어헤드·띠·깜빡임 줄이기는 `LIVE_CORE_OPTS`(`:665-667`)·`applyDisplay` 로 창을 닫을 때 먹는다.
- 다시 올려야 먹는 것: **언어**(그 경기는 고정이라 어차피 다음 판) · **원버튼 `ngp_ss2sp`**(LIVE_CORE_OPTS 에 없음 — 코어가 올릴 때만 읽음) · **컬러 고르기 켬/끔 `Look.K_ON`**(lookSetup 은 loadCore 에서만).
- 그래서 리그 판 «적용하고 이어하기» = 바뀐 값이 원버튼·컬러 고르기면 체크포인트 길, 아니면 그냥 닫기(onClose 와 같음). 언어만 바뀌었으면 다시 올리지 않고 다음 리그 판부터(글 없음). 코어를 내렸다 올리는 위험(R4·R5)을 대부분 피함.
- 경기 언어 고정은 새 note(`lang`) 대신 **경기에 이미 적힌 `rom_md5` → `League.romLabel` 에 «한글패치»가 있나**로 정한다(`leagueVersionProblem :1078-1099` 이 첫 판에 적음 — 옛 경기도 됨). ja↔en 은 같은 롬(md5 같음)이라 막힘이 없고 `ngp_language` 만 다름.

**S2. §7 2안(실측 실패 시)** — 검질 화면을 오가지 않고 **내 캐릭터 화면에서 A = 수라 결정 · B = 나찰 결정**(상대 화면의 «A 수라 · B 나찰 더미»와 같은 규칙). w165fx 에서 B 는 2P색이 빠져 «보통 색 결정» 중복일 뿐이라 연습 HOLD(H_PICK_ME1)에서만 뜻을 바꿔도 다른 모드와 무관(M9 의 1/2 를 그대로 씀). 검질 그림을 미리 못 보는 대신 B «뒤로» 타이밍·무작위 칸 뽑기 기다림·유가(M7)·A 재시도(M8)가 모두 없어진다. 띠 «① 내 캐릭터 · A 수라 · B 나찰». 순서: STY1 하네스 실측 → R_CSUB·B 받힘이 롬 6판 중 하나라도 어긋나면 이쪽(열린 결정 D8).

### G-4. 작은 것

- **치트 알약 자리**: 세로에서 OPTION 알약은 반폭 `0.10 × min(w,h)` = 화면 폭 **0.40~0.60**(PadView `:791-794`). 설계 `(0.36, 0.955, ×0.90)` 은 0.27~0.45 라 **0.40~0.45 가 겹친다**. 세로 기본은 x **0.27**(0.19~0.35 · 십자 아래끝 ≈ 0.76h + 0.17w ≈ 0.84h 라 0.955 줄은 빔) 또는 0.73. 가로 `(0.38, 0.96)` 은 반폭이 높이 기준이라 안 겹침 — 그대로.
- **`Cheats.DIFF` 상수가 없다**(`Cheats.java:29` 는 CARDS·TIME·POW·YUGA 만) — `DIFF = 7`(KEYS 의 "diff") 추가. `Cheats.names(bits)` 도 새로.
- **메뉴 알약 길게(ACT_QSAVE)**: 무시해도 PadView `handleHold` 가 진동을 내고 `handleFired` 로 그 탭(바 열기)을 먹는다 → 리그 판(`setRankedBar`)이면 길게 누르기 타이머를 아예 안 건다(길게 눌러도 그냥 탭).
- **머리말 깜빡**: 상대 화면 머리말은 `csel_f >= 20` 부터 그려지고(`:825`·`:850` — 고르기도 그때부터) 연습 진입은 `csel_f = 10` → 깜빡은 «10~46»이 아니라 **«20~56»**(고르기는 막지 않음).
- **치트 창 «세이브에 남기기·세이브 되돌리기»(올카드 2)**: 리그 판 세이브는 `League.saveDir()` — `sheet.cheatRom`(원래 롬)으로 보관·되돌리는 `.flash` 가 어느 폴더 것인지 확인하고, 리그 판에선 그 줄을 숨긴다(엉뚱한 세이브를 되돌리지 않게).
- **«재대결» 흐림 글**: «이 조합은 아직 못 해요»·«3판을 다 했어요»(MenuModel `:282-283`)도 «못 해요» 글 — 리그 탓은 아니지만 유저 «뭐든»: 못 쓰면 줄을 빼고 이유 글 없음(칼집 높이가 바뀌므로 LgmFuzz).
- **치트 이름표**: `cheatPoll :3415` 의 «치트» 이름표(왼쪽 위)가 리그 판에서도 켜지면 HUD 이름표(157 post)와 겹치는지 확인 — 기본은 리그 판엔 안 띄우고 결판 «치» 도장·기록만.
- **서랍 탭 기억**: `LeagueMenu :751 Math.min(2, p.lastTab)` 과 `League.menuPrefs` 파서 둘 다 0~3 으로(설계는 firstTab 만 적음).
- **베기 색 이어 하기**: 체크포인트 이어 하기는 `nativeLeagueLook → look_set_match` 로 **몸 컬러만** 되살리고 베기 색(`K.fx_sel`)은 타이틀에서 0 이 된 채(look.c title 갈래). hubStart 이어 하기도 같은 옛 문제지만 §A 로 자주 쓰게 된다 → 경기 기록 look 에 fx 를 적고 같은 자리에서 넣는다(w165fx 의 Look fx 값).
- **§3 셋째 줄 «연습 대전»**: 시작한 경기가 도는 동안엔 타이틀 메뉴가 안 보여 handoff 가 안 선다 — 그 갈래(`leagueSuspend(…, switchSession)`)는 사실상 안 쓰임. 지우지 말고 방어로만.
- **E 일정**: K1~K6·M1~M11 몫 +0.5~1일(약 10일). 시험은 G-6.

### G-5. 열린 결정에 더할 것

| # | 물음 | 기본안 |
|---|---|---|
| D6 | 멈춘 경기가 있는데 새 시즌·처음부터 | 막지 않고 두 번 묻기 글에 «기권패로 닫고» → 확정이면 기권 뒤 리셋(M1) |
| D7 | 멈춘 경기를 둔 채 앱을 껐다 켜면 | 타이틀에서 기다림 · A·대기로 이어서(K4). 앱 멈춤·백그라운드 체크포인트는 예전처럼 바로 |
| D8 | 연습 검질 고르기 | 실측이 맞으면 게임 검질 화면(STY1) · 아니면 내 화면 A 수라·B 나찰(S2) |

### G-6. 더할 시험

- sim `newchar`: «첫 판(rankOppV null)»·«결판 뒤(rankOppV 남음)» 둘 — pick-only 동안 **경기 기록 0건**·`leagueId == null`·토스트 0(K1).
- sim «끝나지 않은 경기» 카드 → 이어 하기: 체크포인트 첫 프레임부터 `league_ovr_on == 0` · 사용자 입력이 먹음(K2).
- JVM: 사용자 멈춤 판 + 체크포인트 지움 → `leagueBlocked` 자동 무효 0 · 카드는 기권만 · 이어 하기 성공 뒤엔 표지 없음 · 앱 판 바뀜이면 무효 됨(K3).
- sim: 리셋 → 앱 종료 → 다시 열기 → **타이틀**(이어 하기 안 함) → A → 그 자리부터(K4) · onPause 만으로 내려간 판은 바로 이어짐(옛 동작).
- host: 데모 중 OPTION → 대기 안 열림(K5) · 커서 0/1 에서 대기 «상대 찾기» → `R_MCUR` 2 → go · 롬 6판.
- JVM: 시즌 두 번 묻기 + 멈춘 경기 → 기권 1건이 보관 파일에 · 새 시즌 LP 는 기권 뒤 값에서 · 세션 새로(M1).
- t_prac_order 추가: 검질 화면에서 슬롯 불러오기 → 다음 고르기에 B 안 샘(M6) · 유가 치트 + 무작위 칸 → P1 유가(M7) · 고르기 화면 뜨자마자 결정 → A 재시도로 검질 화면(M8).

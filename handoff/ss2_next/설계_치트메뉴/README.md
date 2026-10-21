# 166 설계 — 치트: 멈춤 바 «치트» 칸 + «프레임 표시»·«대미지 미터» (연습 모드 표시 그대로)

기준 트리: `scratchpad/w160` (내부 163, `8e0a1a4`) — 읽기만 했다. `w164`(다른 고침)는 손대지 않음(지금 diff 없음 — 합칠 때 EmuActivity·PadView 겹침만 볼 것).
아래 `파일:줄` 은 모두 w160 기준(`app/src/main/...`).

유저 요청(순서대로)
1. «치트는 어디서 하는지 모르겠노, 아래 옵션 키 나오는 메뉴에서 되게 하던지 / 프레임이랑 데미지 미터 뜨게 하는 것도 넣자 치트에»
2. «프레임 미터는 화면 밖이었는데? 그대로 쓰지 왜»
3. «그걸 안에 어케 넣누 / 데미지는 숫자라서 되는데 프랙티스 모드처럼 하면 되지»

→ 결론: **연습 모드의 두 표시를 코드째 그대로 일반 판(1인·무한 대전)에 켠다.** 새 그림·새 자리·새 글꼴 없음.
- 프레임 미터 = 연습과 같은 `FrameMeterView`(앱 뷰, **게임 화면 밖**) · 같은 자리 규칙 · 같은 끌기/톡.
- 대미지 = 연습과 같은 **게임 화면 안 HUD 숫자 타일**(체력 막대 아래 검은 띠 가운데, 게임 «N HITS» 숫자 타일) · 같은 셈.
- 157 덧판(ovplane/TileCanvas/LgmPages)은 **쓰지 않는다** — 연습이 안 쓰니까(그대로). 그래서 덧판·HUD 이름표와 충돌할 일이 구조적으로 없다(6장).

---

## 1. 연습 모드가 지금 어떻게 보여 주나 (찾은 것)

### 1-1. 프레임 미터 — 게임 화면 밖 앱 뷰
| 층 | 자리 | 하는 일 |
|---|---|---|
| 자료(native) | `cpp/practice.c:473-611` `fd_tick()` | 진짜 프레임마다 램을 **읽기만** 해서 `FD`(2줄×80칸 + 요약 sum)를 쌓는다. `P`(연습 상태)를 하나도 안 본다 — `FD`·램만 씀. |
| 부르는 곳 | `practice.c:952` | `if (lv && !paused && P.menu != M_EXIT) { fd_tick(ram); game_writes(...) }` — **연습 경기(`P.active`) 안에서만** |
| 읽기 | `practice.c:1058-1077` `practice_fd_get` → JNI `nativePracticeFrames`(`practice.c:1095-1109`) | `sum[0] = PS.fd && P.active` (`:1064`) — 켬 여부가 연습 설정 + 연습 경기에 묶여 있다 |
| 앱 | `java/.../FrameMeterView.java`(그림) · `FrameMeterText.java`(숫자 줄, 순수 자바) | 2줄×80칸 SF6 색 · «발동 7F · 지속 6F · 경직 14F · 히트 -2» |
| 켜고 끄기 | `EmuActivity.java:1733-1752` `setFrameMeter` · `:1754-1760` `fdPoll`(33ms, `S_ON==0` 이면 스스로 끔) | |
| 자리 | `EmuActivity.java:1762-1807` `placeFrameMeter` | 게임 그림 아래 패드 버튼과 안 겹치는 첫 줄(`PadView.freeSpan`) → 없으면(가로) 게임 그림 아래 끝 반투명. 끌기·톡·두 번 톡(`:1809-1846`), 자리 키 `pocketcore_fdmeter_p/_l` |
| 누가 켜나 | `EmuActivity.java:3520` (`practicePoll`, 150ms) | `setFrameMeter(hs[0]==4 && ps[24]==1)` — 허브 경기 + 연습 메뉴 «표시: 프레임·둘 다» |
| 멈춤 바 | `EmuActivity.java:184` | 바가 열린 동안 숨김 |

### 1-2. 대미지 — 게임 화면 **안**, 게임 VRAM 타일
| 층 | 자리 | 하는 일 |
|---|---|---|
| 셈 | `practice.c:300-311` (`game_writes` 안 F8) | 맞은 쪽 콤보 수(0x5A97)가 0→1 이면 새 콤보, 체력(0x5A46/0x5C46)이 준 만큼 더함 · 콤보 수 없이 깎임(가드 깎임)은 40프레임 넘게 떨어지면 따로 · 마지막에 맞은 쪽 값 · 999 상한 · `prev_hp` 는 `game_writes` **끝**(`:371`)에서 — 우리가 쓴 바닥·회복이 대미지로 안 세지게 |
| 그림 | `practice.c:632-649` (`hud_update` 뒷부분) | 첫째 판 **줄 3 · 칸 8~10**(게임 줄 24~31, x 64~87 — 체력 막대 아래 검은 띠 가운데, 칸 10 오른쪽 맞춤 1~3자리)에 게임 «N HITS» 숫자 타일 `0x002+d` · 팔레트 4 (`(4<<9)|(0x002+d)`). 처음 쓸 때 세 칸이 모두 검은 띠 타일 `0x001` 이 아니면 안 씀. 게임이 그사이 쓴 칸은 새 원래 값. 끌 때는 아직 우리 숫자인 칸만 되돌림 |
| 조건 | `practice.c:633` | `PS.num == 0 && P.shown >= 0 && hud_layout()` — `hud_layout()`(`:613-617`)=줄 0 칸 7 «1P»(0x03C)·칸 12/13 «COM»(0x049/0x04A) 이 보이는 경기 HUD |
| 저장 | `practice.c:651-662` `hud_restore` ← `practice_before_save`(`:979-984`) ← `native.c:1297` | 저장 직전 숫자 칸 원래대로, 다음 프레임에 다시 그림 |
| 157 측정 | `LgmPages.java:1286-1288` | 같은 줄의 게임 히트 수 = P1 x34..63 · P2 x98..127 → 숫자 칸(x64..87)은 그 **사이** — 연습에서 이미 안 겹침 |

### 1-3. 일반 판에서 안 나오는 이유 (고칠 곳)
- `practice_tick` 은 **모든 세션 모든 진짜 프레임** 불린다(`native.c:1118-1119`) — 그런데 허브 연습 경기가 아니면 `practice.c:888-893` 에서 바로 돌아간다.
- `sum[0]` 이 `PS.fd && P.active`(`:1064`), Java 쪽 켜기도 `practicePoll`(허브 켬일 때만 도는 것) 하나뿐.
- 즉 «돌릴 함수(fd_tick·대미지 셈·숫자 그림)»는 이미 일반 판에서 그대로 돌 수 있고(입력·더미·메뉴·연습 바닥과 무관 — 읽기 + VRAM 세 칸), **문만 닫혀 있다.**

---

## 2. 진입점 — 멈춤 바 «치트» 칸

지금: 치트 창은 실행 창 «치트 ›» 고리(`LaunchSheet.java:388-392`)와 게임 안 «설정»(ACT_CFG, `EmuActivity.java:560-577`) 안쪽 고리로만 열린다 → 두 단계 + 고리 찾기.

### 2-1. PadView (`java/.../PadView.java`)
`ACT_LOOK`(조건부 칸)·`ACT_LEAGUE` 와 같은 모양으로 **맨 끝에** 붙인다(앞 칸 번호 안 바뀜 — `:161-166` 주석의 규칙).
```java
public static final int ACT_CHEAT = 19;                         /* 166: 사무쇼2 «치트» — 늘 보임(리그·모르는 롬은 흐리게 + 이유) */
private final RectF[] util = new RectF[11];                     /* :147  10 → 11 */
utilLabel  += "치트"                                            /* :154 */
utilSub    = new String[11]                                     /* :158 */
utilAct    += ACT_CHEAT                                         /* :159 */
private static final int UTIL_CHEAT = 10;
private boolean cheatCell = false, cheatDim = false;
/* utilVisible(:352-354) */ ... && (i != UTIL_CHEAT || cheatCell)
/** 166: 칸 보이기 · 아래 줄(«2개 켬» / «꺼짐» / «리그 중 꺼짐» / «이 롬 안 됨») · 흐리게(눌러도 창 대신 알림) */
public void setCheatCell(boolean on, String sub, boolean dim) {
    boolean relayout = cheatCell != on;
    cheatCell = on; cheatDim = dim; utilSub[UTIL_CHEAT] = sub;
    if (!on && barSel == UTIL_CHEAT) barSel = -1;
    if (relayout && getWidth() > 0) layoutBar(getWidth(), getHeight());
    invalidate();
}
```
- 그리기(`:711-735`, 아트·단순 두 갈래 모두): `i == UTIL_CHEAT && cheatDim` 이면 `int sc = c.saveLayerAlpha(확장 사각형(알약 그림자 여백 포함), 110)` → 그리고 `c.restoreToCount(sc)`. 그 밖은 그대로.
- 누르기: 터치(`:990-1000`)·패드(`barActivate :425-441`) 모두 `listener.onAction(ACT_CHEAT)` 뒤 **흐리지 않을 때만** 바를 접는다
  (`if (ua == ACT_CHEAT && !cheatDim) { barOpen = false; barSel = -1; }` — 접기는 onAction 다음이라 창이 이미 떠 있어 `onMenu(false)` 가 멈춤을 안 푼다: `EmuActivity.java:186` 이 `sheet.isShowing()` 을 본다).
  흐린 칸은 알림만, 바는 그대로.
- 칸 수: 늘 8 + 치트 1 + 그때그때 2 = 최대 11. `layoutBar`(`:511-552`)는 개수만 보고 1/2줄을 정하므로 손댈 것 없음. 좁은 세로(360dp)에서 2줄×6칸 ≈ 칸 54dp.

### 2-2. EmuActivity
```java
/* 166: 멈춤 바 «치트» 칸 — 코어를 올린 뒤(cheatSetup 끝, 모든 갈래) · 바를 열 때(onMenu(true)) · 치트 창을 닫을 때 */
private void cheatCellSetup() {
    final boolean ss2 = game != null && Cheats.GAME.equals(game.id);
    final String why = !ss2 ? null : ranked() ? "리그 중 꺼짐" : !cheatOk ? "이 롬 안 됨" : null;
    int n = ss2 && why == null ? Cheats.count(Settings.load()) : 0;
    final String sub = why != null ? why : n > 0 ? n + "개 켬" : "꺼짐";
    h.post(() -> { if (pad != null) pad.setCheatCell(ss2, sub, why != null); });
}
```
- 부르는 곳: `cheatSetup()`(`:3389-3403`)의 **세 갈래 끝 모두**(랭크 return 앞 · 모르는 롬 return 앞 · 끝) — `cheatOk` 가 정해진 뒤라야 함. `onMenu(open)`(`:183`)에서 `refreshSlotInfo()` 옆. ACT_CFG 의 `onClose`(`:573-576`)에도.
- `handleAction`(`:498`) — ACT_CFG(`:560-577`) 바로 아래:
```java
case PadView.ACT_CHEAT: {                                       /* 166: 바에서 바로 치트 창(설정 창을 거치지 않음) */
    if (game == null || !Cheats.GAME.equals(game.id)) break;
    if (ranked() || !cheatOk) { toast(ranked() ? "리그 대전에선 치트가 꺼져요" : "이 롬 판에선 치트가 안 켜져요"); break; }   /* :572 와 같은 글 */
    final String orig = getIntent().getStringExtra("rom");
    padMask = 0; releasePhysical();
    Emu.nativeSetPaused(true);
    sheet = LaunchSheet.showCheats(this, game, new File(orig));    /* sheet 칸을 그대로 쓴다 — 키 넘김(:903, :976)·멈춤 조건(:186, :1196, :2542)이 다 따라온다 */
    sheet.onClose = () -> {
        Emu.nativeSetPaused(pad.isBarOpen());                      /* 바는 PadView 가 접었다 → 바로 게임 */
        if (sheet != null && sheet.cheatsChanged() && pushCheats()) toast("치트 적용");
        cheatCellSetup();
    };
    break; }
```
- 랭크 가드(`:499-505`)엔 넣지 않는다 — 흐린 칸이 스스로 알림.

### 2-3. LaunchSheet — 치트 창만 바로 여는 입구
지금 치트 창은 겉 창 안에서 내용만 갈아 끼운다(`:646-664`, 139 의 «창 하나 고정» 규칙 `:70-72`). 같은 창 틀을 쓰고 처음부터 치트 내용으로:
```java
private boolean cheatsOnly = false;                              /* 166: 멈춤 바 «치트» — 겉 창 없이 치트 창만(뒤로·닫기 = 창 닫기) */
public static LaunchSheet showCheats(Activity a, Games.Game g, File cheatRom) {
    LaunchSheet s = new LaunchSheet(a, g, null);
    s.inGame = true; s.cheatsOnly = true; s.cheatRom = cheatRom;
    s.open(null, null, g != null ? g.ko : "");
    return s;
}
```
- `open()`(`:216-245`): `setSheet(build(...))` 자리를 `if (cheatsOnly) { prepCheats(); setSheet(buildCheats()); } else setSheet(build(rom, thumb, title));`
  (`openCheats()` 를 `prepCheats()`(opts·뷰 비우고 GROUP 줄 채우고 focus 0) + `setSheet` 로 쪼갬 — 기존 고리 경로는 그대로 `prepCheats(); setSheet(buildCheats()); paintFocus();`).
- `closeCheats()`(`:657`) 맨 앞: `if (cheatsOnly) { try { dlg.dismiss(); } catch (Exception ignored) { } return; }` — 패드 «뒤로»(`:611`)·킥 버튼이 겉 창 대신 닫기.
- `go()`(`:578-584`)는 이미 `cheatView && inGame` 이면 닫기(«적용 ▶») — 그대로.
- 패드 안내 줄(`:719-725`)만 `cheatsOnly` 면 «킥 버튼 닫기».
- `cheatOff` 는 흐린 칸에서 막으니 이 입구로는 안 온다.

---

## 3. 치트 창 새 줄 두 개 (`Cheats.java`, `cheat.h`, `cheat.c`)

| 키(options.txt) | 이름 | 값 | 설명(HELPS) |
|---|---|---|---|
| `pocketcore_ss2_cheat_fd` | 프레임 표시 | off / on (끔·켬) | 1인·무한 대전 경기 중, 게임 그림 아래에 연습 대전과 같은 프레임 미터(발동·지속·경직·유불리). 끌어서 옮기기 · 톡 = 색 설명 · 두 번 톡 = 기본 자리. 연습 대전은 연습 메뉴 «표시»대로. |
| `pocketcore_ss2_cheat_dmg` | 대미지 미터 | off / on | 연습 대전처럼 체력 막대 아래 가운데에 콤보 대미지 숫자(체력 128 기준). 다음 라운드가 시작되면 지워져요. |

- native 번호는 **끝에** 붙인다(옛 options·`t_cheat.py` 의 `CH` 표가 안 깨지게): `cheat.h:7-19` `CH_FD = 10, CH_DMG = 11, CH_N = 12`.
- `Cheats.java:28-40`: `KEYS += "fd","dmg"` · `FD = 10, DMG = 11` · `VALS += {"off","on"} ×2` · `NAMES += {"끔","켬"} ×2` · `LABELS`·`HELPS` 두 개씩.
- 창에 보이는 차례는 native 번호와 따로 — 보기 둘을 마스터 바로 밑에(가장 많이 쓸 것):
  ```java
  static final int[] ORDER = { FD, DMG, CARDS, TIME, 2, 3, 4, 5, 6, 7, POW, YUGA };
  /* items() :58-65 — out[k + 1] = item(ORDER[k]) */
  static int views(Map<String, String> m) { int[] v = values(m); return (v[FD] != 0 ? 1 : 0) | (v[DMG] != 0 ? 2 : 0); }
  ```
- `fight()`(`:83`, TIME..POW)는 그대로 — 보기는 «경기 치트»가 아니다(연습 흐름 안내 띠 «경기 치트 쉼»에 안 셈).
- `count()`(`:80`)는 보기도 센다(«치트 · 2개 켬» 고리·바 칸 아래 줄). 마스터 끔이면 보기도 0(`values()` 가 이미 그렇게).
- `cheat.c`:
  - `cheat_set` 의 `MAXV`(`:262`) `{2,1,2,2,1,1,1,5,3,2, 1,1}`.
  - 새 함수(헤더에도):
    ```c
    /* 166: 보기 비트 — bit0 프레임 표시 · bit1 대미지 미터. 잠겨 있으면 0 (practice_tick 이 P_mu 를 잡기 전에 부른다 — C_mu 단독) */
    int cheat_view_bits(void)
    { pthread_mutex_lock(&C_mu); int b = locked ? 0 : (CV[CH_FD] ? 1 : 0) | (CV[CH_DMG] ? 2 : 0); pthread_mutex_unlock(&C_mu); return b; }
    ```
  - `cheat_status` `v[1]`(`:326`)은 **게임을 바꾸는 치트만** 센다: `for (i = 0; i < CH_FD; i++)` — 왼쪽 위 «치트» 표(`EmuActivity.java:3420`)가 보기만 켰을 땐 안 뜨게. `cheat_tick`·`S.used`(`:250-252`, 명시 목록)는 손대지 않음.
  - `cheat_lock`(`:276-282`)이 `CV` 를 통째로 0 → 랭크에선 보기도 자동으로 꺼짐. `cheat_reset_all`(코어 올리기·내리기 `native.c:954,1032`)도.

---

## 4. native — 일반 판 «보기» 경로 (`practice.c`)

### 4-1. 원칙
- **새 표시 코드를 쓰지 않는다.** 연습이 쓰는 `fd_tick`·대미지 셈·숫자 그림을 같은 함수로 부른다. 대미지 셈·숫자 그림은 지금 `P.` 칸에 박혀 있으니
  **동작 그대로 함수로 꺼내** 연습은 `P` 칸을, 보기는 새 `AV` 칸을 넘긴다(`State` 배치·크기 그대로 → `practice_state_*` 시험 덩어리·결정성 시험 그대로).
- 보기 쪽은 작업 램을 **한 바이트도 안 쓴다**(fd_tick·셈은 읽기, 숫자는 VRAM 줄 3 칸 8~10 세 칸만 — 연습과 같은 칸).
- 입력을 막지도 더하지도 않는다(`practice_in_block/or/opt_mask` 는 0 그대로).

### 4-2. 꺼내기(동작 바꿈 없음)
```c
/* F8 대미지 셈 — game_writes(:300-311) 에서 그대로 옮김. 연습: dmg_count(ram, P.f, P.prev_hp, P.prev_combo, P.rec_open, P.dmg_cur, P.dmg_f, &P.shown_side, &P.shown) */
static void dmg_count(const uint8_t *ram, unsigned f, int prev_hp[2], int prev_combo[2], int rec_open[2],
                      int dmg_cur[2], unsigned dmg_f[2], int *side, int *shown)
{
   for (int d = 0; d < 2; d++) {
      int b = PB(d), hp = ram[b + O_HP], combo = ram[b + O_COMBO];
      if (prev_combo[d] == 0 && combo > 0) { dmg_cur[d] = 0; rec_open[d] = 1; *side = d; }
      if (hp < prev_hp[d]) {
         if (!rec_open[d] && combo == 0 && f - dmg_f[d] > 40) dmg_cur[d] = 0;
         dmg_cur[d] += prev_hp[d] - hp; dmg_f[d] = f; *side = d;
      }
      if (combo == 0) rec_open[d] = 0;
      prev_combo[d] = combo;
   }
   if (*side >= 0) *shown = dmg_cur[*side] > 999 ? 999 : dmg_cur[*side];
}
/* 대미지 숫자 — hud_update(:632-649) 뒷부분 그대로. 연습: dig_draw(PS.num == 0 && P.shown >= 0 && hud_layout(), P.shown, &P.dig_state, P.dig_orig, P.dig_ours) */
static void dig_draw(int want, int v, int *st, uint16_t orig[3], uint16_t ours[3]);   /* 본문 = :633-649 의 P.dig_* → st/orig/ours */
/* hud_restore(:655) 의 숫자 부분 — 아직 우리 숫자인 칸만 되돌리고 *st = 0 (v_scr 없으면 *st = 0 만) */
static void dig_restore(int *st, uint16_t orig[3], uint16_t ours[3]);
```
`:633` 의 조기 `return`(검은 띠가 아니면 안 씀)은 `hud_update` 끝부분이라 함수 `return` 으로 옮겨도 같다. `hud_update` 앞부분(COM→2P)은 연습 전용으로 그대로 남김(보기는 안 부름).

### 4-3. 보기 상태와 한 프레임
```c
#define R_PROG A(0x57C6)   /* 메뉴 프로그램 — 06 1인 대전 · 0C 무한 대전 (cheat.c:33 과 같은 주소) */
/* 166 보기(치트 «프레임 표시»·«대미지 미터») — 일반 세션 1인·무한 대전 전투 화면에서만. 연습 경기와 동시에 켜지는 일은 없다(연습 흐름이면 꺼짐) */
static struct {
   int active, bits, why, fd_now, prev_live, rounds;
   unsigned f;
   int prev_hp[2], prev_combo[2], rec_open[2], dmg_cur[2], shown_side, shown; unsigned dmg_f[2];
   int dig_state; uint16_t dig_orig[3], dig_ours[3];
} AV;

static void view_reset_dmg(const uint8_t *ram)
{
   for (int p = 0; p < 2; p++) { AV.prev_hp[p] = ram[PB(p) + O_HP]; AV.prev_combo[p] = ram[PB(p) + O_COMBO]; AV.rec_open[p] = 0; AV.dmg_cur[p] = 0; AV.dmg_f[p] = 0; }
   AV.shown = -1; AV.shown_side = -1;
}
static void view_release(int restore)      /* 꺼짐·막힘·연습 경기 시작 — 숫자 칸 되돌림(restore), 미터 끔 */
{
   if (restore) dig_restore(&AV.dig_state, AV.dig_orig, AV.dig_ours); else AV.dig_state = 0;
   AV.active = 0; AV.fd_now = 0;
}
/* own = league_session_owner() (0 그 밖 · 1 리그 · 2 연습 흐름) */
static void view_tick(uint8_t *ram, int bits, int own)
{
   int prog = ram[R_PROG], fight = ram[R_MODE] == 241 && (prog == 0x06 || prog == 0x0C);   /* 데모(03)·통신 대전 아님 — cheat.c fight_tick 의 «ours» 와 같은 판단 */
   AV.bits = bits;
   AV.why = !bits ? 0 : own == 1 ? 2 : own == 2 ? 3 : !fight ? 4 : 0;
   if (!bits || own != 0 || !fight) { if (AV.active) view_release(1); return; }
   if (!AV.active) { AV.active = 1; AV.prev_live = 0; fd_reset(1); view_reset_dmg(ram); }
   AV.f++;
   int lv = live(ram), paused = ram[R_PAUSE] == 1;
   if (lv && !AV.prev_live) { fd_reset(1); view_reset_dmg(ram); AV.rounds++; }   /* 새 라운드 — 지난 라운드 미터·숫자 지움(기술 기억은 남김) */
   AV.prev_live = lv;
   if (lv && !paused) {                     /* practice.c:952 와 같은 조건 · 같은 순서(셈은 둘 다 늘 — 도중에 켜도 prev 가 맞게) */
      fd_tick(ram);
      dmg_count(ram, AV.f, AV.prev_hp, AV.prev_combo, AV.rec_open, AV.dmg_cur, AV.dmg_f, &AV.shown_side, &AV.shown);
   }
   dig_draw((bits & 2) && AV.shown >= 0 && hud_layout(), AV.shown, &AV.dig_state, AV.dig_orig, AV.dig_ours);
   AV.fd_now = (bits & 1) != 0;
}
```
- 라운드 사이(KO·승리 포즈)엔 마지막 숫자·미터가 남고, 다음 라운드 첫 조작 프레임에 지워진다. 이야기·고르기(MODE 240)로 가면 `fight` 0 → 숫자 칸 되돌림 · 미터 끔.
- `hud_layout()` 이 안 맞는 HUD(모르는 모양)면 숫자는 조용히 안 그린다 — 연습과 같은 안전장치.

### 4-4. `practice_tick` 연결 (`practice.c:881-960`)
```c
void practice_tick(uint8_t *ram, size_t n, int input)
{
   int dummy = -1, dsty = 0;
   if (!ram || n < 0x4000) return;
   int vbits = cheat_view_bits(), own = vbits ? league_session_owner() : 0;   /* 166: 잠금 밖에서(C_mu·L_mu 단독 — 겹쳐 잡지 않음) */
   int match = league_practice_match(&dummy, &dsty);
   pthread_mutex_lock(&P_mu);
   g_ram = ram;
   if (!match || dummy < 0 || dummy > 14) {
      ... (그대로 :889-891)
      view_tick(ram, vbits, own);                 /* 166 */
      pthread_mutex_unlock(&P_mu);
      return;
   }
   if (AV.active) view_release(1);                /* 166: 연습 경기 — 연습 자기 표시만(겹쳐 그리지 않음). 보통은 연습 흐름(own 2)에서 이미 꺼져 있다 */
   ...
```
- `#include "cheat.h"` 추가. 다른 게임: Java 가 사무쇼2 확인 판이 아니면 치트 값을 아예 안 넣으므로(`EmuActivity.java:3398-3400`) `vbits` 0 → 보기는 남의 게임 램을 안 읽는다(`cheat_reset_all` 이 올릴 때 0).

### 4-5. 한 방·무한 체력 치트와 함께일 때 — `prev_hp` 는 치트 **뒤**에
연습은 `prev_hp` 를 자기 바닥·회복을 쓴 **뒤**(`:371`)에 잡는다. 일반 판에선 체력을 쓰는 쪽이 `cheat_tick`(practice_tick **다음**, `native.c:1121`)이라 같은 규칙을 지키려면 치트 뒤에서 잡아야 한다:
```c
/* 166: 진짜 프레임마다 cheat_tick 다음(native.c:1121 뒤) — 이번 프레임에 누가 쓴 체력까지 «지난 값»으로(연습 :371 과 같은 뜻) */
void practice_view_post(const uint8_t *ram)
{ pthread_mutex_lock(&P_mu); if (AV.active) for (int p = 0; p < 2; p++) AV.prev_hp[p] = ram[PB(p) + O_HP]; pthread_mutex_unlock(&P_mu); }
```
- 무한 체력: 맞은 프레임 28 셈 → 치트가 128 로 → post 가 prev=128 → 다음 프레임 대미지 없음(연습의 회복과 같은 결과 — 콤보 대미지가 제대로 쌓임).
- 한 방: 맞은 프레임 28 셈 → 치트가 0 → post 가 prev=0 → 다음 프레임 «남은 100»을 대미지로 안 셈. (post 가 없으면 128 로 부풀어 보인다.)
- 공격력 배율 치트는 게임이 실제로 깎은 값이 그대로 나온다.

### 4-6. 미터 켬 여부 하나로 (`practice.c:1064`)
```c
sum[0] = (PS.fd && P.active) || AV.fd_now;    /* 166: 연습 «표시» 또는 치트 «프레임 표시»(일반 판) — fdPoll(EmuActivity:1757)이 이 값 하나로 끈다 */
```
`FD` 는 연습·보기가 같이 쓰지만 둘이 동시에 쥐는 일은 없다(4-4). 넘어갈 때마다 `fd_reset(1)`(연습 `activate :872` · 보기 활성·새 라운드).

### 4-7. 저장·잊기·상태
- `practice_forget`(`:970-977`, 리셋·불러오기·코어 올리기/내리기·연습 나가기에서 불림): `memset(&AV, 0, sizeof AV); AV.shown = AV.shown_side = -1;` — VRAM 이 통째로 바뀌었으니 되돌리지 않고 잊는다.
- `practice_before_save`(`:979-984`): `if (AV.active) dig_restore(&AV.dig_state, AV.dig_orig, AV.dig_ours);` — 저장된 상태에 숫자 안 실림. 다음 진짜 프레임에 `dig_draw` 가 원래 값(0x001)을 다시 잡고 다시 그림(연습과 같은 흐름 — 저장 뒤 훅 필요 없음).
- 새 상태 읽기 함수(헤더 `PRACTICE_VSTAT 8`) — **`practice_status`(26칸) 를 늘리지 않는다**: 시험 하네스가 `c_int * 26`(`handoff/ss2_practice/stage1/tests/ph.py:15-16`)·`cheat_status` 가 `c_int * 16`(`handoff/ss2_next/cheat/tests/t_cheat.py:18-19`)으로 받아 칸을 늘리면 넘친다.
  ```c
  /* [0 보기 비트, 1 활성, 2 미터 켬(fd_now), 3 숫자 그림(dig_state), 4 막힌 이유(0 없음·2 리그·3 연습 흐름·4 전투 화면 아님), 5 보이는 대미지(−1 없음), 6 라운드 수, 7 보기 프레임] */
  void practice_view_status(int v[PRACTICE_VSTAT]);
  JNI(jintArray, nativeViewStatus)(JNIEnv *env, jclass cls);     /* nativePracticeStatus(:1085-1095) 와 같은 모양 */
  ```
- `practice_state_get/set`(시험용 덩어리)엔 AV 를 넣지 않는다(연습 결정성 시험 그대로).

### 4-8. `native.c`
- `:1121` `cheat_tick(ram, ramsz, in);` 다음 줄에 `practice_view_post(ram);` 하나. 나머지(저장 `:1297`·불러오기 `:1341`·리셋 `:1177`·올리기 `:951`·내리기 `:1030`)는 이미 `practice_forget`/`practice_before_save` 를 부르므로 자동.

---

## 5. Java — 일반 판에서 미터 켜기

`FrameMeterView`·`FrameMeterText`·`setFrameMeter`·`fdPoll`·`placeFrameMeter`·`fdDrag`·자리 키는 **한 줄도 안 바꾼다**(«그대로»).

```java
private volatile int viewBits = 0;                               /* 166: 치트 보기(1 프레임 · 2 대미지) — pushCheats 가 정함 */

/* pushCheats(:3406-3412) 끝 */
viewBits = Cheats.views(m);
h.post(() -> { h.removeCallbacks(viewPoll); h.post(viewPoll); });

/* 166: 치트 «프레임 표시» — 연습 허브가 안 돌 때(«리그·연습» 끔)만 여기서. 허브가 돌면 practicePoll 이 같은 값으로 함께 정한다(둘이 다투지 않게) */
private final Runnable viewPoll = new Runnable() { @Override public void run() {
    if (leaving || !cheatOk || ranked() || (viewBits & 1) == 0) { if (!practiceHub) setFrameMeter(false); return; }
    if (!practiceHub && loaded) setFrameMeter(viewFdNow());
    h.postDelayed(this, 150);                                    /* practicePoll 과 같은 박자 */
}};
private boolean viewFdNow() {
    if ((viewBits & 1) == 0 || !loaded) return false;
    int[] v = Emu.nativeViewStatus();
    return v != null && v.length > 2 && v[2] == 1;
}
```
- `practicePoll`(`:3520`) 한 줄: `setFrameMeter((hs != null && ps != null && hs[0] == 4 && ps.length > 24 && ps[24] == 1) || viewFdNow());`
- 끄기는 `fdPoll` 이 `S_ON == 0`(4-6, 연습·보기 OR)일 때 스스로 — 일관.
- 멈춤 바가 열리면 숨김(`:184`) · 안내 띠가 미터를 피함(`fdBox`) — 연습과 같음.
- `Emu.java:107-109` 옆에 `public static native int[] nativeViewStatus();`.

---

## 6. 충돌 정리

| 상대 | 왜 안 부딪히나 |
|---|---|
| 157 덧판(ovplane·LgmPages·LeagueMenu) | 리그 세션에서만 쓴다(`lgmEligible` 등 `leagueHub`/`hubRanked` 조건). 보기는 `own != 0`(리그)·`cheat_lock` 둘 다로 꺼짐. 덧판은 코어 VRAM 을 안 건드리고(`ovplane.h:3`) 보기는 GL 을 안 건드림 — 층이 다르다. |
| HUD 이름표(`ov_tag*`, 게임 줄 24..31 — 숫자와 **같은 줄**) | 랭크에서만 켬(`EmuActivity.java:2993-2997` `lgmTagsArm`: `leagueHub && hubRanked`). 만약 둘이 같이 켜지면 이름표의 «비켜 주기» 살핌(`ov_tag_scan`)이 우리 숫자(x64..87)를 «게임이 그림»으로 보고 P1 이름표(x16..77)를 숨긴다 — 그래서 **상호 배제가 필수**이고, 위 두 겹 잠금이 그것이다. 시험 V-6 에 넣음. |
| 게임 히트 수 | P1 x34..63 · P2 x98..127(157 실측) — 숫자 x64..87 은 사이. 연습에서 검증됨. |
| 연습 모드 | 연습 흐름(`own == 2`)·연습 경기에서 보기 꺼짐(4-3·4-4) → 미터·숫자 모두 연습 설정만 따름. 미터 뷰는 하나라 «겹쳐 그림» 자체가 불가, 숫자 칸도 하나. |
| 안내 띠(hubBanner)·«치트» 표(왼쪽 위) | 미터 자리(`fdBox`)를 띠가 피함 — 연습과 같음. 일반 판 경기 중엔 띠가 거의 안 뜸(고르기 화면 컬러 안내만). |
| 컬러(look)·리그 허브 | 보기는 VRAM 줄 3 칸 8~10 만, 고르기 화면엔 안 켜짐(`fight` 조건). |
| 치트 «상대 가만히»·«무한 체력» | 연습과 비슷한 연습 판이 됨 — 대미지 셈은 4-5 로 맞음. |

---

## 7. 저장·런어헤드·프레임 패치·배속

- **상태 저장**: 4-7 — 저장 직전 숫자 되돌림, 다음 프레임 다시 그림. 보기 켬/끔은 설정(options.txt)이라 상태 파일에 안 실림 → 불러와도 지금 설정대로. 오토세이브(`.state.auto`)·슬롯 모두 같은 `nativeSaveState`.
- **불러오기·리셋**: `practice_forget` → AV 잊음 + `fd_reset(1)`. 다음 전투 화면에서 새로 시작.
- **작업 램 결정성**: 보기는 작업 램 쓰기 0 → 켬/끔에 상관없이 게임 진행이 같다(시험 V-5). VRAM 세 칸은 게임이 읽지 않는 HUD 칸(연습 FD-5·t_practice 와 같은 근거).
- **런어헤드(코어 `50_runahead.patch`, 기본 2)**: 숨은 프레임은 코어 안에서 되돌려져 `practice_tick` 까지 안 온다(`league.c:9`) → 미터는 진짜 프레임만 센다(연습 «앱 모드» t_framedata 25 PASS 와 같은 조건). 숫자는 VRAM 이라 다음 `c_run` 의 앞선 프레임에도 실려 보인다(지연 ≤ 1 진짜 프레임). 게임이 그 칸을 다시 쓰면 다음 진짜 프레임에 다시 씀(RankVs 주석의 «런어헤드 2 로 3프레임 꺼짐» 꼴 — 검은 띠라 실제로는 게임이 안 씀).
- **프레임 패치(120Hz 합성)**: 합성 호출엔 훅을 안 돌린다(`native.c:1101-1105` `synth`) → 셈이 두 배로 안 감. 숫자는 코어가 그리는 게임 타일이라 160 의 쪽지(ph) 처리 대상 그대로(덧판 이름표가 겪은 «쪽지 셰이더에 밀림» 문제 없음 — 그건 GL 덧칠의 문제).
- **배속(▶▶)**: vsync 당 여러 진짜 프레임 — 프레임마다 `practice_tick`·`practice_view_post` 가 돌아 같음.

---

## 8. 파일별 변경

| 파일 | 변경 | 줄 수(대략) |
|---|---|---|
| `cpp/practice.c` | `#include "cheat.h"` · `R_PROG` · `dmg_count`/`dig_draw`/`dig_restore` 꺼내기(연습 호출부 `:300-311`·`:632-649`·`:655` 를 함수 호출로) · `AV`·`view_reset_dmg`·`view_release`·`view_tick` · `practice_tick` 연결(4-4) · `practice_view_post` · `practice_forget`/`practice_before_save`/`practice_fd_get :1064` · `practice_view_status` + JNI `nativeViewStatus` | +110 / −30 |
| `cpp/practice.h` | `practice_view_post` · `PRACTICE_VSTAT 8` · `practice_view_status` 선언·칸 설명 | +8 |
| `cpp/cheat.h` | `CH_FD`, `CH_DMG`(끝) · `cheat_view_bits` · `cheat_status` v[1] 뜻 «게임을 바꾸는 치트 수» | +5 |
| `cpp/cheat.c` | `MAXV` 12칸 · `cheat_view_bits` · `cheat_status` v[1] 루프 `< CH_FD` · 머리말 한 줄 | +10 |
| `cpp/native.c` | `:1121` 다음 `practice_view_post(ram);` | +1 |
| `java/.../Cheats.java` | KEYS/VALS/NAMES/LABELS/HELPS 두 개씩 · `FD`/`DMG` · `ORDER` · `items()` 차례 · `views()` | +20 |
| `java/.../Emu.java` | `nativeViewStatus()` | +2 |
| `java/.../PadView.java` | `ACT_CHEAT` · 배열 11칸 · `UTIL_CHEAT` · `setCheatCell` · `utilVisible` · 흐린 그리기 · 누를 때 접기 조건(터치·패드) | +30 |
| `java/.../LaunchSheet.java` | `cheatsOnly` · `showCheats()` · `open()` 갈래 · `prepCheats()` 쪼갬 · `closeCheats()` 닫기 · 안내 글 | +25 |
| `java/.../EmuActivity.java` | `ACT_CHEAT` 처리 · `cheatCellSetup()`(세 곳에서) · `viewBits`/`viewPoll`/`viewFdNow` · `pushCheats` 끝 · `practicePoll :3520` 한 줄 · ACT_CFG `onClose` 에 칸 새로 | +55 |
| `tools/ui_shots.py` | 사무쇼2 가짜 롬(`SAMURAI2`)이 ss2 로 잡히면 바 칸에 «치트» — `BAR_LABELS` 기본값(`:623`)에 «치트» 더함(실측으로 확인 후) | +1 |
| 문서 | `next/cheat/design.md` 에 7장 뒤 «보기» 절 · handoff `ss2_practice` 3단계 문서에 «일반 판에서도(치트)» 한 단락 | — |

`FrameMeterView.java`·`FrameMeterText.java`·`practice_glyphs.h`·ovplane·LgmPages·TileCanvas: **변경 없음**.

---

## 9. 시험

### 호스트 하네스(ctypes .so — `t_cheat.py` 의 1인 대전 진입·입력 대본 + stage3 `fd_ref.py`)
새 `t_view.py`(사무쇼2 한패 동봉·순정 JUE 두 판, 앱 모드 런어헤드 2·프레임 생성 켬 한 번 더):
- **V-1 미터 같음**: 1인 대전(0x57C6=06) 라운드에서 `cheat_set(CH_FD,1)` — 대본 입력(약베기 헛침·맞힘·가드·장풍·잡기) + CPU 무작위 3000F 동안 `practice_fd_get` cells/sum 이 `fd_ref.py` 와 매 프레임 같음. 실측 값(하오마루 약베기 7/6/14 · 히트 −2) 그대로.
- **V-2 숫자**: `CH_DMG=1` — 콤보 뒤 `practice_view_status()[5]` = 체력 준 합 · 줄 3 칸 8~10 = `(4<<9)|(0x002+d)`(1~3자리 오른쪽 맞춤) · 999 상한 · 가드 깎임 따로(40F) · 다음 라운드 첫 조작 프레임에 칸 = 0x001 로 되돌림 · 이야기(MODE 240)로 가면 되돌림.
- **V-3 치트와 함께**: 무한 체력 + 대미지 → 콤보 합이 실제 피해 합 · 한 방 + 대미지 → 숫자 = 그 한 대 값(128 아님) · 공격력 3배 → 게임이 깎은 값.
- **V-4 저장**: 숫자가 떠 있을 때 `practice_before_save` 뒤 직렬화한 상태의 VRAM 칸 = 0x001 · 다음 프레임 숫자 다시 · 그 상태 불러오면 AV 잊음(숫자 없음, 다음 맞음부터).
- **V-5 결정성**: 같은 대본 4000F — 보기 켬/끔 두 판의 작업 램 16KB 가 매 프레임 같음(연습 FD-5 꼴) · 보기 끔이면 VRAM 도 같음.
- **V-6 막힘**: 리그 허브(종류 0)·무장(`league_session_owner()==1`) → `why 2`, 미터 `sum[0]==0`, 칸 그대로 · `cheat_lock(1)` → 비트 0 · 연습 흐름(고르기~경기) → `why 3`, 연습 경기에서 `PS.num=1`(숫자 끔)이면 치트 대미지가 켜져 있어도 칸에 숫자 없음 · `sum[0] == PS.fd`.
- **V-7 넘어가기**: 일반 경기에서 숫자 켠 채 → 타이틀 → 연습 경기: 남은 숫자 없음 · 연습 → 타이틀 → 1인 대전: 연습 설정과 무관하게 치트 값대로.
- **V-8 화면 아님**: 데모(03)·무한 대전 고르기·카드 화면 → 아무것도 안 씀.
- 회귀: `t_practice`(68) · `t_framedata`(25 — 연습 대미지·숫자 경로가 함수로 옮겨져도 같음) · `t_cheat`(CH 표에 fd/dmg 더함, `cst()` 16칸 그대로) · `t_fix1`·`t_resume`·`t_dual`·`t_hub_look`·`t_look*`·`t_determ` — `results/integ_143/run.sh` 꼴 한 .so 로.

### JVM
- `FrameMeterTest`(15) 그대로 통과(파일 안 바뀜).
- 새 `CheatsTest`: `values()` 12칸 · 마스터 끔 → 모두 0 · 모르는 값 0 · `views()` 비트 · `items()` 차례(마스터, 프레임 표시, 대미지 미터, 올카드 …) · `fight()` 가 보기를 안 셈 · `count()` 는 셈.

### 에뮬레이터(API 28 세로·가로) / 기기
1. 사무쇼2 일반 판 멈춤 바에 «치트 / 꺼짐» 칸 → 누르면 바가 접히고 치트 창만 → «프레임 표시» 켬 → «적용 ▶» → 바로 게임(멈춤 풀림), 칸 아래 줄 «1개 켬».
2. 1인 대전 경기: 게임 그림 아래 미터(연습과 같은 자리·모양), 끌기·톡·두 번 톡 · 바 열면 숨김 · 이야기 화면에서 사라짐.
3. «대미지 미터» 켬: 체력 막대 아래 가운데 숫자, 히트 수와 안 겹침, 다음 라운드에 지워짐 · 상태 저장·불러오기 뒤 정상.
4. 랭크 판: 칸 흐림 «리그 중 꺼짐» → 누르면 알림만 · 미터·숫자 없음 · HUD 이름표 정상.
5. 연습 대전: 연습 메뉴 «표시»만 따름(치트 켜 둔 채로도 겹침 없음).
6. 패드(물리): 바 커서로 «치트» 칸 → 창 위아래·좌우·킥 = 닫기.
7. `ui_shots.py` 바 칸 자리(«치트» 포함 2줄 배치) 확인.

---

## 10. 공수

| 일 | 시간 |
|---|---|
| native(꺼내기·AV·연결·post·상태 JNI) | 3h |
| Java(Cheats·PadView·LaunchSheet·EmuActivity·Emu) | 3h |
| 하네스 `t_view.py` + 회귀 묶음 | 4h |
| JVM `CheatsTest` | 0.5h |
| 에뮬레이터 확인·ui_shots | 2h |
| **합** | **약 1.5일** |

위험이 가장 큰 곳은 «연습 코드를 함수로 꺼내기» — 동작을 한 글자도 안 바꾸고 옮기는 일이라 `t_practice`·`t_framedata`·`t_determ` 가 그대로 지켜 준다.

---

## 11. 열린 것

- 1인·무한 대전 HUD 줄 3 칸 8~10 이 늘 검은 띠(0x001)인지 — 연습 경기에선 실측됐고 일반 판도 같은 HUD 지만, 시간 숫자가 도는 판(연습은 ∞)에서 V-2 로 한 번 확인. 다르면 숫자는 조용히 안 그려진다(안전).
- 대미지는 연습과 같은 «콤보 대미지(체력 128 기준)» 하나 — «마지막 한 방»·«% » 는 넣지 않음(유저 «프랙티스 모드처럼», 칸도 히트 수 사이 3칸뿐). 원하면 다음 판에서 연습과 함께.
- 가로 화면 미터 겹침 자리(분노 막대 반을 덮음)는 연습 3단계 §5 의 열린 문제 그대로 물려받음.
- «VS»: 이 앱엔 한 기기 2인 대전이 없다(타이틀 셋째 줄 원래 «2인 대전» 자리는 «연습/리그 대전» · 통신 대전 없음) — 1인 대전(06)·무한 대전(0C)만.

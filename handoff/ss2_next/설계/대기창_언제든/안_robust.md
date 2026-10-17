# Ranked waiting window and «리그 언제든 다시»: robustness-first design

**Code snapshot.** The worktree is now at HEAD `7b35ba2` (the 147 commit) and the tree is clean, so the edits the code map called uncommitted are committed. Line numbers below come from `7b35ba2`; use the function names as anchors. Java paths are relative to `app/src/main/java/com/dudu/pocketcore`. **No native change is needed.**

---

## 1. How I read the two requests

**«랭매 대기때 뭐 할지 … 대기창이 있다거나»** asks for a real waiting window between pressing A and «상대 발견!». Today that time is a small box over a frozen title screen.

- The wait is simulated: 2–6 s for about 96% of players, 12 s at most, and 1.2–2.4 s when an opponent is being held for you.
- So the decision is: **fill those seconds with the player's own information** (rank progress, today's record, recent form, and one tip per search measured in SS2). **Do not make the wait longer.**
- The window must not add any new way to get stuck:
  - it stays inside the league EmuActivity;
  - it saves nothing new;
  - every exit is defined (§4).
- Playing while waiting is deliberately out of this version (§8).

**«리그모드는 언제든 다시 할 수 있게 방도를 마련»** is covered in all three readings, in this priority order:

1. **(b) Never locked out. This is the main goal.** Every screen that blocks league play offers its own one-tap fix on the same card. Nothing is saved that only waiting 24 h or editing files could clear.
2. **(a) Get back in from anywhere.**
   - A link in the in-game options sheet. It works mid-fight and also when mods hide title row 3.
   - A direct link in the launcher.
3. **(c) Start over.**
   - «새 시즌 시작» (soft reset) and «처음부터 다시» (full reset). Both save an archive copy first.
   - A «보관함» list with «되돌리기», so no reset is ever destructive.

---

## 2. The design in brief

- **Waiting window.** The search card becomes a full waiting window over the game area. It is Java only, uses input bits native already collects, adds no new state, and keeps the current search timings.
- **Held opponent.** The held opponent (`ranked.pending`) is now saved when the «상대 발견!» card appears, not when the search starts.
- **Releasing a held opponent.** The hold is released:
  - after any `hold`;
  - after two unfinished matches against that same opponent.
  
  This removes the only "wait 24 h" loop.
- **Every block card gets a way out on the card itself:**
  - 무효 (void), when the app is at fault;
  - 기권 (forfeit);
  - 다시 확인 / 권한 설정 (recheck / open permission settings), for storage problems;
  - 나중에 정산 (settle later), when saving a result fails.
- **Reset and archive.** Season and reset tools live only in LeagueActivity. Each one writes a verified copy to `league/archive/` first and can be undone.

---

## 3. What the user sees, screen by screen

### 3.1 Ways in

| From | What the user taps | Result |
|---|---|---|
| Launcher → SS2 options sheet | **«랭크 매치 바로 가기  ›»** (gold, new, above «리그 순위표  ›») | `MainActivity.openRanked(rom)` → EmuActivity with `EXTRA_LEAGUE_HUB` + `EXTRA_HUB_GO` → straight to the search. 2 taps. If `League.dbProblem` is set, it opens LeagueActivity instead, which shows the fix card. |
| Normal session, any moment (title, arcade, practice, mid-fight) → pad bar «설정» → in-game sheet | **«랭크 매치 하러 가기  ›»** / **«리그 순위표  ›»** (new; SS2 normal session only) | `switchSession(true,false)` (autosave as today). If autosave is off, an Ask card appears first: title «지금 게임은 저장되지 않아요», body «자동 저장이 꺼져 있어요. 리그로 가면 이 판은 사라져요.», buttons [그래도 가기] [취소]. This does not depend on `practiceRomOk`, because the league session builds its own ROM copy. That fixes G1–G3. |
| Title row 3 (normal session) | unchanged | unchanged |
| LeagueActivity | «랭크 매치 하러 가기  ›» | Now shown whenever there is no **started** match (see `voidReady` below). When an opponent is held, a line under it reads «기다리는 상대: 칼끝노인 · 검호 ★1 · 내일 21:04까지». |
| Result card | [다음 상대] [재대결] [그만] | unchanged. [다음 상대] is the quick way to search again. |
| After «그만» | Title, banner «리그 대전 · A 상대 찾기» | unchanged |

### 3.2 The waiting window (replaces the content of `RankUi.search`)

The window sits at the top of `gameBox`, as wide as today (≤340dp), with its height capped to the game box. If the game box is shorter than 300dp (landscape or small phones), compact mode drops the «최근» row and the tip.

```
[spinning avatar]  상대 찾는 중…
                   0:04 · 예상 0:06
검호 ★2 · 3,920 LP                     ← tier colour
[■■■■■■■□□□]  다음 ★까지 180 LP
오늘 3승 1패 · 첫 승 보너스 받음
3연승 중!                               ← only when it applies
최근  승 승 패 승 패                     ← WIN/LOSE colours, newest left
────────────────────────────
팁 4/12                    ◀  ▶
다운되면 ↓나 ↑를 쥐어 빨리 일어나요 (44F 빨라짐)
────────────────────────────
비슷한 실력 찾는 중                      ← rotating line
[ 취소 (B) ]
```

**Lines that change with the player's state:**
- Rank line:
  - «배치 경기 2/5» (placement);
  - «무쌍 · MR 1,620» (master).
- Line under the bar:
  - «다음 ★까지 N LP»;
  - «승급까지 N LP»;
  - «강등 위기!» (red);
  - «5판을 마치면 첫 티어가 정해져요» (placement; no bar shown).
- Today line: either «오늘 0승 0패 · 첫 승 보너스 +30 남음» or «… · 첫 승 보너스 받음». It reads `lastWinDay` and the bonus constant in `RankCore`.

**Time line.** It shows «m:ss · 예상 m:ss», where the estimate is `ceil(searchMs/1000)`. It is known when the search starts, so it is honest and never jumps up.
- When the opponent is a held one, it shows «0:01 · 기다리던 상대에게 다시 가는 중» instead. This explains why the match comes so fast.

**Rotating line.** It cycles every 2.5 s through:
- «오늘 36,743명 접속»;
- «비슷한 실력 찾는 중»;
- «상대는 모두 게임 CPU 예요» (kept for honesty).

After 6 s it switches to «범위 넓히는 중…».

**Tips.**
- One tip per search. The index is saved per device in SharedPreferences `pocketcore_rank_tip` and moves forward by 1 each search, so every search shows a new tip.
- ◀▶ (pad ←→, which arrive as native ev 8/16) or tapping the arrows flips the tip.
- The copy comes from measured rules in `설계/framedata.md` §4, never from the opponent already picked, so nothing spoils the reveal:
  - «약베기는 A를 뗄 때 나가요 — 8프레임 넘게 쥐면 강베기» (4-3)
  - «B 혼자는 공격이 아니에요 — ↓B·→B는 튕겨내기 (5F부터 16F)» (4-8)
  - «←B는 B 계열 공격이에요 — 발동 7F» (4-8)
  - «붙어서 →나 ← + A 길게 = 잡기, 발동 3F» (4-9)
  - «다운되면 ↓나 ↑를 쥐어 빨리 일어나요 (44F 빨라짐)» (4-7)
  - «다운 때 뒤를 쥐면 구르며 일어나요 (32F 빨라짐)» (4-7)
  - «필살기는 한 틱 일찍 넣어도 나가요 — 보통 기술은 선입력이 없어요» (4-4)
  - «하오마루 236A 장풍은 발동 11F» / «샬럿 236A는 모으는 데 36F — 발동 41F» (4-10)
  - «지고 바로 재대결에서 이기면 설욕 보너스» / «재대결은 같은 상대와 연속 3판까지» / «오늘 첫 승 보너스 +30»

**Keys during the search:** B or Back = cancel; ←→ = tip; A and OPTION are ignored. The banner for case 6 shows only key hints: «B 취소 · ◀▶ 팁».

### 3.3 The «상대 발견!» card

It is unchanged (stage ◀▶, auto-accept after 3 s, [대전 (A) 3] [나가기]), with two additions:
- **A is ignored for 400 ms after the card appears.** A press made at the end of the search cannot accept an opponent the player hasn't seen yet.
- **This is the moment the held opponent is saved:** `League.holdPending(rankPick)` is called from `rankCardShow`.

### 3.4 Block cards inside the game

All of these are Ask cards that cannot be dismissed by tapping outside.

**A. A started match with no checkpoint, or a checkpoint that won't load.** This means the app crashed or the checkpoint file is unusable, so the app is at fault.
- Title: «멈춘 경기를 이어할 수 없어요»
- Body: «vs 칼끝노인 · 검호 ★1\n앱이 멈춰서 이어할 자리가 없어요.\n무효로 닫으면 LP는 그대로예요.» If the load failed, the second line is «이어할 자리를 불러오지 못했어요.»
- Buttons:
  - **[무효로 닫고 계속]** (primary)
  - [기권하고 계속]
  - [리그 화면으로]
  - [게임으로] (only when coming from a game)
- What "계속" does:
  - In the hub, a void goes to the toast «무효로 닫았어요 — LP 그대로», then `hubReturn(-3)`, which is the existing «다음 상대» path into the search (46 frames).
  - A forfeit goes to `leagueExit(id)`, then `hubResult`, then the normal ranked result card ([다음 상대]/[그만]).
  - In single-match mode (opened from LeagueActivity «재개»), the labels are [무효로 닫기]/[기권] and both return to LeagueActivity.

**B. A started match, but the ROM has changed since it started.**
- Title: «다른 롬으로 바뀌었어요»
- Body: «경기를 시작한 롬: 한패 v1.01\n지금 롬: 순정\n원래 롬으로 되돌리면 이어할 수 있어요.»
- Buttons: [기권하고 계속] [리그 화면으로] ([게임으로]).
- If `m.app` ≠ the current versionCode (an app update caused the change, so the app is at fault), [무효로 닫고 계속] is added first, and the body gains «앱이 바뀌어서 생긴 일이라 무효로 닫을 수 있어요.»

**C. The league can't open because of storage** (`dbProblem` or `writeProblem` at `hubStart`).
- Title: «리그 기록을 쓸 수 없어요», or «리그 기록 파일을 못 읽어요» for `dbProblem`.
- Body: «저장소 권한을 확인한 뒤 «다시 확인»을 눌러 주세요.\n(PocketCore/league)»
- Buttons:
  - [권한 설정 열기]: on Android 11+ this opens `ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION`; on 8–10 it opens the app details screen. It is never a runtime permission dialog over the game view.
  - [다시 확인]: `League.reload()` and then `hubStart()` again. This is safe because `hubStart` returns before any native call when blocked.
  - [게임으로] or [리그 화면으로].
- ROM-unverified and core blocks keep today's text, with [게임으로]/[리그 화면으로]. They cannot be fixed inside the app.

**D. Saving the result keeps failing** (3 failed tries, about 3 s).
- Title: «결과를 저장하지 못했어요»
- Body: «결과는 이 판에 그대로 있어요.\n저장소를 확인한 뒤 다시 시도해 주세요.»
- Buttons:
  - [다시 시도]
  - [권한 설정 열기]
  - [나중에 정산하기]: `leagueSaveCkpt()`, then the toast «다음에 리그를 열면 정산해요», then `goList()`. If the checkpoint also fails, the toast is «이 판도 저장하지 못했어요 — 권한을 먼저 확인해 주세요» and the card stays.
- Retries continue in the background. If one succeeds, the card closes by itself and the flow continues.

**E. Other cases:**
- The title menu disappears during the search: the toast «찾기를 멈췄어요 — A로 다시 찾기» appears (today it closes silently).
- The app comes back after being sent to the background mid-search: the toast «앱이 내려가서 찾기를 멈췄어요 — A로 다시 찾기».

### 3.5 LeagueActivity (no game view, so AlertDialog is allowed)

**On open: `League.voidReady("순위표를 열며 정리(대진 전)")`.** If anything was voided, it shows the toast «첫 라운드 전에 멈춘 경기를 무효로 닫았어요 — 같은 상대가 기다려요». So a `ready` match never blocks or hides the button (fixes G4).

**Card for an open match** (only `playing`/`resume` remain):
- With a checkpoint: as today, [기권] and [재개].
- Without a checkpoint: «앱이 멈춰서 이어할 자리가 없어요. 무효로 닫으면 LP는 그대로예요.» with [무효로 닫기] [기권].
- When the ROM changed and `League.canVoid` allows it, [무효로 닫기] is added.

**Storage card** (replaces the red line):
- Title «리그 기록 파일을 못 읽어요», plus the reason and path.
- Buttons: [다시 읽기] (`League.reload()` + `render()`) and [권한 설정 열기].

**ROM path fallback:** if `rom == null`, use `pref.last_rom`, which the hub writes when it starts successfully. This means «재개» is never hidden just because LeagueActivity was opened without a ROM path.

**List of held and void matches:** it now also shows ranked voids that happened after the match started, as «무효 · 칼끝노인\n앱이 멈춰 이어할 자리가 없음».

**My card:**
- «전국 21,663위 / 39,899명 · 시즌 2». The season number comes from `ranked.season`; «시즌 1» is no longer hard-coded.
- «이번 시즌 12승 9패 · 통산 43승 34패 · 연승 2 (최장 6)».
- When there is a past season: «지난 시즌 최고 검호 ★2».

**New section at the bottom, «시즌 · 기록»:**
- «시즌 2 · 10월 15일부터 · 12승 9패», then the past-season plates: «시즌 1 · 최고 검호 ★2 · 마지막 검객 ★5 · 31승 25패».
- **[새 시즌 시작]**, with the caption «LP를 실력 쪽으로 반만큼 당기고 승패를 0부터 세요».
  - During placement it is hidden, and the line «배치 경기를 마치면 새 시즌을 열 수 있어요» shows instead.
  - Confirm dialog: title «새 시즌을 시작할까요?», body «시즌 1 기록은 지난 시즌에 남아요.\nLP 3,920 → 3,660 (검호 ★2 → 검호 ★1)\n승패·연승은 0부터, 실력과 상대 전적은 그대로예요.», buttons [시작] [취소]. Afterwards the toast «시즌 2 시작!».
- **[처음부터 다시]** (red text), with the caption «지금 기록은 보관함에 남아요».
  - Confirm dialog: title «처음부터 다시 할까요?», body «지금 기록은 보관함에 남겨서 언제든 되돌릴 수 있어요.\n배치 경기 5판부터 다시 하고, 상대 4만 명도 새로 만들어요.\n스테이지·컬러 설정은 그대로예요.», buttons [처음부터] [취소]. Afterwards the toast «새로 시작했어요 — 배치 경기 0/5».
- **«보관함»** rows: «10월 15일 21:04 · 처음부터 다시 전», parsed from the file name only.
  - Tapping a row reads the file and shows a dialog: title «이 기록으로 되돌릴까요?», body «시즌 1 · 검호 ★2 · 56판\n지금 기록도 보관함에 남겨요.», buttons [되돌리기] [취소] [지우기]. [지우기] asks a second time: «이 보관 기록을 지울까요? 되돌릴 수 없어요.».
  - Files that could not be read appear as «읽지 못한 기록 · 9월 30일 (되돌릴 수 없음)».
- While a started match is open, all three buttons are disabled with «끝나지 않은 경기를 먼저 정리해 주세요». The open-match card at the top of the same screen is the way out.
- Any failure shows «저장하지 못했어요 — 기록은 그대로예요».

---

## 4. Behaviour for each event

### 4.1 During the search, the card and the hand-off

| Event | Searching | «상대 발견!» card | Waiting for the go (≤2 s) |
|---|---|---|---|
| B / Back / tap 취소·나가기 | cancel, «그만뒀어요». **No opponent is held** (new). | leave, opponent held, «상대가 기다려요 — 다음에 또 만나요» | (ignored) |
| Pad bar opened | **timers freeze** (today it cancels; remove `rankCancel` from `onMenu`, because `rankTick` already freezes for `isBarOpen()`). They resume when the bar closes. | freeze; auto-accept also frozen | frozen |
| Bar «목록»/«종료» → `hubLeave` Ask | stays frozen; «목록으로»/«순위표» leave cleanly | same; opponent held | same |
| Ask card shown | freeze (existing `rankFrozenAt`) | freeze | freeze |
| App goes to background (`onPause`) | cancel; toast on return | leave; opponent held | 2 s timeout → «상대를 잡지 못했어요» (existing) |
| Process killed or app crash | nothing saved; restoring from recents (`HUB_GO`) searches again | opponent held → re-served in 1.2–2.4 s | the `ready` record is voided on next entry (counts as a miss) |
| A | ignored | accept (ignored for the first 400 ms) | — |
| No input | the card appears after `searchMs` | auto-accept after 3 s (turned off once the stage is changed) | → char select. It has no timer and puts no LP at risk. |

### 4.2 What's on disk when the app is killed, and what happens next

| State | On disk | Next entry |
|---|---|---|
| search | nothing new | new search |
| card | `pending` | same opponent, fast |
| char select | `ready` + `pending` | `ready` voided (miss +1), same opponent |
| fight, normal kill (`onPause` ran) | checkpoint, status `resume` | resumes automatically once |
| fight, crash (no `onPause`) | no checkpoint | card A (void or forfeit) |
| result decided, save failed | checkpoint frozen on the deciding frame | settles on resume (existing `FROM_CKPT`) |
| result card | settled | title |

### 4.3 Timers

| Timer | Value |
|---|---|
| Search | `searchMs` unchanged |
| Found card auto-accept | 3 s |
| A ignored after the card appears | 400 ms |
| Go timeout | 2 s |
| Held opponent | released at 24 h (from the first hold), or by settle/forfeit, any hold, or 2 misses |
| Settle retry | every 1 s; card D after 3 failures |
| Leftover `ready` match | voided on the next `hubStart` or LeagueActivity open |

---

## 5. Data and storage changes (`v` stays 1; no migration step)

| Field | Change |
|---|---|
| `ranked.season`, `ranked.season_start` | already exist; **now read** (my card, `boardLoad` `seasonDay = today(season_start)` instead of `today-30`, season of a match derived from `created`) |
| `ranked.seasons` (new) | `[{n,start,end,final_lp,final_label,peak_lp,peak_label,master,mr,w,l,d,best}]`, one small entry per season. 통산 = sum + current. Missing = `[]`. |
| `ranked.pending.miss` (new) | 0–2. Missing = 0. Increases on a stale `ready` void (`hubStart`/LeagueActivity) or a void after start against that opponent. At 2, `pending` is removed. A user backing out at char select (`hubReturn`) does **not** count, so the anti-dodge rule stays. |
| `ranked.pending` timing | written by the new `holdPending()` at card time, not by `rankedPick()`. Removed by every hold path (`League.hold` **and** the hold branch inside `League.settle`). |
| Match | void after start = `status:"cancelled"`, `void_after_start:true`, `why`. Uses the existing `app`, `rom_md5` fields. |
| `pref.last_rom` (new) | original ROM path, written when the hub starts |
| Files | `league/archive/league-YYYYMMDD-HHMMSS-{reset,restore}.json`. Written from memory with `atomicWrite`, then read back with `read()` before continuing. Never deleted automatically. Existing `league.json.unreadable-*` files are listed but cannot be restored. |

**Old apps (≤147):** they keep unknown keys, so `seasons`, `miss` and `last_rom` survive their writes. 147 shows «시즌 1» (cosmetic only), and treats a voided started match as a terminal `cancelled`. No match carries a `season` field, because the season is derived from `created` against the season boundaries. That keeps matches written by an old app correct.

---

## 6. Implementation plan (3 commits, one release 148, Java only)

### Commit 1: never stuck, and ways in (about 520 lines)

**`League.java` (+~150):**
- `canVoid(m, appVer)`: true for a started match with no checkpoint, `why` = «체크포인트를 불러오지 못함», or `m.app ≠ appVer`. `ready` stays on `cancel`.
- `voidStarted(id, why)`: same backup and rollback pattern as `cancel()`; deletes the checkpoint; calls `pendingMiss`.
- `cancel(id, why, stale)` overload, which calls `pendingMiss` when `stale`.
- `voidReady(why)`.
- Release `pending` in `hold()` and in the hold branch of `settle()`.
- `reload()`: `db=null; dbProblem=null; PF_CACHE.clear(); epoch++`.
- `static volatile int epoch`.
- `setLastRom()` / `lastRom()`.
- `holds()` includes `void_after_start`.
- Test-only `static volatile boolean failSaves` checked at the top of `save()`. This is needed because the test box runs as root, so file permissions can't simulate a failure.

**`EmuActivity.java` (+~170/−20):**
- `leagueBlocked(int kind, String msg)` with the kinds NOCKPT, CKPTBAD, ROM and STORAGE, building the card A/B/C buttons.
- New `leagueResolve(boolean voidIt)`:
  - hub mode: void → `hubReturn(-3)`; forfeit → `leagueExit(id)`;
  - single-match mode: both return to LeagueActivity.
- `leagueStart` passes the kind.
- In `hubStart`, the storage branch goes to card C, and a successful start calls `League.setLastRom`.
- `leaguePoll` shows card D after `leagueRetry ≥ 3`. It also handles `lm()==null`: if the match disappeared, show «리그 기록이 바뀌었어요» with [리그 화면으로].
- `rankNewMatch` refuses when `League.epoch` ≠ `hubEpoch` (captured in `hubStart`).
- New `leagueFromGame()`: autosave check, then `switchSession(true,false)`.
- `ACT_CFG` passes it to `LaunchSheet.showInGame` when the game is SS2 and `!ranked()`.
- `try/catch` around `startActivity` in `switchSession`, `goList` and `leagueExit`, resetting `leaving` on failure (G19).

**`LeagueActivity.java` (+~90):**
- `voidReady` in `onCreate`/`onNewIntent`.
- New go-button condition.
- `openCard` void button.
- Storage card.
- `rom` fallback to `last_rom`.
- Held-opponent line.

**`LaunchSheet.java` (+~30):**
- `showInGame(..., Runnable onLeague)` adds the two in-game links.
- Launcher link «랭크 매치 바로 가기».

**`MainActivity.java` (+~20):** `openRanked(File rom)`.

### Commit 2: the waiting window (about 240 lines)

- **`RankUi.java` (+~110):**
  - `WaitInfo` (rankLine, rankColor, bar, barLine, danger, today, streak, recent, estSec, held, tips, tip0, active);
  - a new `search(c, f, WaitInfo, onCancel, onPrevTip, onNextTip, compact)`;
  - `Search.tick` shows «m:ss · 예상 m:ss»;
  - `Search.tip(d)`;
  - shared `lpInfo(me)` and `bar()`, reused by `LeagueActivity.myCard`.
- **`RankTips.java` (new, ~70):** a static tip list and `next(prefs)`. Pure Java, so it can be tested on the JVM.
- **`League.java` (+~45):**
  - `rankedPick` no longer saves;
  - `holdPending(Pick)`;
  - `rankedToday()` → `{w,l,d}`;
  - `rankedRecent(n)`.
- **`EmuActivity.java` (+~35/−5):**
  - `rankSearchShow` builds `WaitInfo` (compact when `gameBox` height is under 300dp);
  - `rankTick` handles ev 8/16 while searching, and ignores ev 1 until `rankCardAt+400`;
  - `rankCardShow` calls `holdPending`;
  - remove `rankCancel` from `onMenu`;
  - a `rankStoppedByPause` flag for the toast on return;
  - the toast when the menu disappears;
  - banner case 6.

### Commit 3: seasons, reset, archive (about 330 lines)

- **`League.java` (+~150), all `synchronized`, refusing on `dbProblem` or when `openMatch()!=null`, with backup and rollback and `epoch++`:**
  - `seasonPreview()`;
  - `newSeason()`: append to `seasons`; set `lp' = max(0, round10((lp + lpOfMmr(mmr))/2))`; keep master only if `lp' ≥ MASTER_LP`, and `mr' = 1500+(mr−1500)/2`; reset w/l/d, streak, lstreak and best to 0; `peak_lp = lp'`; `shield=false`; keep mmr, games, recent, players and lastWinDay; drop `pending`; `season++`; `season_start = now`.
    - This pulls the player toward the same LP the simulated pool already shows for that skill level, so the pool needs no change.
  - `writeArchive(tag)`;
  - `restartAll()`: archive → `fresh()` + `upgrade` + `upgradeRanked` (new seed, placement 5) + the current `pref`, then delete every `ckpt_*`;
  - `archives()`;
  - `restore(File)`: archive the current state → `read()`. Any open match inside the file is voided («보관함에서 되돌리며 정리»), then upgrade, keep the current `pref`, and save.
  - `deleteArchive(File)`.
- **`LeagueActivity.java` (+~180):**
  - season and archive section, dialogs, past plates in my card;
  - drop the board cache after any reset or restore;
  - season display.

**Docs.** Add a §8 «대기창 · 막힘 풀기 · 시즌» to `handoff/ss2_next/설계/ranked.md`, and a `handoff/ss2_next/ranked/148_*.md` handoff note.

**Total:** about 1,090 Java lines across the three commits, 0 native, plus about 450 test lines.

---

## 7. Tests

### JVM (`handoff/ss2_next/ranked/tests/jvm`; extend `LeagueRankedTest`, add `LeagueRecoverTest`, `LeagueSeasonTest`, `RankTipsTest`)

1. **Held opponent:**
   - `rankedPick` writes nothing; `holdPending` writes it;
   - after a card exit the same opponent is served with `searchMs` ≤2.4 s;
   - after a cancel during the search, a new pick is possible.
2. **Release rules:**
   - `hold()` and a settle-time knob hold both release;
   - a user `cancel` keeps the hold;
   - stale cancel ×2 and `voidStarted` ×2 release;
   - the 24 h expiry still works.
3. **`canVoid` matrix:** ready / playing without checkpoint / resume with checkpoint / bad checkpoint / ROM changed on the same app version / ROM changed on a different app version.
4. **`voidStarted`:**
   - LP, MMR and the h2h record are unchanged; status is `cancelled` with `void_after_start`;
   - the checkpoint is deleted;
   - with `failSaves`, the in-memory record is rolled back.
5. **`newSeason`:**
   - LP math (3920 → 3660 example), the master edge, kept fields;
   - `seasons[0]` peak; `pending` cleared;
   - refuses with an open match or during placement;
   - rollback on save failure;
   - season of a match derived from `created`.
6. **`restartAll`:**
   - the archive is readable and equals the state before the reset;
   - new seed, placement 5, `pref` kept, checkpoints deleted.
   
   **`restore`:**
   - round-trips; open matches in the archive are voided;
   - the current state is archived again.
7. **Old-app compatibility:**
   - a 147 `league.json` is unchanged until the user acts;
   - a file written by 148 passes the old suite (`run_old.sh`), with unknown keys kept.
8. **Other:**
   - `rankedToday` / `rankedRecent`;
   - `reload()` clears a simulated `dbProblem`;
   - `RankTips`: no opponent or matchup text, every tip ≤34 characters (one line at 12sp in 340dp), `next()` wraps around.

### Host (`tests/host`)

1. **`t_hub_resolve.py`:** `league_hub_return(-3)` called at arbitrary boot phases (frame 30 to 3,000, including the attract demo) reaches `H_SEARCH` within 120 frames on the 4 ROMs. This is the exact path after «무효/기권하고 계속».
2. **`t_idle_long.py`:** 36,000 frames (10 min) idle on the title in `H_SEARCH`, and on char select: the menu stays and nothing advances, on the 4 ROMs.
3. **Re-run `t_ranked.py` and `t_ranked_ckpt.py`:** they must be unchanged, since native is unchanged.

### Emulator (API 28, portrait, plus one landscape pass)

1. **Window layout:** at 360dp, compact mode in landscape; ◀▶ via pad and touch; the estimate never increases; the held-opponent line.
2. **Bar during the search:** open the bar → the timer freezes; close → it continues with the correct time shift. Bar «목록» exits cleanly.
3. **Home button:**
   - during the search: return shows the toast, and A searches again;
   - during the card: return, then A gives the same opponent in ≤2.4 s.
4. **Swipe-kill at each state:** search, card, char select, mid-fight. Each re-entry matches §4.2.
5. **Crash:** `adb root; adb shell kill -9 $(pidof com.dudu.pocketcore)` mid-fight → card A → void → search. LeagueActivity then shows «무효 · 앱이 멈춤».
6. **Save failure:** debug toggle `failSaves` → card D after about 3 s → [나중에 정산하기] → turn the toggle off → reopen → the match settles.
7. **`dbProblem` (hook):** card C in-game and in LeagueActivity → [다시 읽기].
8. **In-game sheet link:** from a mid-fight normal game with autosave on and off → league → «그만» → back → «목록» → the normal game resumes at its autosave.
9. **New season / restart / restore / archive delete:** check the files in `/sdcard/PocketCore/league/archive`.
10. **Held-opponent loop:** kill at char select twice → the third search gives a new opponent.

---

## 8. Risks, and what I deliberately left out

### Risks

- **Void can be abused.** Deleting a checkpoint file leads to the void option. I accept this. `league.json` is plain JSON on shared storage, so the user can edit it anyway, and I chose never-stuck over anti-cheat that only works through the UI. A ROM swap still cannot void a match unless the app version changed.
- **The held opponent is saved later than before.** A player can now cancel before seeing the opponent and get a different one. They gain nothing, because they never saw who it was, and the anti-dodge rule from the card onward is unchanged.
- **Freezing on bar open instead of cancelling.** The waiting window stays visible under the bar. The bar only covers the lower area, so nothing overlaps badly. This needs the emulator check in test 2.
- **LeagueActivity and a background league EmuActivity at the same time.** This can happen through Home → launcher → «리그 순위표». Reset and restore are refused while any match is open (same static db). `epoch` covers a hub that is idle or searching, and `lm()==null` covers a match that disappeared.
- **Archives grow.** Each one is a full copy of `league.json`. Nothing is deleted automatically; the user deletes from «보관함».
- **«처음부터 다시» uses a new seed**, so rivals disappear. The confirm text says so.

### Left out on purpose

- **Playing while waiting.** Practising in the queue (via `switchSession`) or a «도전자 난입» interrupt would need two session switches or a refactor of the native hub. That hand-off is the fragile part, and the wait is only 2–12 s. Revisit only if the user asks.
- **Longer fake waits.** People resent idle waiting.
- **Automatic monthly seasons.** They would surprise the user, and it conflicts with the rule that LP moves only through real matches.
- **An Android app shortcut.** The icon alias makes it fragile.
- **A league button on the pad bar.** The bar layout is fixed; the sheet link is used instead.
- **A mini «내 주변» board or a world feed inside the window.** The wait is too short for a board, and a world feed would break the honesty rule.
- **A crash-loop "safe mode" marker file.** Single-use checkpoints plus `pending.miss` already end every loop I could find.
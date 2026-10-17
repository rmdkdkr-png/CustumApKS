# Ranked waiting room and "league anytime": design proposal (realism-first)

## 0. Summary

The design has five parts:

1. **The queue follows you.** A ranked search becomes an app-level ticket (`RankQueue`). It keeps running while you:
   - look at the waiting window over the league title (대기창);
   - practise or play in your normal session (연습하며 기다리기);
   - browse the ranking screen (순위표 보며 기다리기).
2. **Match found.** When the opponent is found, a «상대 발견!» card appears with an accept countdown: 5 s in the waiting window, 10 s anywhere else. Accepting from outside the league session shows a VS loading card while the app switches sessions, then goes straight to character select.
3. **Believable waits.** The wait length depends on the time of day and your MMR, with a median of about 8–12 s. It is never padded just to feel long. On-screen messages about widening the search are true, because a longer wait really does widen the opponent range. A «빠르게» setting keeps the old 2–6 s wait.
4. **A living world.** The waiting window shows your LP progress, today's record, your neighbours on the board, Samurai Shodown 2 frame-data tips, and a «가상 리그 소식» feed computed from the simulated player pool. It is always labelled as CPU or virtual.
5. **League anytime.** All three readings of the second request are covered:
   - (a) Shorter ways in.
   - (b) Every lockout card carries its own way out.
   - (c) A user-triggered «새 시즌» soft reset and an archived «처음부터».

## 1. Interpretation

**Request 1, «랭매 대기때 뭐 할지 / 대기창»:** the user is asking what the player does during the ranked wait, and whether there should be a waiting window.

- Today the search is a small card over a frozen title for 2–6 s.
- Realism means following Street Fighter 6 (SF6) and Tekken 8: the queue stays alive while you train or browse, the match calls you, and you accept.
- So the answer has two parts:
  - a proper waiting window for people who just wait;
  - "wait while doing something else" for people who would rather practise.
- The wait has to be long enough to make the second option meaningful, but short enough that plain waiting is never a chore. That is why the wait model is lengthened only to a believable level (median about 10 s, capped at 90 s), with a «빠르게» escape.

**Request 2, «리그모드는 언제든 다시할수있게 방도를 마련»:** all three readings are covered, ranked by likelihood.

- **(b) Never locked out (primary).** Today a crash leaves «멈춘 리그 경기를 이어할 수 없어요» with only «리그 화면으로»/«게임으로», and the only way out is a full-LP forfeit. Other hard locks: an app or core update, an unreadable league.json, an endless settle retry, and an error hold that keeps re-serving the same opponent.
  - Rule: **every block screen offers, on the same card, an action that leaves the user in a playable state.**
- **(a) Re-enter from anywhere (primary).** Today the in-game route is only title row 3, which needs the «리그·연습» option on, a verified normal-session ROM and a readable league.json. Mid-fight it takes 6 or more inputs.
  - New routes: a pad-bar cell, a launcher-sheet link, an Android app shortcut, and an always-present ranking-screen button.
- **(c) Start over (secondary).** A user-triggered «새 시즌 시작», with LP pulled halfway toward 무사 and MMR kept. This follows the Tekken 8 Season 3 and SF6 soft-reset pattern. «처음부터 다시» archives the whole file and starts a new world.
  - Nothing is ever deleted.

## 2. Principles

- **One queue, many places.** The queue lives outside any Activity, so moving between the waiting window, practice and the ranking screen never restarts the clock.
- **Honest realism.** Waits are believable, and the "평균 대기" (average wait) is the model's real mean. Widening is real. «CPU» chips and «상대는 모두 게임 CPU 예요» stay. There are no ping bars and no live «n명 대기 중» counters.
- **Opponent is held when the card shows, not when the search starts.** This fixes the quirk where B during the search held an opponent the user never saw.
- **No Android windows over the game.** Every in-game card is an in-view card (RankUi or Ask). AlertDialog appears only in LeagueActivity.
- **Nothing is ever deleted.** Resets archive. A void is a recorded `hold`, never an erased match.

## 3. User-facing flow

### 3.1 Starting a queue (entry points)

| Where | Control (Korean text) | What happens |
|---|---|---|
| League session, title row 3 | «리그 대전», press A (unchanged) | Waiting window (3.2) |
| Normal session, title row 3 | ◀▶ «리그 대전», press A (unchanged) | Switches session, then waiting window |
| **Normal session, pad bar (new cell, any screen, mid-fight too)** | «랭크 대기» (while queued: «대기 취소») | Queue starts **in place**. Strip appears (3.3) and you keep playing. Works even when the normal ROM is modded (league uses its own ROM copy). |
| **Launcher options sheet (new link)** | «랭크 매치 바로 하기 ›», above «리그 순위표 ›» | League session, straight into the waiting window |
| **App shortcut (new, long-press icon)** | «랭크 매치» | Same as above, using the last-played SS2 ROM |
| LeagueActivity | «랭크 매치 하러 가기 ›». Shown **always**: a `ready` leftover is silently voided, as the hub already does. With a resumable match: «멈춘 경기 이어서 하기 ›». While queued: «대기창으로 ›». | League session |
| Result card | «다음 상대 (A)» | Waiting window |
| Result card (new) | «연습하며 대기» | Back to practice with a fresh queue running |

**Guard on every start:**
- League.dbProblem or writeProblem → the stuck card (3.8).
- An open `ready` match → auto-void.
- An open `playing`/`resume` match → Ask card «멈춘 랭크 경기가 있어요» / «먼저 이 경기를 이어서 하거나 닫아야 새 상대를 찾을 수 있어요.» [이어서 하기] [나중에].
- From the normal session, the league ROM copy and bundled core are checked on a background thread. On failure: toast «리그 대전을 열 수 없어요 — <이유>».

### 3.2 Waiting window (league session, over the title)

The panel covers the game box, capped to its height. On short screens the tab body is dropped first.

```
┌──────────────────────────────────┐
│ [avatar reel]  상대 찾는 중…   0:12 │
│                평균 대기 0:15       │
│ 범위를 넓혔어요 · ±1 티어            │  ← only after 15 s / 30 s / 60 s
│  내 정보 │ 내 주변 │ 소식            │
│  (4-line tab body)                 │
│ 팁 · 약베기는 버튼을 뗄 때 나가요       │
│ [연습하며 기다리기] [순위표 보며 기다리기]│
│ [취소 (B)]                          │
└──────────────────────────────────┘
```

**Header and status**
- Header: «상대 찾는 중…», then a m:ss timer and «평균 대기 0:15». The average is rounded up to 5 s and never changes during one queue.
- Held opponent: «기다리던 상대에게 연결 중…» (2–4 s).
- Widening lines, at 15 s, 30 s and 60 s: «범위를 넓혔어요 · ±1 티어» / «· ±2 티어» / «· 전체».
- The rotating sub line keeps «상대는 모두 게임 CPU 예요».

**Tab «내 정보»**
- «검객 ★3 · 2,410 LP» with an LP bar and «다음 ★까지 90 LP».
- Or «배치 경기 3/5 — 끝나면 첫 티어가 나와요», or «강등 위기!».
- «오늘 3승 1패 · 첫 승 보너스 +30 남음» (after the first win: «오늘 첫 승 보너스 받음»).
- «최근 5판» with five coloured dots and LP deltas.

**Tab «내 주변»:** board rows at ±2 around me, e.g. «21,662위 칼바람 · 검객 ★3 · 2,455», with my row highlighted.
- During placement: «배치를 마치면 순위가 나와요».
- While loading: «순위 계산 중…».

**Tab «소식»:** header «가상 리그 소식 · 모두 CPU». Three items computed for today from the pool:
- «칼바람 님 검호 승급»
- «달빛검 님 7연승 중»
- «지난번 내가 이긴 백야 님이 검객 ★3 까지 올라왔어요», using my h2h players
- «오늘 무쌍에 오른 사람 12명»

**Tips:** they rotate every 6 s; ↑↓ picks the next one. They come only from the measured facts in `설계/framedata.md`:
- «약베기는 버튼을 뗄 때 나가요»
- «↓B·→B 튕겨내기는 5~16프레임 동안 받아요»
- «잡기는 3프레임 만에 나가요»
- «쓰러지면 ↓나 ↑로 빨리 일어나요»

Tips are never about the opponent's character, which is already picked; showing them would spoil the found card.

**Buttons**
- «연습하며 기다리기». It reads «게임하며 기다리기» when the normal ROM can't run practice (`practiceOkKey` = "0").
- «순위표 보며 기다리기».
- «취소 (B)».

**Keys:** these use the existing ev bits, so no native change is needed. ←→ switches tabs, ↑↓ moves to the next tip, B cancels, A does nothing (so the A that started the search cannot click anything). The banner (case 6) changes from duplicate text to «◀▶ 탭 · ▲▼ 팁 · B 취소».

### 3.3 Waiting elsewhere

**Practice or game (normal session).**
- A pill sits just below the game box in portrait, or in the free side column in landscape. It never covers the game image.
  - Text: «랭크 대기 0:24 · 평균 0:15  ✕». After widening: «랭크 대기 0:41 · 범위 넓힘  ✕».
  - Tapping ✕ cancels: toast «대기를 그만뒀어요». Nothing is held.
- **When the card pops:**
  - In practice or on menus: immediately. This matches SF6 training.
  - In an arcade or VS round in progress: at round end. The strip shows «상대 발견! 이 라운드가 끝나면 떠요»; waiting is bounded by the in-game timer, and after 120 s the card pops anyway.
  - While the pad bar, settings sheet, an Ask card or the cheat window is open: deferred, with «상대 발견! 메뉴를 닫으면 떠요».
- Starting a queue mid-arcade with autosave off shows the toast «자동 저장이 꺼져 있어 수락하면 지금 판은 이어지지 않아요».

**Ranking screen (LeagueActivity).**
- A sticky strip with the same text sits at the top. «랭크 매치 하러 가기 ›» becomes «대기창으로 ›».
- Found: the same RankUi.found view inside a Dialog (allowed here, no GL), with a 10 s countdown.
- Back leaves to the launcher and cancels the queue: toast «대기를 그만뒀어요».

### 3.4 The «상대 발견!» card

- It is the existing card plus «기다린 시간 0:14». Outside the waiting window it also carries a «랭크» chip.
- Pills: «나가기 (B)» and «대전 (A) 5». The countdown is 5 s in the waiting window and 10 s elsewhere.
- ◀▶ (stage) stops the countdown, as today.
- **AFK rule:** if there was no input in the 60 s before the pop, there is no countdown. The pill reads «대전 (A)» and a line says «자리 비움 — 누르면 시작해요». If the card then sits untouched for 60 s, it auto-declines with the toast «자리를 비워서 대기를 멈췄어요 — 상대는 기다려요».
- **Decline (B, «나가기», Back):**
  - The queue ends.
  - The opponent is **held** (written to `ranked.pending` when the card appears).
  - Toast: «상대가 기다려요 — 다음에 찾으면 바로 나와요».
  - The next search re-serves the same opponent in 2–4 s. This is the soft "dodge" rule: no LP penalty.
- **Over the normal session:**
  - `nativeSetPaused(true)` + `releasePhysical()`.
  - Keys go through Java because a paused game sends no ev. Touch works on the pills. Physical keys use `keymap.funcOf` (a = 대전, b = 나가기, left/right = stage). On-screen pad presses are caught in `onMask` edges.
  - Ask's key handler is not reused, because there A and Back mean "cancel".
- **Haptic:** the existing LONG_PRESS.

### 3.5 Accept → VS → character select

| From | Accept path | Latency |
|---|---|---|
| Waiting window | Unchanged: `rankGo` → `nativeHubMatch(go=true)` | under 1 s |
| Practice, game or board | VS card («VS» / «나 · 검객 ★3» / «칼바람 · 검객 ★2 · 하오마루 수라» / «불러오는 중…») is shown over the old screen. `switchSession(true,false)` (or a direct start from LeagueActivity) with new extras `rank_accept`=opp id and `rank_stage`=stage. The new Activity shows the same VS card. `hubStart`: if `openMatch()==null` and the pending id matches → `rankArm(p, stage, go=false)` + `hubReturn(-4)`, the existing rematch path (reset, then straight to my character select). **No native change.** At hub state 3, the existing `rankNewMatch()` writes the `ready` record. | about 2–3 s, shown as a VS screen |

- If st 3 hasn't arrived after 10 s: close the VS card, toast «상대를 잡지 못했어요 — 다시 찾아 주세요», then `hubReturn(-3)`. That lands in the waiting window, where the held opponent comes back in 2–4 s.
- If the pending id doesn't match or an open match appeared: fall back to a normal search, or resume the open match with the toast «멈춘 경기를 먼저 이어서 해요».

### 3.6 After the match (the endless loop)

- Result card pills: «다음 상대 (A)» (primary, full width), then «재대결» «연습하며 대기» «그만» (13 sp).
- «연습하며 대기»:
  - Starts a new queue.
  - Calls `switchSession(false, false)` when autosave is on, so practice resumes exactly where it was (dummy settings via `.prac`), or `switchSession(false, true)` when it is off.
  - The strip continues there.
- LeagueActivity «재개» now launches the **hub** (E7 auto-resume) instead of single-match mode, so every resumed fight also ends on this result card.

### 3.7 Seasons and starting over (LeagueActivity)

**My card**
- «전국 21,663위 / 39,899명 · 시즌 2», reading `ranked.season`. This fixes the hard-coded «시즌 1».
- Plate: «시즌 1 최고 · 검호 ★2».
- Pending line: «기다리는 상대 · 칼바람 (검객 ★2) — 21시간 뒤 풀려요».

**«규칙» tab, new section «시즌·기록»**
- «시즌 2 · 10월 3일부터».
- «지난 시즌» list: «시즌 1 · 최고 검호 ★2 · 31승 22패».
- «매칭 대기 — 실제처럼 · 빠르게», with the note «빠르게: 2~6초 안에 찾아요».
- Buttons «새 시즌 시작» and «처음부터 다시».

**«새 시즌 시작» dialog**
- Title: «새 시즌을 시작할까요?»
- Body: «LP 가 절반쯤 내려가요 (검호 ★2 → 검객 ★4). 실력 점수는 그대로라 빨리 올라와요. 이번 시즌 기록은 «지난 시즌»에 남아요.» The tier preview is computed.
- Buttons: [그만두기] [새 시즌 시작].

**«처음부터 다시» dialog**
- Title: «처음부터 다시 할까요?»
- Body: «지금 기록은 지우지 않고 보관함에 옮겨요. 새 세계(다른 선수 39,899명)에서 배치 5판부터 시작해요.»
- Buttons: [그만두기] [처음부터].

**Rules-tab copy fix:** «상대 카드가 뜬 뒤 나가면, 그 상대와 붙을 때까지 다음 찾기에 같은 상대가 나와요(최대 24시간).»

### 3.8 Stuck screens and their way out

These are in-view Ask cards in-game and the open-match card in LeagueActivity, with the same choices.

| Case | Title / body | Buttons → result |
|---|---|---|
| Started match with no checkpoint, or checkpoint won't load (L3) | «멈춘 경기를 이어할 수 없어요» / «앱이 갑자기 꺼져서 이어할 자리가 없어요. 이 경기를 어떻게 닫을까요?\n무효로 닫으면 LP 는 그대로예요 (이번 주 2번 남음).» | [무효로 닫기] [기권패로 닫기] [나중에]. Once the budget is used, the body ends «이번 주 무효를 다 써서 기권패로만 닫을 수 있어요.» and only [기권패로 닫기] [나중에] remain. |
| App or core changed since the match started (L4, app update) | «경기를 이어할 수 없어요» / «앱이 업데이트돼서 이 경기를 이어할 수 없어요. 점수 없이 닫을게요.» | [무효로 닫고 계속] (free, no budget) [나중에] |
| ROM changed (L4, user swapped ROM) | «경기를 시작한 롬과 지금 롬이 달라요» / «원래 롬으로 되돌리면 이어할 수 있어요.» | [무효로 닫기] (budget) [기권패로 닫기] [나중에] |
| After any close | toast «정리했어요 — 바로 상대를 찾을게요» | In the league session, goes straight to the waiting window |
| `dbProblem` (L8) | «리그 기록을 열 수 없어요» / «기록 파일이 깨졌거나 읽을 수 없어요.\n<경로>» | [다시 확인] [옆으로 치우고 새로 시작] (rename to `.unreadable-<ts>`, the existing precedent) [권한 설정] (app-settings intent) |
| `writeProblem` (L9) | «리그 기록 폴더에 쓸 수 없어요» / path | [다시 확인] [권한 설정] |
| Settle save fails 3 times, about 24 s (L18) | «결과를 기록하지 못했어요» / «저장소에 쓸 수 없어요. 결과는 앱 안에 맡아 두고, 다음에 리그를 열 때 넣을게요.» | [맡겨 두고 계속] (stash, unpause, back to the hub title) [다시 시도] |
| Error hold (L13) | unchanged display | **The hold now releases `pending`**, so a systematic failure can't loop the same opponent |

**Void budget:** 2 free voids per rolling 7 days. Crash voids are rare in practice: swipe-away and force-stop both go through `onPause`, which writes the checkpoint.

## 4. Behaviour matrix

| Event | Searching (waiting window) | Searching (practice/game) | Searching (ranking screen) | Card up | VS / switching |
|---|---|---|---|---|---|
| Back | Cancel, «대기를 그만뒀어요» | Opens the pad bar as usual; queue keeps running | Leave and cancel | Decline (held) | Ignored |
| Pad bar / pause menu | Queue runs, card deferred (today it cancels) | Queue runs, card deferred; the bar shows «대기 취소» | n/a | Countdown frozen (`rankFrozenAt` pattern) | n/a |
| App to background | `RankQueue.pause()` (the clock stops). Back within 60 s: continues. Later: cancelled, «오래 비워서 대기를 그만뒀어요» | same | same | Card stays and the countdown freezes. Back within 60 s: countdown restarts at full. Later: auto-decline (held) | Switch continues; the new Activity resumes it |
| Own session switch | Not a pause: `RankQueue.handoff` flag set before `startActivity` | same | same | n/a | n/a |
| App killed | Queue lost; nothing held | same | same | Opponent stays held (24 h) | Held; recents restore re-accepts (`rank_accept` extra, guarded by `rankAcceptUsed` + pending-id check) |
| Accept | — | — | — | A, tap, or countdown → 3.5 | — |
| Decline | — | — | — | B, tap, Back or AFK 60 s → queue ends, held | — |

**Timers**

| Item | Value |
|---|---|
| Wait | Model in 5, cap 90 s |
| Held opponent | 2–4 s |
| Widening messages | 15, 30 and 60 s |
| Accept countdown | 5 s in the waiting window, 10 s elsewhere |
| AFK | No input for 60 s before the pop → no countdown; card idle 60 s → auto-decline |
| Background grace | 60 s |
| VS timeout | 10 s |
| Round-end defer | Up to 120 s |
| Settle-failure card | After 3 tries |

## 5. Wait model (`RankCore.waitMs`)

**Formula.** The wait is `clamp((5 s + Exp(mean 7 s)) × hour × tier, 3 s, 90 s)`. The device-local hour factor is:

| Hours | Factor |
|---|---|
| 19–23 | 0.8 |
| 12–18 | 1.0 |
| 0–1 | 1.1 |
| 7–11 | 1.4 |
| 2–6 | 2.2 |

The tier factor is 1.0 below MMR 1450, 1.5 for 1450–1600, and 2.2 above 1600 or in 무쌍.

**What that gives:**
- A typical player in the evening has a median of about 8 s.
- At 3 am the median is about 22 s.
- A top player at 3 am has a median of about 48 s.

**The rest of the model:**
- The **wait is drawn first, then the pick**. The pick's spread is `sigma × min(3, 1 + wait/30 s)`, so long waits really do get wider matches. That makes the widening lines true.
- A held opponent takes 2–4 s.
- «빠르게» uses the current 2–6 s formula (Settings key `pocketcore_rank_wait`, default `real`).
- The displayed «평균 대기» is the model mean (12 s × hour × tier), rounded up to 5 s.

## 6. Data and store changes

`league.json` stays `v:1`, and every change is additive. Old apps (147 and below) keep unknown keys.

| Key | Change |
|---|---|
| `ranked.pending` | Same shape. Now written in `rankCardShow`, not at search start. Released by `applyRanked` (as today) **and** by `hold()`. |
| `ranked.voids` | New: `[ms,…]` free voids used, trimmed to 7 days |
| `ranked.season`, `season_start` | Now read (UI) and advanced by a new season |
| `ranked.seasons` | New: `[{n,start,end,games,w,l,d,peak_lp,peak_label,final_lp,final_label,master,mr_peak,best}]` |
| `ranked.career` | New: `{w,l,d,games}`, added up at each new season. Displayed 통산 = career + current. |
| `ranked.matches[].void` | New: `"crash"`, `"version"` or `"rom"`, on a `status:"hold"` record with LP unchanged. It shows in the existing «보류·무효 경기» list. |

**Outside league.json:**
- `league/archive/league-<yyyyMMdd-HHmmss>.json`, written by «처음부터».
- App-internal SharedPreferences `league_unsettled` = `{<matchId>:{result,at}}`. On the next load, `League.db()` applies it if that match is still open, then clears it. It is idempotent.

**Migration:** missing keys mean season 1, `seasons []`, career 0 and `voids []`. No rewrite happens on load.

**Known side effect on old apps:** after a new season, an old app would show the season W/L as 통산. This is accepted and documented.

**New season (`League.newSeason`):**
- Requires no open playing/resume match; a `ready` match is voided automatically.
- Archives the season row.
- LP: `lp' = lp > 1250 ? round5(1250 + (lp−1250)/2) : lp`. 무쌍 → master off, MR reset.
- MMR is kept, so the existing `g` gap factor gives ×1.5 gains and ×0.6 losses until LP catches up.
- Resets shield and streaks, clears `pending`, keeps `players` (rivals persist), `seed` and `pref`.
- `season+1`, new `season_start`.
- Uses the backup-and-rollback pattern of `hold`/`cancel`.

**«처음부터» (`League.restartAll`):**
- Copies league.json to the archive first, then builds a **fresh** `ranked` explicitly. It never just deletes `ranked`, because `upgradeRanked` would rebuild it from legacy data.
- The fresh object has a new seed, MMR 1000, placement 5, `players {}`, `matches []`, `seasons []`, career 0.
- It also deletes `ckpt_*`, keeps `pref`, and leaves the legacy keys untouched.

## 7. Implementation plan

**Paths.**
- Java files are in `/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/impl/ranked/app/src/main/java/com/dudu/pocketcore/`.
- Native files are in `/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/impl/ranked/app/src/main/cpp/`.

**Order:** P1 first. It is small and directly answers "never locked out".

| Phase | File / functions | Change | Size |
|---|---|---|---|
| **P1 Exits and entries** | `League.java`: `voidOpen(id, kind)`, `voidsLeft()`, `hold()` releases pending, `stashUnsettled`/`applyUnsettled` (in `db()`), `recoverDb()` | Void, budget and stash | ~180 |
| | `EmuActivity.java`: `leagueBlocked` → `leagueStuck(kind, why)` with the 3.8 choices; `leaguePoll` 3-strike → stash card | | ~120 |
| | `LeagueActivity.java`: always-on go button (G4); `openCard` choices = same as in-game; dbProblem card; hub launch for «재개»; season label from `ranked.season`; pending line | | ~120 |
| | `LaunchSheet.java` «랭크 매치 바로 하기 ›»; `MainActivity.openRanked(rom)` + shortcut action; new `res/xml/shortcuts.xml` + manifest meta-data | | ~70 |
| **P2 Waiting window** | New `RankQueue.java`: ticket {pick, waitMs, avgSec, activeMs, state, afk, stageSel, handoff}, `start/pause/resume/tick/cancel/found` | | ~180 |
| | `RankCore.java`: `waitMs`, `avgWaitSec`, wait-dependent sigma in `pick`, `news(seed, day, me, book)` (deterministic, from drift) | | ~110 |
| | New `RankTips.java` (framedata facts, my-main from `result.p1blk>>4`, no opponent tips) | | ~80 |
| | `League.java`: split `rankedPick` → `rankedPeek` (no write) + `rankedHold(pick)`; `rankedRecent(n)`; `todayRecord()` | | ~60 |
| | `RankUi.java`: `Search` → `Lobby` (tabs, widening, tips, buttons, height cap); `found(…, acceptSec, afk)`; `vs(…)`; `strip(…)` | | ~260 |
| | `EmuActivity.java`: `rankTick` drives `RankQueue` (ev 8/16 tabs, 32/64 tips, 5 s accept, AFK); `rankLobbyShow`; `rankWaitElsewhere(practice\|board)`; `onMenu`/`onPause`/`onResume` defer and pause instead of cancel; banner case 6 | | ~150 |
| **P3 Queue while practising or browsing** | `EmuActivity.java`: `queuePoll` (normal session, 150 ms), `queueStrip*`, `queueCardShow/Key/Accept/Decline`, round-end defer, `|| queueCardUp` at the `nativeSetPaused` sites (onMenu, sheet close, Ask onDismiss, hubReturn); `rankArm(p, stage, go)` (refactor of `rankGo`); `hubStart` `rank_accept` path + VS card + 10 s timeout; result pill «연습하며 대기»; `handleAction(ACT_RANK)` | | ~330 |
| | `PadView.java`: `ACT_RANK = 18`, cell appended after «컬러 만들기» (keeps indices), `setRankCell(on, queued)` | | ~30 |
| | `LeagueActivity.java`: queue strip + Handler poll, found Dialog, accept intent, «대기창으로 ›» | | ~130 |
| | `native.c` + `league.h`: `nativeRoundLive()`, true when RAM 0x40A7==241 && 0x411A==1 && (0x5824&0x70)==0, read from system RAM. Used only for verified ROMs; otherwise the card pops immediately. `Emu.java` declaration. | | ~25 |
| **P4 Seasons** | `League.java`: `newSeason()`, `restartAll()`, `seasons()`, career | | ~170 |
| | `LeagueActivity.java`: «시즌·기록» section, both dialogs with computed preview, wait setting, peak plate in `myCard` | | ~150 |
| | **Total** | | **~2,165 Java + ~25 C** |

No `H` struct fields are added, so the `.prac` blob size is unchanged. The accept path reuses `hubReturn(-4)`.

## 8. Tests

**JVM tests** (extend `/home/user/CustumApKS/handoff/ss2_next/ranked/tests/jvm/`):
1. `RankQueueTest`
   - The active clock pauses across background; under 60 s it continues, over 60 s it is cancelled.
   - `handoff` is not counted as a pause.
   - due → found; the AFK flag; decline keeps pending.
   - The accept ticket's id check and fallback.
2. `RankCoreTest` additions
   - waitMs: median per hour and tier bucket, bounds of 3–90 s, held 2–4 s, fast mode 2–6 s.
   - avgWaitSec is constant for a ticket.
   - Sigma widens with the wait.
   - `news` is deterministic per (seed, day).
3. `RankTipsTest`: no tip mentions the opponent's character; the my-main fallback works.
4. `LeagueRankedTest` additions
   - `rankedPeek` writes nothing; `rankedHold` writes pending.
   - `hold()` releases pending.
   - Void budget: 2 per 7 days, version voids free.
   - The stash is applied once and is idempotent.
   - `recoverDb` renames the file.
5. `LeagueSeasonTest`
   - LP math: 2410 → 1830, 9000/master → 5125; MMR kept; players and pref kept; pending cleared; season row archived.
   - `restartAll`: archive file exists, new seed, placement 5, legacy untouched, ckpt deleted, refused while a playing match exists.
   - An old-format file (no new keys) loads.
   - Old-app round-trip: unknown keys survive.

**Host tests** (extend `/home/user/CustumApKS/handoff/ss2_next/ranked/tests/host/`):
1. `t_ranked_accept.py`: power-on → `league_hub_match(go=0)` → reset → `league_hub_return(-4)` → state 3 with the fixed opponent and knobs on the 4 ROMs, within about 70 frames.
2. Arcade round → reset → ranked: fight bytes compared with the `t_ranked` baseline (residual RAM).
3. `nativeRoundLive` truth table across round start, KO and the between-rounds screen.
4. `e1_idle`: 10 min idle in H_SEARCH on the title, and on char select, on the 4 ROMs. This covers waits up to 90 s plus a 60 s AFK card.

**Emulator tests**
1. Waiting-window layout at 360×640 dp portrait and in landscape; tab and tip keys from the on-screen pad and a physical pad.
2. Queue → «연습하며 기다리기»: clock continuity across the switch; strip placement; card pops immediately in practice.
3. Card over practice: open and close the pad bar and the sheet under it (no unpause leak); A and B from the pad and from a physical pad; 10 s countdown frozen while the bar is open.
4. Accept → VS → char select in about 3 s or less; VS timeout fallback (simulate by blocking the reset).
5. Home during the search (under 60 s resumes, over 60 s cancels); kill with the card up → re-serve in 2–4 s.
6. Each stuck card: delete the ckpt; fake a core change; make the league dir read-only for the stash.
7. New season and 처음부터 from LeagueActivity; launcher sheet link; app shortcut.

## 9. Risks and what is deliberately left out

**Risks**
- **Longer waits may annoy.** The default median is about 8–12 s, never padded, and «빠르게» exists. Plain waiting has content.
- **«가상 리그 소식» touches the stated principle** «온라인 사람처럼 보이게 하지 않는다» (RankUi.java:14–18). Every number comes from the real simulated pool, and the feed is labelled «가상 리그 소식 · 모두 CPU». **The user should confirm this one item.** If they reject it, drop the tab; nothing else depends on it.
- **Pause leaks.** There are 19 `nativeSetPaused` sites. The audited ones are listed in P3; the emulator test 3 covers them.
- **SF6-style freeze at the training→match handoff.** Mitigated by the VS card, the 10 s timeout and the fallback to the waiting window.
- **Practice is not the ranked environment.** Practice runs on the user's ROM, mods and core; ranked runs on the fixed copy and bundled core. That is acceptable for warm-up.
- **Accepting mid-arcade with autosave off loses the run.** The user is warned at queue start.
- **Title idle beyond 90 s is untested today.** Covered by the 10 min host test.
- **Void budget abuse.** Bounded to 2 per week. Kill-to-void needs an actual crash, because swipe and force-stop both checkpoint.
- **Old app sharing the folder.** Season W/L shows as 통산 there. Accepted.

**Left out on purpose**
- **Practice inside the league session (option 3b).** Too much coupling between the hub and Java.
- **A queue that keeps running in the background with notifications.** That needs the Android 13 permission and is not worth it for CPU opponents.
- **Real dodge penalties or LP loss for declining.** The held opponent is the penalty.
- **Rank-range and region pickers, ping bars, live «n명 대기 중» counters, minigames.**
- **Automatic calendar season resets.** Seasons are user-triggered only.
- **Per-character ranks.**
- **A queue strip in the launcher list.**
# Design proposal: ranked waiting panel (대기창) and league always one tap away

Recommended design, written from the simplicity/fun-first angle.

Worktree: `/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/impl/ranked`. Java files are under `app/src/main/java/com/dudu/pocketcore/`. Line numbers come from the current tree, which has another agent's uncommitted edits in it, so treat them as approximate and use the function names as anchors.

## 0. The decision in one paragraph

**The wait stays short and honest.** Keep `RankCore.pick` timing as it is: 2–6 s for about 96% of players, at most 12 s, and 1.2–2.4 s for a held opponent. Do not make it longer to feel real.

**The bare "상대 찾는 중…" box becomes a real 대기창.** It covers the game area and, in those few seconds, shows:
- where I stand and what is at stake;
- today's record and goal;
- one useful tip;
- the stage choice, moved here from the found card;
- a reel of the actual candidates the matcher looked at, which slows down and lands on the opponent.

**League becomes impossible to lose.** It is:
- one tap away from wherever the player already is: the pause menu in the normal game, the launcher sheet, and the league screen;
- one tap back out to "my game";
- free of dead ends: every block card has a button that moves forward;
- restartable through a «처음부터 다시 하기» that archives the old record and never deletes it.

**Effort and risk.** No native change and no new session switching. About 730 lines of Java. Play-while-waiting is deliberately left for later (§7).

---

## 1. How I read the two requests

**«랭매 대기때 뭐 할지도 결정해야겠네 — 대기창이 있다거나»**

The user wants a decision on what the player sees and does during the ranked search, and suggests a waiting window. Today it is a small box over a frozen title screen, and only B does anything.

My answer: a full-size 대기창. Its job is to make the few seconds feel like the moment before a match, not dead time. It does three things:
- **Anticipation:** the candidate reel and the stakes line.
- **Progress:** LP bar, placement, today's record, first-win bonus.
- **One small choice:** the stage (◀▶), plus tips the player can flip.

It does not stretch the wait and does not add minigames.

**«리그모드는 언제든 다시할수있게 방도를 마련»** — all three readings are covered:

| Reading | Delivered as |
|---|---|
| (a) Get back into league from anywhere, anytime | **In:**<ul><li>«리그 대전» cell in the normal-game pause menu (Back opens it).</li><li>«랭크 매치 바로 하기» in the launcher sheet.</li><li>The league screen button is always shown.</li></ul>**Out:** «내 게임으로» at the league title. |
| (b) Never locked out | <ul><li>Every block card gets a forward button («기권하고 새로 찾기», «다시 시도»).</li><li>A match left before round 1 is voided automatically (already true in the hub; now also from the league screen).</li><li>A system hold releases the held opponent.</li><li>An opponent is held only once the player has actually seen their card.</li></ul> |
| (c) Start over | «처음부터 다시 하기» in the league screen's 규칙 tab. It starts a new season at placement 5/5. The old ranked record goes to an archive file and shows as a «지난 시즌» line. |

---

## 2. User-facing flow, screen by screen

### 2.1 Getting in

| Where the player is | What they do | Result |
|---|---|---|
| Normal SS2 game (any screen, even mid-fight) | Back opens the pause bar, then tap the new cell **«리그 대전»** | Banner «리그 대전으로…», the normal game autosaves where it is, the league session opens straight into the search. |
| Same, but autosave is off and not at the title | Tap «리그 대전» | Ask card. Title «리그 대전으로». Body «자동 저장이 꺼져 있어 지금 판은 이어지지 않아요. 갈까요?». Buttons [가기] [취소]. |
| Launcher, SS2 card | Options chip, then **«랭크 매치 바로 하기  ›»** (gold, above «리그 순위표  ›») | League session, straight into the search. |
| League screen (LeagueActivity) | Main button, which is now **always shown** with a label that depends on state | See §2.5. |
| Title row 3 (either session) | Unchanged | Unchanged. |

### 2.2 대기창 (replaces `RankUi.search`)

Placed at the top of the game box, width `min(root-24dp, 340dp)`, height capped to the game box.

```
┌──────────────────────────────────┐
│ [릴 56dp]  상대 찾는 중…           │
│            0:03 · 예상 0:06        │
│ 칼끝노인 · 무사 ★3   ← reel text, dim, changes every 0.3 s
│ ──────────────────────────────── │
│ 검객 ★2 · 1,240 LP · 다음 ★까지 60 │
│ [■■■■■■□□□□]                      │
│ 비슷한 상대 기준 · 이기면 +25 · 지면 -20 │
│ 오늘 2승 1패 · +35 LP · ●●○●○      │
│ 오늘 첫 승 보너스 +30 남았어요      │
│ ──────────────────────────────── │
│ 팁 3/12  약베기는 버튼을 뗄 때 나가요 — 꾹 쥐면 강베기 │
│ ──────────────────────────────── │
│ ◀   스테이지 · 상대 기본   ▶        │
│ [ 취소 (B) ]                       │
│ 오늘 38,214명 접속   ← existing rotator │
└──────────────────────────────────┘
```

**Header**
- «상대 찾는 중…».
- «m:ss · 예상 m:ss». The estimate is `ceil(searchMs/1000)+1` s. It is fixed when the search starts, so it never goes up, and the card usually arrives "early".

**Reel**
- Avatar, nickname and tier label of the candidates `RankCore.pick` actually sampled (up to 8), cycling every 300 ms.
- In the last 600 ms it slows down (300 → 450 → 650 ms) and lands on the chosen opponent at full brightness. Then «상대 발견!» appears.
- If the pick had no candidates (rival pick), fall back to today's random avatars.

**My block**
- Normal: «<티어> · N LP · 다음 ★까지 N» (or «승급까지 N») plus an LP bar.
- Shield on: the line ends in red with «· 강등 위기!».
- During placement: «배치 경기 n/5 — 결과로 첫 티어가 정해져요». The bar and stakes line are hidden.
- Master: «무쌍 · MR 1712».

**Stakes line**
- «비슷한 상대 기준 · 이기면 +25 · 지면 -20».
- Computed from `RankCore.stakes(me, me.mmr)`. It is honest because it is labelled "비슷한 상대 기준". Use ASCII `-` for minus.

**Today line**
- «오늘 W승 L패 · ±N LP · ●○…».
- Up to 5 dots for the most recent results: ● win, ○ loss, · draw.
- Hidden if there are no games today.

**Bonus line**
- «오늘 첫 승 보너스 +30 남았어요» when `lastWinDay != today`, otherwise «오늘 첫 승 보너스 받았어요».

**Streak line**
- Kept from today: «3연승 중!» and «다음엔 이겨요».

**Tip line**
- «팁 k/N <text>». Changes every 5 s, on ▲/▼, or on tap.
- Starts at a different tip on each search (index advances in memory, seeded by the day).
- General tips only. **Never matchup tips for the picked opponent**, because that would spoil «상대 발견!».

**Stage row**
- «◀  스테이지 · <상대 기본|무작위|이름>  ▶». Changed with ←/→/OPTION or by tapping the arrows.
- Saved with `League.setPrefStage` as today.
- Changing the stage **during the search does not turn off auto-accept.** Changing it on the found card still does, as today.

**Bottom**
- [취소 (B)].
- Existing rotator: «오늘 N명 접속» / «비슷한 실력 찾는 중» / «상대는 모두 게임 CPU 예요» / «범위 넓히는 중…». The last one appears once more than half of `searchMs` has passed and only when `searchMs ≥ 5000`.

**Held opponent (pending) variant**
- Title «상대가 기다리고 있어요…».
- The reel is replaced by that opponent's dimmed avatar, with sub-line «지난번에 카드를 본 상대예요» and estimate «곧 만나요».

**Banner under the game while searching:** «B 취소 · ◀▶ 스테이지 · ▲▼ 팁». This replaces the current text, which repeats the overlay.

**Tips v1** (12 strings in `RankTips`; each traceable to framedata.md or app rules; all checked against the font):
1. «약베기는 버튼을 뗄 때 나가요 — 꾹 쥐면 강베기»
2. «B 혼자는 공격이 아니에요 — ↓B 는 튕겨내기(5F부터)»
3. «붙어서 → 나 ← + A 길게 = 잡기, 3F 에 나가요»
4. «다운됐을 때 ↓ 나 ↑ 를 쥐면 44F 빨리 일어나요»
5. «다운됐을 때 뒤를 쥐면 굴러서 일어나요»
6. «연습 대전에선 프레임 미터로 발동·경직을 볼 수 있어요»
7. «오늘 첫 승엔 +30 LP 보너스»
8. «재대결은 같은 상대와 연속 3판까지»
9. «상대 카드에서 나가도 그 상대는 하루 동안 기다려요»
10. «연승 중엔 조금 더 센 상대가 나와요»
11. «배치 5판이 끝나면 첫 티어가 정해져요»
12. «화면 패드: 약베기는 짧게 톡 — 오래 쥐면 강베기»

### 2.3 «상대 발견!» card and after

- **Unchanged:** avatar, tier, LP, h2h, stakes and the 3 s auto-accept.
- The stage row shows the stage chosen during the search.
- A accepts and goes to char select. B or «나가기» returns to the title on row 3; the opponent is held for 24 h, with toast «상대가 기다려요 — 다음에 또 만나요».
- The result card is unchanged: [다음 상대] [재대결] [그만]. «다음 상대» goes straight back to the 대기창, which is the endless loop.

### 2.4 Getting out (league session)

Back at the league title opens the `hubLeave` card:
- Title «리그 대전». Body «어디로 갈까요?».
- Buttons: [계속] [내 게임으로] [순위표] [목록으로].
- «내 게임으로» calls `switchSession(false,false)`. The normal session resumes its autosave, including mid-fight if the player left from the pause cell.

This makes the round trip: game → Back → «리그 대전» → … → 그만 → Back → «내 게임으로».

### 2.5 League screen main button (LeagueActivity)

| State | Button | Action |
|---|---|---|
| No open match | «랭크 매치 하러 가기  ›» | As today. |
| Open match `ready` | «랭크 매치 하러 가기  ›» | Launch the hub. `hubStart` already voids `ready` matches. The held opponent comes back in 1.2–2.4 s. |
| Open match with a checkpoint | «이어서 하기  ›» | Launch the **hub**, not single-match mode. `hubStart` resumes, and the match ends on the in-game result card with [다음 상대]. |
| Started, no checkpoint, or ROM mismatch | «기권하고 새로 찾기  ›» | AlertDialog (allowed here because there is no GL surface). Title «기권하고 새로 찾을까요?». Body «멈춘 경기는 기권패로 기록돼요(진 것과 같아요). 그다음 바로 새 상대를 찾아요.». Buttons [기권하고 찾기] [취소]. Then `League.forfeit` and launch the hub. |
| `dbProblem` / `writeProblem` | Red reason line plus «다시 시도» pill | `League.reload()`, then `render()`. |

The open-match card above the button stays as it is.

### 2.6 In-game block cards

**`leagueBlocked` (hub):**
- Title «멈춘 리그 경기가 있어요».
- Body depends on the cause:
  - No checkpoint: «앱이 갑자기 꺼져서 이어할 자리가 없어요. 이 경기는 기권패로만 정리할 수 있어요(진 것과 같아요).»
  - Checkpoint failed to load: «이어할 자리를 불러오지 못했어요. 기권패로 정리하거나 나중에 다시 해 볼 수 있어요.»
  - ROM/core mismatch: «경기를 시작한 롬과 지금 롬이 달라요. 원래 롬으로 바꾸면 이어할 수 있어요. 지금 정리하려면 기권패예요.» followed by the existing technical reason in brackets.
- Buttons:
  - [기권하고 새로 찾기] (gold, first) runs `League.forfeit(id)`, toasts «기권패로 정리했어요 · LP -N» (from `lp_delta`, or «배치 1패» during placement), then calls `hubReturn(-3)`. That resets the core and goes straight into the search.
  - [리그 화면으로].
  - [게임으로], only when the player came from the game.
- Ask's "first key press only selects" behaviour stops a mashed pad from forfeiting by accident.
- In single-match mode (`!leagueHub`) the first button is [기권], which forfeits and shows the result in LeagueActivity.

**«리그 대전을 열 수 없어요»** (`hubBlockedBack` / `leagueBlocked` because of `dbProblem` or `writeProblem`): add [다시 시도], which runs `League.reload()` and then `hubStart()` again.

### 2.7 Start over (LeagueActivity, 규칙 tab, bottom)

- Pill «처음부터 다시 하기» in the muted / LOSE colour.
- AlertDialog:
  - Title «처음부터 다시 할까요?».
  - Body «배치 5판부터 새 시즌으로 시작해요.\n지금 티어·LP·전적·상대 전적은 지우지 않고 ‘지난 시즌’으로 보관해요.\n되돌릴 수는 없어요.»
  - If a match is open, add «\n진행 중인 경기는 무효로 닫혀요.».
  - Buttons [처음부터] [취소].
- On success, toast «시즌 2 — 배치 경기부터 시작해요».
- The my-card line changes from the hard-coded «· 시즌 1» to «· 시즌 N».
- New dim line once a past season exists: «지난 시즌 · 시즌 1 최고 검호 ★2 · 34승 20패».

---

## 3. Behaviour rules

| Event | During the search | Found card showing |
|---|---|---|
| B / tap 취소 | Cancel, title on row 3, toast «그만뒀어요». **No opponent held** (new). | `rankLeave`: opponent held, toast «상대가 기다려요 — 다음에 또 만나요». |
| Back | Same as B | Same as B |
| ←/→/OPTION | Change stage, keep auto | Change stage, auto off (as today) |
| ▲/▼ or tap tip | Next tip | — |
| A | Ignored | Accept |
| Pause bar opened | **Freeze**: timer, reel and auto-accept stop and resume when the bar closes. Today it cancels. Uses the existing `rankFrozenAt` logic. | Freeze, same |
| Ask card on top | Freeze (existing) | Freeze (existing) |
| App to background (`onPause`) | Cancel (as today), nothing held | Cancel, opponent held (pending was saved at card time) |
| App killed | Nothing persisted, so the next search is fresh | Pending persisted, so the next search is «상대가 기다리고 있어요…» in 1.2–2.4 s |
| Auto-accept | — | 3 s, frozen while paused or an Ask is up |

**Timers**
- Search uses `searchMs`, unchanged.
- The reel settles in the last 600 ms, inside `searchMs`.
- Tips change every 5 s.
- The estimate is shown once and never changes.

**Pending (held opponent)**
- Now written when the card **shows** (`rankCardShow`), not when the search starts. This matches design doc ranked.md:191.
- Released on settle, forfeit, after 24 h, or (new) when a ranked match is put on `hold`.
- A voluntary void before round 1 keeps it, so the player cannot dodge an opponent they have seen.

**Pause cell visibility (normal session)**
- Shown when: the game is SS2, `!ranked()`, `hubOn()`, and `League.dbProblem == null`.
- It does **not** require `practiceRomOk()`, because the league session builds its own original-plus-translation copy. This partly fixes G1.
- `writeProblem` is checked on tap and shown as a toast with the reason.

---

## 4. Data and store changes (league.json)

**Changes**
- `ranked.season`: now read. Defaults to 1 when missing.
- `ranked.season_start`: unchanged meaning.
- `ranked.prev`: new array, newest first, at most 20 entries: `{season, from, to, lp, peak_lp, master, mr, w, l, d, games, file}`.
- `ranked.pending`: same shape, but written at card show. **No migration**; existing pending entries keep working.
- Archive file (new): `league/archive/ranked-s<season>-<yyyyMMdd-HHmmss>.json` containing `{"v":1,"kind":"ranked_season","archived_at":ms,"app":versionCode,"ranked":{…the whole old ranked object, matches included…}}`. Written atomically (`atomicWrite`) **before** league.json changes.

**`restartRanked()` builds the new ranked object explicitly.** It does not delete `ranked` and does not call `upgradeRanked`, which would re-migrate the legacy league:
- Kept: `rv`, `gen`, and the **same seed**, so it is the same world, the board stays coherent and no caches churn.
- Set: `season+1`, `season_start=now`, `mmr 1000`, `placement 5`, `games 0`, `lp 0`, `peak_lp 0`, all streaks 0.
- Emptied: `players {}`, `recent []`, `matches []`.
- Dropped: `pending`, and `legacy` (that one stays in the archive). The 규칙 tab line «옛 리그 기록 … 시작 실력을 정했어요» shows only while `season == 1`.
- Untouched: top-level `me`, `opps`, `matches`, `pref`.

**Migration:** none. No `v` bump. Older app versions keep unknown nested keys (see League.java:327).

---

## 5. Implementation plan (Java only, no native)

Land this after the other agent's uncommitted edits to EmuActivity, League, LeagueActivity and RankCore are committed.

**Step 1 — 대기창 (~350 lines)**
- `RankCore.java`: add `List<Player> reel` to `Pick`. Fill it inside `pick()`'s candidate loop with the sampled candidates other than `best`, up to 8. It does not touch the RNG, so determinism tests are unaffected. Empty on the pending and rival paths. (+10)
- `RankTips.java` (new, pure Java): `String[] TIPS`, `next(int day)`. (~60)
- `League.java` (+50):
  - `rankedPick` stops writing pending; new `holdPending(Pick)` does it.
  - `todayInfo()` returns today's W/L/D, LP sum and the last 5 outcomes from `rmatches()` (settled ranked matches, KST day via `RankCore.today`), plus whether the first-win bonus is still available.
- `RankUi.java` (+150, −35): `search(Context, Typeface, Wait w, Runnable onCancel, onStageL, onStageR, onTip)` with a small `Wait` holder (my label, LP bar fraction, stakes, today, bonus, streak, active, estimate, reel players, held flag). `Search.tick(ms)` drives the reel, settle, rotator and tip. `bar()` moves here from LeagueActivity, which reuses it.
- `EmuActivity.java` (+70):
  - `rankSearchShow` builds `Wait`.
  - `rankTick` search branch handles ev 4/8/16 (stage, auto stays on), 32/64 (tip), and freezes when `pad.isBarOpen()`.
  - `rankCardShow` calls `League.holdPending`.
  - `onMenu` (≈:176) removes `rankCancel(null)`.
  - Banner case 6 text changes.

**Step 2 — no dead ends (~150 lines)**
- `EmuActivity.leagueBlocked`: new texts plus «기권하고 새로 찾기». Helper `blockedForfeitAndSearch()` runs `League.forfeit`, a toast, then `hubReturn(-3)`; in single-match mode it calls `leagueExit(id)` instead. `leagueStart` passes a cause code instead of a free text. (+45)
- `hubBlockedBack` and the `hubStart` db/write branch: [다시 시도]. (+15)
- `League.hold`: when `isRanked(m)` and `pending.id == m.opp`, remove pending. (+5)
- `League.reload()`: synchronized `db=null; dbProblem=null; db();`. (+8)
- `LeagueActivity.render`: button state table from §2.5, the forfeit dialog, the retry pill. All launches go through the existing hub intent. (+60)

**Step 3 — one tap in/out (~90 lines)**
- `PadView.java`: `ACT_LEAGUE = 18`, `UTIL_LEAGUE = 9`. Extend `utilLabel`, `utilSub` and `utilAct` to 10 entries, add `leagueCell` to `utilVisible`, add `setLeagueCell(boolean)`, close the bar on tap. This copies the `ACT_LOOK` / `UTIL_LOOK` end-append pattern. (+15)
- `EmuActivity` (+40):
  - `handleAction` case `ACT_LEAGUE`: Ask if autosave is off and the screen is not the title, else `switchSession(true,false)`.
  - New `leagueCellSetup()` called next to `practiceSetup` after `loadCore`.
  - `hubLeave` gets «내 게임으로» and the new body text.
- `LaunchSheet.java`: the «랭크 매치 바로 하기  ›» link. (+8)
- `MainActivity.openRanked(File rom)`: the same cleanup as `openLeague`, then EmuActivity with `EXTRA_LEAGUE_HUB` and `EXTRA_HUB_GO`. (+15)

**Step 4 — start over (~140 lines)**
- `League.java` (+90):
  - `synchronized boolean restartRanked()`: refuse if `dbProblem`, or if a **legacy** match is open (top-level `matches`).
  - Ranked open matches are set to `cancelled` with why «처음부터 다시 — 보관» inside the copy that gets archived, and every `ckpt_*.state` / `.tmp` is deleted.
  - Order: write the archive, then build the new ranked object, then `save()`. If the save fails, roll back with `db = new JSONObject(backup)` and delete the archive file.
  - Also `season()` and `prevSeasons()`.
- `LeagueActivity.java` (+50): 규칙 tab pill and dialog, «시즌 N», «지난 시즌» line, and dropping the cached board after a restart.

**Total:** about 730 lines of Java plus about 300 lines of tests. No changes to `league.c`, `native.c` or the `.prac` blob size.

---

## 6. Tests

Use the existing harness under `/home/user/CustumApKS/handoff/ss2_next/ranked/tests/`.

**JVM: `jvm/RankCoreTest`**
- `reel` is a subset of the candidates, excludes the pick, holds at most 8, and is empty on the pending and rival paths.
- The same seed gives the same pick and the same `searchMs` as before (regression).

**JVM: `jvm/LeagueRankedTest`**
- Pending: `rankedPick` writes nothing; `holdPending` writes; the next pick returns the same opponent in 1.2–2.4 s; `cancel` before round 1 keeps it; `hold` releases it; settle releases it.
- `restartRanked`:
  - the archive file equals the old ranked object byte for byte after a JSON round trip;
  - the new ranked object has placement 5, `season+1`, the same seed, `players {}`, no pending and `matches []`;
  - `prev[0]` holds the right peak and record;
  - top-level `matches`, `opps` and `pref` are unchanged;
  - an open ranked match ends up cancelled in the archive and its checkpoint is deleted;
  - it refuses on `dbProblem` and on an open legacy match;
  - with a read-only dir the save fails, memory rolls back, and no archive file is left behind.
- `reload()` clears `dbProblem` once the file becomes readable.
- `todayInfo()` handles the KST midnight boundary.
- `run_old.sh`: the old app reads and rewrites the file and keeps `ranked.prev` and `season`.

**JVM: new `jvm/RankTipsTest` and glyph test**
- Parse the cmap of `app/src/main/assets/fonts/pixel.ttf` and assert that every character in `RankTips` and in the new UI strings (a list kept in the test) exists in the font.
- I checked the font: ▲▼◀▶●○★·…± are present; U+2212 is not; only the 2,350 KS X 1001 Hangul syllables exist.

**Host: `host/t_ranked.py`, new item `search_keys`**
- In H_SEARCH, press ↑ ↓ ← → OPTION for 300 frames on 4 ROMs.
- Assert the ev bits arrive, `R_MCUR` stays 2, and the title MODE is unchanged.
- Then `go` must still reach char select.

**Host: new `idle_search`**
- 36,000 frames (10 min) on the title with the hub in H_SEARCH, and on the found-card state.
- Assert no attract demo and that the menu is still visible. Today only 90 s is measured.

**Emulator (`android_emu.sh`)**
- Panel layout at 360×640 and 411×891, portrait and landscape: nothing clipped, no overlap with the pad, readable pixel font.
- Search keys: ←→ changes the stage and the card still auto-accepts after 3 s; ▲▼ flips tips; B, Back and Home behave as in the §3 table.
- Pause bar during the search: the timer stops while the bar is open and resumes when it closes.
- Cancel during the search, then search again: a different opponent, and no «기다리고 있어요» line.
- Kill the app while the card is up, relaunch: the held variant appears within 2.4 s.
- Normal game mid-fight → Back → «리그 대전» → search → 그만 → Back → «내 게임으로»: the same fight frame. With autosave off: the confirmation card appears.
- `kill -9` mid-fight (no checkpoint), re-enter: «기권하고 새로 찾기» → toast with the LP change → search. Also check the LeagueActivity button label in this state.
- Restart: «시즌 2», placement 1/5, the «지난 시즌» line, and the archive file exists.

---

## 7. Risks, and what is deliberately left out

**Risks**
- **Panel height** on small phones and in landscape. Cap it to the game box height. Drop rows in this order if it overflows: tip, today, stakes.
- **Reel cost:** `League.pfOf` and `Avatar.of` run once per 300 ms tick on the UI thread, for up to 8 profiles. Measure it on the emulator. If a tick takes more than 16 ms, precompute the 8 profiles on a background thread at search start. `pfOf` holds the League lock, so keep that work short.
- **Pause cell switching mid-fight** relies on autosave; the Ask card covers the autosave-off case. Also check that `PadView`'s layout loops handle a 10th util cell; the look cell is the precedent.
- **Freeze instead of cancel when the bar opens:** check that no `nativeSetPaused` recompute unpauses under the panel. The bar close path already recomputes, and the panel does not need the game to run.
- **One-tap forfeit on the block card:** the gold first button is the forward path. Ask's select-first behaviour protects pad users; touch users read the consequence in the body text.
- **Restart cannot be undone in the app.** The archive allows manual recovery, and the dialog says it cannot be undone.
- **Merge conflict risk** with the in-flight edits to the same four files.

**Left out, on purpose**
- **Playing arcade or practice while waiting** (the challenger interrupt, or practice in the normal or league session). The wait is 2–6 s, a session switch takes about as long or longer, and both need native or lifecycle work. Revisit if the user asks for something like «기다리는 동안 연습».
- **Longer or "realistic" waits**, a time-of-day factor, or a setting for wait length. Players resent idle waiting (MK1 and GG Strive complaints).
- **A world feed** such as «○○님 승급». It conflicts with the "no online imitation" principle in `RankUi.java:14-18`.
- **Automatic or soft seasons** (LP pulled 50% toward the baseline), season rewards, title plates. The manual restart plus the «지난 시즌» line covers reading (c) for now.
- **Voiding a started match after a crash.** That would let a player kill the app to escape a loss. Forfeit stays the only exit, but it is now one tap away on every block card. Periodic checkpoints at round breaks are a possible later improvement.
- **App-icon shortcut and sticky league on cold start.**
- **Automatically moving an unreadable record aside when `dbProblem` is set** (the rename already failed once, so only a retry is offered), and the endless settle-save retry (G9).
- **Picking my character before the call.** It stays in the game's own char select screen, as ranked.md §7 Q2 decided.
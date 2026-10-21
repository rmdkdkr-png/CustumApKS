# Final spec: ranked 대기창 + «리그 언제든 다시» (build 148)

**Starting point**
- Base: worktree `/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/impl/ranked`, HEAD `7b35ba2` (147). The tree is clean.
- Java path: `app/src/main/java/com/dudu/pocketcore/`. Native path: `app/src/main/cpp/`.
- Line numbers are approximate. Use the function names as anchors.

**Native changes: none.**
- Every key the waiting window needs already reaches Java as `ev` bits in `H_SEARCH`.
- Every "go back to search" path reuses `hubReturn(-3)`.
- No `H` struct fields are added, so the `.prac` blob size is unchanged.

**How this was put together**
- Spine from the engineering judge's winner (robust): never get stuck, then the 대기창, then seasons.
- From simple: the pad-bar cell, «내 게임으로», the candidate reel, picking the stage during the search, and a restart that keeps the same seed.
- From realism: a modest, honest increase in wait time with a «빠르게» option; «재개» goes through the hub; the line showing when a held opponent expires; season plates.
- Dropped, because the judges found them risky or unwanted:
  - realism's 90 s waits, wider pick spread (sigma), void budget, AFK rules, native round probe, queue across activities, and news feed;
  - robust's archive restore and its `failSaves` hook in production code.

---

## 1. 결정 요약

1. **대기창**: 지금의 작은 «상대 찾는 중…» 상자 대신, 게임 화면을 덮는 대기창을 띄워요. 실제로 훑어본 후보 선수들이 돌다가 내 상대에게 멈춰요. 그동안 내 티어·LP 막대, 오늘 전적, 팁 한 줄을 보고 스테이지(◀▶)도 골라요.
2. **기다리는 시간**: 4~9초쯤으로 살짝 늘려 읽을 틈을 둬요. 저녁엔 조금 빠르고 새벽엔 조금 늦어요. 리그 화면에서 «빠르게»(지금처럼 2~6초)로 바꿀 수 있어요. 예상 시간은 처음에 정해지고 늘어나지 않아요.
3. **상대 잡기**: 상대는 카드를 본 다음에만 잡혀요. 찾는 중에 B로 그만두면 아무도 잡히지 않아요.
4. **언제든 들어가기**: 일반 게임 멈춤 바에 «리그 대전» 칸이 생겨요(싸우는 중에도 뒤로 → 한 번). 런처에 «랭크 매치 바로 가기»가 생기고, 리그 화면 버튼은 늘 보여요. 리그 판에서 «내 게임으로» 바로 돌아가요.
5. **절대 안 막히기**: 앱이 멈춰서 이어할 수 없는 경기는 LP 그대로 «무효로 닫고 계속» 할 수 있어요. 막힘 카드마다 그 자리에서 푸는 버튼(기권·다시 확인·권한 설정·나중에 정산)이 있어요.
6. **처음부터**: 리그 화면 규칙 탭에 «새 시즌 시작»(LP 반쯤 내림, 실력 점수 그대로)과 «처음부터 다시»(배치 5판부터)를 둬요. 옛 기록은 지우지 않고 보관해요. 고정돼 있던 «시즌 1» 글자도 실제 시즌 번호로 바뀌어요.
7. **연습하며 기다리기**(SF6처럼)는 다음 빌드에서 해요. 이번 빌드는 안 막히고 쉽게 들어가는 것부터 해요. C(네이티브)는 고치지 않고 자바만 고쳐요.

---

## 2. How the two requests are read and covered

### Request 1: «랭매 대기때 뭐 할지 / 대기창»

**Decision.** The wait becomes a short, readable pre-match moment.
- The player gets one real choice (the stage).
- The player gets something to watch (the reel landing on the real opponent).
- The player gets one useful thing to learn (a tip measured in SS2).
- The player sees where they stand: tier, LP bar, today's record, bonus or streak.

**Wait length.** The «보통» default goes from 2–6 s to 4–9 s, with a mild time-of-day factor and a 15 s cap. That makes the panel readable without dead time. «빠르게» keeps today's 2–6 s. A held opponent stays at 1.2–2.4 s.

**What stays honest.**
- The estimate is computed when the search starts and never rises.
- The reel only shows players the matcher actually sampled.
- «상대는 모두 게임 CPU 예요» stays in the rotating line.
- There is no fake news feed and no live «n명 대기 중» counter.

**Practice or arcade while waiting** (SF6 / Tekken style) is **v2**. Its accept path is already proven: persisted pending, then `nativeHubMatch(go=false)`, then `hubReturn(-4)` straight to char select. It is deferred because each cycle needs two session switches and the 21 `nativeSetPaused` call sites would need auditing.

### Request 2: «리그모드는 언제든 다시할수있게 방도를 마련». All three readings ship.

| Reading | What ships |
|---|---|
| **(a) Get back in from anywhere** | <ul><li>A «리그 대전» cell in the normal-session pad bar (Back, then one tap, even mid-fight). It does not depend on `practiceRomOk`, which fixes G1/G2.</li><li>A launcher-sheet link «랭크 매치 바로 가기».</li><li>The LeagueActivity main button is always shown, with a label that depends on state (fixes G4).</li><li>«내 게임으로» in `hubLeave` gives a real round trip back to the autosaved game.</li><li>«재개» launches the hub, so every resumed fight ends on [다음 상대].</li></ul> |
| **(b) Never locked out** (primary) | <ul><li>Every block card offers a forward action on the card itself.</li><li>A free void when the app is at fault: no checkpoint, a checkpoint that won't load, or an app version change.</li><li>Forfeit is still available, with a confirm step.</li><li>Storage cards offer [다시 확인] and [권한 설정 열기] (G8). After 3 failed saves the player gets [나중에 정산하기] instead of an endless toast (G9).</li><li>Every hold releases the held opponent, and two stale misses release it too (G7).</li><li>An opponent is held only after the card has been seen.</li><li>LeagueActivity voids a leftover `ready` match when it opens.</li><li>`pref.last_rom` is the fallback when no ROM path is passed.</li><li>`startActivity` is wrapped in try/catch so the `leaving` flag is reset on failure (G19).</li></ul> |
| **(c) Start over** | <ul><li>«새 시즌 시작»: a soft reset. LP above the post-placement landing point is halved toward it; MMR, games and rivals are kept.</li><li>«처음부터 다시»: placement 5/5 again, with the same world (same seed).</li><li>Both write an archive file first and add a «지난 시즌» row. Nothing is deleted.</li><li>The «시즌 N» label is read from `ranked.season` (fixes G10).</li></ul> |

---

## 3. User flows, screen by screen (exact Korean texts)

### 3.1 Ways in

| Where | Control | Result |
|---|---|---|
| Normal SS2 game, any screen (title, arcade, practice, mid-fight) | Back opens the pause bar, then the new cell **«리그 대전»** (sub-line «랭크 매치») | <ul><li>Autosave on: banner «리그 대전으로…», then `switchSession(true,false)`, which autosaves where you are and lands in the 대기창.</li><li>Autosave off: Ask card «리그 대전으로» / «자동 저장이 꺼져 있어서 지금 판은 이어지지 않아요. 갈까요?» [가기] [취소].</li><li>`League.writeProblem()` set: toast «리그 기록을 쓸 수 없어요 — 저장소 권한을 확인해 주세요».</li></ul> |
| Launcher, SS2 card, then options sheet | **«랭크 매치 바로 가기  ›»** (gold, directly above «리그 순위표  ›») | `MainActivity.openRanked(rom)` lands in the 대기창. If `League.dbProblem`/`writeProblem()` is set, it opens LeagueActivity instead, which shows the storage card. |
| LeagueActivity | Main button (state table in §3.6) | Hub intent |
| Title row 3 (either session) | unchanged | unchanged |
| Ranked result card | [다음 상대] [재대결] [그만] | unchanged; [다음 상대] goes back to the 대기창 |

**When the pad cell shows** (`leagueCellSetup()`), all of these must hold:
- the game is SS2 (same check as `practiceSetup`);
- `!ranked()`, `leagueId == null`, `!leagueHub`;
- `hubOn()`;
- `League.dbProblem == null`.

It does **not** require `practiceRomOk()`, because the league session builds its own ROM copy.

### 3.2 The 대기창 (replaces the content of `RankUi.search`)

**Placement.** Top of `gameBox`, width `min(root−24dp, 340dp)`, height capped to the game box. When `gameBox` is shorter than 300dp (landscape or small phones), compact mode drops the tip and "today" rows.

```
┌──────────────────────────────────┐
│ [reel 56dp]  상대 찾는 중…         │
│              0:03 · 예상 0:07      │
│ 칼끝노인 · 무사 ★3                 │ ← reel line, dim
│ ──────────────────────────────── │
│ 검객 ★2 · 1,240 LP                 │ ← tier colour
│ [■■■■■■□□□□]  다음 ★까지 60 LP     │
│ 오늘 2승 1패 · +35 LP  ●●○         │
│ 첫 승 보너스 +30 남았어요           │ ← note line (one)
│ ──────────────────────────────── │
│ 팁 · 약베기는 버튼을 뗄 때 나가요  ▲▼ │
│ ◀   스테이지 · 상대 기본   ▶        │
│ [ 취소 (B) ]                       │
│ 오늘 38,214명 접속                  │ ← existing rotator
└──────────────────────────────────┘
```

**Header**
- «상대 찾는 중…», then «m:ss · 예상 m:ss».
- The estimate is `ceil(waitMs/1000)+1` s. It is fixed when the search starts, so the card arrives on time or a little early.

**Held-opponent variant**
- Title «기다리던 상대에게 가는 중…», time line «0:01 · 곧 만나요».
- The reel line is replaced by «지난번 카드에서 본 상대예요», with that opponent's avatar dimmed.

**Reel**
- Avatar plus «<닉네임> · <티어>» for the candidates `RankCore.pick` actually sampled (`Pick.reel`, at most 8).
- Cycles every 250 ms. The last two steps slow to 350 ms and 450 ms. At `rankEnd − 500 ms` it lands on the real opponent at full brightness, then the card appears.
- If `waitMs` is under 2.5 s: no slow-down, it just lands at `rankEnd − 500`.
- If the reel is empty (rival pick) or the profiles are not loaded yet: the existing random-avatar spinner, with no names.

**Rank line**
- «<티어> · N LP» (thousands separator).
- «배치 경기 n/5»
- «무쌍 · MR 1,712»

**Line under the bar**
- «다음 ★까지 N LP»
- «승급까지 N LP»
- «강등 위기!» (LOSE colour, when the shield is on)
- During placement there is no bar and the line reads «5판을 마치면 첫 티어가 정해져요».

**Today line**
- «오늘 W승 L패 · ±N LP  ●○·»: up to 5 dots, newest on the left. ● win, ○ loss, · draw. Use ASCII `-` for minus.
- With no games today: «오늘 첫 판이에요».

**Note line** (one line, first match wins)
- «N연승 중!» (streak ≥ 2)
- «다음엔 이겨요» (losing streak ≥ 3)
- «첫 승 보너스 +30 남았어요» (when `last_win_day != today`)
- otherwise hidden.

**Tip line**
- «팁 · <text>» with «▲▼» at the right.
- One new tip per search. ▲/▼ or a tap flips it. It never names the already-picked opponent.

**Stage row**
- «◀  스테이지 · <상대 기본|무작위|이름>  ▶», changed by ←/→/OPTION or by tapping the arrows.
- It calls `League.setPrefStage`. **Auto-accept stays on.** It only turns off when the stage is changed on the found card, as today.

**Bottom**
- [취소 (B)].
- The existing rotator: «오늘 N명 접속» / «비슷한 실력 찾는 중» / «상대는 모두 게임 CPU 예요». Once elapsed time passes `waitMs/2`, and only when `waitMs ≥ 6000`, it adds «범위 넓히는 중…».

**Keys during the search**

| Key | Action |
|---|---|
| B or Back | Cancel |
| ←/→/OPTION | Stage |
| ▲/▼ | Tip |
| A | Ignored |

**Banner (case 6)**
- While searching: «B 취소 · ◀▶ 스테이지 · ▲▼ 팁»
- While the card is up: unchanged «A 대전 · B 나가기 · ◀▶ 스테이지»

**Tips** (`RankTips.TIPS`, 12 entries, all checked against the font, none about a specific character):
1. «약베기는 버튼을 뗄 때 나가요 — 꾹 쥐면 강베기»
2. «B 혼자는 공격이 아니에요 — ↓B·→B 는 튕겨내기»
3. «튕겨내기는 누르고 5프레임부터 16프레임 동안 받아요»
4. «←B 는 B 로 치는 공격이에요»
5. «붙어서 → 나 ← + A 길게 = 잡기, 3프레임 만에 나가요»
6. «다운됐을 때 ↓ 나 ↑ 를 쥐면 빨리 일어나요»
7. «다운됐을 때 뒤를 쥐면 굴러서 일어나요»
8. «필살기는 한 틱 일찍 넣어도 나가요 — 보통 기술은 선입력이 없어요»
9. «연습 대전에선 프레임 미터로 발동·경직을 볼 수 있어요»
10. «오늘 첫 승엔 +" + BONUS_DAILY + " LP 보너스»
11. «지고 바로 재대결에서 이기면 설욕 보너스 +" + BONUS_REVENGE»
12. «상대 카드에서 나가도 그 상대는 하루 동안 기다려요»

No tip quotes the 7 vs 8 frame strong-slash threshold, because it differs between the one-button and two-button cores.

### 3.3 The «상대 발견!» card

It is unchanged (avatar, tier, LP, h2h, stakes, stage ◀▶, [대전 (A) 3] [나가기 (B)], 3 s auto-accept), plus:
- A dim line «기다린 시간 0:07».
- **A is ignored for 400 ms after the card appears**, so an A press from the end of the search cannot accept an opponent the player hasn't seen.
- **The held opponent is saved here**: `League.holdPending(rankPick)` runs in `rankCardShow()`.
- Leaving (B, Back or «나가기») holds the opponent and shows the toast «상대가 기다려요 — 다음에 또 만나요» (unchanged).

### 3.4 Leaving the league session: `hubLeave`

**At the title**
- Title «리그 대전», body «어디로 갈까요?».
- Buttons: [계속] [내 게임으로] [순위표] [목록으로].

**At char select**
- Body unchanged: «상대 고르기를 그만둘까요? …».
- Buttons: [계속] [타이틀로] [내 게임으로] [순위표].

**«내 게임으로»**
- Cancels a `ready` record as a user back-out (`League.cancel`, which does not count as a miss).
- Then calls `switchSession(false,false)`. The normal session resumes its autosave, including mid-fight or mid-practice if the player left from the pad cell.

### 3.5 Block cards inside the game

All of these are Ask cards with `cancelable(false)`. Ask's "first key press only selects" behaviour protects pad users. A forfeit always asks once more, which protects touch users:
- Title «기권할까요?».
- Body «이 경기는 기권패로 기록돼요 (LP -N).», or during placement «배치 1패로 기록돼요.».
- Buttons [기권] [취소].
- N comes from `RankCore.stakes(me, start.opp_mmr)[1]`.

**A. Started match: no checkpoint, or the checkpoint won't load** (`void_kind` "crash" / "ckpt")
- Title: «멈춘 경기를 이어할 수 없어요»
- Body: «vs <닉> · <티어>\n앱이 멈춰서 이어할 자리가 없어요.\n무효로 닫으면 LP·전적은 그대로예요.» When the load failed, the second line is «이어할 자리를 불러오지 못했어요.»
- Buttons: **[무효로 닫고 계속]** (first), [기권하고 계속], [리그 화면으로], and [게임으로] only when the session came from a game (`EXTRA_FROM_GAME`).
- What happens:
  - Void: `League.voidStarted`, toast «무효로 닫았어요 — LP 그대로 · 바로 상대를 찾아요», then `hubReturn(-3)` into the search. The same opponent comes back in 1.2–2.4 s.
  - Forfeit: confirm, then `League.forfeit(id)`, then `leagueExit(id)`, which shows the ranked result card with [다음 상대].
  - In single-match mode (only reachable from an old intent restored from recents) the labels are [무효로 닫기] / [기권], and both return to LeagueActivity.

**B. Started match, ROM changed, same app version**
- Title: «다른 롬으로 바뀌었어요»
- Body: «경기를 시작한 롬: <m.rom 파일 이름>\n지금 롬: <현재>\n원래 롬으로 되돌리면 이어할 수 있어요.»
- Buttons: [기권하고 계속] [리그 화면으로] ([게임으로])

**B′. Started match, ROM or core problem, and `m.app != BuildConfig.VERSION_CODE`** (`void_kind` "app")
- Title: «앱이 바뀌어 이어할 수 없어요»
- Body: «앱을 업데이트해서 이 경기를 이어할 수 없어요.\n무효로 닫으면 LP·전적은 그대로예요.»
- Buttons: **[무효로 닫고 계속]** [기권하고 계속] [리그 화면으로] ([게임으로])

**C. Storage** (`hubStart` with `dbProblem` / `writeProblem`; this replaces `hubBlockedBack` and the storage branch of `leagueBlocked`)
- Title: «리그 기록 파일을 못 읽어요» (dbProblem) or «리그 기록 폴더에 쓸 수 없어요» (writeProblem)
- Body: «저장소 권한을 확인한 뒤 «다시 확인»을 눌러 주세요.\n(<League.dir path>)»
- Buttons:
  - [다시 확인]: `League.reload()`. If the problem is cleared, close the card and call `hubStart()` again. That is safe because the blocked `hubStart` returned before any native call. Otherwise toast «아직 안 돼요 — <이유>».
  - [권한 설정 열기]: `StorageAccess.open(this)`.
  - [게임으로] when coming from a game, otherwise [리그 화면으로].
- ROM-unverified, core and load-failure blocks keep today's text and buttons. They cannot be fixed in the app.

**D. Saving the result fails 3 times** (`leagueRetry ≥ 3`, about 3 s). Store this in its own field `leagueSaveAsk`, **not** `leagueDlg`, which `leaguePoll` dismisses on every pass.
- Title: «결과를 저장하지 못했어요»
- Body: «결과는 이 판에 그대로 있어요.\n저장소를 확인한 뒤 다시 시도해 주세요.»
- Buttons:
  - [다시 시도]: retry now.
  - [권한 설정 열기]
  - [나중에 정산하기]: `leagueSaveCkpt()`, then toast «다음에 리그를 열면 정산해요», then `goList()`. If the checkpoint also fails: toast «이 판도 저장하지 못했어요 — 권한을 먼저 확인해 주세요», and the card stays.
- Background retries keep running every 1 s. If one succeeds, the card closes by itself and the flow continues.

**E. Other toasts that replace silent closes**
- Title menu vanished during the search: «찾기를 멈췄어요 — A로 다시 찾기»
- Returning after the app went to the background mid-search: «앱이 내려가서 찾기를 멈췄어요 — A로 다시 찾기»
- Returning after it went to the background with the card up: «상대가 기다려요 — 다음에 또 만나요»
- Match record vanished mid-match (defensive, `lm()==null`): Ask «리그 기록이 바뀌었어요» with [리그 화면으로].

### 3.6 LeagueActivity (no game view, so AlertDialog is allowed)

**On open** (`onCreate`/`onNewIntent`), unless `League.liveHub`:
- `League.markInterrupted()` as today.
- `int n = League.voidReady("순위표를 열며 정리(대진 전)")`. If n > 0, toast «첫 라운드 전에 멈춘 경기를 무효로 닫았어요 — 같은 상대가 기다려요».

**ROM path.** If `rom == null`, use `League.lastRom()` when that file exists.

**Main button**

| State | Button / card | Action |
|---|---|---|
| No open match | «랭크 매치 하러 가기  ›» | Hub intent (rom, `EXTRA_LEAGUE_HUB`, `EXTRA_HUB_GO`) |
| Open match with a checkpoint | «멈춘 경기 이어서 하기  ›». The open card shows [기권하고 찾기] [이어서 하기]. | Hub intent. `hubStart` auto-resumes (E7) and the match ends on the in-game result card. |
| Open, `voidKind != null` (no or bad checkpoint, app changed) | Main button hidden. Open card text «앱이 멈춰서 이어할 자리가 없어요. 무효로 닫으면 LP·전적은 그대로예요.» (or the B′ text), with [무효로 닫고 찾기] [기권하고 찾기]. | Void or forfeit, then the hub intent |
| Open, ROM changed, same app | Card text «원래 롬으로 되돌리면 이어할 수 있어요.» with [기권하고 찾기] | Forfeit, then the hub intent |
| `dbProblem` / `writeProblem` | Storage card «리그 기록 파일을 못 읽어요» / «리그 기록 폴더에 쓸 수 없어요», the reason and path, then [다시 읽기] [권한 설정 열기] | `League.reload()` then `render()` / `StorageAccess.open` |
| No ROM at all | existing «롬 경로가 없어 …» line | — |

**Forfeit dialog**
- Title «기권하고 새로 찾을까요?»
- Body «멈춘 경기는 기권패로 기록돼요 (LP -N). 그다음 바로 새 상대를 찾아요.»
- Buttons [기권하고 찾기] [취소]

**My card**
- «전국 21,663위 / 39,899명 · 시즌 N», with N from `League.season()`. This replaces the hard-coded «시즌 1» at :248.
- When past seasons exist:
  - the record line adds «· 통산 43승 34패»;
  - a dim line «지난 시즌 최고 · 검호 ★2».
- Held-opponent line: «기다리는 상대 · 칼끝노인 (검호 ★1) — 내일 21:04 까지». Use «오늘 HH:mm 까지» when it expires today.

**«보류·무효 경기» list.** It also shows ranked voids after the match started, e.g. «무효 · 칼끝노인 — 앱이 멈춰 이어할 자리가 없음» or «… — 앱이 바뀌어 닫음».

**«규칙» tab: new section «시즌 · 기록»**
- «시즌 N · M월 D일부터 · W승 L패»
- One row per past season:
  - «시즌 1 · 최고 검호 ★2 · 마지막 검객 ★5 · 31승 25패»
  - for a restart row: «시즌 1 · 처음부터 다시 · 최고 … · …»
- «매칭 대기» with a two-pill toggle [보통] [빠르게]. Caption «보통: 4~9초쯤 (새벽엔 조금 더) · 빠르게: 2~6초». Stored in Settings `pocketcore_rank_wait` = `normal` | `fast`.
- [새 시즌 시작], caption «LP 를 반쯤 내리고 승패를 0부터 세요 · 실력 점수는 그대로».
  - During placement it is hidden, and the line «배치 경기를 마치면 새 시즌을 열 수 있어요» shows instead.
  - Dialog title: «새 시즌을 시작할까요?»
  - Dialog body: «시즌 N 기록은 ‘지난 시즌’에 남아요.\nLP 3,920 → 3,310 (검호 ★2 → 검객 ★5)\n승패·연승은 0부터, 실력 점수와 상대 전적은 그대로라 빨리 올라와요.» The preview comes from `League.newSeasonPreview()`.
  - Buttons: [시작] [취소]. Then toast «시즌 N+1 시작!».
- [처음부터 다시] (LOSE colour), caption «지금 기록은 보관해요 · 배치 5판부터».
  - Dialog title: «처음부터 다시 할까요?»
  - Dialog body: «티어·LP·전적·상대 전적을 처음으로 돌리고 배치 경기 5판부터 시작해요.\n지금 기록은 지우지 않고 보관 파일과 ‘지난 시즌’에 남겨요.\n앱 안에서 되돌릴 수는 없어요.»
  - Buttons: [처음부터] [취소]. Then toast «시즌 N+1 — 배치 경기부터 시작해요».
- When a tool is not allowed:
  - a started match is open: both buttons disabled with «끝나지 않은 경기를 먼저 정리해 주세요»;
  - `League.liveHub`: «게임 속 리그를 닫은 뒤에 할 수 있어요».
- Any failure: «저장하지 못했어요 — 기록은 그대로예요».
- After any reset: drop the board cache (`boardKey`) and call `render()`.

**Rules copy fix.** «상대 카드가 뜬 뒤 나가면, 그 상대와 붙을 때까지 다음 찾기에 같은 상대가 나와요 (최대 24시간). 찾는 중에 그만두면 잡히지 않아요.»

**Legacy line.** The «옛 리그 기록 …» line already reads `ranked.legacy`. A restart drops that key, so the line disappears by itself.

---

## 4. Edge cases

### 4.1 Events during the search, the card and the hand-off

| Event | Searching | Card up | After «대전» (≤2 s go wait) |
|---|---|---|---|
| B / Back / tap 취소·나가기 | `rankCancel("그만뒀어요")`; **nothing held** | `rankLeave`: held, «상대가 기다려요 — 다음에 또 만나요» | ignored |
| Pad bar opened | **Freeze, don't cancel**: remove `rankCancel` from `onMenu`; `rankTick` already freezes via `rankFrozenAt`. **Hide the panel** (`INVISIBLE`) while the bar is open, because `rankView` sits above PadView and covers the top bar row when `barLow` is false (landscape, edit). Restore on close; `rankTick` sets visibility each pass. | Same; the 3 s countdown is frozen too | frozen |
| Bar «목록»/«종료» → `hubLeave` | stays frozen; every exit leaves cleanly | same; opponent stays held | same |
| Ask card on top | freeze (existing) | freeze | freeze |
| App to background (`onPause`) | `rankCancel(null)`, set `rankStopNote`; toast on `onResume` | silent leave (held); toast on resume | existing 2 s timeout → «상대를 잡지 못했어요 — 다시 찾아 주세요» |
| Title menu disappears (`st != 6` with `rankView != null && rankGoAt == 0`) | close, toast «찾기를 멈췄어요 — A로 다시 찾기» | same; opponent held | n/a |
| A | ignored | accept, ignored for the first 400 ms | — |
| No input | the card appears at `waitMs` | auto-accept after 3 s, unless the stage was changed on the card | char select (no timer, no LP at risk) |

### 4.2 App killed or crashed: what's on disk and what happens next

| State when killed | On disk | Next entry |
|---|---|---|
| Searching (crash mid-queue) | nothing new | fresh search |
| Card up | `ranked.pending` | «기다리던 상대에게 가는 중…», 1.2–2.4 s |
| Char select | `ready` + `pending` | `hubStart` or LeagueActivity voids `ready` as **stale** (`pending.miss += 1`); same opponent. After 2 misses `pending` is dropped and a new opponent comes. |
| Fight, normal kill (`onPause` ran) | checkpoint, status `resume` | resumes once automatically (hub E7) |
| Fight, crash (no `onPause`) | no checkpoint | card A (void or forfeit) |
| Result decided, save failed | the checkpoint, if «나중에 정산하기» succeeded | resumes on the deciding frame, then settles (existing `FROM_CKPT` path) |
| Result card | settled | title |

### 4.3 Other edge cases

- **Restored from recents after process death.** Same intent extras, so the hub reopens with `HUB_GO` into a search. `League.liveHub` is reset by process death.
- **LeagueActivity alive while a league EmuActivity is alive.** This is unlikely, because the task stack makes the launcher icon resume EmuActivity. As a guard, `League.liveHub` is set in `hubStart` and cleared in `onDestroy`/`goList`/`leagueExit`/`switchSession`. While it is set, LeagueActivity skips `markInterrupted`/`voidReady` and disables the season tools.
- **Pad cell mid-practice.** `switchSession` autosaves with the `.prac` blob, as today's title path does. Covered by an emulator check.
- **Pad cell with autosave off.** Always ask, wherever the player is. The app cannot reliably tell the title from other screens on modded ROMs, where no hub runs.
- **`startActivity` throws.** Wrap it in `switchSession`, `goList` and `leagueExit`.
  - In `goList`/`leagueExit`: reset `leaving` and toast «화면을 열지 못했어요 — 다시 눌러 주세요».
  - In `switchSession` the core is already unloaded, so try `MainActivity` as a fallback, then `finish()`.
- **Void abuse.** A void needs a real crash or a deleted checkpoint, because swipe-away and force-stop both run `onPause`, which writes the checkpoint. Accepted: league.json is user-editable anyway, and never getting stuck comes first. A ROM swap alone never unlocks a void.

### 4.4 Older builds sharing `league.json`

- `v` stays 1.
- All new keys are additive and nested. Builds ≤147 keep unknown keys when they rewrite the file.
- **147** sees:
  - «시즌 1» (cosmetic only);
  - the season W/L as its record;
  - voided-after-start matches as terminal `cancelled`, hidden as ranked cancels are today;
  - `pending` in the same shape, with the extra `miss` key preserved.
  
  147 still writes `pending` at search start. That is harmless: 148 honours it.
- After a restart, 147 skips `upgradeRanked` because `ranked` exists (League.java:775), so it never re-migrates legacy data.
- **≤146** ignore `ranked` entirely. Legacy top-level `me`/`opps`/`matches` are never touched by 148's resets.
- 148 never needs a migration pass. Missing keys mean season 1, `seasons []`, `miss 0` and no `last_rom`.

---

## 5. Data changes and migration

| Item | Change |
|---|---|
| `ranked.pending` | Same shape `{id, at, mmr, stage, knobs}` plus new `miss` (0–1; missing = 0). Now written by `holdPending()` when the card shows, not by `rankedPick()`. Re-holding the same id keeps `at` and `miss`. **Released** by `applyRanked` (as today), by `League.hold`, by **both** hold branches in `League.settle` (≈:563, :582), by the second miss, and by new season / restart. 24 h expiry is unchanged. |
| `ranked.matches[]` (void after start) | `status:"cancelled"`, `void_after_start:true`, `void_kind:"crash"\|"ckpt"\|"app"`, `why`. LP, MMR, `players` h2h, w/l and placement are untouched. |
| `ranked.matches[].resume_fail` | New `"nockpt"`\|`"badckpt"`, set by `leagueStart` next to the existing status/why. `voidKind()` reads this, not the Korean `why` strings. |
| `ranked.season`, `ranked.season_start` | Already written; now **read** for display and advanced by resets |
| `ranked.seasons` | New `[{n, start, end, kind:"season"\|"restart", games, w, l, d, peak_lp, peak_label, final_lp, final_label, master, mr, best, file}]`, newest last. 통산 = Σ rows + current. |
| `pref.last_rom` | New. The original ROM path, written by `hubStart` on success, only when it changed. |
| `league/archive/ranked-s<N>-<season\|restart>-<yyyyMMdd-HHmmss>.json` | New file: `{"v":1, "kind":"ranked_season"\|"ranked_restart", "archived_at":ms, "app":versionCode, "ranked":{…the whole old ranked object…}}`. Written atomically, read back and parsed **before** league.json changes. Deleted only when that same reset rolls back. Never deleted automatically. |
| Settings `pocketcore_rank_wait` | New, `normal` (default) \| `fast` |

**New season, `League.newSeason()`**
- `base = max(0, round10(lpOfMmr(mmr) − 300))` (the existing post-placement landing).
- `lp' = lp ≤ base ? lp : round10(base + (lp − base)/2)`, capped at `MASTER_LP − 10`.
- Master is turned off and `mr = 0`. It is recomputed on re-entry, as at RankCore:321.
- Reset: `w`/`l`/`d`/`streak`/`lstreak`/`best` to 0, `peak_lp = lp'`, `shield = false`.
- Kept: `mmr`, `games`, `recent`, `players`, `last_win_day`, `seed`, `matches`.
- `pending` is dropped. `season+1`, `season_start = now`.
- Example: lp 3,920 with base 2,700 → 3,310.

**Restart, `League.restartRanked()`.** It builds a fresh ranked object explicitly; it never deletes `ranked` and never calls `upgradeRanked`.
- Same `rv`, `gen`, `seed`.
- `season+1`, `season_start = now`.
- The values `upgradeRanked` gives a player with no legacy games: MMR from score 1000, `placement 5`, `games 0`, `lp 0`, `peak_lp 0`, no master or shield, all streaks 0.
- `recent []`, `players {}`, `matches []`.
- `seasons` = old rows plus a new `kind:"restart"` row.
- **No** `pending`, `legacy` or `last_win_day`.
- All `ckpt_*.state` and `.tmp` files are deleted.
- Top-level `me`, `opps`, `matches` and `pref` are untouched.

**Both resets**
- `synchronized`.
- Refused when `dbProblem` is set, when a `playing`/`resume` match is open, or when `liveHub` is set. A `ready` match is cancelled first, as a user back-out.
- Use the `hold()`/`cancel()` pattern: `backup = db.toString()`; on save failure `db = new JSONObject(backup)` and the archive file is deleted.

**Migration:** none.

---

## 6. Implementation plan (dependency order, Java only)

Build 148: set `versionCode` to 148 in `app/build.gradle`. Add `RankTips.java` to the `javac` line in `handoff/ss2_next/ranked/tests/jvm/run_jvm.sh`.

### Step 1: `RankCore.java` (pure, ~45 lines)
- `Pick`: add `int waitU; long waitMs; final List<Player> reel = new ArrayList<>();`.
- `pick()`:
  - Normal path: `int u = r.nextInt(4000); pk.waitU = u;` and keep `ms = 2000 + u + …`. This is the same single draw, so `searchMs`, the pick and the RNG order are unchanged.
  - In the 12-try loop, after the `recent` check: `if (pk.reel.size() < 12) pk.reel.add(p)`. After the loop: remove `best`, remove duplicates, trim to 8. No RNG draws.
  - Pending and rival paths: `reel` empty, `waitU = -1`.
- `static long waitMs(Pick pk, double myMmr, boolean fast, int hour)`:
  - `pk.pending || fast || pk.waitU < 0` → `pk.searchMs`.
  - Otherwise `base = 4000 + waitU*5/4`, `top = max(0, myMmr−1450)*60`, `hourF = 19–23h → 0.85, 2–6h → 1.4, else 1.0`, return `min(15000, round((base+top)*hourF))`.
- `static int estSec(long waitMs)` = `ceil(waitMs/1000.0)+1`.
- `static final int BONUS_DAILY = 30, BONUS_REVENGE = 20;` replacing the literals at ≈:305–306.
- `static int newSeasonLp(int lp, double mmr)` (formula in §5).

### Step 2: `League.java` (pure store, ~270 lines)
- **Pending**
  - `rankedPick(c)` stops writing. It sets `pk.waitMs = RankCore.waitMs(pk, me.mmr, "fast".equals(Settings.load().get("pocketcore_rank_wait")), hourOfDay())`.
  - New `synchronized holdPending(Pick)`: the moved write block; keeps `at`/`miss` when the id is the same.
  - Private `releasePending(opp)` and `pendingMiss(opp)` (at 2 → remove).
  - Call `releasePending` in `hold()` and in both hold branches of `settle()` when `isRanked(m)`.
- **Cancel and void**
  - `cancelStale(id, why)` = `cancel` + `pendingMiss`.
  - `setResumeFail(id, kind)`.
  - `static String voidKind(JSONObject m, int appVer)`: started match, and `resume_fail` set or the checkpoint missing → "crash"/"ckpt"; `m.app != appVer` → "app"; otherwise null.
  - `synchronized boolean voidStarted(id, kind)`: backup and rollback, delete the checkpoint, `pendingMiss`.
  - `synchronized int voidReady(why)`: loops `cancelStale` over `ready` matches; returns 0 when `liveHub`.
  - `holds()` includes `void_after_start`.
- **Infrastructure**
  - `static volatile boolean liveHub`.
  - `synchronized reload()`: `db = null; dbProblem = null; PF_CACHE.clear(); db();`.
  - `lastRom()` / `setLastRom(path)`.
- **Panel data**
  - `rankedToday()` → `{w, l, d, lpSum, last5[]}`. Settled and forfeit ranked matches on `today()` (KST); forfeit counts as L; cancelled and hold excluded.
  - `bonusLeft()`.
- **Seasons**
  - `season()`, `seasons()`, `careerWLD()`.
  - `resetBlockedWhy()` → reason string or null.
  - `newSeasonPreview()`, `newSeason()`, `restartRanked()`.
  - Private `writeArchive(kind)` (atomic write, read back, parse) and `seasonRow(kind, file)`.
  - Factor the no-legacy branch of `upgradeRanked` into `freshRanked(seed, season)`, so restart and migration share it.

### Step 3: `RankTips.java` (new, ~60 lines)
- `static final String[] TIPS`, built from §3.2 with the `RankCore` bonus constants.
- `static int next()`: a process-static index seeded from `today()`, advanced on each call.

### Step 4: `RankUi.java` (~170 lines)
- `static final class Wait`: `rankLine`, `rankColor`, `barFrac`, `barLine`, `danger`, `todayLine`, `dots`, `noteLine`, `estSec`, `held`, `heldAv`, `stageLabel`, `active`, `compact`.
- `Search` becomes a lobby view; keep the `search(...)` name. Signature: `search(Context, Typeface, Wait, Runnable onCancel, Runnable onStageL, Runnable onStageR, Runnable onTip)`.
- Methods:
  - `tick(elapsedMs, waitMs)`: «m:ss · 예상 m:ss», the rotator, reel stepping and the slow-down schedule;
  - `setReel(List<ReelItem{Bitmap av, String line}>)`;
  - `land(ReelItem)`;
  - `setStage(String)`;
  - `setTip(String)`.
- Only call `setText` when the text changed.
- `found(..., String waitedLine)` adds «기다린 시간 m:ss».
- Move `LeagueActivity.bar()` here as `RankUi.lpBar(...)`; LeagueActivity reuses it.

### Step 5: `EmuActivity.java`, waiting window (~110 lines)
- `rankSearchShow()`:
  - build `Wait` from `League.rankMe()`, `rankedToday()`, `bonusLeft()`, `RankTips.next()` and the stage label;
  - set `rankEnd = rankT0 + rankPick.waitMs`;
  - precompute the reel on a background thread (`League.pfOf` + `Avatar.of` for each `Pick.reel` player, line «닉 · label(lp)»), then post `setReel`;
  - set `compact` when the `gameBox` height is under 300dp.
- `rankTick()`:
  - Freeze branch: also `rankView.setVisibility(barOpen ? INVISIBLE : VISIBLE)`.
  - `st != 6` with `rankView != null && rankGoAt == 0`: toast «찾기를 멈췄어요 — A로 다시 찾기». Capture this before the existing clear.
  - Search branch:
    - ev 2 → cancel;
    - ev 4/8/16 → new `rankStageStepSearch(d)`: same stage cycling as `rankStageStep`, plus `League.setPrefStage` and `hubStageSel`, and **no** change to `rankAuto`;
    - ev 32/64 → tip;
    - at `rankEnd − 500` → `land(pick)`.
  - Card branch: `(ev & 1) != 0 && now − rankCardAt ≥ 400` → `rankGo()`.
- `rankCardShow()`: `League.holdPending(rankPick)`; pass `waitedLine`.
- `onMenu` (≈:176): delete `if (rankView != null) rankCancel(null)`.
- `onPause` (≈:1017):
  - if searching: `rankCancel(null)` and `rankStopNote = SEARCH`;
  - if the card is up: a silent leave and `rankStopNote = CARD`.
  
  `onResume` shows the matching toast.
- Banner case 6 (≈:1785): two texts, depending on `rankFound == null`.

### Step 6: `EmuActivity.java`, no dead ends (~150 lines), plus `StorageAccess.java` (new, ~25 lines)
- `StorageAccess.open(Activity)`:
  - API 30+: `ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION` with `package:`;
  - 26–29: `ACTION_APPLICATION_DETAILS_SETTINGS`.
  
  It never calls `requestPermissions` over the game. `MainActivity.askStorage` keeps its own runtime path.
- `leagueStart()`: for blocked started matches, call `League.setResumeFail` / `setStatus`, then `leagueBlocked(kind, why)` with kind `BLK_NOCKPT`/`BLK_BADCKPT`/`BLK_ROM`. When `League.voidKind(m, VERSION_CODE)` is "app", use B′.
- `leagueBlocked(int kind, String why)` builds cards A/B/B′/C (§3.5). The legacy one-argument form stays for load and version texts.
- `leagueResolve(boolean voidIt)`:
  - hub: void → toast → `hubReturn(-3)`; forfeit → `askForfeit(() -> { League.forfeit(id); leagueExit(id); })`;
  - single-match: `leagueExit`.
- `askForfeit(Runnable)`: the confirm Ask.
- `hubStart()`:
  - the storage branch goes to card C for both `fromGame` and not;
  - the `ready` loop uses `League.cancelStale`;
  - on success: `League.liveHub = true; League.setLastRom(rom)`.
- `hubReturn()` keeps `League.cancel`, a user back-out that is not counted as a miss.
- `leaguePoll`: show card D when `leagueRetry ≥ 3 && leagueSaveAsk == null`; dismiss it when a retry succeeds. Add `leagueSaveLater()`.
- `onDestroy`: if `leagueHub`, `League.liveHub = false`. Do the same in `goList`, `leagueExit` and `switchSession`.
- try/catch around `startActivity` (§4.3).

### Step 7: entries and exits (~70 lines)
- `PadView.java`:
  - `ACT_LEAGUE = 18` (confirm the id is unused), `UTIL_LEAGUE = 9`;
  - append «리그 대전» to `utilLabel`, grow `utilSub` to 10 with sub «랭크 매치», append `ACT_LEAGUE` to `utilAct`;
  - add a `leagueCell` flag in `utilVisible`, plus `setLeagueCell(boolean)` modelled on `setLookCell`;
  - add `ACT_LEAGUE` to both bar-close lists (≈:410 and ≈:974).
- `EmuActivity`:
  - `leagueCellSetup()`, called right after `practiceSetup` once the core loads;
  - `handleAction` case `ACT_LEAGUE` → `leagueFromGame()` (writeProblem toast / autosave Ask / `switchSession(true,false)`);
  - `hubLeave()`: «어디로 갈까요?» and «내 게임으로» (§3.4).
- `LaunchSheet.java` (≈:354): link «랭크 매치 바로 가기  ›» above «리그 순위표  ›», shown under the same condition.
- `MainActivity.java`: `openRanked(File rom)`. Same cleanup as `openLeague`; storage problem → `openLeague(rom)`; otherwise EmuActivity with `rom`, `EXTRA_LEAGUE_HUB`, `EXTRA_HUB_GO`.

### Step 8: `LeagueActivity.java` (~230 lines)
- On open: `liveHub` guard, `markInterrupted`, `voidReady` toast, `rom` fallback to `League.lastRom()`.
- `render()`:
  - the main-button state table (§3.6);
  - the storage card;
  - the held-opponent line;
  - `"시즌 " + League.season()`;
  - career totals and the past-season plate.
- `openCard()`: «이어서 하기» goes through the hub intent (not `launch(id, resume)`); [무효로 닫고 찾기] / [기권하고 찾기] use `League.voidKind`; forfeit uses the AlertDialog.
- The holds list shows void rows.
- `rulesTab()`: the «시즌 · 기록» section, the wait toggle, both dialogs with the computed preview, the rules copy fix, and dropping the board cache after a reset.

### Step 9: docs
- Add §8 «대기창 · 막힘 풀기 · 시즌» to `/home/user/CustumApKS/handoff/ss2_next/설계/ranked.md`.
- Add a handoff note `/home/user/CustumApKS/handoff/ss2_next/ranked/148_대기창_막힘풀기_시즌.md`.

**Size:** about 1,130 Java lines across 10 files, plus about 550 test lines. No changes to `league.c` / `native.c` / `league.h`.

---

## 7. Test plan

### JVM (`/home/user/CustumApKS/handoff/ss2_next/ranked/tests/jvm/`, same `ok(cond, what)` style)

**`RankCoreTest`: new `waitModel()`, `reel()`, `seasonLp()`**
- `waitModel()`:
  - normal mode is within [4000, 9000] × hourF, capped at 15 s;
  - hour buckets 21h < 14h < 4h for the same `waitU`;
  - fast mode equals `searchMs`;
  - a held opponent is within 1.2–2.4 s in both modes;
  - `estSec·1000 ≥ waitMs`.
- `reel()`:
  - a regression check: record about 20 (seed, Rng seed) → (`p.id`, `searchMs`) pairs from HEAD `7b35ba2` before editing, and assert they are identical after;
  - the reel holds sampled players only, never `best`, never `recent`, at most 8;
  - the reel is empty on the pending and rival paths.
- `seasonLp()`:
  - lp ≤ base is unchanged;
  - above base it is halved toward base;
  - results are multiples of 10, never negative, and < `MASTER_LP` from master.

**`LeagueRankedTest`: new functions called from `main`**
- `pendingTiming()`:
  - `rankedPick` leaves league.json byte-identical and creates no `pending`;
  - `holdPending` writes all fields;
  - the next pick returns the same id with `pending` true and `waitMs` ≤ 2400;
  - re-holding keeps `at`.
- `holdRelease()`:
  - `hold()` releases `pending`;
  - the settle knob-mismatch hold releases `pending` (fake `st`);
  - a user `cancel` keeps it;
  - `cancelStale` ×2 releases it (miss 1, then gone);
  - `voidStarted` ×2 releases it;
  - 24 h expiry still works (`at = now − 25h`).
- `voids()`:
  - the `voidKind` matrix: ready → null; playing without checkpoint → crash; resume with checkpoint → null; `badckpt` → ckpt; different app → app; ROM changed on the same app → null;
  - after `voidStarted`, `lp`/`mmr`/`w`/`l`/`placement`/`players` are unchanged, status is `cancelled` with `void_after_start` and `void_kind`, the checkpoint is deleted, and `holds()` lists it.
- `saveFailRollback()`:
  - make the save fail without a production hook by creating a **directory** at the exact tmp path `save()` writes (this works as root);
  - `voidStarted`, `newSeason` and `restartRanked` roll memory back and leave no archive file.
- `recover()`: set `dbProblem` via reflection; `reload()` clears it when the file is readable.
- `today()`: `rankedToday` across a KST 23:59 / 00:01 boundary; forfeit counts as L; `last5` is newest first.
- `seasons()`:
  - `newSeason` is refused during placement, with an open playing match, and when `liveHub`;
  - a `ready` match is cancelled first;
  - LP equals `RankCore.newSeasonLp`;
  - kept and reset fields match §5; `pending` is removed;
  - the `seasons[last]` row is correct;
  - the archive file parses and its `ranked` equals the state before the reset.
- `restart()`:
  - same seed, `placement 5`, `games 0`, `players {}`, `matches []`, no `pending`/`legacy`, `season+1`;
  - `seasons` is carried over plus a restart row;
  - top-level `me`/`opps`/`matches`/`pref` are deep-equal to before;
  - `ckpt_*` files are deleted;
  - after `restart()` and a reload from disk, `upgradeRanked` does not run and placement is still 5.
- `lastRom()`: set, then get; a second set with the same path doesn't write.
- `oldFile()`: a 147-format file loads with defaults and stays byte-identical on disk until a user action.

**`run_old.sh`**: run 147's suite against a file written by 148 (season 2, `seasons[]`, `pending.miss`, a void match, `pref.last_rom`). Assert those keys survive 147's write.

**New `RankTipsTest`**
- No tip contains a character name from RankCore's character table.
- `next()` cycles through all tips.
- Every tip fits 2 lines at 12sp in 340dp (≤ 40 characters as a proxy).
- A glyph test: parse the cmap (format 4/12) of `app/src/main/assets/fonts/pixel.ttf` and assert that every character in `TIPS` and in a listed set of the new UI strings is present. The arrows ↓↑←→, ▲▼◀▶●○★·…« » are present; U+2212 is not, and the test must reject it.

### Host (`/home/user/CustumApKS/handoff/ss2_next/ranked/tests/host/`; native is unchanged, these confirm the assumptions)
- **New `t_hub_resolve.py`.** Set up the hub with no `HUB_GO`, which is the state after a blocked resume. Call `league_hub_return(-3)` at frames 30, 200, 600, 1500 and 3000 (including the attract demo). It must reach `H_SEARCH` within 120 frames on the 4 ROMs. Also check `-4` after `league_hub_match(go=0)` reaches `H_PICK_ME` with the fixed opponent and knobs.
- **`t_ranked.py`, new item `search_keys`.** In `H_SEARCH`, press ↑↓←→ OPTION for 300 frames. The `ev` bits 32/64/8/16/4 must arrive, `R_MCUR` must stay 2, and MODE must be unchanged. A later `go` must still reach char select.
- **New `t_idle_long.py`.** 36,000 frames idle in `H_SEARCH` and on char select, on the 4 ROMs: the menu stays visible, no attract demo, nothing advances.
- Re-run `t_ranked.py` and `t_ranked_ckpt.py`: results must be unchanged.

### Emulator (API 28, portrait 360×640 and 411×891, one landscape pass)
1. **Panel layout**: nothing clipped, pixel font, compact mode in landscape, panel hidden while the bar is open (landscape top bar row stays tappable).
2. **Keys**:
   - ◀▶/OPTION change the stage and the card still auto-accepts after 3 s;
   - ▲▼ flips tips;
   - B/Back cancel; A is ignored during the search;
   - hold A across the end of the search → the card does not accept.
3. **Wait**: «보통» vs «빠르게» toggled in LeagueActivity; the shown estimate is never below the real time.
4. **Reel and held opponent**:
   - the reel lands on the opponent shown on the card;
   - leave the card, search again → «기다리던 상대에게 가는 중…» within 2.4 s;
   - cancel during the search, search again → no held line.
5. **Bar during the search**: the timer freezes and resumes with the right offset; bar «목록» → `hubLeave` with «어디로 갈까요?».
6. **Home**: during the search and during the card; the toasts appear on return; after the card the opponent is held.
7. **Round trip**: normal game mid-fight → Back → «리그 대전» → search → match → «그만» → Back → «내 게임으로» → same fight frame. Repeat mid-practice (dummy settings restored), with autosave off (Ask appears), and with a modded ROM (`practiceRomOk` false: the cell still shows and league opens).
8. **Launcher link** «랭크 매치 바로 가기» → search. With a simulated `dbProblem` → the LeagueActivity storage card.
9. **Crash mid-fight** (`adb root; adb shell kill -9 $(pidof com.dudu.pocketcore)`) → card A:
   - «무효로 닫고 계속» → search with the same opponent; LeagueActivity lists «무효 · …»;
   - the forfeit path → confirm → result card with [다음 상대].
10. **ROM swap mid-match** → card B. Set `m.app` to 147 in league.json → card B′.
11. **Settle failure** (make the league dir unwritable with root) → card D after about 3 s → «나중에 정산하기» → fix the dir → reopen → the match settles.
12. **Storage card C** in-game and in LeagueActivity → «다시 확인» / «다시 읽기» work.
13. **LeagueActivity**:
    - a leftover `ready` match is voided on open, with the toast;
    - button labels per state;
    - «멈춘 경기 이어서 하기» resumes in the hub and ends on the result card;
    - the held-opponent line and its expiry;
    - «시즌 N».
14. **Resets**: «새 시즌 시작» and «처음부터 다시»; files appear in `/sdcard/PocketCore/league/archive/`; the «지난 시즌» rows and 통산 are right; both are refused with an open match.
15. **Held-opponent loop**: kill the app at char select twice against the same opponent → the third search gives a new opponent.
16. **Old build**: install 147 over 148 data (or use `run_old.sh`); LeagueActivity opens and the data is kept.

---

## 8. Open questions (recommended default: implementation proceeds with these)

| # | Question | Default |
|---|---|---|
| 1 | Make the default wait longer (4–9 s) or keep 2–6 s? | **Longer «보통» by default**, with «빠르게» in the 규칙 tab |
| 2 | Practise or play arcade while waiting (SF6-style call) in this build? | **No: next build (v2)**, reusing pending + `hubReturn(-4)`, after the 10-minute idle test and a `nativeSetPaused` audit |
| 3 | Limit free voids (for example 2 a week)? | **No limit.** Voids are only for app faults; each is recorded and shown in «보류·무효 경기» |
| 4 | «처음부터 다시»: same world or a new 39,899-player world? | **Same seed** (same world, no cache churn); h2h is reset |
| 5 | In-app restore of an archive («되돌리기»)? | **Not in this build** (it allows save-scumming); the files stay on disk for manual recovery |
| 6 | Should the pad cell need the «리그·연습» option on? | **Yes** (respect the user's switch) |
| 7 | «가상 리그 소식» news feed in the 대기창? | **No** (it conflicts with RankUi's "no online imitation" rule) |
| 8 | «리그 순위표» link in the in-game options sheet as well? | **No.** The pad cell, plus `hubLeave` [순위표], covers it |
| 9 | Found-card auto-accept time? | **Keep 3 s** (char select has no timer, so nothing is lost) |
| 10 | Time-of-day factor on the wait? | **Yes, mild** (×0.85 evening, ×1.4 at 2–6 am); «빠르게» ignores it |
| 11 | Android app-icon shortcut «랭크 매치»? | **No** (four switchable activity-aliases, and it would cold-start EmuActivity) |
| 12 | Season number after «처음부터 다시»? | **Continues** (season+1), so the «지난 시즌» history stays unique |
| 13 | Should killing the app at char select count as a "miss" that can release the held opponent? | **Yes, after 2.** Backing out yourself with Back / «타이틀로» does not count |
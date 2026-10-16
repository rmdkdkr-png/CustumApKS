
## summary
The idea as given doesn't exist in the game. SS2 NGPC has no VS screen with both fighters' portraits or names before a 1-player bout, and the «대사» value R_SCR 8 (w149/int league.c:215 and :595) is not a dialogue screen. But the game does have its own pre-fight moment, and that is what I recommend using as the ranked VS screen: the **stage intro**. In it, the forced opponent and my pick stand facing each other on the chosen stage, with my look.c colour already applied. The opponent character's taunt types out in the bottom band. The top 32 px is an empty black band (plane 0, rows 0–3), which is where the fight HUD appears later.

The prototype draws a band rendered by Java (both nicknames, tier + stars, LP, and a red «VS» box in the game's HUD palettes and the app's pixel font) into that black band. It also skips the 29-second prologue for you, holds the intro for `hold` frames, and then presses A to move into the game's own «자아 당당히 → 1회전 → 승부» banner. Before the HUD appears it puts back every cell and tile it changed.

Results:
- The full suite passes on the real core with runahead 2 and frame generation on: 17 jobs, 353 checks, 0 FAIL (`/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/out_final_run2.log`).
- Coverage: 6 ROM variants; all 15 opponents, with both Asura and Galford as my character; next-opponent (−3), rematch (−4), a leftover band meant for another opponent, turning the band off while it is showing, mashing buttons, and saving a state mid-VS. The existing t_ranked, t_dual and t_hub_look tests also pass.
- t_practice passed (75 checks) only on an earlier build of this prototype; it was not re-run on the final build.

The diff applies cleanly to w149/int HEAD 4bced84, and builds to the same host .so that was tested. Against the current uncommitted w149/int working tree it applies with fuzz and no failed hunks. native.c, league.c and vsband.c compile with NDK 27 for aarch64. The Java tree, including RankVs, compiles against android-34. No adb or emulator was used.

## scene_facts
VERIFIED (Linux harness, Korean bundled ROM unless noted; tools in u153/vsgame/tests):
1. **What comes after the card screen in a 1-player first bout** (probe1/probe2/probe8b):
   - **Prologue:** MODE 241, R_SCR 0, FIGHT 0, 0x57CB = 0. A narrated silhouette scene, about 1760 frames if left alone. No fighter information at all.
   - **A during the prologue:** 0x57CB goes 3 → 6 → 0x0C about 47 frames later, and the intro starts at +53/54 frames (+64 with the hub's pulse timing).
   - **Stage intro:** MODE 240. R_SCR = 8 + 2 × (number of companions on screen): Nakoruru's hawk, Rimururu's ice spirit, Galford's dog. So it is 8, 10, 12 or 14, and the intro must be detected as R_SCR ≥ 8, not == 8. 0x57CB = 0x0C during the taunt phase.
   - **Without the hub:** card → round 1 = 2586 frames (43 s).
2. **The intro is the real match setup** (survey: 231 + 12 intro runs):
   - P1B/P2B (0x5B51/0x5D51) are already set on the first intro frame.
   - P2 always equals the forced 0x57DF/0x57E0: all 30 opponent × style pairs, and all 14 selectable player characters × 15 opponents.
   - The player's character is always on the left (X 120 vs 200).
   - The look.c match colour is already applied (sprite palette 0 FFF/444/222 → 2P FFF/988/222 → colour 3 FFF/832/310).
3. **Intro timing:**
   - The taunt phase lasts 214–426 frames if left alone, depending on the opponent (the taunt's first character appears 70–186 frames in).
   - A is accepted at any point in that phase (tested at 10…280 frames). It sends 0x57CB 0x0C → 0x18 → 0x1B → 0x1E → 0x21 (banner) → 0x27 → 0x2A (MODE 241, 195–214 frames later) → 0x2D (FIGHT = 1, +2).
   - A pressed during the banner does not shorten it.
4. **VRAM during the intro** (dumps, gfxregs.py):
   - Window is the full screen.
   - Plane 0 (scroll plane 1, scroll 0,0) is the UI overlay:
     - Rows 0–3 × cols 0–19 are tile 0x001, palette 0 (opaque black band).
     - Rows 4–16 are transparent; the banner's big letters later use tiles 0x00C–0x054.
     - Rows 17–18 hold the taunt in tiles 0x002–0x00B, palette 0 (drawn by the Korean patch; JUE shows its own text).
   - Plane 1 (scroll x 80–91, y 248) is the stage, tiles 0x106–0x1FF.
   - Sprites:
     - Fighters use 0x057–0x09C (player block from 0x057, ≤0x06E; opponent block 0x070–0x09C).
     - Companions in companion-vs-companion intros go up to 0x0AA.
     - Fight effects go up to 0x0CF.
     - 0x0D0–0x105 was never used in any run.
   - About 6 frames into the banner, the game rewrites the band as 0x1E01 (same tile, palette 15) and blanks the whole screen for about 8 displayed frames.
   - At MODE 241 the HUD replaces the band: face icons 0x045–0x048 / 0x053–0x056 on palettes 8–10, 1P/COM on palette 5, «수라» on palette 4, timer on palette 3.
5. **Plane 0 palettes during the taunt phase:**

   | Palette | Colours | Behaviour |
   |---|---|---|
   | 0 | FFF/666/000 | was EF6/52F before frame 85; flashes during the banner |
   | 1 | 7FF/E69 | changes at banner frame ~411 |
   | 2 | 7FF/25F | constant |
   | 3 | AFF/07F | constant |
   | 4 | FFD/E70 | constant |
   | 5 | FFF/00E | constant |
   | 6, 8 | 0FF/067/014 | colour 3 is not black |
   | 9 | EEE/777 | constant |
   | 13, 14 | FFF/666 | constant |
   | 15 | 0BD/00D | changes during the banner |

   8–11 change at MODE 241. Palettes 2, 3, 4, 5, 9, 13 and 14 stay the same from the intro through the end of the banner; every t_vs and t_vs15 run checks this.
6. **No portrait-style VS exists anywhere:**
   - The HUD face icons are only loaded at MODE 241.
   - The red winner nameplate appears only after the fight (plane 0 rows 5–8, cols 5–14, tiles 0x002–0x015, palette 1 reloaded to FFF/65F/00C, at MODE 241 / R_SCR 8 / 0x57CB = 63).
   - Later chapters add story interludes but no VS screen.
7. **Existing app hooks this builds on:**
   - native.c:402–404: input = (user & ~block) | league_in_or.
   - native.c:940–944: the hub only ticks on real frames.
   - native.c:1124: save state calls league_hub_before_save.
   - native.c:997–998: nativeLeagueHubReturn resets the core and calls league_hub_return.
   - EmuActivity.java:2644: but Java queues that call on the GL thread, so it runs later.
   - EmuActivity.java:2492 / :2631: nativeHubMatch with go = true / false.

INFERRED:
- Why R_SCR counts tasks (only the observed pattern is known).
- That the 195 vs 212-frame banner length depends on when A lands.
- That RAM timers could freeze or shorten the taunt or banner (not tried, not needed).
- Practice mode (league.c:595) presses A only when R_SCR == 8, so it skips the taunt only in intros without companions. Existing behaviour, untouched.

## design
**Recommended: the stage intro is the VS screen.** Only the empty black band at the top is overwritten; the bottom taunt line stays the game's own (mock-up: `/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/shots/MOCKUP_vs_flow.png`).

**Band layout** (160×32 px = 20×4 tiles; one palette per 8×8 cell, so differently coloured pieces split on cell edges; background colour 3 is opaque black, same as tile 0x001):
- **Line 1:** left = my nickname (player 1 is always on the left) plus an optional style tag in HUD blue (palette 4); right = opponent nickname, right-aligned. Each is limited to 77 px and ends in «…» if longer. Text is white with a grey drop shadow (palette 13), the same look as the game's taunt text.
- **Line 2:** left = tier name + small ★ and number (our own 5×5 / 4×7 pixel glyphs) + LP in the timer's orange (palette 3); centre = a red «VS» box in the same palette as the HUD's «1P»/«COM» (palette 5, cells 9–10); right = the mirror image. Tier colours: 수련생 grey, 낭인 light grey, 무사 orange, 검객 white, 검호 pale yellow, 달인 cyan, 검성 red, 무쌍 white with red shadow. These only use palettes whose colour 3 is black (2/3/4/5/9/13). Palettes 6 and 8 tint the cell background red (seen in the first mock-up, then fixed).
- Text uses the app's own font file (assets/fonts/pixel.ttf = Galmuri11, OFL) and our own pixel art. No ROM graphics are copied or decoded.

**Flow, once Java has armed the band:**
1. Character, style and card screens run as before; the auto-pick work is a separate task.
2. The hub skips the prologue with A pulses, only while 0x57CB == 0.
3. On the first intro frame it checks P2 against the opponent the band was made for. If it differs, it gives up (status 6) and the game plays normally.
4. It draws the band and keeps it there for `hold` frames, blocking the player's A, B and OPTION.
5. It presses A, retrying every 24 frames up to 3 times, which starts the banner.
6. By default (flags 0) it removes the band when the banner starts. The game blanks the screen for about 8 frames at that point, so the removal can't be seen. With flags 1 the band stays through the banner and is re-drawn after the game's 0x1E01 rewrite, but runahead then shows a 3-frame blink (measured).
7. At MODE 241 everything is restored and the HUD takes the band's place.

**Recommended Java flow:** short search overlay → skip the Java «상대 발견!» card (or flash it for about 0.5 s) → in-game VS → fight.

**Safety:**
- The band is only drawn when all 80 band cells are game blanks.
- Our tiles use 0x0D0–0x105 first (54), then 0x0B6–0x0CF (26). Both were free in all 243 intros, including companion-vs-companion ones.
- Every frame it checks that our tiles weren't rewritten and that no visible sprite points at them; if either happens it withdraws the band and puts the original tiles back.
- This was proven on a live run: an earlier overflow range, 0x0A2–0x0BB, collided with Galford vs Nakoruru/Galford; the band withdrew cleanly and the match was unaffected. That is why the range moved.

**Alternatives evaluated:**
- (b) Building our own VS from the game's portrait graphics: rejected. The faces only exist once the fight starts, and the select-screen preview only shows the character under the cursor.
- (c) A Java overlay in the game's style: keep as a fallback only, shown when status stays at phase 3 without the 0x10 flag for more than about 10 frames (an unknown ROM layout).

## native_api
C side (prototype file `/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/src/league.c`):

- **`int league_hub_vs(const uint8_t *tiles, int n, const uint16_t *map, int hold, int flags)`** (league.c:999)
  - `tiles` = n×16 bytes of NGPC 2bpp, n ≤ 80.
  - `map` = 80 cells, row-major: 0xFFFF keeps the game's cell, otherwise (palette<<9) | index.
  - `hold` = how many taunt-phase frames before the hub presses A; −1 leaves the game's natural length.
  - `flags` 1 = keep the band through the banner.
  - Call it after `league_hub_match`; it records the opponent it was made for. Ranked hub only (kind 0). A NULL `tiles` turns it off (removed on the next real frame).
  - It is refused while a band is on screen.
  - It survives `league_hub_return(−4)`, so a rematch can arm it either before or after the queued return. It is cleared by −3, −1, −2, cancel, a new hub, or reaching round 1.
- **`void league_hub_vs_status(int v[3])`**
  - v0 = phase (0 off, 1 armed, 2 skipping the prologue, 3 band showing, 4 banner, 5 done, 6 fail), plus 0x10 while the band is drawn and 0x20 if it gave up over a tile clash.
  - v1 = taunt-phase frames so far; v2 = hold.
  - `league_hub_status` stays at 15 entries on purpose. Growing it to 17 overflowed callers with fixed 15-int buffers (u149 t_hub_look.py:45, stage3 t_hub.py): t_hub_look crashed silently, which I caught and fixed.
- **`void league_spr(void *spr)`** — native.c gets one new line after `league_vram(...)`: `league_spr(c_spriteram ? c_spriteram() : NULL);` (needed for the sprite-clash check).
- `vsband.c` / `vsband.h` (new; add `vsband.c` to CMakeLists): set / layout / put / restore / forget / slot.
- `league_hub_before_save` also restores the band, so saved states never contain it.

JNI / Java:
- `Emu.nativeHubVs(byte[] tiles, short[] map, int hold, int flags)` → boolean.
- `Emu.nativeHubVsStatus()` → int[3].
- `RankVs.java` (new) renders the band:
  - `RankVs.render(RankVs.androidInk(hubFont()), RankVs.side("나", sty, me.lp, me.master, me.mr), RankVs.side(nick, null, v.lp, v.master, v.mr))` → `Out{tiles, map}`, or null if it needs more than 80 tiles.
  - Constants: `HOLD` = 180, `FLAGS` = 0.
- `EmuActivity.rankVsArm(p)` is called after `nativeHubMatch(..., true)` in `rankGo`, and before `hubReturn(-4)` in `rankRematch`. During placement matches, my tier shows «배치 n/5».
- The renderer was tested on the JVM through an AWT font adapter (`RankVsMain`). Its output was fed to the real core and stamped correctly on KO, KO101 and JUE.

## timings
VERIFIED, in real frames at 60 Hz:

| Step | Frames |
|---|---|
| go → character select | 15 |
| card confirm → round 1 | 64 (prologue skip) + hold + 195–214 (banner) + 2 |
| hold 180 | 520 total (8.7 s); band visible from intro frame ~4 to 180 (~2.9 s) |
| hold 150 | 490 (8.2 s) |
| hold 120 | 460 (7.7 s) |
| hold 60 | 400 (6.7 s) |
| hold −1 (natural taunt phase) | e.g. 648 (10.8 s), H1 ROM, Galford |
| today, idle player (prologue 1760 + taunt 300 + banner 214) | 2586 (43 s) |

- With flags 1 the band stays about another 3.5 s through the banner (minus a 3-frame blink); with the default flags 0 it disappears inside the game's own 8-frame blank.
- To let the taunt finish typing, use hold ≥ ~240 (its first character appears 70–186 frames in). 180 is the "~3 s VS" compromise.
- The prologue skip presses A for 4 frames every 40 frames while 0x57CB == 0, and stops once the skip takes effect (at +47). A press landing on the intro's first frame would end the taunt phase immediately (seen in probe2).
- The hold A retries every 24 frames, at most 3 times.

## risks
[
 "Tile clash: our tiles sit at 0x0D0–0x105, then 0x0B6–0x0CF. Fighter sprites stay ≤0x09C and companions reach 0x0AA in all 243 intros (14 player characters × 15 opponents, Korean ROM, plus 15 on JUE; mostly player style 수라). Other styles or unseen animations could reach further. If so, the per-frame tile and sprite check withdraws the band and puts the original tiles back (status 0x20), and the match carries on. This is proven by the earlier 0x0A2 range clashing on Galford vs Nakoruru/Galford. At worst there could be a 1–3 frame glitch on the clashing sprite before it withdraws (inferred).",
 "Intro detection must use R_SCR ≥ 8, because the value is 8/10/12/14 depending on companions. My first version used 8/10, missed 9 companion-vs-companion intros in the survey, and that polluted the tile data until I fixed and re-measured. The same blind spot exists in practice mode's story skip (league.c:595), which is existing behaviour and untouched.",
 "Runahead: if flags 1 keeps the band through the banner, it blinks off for 3 displayed frames after the game rewrites the band as 0x1E01 (measured). The default flags 0 avoids this.",
 "Taunt line: it is game text — Korean patch text on the Korean ROMs, Japanese/English on JUE/ORIG — next to our Korean band. With hold 180, long taunts are cut while typing (e.g. Haohmaru's starts at frame 186).",
 "ROM variants: tested KO bundled, KO101, H1, H1 + KO bundled, original, and JUE; all pass the same 19 checks. On an unknown ROM where the band cells aren't 0x001, nothing is drawn: phase 3 without the 0x10 flag, which Java can use to show a fallback overlay.",
 "Diff base: it applies cleanly to w149/int HEAD 4bced84. The w149/int working tree has another worker's uncommitted league.c/look.c/EmuActivity changes; the diff applies there with fuzz (0 failed hunks) and builds, but should be re-checked after their commit.",
 "The player's A, B and OPTION are swallowed from the prologue until the banner. Pausing or leaving through the app still works. If the hub is switched off (league_hub(0)) while the band is up, the band is forgotten rather than restored; this only happens when the session is being torn down.",
 "Not covered: a real device or emulator, 120 Hz double output (the hub runs on real frames only, the same as the existing code), resuming from a checkpoint mid-intro (no band; the game plays normally), and Galford as the player's character for the prologue/rematch edge tests (only t_vs15 used him). t_practice was only re-run on an earlier build of this prototype; the VS code only runs in the ranked hub (kind 0)."
]

## artifacts
[
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/vs_prototype.diff",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/src/vsband.c",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/src/vsband.h",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/src/league.c",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/src/league.h",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/java/RankVs.java",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/java/RankVsMain.java",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/jtree/java/com/dudu/pocketcore/EmuActivity.java",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/run_vs_tests.sh",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/tests/t_vs.py",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/tests/t_vs2.py",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/tests/t_vs15.py",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/tests/t_vsband_unit.py",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/tests/vs_common.py",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/tests/vsband_render.py",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/tests/survey.py",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/out_final_run2.log",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/shots/MOCKUP_vs_flow.png",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/shots/vs15_galford_final_sheet.png",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/shots/vs_ko_seq.png",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/shots/band_tiers_preview.png",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/shots/ko_seq_sheet.png",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/shots/ko_banner_sheet.png",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/shots/ko_ch2_sheet.png",
 "/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/u153/vsgame/shots/fight_hud.png"
]

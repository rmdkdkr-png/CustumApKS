# 컬러(COLOR) — 모든 모드 컬러 · 16가지 + 내 색 · 컬러 만들기 — 바꾼 것

가지 `impl/color` (기준 `feat/framegen-art` 7a851e6). 설계: `scratchpad/next/color/design.md`(시제품 `proto/`·시험 `tests/`).
커밋: `7f45180`(native) · `f572788`(앱) · `968ea51`(고침 둘) — 이 문서는 시험 폴더에만(커밋 안 함).

## 한 줄

1인 대전·무한 대전·연습 대전·리그 대전 어디서나 캐릭터·검질 고르기에서 **OPTION = 다음 컬러**(길게 = **컬러 만들기**), 캐릭터 고르기에서
**B = 2P색으로 결정**(그 판만), 오른쪽 세로 이름 칸 = 컬러 이름, 가운데 미리보기 = 그 색. 컬러 16가지 + 캐릭터마다 내 색 2칸, 캐릭터마다 기억. 〔177 정리: 175부터 B 도 보통 색으로 결정 — «B = 2P색» 없앰(166-4). 2P색은 거울전에 게임이 상대에 쓰는 색 · 상대 컬러 거울 대신 색으로만〕

## 바꾼 파일

### native (`app/src/main/cpp`)

| 파일 | 내용 |
|---|---|
| `look.c` · `look.h` (새) | 모든 모드 컬러. 시제품 `proto/look.c` 를 바탕으로, 아래 «시제품과 다른 점». JNI(`Emu.nativeLook*`)도 여기(JNI() 매크로) |
| `look_tab.h` (새, 생성물) | `LOOK_TAB[15][2][16][3]` · `LOOK_DUP[15][2]` · `LOOK_NAME[18]` — `look_gen.py`(이 폴더) 가 `colorgen.py` 의 `FINAL` 로 만든다. 시제품 표와 바이트까지 같음(주석 한 줄만 다름) |
| `vpanel.c` · `vpanel.h` (새) | 오른쪽 세로 칸의 주인 하나(league.c 의 vp_layout·vp_put·vp_restore + menu_kind 를 옮김, 동작 같음) |
| `hub_glyphs.h` (다시 만듦) | `HUB_VLAB` 에서 컬러 글자 넷을 빼고 `HUB_VLAB_N = 9`(배경 8 + 무작위), 컬러 18개는 `LOOK_VLAB`(`#ifdef HUB_WANT_LOOK` — look.c 만 받음). 생성기 = 이 폴더의 `hub_glyphs.py`(handoff/ss2_league/stage3/hub_glyphs.py 를 늘린 사본). 기존 글자(HUB_MENU_RIGEU·HUB_HDR_*·배경 9개)는 바이트까지 그대로, LOOK_VLAB 는 시제품 `look_glyphs.h`·`look_vlab.json` 과 바이트까지 같음 |
| `league.c` · `league.h` | 컬러 코드(PAL1·gen_color·look_targets·look_apply·look_preview·g_palremap·pr_*·H_PICK_ME 의 OPTION/B/미리보기/세로 칸·nav 4) 삭제 → look 에 넘김. `league_vram` → `look_vram`, `league_palremap_fn` → `look_palremap_fn`, `league_look(stage, color)` → 배경 + `look_set_match(color)`, `league_hub_status` v[10] = `look_cur()`, 새 `league_hub_owns_select()`. 세로 칸은 vpanel 로. **H·L 의 컬러 칸(H.color·H.vp_on·H.vp_orig·L.color·look_color)은 지우지 않음** — `.prac` 덩어리가 sizeof H·L 그대로라(크기 안 바뀜 → t_dual 의 636/496 상수 그대로 통과). `& 3` 세 곳은 지운 코드와 함께 없어짐 |
| `native.c` | 입력 콜백 `| look_in_block` · `| look_in_or`; 진짜 프레임에서 `league_tick_hub` 다음 `look_tick(…, league_hub_owns_select() ? BUSY : FREE)`; 코어 올림/내림 `look_enable(0); look_forget()`; 리셋·연습 나가기 리셋·리그 돌려보냄·상태 불러오기에서 `look_forget()`; 상태 저장 직전 `look_before_save()`; 상태 옆 `<경로>.look`("LOK1" · 상태 크기 · FNV-1a · 16바이트 덩어리, 경기 컬러 없으면 지움, 불러올 때 크기·지문 맞아야 `look_resume`) |
| `CMakeLists.txt` | `look.c vpanel.c` 더함 |

### 앱 (`app/src/main/java/com/dudu/pocketcore`)

| 파일 | 내용 |
|---|---|
| `Look.java` (새) | 이름 18개 · `name(idx, cv)`(cv 없는 옛 기록 = «컬러 3·4») · 앱 설정 키 `pocketcore_ss2_look`(켬/끔)·`pocketcore_ss2_look_mem`("0,1,…" 16칸)·`pocketcore_ss2_look_cus`(JSON `{"v":1,"c":{"11":[[3039,744,65],null]}}`) · `migrate()`(처음 한 번 옛 리그 `pref.color` 0~3 → 16칸 모두 그 값, 리그 기록 파일이 있을 때만 읽음 — 리그 안 써 본 사람에게 파일을 안 만든다) · `push()` |
| `LookEditor.java` (새) | «컬러 만들기 — 우쿄» 창(코드로 만든 뷰, 픽셀 글꼴). 처음 색 ◀▶ · 밝은 색/옷 색/테 색 견본(누르면 그 색) · 빨강·초록·파랑 0~15 막대 + −/+ · «세 색이 너무 비슷해요» · «내 색 1에 저장»·«내 색 2에 저장»·«취소» |
| `EmuActivity.java` | `lookSetup()`(loadCore 끝 — practiceSetup 바로 뒤) · `lookPoll`(200ms) · `openLookEditor`/`lookEditorClose` · 뒤로 = 창 취소 · 멈춤 메뉴 `ACT_LOOK` · `onPause` 기억 저장 · 띠 안내(아래) · 리그: `hubStart` 는 배경만, `hubTick` 은 `setPrefStage` + 기록에 tri, `leagueStart` 새 경기 컬러 −1, 체크포인트 tmp 옆 `.look` 지움 · `myPickKeys` 는 컬러가 꺼진 판이면 «A 결정» 만 |
| `PadView.java` | 멈춤 메뉴 끝 칸 «컬러 만들기»(`ACT_LOOK`, `setLookCell` — 고르기 화면일 때만). 누르면 바를 닫는다(게임이 돌아야 미리보기가 그려짐). 리스너가 칸을 바꿔도 안전하게 act 를 먼저 잡음 |
| `Settings.java` | «컬러 고르기»(`Look.K_ON`, 기본 켬, `.g("ss2").l()`) — «리그·연습» 바로 위 |
| `League.java` | `COLORS = Look.NAMES`(18) · `prefColor()` 범위 넓힘(옛 값만 읽음 — Look.migrate) · 새 `setPrefStage(stage)` · `setLook(id, stage, color, tri)` → `{"stage","color","cv":2,"tri"(내 색일 때만)}` (3인자 판은 그대로 둠 — RANKED 쪽 호출과 겹치지 않게) · `setPrefLook` 은 남김(JVM 시험·호환) |
| `LeagueActivity.java` | 상대 상세 안내 «… (상대 선택에서 OPTION) · 컬러는 캐릭터마다 — 고르기 화면에서 OPTION» |
| `Emu.java` | `nativeLookEnable/SetMem/GetMem/SetCustom/SetMatch/Edit/Status/Triples` |

## 시제품과 다른 점(결정)

1. **내 색은 캐릭터마다 하나(두 검질 같이)** — 시제품은 `cus[14][2][2][3]`(검질마다) + 검질 인자였지만, 설계 4-가·5-가와 제품 결정(«custom shared by both styles»)대로 native 를 `cus[14][2][3]` 로.
   그래서 API 가 `look_set_custom(ch, k, c1, c2, c3)` · `look_edit(on, c1, c2, c3)`(검질 인자 없음), JNI `nativeLookSetCustom(ch, k, …)` · `nativeLookEdit(on, …)`.
2. `look_status` 14칸(시제품 12) — v[12] = 만들 수 있는 캐릭터(쥔 고르기 화면 캐릭터, 쿠로코·무작위 칸이면 −1) · v[13] = 미리보기 검질(만들기 창의 시작 색 표). `look_triples()` 를 C 함수로 꺼냄(시험이 봄).
3. OPTION 길게 요청은 **기억 칸이 그 캐릭터일 때만**(무작위로 고른 검질 고르기·쿠로코 제외 — 내 색은 캐릭터마다라).
4. OPTION 누름은 **고르기 화면을 쥔 채 시작한 것만** 센다(밖에서 누른 채 들어와 뗀 것·우연히 40프레임째가 맞는 것으로 바뀌거나 창이 뜨지 않게).
5. 미리보기 «우리 색» 알아보기에 **마지막으로 쓴 세 색(pv_last)** 을 더함 — 만들기 창에서 색을 바꾸거나 창을 닫을 때 그 색은 표에 없어서 시제품은 미리보기가 옛 색에 남았다(새 시험 t_look2 에서 찾음).
6. 설계 위험 6 대로 B 2P색 대신 누르기 8프레임 동안 **십자도 막음**.
7. 표의 «기본 → 같은 색» 칸은 안 넣음(내 색이 기본과 같을 때 등 — 쓸모없는 표 칸).
8. `look_before_save` 는 검질을 «전투 중이면 P1 블록, 아니면 검질 커서 0x574C» 로 정하고, 그 검질 색이 아니면 다른 검질도 본다(이야기 화면 동안 P1 블록이 옛 값이라 — 설계 2-라의 뜻 그대로, 조건만 단단히).
9. 경기 기록의 내 색 세 색(tri)은 기록에만 남기고, 체크포인트 이어 하기는 그때 앱에 있는 내 색을 쓴다(덩어리·look_set_match 는 번호만).
10. 만들기 창 모양: 설계는 «세 줄 × 막대 셋»(막대 아홉 개)이지만 덮개 화면·가로 화면에서 엄지로 쓰기 어려워 «견본 셋(고르면 그 색) + 막대 셋(−/+)» 으로. 글·단추 이름은 설계 7장 그대로.
11. 생성기는 handoff 대신 이 폴더에 둠(`look_gen.py` · `colorgen.py` · `hub_glyphs.py`) — 저장소(handoff)는 건드리지 말라는 지시. 글자는 `look_gen.py` 가 아니라 제품 결정대로 `hub_glyphs.py` 가 만든다.
12. `look_enable(0)`·`look_forget()` 에서 보이는 컬러(cur)도 0 — 허브 상태 v[10] 이 앞 판 컬러를 들고 있다가 «컬러 고르기» 끈 리그 판 기록에 남지 않게(968ea51).
13. 그대로 둔 설계 동작: OPTION 은 «뗄 때» 바뀜(길게 누르기와 가르려고 — 위험 5), 가운데 무작위 칸에서 B = 미리보기는 쿠로코 그대로·세로 칸 «2P색», 경기는 뽑힌 캐릭터의 2P색(0x57D5).

## 띠·멈춤 메뉴

- 띠 안내는 **허브 띠가 없는 화면의 고르기 화면에서만**(일반 1인·무한 대전): 캐릭터 `A 결정  ·  B 2P색  ·  OPTION 컬러` / `OPTION 길게 = 컬러 만들기`, 검질 `A 결정  ·  OPTION 컬러`.
  연습 판(허브가 타이틀 상태로 1인·무한 대전 중)은 `practicePoll` 이 그 글을 받아 보이고(한 줄 훅), «리그·연습» 이 꺼진 판은 `lookTick` 이 띠를 직접 만든다. 리그 판·리그 화면 경기의 띠는 안 바꿈(내 캐릭터 단계는 원래 `myPickKeys`).
- 멈춤 메뉴(위 바)의 «컬러 만들기» 칸은 고르기 화면을 컬러 쪽이 쥐었을 때만(리그·연습 포함). 바를 닫고 창을 연다.

## 시험 (이 폴더)

준비: `source env.sh`(LEAGUE_HOST_SO=host.so · 코어 89860fe · PYTHONPATH). host.so = `gcc -O2 -Wall -shared -fPIC -I…/host/inc -o host.so league.c practice.c look.c vpanel.c -lm`(경고 0).
NDK clang `-Wall -fsyntax-only`(compile_commands 그대로) native.c·league.c·look.c·vpanel.c 경고 0.

### 필수 회귀(마지막 코드 = 커밋 968ea51 의 host.so, md5 f12212b8…)

| 시험 | 조건 | 결과 | 파일 |
|---|---|---|---|
| `stage1/tests/t_practice.py` | 동봉 한글판 · FIXT=1791974914(ftenv.so) · 원본 하네스 | **68/68 ALL PASS** | `final_t_practice_914.txt` (앞 판 `reg_practice_914.txt` 68/68) |
| `stage1/tests/t_fix1.py` | 〃 | **7/7 ALL PASS** | `final_t_fix1_914.txt` (앞 판 `reg_fix1_914.txt` 7/7) |
| `stage1/tests/t_resume.py` | 〃 | **12/12 ALL PASS** | `final_t_resume_914.txt` (앞 판 `reg_resume_914.txt` 12/12) |
| `stage3/tests/t_hub.py` → 사본 `t_hub_look.py` | 동봉 한글판 · 시계 고정 없음 · 하네스에 look_tick(아래 «통합할 때») | **28/28 ALL PASS** | `final_t_hub_look.txt` (앞 판 `reg_hub_look.txt` 28/28) |
| `stage2/tests/t_dual.py` | 동봉 한글판 · 시계 고정 없음 · 원본 그대로 | **31 PASS · fails=0** | `final_t_dual.txt` (앞 판 `reg_dual.txt` 31 · fails=0) |
| 원본 `t_hub.py`(참고) | 원본 하네스(look_tick 없음) | 컬러 항목부터 실패 — 기대한 것(잘라 멈춤) | `reg_hub_orig.txt` |

### 새 시험 · 롬 판

| 시험 | 무엇 | 동봉 한글(앱 설정: 런어헤드 2·프레임 생성) | 동봉 한글 fast | 한글 v1.01 fast | h1 한글 fast | 순정 JUE fast |
|---|---|---|---|---|---|---|
| `t_look.py`(시제품 시험, 하네스만 14칸) | 1인 대전 OPTION·B·미리보기·세로 칸·기억·검질 고르기·경기 색·원래 색 0프레임·.look·이어하기 화면·인트로/데모·무한 대전·무작위 칸·미러전 | 27/27 | 27/27 | 27/27 | 27/27 | 27/27 |
| `t_look_hub.py`(시제품 시험) | 연습·리그 상대 선택은 안 쥠(OPTION = 스테이지) · 내 캐릭터에서 쥠 · 연습/리그 경기 색 · 체크포인트 이어 하기(league_look) | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 |
| `t_look2.py`(새로 — 설계 9-나) | 내 색 한 바퀴·안 만든 칸 건너뜀·look_triples·OPTION 길게 = 요청(컬러 그대로)·만들기 창 입력 전부 막음·창에서 색 바꿈·창 닫으면 원래·검질 고르기 내 색(두 검질 같이)·내 색 경기 원래 색 0프레임·쿠로코/무작위는 만들기 없음·겹침 건너뛰기(아수라 수라 먹빛·나찰 보라)·고르기 화면 저장→불러오기·꺼짐 = 세로 칸 되돌림·옛 코어 INFO | 28/28 | 28/28 | 28/28 | 28/28 | 28/28 |
| `t_hub_look.py` | 위 «필수» 의 사본 — 이 시험은 늘 런어헤드 2·프레임 생성(fast 없음) | 28/28 | — | — | 28/28 | 28/28 |

옛 코어(palremap 없음, 하네스에서 `prf = None`) INFO: 경기 1500프레임 중 화면에 원래 색이 그려진 프레임 46(1초에 한 번꼴, 프레임 뒤 고쳐 쓰기만) · 지금 코어 0.
(동봉 한글 앱 설정·v1.01·h1 의 t_look/t_look_hub/t_look2 와 «컬러 켬 회귀»는 cur = 0 고침(968ea51) 바로 앞 판 host.so 로, JUE·동봉 fast·t_hub_look h1/JUE·필수 회귀는 마지막 판으로 돌았다 — 차이는 look_enable(0)/look_forget 에서 cur 를 0 으로 하는 한 줄.)

### 컬러 켬 회귀(추가 — 기존 시험을 look 이 켜진 하네스 `lookph/ph.py` 로)

| 시험 | 결과 | 파일 |
|---|---|---|
| t_practice(FIXT) | 68/68 ALL PASS | `lookon_t_practice_914.txt` |
| t_fix1(FIXT) | 7/7 | `lookon_t_fix1_914.txt` |
| t_resume(FIXT) | 12/12 | `lookon_t_resume_914.txt` |
| t_dual | 31 · fails=0 | `lookon_t_dual.txt` |

스크립트 폴더가 sys.path 맨 앞이라 t_practice·t_fix1·t_resume 는 `lookph/` 에 내용 그대로 복사한 것을 돌렸다(그래야 lookph/ph.py 가 잡힘).

### JVM(`jvm/run_jvm.sh` — 앱 League.java·Look.java 그대로 + 스텁 MainActivity·Settings·Emu·Log)

| 시험 | 결과 |
|---|---|
| `jvm/LeagueTest.java`(stage3 사본 — «컬러 4개» 검사만 18개로) main | 65/65 ALL PASS (`jvm/res_jvm_main.txt`) |
| 〃 migrate | 13/13 ALL PASS (`jvm/res_jvm_migrate.txt`) |
| `jvm/LookTest.java`(새로) | 28/28 ALL PASS (`jvm/res_jvm_look.txt`) — 옛 기록 이름·기억 글자 왕복·옛 pref.color 옮기기(리그 파일 없으면 안 만듦·한 번만)·setPrefStage·prefColor 넓힘·내 색 JSON 왕복/자름/지움·push·argb·tooClose·경기 기록 look.cv/tri |

### 안드로이드 빌드

`gradle :app:assembleDebug -PpcSuffix=.fgtest "-PpcLabel=Legacito 시험"` BUILD SUCCESSFUL(`gradle6.txt`, C/C++ 경고 없음).

## 통합할 때 알 것

- **t_hub.py 는 사본(`t_hub_look.py`)으로**: 원본 하네스는 `league_tick_hub` 만 부르는데 컬러가 look 으로 옮겨 가 원본은 컬러 항목(옵션 2P색·미리보기·B 2P색 결정)에서 실패하고 그 뒤 흐름도 엉킨다(`reg_hub_orig.txt` — 기대한 실패, 잘라 멈춤). 사본은 시제품 `t_hub_look.py` 그대로 = 원본 28항목 + 하네스에 `look_tick`·look 입력 비트(앱 native.c 순서)·`look_enable(1)`. 검사 글 «컬러 2: 만든 색» 은 이제 «쪽빛»(가장 밝은 색 그대로라 같은 조건으로 통과).
- `t_practice`·`t_fix1`·`t_resume`·`t_dual` 은 원본 그대로 통과(원본 하네스는 look 을 안 켬 = 컬러 꺼짐). 같은 넷을 **컬러가 켜진 하네스(`lookph/ph.py`)** 로도 돌렸다(아래 «컬러 켬 회귀»).
- 구조체 크기: H·L 그대로(.prac 호환). look 상태는 따로 `.look`(새 파일 — 옛 앱은 무시).
- `league.c` 에서 고친 곳: 파일 맨 위 include 2줄, L·H 의 컬러 칸 주석, 컬러 블록 삭제, `league_vram`/`league_palremap_fn` 한 줄씩, 세로 칸 함수 셋 → 두 줄 래퍼, `nav == 4` 갈래 삭제, H_PICK_ME 컬러 블록 삭제(주석 한 줄), `league_hub`·`pr_apply`·`league_practice_hub` 의 `pr_init = 0` 삭제, `league_hub_look`(color 안 씀)·`league_look`(→ look_set_match)·`league_hub_status` v[10], `pr_update` 삭제, `league_tick_hub` 의 pr_update·look_apply 줄 삭제, 끝에 `league_hub_owns_select()`. 허브 상태 기계·상대 선택·배경 고르기는 손대지 않음(RANKED).
- RANKED 의 `hub_go_fixed`(재대결 길 일반화)도 `nav = 1` 로 H_PICK_ME 에 들어가면 look 은 바쁨 → 캐릭터 고르기에 닿아 nav 가 끝나면 쥔다(별도 할 일 없음). `look_color` 대신 `look_set_match` 를 쓰면 된다.
- EmuActivity 의 겹칠 만한 곳: `hubStart` 2줄, `hubTick` 컬러 4줄, 경기 만들 때 `setLook` 1줄, `leagueStart` 컬러 3줄, `practicePoll` 1줄, `myPickKeys` 1줄, `loadCore` 1줄, `handleAction`·`onBackPressed`·`onPause` 각 1~3줄 — 나머지는 파일 끝 «모든 모드 컬러» 블록.
- 생성기: 표 `python3 look_gen.py <앱>/app/src/main/cpp`, 글자 `python3 hub_glyphs.py <앱>/app/src/main/cpp/hub_glyphs.h glyphs.json <앱>/app/src/main/assets/fonts/pixel.ttf`(Pillow).
- 기기 시험(설계 9-나 마지막 줄)은 안 했다(지시대로 adb·에뮬레이터 안 씀) — 고르기 화면 OPTION·B·띠·세로 칸, OPTION 길게 → 창 → 막대 → 미리보기 바로 바뀜 → 저장 → 경기, 앱을 다시 켜도 기억, 멈춤 메뉴 칸, 리그 결과·기록을 기기에서 봐 줄 것.

## 폴더 안내

- `work_*`(시험 작업 폴더)에는 롬에서 나온 상태 파일·찍은 화면(png)이 있다 — scratch 에만 두고 어디에도 올리지 말 것.
- `chainA~D.sh·chainF.sh` = 위 시험을 돌린 순서(동시에 python 셋 이하). `env.sh` = 환경. `lh.py`·`cx.py` = 시제품 하네스(lh 는 look_status 14칸 등만 고침).
- `hub_glyphs.orig.h` = 다시 만들기 전 앱 hub_glyphs.h(비교용), `glyphs.json` = hub_glyphs.py 둘째 출력.

## 남은 것·알려진 틈

- 실기(안드로이드)에서 «컬러 만들기» 창의 모양·크기(특히 가로 화면 — 게임 그림 오른쪽, 덮개 화면)를 아직 못 봄.
- 경기 기록의 컬러 이름을 보여 주는 화면은 아직 없음(`Look.name(idx, cv)` 는 준비됨 — 결과 카드는 RANKED 쪽이라 안 건드림).
- 랭크/허브 «타이틀 상태로 1인 대전» 을 하는 리그 판의 띠는 원래대로 «리그 대전 — 메뉴 셋째 줄»(설계: 띠 안내는 일반 판만).
- 리그 체크포인트를 `.tmp` 로 저장했다 이름을 바꾸는 길이라 그 옆 `.look` 은 지운다(컬러는 경기 기록이 정함). 다른 저장(슬롯·오토세이브·옵션 바꾸기)은 `.look` 이 같이 남는다.
- 0x574C(검질 커서)는 설계대로 롬 4판(동봉 한글·v1.01·h1·순정 JUE)에서만 확인 — 롬 6판 전부는 아님.

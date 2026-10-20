# 사쇼2 컬러 — 모든 모드에서 고르기 + 16가지로 늘리기 + 내 색 만들기 (설계)

대상: Legacito `fgint` 7a851e6 · 동봉 코어 ss2-sp-core 89860fe(`retro_ngp_palremap` 있음) · 2026-10-15
요청(묶음 #22 중 둘): «컬러 선택 어느 모드든 되게» · «컬러 추가 확충».
이번 워크플로에 함께 전해진 유저 글 «연습모드는 프레임 발동시간 경직 차 등»은 연습 대전 프레임 데이터 이야기라 이 문서 범위가 아니다(같은 묶음의 다른 갈래).

작업 폴더(모두 scratch, 저장소는 안 건드림): `/tmp/claude-0/-home-user-CustumApKS/e6c46352-6bb9-5a9d-8b3a-f2da7447674e/scratchpad/next/color/`
— 아래에서 `<C>` 로 줄여 쓴다. 롬에서 나온 그림(찍은 화면·대조표)은 모두 `<C>` 안에만 있다.

---

## 0. 한눈에

- **모든 모드에서 된다.** 컬러 코드를 리그 허브(`league.c`)에서 떼어 새 모듈 `look.c` 로 옮긴다. look 은 허브와 상관없이 매 프레임 돈다.
  1인 대전·무한 대전(허브 없음), 연습 대전·리그 대전(허브의 «내 캐릭터» 단계)에서 똑같이:
  캐릭터·검질 고르기에서 **OPTION = 다음 컬러**, 캐릭터 고르기에서 **B = 2P색으로 결정**, 오른쪽 세로 이름 칸 = **컬러 이름**, 가운데 미리보기 그림이 바로 그 색. 〔177 정리: 175부터 B 도 보통 색으로 결정 — «B = 2P색» 없앰(166-4). 2P색은 거울전에 게임이 상대에 쓰는 색 · 상대 컬러 거울 대신 색으로만〕
  경기(이야기·라운드 사이·이어하기 화면 포함) 내내 P1 몸이 그 색이다.
- **허브가 고르기 화면 입력을 쓰는 동안엔 손대지 않는다.** 연습·리그의 «상대 선택»(OPTION = 스테이지, A/B = 고르기)과 허브의 대신 누르기 동안 look 은 «바쁨»을 받고 아무것도 안 한다.
- **컬러 16가지 + 내 색 2개.** 기본 · 2P색 · 쪽빛 · 비취 · 보라 · 다홍 · 분홍 · 먹빛 · 흰옷 · 황금 · 은빛 · 청동 · 흑백 · 그림자 · 핏빛 · 유령 · 내 색 1 · 내 색 2.
  26개 후보를 14명 × 2검질 × 여러 배경 경기 화면으로 찍어 보고 10개를 뺐다(5장). 표는 생성기가 한 번 계산해 C 표로 박는다(`look_tab.h`).
- **캐릭터마다 기억.** 마지막에 고른 컬러를 캐릭터마다 기억한다(스파6·길티기어식). B(2P색)는 그 판만.
- **내 색 만들기.** 고르기 화면에서 OPTION 길게(0.7초) → 앱 창에서 세 색(밝은 색·옷 색·테 색)을 12비트(0x0BGR, 채널 0~15)로 고른다. 게임 화면의 미리보기 그림이 바로 바뀐다. 캐릭터마다 2칸.
- **시제품을 실제 코어 위에서 돌려 봤다.** `look.c`·`vpanel.c` 시제품 + 고친 `league.c` 사본으로 호스트 시험 4종 —
  새 `t_look.py` 27항목 × 롬 4판 통과(앱과 같은 런어헤드 2·프레임 생성 판도 27/27, 두 라운드 + 사이 연출 내내 원래 색 프레임 0),
  새 `t_look_hub.py` 12항목 × 롬 4판 통과, 기존 `t_hub.py`(28항목, 하네스에 look 만 더함) 롬 3판 ALL PASS, 기존 `t_dual.py` 31항목 fails=0, 기존 `t_practice.py`(시계 1791974914) 회귀 없음.

---

## 1. 실측 — 이번에 잰 것과 확인한 것

도구: `ss2probe`/`ph.PH` 하네스 + 실제 코어 `core_89860fe.so`. 스크립트는 `<C>/exp*.py`, 공용 함수 `<C>/cx.py`.

### 1-가. 주소

| 주소 | 뜻 | 근거 |
|---|---|---|
| 0x40A7 | MODE — 240 메뉴·연출 · 241 전투측 | [0단계] |
| 0x41C0 | SCR — 메뉴일 때 0 타이틀 · 2 캐릭터 · 4 검질 · 6 카드 · 8 라운드 소개 · 10 판 사이. **이어하기 화면도 MODE 240 · SCR 2** 이고, 이어하기 A 뒤 SCR 0 이 8프레임 섰다가 캐릭터 고르기(SCR 2)로 간다. 인트로·데모도 SCR 2·4·6 을 지난다 | exp7·exp8·exp9 |
| 0x4E3C | 캐릭터 고르기 커서 = 캐릭터 × 4 (가운데 무작위 칸 = 60 = 15 × 4, 게임 속 이름 «쿠로코»). **무작위 칸으로 결정하면 검질 고르기 동안 이 값이 뽑기처럼 돌다가 실제 캐릭터에서 멈춘다**(예: 60 → 28 → 20, 0x57D5 = 5 와 같음) | exp10·dbg3 |
| **0x574C** | **검질 고르기 커서 0 수라 · 1 나찰** — 확정 뒤에도 남는다. 16KB 중 미리보기 팔레트의 검질과 늘 같은 바이트는 이것 하나(4명 × 8번 누름). 검질 고르기에서 ← = 수라 · → = 나찰(토글 아님) | exp13 |
| 0x57D5 | P1 캐릭터 — 검질 확정 뒤 약 160프레임에 씀(그 전 255, 새 판 전원 뒤). 무작위 칸도 실제로 뽑힌 캐릭터. 다음 판에서 다시 쓸 때까지 옛 값이 남는다 | exp11·exp12 |
| 0x57D7 | 검질이 **아니다**(처음부터 1인 경우가 있음 — 반박) | exp12 |
| 0x5B51 / 0x5D51 | P1·P2 블록 (캐릭터<<4 \| 검질<<3 \| 미러 +0x04) — 전투 로드 때 선다(이야기 화면 동안은 옛 값) | [0단계] · exp11 |
| 0x624B | 타이틀 메뉴 커서(0 1인 · 1 무한 · 2 셋째 줄) | [3단계] |

### 1-나. 고르기 화면에서 B·OPTION

- 1인 대전·무한 대전 캐릭터 고르기에서 B·OPTION 을 눌러도 화면·커서·SCR 이 그대로이고, 램이 바뀌는 곳은 0x70xx~0x76xx(스택)뿐이다 — 게임은 두 버튼을 안 쓴다(exp1·exp4, [3단계]와 같음).
- 검질 고르기에서 B = 캐릭터 고르기로 뒤로(게임). 이어하기 화면에서 A = 이어하기, OPTION·B 는 아무 일 없음(카운트가 끝나면 타이틀).
- **함정(시제품에서 찾음):** 검질 고르기에서 «뒤로»로 쓴 B 는 **같은 프레임에** 캐릭터 고르기로 넘어온다. 프레임 뒤에서 «캐릭터 고르기 + B 눌림 시작»만 보면 이것을 «2P색으로 결정»으로 또 잡아 A 를 대신 눌러 버린다.
  → 지난 프레임에도 캐릭터 고르기를 쥐고 있었을 때만 B 를 받는다(`was2`, 4-다).

### 1-다. 스프라이트 팔레트 — 누가 무엇을 쓰나

팔레트 0 의 색 1~3 을 초록, 팔레트 5 를 자주로 바꿔 놓고(코어 바꿔 쓰기) 기술 6개를 쓰며 48프레임씩 찍었다(하오마루·나코루루·갈포드·우쿄, `exp3.py` → `<C>/work/e3_moves_*.png`).

| 팔레트 | 쓰는 것 |
|---|---|
| **0** | **P1 몸만.** 고르기 화면 미리보기 그림(스프라이트 24개)·라운드 소개(«자아 당당히»)·경기·승리 포즈·판 사이·이어하기 화면의 쓰러진 P1 도 모두 이 팔레트·같은 기본 색(exp6·exp7). 회오리·«風» 글자·칼 궤적·불꽃·맞은 불똥은 다른 팔레트 |
| 5 | P2 몸 (미러전이면 게임이 2P색으로) |
| 3 · 4 | 짐승 짝꿍 — 나코루루 매 = 4, 리무루루 콘루 = 3 (게임 2P색에서도 안 바뀜 → 우리도 안 건드린다) |
| 15 | 고르기 화면 커서 |
| 7·8·9·10·11·12 | 기술 이펙트·그림자 등 |

- 인트로·데모 9000프레임 동안 MODE 241(전투)은 한 번도 없었다. 인트로가 팔레트 0 에 캐릭터(아수라·겐쥬로)를 그리므로, 경기 컬러는 **타이틀 메뉴가 보이면 잊어야** 인트로에 안 샌다.
- 쿠로코(가운데 무작위 칸) 미리보기 팔레트 = EEE/666/000 (PAL1 에 없던 줄).
- 캐릭터 고르기 미리보기 그림은 늘 **수라** 색이다(14명 모두 PAL1[ch][0][0] 와 같음). 검질 고르기는 커서(0x574C) 검질 색.

### 1-라. 코어 팔레트 바꿔 쓰기 (`retro_ngp_palremap`, ss2-sp-core `build/mednafen/ngp/gfx.c` 824~850)

- `retro_ngp_palremap(idx, slot, from, to)` — idx = 16비트 칸 0~255(팔레트 k 의 색 j = k*4 + j, 스프라이트 팔레트 0~15 = 칸 0~63), slot 0·1, from < 0 이면 그 자리 비움, idx < 0 이면 표 전체 비움.
- `ngpgfx_write8` 이 팔레트 램(0x8200~0x83FF)의 **윗바이트**를 쓸 때 `pal_remap` — 그 팔레트의 색 1~3 이 **모두** 같은 자리(slot)의 from 과 같으면 셋 다 to 로. 16비트 쓰기도 아랫바이트 → 윗바이트 순으로 같은 길.
- 한 팔레트에 자리 둘 — 검질 둘(수라·나찰)을 한 번에 걸 수 있다. 세 칸을 함께 보므로 맞을 때 번쩍임·분노처럼 게임이 잠깐 쓴 다른 세 색은 그대로 둔다.
- 표는 상태 저장에 안 들어간다 → 매 프레임 앱이 표를 정한다(지금도 `pr_update`).
- 런어헤드·프레임 생성 프레임까지 같은 결과(코어 안에서 바뀐다). 옛 코어(없음)면 프레임 뒤 고쳐 쓰기만 — 1초에 한 번꼴 1~3프레임 원래 색이 보인다([3단계]).

### 1-마. 지금의 리그 컬러 길(끝에서 끝까지) — 무엇을 옮기나

| 자리 | 지금 | 문제 |
|---|---|---|
| `PAL1[14][2][2][3]` | 캐릭터·검질마다 {기본, 2P색} 세 색(미러전 실측) | 그대로 쓴다(새 표의 0·1번) |
| `gen_color` · `look_targets` | 컬러 2·3 = 기본 색의 색상 +120°/+240°(무채색이면 진홍·청록), 가장 밝은 색은 둠 | 이름이 «컬러 3·4» 뿐이고 캐릭터마다 결과가 들쭉날쭉(5장) |
| `look_preview` | 허브 H_PICK_ME + SCR 2/4 에서, 팔레트 0 이 커서 캐릭터 어느 검질의 컬러 0~3 이면 고른 컬러로 | 허브 안에서만 · 4개만 · 검질 구분을 색으로 함 |
| `look_apply` | 무장(L.armed)·경기 화면에서 P1 기본 색 → 고른 색, 2P색이면 미러전 P2 2P색 → 기본 | P1BLK 로 캐릭터를 봄(이야기 화면에선 옛 값) · 무장한 경기만 |
| `pr_update` · `pr_push` | 코어 표: PR_IDX {1,2,3,21,22,23}(팔레트 0·5 의 색 1~3) × 자리 2 | 그대로 옮긴다(주인 = look) |
| `vp_put(9 + color)` | 세로 칸 글자 HUB_VLAB 9~12(«기본·2P색·컬러3·컬러4», `hub_glyphs.py` VLABELS, 한 글자 16×13px, 칸 18타일) | 글자 18개로 늘리고 look 쪽으로 |
| H_PICK_ME OPTION/B | OPTION → `H.color = (H.color + 1) & 3`, B → `H.color = 1` + `H.nav = 4`(ovr 로 A 4프레임) | `& 3` 세 곳(league.c 603·782·790) |
| Java | `League.COLORS`(4개) · `prefColor()`(리그 세이브 `pref.color`) · `setPrefLook` · 경기 기록 `look.color` · `LeagueActivity` 291 안내 · `myPickKeys` 띠 | 하나의 전역 컬러 · 리그 세이브에만 저장 · 연습은 늘 0 에서 시작(Java 가 안 넣음) |

---

## 2. 설계 (1) — 모든 모드에서 되는 `look.c`

### 2-가. 자리

```
retro_run
 → league_vram(chr, scr, pal)          (league.c 가 look_vram·vpanel_vram 에 넘김)
 → league_palremap_fn(c_palremap)      (league.c 가 look_palremap_fn 에 넘김)
 → league_tick_hub(ram, n, in)         (허브 — 컬러 코드는 빠짐)
 → look_tick(ram, n, in, league_hub_owns_select())     ← 새로
 → practice_vram / practice_tick …
입력 콜백 = ovr ? mask : (in & ~(league_in_block | practice_in_block | look_in_block)) | league_in_or | practice_in_or | look_in_or
```

- look 은 Java 가 켠 판에서만 일한다: 사쇼2 이고 롬 판이 확인된 판(`practiceRomOk()` — League.romLabel 또는 배경음악만 심은 사본) 또는 리그 세션, 그리고 설정 «컬러 고르기»가 켬일 때.
  코어를 올릴 때마다 native.c 가 `look_enable(0)`·`look_forget()` 로 끄고 시작한다(다른 게임 램에 손대지 않게).
- `league_hub_owns_select()` = `H.st == H_PICK_OPP || H.nav != 0 || league_ovr_on` — 허브가 고르기 화면 입력을 쓰는 동안 1(look 은 «바쁨»: 표 비움·칸 안 건드림·입력 안 막음).
  2단계 «도전»(LEAGUE_AUTONAV 로 메뉴 대신 누르기) 중에도 `league_ovr_on` 이라 바쁨, 캐릭터 고르기에 닿으면 look 이 쥔다.

### 2-나. 상태

```c
static struct {
   int on;                          /* Java 가 켬 */
   signed char mem[16];             /* 기억 칸: 0~13 캐릭터 · 14 안 씀(유가) · 15 가운데 무작위 칸 */
   uint16_t cus[14][2][3]; uint8_t cus_ok[14][2];   /* 내 색 1·2 — 캐릭터마다(두 검질 같이) */
   int cur;                         /* 고르기 화면에 보이는 컬러 0~17 */
   int sel, sel_ch;                 /* 경기 컬러(−1 없음) · 그 캐릭터(−1 = 0x57D5 로) */
   int b2p;                         /* B 로 2P색 결정 중(그 판만 — 기억은 안 바꿈) */ 〔175에서 없앰 — B 도 보통 색(166-4)〕
   int rand_pick;                   /* 무작위 칸으로 결정했다 */
   int owned, last_scr, prev_in, hold_b, inj, inj_f, opt_f;
   int edit; uint16_t edit_c[3];    /* 내 색 만들기 창이 열려 있음 · 그 색 */
   int prow, psty; const uint8_t *ram;   /* 상태 저장 직전 되돌리기용 */
   int mem_gen, sel_gen, edit_req;  /* Java 가 보는 바뀜 셈 */
   unsigned f;
} K;
```

### 2-다. 매 프레임 규칙(`look_tick`)

1. **타이틀 메뉴**(MODE 240 · SCR 0 · 메뉴 글자 타일이 제자리 = `menu_kind()`)가 보이면 `sel = −1`, `b2p = 0`. SCR 0 만으로는 안 된다(이어하기 뒤 8프레임 SCR 0).
2. **고르기 화면을 쥔다** = MODE 240 · SCR 2/4 · **오른쪽 세로 이름 칸이 있음**(`vpanel_layout()` — 위아래 테 0x16C/0x16E·0x19C/0x19E + 18칸이 이름 타일) · 허브가 안 바쁨.
   세로 칸 조건이 이어하기 화면(SCR 2)·인트로(SCR 2/4)를 가린다 — 이어하기에서 OPTION 을 막지 않는다(시험 «이어하기 화면»).
3. 쥔 동안:
   - 커서 `h = 0x4E3C >> 2`. SCR 2 에서 `rand_pick = (h == 15)`. 기억 칸 `slot = (SCR 4 && rand_pick) || h == 15 ? 15 : h`(무작위로 골랐으면 돌아가는 캐릭터와 상관없이 무작위 칸의 기억), 표 줄 `row = h < 14 ? h : 쿠로코(14)`.
   - 검질 `sty = SCR 2 ? 0 : (0x574C & 1)`.
   - `was2 = owned(지난 프레임) && last_scr == 2`. `SCR 2 && last_scr == 4` 면 `b2p = 0`(검질 고르기에서 뒤로).
   - **OPTION** 은 게임에 안 준다. 뗄 때 누른 시간이 40프레임 미만이면 `mem[slot] = 다음 컬러`(b2p 풀림, `mem_gen++`). 40프레임째에 아직 누르고 있으면 `edit_req++`(Java 가 «컬러 만들기» 창을 연다, 쿠로코 칸 제외).
     다음 컬러는 0~17 을 돌며 건너뛴다: 그 캐릭터에서 앞 프리셋과 같은 색(LOOK_DUP — 캐릭터 고르기에선 두 검질 모두 같을 때만, 검질 고르기에선 그 검질), 안 만든 내 색, 쿠로코의 2P색.
   - **B**(SCR 2 만) 는 게임에 안 준다. `was2` 이고 새로 누른 B 면 `b2p = 1`, 2프레임 뒤부터 4프레임 A 를 `look_in_or` 로 더한다. 누른 B 는 뗄 때까지 막는다(검질 고르기에서 «뒤로»로 새지 않게). B·A 를 막을 땐 코어가 A+B 로 접는 비트(Y·X·L·R)도 막는다.
   - `cur = b2p ? 1 : mem[slot]`(쓸 수 없는 값이면 0). `sel = cur`, `sel_ch = h < 14 ? h : −1` — 무작위 뽑기가 멈춘 커서도 실제 캐릭터라 그대로 맞는다.
   - 미리보기: 팔레트 0 이 (row, sty) 의 어느 컬러든(또는 만드는 색) 보일 색이 아니면 고쳐 쓴다(OPTION 으로 바꿀 땐 게임이 팔레트를 다시 안 쓴다). 다른 검질 색이면 둔다(곧 게임이 다시 쓰고 코어가 바꾼다).
   - 코어 표: `cur > 0` 이면 두 자리(수라·나찰) 모두 `기본(row, k) → 컬러(row, k, cur)`.
   - 세로 칸 = `LOOK_VLAB[cur]`(만드는 중이면 «내 색 1»).
4. 쥐지 않은 동안: 방금까지 쥐었으면 세로 칸을 되돌린다. `sel > 0` 이고 고르기 화면이 아니면 **경기 표**:
   - `ch = sel_ch >= 0 ? sel_ch : (0x57D5 < 14 ? 0x57D5 : 없음)`.
   - 두 자리 모두 `기본(ch, k) → 컬러(ch, k, sel)`. 그리고 팔레트 0 이 지금 `기본(ch, k)` 이면 바로 고쳐 쓴다(불러온 상태·켠 순간 — 게임이 다시 쓰기 전).
   - `sel == 1`(2P색)이면 팔레트 5 의 두 자리 `2P색(ch, k) → 기본(ch, k)` + 같은 고쳐 쓰기 — 그 2P색은 같은 캐릭터·같은 검질 미러전의 P2 에만 나온다(같은 캐릭터 다른 검질은 그 검질 기본 색이라 안 걸림).
   - 검질을 몰라도 된다(두 자리) · P1BLK 를 안 본다(이야기 화면 동안 옛 값).
5. `look_in_block`·`look_in_or` 를 정하고 코어 표를 넣는다(바뀐 칸만 — 지금 `pr_push` 와 같음, 코어를 새로 올리면 `rm_init = 0` 으로 표 전체를 비우고 다시).

경기 컬러가 남는 범위: 고르기를 떠난 뒤부터 타이틀 메뉴가 보일 때까지 — 1인 대전 내내(이야기·판 사이·이어하기 화면 포함). 이어하기 → 캐릭터 고르기에서 다시 고르면 그 값.

### 2-라. 상태 저장·불러오기

- `look_before_save()`(native `nativeSaveState`, `league_hub_before_save()` 바로 뒤): 세로 칸을 원래대로 + **팔레트 0·5 도 우리가 바꾼 색이면 원래 색으로**(캐릭터·검질을 알고 되돌린다 — 황금·은빛·그림자처럼 캐릭터가 달라도 같은 세 색인 프리셋이 있어 색만으론 못 가린다). 다음 프레임에 다시 바꾼다.
  → `.look` 없이 그 상태를 불러도(옛 앱·다른 판) 원래 색이고, 게임이 팔레트를 다시 쓸 때까지 엉뚱한 색이 남지 않는다(시험 «.look 없이 불러오면 원래 색»).
- 경기 컬러는 상태 파일 옆 **`<경로>.look`** 에 남긴다(아래 8-다). 불러온 뒤 `look_resume(blob|NULL)`. 연습의 `.prac` 와 같은 방식(상태 크기·FNV 지문이 맞을 때만).
- 리그 체크포인트 이어 하기: `league_look(stage, color)` 가 `look_set_match(color)` 를 부른다(`sel = color`, `sel_ch = −1` → 0x57D5). 새 경기는 −1(고르기 화면에서 정함).

### 2-마. 세로 칸 주인 하나 — `vpanel.c`

리그 «상대 선택»(배경 이름)과 look(컬러 이름)이 같은 칸(둘째 판 3~11줄 × 17·18칸 → 빈 타일 0x130~0x141)을 쓴다. 지금처럼 `H.vp_orig` 가 league.c 안에 있으면,
허브가 배경 이름으로 바꿔 둔 칸을 look 이 넘겨받을 때 «이미 우리 타일»이라 원래 값을 못 남기고, 되돌릴 때 엉뚱한 값을 쓴다.
→ `vp_layout`·`vp_put`·`vp_restore` 와 `menu_kind` 를 `vpanel.c` 로 옮기고(동작 같음), 둘 다 이것을 부른다. 부르는 쪽은 모두 코어 잠금 안(GL 스레드 · 상태 저장 직전)이라 따로 잠그지 않는다.

### 2-바. 잠금

- look 은 자기 잠금(K_mu). `league_hub_status`(L_mu) 가 `look_cur()`(K_mu) 를 부른다 → 순서 L_mu → K_mu 만. look 은 L_mu 를 안 잡는다.
  native 는 `league_hub_owns_select()` 를 먼저 부르고(잠금 풀림) 그 값을 `look_tick` 에 준다(겹치지 않음).
- Java(UI 스레드)의 `nativeLook*` 는 K_mu 만. 팔레트를 직접 쓰는 일은 `look_tick`·`look_before_save`(코어 잠금 안)에서만.

---

## 3. 설계 (2) — 컬러 16가지

### 3-가. 고른 16개 (번호 = 기록·기억에 남는 값)

c1 = 가장 밝은 색(살·하이라이트, 하오마루·주베이는 옷 대부분도), c2 = 옷 주색, c3 = 테·어두운 색. «살색 둠» 은 c1 을 기본 그대로.

| # | 이름(세로 칸) | 만드는 법 |
|---|---|---|
| 0 | 기본 | PAL1 기본 |
| 1 | 2P색 | PAL1 2P색(게임 공식) |
| 2 | 쪽빛 | 물들임 225° |
| 3 | 비취 | 물들임 150° |
| 4 | 보라 | 물들임 280° |
| 5 | 다홍 | 물들임 355° |
| 6 | 분홍 | 살색 둠 · c2 = HSV(330°, 0.40, 1.0) · c3 = HSV(330°, 0.75, 0.60) |
| 7 | 먹빛 | 살색 둠 · c2 333 · c3 111 |
| 8 | 흰옷 | 살색 둠 · c2 EEE · c3 444 |
| 9 | 황금 | 밝기 순위로 (9EF, 0AE, 035) |
| 10 | 은빛 | 밝기 순위로 (FFF, BAA, 544) |
| 11 | 청동 | 밝기 순위로 (8BE, 269, 123) |
| 12 | 흑백 | 세 색을 밝기(0.299R+0.587G+0.114B) 회색으로 — 이미 무채색이면(기본과 채널 차 합 ≤ 6, 아수라 수라) 순위로 (FFF, 999, 000) |
| 13 | 그림자 | 밝기 순위로 (645, 323, 101) |
| 14 | 핏빛 | 밝기 순위로 (9AF, 00C, 003) |
| 15 | 유령 | 밝기 순위로 (FFE, EC9, 965) |
| 16·17 | 내 색 1·2 | 캐릭터마다 사용자가 만든 세 색(6장) |

- 물들임(hue h): 살색 둠, c2 = HSV(h, 0.8, clamp(V₂, 0.55, 1.0)), c3 = HSV(h, 0.85, clamp(V₃, 0.20, 0.45)).
  기본 옷이 이미 그 색 계열이면(채도 ≥ 0.3, 색상 차 < 35°) 다른 모습이 되게 — 어두운 옷(V₂ < 0.75)은 밝게 c2 = HSV(h, 0.45, 1.0) · c3 = HSV(h, 0.9, 0.55), 밝은 옷은 짙게 c2 = HSV(h, 1, 0.55) · c3 = HSV(h, 1, 0.2).
- «밝기 순위로»: 기본 세 색을 밝기 순으로 (밝음, 중간, 어두움) 에 대 준다 — 캐릭터마다 어느 칸이 살·옷·테든 같은 금속·석상 느낌. 이 프리셋들은 캐릭터가 달라도 같은 세 색이 나온다(그래서 되돌릴 땐 캐릭터를 안다 — 2-라).
- 겹침: 같은 캐릭터·검질에서 앞(보이는) 프리셋과 채널 차 합 ≤ 6 이면 그 칸을 건너뛴다(LOOK_DUP). 지금 표에서 걸리는 것 —
  겐쥬로 수라 다홍(≈2P색) · 한조 나찰 다홍(≈기본) · 아수라 수라 먹빛(≈기본) · 아수라 나찰 보라(≈2P색) · 주베이 나찰 먹빛(≈기본) · 시키 수라 흑백(≈먹빛) · 쿠로코 2P색(없음).
  캐릭터 고르기에선 두 검질 모두 같을 때만 건너뛰므로 위 것은 모두 그대로 돌고, 검질 고르기에서만 그 검질 것을 건너뛴다.

표 일부(수라, 색 1·2·3, 0x0BGR):

| | 기본 | 2P색 | 쪽빛 | 비취 | 보라 | 다홍 | 분홍 | 먹빛 | 흰옷 | 황금 | 은빛 | 청동 | 흑백 | 그림자 | 핏빛 | 유령 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 우쿄 | BDF·E60·500 | BBF·40A·005 | BDF·820·310 | BDF·8E3·351 | BDF·E3A·514 | BDF·43E·115 | BDF·C9F·629 | BDF·333·111 | BDF·EEE·444 | 9EF·0AE·035 | FFF·BAA·544 | 8BE·269·123 | DDD·555·111 | 645·323·101 | 9AF·00C·003 | FFE·EC9·965 |
| 나코루루 | CDF·43F·224 | BDF·07F·224 | CDF·F63·411 | CDF·9F3·241 | CDF·F3B·413 | CDF·108·003 | CDF·C9F·629 | CDF·333·111 | CDF·EEE·444 | 9EF·0AE·035 | FFF·BAA·544 | 8BE·269·123 | DDD·777·333 | 645·323·101 | 9AF·00C·003 | FFE·EC9·965 |
| 아수라 | FFF·444·222 | FFF·988·222 | FFF·832·310 | FFF·582·230 | FFF·826·302 | FFF·228·103 | FFF·C9F·629 | FFF·333·111 | FFF·EEE·444 | 9EF·0AE·035 | FFF·BAA·544 | 8BE·269·123 | FFF·999·000 | 645·323·101 | 9AF·00C·003 | FFE·EC9·965 |
| 하오마루 | BDF·00D·023 | BDF·080·023 | BDF·D53·310 | BDF·8D3·230 | BDF·D3A·302 | BDF·108·003 | BDF·C9F·629 | BDF·333·111 | BDF·EEE·444 | 9EF·0AE·035 | FFF·BAA·544 | 8BE·269·123 | DDD·444·222 | 645·323·101 | 9AF·00C·003 | FFE·EC9·965 |

전체 표(15줄 × 2검질 × 16): `<C>/proto/look_tab.h`(생성기 `<C>/proto/look_gen.py` + `<C>/colorgen.py` 의 `FINAL`).

### 3-나. 어떻게 골랐나 — 보고 뺀 것

후보 26개를 14명 × 수라/나찰, 배경 7곳(후지산 마을 · 숲속 호숫가 · 산 위 신사 · 화염 사원(밤) · 불꽃 동굴 · 마계 제단 · 수정 신전) 경기 화면에 실제 코어 바꿔 쓰기로 입혀 찍고 봤다(`<C>/render.py`).

| 대조표(`<C>` 안, 롬 그림이라 scratch 만) | 내용 |
|---|---|
| grid_a.png · grid_b.png · g1~g3.png | 후보 26개 × 6명(하오마루·나코루루·아수라·샬럿·우쿄·시키) |
| f1.png · f2.png | 최종 16개 × 다른 8명(카즈키·소게츠·겐쥬로·리무루루·한조·갈포드·모로즈미·주베이) |
| f3.png · f4.png | 최종 16개 × 어두운·밝은 배경 6곳 |
| final_sura_a/b.png · final_nachura.png | 최종 16개 × 14명 수라 · 4명 나찰 |
| look_select_shots.png · tl_ko_shots.png | 고르기 화면(세로 칸 «기본·쪽빛·그림자·내 색 1»·내 색 미리보기·검질 고르기) · 경기(보라·무작위 은빛·미러전 2P색 대 기본) |

| 뺀 후보 | 까닭 |
|---|---|
| 컬러3 · 컬러4(지금의 +120°/+240° 돌림) | 이름이 뜻이 없고 캐릭터마다 결과가 제각각(아수라는 진홍·청록, 나머지는 녹·청 아무거나) — 물들임 넷이 대신 |
| 하늘 · 풀빛 | 쪽빛·비취와 거의 같다 |
| 노랑 · 주황 | 옷이 어두운 캐릭터(시키·아수라·하오마루 띠)에서 올리브·갈색이 된다 — 황금·청동이 대신 |
| 옥돌(초록 석상) | 비취와 겹친다 |
| 세피아 | 탁하고 청동과 겹친다 |
| 반전(네거티브) | 캐릭터마다 딴판 — 샬럿·우쿄·시키는 올리브 노랑 덩어리, 아수라만 멋있음 |
| 불꽃(주황 석상) | 황금과 겹친다 |

남긴 것 중 확인한 점: 흰옷은 테를 777 → 444 로 진하게(모래 바닥에 녹던 것), 분홍은 고정 밝은 분홍(다홍과 겹치던 것), 그림자는 가장 어두운 화염 사원(밤)에서도 윤곽이 보인다(c1 645).
짝꿍 짐승(매·콘루·갈포드 개)은 원래 색 그대로(게임 2P색과 같은 규칙).

---

## 4. 설계 (3) — 내 색(캐릭터마다 2칸)

### 4-가. 데이터

- 한 칸 = 세 색 {c1, c2, c3}, 각각 12비트 0x0BGR(빨강 = 아래 4비트, 채널 0~15). 색 0(투명)은 안 건드린다.
- 캐릭터마다 2칸(내 색 1·2), **두 검질 같이 쓴다** — 세 칸의 역할(밝은 색·옷·테)이 두 검질에서 같고, 고르기 화면에서 검질을 바꿔도 «내 색 1»이 같은 모습이어야 헷갈리지 않는다.
  (시제품 API 는 검질 인자가 있다 — Java 가 두 검질에 같은 값을 넣는다.)
- 쿠로코(무작위 칸)는 내 색 없음.

### 4-나. 만들기 창(앱, «컬러 만들기»)

- 여는 법: 고르기 화면(캐릭터·검질, look 이 쥔 때)에서 **OPTION 길게(40프레임)** → look 이 `edit_req++` → Java 가 창을 연다. 멈춤 바(뒤로) 에도 «컬러 만들기» 칸(고르기 화면일 때만 보임).
- 게임은 멈추지 않는다(멈추면 미리보기가 다시 안 그려진다). 창이 열린 동안 look 이 게임 입력을 모두 막는다(`look_in_block = 0xFFF`) — 고르기 화면엔 시간 제한이 없다(4000프레임 그대로, `exp14.py`).
- 창은 화면 아래쪽(가운데 위 미리보기 그림이 보이게), 엄지로 쓰는 큰 칸:
  - 맨 위: «컬러 만들기 — 우쿄» · 시작 색 고르기(16개 중 하나 — 처음엔 지금 보이는 색).
  - 세 줄 «밝은 색» «옷 색» «테 색» — 줄마다 색 견본 + 빨강·초록·파랑 0~15 막대(−/+ 단추 포함).
  - 아래: «내 색 1에 저장» · «내 색 2에 저장» · «취소».
- 바꿀 때마다 `nativeLookEdit(true, sty, c1, c2, c3)` → 게임 미리보기 그림이 바로 그 색(look 이 팔레트 0 을 그 색으로 · 세로 칸 «내 색 1»).
- 저장: Java 가 `Look.saveCustom(ch, k, c)` → `nativeLookSetCustom(ch, 0|1, k, …)` 두 번 → `mem[ch] = 16 + k` → `nativeLookSetMem` → `nativeLookEdit(false, …)`. 취소는 `nativeLookEdit(false, …)` 만.
- 알아보기 어려운 색 막기(아랑 «Edited Colors» 조사 항목): 세 색이 모두 거의 같으면(채널 차 합 < 6) 저장 단추 옆에 «세 색이 너무 비슷해요» 안내(막지는 않음).

---

## 5. 바꿀 것 — 네이티브

### 5-가. 새 파일

| 파일 | 내용 | 시제품 |
|---|---|---|
| `cpp/look.c` · `look.h` | 2장 전부 + JNI(`Emu.nativeLook*`) | `<C>/proto/look.c`(353줄) · `look.h` |
| `cpp/look_tab.h` | `LOOK_TAB[15][2][16][3]`(2880바이트) · `LOOK_DUP[15][2]` · `LOOK_NAME[18]` — 생성물 | `<C>/proto/look_tab.h` |
| `cpp/look_glyphs.h` | `LOOK_VLAB[18 × 18타일 × 16]`(5184바이트) — 갈무리11 12px 세로 글자(지금 HUB_VLAB 와 같은 방식) | `<C>/proto/look_glyphs.h` · 미리보기 `look_vlabels.png` |
| `cpp/vpanel.c` · `vpanel.h` | 세로 칸 주인 하나(league.c 의 vp_* + menu_kind 를 옮김) | `<C>/proto/vpanel.c` |
| `handoff/ss2_color/look_gen.py` · `colorgen.py` | 표·글자 생성기(`python3 look_gen.py <cpp 폴더> <assets/fonts/pixel.ttf>`) | `<C>/proto/look_gen.py` · `<C>/colorgen.py` |

look.h API(시제품 그대로):

```c
#define LOOK_NIDX 18   /* 0~15 프리셋 · 16·17 내 색 */
#define LOOK_NSLOT 16  /* 0~13 캐릭터 · 14 안 씀 · 15 무작위 칸 */
#define LOOK_NSTAT 12
#define LOOK_CTX_FREE 0
#define LOOK_CTX_BUSY 1
void look_enable(int on);
void look_vram(void *chr, void *scr, void *pal);
void look_palremap_fn(void *fn);
void look_tick(uint8_t *ram, size_t n, int input, int ctx);
void look_set_mem(const signed char *mem, int n);
int  look_get_mem(signed char *mem, int n);          /* 돌려줌 = mem_gen */
void look_set_custom(int ch, int sty, int k, int c1, int c2, int c3);   /* c1 < 0 = 지움 */
void look_set_match(int idx);                        /* 리그 체크포인트 — −1/0 = 정하지 않음 */
void look_edit(int on, int sty, int c1, int c2, int c3);
void look_status(int v[LOOK_NSTAT]);
int  look_cur(void);
void look_before_save(void);
size_t look_blob(void *buf, size_t cap);             /* 16바이트, 경기 컬러 없으면 0 */
void look_resume(const void *buf, size_t n);         /* NULL = 없음(경기 컬러 잊음) */
void look_forget(void);
extern volatile int look_in_block, look_in_or;
```

`look_status` = [켜짐, 고르기 화면을 쥠, 기억 바뀐 횟수, 보이는 컬러, 경기 컬러(−1), 경기 캐릭터(−1), 2P색 결정 중, 만들기 요청 횟수, 검질 고르기 검질(−1), 경기 컬러 바뀐 횟수, 만드는 중, 프레임].

`look_edit` 는 실제 판에선 검질 인자 없이 두 검질 모두에 쓰게 바꾼다(4-가).

### 5-나. `league.c` (시제품 diff `<C>/proto/league.c.diff`)

- 지운다: `PAL1`·`g_pal`·`gen_color`·`look_targets`·`pal_rd/pal_wr/pal_is`·`look_apply`·`look_preview`(약 75줄), `g_palremap`·`PR_IDX`·`pr_have`·`pr_init`·`pr_push`·`pr_update`(약 60줄),
  `league_tick` 의 `look_apply` 줄, `league_tick_hub` 의 `pr_update(ram)`, 여러 곳의 `pr_init = 0`.
- H_PICK_ME: OPTION·B·`look_preview`·`vp_put(9 + H.color)`·`vp_restore` 블록을 지운다(look 이 쥔다). `H.nav == 4`(B 2P색 대신 누르기) 갈래도 지운다(look 의 `look_in_or`).
- `league_vram` → `look_vram(chr, scr, pal)` 도 부름. `league_palremap_fn(fn)` → `look_palremap_fn(fn)`.
- `vp_layout/vp_put/vp_restore` → `vpanel_*`(배경 이름 HUB_VLAB 0~8 은 그대로 league 가 넣음). `menu_kind` 는 vpanel 의 것을 같이 쓴다.
- `league_hub_status` v[10] = `look_cur()`(Java hubTick 이 그대로 읽음). `league_hub_look(home, stage_sel, color)` 의 color 는 안 씀. `league_look(stage, color)` → 배경만 + `look_set_match(color)`.
- 새 `int league_hub_owns_select(void)`(league.h 에 선언).
- **`H`·`L` 의 칸은 지우지 말고 남긴다**(`H.color`·`H.vp_on`·`H.vp_orig`·`L.color`) — `.prac`(연습 이어 하기 blob)가 `sizeof H`·`sizeof L` 그대로 들어 있어 판이 바뀌면 옛 `.prac` 를 못 읽는다. 쓰지 않는 칸이라고 주석만.
- `& 3` 세 곳은 지운 코드와 함께 사라진다.

### 5-다. `native.c`

- `#include "look.h"`.
- 입력 콜백(376~378줄): `blk |= look_in_block`, or 에 `| look_in_or`.
- `nativeFrame` 진짜 프레임 갈래(931~939줄): `league_tick_hub(…)` 다음에 `look_tick(ram, ramsz, in, league_hub_owns_select() ? LOOK_CTX_BUSY : LOOK_CTX_FREE);`.
- 코어 올림(771줄 근처)·내림(842줄 근처): `look_enable(0); look_forget();`.
- `nativeSaveState`: `league_hub_before_save();` 다음에 `look_before_save();`, 같은 잠금 안에서 `look_blob` 을 받아 `<경로>.look` 에 쓴다(없으면 지움). `nativeLoadState`: `.look` 을 읽어 지문이 맞으면 `look_resume(blob, n)`, 아니면 `look_resume(NULL, 0)`(불러온 판 램에 맞지 않는 경기 컬러를 버린다).
- 앱 리셋·상태 불러오기 실패 길(1011·1128줄 근처, `league_practice_title()` 옆): `look_resume(NULL, 0)`.

### 5-라. 빌드·글자

- `CMakeLists.txt`: `add_library(pocketcore SHARED native.c framegen.c league.c practice.c look.c vpanel.c)`.
- `hub_glyphs.py` VLABELS 에서 컬러 넷(«기본·2P색·컬러3·컬러4»)을 빼고 HUB_VLAB_N = 9(배경 8 + 무작위). 컬러 글자는 `look_gen.py` 가 만든다.

---

## 6. 바꿀 것 — Java

### 6-가. 새 `Look.java`

```java
final class Look {
    static final String[] NAMES = { "기본","2P색","쪽빛","비취","보라","다홍","분홍","먹빛","흰옷","황금","은빛","청동","흑백","그림자","핏빛","유령","내 색 1","내 색 2" };
    static final String[] OLD = { "기본","2P색","컬러 3","컬러 4" };            /* cv 없는 옛 리그 기록 */
    static String name(int idx, int cv) { … cv < 2 && idx >= 2 ? OLD[idx & 3] : NAMES[idx] … }
    static final String K_ON = "pocketcore_ss2_look", K_MEM = "pocketcore_ss2_look_mem", K_CUS = "pocketcore_ss2_look_cus";
    static byte[] loadMem();             /* Settings K_MEM "0,1,…"(16개) — 없으면 migrate() */
    static void saveMem(byte[] m);
    static int[][][] loadCustom();       /* [14][2][3], 없는 칸 null */
    static void saveCustom(int ch, int k, int[] c3);   /* null = 지움 */
    static void push();                  /* nativeLookSetMem + nativeLookSetCustom(ch, 0/1, k, …) 모두 */
    static void migrate();               /* 옛 리그 pref.color(0~3) → 16칸 모두 그 값(2·3 은 같은 번호 = 쪽빛·비취) */
}
```

### 6-나. `Emu.java`

```java
public static native void   nativeLookEnable(boolean on);
public static native void   nativeLookSetMem(byte[] mem16);
public static native byte[] nativeLookGetMem();
public static native void   nativeLookSetCustom(int ch, int sty, int k, int c1, int c2, int c3);
public static native void   nativeLookSetMatch(int idx);
public static native void   nativeLookEdit(boolean on, int sty, int c1, int c2, int c3);
public static native int[]  nativeLookStatus();
public static native int[]  nativeLookTriples(int ch, int sty);   /* 만들기 창: 그 캐릭터 18색 × 3 */
```

### 6-다. `EmuActivity.java`

- `lookSetup()` — `practiceSetup(resumed)` 바로 뒤와 리그 허브 `hubStart` 끝에서: 켤 조건(2-가) → `Emu.nativeLookEnable(true)` + `Look.push()` + `lookPoll` 시작(200ms), 아니면 `nativeLookEnable(false)`.
- `lookPoll`: `nativeLookStatus()` →
  - v[2](기억 바뀜)가 달라졌으면 `Look.saveMem(Emu.nativeLookGetMem())`.
  - v[7](만들기 요청)이 늘었으면 `openLookEditor(hover 캐릭터, 검질)`.
  - 허브가 없거나 허브가 타이틀 상태(1)이고 v[1] = 1(고르기 화면을 쥠)이면 띠에 `myPickKeys(scr)` + 둘째 줄 «OPTION 길게 = 컬러 만들기»; 고르기 화면을 떠나면 띠 숨김(연습·리그 띠 자리 그대로).
- `hubTick`: `hs[10]` 은 이제 look 의 보이는 컬러 — `League.setPrefLook(stageSel, …)` 에서 컬러는 빼고(배경만 저장), `League.setLook(leagueId, hubStage, hubColor)` 는 그대로(기록에 그 경기 컬러). 내 색이면 기록에 세 색도(8-나).
- `leagueStart`(1126~1132줄): `int col = lk != null ? lk.optInt("color", 0) : -1;` → `Emu.nativeLeagueLook(stg, col)`(새 경기는 −1 — 고르기 화면에서 정함). `League.prefColor()` 를 안 쓴다.
- `openLookEditor(ch, sty)`: 4-나 창. `Emu.nativeLookTriples(ch, sty)` 로 시작 색 목록.
- 멈춤 바: 고르기 화면(look v[1] = 1)일 때 «컬러 만들기» 칸.

### 6-라. `League.java`·`LeagueActivity.java`·`Settings.java`

- `League.COLORS` → `Look.NAMES` 로 바꾸고(옛 이름은 `Look.name(idx, cv)`), `prefColor()` 는 `Look.migrate()` 에서만 쓰고 지운다. `setPrefLook(stage, color)` → `setPrefStage(stage)`.
- `setLook(id, stage, color)` → `{"stage", "color", "cv": 2, "tri": [c1,c2,c3](내 색일 때만)}`.
- `LeagueActivity` 291줄 안내: « · 컬러는 캐릭터마다 — 고르기 화면에서 OPTION» 으로(«내 컬러 «…»» 한 값이 없어졌다).
- `Settings.java` «ss2» 묶음에 새 줄(«리그·연습» 위):

```java
new Item("pocketcore_ss2_look", "컬러 고르기",
    "켬 = 캐릭터 고르기에서 OPTION 으로 컬러(16가지 + 내 색 2), B = 2P색으로 결정. 1인·무한·연습·리그 모두. OPTION 길게 = 컬러 만들기. 캐릭터마다 기억해요.", 〔177 정리: 175부터 «B 2P색» 안내 없음 — B 도 보통 색 결정(166-4)〕
    ONOFF, ONOFF_K, "enabled").g("ss2").l(),
```

---

## 7. 화면 글(한국어 — 짧게)

| 자리 | 글 |
|---|---|
| 세로 칸(게임 화면 안) | 기본 · 2P색 · 쪽빛 · 비취 · 보라 · 다홍 · 분홍 · 먹빛 · 흰옷 · 황금 · 은빛 · 청동 · 흑백 · 그림자 · 핏빛 · 유령 · 내 색 1 · 내 색 2 |
| 띠 — 캐릭터 고르기 | `A 결정  ·  B 2P색  ·  OPTION 컬러` / `OPTION 길게 = 컬러 만들기` |
| 띠 — 검질 고르기 | `A 결정  ·  OPTION 컬러` |
| 만들기 창 제목 | `컬러 만들기 — 우쿄` |
| 만들기 창 줄 | `밝은 색` · `옷 색` · `테 색` · 막대 `빨강` `초록` `파랑` |
| 만들기 창 단추 | `내 색 1에 저장` · `내 색 2에 저장` · `취소` · 시작 색 `처음 색:` |
| 만들기 창 안내 | `세 색이 너무 비슷해요` |
| 저장 알림(토스트) | `내 색 1 저장 — 우쿄` |
| 설정 | 위 6-라 |
| 리그 화면 | `컬러는 캐릭터마다 — 고르기 화면에서 OPTION` |

---

## 8. 데이터 형식

### 8-가. 앱 설정(`Settings`, 앱 전체 — 리그 세이브와 따로)

| 키 | 값 |
|---|---|
| `pocketcore_ss2_look` | `enabled` / `disabled`(기본 enabled) |
| `pocketcore_ss2_look_mem` | 16개 정수 `"0,1,0,9,…"` — 칸 0~13 캐릭터 · 14 안 씀 · 15 무작위 칸, 값 0~17 |
| `pocketcore_ss2_look_cus` | JSON `{"v":1,"c":{"11":[[3039,744,65],null], …}}` — 캐릭터 → [내 색 1, 내 색 2], 각 [c1,c2,c3] 12비트 정수(0x0BGR) 또는 null |

### 8-나. 리그 경기 기록(`league.json` matches[].look)

`{"stage": 1, "color": 9, "cv": 2}` · 내 색이면 `{"stage": 1, "color": 16, "cv": 2, "tri": [3039, 744, 65]}`. `cv` 가 없으면 옛 기록(0~3 = 기본·2P색·컬러 3·컬러 4).
`pref` 에서 `color` 는 더 안 쓴다(남아 있어도 무시, 첫 실행에 `Look.migrate()` 가 한 번 읽음).

### 8-다. 상태 옆 `<경로>.look`

`"LOK1"` · u32 상태 크기 · u32 상태 FNV-1a · 16바이트 blob. blob = `'L' 'K' 1 sel sel_ch(부호) 0…` (시제품 `look_blob`).
경기 컬러가 없으면 파일을 지운다. 불러올 때 크기·지문이 맞아야 쓴다(`.prac` 와 같은 규칙).

---

## 9. 시험

### 9-가. 이번에 쓰고 돌린 호스트 시험(모두 `<C>/tests/`, 시제품 lib `<C>/proto/host_look.so`)

빌드: `cd <C>/proto && gcc -O2 -Wall -shared -fPIC -I<scratchpad>/legacito/host/inc -o host_look.so league.c practice.c look.c vpanel.c -lm`
환경: `source <C>/env.sh` 뒤 `LEAGUE_HOST_SO=<C>/proto/host_look.so PYTHONPATH=$PYTHONPATH:<C>/tests`. 하네스 `lh.py`(= ph.PH + look_tick + look 입력 비트, 2-가 순서).

| 시험 | 무엇 | 결과 |
|---|---|---|
| `t_look.py <롬> [fast]` | 꺼짐 = 원래 게임 · 1인 대전 캐릭터 고르기 세로 칸 «기본» · OPTION → 2P색 → … → 황금(미리보기·세로 칸·기억) · 다른 캐릭터는 그 기억 · B(40프레임) = 2P색 결정 + 검질 고르기(안 샘), 기억 그대로 · 검질 고르기 B = 뒤로 + 2P색 풀림 · 나찰 미리보기 · 검질 고르기 OPTION · 경기 색 · 고르기→이야기→소개까지 원래 색 0프레임 · 두 라운드 + 사이 연출 원래 색 0프레임 · .look 저장·되돌림 · .look 없이 = 원래 색 · 이어하기 화면에서 OPTION 안 막음·쓰러진 P1 도 그 색 · 이어하기 → 다시 고르기 · 타이틀에서 경기 컬러 잊음 · 인트로·데모 3000프레임 동안 안 쥠 · 무한 대전 · 무작위 칸(쿠로코 미리보기, 2P색 건너뜀, 뽑힌 캐릭터에 그 색) · 미러전 2P색 → P2 기본 색 | **27/27 × 롬 4판**(동봉 한글판·한글 v1.01·h1 한글·순정 JUE), 동봉 한글판은 앱과 같은 런어헤드 2·프레임 생성으로도 27/27(`res_*.txt`) |
| `t_look_hub.py <롬> [fast]` | 연습 상대 선택: look 안 쥠·OPTION = 스테이지·컬러 기억 그대로·세로 칸 = 스테이지 이름·상대 미리보기 원래 색 · 더미 고른 뒤 내 캐릭터: look 이 쥠 · OPTION → 다홍(허브 상태 v[10] 도) · 연습 경기 P1 색 · 경기 중 입력 안 막음 · 리그 상대 선택 OPTION = 스테이지 · 내 캐릭터 B 2P색 · 리그 경기 색·무장 · 체크포인트 이어 하기(`league_look(배경, 9)` → 0x57D5 캐릭터 황금) | **12/12 × 롬 4판**(`resh_*.txt`) |
| `t_hub_look.py <롬>` | 기존 3단계 `t_hub.py`(28항목) 그대로, 하네스에만 look_tick·look 입력 비트 — 컬러 항목(옵션 2P색·미리보기·B 2P색·경기 2P색·경기 내내 원래 색 0프레임)까지 | **ALL PASS × 롬 3판**(동봉 한글·JUE·h1, `res_thub_*.txt`) |
| 기존 `t_dual.py` | 리그·연습 둘 다(셋째 줄 ◀▶·갈아타기·상태 저장 전 되돌리기) — 허브에서 컬러를 뺀 판 회귀 | 31 PASS · fails=0(`resdual_ko.txt`) |
| 기존 `t_practice.py`(시계 1791974914) | 연습 대전 1단계 전부 — 회귀 | ALL PASS(68항목, `res_tprac_914.txt`) |

### 9-나. 실제 판에서 더할 시험

- **`t_look.py`·`t_look_hub.py` 를 handoff 로**(`handoff/ss2_color/tests/`), 실제 `league.c` 가 바뀐 뒤 그대로 돈다(시제품과 API 같음). 롬 6판(동봉판 h1 포함) × fast + 동봉판 앱 설정.
- `t_hub.py` 를 `t_hub_look.py` 처럼 look_tick 을 더한 하네스로 바꾸고, 컬러 2 검사 문구(«만든 색») → «쪽빛».
- `t_dual.py`·`t_practice.py`·`t_resume.py`(연습 이어 하기 — `.prac` 판 크기 그대로인지)·`t_fix1.py` 회귀.
- 새로 넣을 항목:
  - 고르기 화면에서 상태 저장 → 불러오기: 미리보기 원래 색으로 저장되고 다음 프레임에 다시 그 색.
  - 내 색: `look_set_custom` 뒤 OPTION 으로 «내 색 1» 이 돎 · 안 만든 칸은 건너뜀 · `look_edit(1, …)` 동안 커서가 안 움직이고(입력 전부 막음) 미리보기가 그 색 · 끝내면 원래.
  - OPTION 길게(45프레임) → `edit_req` 1 늘고 컬러는 안 바뀜.
  - 겹침 건너뛰기: 아수라 나찰 검질 고르기에서 보라(≈2P색)를 건너뜀, 캐릭터 고르기에선 안 건너뜀.
  - 옛 코어(palremap 없음): 프레임 뒤 고쳐 쓰기만으로 돌고 원래 색 프레임 수를 INFO 로.
- JVM(`LeagueTest` 쪽): `Look.name(idx, cv)` 옛 기록 이름, `migrate()`(pref.color 2 → 16칸 2), `K_CUS` JSON 왕복, 경기 기록 `look.cv/tri`.
- 기기(안드로이드 에뮬레이터, 3단계 `android_emu.sh`): 1인 대전 고르기 화면 OPTION·B·띠·세로 칸, OPTION 길게 → 만들기 창 → 막대 → 미리보기가 바로 바뀜 → 저장 → 경기, 앱을 다시 켜도 기억, 리그 결과 카드·기록.

---

## 10. 위험

1. **모르는 롬 판** — 쓰는 주소(0x40A7·0x41C0·0x4E3C·0x574C·0x57D5·0x5B51·0x5D51)와 화면 칸 판별은 롬 4판에서만 쟀다. Java 가 확인한 판(`practiceRomOk`·리그 판)에서만 켠다. 0x574C 는 이번에 새로 찾은 주소라 롬 6판 모두에서 한 번 더 잴 것.
2. **옛 코어** — 업데이터가 palremap 없는 코어를 받으면 컬러는 되지만 1초에 한 번꼴 1~3프레임 원래 색이 보인다(지금 리그와 같음). 고르기 화면 미리보기는 프레임 뒤 고쳐 쓰기라 영향 적음.
3. **세로 칸 주인을 옮김** — 리그 배경 이름(상대 선택) 회귀 가능. `t_hub_look`·`t_dual` 이 지금 통과하지만 실제 판에서도 둘을 꼭 돌린다.
4. **`.prac` 크기** — `H`·`L` 칸을 지우면 옛 연습 이어 하기를 못 읽는다(5-나: 남긴다).
5. **OPTION 을 뗄 때 바뀜** — 길게 누르기를 가리려고 컬러가 «뗄 때» 바뀐다(누르는 순간이 아니라). 짧게 누르면 차이를 못 느낀다. 길게 누르기를 안 쓰기로 하면 누르는 순간으로 되돌린다.
6. **B 대신 누르기** — 허브의 옛 B(nav 4)는 ovr 로 모든 입력을 막았는데, look 은 A 만 더한다(B 는 막음). 그 4프레임 동안 십자를 누르면 게임이 커서를 옮길 수 있다 — 실측에선 A 가 먼저 먹었다. 필요하면 look 도 그 4프레임은 십자를 막는다.
7. **«밝기 순위로» 프리셋은 캐릭터가 달라도 같은 세 색** — 되돌리기·미리보기를 색만으로 하면 틀린다. 시제품은 캐릭터·검질을 알고 한다(2-라). 실제 판에서도 이 규칙을 지킬 것.
8. **이야기·엔딩의 P1 그림** — 팔레트 0 에 같은 기본 색으로 P1 을 그리는 화면은 모두 고른 색이 된다(이야기·판 사이·이어하기 실측, 엔딩은 못 봄). 엔딩 그림이 팔레트 0 의 다른 세 색이면 원래 색(안 바뀜).
9. **경기 컬러가 남는 범위** — 타이틀 메뉴를 거치지 않고 다른 모드로 가는 길(예: 상태 불러오기로 다른 판)은 `.look` 이 정한다. `.look` 이 없는 옛 상태를 불러오면 경기 컬러를 버린다(`look_resume(NULL)`).

## 11. 열린 질문(권장안)

| 질문 | 권장 |
|---|---|
| 컬러를 캐릭터마다 기억할까, 하나만 둘까 | 캐릭터마다(스파6·길티기어식 — 16가지면 캐릭터마다 어울리는 색이 다르다) |
| B(2P색 결정)는 기억에 남길까 | 그 판만(네오지오식 «누른 버튼 = 그 판 색», 실수로 B 를 눌러도 고른 색을 안 잃음) |
| 내 색을 검질마다 따로 둘까 | 캐릭터마다 하나(두 검질 같이) — 칸 역할이 같고 덜 헷갈림 |
| 만들기 창 여는 법 | OPTION 길게 + 멈춤 바 칸 둘 다 |
| 기본 켬? | 켬(설정 «컬러 고르기»로 끔) — 게임이 안 쓰던 버튼만 쓴다 |
| 옛 «컬러 3·4» 를 남길까 | 안 남김 — 번호 2·3 은 쪽빛·비취로 넘김(옛 기록은 cv 로 옛 이름) |
| CPU(P2) 상대 컬러 | 이번 범위 밖 — 표에 팔레트 5 자리가 이미 있어 «상대 고유 컬러»(랭크매칭 조사 4장)는 나중에 같은 길로 〔177 구현 — §12〕 |
| 띠 안내를 일반 1인 대전에도 띄울까 | 고르기 화면에서만 — 경기 중엔 안 띄움 |

## 12. 상대 컬러 (177 — 리그 랭크 상대마다 고정 색 · 설계 `../설계_상대컬러_166B/README.md` §2·§16)
- **누가 정하나**: `OppLook.of(seed, Player)`(Java, V=1) — 라이벌 12명은 표(`RIVAL`), 나머지는 `mix(seed, idHash, 0xC0105EED)` 흐름 하나로
  고유 색 15%(색상·채도·명도 뽑기 12번 — 기본·2P색과 거리 ≥ 13, 프리셋과 > 6) → 아니면 프리셋 가중치(`W` — 기본·2P 2+2 ≈ 4%, 금·은·유령은 MMR 1500 이상 두 배) →
  베기 색 20%(1~6). 쓸 수 있는 프리셋 = 그 캐릭터·검질 기본·2P색과 거리 ≥ 13 · 앞 프리셋과 ≤ 6 겹침 없음(평균 12.2개).
- **정본**: 처음 만날 때 경기 기록 `opp_snap.col`({i, t[3], n, fx})에 굳힌다 — 이어 하기·다시 올리기는 이 값만. 없으면(옛 경기) 끈다(판 중간에 색이 생기지 않게).
- **native**(look.c `OP`): 팔레트 5(P2 몸)만 고쳐 쓰기 · 고르기 화면(240 / 0·2·4·6)·타이틀 밖 · P2 캐릭터 = 그 상대일 때만 · 리그 무장·결판 대기(`league_opp_live`) 또는 불러온 뒤 120f.
  거울전에서 내 보이는 색과 거리 ≤ 9 면 대신 색(차례 2P·흰옷·먹빛·황금·쪽빛·다홍·비취·기본 — 게임 짝은 겹침 아님(K3): 같은 검질 {기본, 2P} 짝 ·
  다른 검질이면 둘 다 제 검질 게임 색(기본·2P — 게임은 거울 비트 없이 상대 검질 기본을 보임 · 177 리뷰 고침: 주베이 나찰 기본 vs 수라 기본 거리 7 에 흰옷이 나오던 것)) · 상태 `look_status` [18] 0/1/2 · [19] 대신 색.
  상대 베기 색은 내 베기 색과 같으면 끔. 저장 직전 게임 색으로 되돌리고 저장 뒤 다시(세이브에 우리 색이 안 남음).
- **넣고 끄기**(Java `oppLookSet`): 허브 대진(`rankArmNext`·`rankQGo` — VS 인트로 첫 프레임부터) · 경기 기록 · 이어 하기(`leagueStart` — 불러오기 **전**) ·
  끄기: `hubReturn`(−4 빼고) · `leagueExit` · 연습 허브 켤 때 · 이어 하기 실패 · 코어 올리기/내리기(native). `onDestroy` 에선 안 끈다(K1 — 새 창 leagueStart 가 먼저).
- **화면**: 쉼 정보 패 r6 c8–9 견본(팔레트 7, 지금 보이는 세 색 — 대신 색이면 그 색) · «상대 발견!» 카드 캐릭터 줄 뒤 색 이름(프리셋·고유 색, 저장한 내 캐릭터와 다른 상대, 들 때만 — 새 알림 글 없음).
- 내 «컬러 고르기» 끔이어도 상대 색은 그대로(K2). 연습 더미·리그 밖 1인 대전엔 없음. 분노 MAX 얼굴색(§9)은 **보류**(유저 10/19).
- 커스텀 프리셋·고유 색은 **검질 무관**(수라·나찰 같은 세 색 — 166-5) · 유가는 표 줄 15(롬 실측 · 수라 거울 2P = FFB/570/330).

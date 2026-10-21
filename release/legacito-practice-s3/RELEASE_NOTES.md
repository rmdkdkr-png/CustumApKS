# Legacito 시험판 — 연습 대전 1단계 · 코어 갱신 s3 (2026-10-14)

`Legacito-practice-s3.apk` — `legacito-practice-s1`·`s2` 와 같은 앱(패키지 `com.dudu.legacito.league`, 리그·연습 대전 그대로)에
동봉 코어만 ss2-sp-core main **1e0034b**(스탬프 d8137f4 — 99r·99s)로 바꿨습니다. 덮어 설치하면 리그 기록을 그대로 잇습니다.

- 99s: 고르기 화면(게임의 캐릭터 고르기·연습/리그의 상대 선택)에서 커서를 두 캐릭터 사이로 몇 번 오간 뒤 한 캐릭터에 두면,
  가운데 미리보기가 다른 캐릭터 모양 쪽으로 반쯤 바뀐 그림이 섞여 보이던 것 고침.
- 99r: 몸 ¼픽셀 작은 결함 셋(창 찌르기 때 창대 테두리 비침 · 서기 사이 그림은 ¼픽셀로 안 옮김 · 대전 밖 화면 가장자리의 몸은 안 옮김).
- 확인: 연습 시험 t_practice(ss2_ko_bundled) 68/68 · 리그 t_hub 28/28 을 새 코어로 다시 돌림 — 결과는 `handoff/ss2_practice/stage1/tests/results/*_core1e0034b.txt`.
  에뮬레이터에서 설치 → 실행 창 «연습 대전으로 ›» → 상대 선택 화면 확인.
- 리그·연습 패치(`handoff/ss2_league/stage3/`·`handoff/ss2_practice/stage1/`)는 Legacito `feat/framegen-art` 새 머리 357abd5(내부 129)에도 그대로 붙습니다.

자세한 것: `handoff/ss2_practice/1단계_연습대전.md`, s1 노트 `release/legacito-practice-s1/RELEASE_NOTES.md`.

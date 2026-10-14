# Legacito 시험판 — 연습 대전 1단계 · 코어 갱신 s4 (2026-10-14)

`Legacito-practice-s4.apk` — `legacito-practice-s1`~`s3` 와 같은 앱(패키지 `com.dudu.legacito.league`, 리그·연습 대전 그대로)에
동봉 코어만 ss2-sp-core main **89860fe**(스탬프 daca5c1 — 99t·99u)로 바꿨습니다. 덮어 설치하면 리그 기록을 그대로 잇습니다.

- 99t: 판 끝 승리 포즈의 첫 두 장도 머묾 내내 사이 그림(전에 같은 줄기에서 본 포즈면 첫 장부터 미리 봄).
- 99u: 10 프레임 넘는 머묾에서 ¼·½ 를 고르게(main 의 «마지막 8 프레임 창»이 걸리는 곳은 그대로).
- 확인: 연습 시험 t_practice(ss2_ko_bundled) 68/68 · 리그 t_hub 28/28 을 새 코어로 다시 돌림 — 결과는
  `handoff/ss2_practice/stage1/tests/results/*_core89860fe.txt`. 에뮬레이터에서 설치 → 실행 창 «연습 대전으로 ›» → 상대 선택 화면 확인.
- 알려진 것: 게임 시계를 특정 시각(유닉스 1791974914)에 고정하면 t_practice 의 세 항목(더미를 다시 서기로 돌린 뒤 대미지 · MAX 비오 뒤 창이 한 프레임 걸러 보임 ·
  메뉴 창이 안 보인 프레임)이 실패합니다. s3 코어(1e0034b)도 같은 시각에 똑같이 실패해 이번 코어 탓은 아니며, 연습 대전 쪽에서 따로 찾고 있습니다
  (`tests/results/*_fixt1791974914.txt`).
- 리그·연습 패치는 Legacito `feat/framegen-art` 새 머리 6cd78b2(내부 130)에도 그대로 붙습니다.

자세한 것: `handoff/ss2_practice/1단계_연습대전.md`, s1 노트 `release/legacito-practice-s1/RELEASE_NOTES.md`.

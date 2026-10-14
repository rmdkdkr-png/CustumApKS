# Legacito 시험판 — 연습 대전 1단계 · 코어 갱신 (2026-10-14)

`Legacito-practice-s2.apk` — `legacito-practice-s1` 과 같은 앱(패키지 `com.dudu.legacito.league`, 리그·연습 대전 그대로)에
동봉 코어만 ss2-sp-core main **66c81d7**(스탬프 f276d0f — 99q)로 바꿨습니다. 덮어 설치하면 리그 기록을 그대로 잇습니다.

- 99q: 번쩍임 줄이기 «거의 없게»에서 필살기 빛기둥·불꽃 같은 이펙트가 멈춘 듯 보이던 것 고침(빛기둥 깜빡임 섞기 뺌 · 밝기 급변은 평균 색 막으로).
  이 시험판 앱엔 번쩍임 줄이기 설정 항목이 아직 없어(코어 기본 «끔») 화면은 s1 과 같습니다 — 코어를 최신으로 맞춘 판.
- 확인: 연습 시험 t_practice(ss2_ko_bundled)·리그 t_hub 를 새 코어로 다시 돌림 — 결과는 `handoff/ss2_practice/stage1/tests/results/`.

자세한 것: `handoff/ss2_practice/1단계_연습대전.md`, s1 노트 `release/legacito-practice-s1/RELEASE_NOTES.md`.

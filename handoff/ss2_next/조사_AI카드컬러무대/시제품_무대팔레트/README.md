# 무대 팔레트 변형 — 10/17 시제품(클라우드 scratch u159/topicD-stages 에서 건짐, 2026-10-21)

조사 결론·실측은 위 폴더 README §5 · 부록 D4·D5. 코드는 앱·코어 어디에도 아직 없음.

- `core_proto_rom_overlay_bgtint_rtc.diff` — 코어 시제품(롬 덮어쓰기 rom_overlay · 배경 물들임 bgtint · RTC). core_patches 에는 안 들어간 것.
- `tint.py` · `mkpack.py` — 무대 칸 색 바꾸기 · 덮어쓰기 묶음 만들기(하네스 실측용).
- `topicD-stages.tar.gz` — 그 폴더의 스크립트·노트·시험 170개 전부(work/ 결과·빌드·롬 없음). 경로는 클라우드 scratch 고정 — 로컬/setup_wsl.sh 로 건 자리에 풀면 그대로: `tar -xzf topicD-stages.tar.gz -C $SP/u159/topicD-stages`.

PC 방 제안 순서: 기존 `retro_ngp_palremap` 으로 무대 칸(팔레트 128~191)이 바뀌는지 먼저 재기 → 안 되면 rom_overlay 다시. ▲▼ 조작이 결판·쉼 «줄» 이동과 겹치는 문제는 유저 결정.

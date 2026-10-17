# 배경음악 끔 사본 만들기(호스트 시험용)

`MuteTool.java` 는 앱 `Patcher.resolve` 와 같은 순서(원본 → 번역 IPS → 빈칸 계산 → `Ss1Music.mute`)로 «배경음악 끔» 사본을 만든다.
SS1 롬 없이 되는 «끔»이 «SS1 음악»과 같은 길(`Ss1Music.build` — 빈칸에 소리 자료 · 조립 코드 즉시값 바꾸기)을 타므로, 배경음악을 심은 사본에서
연습 대전이 그대로 도는지 보는 데 쓴다.

준비: 앱의 `Ss1Music.java`·`SnkScore.java` 를 `src/com/dudu/pocketcore/` 에 복사하고 `Ss1Music.java` 의 «사무쇼1 롬을 찾는다» 주석부터 끝까지
(롬 찾기 — Games·Archives·MainActivity 를 씀)를 지운 뒤 닫는 `}` 하나를 남긴다. `android/os/Environment.java` 빈 껍데기도 둔다.

    javac -d out $(find src -name "*.java")
    java -cp out com.dudu.pocketcore.MuteTool <원본 롬> <번역 IPS 또는 -> <출력>

결과: `results/*_mute_practice.txt` (롬 6판 모두 68/68, 최종 코드 1188eb8 · 코어 2cc0c59).

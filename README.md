# SANGO SP — 안드로이드 APK 빌드

`app/src/main/assets/index.html` 안에 DOSBox(js-dos)와 SP 버튼 UI가 전부 들어 있습니다.
이 프로젝트는 그걸 전체화면 WebView 로 띄우는 껍데기입니다.

## 방법 A — GitHub 에서 빌드 (PC 없이 가능)

1. GitHub 에 새 저장소를 만들고 이 폴더 내용을 그대로 올립니다.
2. Actions 탭 → **Build APK** → Run workflow.
3. 끝나면 Artifacts 에서 `sango-sp-apk` 다운로드 → 폰에서 설치.

## 방법 B — PC 에서 빌드

Android Studio 로 이 폴더를 열고 Run, 또는:

```
./gradlew :app:assembleDebug
# app/build/outputs/apk/debug/app-debug.apk
```

## 게임 파일

저작권 때문에 게임은 포함하지 않았습니다.
앱을 처음 켜면 ZIP 을 고르는 화면이 나옵니다. Sango Fighter 2 무료 배포판 ZIP 을
한 번 물려주면 기기 안에 보관되고 다음부터 자동으로 실행됩니다.

## 릴리즈

| 버전 | 파일 | 비고 |
|---|---|---|
| **SS2-1.0.1** | [`release/ss2-v1.0.1/NGPcustumSP-v1.0.1.apk`](release/ss2-v1.0.1/NGPcustumSP-v1.0.1.apk) | 앱 이름 NGPcustumSP · 간다라 기둥 · SP 배치 오버레이(타이거니) · 일시정지 · 전황 연출 · SS2 전용 잠금 — [릴리즈 노트](release/ss2-v1.0.1/RELEASE_NOTES.md) |
| SS2-1.0.0 | [`release/ss2-v1.0.0/NgpEmu-SS2-v1.0.0.apk`](release/ss2-v1.0.0/NgpEmu-SS2-v1.0.0.apk) | [릴리즈 노트](release/ss2-v1.0.0/RELEASE_NOTES.md) · 전체 이력 [CHANGELOG](handoff/CHANGELOG.md) |

롬은 포함되지 않는다 — 본인 소유 롬으로 구동할 것.

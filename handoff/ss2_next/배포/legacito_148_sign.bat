@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
rem Legacito 148 서명 — legacito-release.jks 를 이 파일과 같은 폴더에 두고 두 번 클릭.
rem 비밀번호는 화면에서만 받고 어디에도 저장하지 않는다.

if not exist legacito-release.jks (
  echo [!] legacito-release.jks 를 이 파일과 같은 폴더에 두세요.
  goto end
)
where java >nul 2>nul
if errorlevel 1 (
  echo [!] Java 가 필요합니다: https://adoptium.net 에서 받아 설치한 뒤 다시 실행하세요.
  goto end
)

set "BASE=https://github.com/rmdkdkr-png/PocketCore/releases/download/ci-release"
set "OUT=Legacito-v0.9-test50.apk"

echo 1/3 서명 전 APK 받는 중...
curl -fL -o Legacito-unsigned.apk "%BASE%/Legacito-unsigned.apk" || goto fail
curl -fL -o apksigner.jar "%BASE%/apksigner.jar" || goto fail

echo 2/3 서명
set /p "PW=키 비밀번호: "
java -jar apksigner.jar sign --ks legacito-release.jks --ks-key-alias legacito --ks-pass env:PW --key-pass env:PW --out "%OUT%" Legacito-unsigned.apk || goto fail
set "PW="

echo 3/3 확인
java -jar apksigner.jar verify --print-certs "%OUT%" | findstr /c:"5915abe0b8cc90e3e51d73e91751dd85ce79bc7c0fd31956fa9968eaf1b64f16" >nul || goto badkey

> legacito-version.json echo {"versionCode":90,"versionName":"0.9","apk":"Legacito-v0.9.apk","test":{"versionCode":148,"versionName":"0.9","apk":"%OUT%"}}

echo.
echo 끝. 이 폴더에 두 파일이 생겼습니다:
echo   %OUT%
echo   legacito-version.json
echo.
echo 이제 https://github.com/rmdkdkr-png/PocketCore/releases/tag/app 에서 Edit 을 눌러
echo   - %OUT% 를 끌어다 올리고
echo   - 원래 있던 legacito-version.json 을 지운 뒤 새 legacito-version.json 을 올리고
echo   - Update release 를 누르세요.
echo 폰의 Legacito 에서 「업데이트 확인」 하면 148 이 뜹니다(배포 레벨: 시험).
goto end

:badkey
echo [!] 서명 인증서가 Legacito 키(59:15:AB:E0...)와 다릅니다. 올리지 마세요.
del "%OUT%" 2>nul
goto end

:fail
set "PW="
echo [!] 실패했습니다. 위 메시지를 확인하세요.

:end
pause

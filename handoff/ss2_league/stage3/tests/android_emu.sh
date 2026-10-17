#!/bin/bash
# 게임 속 리그(3단계)를 진짜 안드로이드에서 돌려 보는 법 — KVM 없는 리눅스(클라우드 컨테이너)에서도 된다(느림: 게임 속도 1/15 안팎).
#   source android_emu.sh            # 함수만 읽기
#   emu_setup                        # 처음 한 번: 에뮬레이터·시스템 이미지·AVD
#   emu_boot                         # 부팅(소프트웨어 CPU 라 4분쯤)
#   emu_install app-debug.apk 원본롬.ngc
#   emu_hub ss2.ngc                  # 게임 속 리그로 바로 띄우기(adb root 로 비공개 EmuActivity 직접)
#   A; D; R; Lf; U; Bb; shot 이름     # 화면 패드 누르기(1080x2220 세로 · pixel_3a) · 화면 찍기
# 롬·화면 사진은 저장소에 넣지 않는다.
SDK=${ANDROID_HOME:-/root/android-sdk}
ADB=$SDK/platform-tools/adb
E=${EMU_OUT:-$PWD/emu_out}; mkdir -p "$E"
PKG=com.dudu.legacito.league

emu_setup() {
   local SM; SM=$(ls -d $SDK/cmdline-tools/*/bin | head -1)/sdkmanager
   yes | $SM --licenses >/dev/null 2>&1
   $SM --install "emulator" "platform-tools" "system-images;android-28;default;x86_64"
   echo no | $SDK/cmdline-tools/latest/bin/avdmanager create avd -n lg28 -k "system-images;android-28;default;x86_64" -d pixel_3a --force
   cat >> ~/.android/avd/lg28.avd/config.ini <<'EOF'
hw.ramSize=3072
disk.dataPartition.size=6G
hw.gpu.enabled=yes
hw.gpu.mode=swiftshader_indirect
hw.keyboard=yes
EOF
}

emu_boot() {   # KVM 이 없으면 -accel off(TCG). 창 없이, GL 은 swiftshader
   nohup $SDK/emulator/emulator -avd lg28 -accel off -no-window -no-audio -no-boot-anim -gpu swiftshader_indirect \
      -no-snapshot -cores 4 -memory 3072 -camera-back none -camera-front none > "$E/emu.log" 2>&1 &
   $ADB wait-for-device
   until [ "$($ADB shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = 1 ]; do sleep 5; done
   $ADB root >/dev/null; sleep 3; $ADB wait-for-device
}

emu_install() {   # $1 = apk, $2… = 롬(원본 — 한글은 앱이 리그 전용 사본에 입힌다)
   $ADB install -r -g "$1"; shift
   $ADB shell mkdir -p /sdcard/PocketCore/roms
   for r in "$@"; do $ADB push "$r" /sdcard/PocketCore/roms/; done
}

emu_hub() {       # 게임 속 리그 바로 띄우기 — 앱에서는 런처 사무쇼2 카드 → 「가상 리그 (시험) — 게임 속 「리그 대전」으로 ›」
   $ADB shell am force-stop $PKG
   $ADB shell am start -n $PKG/com.dudu.pocketcore.EmuActivity --es rom /sdcard/PocketCore/roms/"$1" --ez league_hub true
}

# 화면 패드(기본 배치). 부하가 크면 `input swipe` 의 누름·뗌이 한 프레임 안에 들어가 게임이 못 보는 일이 있어 길게(≥1초) 누른다.
A()  { $ADB shell input swipe 710 1670 712 1670 ${1:-1200}; }
Bb() { $ADB shell input swipe 950 1500 952 1500 ${1:-1200}; }
D()  { $ADB shell input swipe 236 1716 238 1716 ${1:-1200}; }
U()  { $ADB shell input swipe 236 1464 238 1464 ${1:-1200}; }
R()  { $ADB shell input swipe 360 1590 362 1590 ${1:-1200}; }
Lf() { $ADB shell input swipe 110 1590 112 1590 ${1:-1200}; }
FF() { $ADB shell input swipe 1010 350 1012 350 ${1:-60000}; }   # ▶▶ 배속(누르는 동안)
shot() { $ADB exec-out screencap -p > "$E/$1.png"; }

package com.dudu.pocketcore;
/* JVM 시험용 — 기록 뿌리 = -Dleague.root, 앱 설정 파일 = 그 아래 options.txt */
public class MainActivity {
    public static java.io.File root() { return new java.io.File(System.getProperty("league.root")); }
    public static java.io.File optsFile() { return new java.io.File(root(), "options.txt"); }
}

package com.dudu.pocketcore;
import java.io.*; import java.util.*;
/** Cheats.java(치트 키·값 ↔ native 번호, 올카드 세이브 보관·되돌리기)와 Settings 등록 시험(호스트 JVM).
 *  실행: javac -cp json.jar -d out stub/com/dudu/pocketcore/*.java <앱>/Settings.java <앱>/Cheats.java CheatsTest.java
 *        && java -Dcheat.root=<빈 폴더> -cp out:json.jar com.dudu.pocketcore.CheatsTest */
public class CheatsTest {
    static int fails = 0, passes = 0;
    static void ok(boolean c, String what) { System.out.println((c ? "PASS " : "FAIL ") + what); if (c) passes++; else fails++; }
    static byte[] read(File f) throws Exception { try (FileInputStream in = new FileInputStream(f)) { byte[] b = new byte[(int) f.length()]; int o = 0, n; while (o < b.length && (n = in.read(b, o, b.length - o)) > 0) o += n; return b; } }
    static void write(File f, byte[] b) throws Exception { f.getParentFile().mkdirs(); try (FileOutputStream o = new FileOutputStream(f)) { o.write(b); } }
    static Map<String, String> m(String... kv) { Map<String, String> r = new HashMap<>(); for (int i = 0; i < kv.length; i += 2) r.put(kv[i], kv[i + 1]); return r; }

    public static void main(String[] a) throws Exception {
        File root = new File(System.getProperty("cheat.root")); root.mkdirs();

        // ── J-1 키·값 ↔ native 번호
        Settings.Item[] g = Settings.GROUPS.get(Cheats.GROUP);
        ok(g != null && g.length == 11, "Settings.GROUPS «치트» 11줄(마스터 + 10)");
        boolean keysOk = g[0].key.equals("pocketcore_ss2_cheat") && "enabled".equals(g[0].def);
        for (int i = 0; i < 10; i++) keysOk &= g[i + 1].key.equals("pocketcore_ss2_cheat_" + Cheats.KEYS[i]) && g[i + 1].def.equals(g[i + 1].vals[0]);
        ok(keysOk, "키 = pocketcore_ss2_cheat_<native CH_* 순서> · 마스터 기본 켬 · 하나하나 기본 = 첫 값(끔)");
        boolean scope = true; for (Settings.Item it : g) scope &= "ss2".equals(it.game) && !it.launch && it.feature == null && it.vals.length == it.names.length;
        ok(scope, "모두 사무쇼2 전용(.g) · 실행 창 본문에 안 낌(.l() 없음) · 값·이름 수 같음");
        int[] MAXV = { 2, 1, 2, 2, 1, 1, 1, 5, 3, 2 };   // cheat.c cheat_set
        boolean nOk = true; for (int i = 0; i < 10; i++) nOk &= g[i + 1].vals.length == MAXV[i] + 1;
        ok(nOk, "값 수 = native 범위(cheat_set MAXV + 1)");
        ok(Arrays.asList(g[1].vals).equals(Arrays.asList("off", "temp", "save")) && "세이브에 남기기".equals(g[1].names[2]) && "이번만".equals(g[1].names[1]),
           "올카드 값 off·temp·save = 끔·이번만·세이브에 남기기");
        boolean inPages = false; for (Settings.Page p : Settings.PAGES) for (String sct : p.sections) inPages |= Cheats.GROUP.equals(sct);
        for (Settings.Page p : Settings.SUBPAGES) for (String sct : p.sections) inPages |= Cheats.GROUP.equals(sct);
        ok(!inPages, "설정 화면 쪽(PAGES)엔 없음 — 확인 창·세이브 보관을 건너뛰지 않게 치트 창에서만");

        ok(Arrays.equals(Cheats.values(m()), new int[10]) && Cheats.count(m()) == 0 && !Cheats.any(m()), "빈 options: 모두 0 · 켜진 수 0");
        Map<String, String> on = m("pocketcore_ss2_cheat_cards", "save", "pocketcore_ss2_cheat_time", "inf", "pocketcore_ss2_cheat_hp1", "one",
                "pocketcore_ss2_cheat_hp2", "inf", "pocketcore_ss2_cheat_rage1", "max", "pocketcore_ss2_cheat_cpu", "idle",
                "pocketcore_ss2_cheat_diff", "max", "pocketcore_ss2_cheat_pow", "1.5", "pocketcore_ss2_cheat_yuga", "rasetsu");
        ok(Arrays.equals(Cheats.values(on), new int[]{ 2, 1, 2, 1, 1, 0, 1, 5, 1, 2 }) && Cheats.count(on) == 9, "값 이름 → native 번호(cards save 2 · diff max 5 · pow 1.5 → 1 · yuga 나찰 2) · 켜진 수 9");
        on.put("pocketcore_ss2_cheat", "disabled");
        ok(Arrays.equals(Cheats.values(on), new int[10]) && Cheats.count(on) == 0 && !Cheats.fight(on), "마스터 끔: 모두 0(고른 값은 options 에 그대로)");
        on.put("pocketcore_ss2_cheat", "enabled");
        ok(Cheats.count(on) == 9, "마스터 다시 켬: 고른 값 그대로 9개");
        ok(Arrays.equals(Cheats.values(m("pocketcore_ss2_cheat_diff", "bogus", "pocketcore_ss2_cheat_pow", "")), new int[10]), "모르는 값·빈 값 → 0(기본 끔)");
        ok(!Cheats.fight(m("pocketcore_ss2_cheat_cards", "temp", "pocketcore_ss2_cheat_yuga", "shura")) && Cheats.fight(m("pocketcore_ss2_cheat_pow", "3"))
           && Cheats.fight(m("pocketcore_ss2_cheat_time", "inf")), "경기 치트 = 시간~공격력(올카드·유가는 아님)");
        boolean getOk = true;
        for (int i = 0; i < 10; i++) { Settings.Item it = g[i + 1]; getOk &= it.indexOf(Settings.get(on, it)) == Cheats.values(on)[i]; }
        ok(getOk, "Settings.get/indexOf(창에 보이는 값)과 Cheats.values(native 값)이 같은 자리");
        Emu.calls = 0; Arrays.fill(Emu.cheat, -1);
        Cheats.push(on);
        ok(Emu.calls == 10 && Emu.cheat[0] == 2 && Emu.cheat[7] == 5 && Emu.cheat[9] == 2 && Emu.cheat[5] == 0, "push: native 에 10개(CH_* 순서)");
        on.put("pocketcore_ss2_cheat", "disabled"); Cheats.push(on);
        boolean zero = true; for (int i = 0; i < 10; i++) zero &= Emu.cheat[i] == 0;
        ok(zero, "마스터 끔 push: 모두 0");
        ok(Settings.retired("ss2_allcards", "") && Settings.retired("ss2_lightrecover", ""), "옛 조작 패치 ss2_allcards 은퇴(치트 올카드가 대신)");

        // options.txt 로 왕복 — Settings.put 으로 쓴 값을 load → values
        Settings.put("pocketcore_ss2_cheat_cards", "temp"); Settings.put("pocketcore_ss2_cheat_hp2", "one");
        ok(Cheats.values(Settings.load())[0] == 1 && Cheats.values(Settings.load())[3] == 2 && Cheats.count(Settings.load()) == 2, "options.txt 왕복(Settings.put → load → values)");

        // ── J-2 세이브 보관·되돌리기
        File sd = new File(root, "saves"); sd.mkdirs();
        String rom = "/sdcard/PocketCore/roms/ss2.ngc";
        File fl = new File(sd, "ss2.flash"), bk = new File(sd, "ss2.flash.cheatbak");
        ok(Cheats.flash(sd, rom).equals(fl) && Cheats.backup(sd, rom).equals(bk) && Cheats.flash(sd, "/x/.patched/ss2.ngc").equals(fl),
           "이름: <롬 이름(확장자 뺌)>.flash · .flash.cheatbak — 사본(.patched)도 같은 이름");
        byte[] orig = "FLASH-ORIGINAL".getBytes("UTF-8");
        write(fl, orig);
        ok(Cheats.backupFlash(sd, rom) && Arrays.equals(read(bk), orig) && Cheats.hasBackup(sd, rom), "보관: .flash → .cheatbak(같은 바이트)");
        write(fl, "FLASH-ALLCARDS".getBytes("UTF-8"));
        ok(Cheats.backupFlash(sd, rom) && Arrays.equals(read(bk), orig), "두 번 켜도 처음 보관본 그대로(올카드 뒤 세이브로 안 덮음)");
        File auto = new File(sd, "ss2.ngc.state.auto"), autoP = new File(sd, "ss2.ngc.state.auto.prac");
        write(auto, "STATE".getBytes("UTF-8")); write(autoP, "PRAC".getBytes("UTF-8"));
        ok(Cheats.restoreFlash(sd, rom) && Arrays.equals(read(fl), orig) && !bk.exists(), "되돌리기: .flash = 보관본 · 보관본 지움");
        ok(!auto.exists() && !autoP.exists() && new File(sd, "ss2.ngc.state.auto.cheat").exists() && new File(sd, "ss2.ngc.state.auto.cheat.prac").exists(),
           "오토세이브(+.prac)는 .state.auto.cheat 로 비킴(상태 파일이 플래시를 싣고 다님)");
        ok(!Cheats.restoreFlash(sd, rom) && !Cheats.hasBackup(sd, rom), "보관본이 없으면 되돌리기 안 함");
        fl.delete();
        ok(Cheats.backupFlash(sd, rom) && bk.exists() && bk.length() == 0, ".flash 가 없던 사람: 빈 보관본(= 없었음)");
        write(fl, "FLASH-AFTER".getBytes("UTF-8"));
        ok(Cheats.restoreFlash(sd, rom) && !fl.exists() && !bk.exists(), "빈 보관본으로 되돌리기 = .flash 지움(롬 안 세이브로)");
        ok(!new File(sd, "ss2.flash.cheatbak.tmp").exists() && !new File(sd, "ss2.flash.tmp").exists(), "임시 파일 안 남음");

        System.out.println("== CheatsTest: " + passes + " PASS, " + fails + " FAIL");
        System.exit(fails == 0 ? 0 : 1);
    }
}

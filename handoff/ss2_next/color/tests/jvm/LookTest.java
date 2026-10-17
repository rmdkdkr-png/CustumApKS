package com.dudu.pocketcore;
import org.json.*; import java.io.*; import java.lang.reflect.Field; import java.util.*;
/** Look.java(모든 모드 컬러 앱 쪽) 시험 — 옛 기록 이름 · 기억 글자 왕복 · 옛 리그 «내 컬러» 옮기기 · 내 색 JSON 왕복 · push · 경기 기록 look.cv/tri.
 *  실행: run_jvm.sh (javac -cp json.jar stub/… League.java Look.java LookTest.java → java -Dleague.root=<빈 폴더> … LookTest) */
public class LookTest {
    static int fails = 0;
    static void ok(boolean c, String what) { System.out.println((c ? "PASS " : "FAIL ") + what); if (!c) fails++; }
    static void restart() throws Exception { Field f = League.class.getDeclaredField("db"); f.setAccessible(true); f.set(null, null); }
    static String raw(File f) throws Exception { try (FileInputStream in = new FileInputStream(f)) { byte[] b = new byte[(int) f.length()]; int off = 0, n; while (off < b.length && (n = in.read(b, off, b.length - off)) > 0) off += n; return new String(b, "UTF-8"); } }

    public static void main(String[] a) throws Exception {
        File root = new File(System.getProperty("league.root"));
        File lj = new File(new File(root, "league"), "league.json");

        // ── 이름
        ok(Look.NAMES.length == 18 && Look.NAMES[2].equals("쪽빛") && Look.NAMES[13].equals("그림자") && Look.NAMES[17].equals("내 색 2"), "이름 18개(기본 · 2P색 · 쪽빛 … 그림자 … 내 색 2)");
        ok(Look.name(2, 0).equals("컬러 3") && Look.name(3, 1).equals("컬러 4") && Look.name(1, 0).equals("2P색") && Look.name(9, 0).equals("기본"),
           "cv 없는 옛 기록: 2·3 = 컬러 3·4, 범위 밖 = 기본");
        ok(Look.name(2, 2).equals("쪽빛") && Look.name(16, 2).equals("내 색 1") && Look.name(99, 2).equals("기본"), "cv 2: 2 = 쪽빛 · 16 = 내 색 1 · 범위 밖 = 기본");
        ok(League.COLORS == Look.NAMES, "League.COLORS = Look.NAMES (넓힌 컬러 이름 하나로)");

        // ── 기억 글자
        byte[] m = new byte[16]; m[0] = 9; m[11] = 16; m[15] = 13;
        String s = Look.fmtMem(m);
        ok(s.equals("9,0,0,0,0,0,0,0,0,0,0,16,0,0,0,13") && Arrays.equals(Look.parseMem(s), m), "기억 16칸 글자 왕복 «" + s + "»");
        ok(Look.parseMem("1,2,3") == null && Look.parseMem(null) == null && Look.parseMem("a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p") == null, "깨진 기억 글자 = null(처음처럼 옮기기)");
        ok(Look.parseMem("99,-1,5,0,0,0,0,0,0,0,0,0,0,0,0,0")[0] == 0 && Look.parseMem("99,-1,5,0,0,0,0,0,0,0,0,0,0,0,0,0")[1] == 0
           && Look.parseMem("99,-1,5,0,0,0,0,0,0,0,0,0,0,0,0,0")[2] == 5, "범위 밖 값(99·−1)은 0");

        // ── 옛 리그 «내 컬러» 옮기기 — 리그 기록이 없으면 파일을 안 만든다
        ok(!lj.exists(), "(시작) 리그 기록 파일 없음");
        byte[] m0 = Look.loadMem();
        ok(m0.length == 16 && allEq(m0, 0) && !lj.exists() && "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0".equals(Settings.load().get(Look.K_MEM)),
           "리그를 안 써 본 사람: 16칸 모두 기본 · 앱 설정에 남김 · 리그 기록 파일은 안 만듦");
        new File(root, "options.txt").delete();
        League.setPrefLook(-1, 2); restart();                           // 옛 앱이 남긴 pref.color = 2(컬러 3)
        ok(League.prefColor() == 2, "옛 pref.color 2");
        byte[] m1 = Look.loadMem();
        ok(allEq(m1, 2) && Look.NAMES[m1[5]].equals("비취") == false && Look.NAMES[m1[5]].equals("쪽빛"), "옛 «컬러 3»(2) → 16칸 모두 2 = 쪽빛");
        League.setPrefLook(-1, 3); restart();
        ok(allEq(Look.loadMem(), 2), "한 번 옮긴 뒤엔 pref.color 가 바뀌어도 앱 설정 값 그대로(다시 안 옮김)");
        League.setPrefStage(5); restart();
        ok(League.prefStage() == 5 && League.prefColor() == 3, "setPrefStage 는 배경만 — pref.color 는 안 건드림");
        League.setPrefLook(-1, 12); restart();
        ok(League.prefColor() == 12, "prefColor 넓힘: 0~17 (예전 & 3 없음) — 12 그대로");
        League.setPrefLook(-1, 0);
        byte[] m2 = Look.loadMem(); m2[11] = 9; Look.saveMem(m2);
        ok(Look.loadMem()[11] == 9 && Settings.load().get(Look.K_MEM).startsWith("2,2,2,2,2,2,2,2,2,2,2,9,"), "saveMem → 우쿄 칸만 황금(9)");

        // ── 내 색 JSON
        ok(Look.loadCustom()[11][0] == null && Look.loadCustom()[11][1] == null, "처음 내 색 없음");
        Look.saveCustom(11, 0, new int[] { 3039, 744, 65 });
        int[][][] c = Look.loadCustom();
        String js = Settings.load().get(Look.K_CUS);
        ok(c[11][0] != null && c[11][0][0] == 3039 && c[11][0][1] == 744 && c[11][0][2] == 65 && c[11][1] == null && c[4][0] == null,
           "내 색 1(우쿄) 저장 → 다시 읽어도 같은 세 색 · 내 색 2 없음");
        ok(js != null && new JSONObject(js).optInt("v") == 1 && new JSONObject(js).getJSONObject("c").getJSONArray("11").isNull(1)
           && new JSONObject(js).getJSONObject("c").getJSONArray("11").getJSONArray(0).getInt(0) == 3039, "앱 설정 JSON {\"v\":1,\"c\":{\"11\":[[3039,744,65],null]}} — " + js);
        Look.saveCustom(11, 1, new int[] { 0x1FFF, 0, 0xF0F });
        ok(Look.loadCustom()[11][1][0] == 0xFFF, "12비트로 자름(0x1FFF → 0xFFF)");
        Look.saveCustom(11, 0, null);
        ok(Look.loadCustom()[11][0] == null && Look.loadCustom()[11][1] != null, "내 색 1 지움 — 내 색 2 는 그대로");
        ok(Look.parseCus("{깨짐")[0][0] == null && Look.parseCus(null)[13][1] == null && Look.parseCus("{\"v\":1,\"c\":{\"99\":[[1,2,3]],\"x\":[]}}")[0][0] == null,
           "깨진 JSON·없는 캐릭터 번호는 무시");

        // ── push: native 에 기억 + 28칸(14명 × 2) 모두
        Look.saveCustom(2, 0, new int[] { 1, 2, 3 });
        Emu.cus[2][1] = new int[] { 9, 9, 9 };
        Look.push();
        ok(Emu.mem != null && Emu.mem[11] == 9 && Emu.cus[2][0] != null && Emu.cus[2][0][2] == 3 && Emu.cus[2][1] == null && Emu.cus[11][1] != null,
           "push: 기억 16칸 · 내 색 있는 칸은 세 색, 없는 칸은 지움(−1)");

        // ── 도움 셈
        ok(Look.argb(0x00F) == 0xffff0000 && Look.argb(0xF00) == 0xff0000ff && Look.argb(0x0F0) == 0xff00ff00 && Look.argb(0x888) == 0xff888888, "0x0BGR → 안드로이드 색");
        ok(Look.tooClose(new int[] { 0x111, 0x112, 0x121 }) && !Look.tooClose(new int[] { 0xBDF, 0xE60, 0x500 }), "세 색이 너무 비슷한지(채널 차 합 < 6)");

        // ── 경기 기록 look.cv/tri
        JSONObject mt = League.newMatch("o05"); String id = mt.optString("id");
        League.setLook(id, 3, 16, new int[] { 3039, 744, 65 }); restart();
        JSONObject lk = League.matchById(id).optJSONObject("look");
        ok(lk != null && lk.optInt("stage") == 3 && lk.optInt("color") == 16 && lk.optInt("cv") == 2 && lk.optJSONArray("tri") != null
           && lk.optJSONArray("tri").optInt(0) == 3039, "경기 기록: 내 색이면 {stage, color 16, cv 2, tri [3039,744,65]} — 재시작 뒤 그대로");
        League.setLook(id, 3, 9, new int[] { 1, 2, 3 }); restart();
        lk = League.matchById(id).optJSONObject("look");
        ok(lk.optInt("color") == 9 && lk.optInt("cv") == 2 && lk.optJSONArray("tri") == null, "프리셋이면 tri 없음(cv 2)");
        League.setLook(id, 3, 9); restart();
        ok(League.matchById(id).optJSONObject("look").optInt("cv") == 2, "옛 3인자 setLook 도 cv 2 로 남김");
        League.cancel(id, "시험"); League.setLook(id, 0, 0);
        ok(League.matchById(id).optJSONObject("look").optInt("color") == 9, "끝난 경기는 안 바뀜");

        System.out.println(fails == 0 ? "ALL PASS" : fails + " FAIL");
        System.exit(fails == 0 ? 0 : 1);
    }
    static boolean allEq(byte[] m, int v) { for (byte b : m) if (b != v) return false; return true; }
}

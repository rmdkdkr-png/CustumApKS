package com.dudu.pocketcore;
import java.io.*; import java.util.*;
/** FrameMeterText 숫자 줄 시험(호스트 JVM). 실제 sum 은 호스트 시험 t_framedata.py 가 남긴 fd_sums_<롬>.txt(이름|정수 40개).
 *  실행: javac -d out FrameMeterText.java FrameMeterTest.java && java -cp out com.dudu.pocketcore.FrameMeterTest <fd_sums.txt> */
public class FrameMeterTest {
    static int fails = 0;
    static void ok(boolean c, String what) { System.out.println((c ? "PASS " : "FAIL ") + what); if (!c) fails++; }
    static int[] blank() { int[] s = new int[FrameMeterText.NSUM]; s[FrameMeterText.S_FOCUS] = -1; s[FrameMeterText.S_ADV] = FrameMeterText.NONE; s[FrameMeterText.S_ADV_ATT] = -1;
        for (int b : new int[] { FrameMeterText.S_P1, FrameMeterText.S_P2 }) for (int k = 10; k < 14; k++) s[b + k] = FrameMeterText.NONE; return s; }
    public static void main(String[] a) throws Exception {
        Map<String, int[]> m = new LinkedHashMap<>();
        try (BufferedReader r = new BufferedReader(new InputStreamReader(new FileInputStream(a[0]), "UTF-8"))) {
            for (String ln; (ln = r.readLine()) != null; ) {
                String[] p = ln.split("\\|"); String[] n = p[1].trim().split(" "); int[] s = new int[n.length];
                for (int i = 0; i < n.length; i++) s[i] = Integer.parseInt(n[i]);
                m.put(p[0], s);
            }
        }
        String[][] want = {
            { "5A 헛침", "발동 7F · 지속 6F · 경직 14F" },
            { "5A 히트", "발동 7F · 히트 -2" },
            { "5A 가드", "발동 7F · 가드 -6" },
            { "5A+ 히트", "발동 9F · 히트 -8" },
            { "2A+ 다운", "발동 9F · 다운 +120" },
            { "236A 가드", "발동 11F · 장풍 · 가드 -20" },
            { "잡기", "발동 3F · 잡기 +26" },
            { "↓B 튕겨내기", "튕겨내기 5F · 지속 16F · 전체 52F" },
            { "점프 A", "발동 7F · 지속 16F · 경직 6F" },
        };
        for (String[] w : want) {
            int[] s = m.get(w[0]);
            String got = s == null ? null : FrameMeterText.line(s);
            ok(w[1].equals(got), "실제 sum «" + w[0] + "» → «" + got + "»");
        }
        /* 기억: 같은 기술의 히트·가드가 다 보이고 방금 것만 밝게 */
        int[] s = blank();
        int b = FrameMeterText.S_P1;
        s[FrameMeterText.S_FOCUS] = 0; s[b] = 3; s[b + 1] = 7; s[b + 2] = 11; s[b + 3] = 14; s[b + 4] = 31; s[b + 5] = FrameMeterText.C_HIT;
        s[b + 8] = 6; s[b + 9] = 14; s[b + 10] = -2; s[b + 12] = -6;
        s[FrameMeterText.S_ADV] = -2; s[FrameMeterText.S_ADV_KIND] = FrameMeterText.C_HIT; s[FrameMeterText.S_ADV_ATT] = 0; s[FrameMeterText.S_ADV_ID] = 4;
        ok("발동 7F · 지속 6F · 경직 14F · 히트 -2 · 가드 -6".equals(FrameMeterText.line(s)), "기억(헛친 지속·경직 + 히트·가드 유불리): " + FrameMeterText.line(s));
        FrameMeterText.Part[] ps = FrameMeterText.parts(s);
        ok(ps.length == 4 && ps[2].now && !ps[3].now && ps[2].sign < 0, "방금 닿은 «히트»만 밝게 · 부호 색(불리)");
        /* 상대 기술을 막음 — 내 쪽 유불리 */
        s = blank(); b = FrameMeterText.S_P2;
        s[FrameMeterText.S_FOCUS] = 1; s[b] = 1; s[b + 1] = 5; s[b + 2] = 6; s[b + 3] = 14; s[b + 4] = 24; s[b + 5] = FrameMeterText.C_BLOCK; s[b + 8] = -1; s[b + 9] = -1;
        s[FrameMeterText.S_ADV] = 6; s[FrameMeterText.S_ADV_KIND] = FrameMeterText.C_BLOCK; s[FrameMeterText.S_ADV_ATT] = 1; s[FrameMeterText.S_ADV_ID] = 1;
        ok("상대 발동 5F · 막음 +6".equals(FrameMeterText.line(s)), "상대 기술 막음: " + FrameMeterText.line(s));
        ok("±0".equals(FrameMeterText.signed(0)) && "-4".equals(FrameMeterText.signed(-4)) && "+2".equals(FrameMeterText.signed(2)), "부호: ±0 · -4 · +2 (U+2212 안 씀)");
        ok(FrameMeterText.parts(blank()).length == 0, "아직 동작 없음 → 빈 줄(안내 글)");
        boolean noMinusSign = true;
        for (int[] v : m.values()) if (FrameMeterText.line(v).indexOf('−') >= 0) noMinusSign = false;
        ok(noMinusSign, "숫자 줄에 U+2212 없음(갈무리11 에 없는 글자)");
        System.out.println("FAILS " + fails);
        if (fails > 0) System.exit(1);
    }
}

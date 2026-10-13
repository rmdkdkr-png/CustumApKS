package com.dudu.pocketcore;
import org.json.*; import java.io.*; import java.lang.reflect.Field;
public class LeagueTest {
    static int fails = 0;
    static void ok(boolean c, String what) { System.out.println((c ? "PASS " : "FAIL ") + what); if (!c) fails++; }
    static void restart() throws Exception { Field f = League.class.getDeclaredField("db"); f.setAccessible(true); f.set(null, null); }
    static int[] st(int bits, int w1, int w2, int p2) { return new int[]{1,5000,1,1,1,bits,w1,w2,0x88,2,0x80,p2,p2,3000,5000,0x80,0x81}; }
    public static void main(String[] a) throws Exception {
        File root = new File(System.getProperty("league.root"));
        ok(League.me().optInt("score") == 1000 && League.opps().length() == 1, "새 기록: 나 1000, 상대 1명");
        // 1) 시작 전 영속 저장
        JSONObject m = League.newMatch("o01"); String id = m.optString("id");
        restart();
        ok("ready".equals(League.matchById(id).optString("status")), "경기 id·설정이 시작 전에 파일에 저장됨(재시작 뒤에도 ready)");
        // 2) 승리 정산
        JSONObject r = League.settle(id, st(0xC0, 2, 1, 0xB0));
        ok(r != null && "settled".equals(r.optString("status")) && r.optInt("delta") == 12, "승리 2:1 정산, +12");
        ok(League.me().optInt("score") == 1012 && League.oppById("o01").optInt("score") == 988, "점수 1012 / 상대 988 (반대로)");
        // 3) 같은 결과 다시 → 한 번만
        League.settle(id, st(0xC0, 2, 1, 0xB0)); League.settle(id, st(0xA0, 0, 2, 0xB0));
        ok(League.me().optInt("score") == 1012 && League.me().optInt("w") == 1, "같은 경기 결과를 반복 전달해도 점수는 한 번만");
        // 4) 재시작 후 유지·중복 없음
        restart();
        ok(League.me().optInt("score") == 1012 && League.me().optInt("w") == 1 && League.me().optInt("streak") == 1, "재시작 후에도 동일한 기록");
        League.settle(id, st(0xC0, 2, 1, 0xB0));
        ok(League.me().optInt("w") == 1, "재시작 후 같은 결과 재전달 — 중복 없음");
        // 5) 대진 불일치 → 보류, 점수 그대로
        String id2 = League.newMatch("o01").optString("id");
        JSONObject h = League.settle(id2, st(0xC0, 2, 0, 0x30));
        ok(h != null && "hold".equals(h.optString("status")) && League.me().optInt("score") == 1012, "대진 준비 실패(P2 겐주로) → 보류, 점수 반영 안 함");
        // 6) 무승부 경기
        String id3 = League.newMatch("o01").optString("id");
        JSONObject d = League.settle(id3, st(0x90, 3, 3, 0xB0));
        ok(d != null && "D".equals(d.optString("outcome")) && d.optInt("delta") == 0 && League.me().optInt("d") == 1 && League.me().optInt("score") == 1012, "무승부(0x90 3:3) — 점수 유지, 무승부 전적만");
        // 7) 기권
        String id4 = League.newMatch("o01").optString("id");
        JSONObject f = League.forfeit(id4);
        ok(f != null && "forfeit".equals(f.optString("status")) && f.optInt("delta") == -12 && League.me().optInt("score") == 1000 && League.me().optInt("streak") == 0 && f.optInt("broke_streak") == 1, "기권패 −12, 연승 끊김 기록");
        ok(League.forfeit(id4).optInt("delta") == -12 && League.me().optInt("l") == 1, "기권 두 번 눌러도 한 번만");
        // 8) 저장 실패 → 메모리 되돌림 → 다시 시도하면 한 번만
        String id5 = League.newMatch("o01").optString("id");
        File dir = new File(root, "league"); File blocker = new File(dir, "league.json.tmp"); blocker.mkdir(); new File(blocker, "x").createNewFile();   // root 는 권한을 무시하므로 임시 파일 자리를 폴더로 막는다
        JSONObject bad = League.settle(id5, st(0x60 | 0x80, 2, 0, 0xB0));
        boolean failed = bad == null && League.me().optInt("score") == 1000 && !"settled".equals(League.matchById(id5).optString("status"));
        new File(blocker, "x").delete(); blocker.delete();
        ok(failed, "저장 실패 시 정산을 되돌림(점수·상태 그대로)");
        JSONObject good = League.settle(id5, st(0xC0, 2, 0, 0xB0));
        ok(good != null && League.me().optInt("score") == 1012 && League.me().optInt("w") == 2, "재시도에서 정확히 한 번 정산");
        // 9) 파일이 깨지면 직전 판(.bak)
        try (FileOutputStream o = new FileOutputStream(new File(dir, "league.json"))) { o.write("{깨짐".getBytes("UTF-8")); }
        restart();
        ok(League.me() != null && League.me().optInt("w") == 2 && League.me().optInt("score") == 1012, "league.json 이 깨져도 .bak 에서 최신 기록 그대로 복구 (w=" + League.me().optInt("w") + ")");
        // 10) 점수 구간
        ok(League.delta(1000, 1101, "W") == 18 && League.delta(1000, 1101, "L") == -6 && League.delta(1000, 1100, "W") == 12
           && League.delta(1000, 899, "W") == 6 && League.delta(1000, 899, "L") == -18 && League.delta(1000, 900, "L") == -12, "점수 구간 표(±100 경계 포함)");
        System.out.println(fails == 0 ? "ALL PASS" : fails + " FAIL");
        System.exit(fails == 0 ? 0 : 1);
    }
}

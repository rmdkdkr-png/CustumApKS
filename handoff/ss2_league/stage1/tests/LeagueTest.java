package com.dudu.pocketcore;
import org.json.*; import java.io.*; import java.lang.reflect.Field;
/** League.java 정산·저장 규칙 시험(호스트 JVM). 실행: javac -cp json.jar … && java -Dleague.root=<빈 폴더> -cp out:json.jar com.dudu.pocketcore.LeagueTest */
public class LeagueTest {
    static int fails = 0;
    static void ok(boolean c, String what) { System.out.println((c ? "PASS " : "FAIL ") + what); if (!c) fails++; }
    static void restart() throws Exception { Field f = League.class.getDeclaredField("db"); f.setAccessible(true); f.set(null, null); }
    /* league_status 18칸: [무장,프레임,bit7 0 봄,시작 봄,결과,비트,승1,승2,KO,실효포인트,P1,P2,P2시작,시작프레임,결판프레임,카드1,카드2,실효시간] */
    static int[] st(int bits, int w1, int w2, int p2, int need, int time) { return new int[]{1,5000,1,1,1,bits,w1,w2,0x88,need,0x80,p2,p2,3000,5000,0x80,0x81,time,4,0x00D9,0x0126}; }
    static int[] st(int bits, int w1, int w2, int p2) { return st(bits, w1, w2, p2, 2, 60); }
    static File touchCk(String id) throws Exception { File f = League.ckpt(id); try (FileOutputStream o = new FileOutputStream(f)) { o.write(1); } return f; }
    public static void main(String[] a) throws Exception {
        File root = new File(System.getProperty("league.root"));
        ok(League.me().optInt("score") == 1000 && League.opps().length() == 1 && League.rankOf("me") == 1, "새 기록: 나 1000·1위, 상대 1명");
        // 1) 시작 전 영속 + 열린 경기 있으면 새 경기 안 됨
        JSONObject m = League.newMatch("o01"); String id = m.optString("id");
        ok(League.newMatch("o01") == null, "열린 경기가 있으면 새 경기를 만들지 않음");
        restart();
        ok("ready".equals(League.matchById(id).optString("status")) && League.matchById(id).optJSONObject("start_score").optInt("me") == 1000,
           "경기 id·설정·시작 점수가 시작 전에 파일에 저장됨(재시작 뒤 ready)");
        // 2) 패배 정산 → 988/1012, 순위 2위
        League.setStatus(id, "playing", null);
        JSONObject r = League.settle(id, st(0xA0, 0, 2, 0xB0));
        ok(r != null && "settled".equals(r.optString("status")) && r.optInt("delta") == -12 && r.optInt("rank_before") == 1 && r.optInt("rank_after") == 2,
           "패배 0:2 정산 −12, 순위 1위 → 2위");
        // 3) 끝난 경기는 상태가 안 바뀜 · 반복 정산·기권 무시
        ok(!League.setStatus(id, "resume", "x") && "settled".equals(League.matchById(id).optString("status")), "정산 완료 경기는 다른 상태로 못 바꿈");
        League.settle(id, st(0xC0, 2, 0, 0xB0)); League.forfeit(id);
        ok(League.me().optInt("score") == 988 && League.me().optInt("l") == 1 && League.me().optInt("w") == 0, "같은 경기 반복 정산·기권 — 한 번만");
        // 4) 이기면 1000:1000 동점 — 기존 순서(상대 1위) 유지
        String id2 = League.newMatch("o01").optString("id");
        JSONObject w = League.settle(id2, st(0xC0, 2, 1, 0xB0));
        ok(w != null && League.me().optInt("score") == 1000 && League.oppById("o01").optInt("score") == 1000 && League.rankOf("me") == 2 && w.optInt("rank_after") == 2,
           "동점 1000:1000 — 직전 순위 유지(상대 1위, 나 2위)");
        restart();
        ok(League.rankOf("me") == 2 && League.me().optInt("streak") == 1, "재시작 후에도 같은 순위·연승");
        // 5) 대진 불일치·규칙 불일치 → 보류, 점수 그대로, 원인·복구 기록
        String id3 = League.newMatch("o01").optString("id"); File ck3 = touchCk(id3);
        JSONObject h = League.settle(id3, st(0xC0, 2, 0, 0x30));
        ok(h != null && "hold".equals(h.optString("status")) && h.has("fix") && League.me().optInt("score") == 1000 && !ck3.exists(), "대진 불일치(P2 겐쥬로) → 보류·복구 안내, 점수 그대로, 체크포인트 정리");
        String id4 = League.newMatch("o01").optString("id");
        JSONObject h2 = League.settle(id4, st(0xC0, 1, 0, 0xB0, 1, 128));
        ok(h2 != null && "hold".equals(h2.optString("status")) && h2.optString("why").contains("규칙 불일치") && League.me().optInt("w") == 1, "무한 대전식 1라운드 결판(실효 포인트 1·시간 128) → 보류");
        // 6) 무승부
        String id5 = League.newMatch("o01").optString("id");
        JSONObject d = League.settle(id5, st(0x90, 3, 3, 0xB0));
        ok(d != null && "D".equals(d.optString("outcome")) && d.optInt("delta") == 0 && League.me().optInt("d") == 1 && League.me().optInt("score") == 1000, "무승부(0x90 3:3) — 점수 유지, 무승부 전적만");
        // 7) 준비 상태 경기는 무효로 닫기(점수 없음), 진행 중 경기는 무효로 못 닫음
        String id6 = League.newMatch("o01").optString("id");
        ok(League.cancel(id6, "대진 전") && "cancelled".equals(League.matchById(id6).optString("status")) && League.me().optInt("score") == 1000 && League.openMatch() == null, "대진 전(준비) 경기 무효 — 점수 그대로");
        String id7 = League.newMatch("o01").optString("id"); League.setStatus(id7, "playing", null);
        ok(!League.cancel(id7, "x"), "시작한 경기는 무효로 못 닫음");
        // 8) 기권: 저장 실패면 체크포인트 남김 → 재시도 1번
        File ck7 = touchCk(id7);
        File dir = new File(root, "league"); File blocker = new File(dir, "league.json.tmp"); blocker.mkdir(); new File(blocker, "x").createNewFile();
        JSONObject bad = League.forfeit(id7);
        boolean keep = bad == null && ck7.exists() && "playing".equals(League.matchById(id7).optString("status")) && League.me().optInt("score") == 1000;
        new File(blocker, "x").delete(); blocker.delete();
        ok(keep, "기권 저장 실패 → 메모리 되돌림, 체크포인트 남김(재개 가능)");
        JSONObject f = League.forfeit(id7);
        ok(f != null && "forfeit".equals(f.optString("status")) && f.optInt("delta") == -12 && !ck7.exists() && League.me().optInt("streak") == 0 && f.optInt("broke_streak") == 1,
           "기권 재시도에서 한 번 −12, 연승 끊김, 체크포인트 정리");
        // 9) 정산 저장 실패 → 되돌림 → 재시도 1번
        String id8 = League.newMatch("o01").optString("id");
        blocker.mkdir(); new File(blocker, "x").createNewFile();
        JSONObject bad2 = League.settle(id8, st(0xC0, 2, 0, 0xB0));
        boolean failed = bad2 == null && League.me().optInt("score") == 988 && !"settled".equals(League.matchById(id8).optString("status"));
        new File(blocker, "x").delete(); blocker.delete();
        ok(failed, "정산 저장 실패 시 되돌림(점수·상태 그대로)");
        ok(League.setStatus(id8, "playing", null), "되돌린 뒤에도 id 로 찾아 상태를 바꿀 수 있음(옛 객체 아님)");
        JSONObject good = League.settle(id8, st(0xC0, 2, 0, 0xB0));
        ok(good != null && League.me().optInt("w") == 2 && League.me().optInt("score") == 1000, "재시도에서 정확히 한 번 정산");
        // 10) 시작 때 점수로 구간 고정
        String id9 = League.newMatch("o01").optString("id");
        League.me().put("score", 1300);                               // 시작 뒤 점수가 바뀌어도(가정)
        JSONObject fx = League.settle(id9, st(0xC0, 2, 0, 0xB0));
        ok(fx != null && fx.optInt("delta") == 12, "구간은 시작 때 두 점수(1000:1000)로 고정 — 정산 때 1300 이어도 +12");
        // 11) 파일이 깨지면 .bak
        int wNow = League.me().optInt("w");
        try (FileOutputStream o = new FileOutputStream(new File(dir, "league.json"))) { o.write("{깨짐".getBytes("UTF-8")); }
        restart();
        ok(League.me() != null && League.me().optInt("w") == wNow, "league.json 이 깨져도 .bak 에서 최신 기록 그대로 복구");
        // 12) 앱이 경기 중에 내려간 경기 → 리그 화면에서 복귀 대기, 지난 사유는 지우기
        String idA = League.newMatch("o01").optString("id");
        League.setStatus(idA, "resume", "체크포인트 없음"); League.note(idA, "fix", "x");
        League.setStatus(idA, "playing", "");
        ok(!League.matchById(idA).has("why") && !League.matchById(idA).has("fix"), "진행 중으로 바꿀 때 지난 사유·복구 안내를 지움");
        League.markInterrupted();
        ok("resume".equals(League.matchById(idA).optString("status")) && League.matchById(idA).optString("why").contains("내려감"), "리그 화면을 열 때 진행 중 경기는 복귀 대기(앱이 경기 중에 내려감)");
        League.forfeit(idA);
        // 13) 싸우지 않는 CPU 대진은 지원하지 않음
        ok(!League.oppSupported(1, 0) && !League.oppSupported(12, 1) && !League.oppSupported(4, 1) && League.oppSupported(11, 0) && League.oppSupported(4, 0) && !League.oppSupported(15, 0),
           "미지원 상대(소게츠 수라·주베이 나찰·나코루루 나찰·id 15) 거르고 우쿄 수라·나코루루 수라는 허용");
        League.oppById("o01").put("char", 1); League.oppById("o01").put("style", 0);
        ok(League.newMatch("o01") == null, "미지원 상대로는 경기를 만들지 않음");
        League.oppById("o01").put("char", 11); League.oppById("o01").put("style", 0);
        // 14) 점수 구간 표
        ok(League.delta(1000, 1101, "W") == 18 && League.delta(1000, 1101, "L") == -6 && League.delta(1000, 1100, "W") == 12
           && League.delta(1000, 899, "W") == 6 && League.delta(1000, 899, "L") == -18 && League.delta(1000, 900, "L") == -12, "점수 구간 표(±100 경계 포함)");
        System.out.println(fails == 0 ? "ALL PASS" : fails + " FAIL");
        System.exit(fails == 0 ? 0 : 1);
    }
}

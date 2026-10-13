package com.dudu.pocketcore;
import org.json.*; import java.io.*; import java.lang.reflect.Field; import java.util.*;
/** League.java 2단계(가상 상대 12명) 정산·저장·순위·이어받기 시험(호스트 JVM).
 *  실행: javac -cp json.jar -d out stub/… League.java LeagueTest.java && java -Dleague.root=<빈 폴더> -cp out:json.jar com.dudu.pocketcore.LeagueTest
 *  인자 "migrate" 를 주면 1단계 기록 파일을 먼저 깔아 두고 이어받기만 따로 시험한다. */
public class LeagueTest {
    static int fails = 0;
    static void ok(boolean c, String what) { System.out.println((c ? "PASS " : "FAIL ") + what); if (!c) fails++; }
    static void restart() throws Exception { Field f = League.class.getDeclaredField("db"); f.setAccessible(true); f.set(null, null); }
    /* league_status 21칸: [무장,프레임,bit7 0 봄,시작 봄,결과,비트,승1,승2,KO,실효포인트,P1,P2,P2시작,시작프레임,결판프레임,카드1,카드2,실효시간,CPU단계,배율,배율] */
    static int[] st(int bits, int w1, int w2, int p2, int need, int time, int lv) { return new int[]{1,5000,1,1,1,bits,w1,w2,0x88,need,0x80,p2,p2,3000,5000,0x80,0x81,time,lv,0x00D9,0x0126}; }
    static int blk(String oppId) { JSONObject o = League.oppById(oppId); return (o.optInt("char") << 4) | (o.optInt("style") << 3); }
    static int lv(String oppId) { return 1 + 3 * League.oppById(oppId).optInt("diff"); }
    static int[] win(String o)  { return st(0xC0, 2, 1, blk(o), 2, 60, lv(o)); }
    static int[] lose(String o) { return st(0xA0, 0, 2, blk(o), 2, 60, lv(o)); }
    static int[] draw(String o) { return st(0x90, 3, 3, blk(o), 2, 60, lv(o)); }
    /** 경기 하나: 만들고 → 진행 중 → 정산. 정산 결과(경기). */
    static JSONObject play(String o, int[] res) { JSONObject m = League.newMatch(o); League.setStatus(m.optString("id"), "playing", ""); return League.settle(m.optString("id"), res); }
    static File touchCk(String id) throws Exception { File f = League.ckpt(id); try (FileOutputStream o = new FileOutputStream(f)) { o.write(1); } return f; }
    static String raw(File f) throws Exception { try (FileInputStream in = new FileInputStream(f)) { byte[] b = new byte[(int) f.length()]; int off = 0, n; while (off < b.length && (n = in.read(b, off, b.length - off)) > 0) off += n; return new String(b, "UTF-8"); } }

    public static void main(String[] a) throws Exception {
        File root = new File(System.getProperty("league.root"));
        File dir = new File(root, "league");
        if (a.length > 0 && "migrate".equals(a[0])) { migrate(dir); return; }

        // ── 0) 새 기록: 나 + 가상 상대 12명
        ok(League.opps().length() == 12, "새 기록: 가상 상대 12명");
        Set<String> nicks = new HashSet<>(), ids = new HashSet<>(); Set<Integer> combos = new HashSet<>();
        boolean allOk = true; int[] perDiff = new int[3];
        for (int i = 0; i < 12; i++) {
            JSONObject o = League.opps().optJSONObject(i);
            nicks.add(o.optString("nick")); ids.add(o.optString("id")); combos.add(o.optInt("char") * 2 + o.optInt("style"));
            allOk &= League.oppSupported(o.optInt("char"), o.optInt("style")) && String.format("o%02d", i + 1).equals(o.optString("id"));
            perDiff[o.optInt("diff")]++;
            int sc = o.optInt("score"), d = o.optInt("diff");
            allOk &= d == 0 ? sc >= 880 && sc <= 940 : d == 1 ? sc >= 970 && sc <= 1030 : sc >= 1060 && sc <= 1120;
        }
        ok(allOk && nicks.size() == 12 && ids.size() == 12 && combos.size() == 12, "12명 모두 지원 대진·고정 id o01~o12 순·닉네임/조합 겹침 없음·난도 구간 안의 초기 점수");
        ok(perDiff[0] == 4 && perDiff[1] == 4 && perDiff[2] == 4, "난도 쉬움·보통·어려움 4명씩");
        ok("칼끝노인".equals(League.oppById("o01").optString("nick")) && League.oppById("o01").optInt("char") == 11 && League.oppById("o01").optInt("score") == 1000,
           "o01 = 1단계와 같은 칼끝노인(우쿄 수라 보통 1000)");
        List<String> ord = League.order();
        ok(ord.size() == 13 && League.rankOf("me") == 7 && ord.indexOf("o01") == 7, "처음 순위: 13명, 나 7위, 동점 1000 은 고정 id 순(나 먼저, 칼끝노인 8위)");
        ok(new File(dir, "league.json").exists(), "새 명단이 바로 파일에 저장됨");
        restart();
        ok(League.opps().length() == 12 && League.order().equals(ord), "재시작해도 같은 명단·같은 순위");

        // ── 1) 시작 전 영속 + 열린 경기 있으면 새 경기·다른 상대 도전 안 됨
        JSONObject m = League.newMatch("o01"); String id = m.optString("id");
        ok(League.newMatch("o05") == null && League.blockedWhy(League.oppById("o05")) != null, "열린 경기가 있으면 다른 상대에게도 새 경기 안 됨 + 도전 불가 이유");
        restart();
        ok("ready".equals(League.matchById(id).optString("status")) && League.matchById(id).optJSONObject("start_score").optInt("opp") == 1000,
           "경기 id·설정·시작 점수가 시작 전에 파일에 저장됨(재시작 뒤 ready)");

        // ── 2) 패배 정산 → 988/1012, 순위 7 → 8
        League.setStatus(id, "playing", null);
        JSONObject r = League.settle(id, lose("o01"));
        ok(r != null && "settled".equals(r.optString("status")) && r.optInt("delta") == -12 && r.optInt("rank_before") == 7 && r.optInt("rank_after") == 8,
           "칼끝노인에게 패배 0:2 정산 −12, 순위 7위 → 8위");
        League.settle(id, win("o01")); League.forfeit(id);
        ok(League.me().optInt("score") == 988 && League.me().optInt("l") == 1, "같은 경기 반복 정산·기권 — 한 번만");
        ok(League.tags(League.oppById("o01")).contains("아직 못 이긴 상대"), "한 번 지고 못 이긴 상대 표시");

        // ── 3) 이기면 1000:1000 동점 — 직전 순서(칼끝노인 위) 유지 · 첫 승 표시
        JSONObject w = play("o01", win("o01"));
        ok(w != null && w.optBoolean("first_win") && League.me().optInt("score") == 1000 && League.rankOf("me") == 8 && League.rankOf("o01") == 7,
           "동점 1000:1000 — 직전 순위 유지(칼끝노인 7위, 나 8위) · 이 상대에게 첫 승");
        ok(League.tags(League.oppById("o01")).contains("처음 이긴 상대") && !League.tags(League.oppById("o01")).contains("아직 못 이긴 상대"), "처음 이긴 상대 표시, 못 이긴 상대 표시는 사라짐");
        JSONObject w2 = play("o01", win("o01"));
        ok(w2 != null && !w2.optBoolean("first_win") && !League.tags(League.oppById("o01")).contains("처음 이긴 상대"), "두 번째 승리는 첫 승 아님");

        // ── 4) 점수 구간 — 시작 때 두 점수 차이로(어려움·쉬움 상대)
        int my0 = League.me().optInt("score");                          // 1012
        JSONObject hw = play("o12", win("o12"));                         // 끝판왕 1120: 차이 108 → +18
        ok(hw != null && hw.optInt("delta") == 18 && League.me().optInt("score") == my0 + 18 && League.oppById("o12").optInt("score") == 1102,
           "101점 이상 높은 상대(끝판왕 1120)를 이기면 +18, 상대 −18");
        JSONObject el = play("o08", lose("o08"));                        // 독수리산책 880 vs 1030: −150 → −18
        ok(el != null && el.optInt("delta") == -18 && el.optInt("broke_streak") == 3 && League.oppById("o08").optInt("broke_streak") == 3,
           "101점 이상 낮은 상대에게 지면 −18 · 내 3연승을 끊음(경기·상대 둘 다 기록)");
        ok(League.tags(League.oppById("o08")).contains("내 3연승을 끊은 상대"), "연승을 끊은 상대 표시");
        ok(League.oppById("o12").optInt("l") == 1 && League.oppById("o08").optInt("w") == 1 && League.oppById("o03").optInt("w") == 0,
           "상대전적은 상대마다 따로(다른 상대 기록은 그대로)");

        // ── 5) 자주 지는 상대
        play("o05", win("o05")); play("o05", lose("o05")); play("o05", lose("o05")); play("o05", lose("o05"));
        ok(League.tags(League.oppById("o05")).contains("자주 지는 상대"), "1승 3패 상대 → 자주 지는 상대");
        ok(League.recent("o05", 3).equals("패 패 패") && League.history("o05", 10).size() == 4, "최근 결과(새것부터)와 상대별 경기 목록");

        // ── 6) 동점 순서 — 두 상대가 같은 점수가 돼도 직전 순서 유지
        List<String> before = League.order();
        JSONObject oA = League.oppById("o02"), oB = League.oppById("o09");
        int sA = oA.optInt("score"), sB = oB.optInt("score");
        boolean aAbove = before.indexOf("o02") < before.indexOf("o09");
        oA.put("score", 1050); oB.put("score", 1050);
        List<String> tie = League.order();
        ok((tie.indexOf("o02") < tie.indexOf("o09")) == aAbove, "상대끼리 동점 → 직전 순서 유지");
        oA.put("score", sA); oB.put("score", sB);

        // ── 7) 주변 순위·다음 상대
        List<String> nb = League.neighbors(2); ord = League.order(); int me = ord.indexOf("me");
        boolean nbOk = nb.size() == 4 && !nb.contains("me");
        for (String x : nb) nbOk &= Math.abs(ord.indexOf(x) - me) <= 4;
        ok(nbOk, "가까운 순위 4명(내 위·아래, 끝이면 반대쪽에서 채움)");
        String nx = League.nextOpp("o05");
        ok(nx != null && !nx.equals("o05") && !nx.equals("me") && (me == 0 || ord.indexOf(nx) < me || ord.indexOf(nx) > me), "다음 상대 추천 — 방금 상대가 아닌 바로 위(없으면 아래)");
        JSONObject meJ = League.me(); int keep = meJ.optInt("score");
        meJ.put("score", 5000);
        List<String> nbTop = League.neighbors(2);
        ok(League.rankOf("me") == 1 && nbTop.size() == 4 && League.order().subList(1, 5).equals(nbTop), "1위일 때 가까운 순위는 아래 4명");
        meJ.put("score", keep);

        // ── 8) 무승부·보류·무효·기권(저장 실패 포함)
        int sc = League.me().optInt("score");
        JSONObject d = play("o03", draw("o03"));
        ok(d != null && "D".equals(d.optString("outcome")) && League.me().optInt("score") == sc && League.oppById("o03").optInt("d") == 1, "무승부 — 점수 유지, 무승부 전적만");
        String id3 = League.newMatch("o06").optString("id"); File ck3 = touchCk(id3);
        JSONObject h = League.settle(id3, st(0xC0, 2, 0, blk("o07"), 2, 60, 1));
        ok(h != null && "hold".equals(h.optString("status")) && League.me().optInt("score") == sc && !ck3.exists(), "대진 불일치(얼음요정 대신 그늘닌자 블록) → 보류, 점수 그대로");
        String id4 = League.newMatch("o06").optString("id");
        ok(League.cancel(id4, "대진 전") && League.openMatch() == null, "대진 전 경기 무효");
        int o10s = League.oppById("o10").optInt("score");
        String id5 = League.newMatch("o10").optString("id"); League.setStatus(id5, "playing", null); File ck5 = touchCk(id5);
        File blocker = new File(dir, "league.json.tmp"); blocker.mkdir(); new File(blocker, "x").createNewFile();
        JSONObject bad = League.forfeit(id5);
        boolean kept = bad == null && ck5.exists() && League.me().optInt("score") == sc;
        new File(blocker, "x").delete(); blocker.delete();
        ok(kept, "기권 저장 실패 → 되돌림·체크포인트 남김");
        JSONObject ff = League.forfeit(id5);
        ok(ff != null && ff.optInt("delta") == League.delta(sc, o10s, "L") && ff.optInt("delta") == (o10s - sc >= 101 ? -6 : -12) && League.oppById("o10").optInt("w") == 1,
           "기권 재시도에서 한 번 — 시작 때 두 점수 차이 구간대로(검은달)");

        // ── 9) 재시작 후 동일한 기록(기획서 2단계 확인 결과)
        String snap = League.db().toString();
        List<String> ordSnap = League.order();
        Map<String, List<String>> tagSnap = new HashMap<>();
        for (int i = 0; i < 12; i++) { String oid = League.opps().optJSONObject(i).optString("id"); tagSnap.put(oid, League.tags(League.oppById(oid))); }
        restart();
        boolean same = League.db().toString().equals(snap) && League.order().equals(ordSnap);
        for (int i = 0; i < 12; i++) { String oid = League.opps().optJSONObject(i).optString("id"); same &= League.tags(League.oppById(oid)).equals(tagSnap.get(oid)); }
        ok(same, "재시작 후 기록·순위·상대전적·표시가 그대로");
        try (FileOutputStream o = new FileOutputStream(new File(dir, "league.json"))) { o.write("{깨짐".getBytes("UTF-8")); }
        restart();
        ok(League.db().toString().equals(snap), "league.json 이 깨져도 .bak 에서 같은 기록");
        restart();
        ok(League.db().toString().equals(snap), "한 번 더 재시작해도 같음(.bak 복구 뒤 명단을 다시 더하지 않음)");

        // ── 10) 미지원 대진은 도전 불가
        JSONObject o1 = League.oppById("o01"); o1.put("char", 12); o1.put("style", 1);
        ok(League.blockedWhy(o1) != null && League.newMatch("o01") == null, "미지원 대진(주베이 나찰)은 도전 불가·경기 안 만듦");
        o1.put("char", 11); o1.put("style", 0);
        ok(League.delta(1000, 1101, "W") == 18 && League.delta(1000, 1100, "L") == -12 && League.delta(1000, 899, "L") == -18, "점수 구간 표(±100 경계)");
        System.out.println(fails == 0 ? "ALL PASS" : fails + " FAIL");
        System.exit(fails == 0 ? 0 : 1);
    }

    /** 1단계 기록(상대 1명, 경기 3개, 순위 굳힘)을 깔아 두고 이어받기. */
    static void migrate(File dir) throws Exception {
        dir.mkdirs();
        String s1 = "{\"v\":1,\"me\":{\"name\":\"나\",\"score\":1012,\"w\":2,\"l\":1,\"d\":0,\"streak\":2,\"best\":2},"
            + "\"opps\":[{\"id\":\"o01\",\"nick\":\"칼끝노인\",\"char\":11,\"style\":0,\"diff\":1,\"score\":988,\"w\":1,\"l\":2,\"d\":0}],"
            + "\"order\":[\"me\",\"o01\"],"
            + "\"matches\":[{\"id\":\"m1\",\"opp\":\"o01\",\"status\":\"settled\",\"outcome\":\"L\",\"delta\":-12},"
            + "{\"id\":\"m2\",\"opp\":\"o01\",\"status\":\"settled\",\"outcome\":\"W\",\"delta\":12,\"first_win\":true},"
            + "{\"id\":\"m3\",\"opp\":\"o01\",\"status\":\"settled\",\"outcome\":\"W\",\"delta\":12}]}";
        try (FileOutputStream o = new FileOutputStream(new File(dir, "league.json"))) { o.write(s1.getBytes("UTF-8")); }
        JSONObject o1 = League.oppById("o01");
        ok(League.opps().length() == 12 && o1.optInt("score") == 988 && o1.optInt("w") == 1 && o1.optInt("l") == 2 && "칼끝노인".equals(o1.optString("nick")),
           "1단계 기록 이어받기: 12명으로 늘고 칼끝노인 점수·전적 그대로");
        ok(League.me().optInt("score") == 1012 && League.me().optInt("streak") == 2 && League.matches().length() == 3 && League.history("o01", 9).size() == 3,
           "내 점수·연승·경기 기록 그대로");
        ok(League.opps().optJSONObject(1).optString("id").equals("o02") && League.oppById("o02").optInt("score") == 1020 && League.oppById("o12").optInt("w") == 0,
           "새 상대는 고정 id 순으로 뒤에, 초기 점수·빈 전적");
        String f1 = raw(new File(dir, "league.json"));
        ok(new JSONObject(f1).optJSONArray("opps").length() == 12 && new JSONObject(f1).optInt("roster") == 2, "이어받은 명단이 바로 파일에 저장됨(roster 2)");
        restart();
        String again = League.db().toString();
        restart();
        ok(League.db().toString().equals(again) && raw(new File(dir, "league.json")).equals(f1), "다시 열어도 그대로(명단을 두 번 더하지 않음)");
        List<String> ord = League.order();
        ok(ord.indexOf("me") < ord.indexOf("o01") && League.rankOf("me") == 7, "이어받은 뒤 순위: 나 1012 는 새 상대들 사이 7위, 칼끝노인 988 아래");
        System.out.println(fails == 0 ? "ALL PASS (migrate)" : fails + " FAIL (migrate)");
        System.exit(fails == 0 ? 0 : 1);
    }
}

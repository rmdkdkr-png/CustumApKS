package com.dudu.pocketcore;
import org.json.*; import java.io.*; import java.lang.reflect.Field; import java.util.*;
/**
 * League.java 랭크 매치 칸 시험(호스트 JVM, 앱 소스 그대로 + 스텁). 실행:
 *   java -Dleague.root=<빈 폴더> -Dassets.dir=<앱 assets> -cp out:json.jar com.dudu.pocketcore.LeagueRankedTest [migrate]
 * 기본: 새 기록(배치 5판)부터 — 찾기·잡힌 상대·경기 만들기·손잡이 불일치 보류·정산·배치 완료·설욕·재대결 수·기권·재시작·예전 경기 공존.
 * migrate: 예전 리그 기록(정산 6판, 1100점)에서 이어받기 — 배치 없이 MMR·LP, 12명 상대전적 → players, 예전 칸 그대로.
 */
public class LeagueRankedTest {
    static int fails = 0;
    static void ok(boolean c, String what) { System.out.println((c ? "PASS " : "FAIL ") + what); if (!c) fails++; }
    static void restart() throws Exception { Field f = League.class.getDeclaredField("db"); f.setAccessible(true); f.set(null, null); }
    static final android.content.Context C = new android.content.Context();
    /** league_status 22칸 — 결판 비트·승수·P2 블록과 CPU 단계·배율·상한(손잡이 확인) */
    static int[] st(int bits, int w1, int w2, int p2, int lv, int atk, int dfn, int cap) {
        return new int[]{1,5000,1,1,1,bits,w1,w2,0x88,2,0x80,p2,p2,3000,5000,0x80,0x81,60,lv,atk,dfn,cap};
    }
    static int[] stFor(JSONObject m, int bits, int w1, int w2) {
        JSONObject r = m.optJSONObject("rule"), k = r.optJSONObject("cpu");
        return st(bits, w1, w2, (r.optInt("char") << 4) | (r.optInt("style") << 3), k.optInt("lv"), k.optInt("atk"), k.optInt("dfn"), k.optInt("cap"));
    }
    /** 카드 → 대전 → 허브 3 에서 경기 기록(EmuActivity.rankGo/rankNewMatch 와 같은 값의 길) */
    static JSONObject newMatch(RankCore.Player p) {
        League.OppView v = League.oppView(p);
        RankCore.Knobs k = RankCore.knobs(v.mmr, p.personaIdx);
        return League.newRankedMatch(C, v, k, 3, League.rematchCount(p.id));
    }
    static JSONObject play(String out) {
        RankCore.Pick pk = League.rankedPick(C);
        JSONObject m = newMatch(pk.p);
        int bits = "W".equals(out) ? 0xC0 : "L".equals(out) ? 0xA0 : 0x90;
        return League.settle(m.optString("id"), stFor(m, bits, "W".equals(out) ? 2 : "L".equals(out) ? 0 : 3, "W".equals(out) ? 0 : "L".equals(out) ? 2 : 3));
    }

    public static void main(String[] a) throws Exception {
        if (a.length > 0 && "migrate".equals(a[0])) { migrate(); System.out.println("FAILS " + fails); System.exit(fails == 0 ? 0 : 1); }
        if (a.length > 0 && "late".equals(a[0])) { lateFile(); System.out.println("FAILS " + fails); System.exit(fails == 0 ? 0 : 1); }
        JSONObject r0 = League.ranked();
        RankCore.Me me = League.rankMe();
        ok(r0 != null && me.placementLeft == 5 && me.mmr == 1000 && r0.optString("seed").length() == 16, "새 기록: 랭크 칸(씨앗 16자리) · 배치 5판 · MMR 1000");
        String seed = r0.optString("seed");
        restart();
        ok(seed.equals(League.ranked().optString("seed")), "재시작 뒤 같은 씨앗(같은 세상)");

        // 1) 찾기 → 카드(holdPending) → 잡힌 상대 (148: 찾기만으론 안 잡힘)
        RankCore.Pick p1 = League.rankedPick(C);
        ok(p1 != null && p1.p != null && !p1.pending && League.ranked().optJSONObject("pending") == null, "찾기 — 148: 고르기만 하고 «잡힘»은 안 씀");
        League.holdPending(p1);
        ok(League.ranked().optJSONObject("pending").optString("id").equals(p1.p.id), "카드가 뜰 때(holdPending) 고른 상대를 «잡힘»으로 저장");
        restart();
        RankCore.Pick p2 = League.rankedPick(C);
        ok(p2.pending && p2.p.id.equals(p1.p.id), "카드에서 나가도(재시작해도) 다음 찾기에 같은 상대 — 골라 받기 막기");
        JSONObject pfA = League.pfOf(C, p1.p);
        restart();
        JSONObject pfB = League.pfOf(C, League.rankPlayer(p1.p.id));
        ok(pfA.optString("nick").length() > 0 && pfA.toString().equals(pfB.toString()) && pfA.optString("av").length() == 16, "프로필(닉네임·칭호·지역·아바타 씨앗)은 씨앗·id 로 늘 같음");

        // 2) 경기 만들기
        JSONObject m = newMatch(p1.p);
        ok(m != null && League.isRanked(m) && m.optJSONObject("rule").optJSONObject("cpu").has("floor") && m.optJSONObject("opp_snap").optString("nick").equals(pfA.optString("nick"))
           && m.optJSONObject("start").optInt("placement_left") == 5, "랭크 경기 기록 — 모드·손잡이 5개·상대 모습 사본·시작 값");
        ok(League.ranked().optJSONObject("players").optJSONObject(p1.p.id).optJSONObject("pf") != null, "처음 만난 상대의 프로필을 글자 그대로 저장");
        ok(newMatch(p1.p) == null, "열린 경기가 있으면 새 경기를 만들지 않음");
        ok(League.matches().length() == 0 && League.rmatches().length() == 1 && League.openMatch() != null && m.optJSONObject("start").optInt("opp_mr") > 0,
           "랭크 경기는 ranked.matches 에(예전 앱이 안 봄) · 열린 경기로 보임 · 상대 MR 은 무쌍이 아니어도 적음(" + m.optJSONObject("start").optInt("opp_mr") + ")");
        restart();
        ok("ready".equals(League.matchById(m.optString("id")).optString("status")), "경기 기록은 시작 전에 파일에");

        // 3) 손잡이 불일치 → 보류
        JSONObject k = m.optJSONObject("rule").optJSONObject("cpu");
        JSONObject h = League.settle(m.optString("id"), st(0xC0, 2, 0, (m.optJSONObject("rule").optInt("char") << 4) | (m.optJSONObject("rule").optInt("style") << 3),
                k.optInt("lv") + 1, k.optInt("atk"), k.optInt("dfn"), k.optInt("cap")));
        ok(h != null && "hold".equals(h.optString("status")) && h.optString("why").startsWith("난도 불일치") && League.rankMe().w == 0
           && League.ranked().optJSONObject("pending") == null, "CPU 단계가 다르면 «난도 불일치» 보류 — LP·전적 그대로, 148: 잡힌 상대는 풂(같은 원인으로 되풀이 안 막히게)");
        JSONObject m2 = newMatch(p1.p);
        JSONObject h2 = League.settle(m2.optString("id"), stFor(m2, 0xC0, 2, 0) .clone());
        ok(h2 != null && "settled".equals(h2.optString("status")), "같은 상대 다시 — 맞는 손잡이면 정산");
        me = League.rankMe();
        ok(me.w == 1 && me.placementLeft == 4 && League.ranked().optJSONObject("pending") == null && me.recent.get(0).equals(p1.p.id)
           && League.h2h(p1.p.id)[0] == 1 && "배치".equals(h2.optString("tier_before")), "이김 — 배치 4판 남음 · 잡힌 상대 풀림 · 최근 상대 · 상대전적 1승");

        // 4) 상한이 다르면도 보류(결판 때 0x5815)
        RankCore.Pick p3 = League.rankedPick(C);
        ok(!p3.p.id.equals(p1.p.id), "다음 찾기 — 방금 상대는 안 나옴(최근 상대 빼기)");
        JSONObject m3 = newMatch(p3.p);
        int[] s3 = stFor(m3, 0xC0, 2, 0); s3[21] = s3[21] + 1;
        ok("hold".equals(League.settle(m3.optString("id"), s3).optString("status")), "결판 때 상한(0x5815)이 다르면 보류");
        JSONObject m3b = newMatch(p3.p);
        League.settle(m3b.optString("id"), stFor(m3b, 0xA0, 0, 2));
        // 5) 배치 나머지
        for (int i = 0; i < 2; i++) play("W");
        JSONObject last = play("L");
        me = League.rankMe();
        ok(me.placementLeft == 0 && me.lp > 0 && last.optString("event").startsWith("배치 완료") && !"배치".equals(last.optString("tier_after")),
           "배치 5판 끝 — 첫 티어·LP (" + last.optString("tier_after") + " " + me.lp + ")");
        int lp0 = me.lp;
        JSONObject w = play("W");
        ok(w.optInt("lp_delta") > 0 && League.rankMe().lp == lp0 + w.optInt("lp_delta") && w.optJSONObject("bonus") != null, "배치 뒤 이김 — LP 오름(+" + w.optInt("lp_delta") + ")");

        // 6) 설욕: 지고 → 재대결 이김 → +20
        RankCore.Pick pr = League.rankedPick(C);
        JSONObject ma = newMatch(pr.p);
        JSONObject la = League.settle(ma.optString("id"), stFor(ma, 0xA0, 0, 2));
        ok(la.optInt("lp_delta") <= 0 && League.h2h(pr.p.id)[3] == -1, "짐 — LP 내려감(" + la.optInt("lp_delta") + ") · 마지막 결과 패");
        ok(League.rematchCount(pr.p.id) == 1, "같은 상대 이어 붙은 판 수 1");
        JSONObject mb = newMatch(pr.p);
        ok(mb.optInt("rematch_n") == 1, "재대결 경기에 rematch_n 1");
        JSONObject wb = League.settle(mb.optString("id"), stFor(mb, 0xC0, 2, 1));
        ok(wb.optJSONObject("bonus").optInt("revenge") == 20, "재대결로 진 상대를 이김 — 설욕 +20");
        ok(League.rematchCount(pr.p.id) == 2, "이어 붙은 판 수 2 (3판째까지 재대결 가능)");
        JSONObject mc = newMatch(pr.p);
        JSONObject fc = League.forfeit(mc.optString("id"));
        ok(fc != null && "forfeit".equals(fc.optString("status")) && "L".equals(fc.optString("outcome")) && League.rematchCount(pr.p.id) == 3, "기권 = 짐 · 이어 붙은 판 수 3(재대결 끝)");

        // 7) 재시작 — 같은 LP·티어·순위표
        me = League.rankMe();
        long key = League.myKey(me);
        List<RankCore.Row> t1 = RankCore.top(League.rankSeed(), League.today(), 20, League.book(), key, "나");
        restart();
        RankCore.Me me2 = League.rankMe();
        List<RankCore.Row> t2 = RankCore.top(League.rankSeed(), League.today(), 20, League.book(), League.myKey(me2), "나");
        boolean same = t1.size() == t2.size();
        for (int i = 0; same && i < t1.size(); i++) same = t1.get(i).id.equals(t2.get(i).id) && t1.get(i).lp == t2.get(i).lp;
        ok(me2.lp == me.lp && me2.w == me.w && me2.l == me.l && same, "재시작 뒤 같은 LP·전적·순위표");

        // 8) 예전 경기(12명 리그)도 그대로 정산 — 랭크 칸은 안 움직임
        int lpBefore = League.rankMe().lp, gBefore = League.rankMe().games;
        JSONObject om = League.newMatch("o01");
        int[] ost = new int[]{1,5000,1,1,1,0xC0,2,0,0x88,2,0x80,(11 << 4),(11 << 4),3000,5000,0x80,0x81,60,4,0x00D9,0x0126};
        JSONObject os = League.settle(om.optString("id"), ost);
        ok(os != null && "settled".equals(os.optString("status")) && os.optInt("delta") != 0 && League.rankMe().lp == lpBefore && League.rankMe().games == gBefore,
           "예전 리그 경기는 예전 규칙(점수) — 랭크 LP·판수 그대로");

        // 9) JSON 왕복(예전 앱이 읽고 다시 써도 ranked 칸이 남는다)
        File f = new File(new File(System.getProperty("league.root"), "league"), "league.json");
        String txt = new String(java.nio.file.Files.readAllBytes(f.toPath()), "UTF-8");
        JSONObject j = new JSONObject(txt);
        ok(j.optInt("v") == 1 && j.optJSONObject("ranked") != null && new JSONObject(j.toString()).optJSONObject("ranked").optInt("w") == me2.w, "파일은 v 1 그대로 · ranked 칸 왕복");

        // 10) 순위·주변
        long rk = RankCore.rankOf(League.rankSeed(), League.today(), League.book(), League.myKey(me2));
        List<RankCore.Row> ar = RankCore.around(League.rankSeed(), League.today(), League.book(), League.myKey(me2), "나", 5);
        boolean hasMe = false; for (RankCore.Row x : ar) hasMe |= x.me;
        ok(rk >= 1 && rk <= RankCore.total() && hasMe && ar.size() >= 3, "내 순위 " + rk + " / " + RankCore.total() + " · 내 주변 " + ar.size() + "명");
        // 11) 무쌍 — 상대가 무쌍이 아니어도 이기면 MR 오름, 결과 줄은 MR
        JSONObject rr = League.ranked();
        rr.put("master", true).put("mr", 1520).put("lp", 9000).put("mmr", 1580.0).put("placement", 0).put("shield", false);
        League.save();
        JSONObject wm = null; int tries = 0;
        while (tries++ < 60) {                  /* 무쌍 아닌 상대가 나올 때까지(MMR 1580 근처는 무쌍이 많다 — 6번이면 가끔 모자랐다) */
            RankCore.Pick pm = League.rankedPick(C);
            League.OppView ov = League.oppView(pm.p);
            JSONObject mm = League.newRankedMatch(C, ov, RankCore.knobs(ov.mmr, pm.p.personaIdx), 3, League.rematchCount(pm.p.id));
            JSONObject sm = League.settle(mm.optString("id"), stFor(mm, 0xC0, 2, 0));
            if (!ov.master) { wm = sm; break; }
        }
        ok(wm != null && wm.optJSONObject("start").optInt("opp_mr") > 0 && wm.optInt("mr_after") > wm.optInt("mr_before")
           && League.rankedResultLine(wm).endsWith(" MR") && League.rankedResultLine(wm).contains("+"),
           "무쌍이 무쌍 아닌 상대를 이김 — MR " + (wm != null ? wm.optInt("mr_before") + " → " + wm.optInt("mr_after") + " · «" + League.rankedResultLine(wm) + "»" : "?"));
        // 12) 예전 앱이 보는 파일 — 위쪽 matches 에 랭크 경기 없음
        JSONObject j2 = new JSONObject(new String(java.nio.file.Files.readAllBytes(f.toPath()), "UTF-8"));
        boolean noRk = true; JSONArray tm = j2.optJSONArray("matches");
        for (int i = 0; i < tm.length(); i++) noRk &= !"ranked".equals(tm.optJSONObject(i).optString("mode"));
        ok(noRk && tm.length() == 1 && j2.optJSONObject("ranked").optJSONArray("matches").length() >= 12, "파일: 위쪽 matches 는 예전 경기 1판뿐 · 랭크 " + j2.optJSONObject("ranked").optJSONArray("matches").length() + "판은 ranked.matches");
        // 148 — 대기창·막힘 풀기·시즌
        pendingTiming(); holdRelease(); voids(); saveFailRollback(); recover(); today(); seasons(); restartTest(); lastRom(); oldFile();
        System.out.println("FAILS " + fails);
        System.exit(fails == 0 ? 0 : 1);
    }

    /** 148 통합: 저장소 권한 없이 처음 읽어 빈 기록이 메모리에 남은 뒤 진짜 파일이 보이면 — 다시 읽고, 빈 기록으로 덮지 않는다 */
    static void lateFile() throws Exception {
        File root = new File(System.getProperty("league.root")); root.mkdirs();
        File blocker = new File(root, "league");
        try (FileOutputStream o = new FileOutputStream(blocker)) { o.write(1); }   /* league 자리에 파일 — 폴더를 못 만들고 저장도 실패(권한 없음 흉내) */
        restart();
        RankCore.Me m0 = League.rankMe();
        ok(m0.placementLeft == 5 && !new File(blocker, "league.json").exists(), "파일을 못 보는 동안: 빈 기록(배치 5판) · 저장 못 함");
        blocker.delete();
        migrate0();                                                   /* 진짜 기록이 나타남(예전 6판 · 1100점) */
        RankCore.Me m1 = League.rankMe();
        ok(m1.placementLeft == 0 && Math.abs(m1.mmr - 1100) < 0.01, "진짜 파일이 보이면 다시 읽음 — 배치 없이 MMR 1100 (" + m1.placementLeft + " · " + m1.mmr + ")");
        League.save();
        JSONObject disk = new JSONObject(new String(java.nio.file.Files.readAllBytes(new File(new File(root, "league"), "league.json").toPath()), "UTF-8"));
        ok(disk.optJSONArray("matches").length() == 6 && disk.optJSONObject("me").optInt("score") == 1100, "저장해도 진짜 기록 그대로(빈 기록으로 안 덮음)");
        // 2) 나중에 보인 파일이 못 읽는 것이면 — 매번 새로 만들지 않고(씨앗 고정) 막아 둔다, reload 가 옆으로 치운다
        File root2 = new File(root.getParentFile(), root.getName() + "_bad"); root2.mkdirs();
        System.setProperty("league.root", root2.getAbsolutePath());
        File blk2 = new File(root2, "league");
        try (FileOutputStream o = new FileOutputStream(blk2)) { o.write(1); }
        restart();
        long sd0 = League.rankSeed();
        blk2.delete(); blk2.mkdirs();
        try (FileOutputStream o = new FileOutputStream(new File(blk2, "league.json"))) { o.write("{깨진".getBytes("UTF-8")); }
        long sd1 = League.rankSeed(), sd2 = League.rankSeed();
        ok(sd1 == sd0 && sd2 == sd0 && League.dbProblem != null && !League.save(), "못 읽는 파일이 나타남 — 씨앗 그대로(다시 만들기 고리 없음) · 저장 막음(" + League.dbProblem + ")");
        String why = League.reload();
        File[] moved = blk2.listFiles((d, n) -> n.startsWith("league.json.unreadable-"));
        ok(why == null && League.dbProblem == null && moved != null && moved.length == 1, "다시 확인(reload) — 못 읽는 파일은 옆으로 치우고 새로 시작");
    }
    /** migrate() 와 같은 예전 기록 파일만 만든다 */
    static void migrate0() throws Exception {
        File dir = new File(System.getProperty("league.root"), "league"); dir.mkdirs();
        JSONObject j = new JSONObject();
        j.put("v", 1).put("roster", 2);
        j.put("me", new JSONObject().put("name", "나").put("score", 1100).put("w", 4).put("l", 2).put("d", 0).put("streak", 1).put("best", 3));
        JSONArray os = new JSONArray();
        for (Object[] r : League.ROSTER) os.put(new JSONObject().put("id", r[0]).put("nick", r[1]).put("char", r[2]).put("style", r[3]).put("diff", r[4]).put("score", r[5]).put("w", 0).put("l", 0).put("d", 0));
        j.put("opps", os);
        JSONArray ms = new JSONArray();
        long t = 1792000000000L;
        for (String o : new String[]{"o01","o01","o03","o03","o01","o02"}) ms.put(new JSONObject().put("id", UUID.randomUUID().toString()).put("opp", o).put("status", "settled").put("outcome", "W").put("settled", t++));
        j.put("matches", ms);
        try (FileOutputStream o = new FileOutputStream(new File(dir, "league.json"))) { o.write(j.toString().getBytes("UTF-8")); }
    }
    static void migrate() throws Exception {
        File dir = new File(System.getProperty("league.root"), "league"); dir.mkdirs();
        JSONObject j = new JSONObject();
        j.put("v", 1).put("roster", 2);
        j.put("me", new JSONObject().put("name", "나").put("score", 1100).put("w", 4).put("l", 2).put("d", 0).put("streak", 1).put("best", 3));
        JSONArray os = new JSONArray();
        for (Object[] r : League.ROSTER) os.put(new JSONObject().put("id", r[0]).put("nick", r[1]).put("char", r[2]).put("style", r[3]).put("diff", r[4]).put("score", r[5]).put("w", 0).put("l", 0).put("d", 0));
        os.getJSONObject(0).put("w", 1).put("l", 3);           /* o01: 상대 1승 3패 = 내 3승 1패 */
        os.getJSONObject(2).put("w", 1).put("l", 1).put("broke_streak", 3);
        j.put("opps", os);
        JSONArray ms = new JSONArray();
        String[][] seq = { {"o01","W"}, {"o01","L"}, {"o01","W"}, {"o03","L"}, {"o03","W"}, {"o01","W"} };
        long t = 1792000000000L;
        for (String[] s : seq) ms.put(new JSONObject().put("id", UUID.randomUUID().toString()).put("opp", s[0]).put("status", "settled").put("outcome", s[1]).put("settled", t++));
        j.put("matches", ms);
        try (FileOutputStream o = new FileOutputStream(new File(dir, "league.json"))) { o.write(j.toString().getBytes("UTF-8")); }
        RankCore.Me me = League.rankMe();
        int lpWant = Math.max(0, (int) Math.round(RankCore.lpOfMmr(1100) - 200) / 10 * 10);
        ok(me.placementLeft == 0 && me.games == 5 && Math.abs(me.mmr - 1100) < 0.01 && me.lp == lpWant, "예전 6판 · 1100점 → 배치 없이 MMR 1100 · LP " + me.lp + " (" + RankCore.label(me.lp) + ")");
        JSONObject ps = League.ranked().optJSONObject("players");
        ok(ps.optJSONObject("o01").optInt("w") == 3 && ps.optJSONObject("o01").optInt("l") == 1 && ps.optJSONObject("o01").optInt("last") == 1
           && ps.optJSONObject("o03").optInt("broke") == 3, "12명 상대전적(내 쪽으로 뒤집음)·마지막 결과·끊은 연승 → players");
        ok(me.recent.size() == 2 && me.recent.get(0).equals("o01"), "최근 상대 — 예전 경기에서(새것 먼저)");
        JSONObject lg = League.ranked().optJSONObject("legacy");
        ok(lg.optInt("score") == 1100 && lg.optInt("games") == 6 && League.me().optInt("score") == 1100 && League.opps().length() == 12, "옛 기록(legacy) 남김 · 예전 me·opps 칸 그대로");
        restart();
        ok(League.rankMe().lp == me.lp && League.ranked().optString("seed").equals(League.ranked().optString("seed")), "다시 열어도 이어받기 결과 그대로(한 번만)");
        List<RankCore.Player> rv = League.rivals();
        ok(rv.size() == 12 && rv.get(0).legacy && League.pfOf(C, rv.get(0)).optBoolean("curated"), "라이벌 12명 — 손으로 고른 프로필(pool.roster)");
    }

    /* ── 148: 대기창·막힘 풀기·시즌 ─────────────────────────────────────── */
    static File leagueDir() { return new File(System.getProperty("league.root"), "league"); }
    static File dbFile() { return new File(leagueDir(), "league.json"); }
    static byte[] bytes(File f) throws Exception { return java.nio.file.Files.readAllBytes(f.toPath()); }
    static JSONObject readJ(File f) throws Exception { return new JSONObject(new String(bytes(f), "UTF-8")); }
    static void write(File f, String s) throws Exception { try (FileOutputStream o = new FileOutputStream(f)) { o.write(s.getBytes("UTF-8")); } }
    static void rmrf(File f) { File[] k = f.listFiles(); if (k != null) for (File x : k) rmrf(x); f.delete(); }
    /** 빈 기록부터 — 폴더·설정 파일을 지우고 메모리 판도 버린다 */
    static void wipe() throws Exception {
        rmrf(leagueDir()); new File(System.getProperty("league.root"), "options.txt").delete();
        restart(); League.dbProblem = null; League.liveHub = false;
    }
    static JSONObject dbNow() throws Exception { Field f = League.class.getDeclaredField("db"); f.setAccessible(true); return (JSONObject) f.get(null); }
    static JSONObject copy(JSONObject j) throws Exception { return new JSONObject(j.toString()); }
    static JSONObject pend() { return League.ranked().optJSONObject("pending"); }
    static int archiveFiles() { File[] fs = new File(leagueDir(), "archive").listFiles(); return fs == null ? 0 : fs.length; }
    /** 찾기 → 카드(EmuActivity.rankCardShow 가 holdPending) */
    static RankCore.Pick card() { RankCore.Pick pk = League.rankedPick(C); League.holdPending(pk); return pk; }
    /** 첫 라운드가 시작된 경기(EmuActivity.leagueStart 처럼 playing · 앱 판) */
    static JSONObject started(RankCore.Pick pk, int app) {
        JSONObject m = newMatch(pk.p); String id = m.optString("id");
        League.setStatus(id, "playing", null); League.note(id, "app", app);
        return League.matchById(id);
    }
    static void setPlaced(int lp, double mmr) throws Exception {
        League.ranked().put("placement", 0).put("lp", lp).put("mmr", mmr).put("peak_lp", lp).put("games", 30); League.save();
    }

    /** 잡는 때 — 찾기는 저장하지 않고, 카드가 뜰 때(holdPending) 잡는다 */
    static void pendingTiming() throws Exception {
        wipe();
        League.ranked();
        byte[] b0 = bytes(dbFile());
        RankCore.Pick pk = League.rankedPick(C);
        ok(Arrays.equals(b0, bytes(dbFile())) && pend() == null && !pk.pending, "148 찾기(rankedPick)는 league.json 을 한 바이트도 안 바꾸고 «잡힘»도 안 만듦");
        ok(pk.waitMs == RankCore.waitMs(pk, League.rankMe().mmr, false, League.hourOfDay()) && pk.waitMs >= 2000 && pk.waitMs <= 15000, "대기창 시간 waitMs = RankCore.waitMs(보통 · 한국 시각) " + pk.waitMs + "ms");
        ok(League.holdPending(pk), "holdPending 저장");
        JSONObject pd = pend(), kn = pd.optJSONObject("knobs");
        ok(pd.optString("id").equals(pk.p.id) && pd.optLong("at") > 0 && pd.has("mmr") && pd.optInt("stage", -9) == pk.p.stage && pd.optInt("miss", -1) == 0
           && kn != null && kn.has("diff") && kn.has("lv") && kn.has("cap") && kn.has("floor") && kn.has("atk") && kn.has("dfn"), "holdPending — id·at·mmr·stage·knobs 6칸·miss 0");
        long at0 = pd.optLong("at");
        restart();
        RankCore.Pick pk2 = League.rankedPick(C);
        ok(pk2.pending && pk2.p.id.equals(pk.p.id) && pk2.waitMs >= 1200 && pk2.waitMs <= 2400, "다음 찾기 = 같은 상대 · pending · " + pk2.waitMs + "ms (≤ 2400)");
        Thread.sleep(3);
        byte[] b1 = bytes(dbFile());
        ok(League.holdPending(pk2) && pend().optLong("at") == at0 && Arrays.equals(b1, bytes(dbFile())), "같은 상대를 다시 잡아도 at 그대로(파일도 그대로)");
        League.ranked().remove("pending"); League.save();
        Settings.put("pocketcore_rank_wait", "fast");
        boolean fast = true;
        for (int i = 0; i < 20; i++) { RankCore.Pick f = League.rankedPick(C); fast &= f.waitMs == f.searchMs && f.waitMs >= 2000 && f.waitMs < 6000; }
        Settings.put("pocketcore_rank_wait", "normal");
        ok(fast && pend() == null, "설정 «빠르게»(pocketcore_rank_wait=fast) = searchMs 2~6초");
    }

    /** 잡힌 상대 풀기 — hold()·정산 보류 둘 다·남은 판 2번·무효 2번·하루. 사용자가 뒤로(cancel)는 그대로 */
    static void holdRelease() throws Exception {
        wipe();
        RankCore.Pick pk = card();
        JSONObject m = newMatch(pk.p);
        ok(pend() != null && League.hold(m.optString("id"), "시험 보류", "고침") && pend() == null, "hold() — 잡힌 상대를 풂");
        pk = card(); m = newMatch(pk.p);
        JSONObject k = m.optJSONObject("rule").optJSONObject("cpu");
        int want = (m.optJSONObject("rule").optInt("char") << 4) | (m.optJSONObject("rule").optInt("style") << 3);
        JSONObject h = League.settle(m.optString("id"), st(0xC0, 2, 0, want, k.optInt("lv") + 1, k.optInt("atk"), k.optInt("dfn"), k.optInt("cap")));
        ok("hold".equals(h.optString("status")) && h.optString("why").startsWith("난도 불일치") && pend() == null, "정산 손잡이 불일치 보류 — 잡힌 상대를 풂");
        pk = card(); m = newMatch(pk.p);
        k = m.optJSONObject("rule").optJSONObject("cpu");
        want = (m.optJSONObject("rule").optInt("char") << 4) | (m.optJSONObject("rule").optInt("style") << 3);
        h = League.settle(m.optString("id"), st(0xC0, 2, 0, want ^ 0x10, k.optInt("lv"), k.optInt("atk"), k.optInt("dfn"), k.optInt("cap")));
        ok("hold".equals(h.optString("status")) && h.optString("why").startsWith("대진 불일치") && pend() == null, "정산 대진 불일치 보류 — 잡힌 상대를 풂");
        pk = card(); m = newMatch(pk.p);
        ok(League.cancel(m.optString("id"), "뒤로") && pend() != null && pend().optString("id").equals(pk.p.id) && pend().optInt("miss") == 0, "사용자가 뒤로(cancel) — 잡힌 상대 그대로(miss 아님)");
        m = newMatch(pk.p);
        ok(League.cancelStale(m.optString("id"), "남은 판") && pend() != null && pend().optInt("miss") == 1 && "cancelled".equals(League.matchById(m.optString("id")).optString("status")),
           "남은 «준비»(cancelStale) 1번 — 무효 + miss 1");
        RankCore.Pick again = League.rankedPick(C);
        League.holdPending(again);
        ok(again.pending && again.p.id.equals(pk.p.id) && pend().optInt("miss") == 1, "그 상대를 다시 잡아도 miss 1 그대로");
        m = newMatch(pk.p);
        ok(League.cancelStale(m.optString("id"), "남은 판") && pend() == null && !League.rankedPick(C).pending, "남은 판 2번째 — 풂, 다음엔 새 상대");
        pk = card(); m = started(pk, 148);
        ok(League.voidStarted(m.optString("id"), "crash") && pend() != null && pend().optInt("miss") == 1, "시작한 뒤 무효 1번 — miss 1");
        RankCore.Pick p3 = League.rankedPick(C);
        ok(p3.pending && p3.p.id.equals(pk.p.id) && p3.waitMs <= 2400, "무효 뒤 다음 찾기 = 같은 상대(1.2~2.4초)");
        m = started(pk, 148);
        ok(League.voidStarted(m.optString("id"), "ckpt") && pend() == null, "무효 2번째 — 풂");
        pk = card();
        pend().put("at", System.currentTimeMillis() - 25 * 3600_000L); League.save(); restart();
        ok(League.rankMe().pendingId == null && !League.rankedPick(C).pending, "잡힌 지 25시간 — 풀림(하루 기한 그대로)");
    }

    /** 무효(시작한 뒤) — voidKind 표 · voidStarted 는 LP·전적을 안 건드림 · 목록 · voidReady */
    static void voids() throws Exception {
        wipe();
        League.ranked().put("placement", 0).put("lp", 2400).put("mmr", 1010.0).put("w", 3).put("l", 2).put("d", 1).put("games", 25); League.save();
        RankCore.Pick pk = card();
        JSONObject m = newMatch(pk.p); String id = m.optString("id");
        ok(League.voidKind(League.matchById(id), 148) == null, "voidKind: 준비(대진 전) → null");
        League.setStatus(id, "playing", null); League.note(id, "app", 148);
        ok("crash".equals(League.voidKind(League.matchById(id), 148)), "voidKind: 진행 중 · 체크포인트 없음 → crash");
        League.liveHub = true;
        ok(League.voidKind(League.matchById(id), 148) == null && !League.voidStarted(id, "crash") && "playing".equals(League.matchById(id).optString("status")),
           "voidKind: 게임 속 리그가 지금 하는 판(진행 중 · liveHub) → null · voidStarted 도 안 됨");
        League.liveHub = false;
        File ck = League.ckpt(id); write(ck, "state");
        League.setStatus(id, "resume", "앱이 경기 중에 내려감");
        ok(League.voidKind(League.matchById(id), 148) == null, "voidKind: 복귀 대기 · 체크포인트 있음 → null(이어 하기)");
        League.setResumeFail(id, "badckpt");
        ok("ckpt".equals(League.voidKind(League.matchById(id), 148)) && "badckpt".equals(League.matchById(id).optString("resume_fail")), "voidKind: 불러오지 못함(resume_fail badckpt) → ckpt");
        League.setStatus(id, "playing", "");
        ok(!League.matchById(id).has("resume_fail") && League.voidKind(League.matchById(id), 148) == null, "나중에 이어 하기가 되면(setStatus playing) 실패 표시 지움 → null");
        League.matchById(id).put("resume_fail", "badckpt");      // 옛 판(147)이 이어 하며 남긴 표시 — 147 은 resume_fail 을 모른다
        ok(League.voidKind(League.matchById(id), 148) == null, "진행 중에 남은 옛 실패 표시는 안 봄 → null");
        League.matchById(id).remove("resume_fail");
        League.setStatus(id, "resume", "앱이 경기 중에 내려감");
        League.note(id, "app", 147);
        ok(League.voidKind(League.matchById(id), 148) == null && !League.matchById(id).has("resume_fail"),
           "voidKind: 앱 판만 다름(147 → 148) · 체크포인트·롬 멀쩡 → null(이어 하기 — 앱 업데이트만으로는 무효가 안 열림)");
        League.setResumeFail(id, "rom");
        ok("app".equals(League.voidKind(League.matchById(id), 148)) && League.voidKind(League.matchById(id), 0) == null && "rom".equals(League.matchById(id).optString("resume_fail")),
           "voidKind: 롬·코어로 막힘(resume_fail rom) + 앱 판 다름(147 → 148) → app (판을 모르면 안 봄)");
        League.note(id, "app", 148); League.note(id, "rom", "/sdcard/other.ngc"); League.note(id, "rom_md5", "00ff00ff");
        ok(League.voidKind(League.matchById(id), 148) == null, "voidKind: 같은 앱에서 롬만 바뀜(resume_fail rom) → null(롬 바꾸기로는 무효가 안 열림)");
        League.setResumeFail(id, "nockpt");
        ok("crash".equals(League.voidKind(League.matchById(id), 148)), "voidKind: resume_fail nockpt → crash");
        League.setResumeFail(id, null);
        RankCore.Me b = League.rankMe(); JSONObject ps0 = copy(League.ranked().optJSONObject("players"));
        ok(League.voidStarted(id, "crash"), "voidStarted 저장");
        RankCore.Me a = League.rankMe(); JSONObject mm = League.matchById(id);
        ok(a.lp == b.lp && a.mmr == b.mmr && a.w == b.w && a.l == b.l && a.d == b.d && a.placementLeft == b.placementLeft && a.games == b.games && a.recent.equals(b.recent)
           && League.sameJson(ps0, League.ranked().optJSONObject("players")), "무효 — LP·MMR·승패·배치·판수·최근 상대·상대 전적 그대로");
        ok("cancelled".equals(mm.optString("status")) && mm.optBoolean("void_after_start") && "crash".equals(mm.optString("void_kind")) && League.voidWhy("crash").equals(mm.optString("why"))
           && !mm.has("result") && !mm.has("outcome") && !ck.exists() && League.openMatch() == null, "cancelled + void_after_start + void_kind + why · 정산 없음 · 체크포인트 지움");
        boolean listed = false; for (JSONObject x : League.holds(20)) listed |= id.equals(x.optString("id"));
        ok(listed, "«보류·무효 경기» 목록(holds)에 보임 — «" + mm.optString("why") + "»");
        ok(!League.voidStarted(id, "crash") && League.voidKind(mm, 148) == null, "끝난 경기는 다시 무효 안 됨");
        RankCore.Pick p2 = League.rankedPick(C);
        JSONObject m2 = newMatch(p2.p);
        ok(!League.voidStarted(m2.optString("id"), "crash") && "ready".equals(League.matchById(m2.optString("id")).optString("status")), "준비 경기엔 voidStarted 안 됨");
        League.cancel(m2.optString("id"), "뒤로");
        boolean l2 = false; for (JSONObject x : League.holds(20)) l2 |= m2.optString("id").equals(x.optString("id"));
        ok(!l2, "랭크 대진 전 무효는 목록에 안 쌓임(147 그대로)");
        JSONObject m3 = newMatch(p2.p);
        League.liveHub = true;
        ok(League.voidReady("시험") == 0 && "ready".equals(League.matchById(m3.optString("id")).optString("status")), "게임 속 리그가 살아 있으면(liveHub) voidReady 0");
        League.liveHub = false;
        ok(League.voidReady("순위표를 열며 정리(대진 전)") == 1 && "cancelled".equals(League.matchById(m3.optString("id")).optString("status")) && League.openMatch() == null && League.voidReady("x") == 0,
           "voidReady — 남은 «준비» 경기를 무효로(1) · 다시 부르면 0");
    }

    /** 저장 실패 — 앱 코드에 시험 갈고리 없이: save() 가 쓰는 임시 파일 자리에 (못 지우는) 폴더를 둔다 */
    static void saveFailRollback() throws Exception {
        wipe();
        setPlaced(3920, 1090);
        RankCore.Pick pk = card(); JSONObject m = started(pk, 148); String id = m.optString("id");
        File ck = League.ckpt(id); write(ck, "state");
        File block = new File(leagueDir(), "league.json.tmp"); block.mkdirs(); write(new File(block, "x"), "x");
        JSONObject before = copy(dbNow());
        ok(!League.save(), "임시 파일 자리에 폴더 — 저장 실패");
        ok(!League.voidStarted(id, "crash") && League.sameJson(before, dbNow()) && "playing".equals(League.matchById(id).optString("status")) && ck.exists(),
           "무효 저장 실패 — 메모리 되돌림 · 체크포인트 그대로");
        rmrf(block);
        ok(League.voidStarted(id, "crash"), "막힌 게 풀리면 무효 저장");
        block.mkdirs(); write(new File(block, "x"), "x");
        before = copy(dbNow());
        ok(!League.newSeason() && League.sameJson(before, dbNow()) && League.season() == 1 && archiveFiles() == 0, "새 시즌 저장 실패 — 메모리 되돌림 · 보관 파일 안 남음");
        ok(!League.restartRanked() && League.sameJson(before, dbNow()) && League.rankMe().placementLeft == 0 && archiveFiles() == 0, "처음부터 저장 실패 — 메모리 되돌림 · 보관 파일 안 남음");
        rmrf(block);
        restart();
        ok(League.season() == 1 && League.rankMe().lp == 3920 && League.seasons().isEmpty(), "파일도 그대로(시즌 1 · LP 3920)");
    }

    /** 다시 읽기 — dbProblem 을 풀고 파일에서 새로 */
    static void recover() throws Exception {
        wipe();
        League.ranked();
        Field f = League.class.getDeclaredField("dbProblem"); f.setAccessible(true); f.set(null, "시험: 못 읽음");
        ok(!League.save(), "dbProblem 이면 저장 안 함");
        League.ranked().put("lp", 777);
        String why = League.reload();
        ok(why == null && League.dbProblem == null && League.ranked().optInt("lp") == 0 && League.save(), "reload() — 파일을 다시 읽어 dbProblem 풂(메모리 판은 버림) · 다시 저장됨");
        File wt = new File(leagueDir(), ".write_test"); wt.mkdirs(); write(new File(wt, "x"), "x");   // 쓰기 시험 파일 자리에 (못 지우는) 폴더 = 폴더에 못 씀
        String w2 = League.reload();
        ok(w2 != null && w2.equals(League.writeProblem()) && League.dbProblem == null, "reload() — 아직 못 쓰면 남은 이유를 돌려줌(«아직 안 돼요 — …») : " + w2);
        rmrf(wt);
        ok(League.reload() == null, "막힌 게 풀리면 reload() null");
        League.ranked().put("lp", 1230); League.save();
        write(dbFile(), "{깨짐"); write(new File(leagueDir(), "league.json.bak"), "{깨짐");
        String w3 = League.reload();
        File[] moved = leagueDir().listFiles((d, n) -> n.startsWith("league.json.unreadable-"));
        ok(w3 == null && League.ranked().optInt("lp") == 0 && moved != null && moved.length == 1, "reload() — 못 읽는 파일은 옆으로 옮기고(지우지 않음) 새 기록 · null");
    }

    /** 오늘 전적 — 한국 시각 자정 · 기권 = 패 · 무효·보류 빼고 · 새것부터. 첫 승 보너스 */
    static void today() throws Exception {
        wipe();
        int day = RankCore.today(1792000000000L); long d0 = day * 86_400_000L - 9 * 3600_000L;   // 그날 한국 시각 0시
        JSONArray rm = League.rmatches();
        Object[][] X = { { "settled", "W", 50, -60_000L, "" }, { "settled", "L", -40, 30_000L, "" }, { "forfeit", "L", -45, 60_000L, "" }, { "cancelled", "", 0, 90_000L, "" },
                         { "hold", "", 0, 100_000L, "" }, { "settled", "D", 0, 120_000L, "" }, { "settled", "W", 2400, 150_000L, "배치" }, { "settled", "W", 55, 180_000L, "" } };
        for (Object[] x : X) {
            JSONObject m = new JSONObject().put("id", UUID.randomUUID().toString()).put("mode", "ranked").put("status", x[0]).put("outcome", x[1]).put("lp_delta", x[2])
                    .put("created", d0 + (Long) x[3] - 5000).put("settled", d0 + (Long) x[3]);
            if ("forfeit".equals(x[0])) m.put("forfeit", true);
            if (!"".equals(x[4])) m.put("tier_before", x[4]);
            rm.put(m);
        }
        League.save();
        League.Today td = League.rankedToday(d0 + 3600_000L);
        ok(td.w == 2 && td.l == 2 && td.d == 1 && td.lpSum == -30 && new String(td.last5).equals("WWDLL"),
           "오늘(한국 0시 넘어) 2승 2패 1무 · -30 LP(배치 판 LP 빼고) · 새것부터 WWDLL — 23:59 판·무효·보류 빼고, 기권 = 패 (" + td.w + "/" + td.l + "/" + td.d + " " + td.lpSum + " " + new String(td.last5) + ")");
        League.Today yd = League.rankedToday(d0 - 1000);
        ok(yd.w == 1 && yd.l == 0 && yd.d == 0 && yd.lpSum == 50 && new String(yd.last5).equals("W"), "전날 23:59 판은 전날로");
        for (int i = 0; i < 4; i++) rm.put(new JSONObject().put("id", "x" + i).put("mode", "ranked").put("status", "settled").put("outcome", "L").put("lp_delta", -10).put("settled", d0 + 200_000L + i));
        League.Today t2 = League.rankedToday(d0 + 3600_000L);
        ok(t2.last5.length == 5 && new String(t2.last5).equals("LLLLW") && t2.l == 6 && t2.games() == 9, "점은 5개까지(새것부터)");
        ok(League.rankedToday().games() == 0, "지금(다른 날)은 오늘 첫 판");
        JSONObject r = League.ranked(); r.put("placement", 0).put("lp", 2400); r.remove("last_win_day");
        ok(League.bonusLeft(), "오늘 첫 승 전 — 보너스 남음");
        r.put("last_win_day", League.today());
        ok(!League.bonusLeft(), "오늘 이미 이김 — 보너스 없음");
        r.put("last_win_day", League.today() - 1).put("placement", 2);
        ok(!League.bonusLeft(), "배치 중엔 보너스 없음");
    }

    /** 새 시즌 — 막힘 · 준비 경기 먼저 무효 · LP = newSeasonLp · 남기는 것·0으로 · 지난 시즌 줄 · 보관 파일 */
    static void seasons() throws Exception {
        wipe();
        League.ranked();
        ok(!League.newSeason() && League.newSeasonPreview() == null && League.season() == 1 && archiveFiles() == 0, "배치 중엔 새 시즌 안 됨");
        JSONObject r = League.ranked();
        r.put("placement", 0).put("lp", 3920).put("mmr", 1090.0).put("peak_lp", 4100).put("games", 57).put("w", 31).put("l", 25).put("d", 1)
         .put("streak", 3).put("lstreak", 0).put("best", 6).put("shield", true).put("last_win_day", League.today())
         .put("recent", new JSONArray().put("p0650001").put("o03"));
        r.put("players", new JSONObject().put("p0650001", new JSONObject().put("w", 2).put("l", 1).put("d", 0).put("last", 1).put("broke", 0).put("mmr_adj", -12.5).put("lp_adj", -40)));
        League.save();
        long t0 = System.currentTimeMillis();
        RankCore.Pick pk = card(); JSONObject m = started(pk, 148);
        ok(!League.newSeason() && "끝나지 않은 경기를 먼저 정리해 주세요".equals(League.resetBlockedWhy()) && !League.restartRanked() && League.season() == 1 && archiveFiles() == 0,
           "시작한 경기가 열려 있으면 둘 다 안 됨");
        League.voidStarted(m.optString("id"), "crash");
        League.liveHub = true;
        ok(!League.newSeason() && "게임 속 리그를 닫은 뒤에 할 수 있어요".equals(League.resetBlockedWhy()) && !League.restartRanked() && League.season() == 1, "게임 속 리그가 살아 있으면(liveHub) 안 됨");
        League.liveHub = false;
        League.dbProblem = "시험";
        ok(!League.newSeason() && "시험".equals(League.resetBlockedWhy()), "기록 파일 문제(dbProblem)면 안 됨");
        League.dbProblem = null;
        ok(League.resetBlockedWhy() == null, "막힘 없음");
        League.SeasonPreview pv = League.newSeasonPreview();
        ok(pv != null && pv.season == 1 && pv.lp0 == 3920 && pv.lp1 == 3310 && "검호 ★2".equals(pv.label0) && "검객 ★5".equals(pv.label1), "미리보기 — 시즌 1 · LP 3920 → 3310 (검호 ★2 → 검객 ★5)");
        RankCore.Pick pr = card(); JSONObject ready = newMatch(pr.p);
        ok(pend() != null && "ready".equals(ready.optString("status")), "준비 경기 + 잡힌 상대 있음");
        JSONObject before = copy(League.ranked());
        int nMatches = League.rmatches().length();
        ok(League.newSeason(), "새 시즌 시작");
        r = League.ranked();
        RankCore.Me me = League.rankMe();
        ok(me.lp == RankCore.newSeasonLp(3920, 1090) && me.lp == 3310 && me.peakLp == 3310, "LP = RankCore.newSeasonLp (3310) · 최고 LP = 새 LP");
        ok(me.w == 0 && me.l == 0 && me.d == 0 && me.streak == 0 && me.lstreak == 0 && me.best == 0 && !me.shield && !me.master && me.mr == 0, "승패·연승·연패·최장·강등 위기·무쌍 0부터");
        ok(Math.abs(me.mmr - before.optDouble("mmr")) < 1e-9 && me.games == before.optInt("games") && me.lastWinDay == League.today()
           && r.optJSONArray("recent").toString().equals(before.optJSONArray("recent").toString()) && League.sameJson(r.optJSONObject("players"), before.optJSONObject("players"))
           && r.optString("seed").equals(before.optString("seed")) && r.optJSONArray("matches").length() == nMatches, "MMR·판수·최근 상대·상대 전적·오늘 첫 승·씨앗·경기 기록 그대로");
        ok(!r.has("pending") && "cancelled".equals(League.matchById(ready.optString("id")).optString("status")) && League.openMatch() == null, "준비 경기는 먼저 무효로 · 잡힌 상대 풂");
        ok(League.season() == 2 && League.seasonStart() >= t0, "시즌 2 · 새 시작 시각");
        List<JSONObject> rows = League.seasons();
        JSONObject row = rows.isEmpty() ? new JSONObject() : rows.get(rows.size() - 1);
        ok(rows.size() == 1 && row.optInt("n") == 1 && "season".equals(row.optString("kind")) && row.optInt("w") == 31 && row.optInt("l") == 25 && row.optInt("d") == 1 && row.optInt("games") == 57
           && row.optInt("peak_lp") == 4100 && RankCore.label(4100).equals(row.optString("peak_label")) && row.optInt("final_lp") == 3920 && "검호 ★2".equals(row.optString("final_label"))
           && row.optInt("best") == 6 && !row.optBoolean("master") && row.optLong("start") == before.optLong("season_start") && row.optLong("end") >= t0, "지난 시즌 줄 — " + row);
        int[] c = League.careerWLD();
        ok(c[0] == 31 && c[1] == 25 && c[2] == 1, "통산 31승 25패 1무(지난 시즌 + 이번)");
        File af = new File(League.archiveDir(), row.optString("file"));
        JSONObject arc = af.isFile() ? readJ(af) : new JSONObject();
        JSONArray am = arc.optJSONObject("ranked") != null ? arc.optJSONObject("ranked").optJSONArray("matches") : null;
        boolean readyIn = false;
        for (int i = 0; am != null && i < am.length(); i++) if (ready.optString("id").equals(am.optJSONObject(i).optString("id"))) readyIn = "ready".equals(am.optJSONObject(i).optString("status"));
        ok(af.getName().matches("ranked-s1-season-\\d{8}-\\d{6}\\.json") && arc.optInt("v") == 1 && "ranked_season".equals(arc.optString("kind")) && arc.optLong("archived_at") >= t0 && arc.has("app")
           && League.sameJson(arc.optJSONObject("ranked"), before) && readyIn && arc.optJSONObject("ranked").has("pending"), "보관 파일 " + af.getName() + " — 풀림 · ranked = 바꾸기 전 그대로(준비 경기·잡힌 상대도 그때 그대로)");
        restart();
        ok(League.season() == 2 && League.rankMe().lp == 3310 && League.seasons().size() == 1, "다시 열어도 시즌 2 · LP 3310 · 지난 시즌 1줄");
    }

    /** 처음부터 다시 — 같은 씨앗·배치 5판·비운 칸 · 지난 시즌 줄 이어받기 · 위쪽 칸 그대로 · 체크포인트 지움 · 다시 열어도 이어받기가 안 돎 */
    static void restartTest() throws Exception {
        wipe();
        File dir = leagueDir(); dir.mkdirs();
        JSONObject j = new JSONObject().put("v", 1).put("roster", 2);
        j.put("me", new JSONObject().put("name", "나").put("score", 1100).put("w", 4).put("l", 2).put("d", 0).put("streak", 1).put("best", 3));
        JSONArray os = new JSONArray();
        for (Object[] r : League.ROSTER) os.put(new JSONObject().put("id", r[0]).put("nick", r[1]).put("char", r[2]).put("style", r[3]).put("diff", r[4]).put("score", r[5]).put("w", 0).put("l", 0).put("d", 0));
        os.getJSONObject(0).put("w", 1).put("l", 3);
        j.put("opps", os);
        JSONArray ms = new JSONArray(); long t = 1792000000000L;
        for (String o : new String[]{ "W", "L", "W", "L", "W", "W" }) ms.put(new JSONObject().put("id", UUID.randomUUID().toString()).put("opp", "o01").put("status", "settled").put("outcome", o).put("settled", t++));
        j.put("matches", ms);
        j.put("pref", new JSONObject().put("stage", 3).put("last_rom", "/sdcard/roms/ss2.ngc"));
        write(dbFile(), j.toString());
        RankCore.Me m0 = League.rankMe();
        ok(m0.placementLeft == 0 && League.ranked().has("legacy"), "예전 리그 6판에서 이어받음(배치 없음 · legacy) — 이어받기가 다시 돌면 배치 0 이 된다");
        ok(League.newSeason(), "새 시즌(시즌 2)");
        play("W"); play("L");
        card();
        File ck1 = new File(dir, "ckpt_orphan.state"), ck2 = new File(dir, "ckpt_orphan.state.tmp");
        write(ck1, "s"); write(ck2, "s");
        JSONObject lg = League.newMatch("o01");                  // 예전 칸(위쪽 matches)에 «준비» 경기 — 처음부터 다시가 안 건드려야
        ok(lg != null && "ready".equals(lg.optString("status")) && League.resetBlockedWhy() == null, "예전 칸 «준비» 경기가 열려 있어도 막지 않음");
        JSONObject top0 = copy(dbNow()); top0.remove("ranked");
        JSONObject before = copy(League.ranked());
        ok(League.restartRanked(), "처음부터 다시");
        JSONObject r = League.ranked(); RankCore.Me me = League.rankMe();
        ok(r.optString("seed").equals(before.optString("seed")) && r.optInt("rv") == before.optInt("rv") && r.optInt("gen") == before.optInt("gen"), "같은 rv·gen·씨앗(같은 세상)");
        ok(me.placementLeft == 5 && me.games == 0 && me.lp == 0 && me.peakLp == 0 && Math.abs(me.mmr - 1000) < 1e-9 && me.w + me.l + me.d == 0 && me.streak + me.lstreak + me.best == 0
           && !me.master && !me.shield && me.mr == 0, "배치 5판 · 판수 0 · LP 0 · MMR 1000 · 승패·연승 0");
        ok(r.optJSONObject("players").length() == 0 && r.optJSONArray("matches").length() == 0 && r.optJSONArray("recent").length() == 0
           && !r.has("pending") && !r.has("legacy") && !r.has("last_win_day"), "상대 전적 {} · 경기 기록 [] · 최근 상대 [] · 잡힌 상대·legacy·오늘 첫 승 없음");
        List<JSONObject> rows = League.seasons();
        ok(League.season() == 3 && rows.size() == 2 && "season".equals(rows.get(0).optString("kind")) && rows.get(0).optInt("n") == 1 && "restart".equals(rows.get(1).optString("kind"))
           && rows.get(1).optInt("n") == 2 && rows.get(1).optInt("w") == 1 && rows.get(1).optInt("l") == 1, "시즌 3 · 지난 시즌 줄 이어받기 + restart 줄(시즌 2: 1승 1패)");
        JSONObject top1 = copy(dbNow()); top1.remove("ranked");
        ok(League.sameJson(top0, top1) && "ready".equals(League.matchById(lg.optString("id")).optString("status")), "위쪽 me·opps·matches(예전 «준비» 경기 포함)·pref(last_rom 포함) 그대로");
        ok(!ck1.exists() && !ck2.exists(), "체크포인트(ckpt_*.state·.tmp) 지움");
        File af = new File(League.archiveDir(), rows.get(1).optString("file"));
        JSONObject arc = af.isFile() ? readJ(af) : new JSONObject();
        ok(af.getName().matches("ranked-s2-restart-\\d{8}-\\d{6}\\.json") && "ranked_restart".equals(arc.optString("kind")) && League.sameJson(arc.optJSONObject("ranked"), before)
           && archiveFiles() == 2, "보관 파일 " + af.getName() + " — ranked = 바꾸기 전 그대로 · 지난 보관 파일도 남음");
        int[] c = League.careerWLD();
        ok(c[0] == rows.get(0).optInt("w") + rows.get(1).optInt("w") && c[1] == rows.get(0).optInt("l") + rows.get(1).optInt("l"), "통산 = 지난 시즌 줄 합 + 이번(0)");
        restart();
        ok(League.rankMe().placementLeft == 5 && !League.ranked().has("legacy") && League.ranked().optString("seed").equals(before.optString("seed")) && League.season() == 3,
           "다시 열어도 배치 5 · legacy 없음(예전 기록 이어받기가 다시 안 돎)");
    }

    /** pref.last_rom — 바뀔 때만 쓴다 */
    static void lastRom() throws Exception {
        wipe();
        League.ranked();
        ok(League.lastRom() == null && !League.db().has("pref"), "처음엔 없음(pref 칸도 안 만듦)");
        ok(League.setLastRom("/sdcard/roms/ss2.ngc") && "/sdcard/roms/ss2.ngc".equals(League.lastRom()), "set → get");
        File f = dbFile(); f.setLastModified(1_000_000L); byte[] b = bytes(f);
        ok(League.setLastRom("/sdcard/roms/ss2.ngc") && f.lastModified() == 1_000_000L && Arrays.equals(b, bytes(f)), "같은 경로를 다시 — 파일 안 씀");
        restart();
        ok("/sdcard/roms/ss2.ngc".equals(League.lastRom()), "다시 열어도 그대로");
        ok(League.setLastRom("/sdcard/roms/ss2_h1.ngc") && "/sdcard/roms/ss2_h1.ngc".equals(League.lastRom()) && f.lastModified() != 1_000_000L, "바뀌면 씀");
    }

    /** 147 이 쓴 파일 — 기본값(시즌 1·seasons 없음·miss 0·last_rom 없음)으로 읽고, 사용자가 뭘 하기 전엔 한 바이트도 안 바뀜 */
    static void oldFile() throws Exception {
        wipe();
        File dir = leagueDir(); dir.mkdirs();
        long now = System.currentTimeMillis();
        JSONObject j = new JSONObject().put("v", 1).put("roster", 2);
        j.put("me", new JSONObject().put("name", "나").put("score", 1000).put("w", 0).put("l", 0).put("d", 0).put("streak", 0).put("best", 0));
        JSONArray os = new JSONArray();
        for (Object[] r : League.ROSTER) os.put(new JSONObject().put("id", r[0]).put("nick", r[1]).put("char", r[2]).put("style", r[3]).put("diff", r[4]).put("score", r[5]).put("w", 0).put("l", 0).put("d", 0));
        j.put("opps", os).put("matches", new JSONArray()).put("pref", new JSONObject().put("stage", -1));
        JSONObject kn = new JSONObject().put("diff", 1).put("lv", 4).put("cap", 6).put("floor", 2).put("atk", 0xD9).put("dfn", 0x126);
        JSONObject r = new JSONObject().put("rv", 1).put("gen", 1).put("seed", "00000000c0ffee01").put("season", 1).put("season_start", now - 10 * 86_400_000L)
            .put("mmr", 1012.3).put("games", 9).put("placement", 0).put("lp", 2440).put("shield", false).put("master", false).put("mr", 0).put("peak_lp", 2500)
            .put("w", 5).put("l", 4).put("d", 0).put("streak", 1).put("lstreak", 0).put("best", 3).put("last_win_day", RankCore.today(now) - 1)
            .put("recent", new JSONArray().put("p0650001"))
            .put("players", new JSONObject().put("p0650001", new JSONObject().put("w", 1).put("l", 0).put("d", 0).put("last", 1).put("broke", 0).put("mmr_adj", -3.2).put("lp_adj", -25).put("at", now - 7200_000L)))
            .put("pending", new JSONObject().put("id", "p0650002").put("at", now - 3600_000L).put("mmr", 1001.5).put("stage", 3).put("knobs", kn))
            .put("matches", new JSONArray().put(new JSONObject().put("id", "m147").put("mode", "ranked").put("opp", "p0650001").put("created", now - 2000).put("status", "settled")
                .put("outcome", "W").put("lp_delta", 95).put("settled", now - 1000).put("tier_before", "검객 ★1")));
        j.put("ranked", r);
        File f = dbFile();
        write(f, j.toString(1));
        f.setLastModified(1_000_000L); byte[] b0 = bytes(f);
        ok(League.season() == 1 && League.seasons().isEmpty() && League.seasonStart() == now - 10 * 86_400_000L && League.lastRom() == null, "147 파일: 시즌 1 · 지난 시즌 없음 · last_rom 없음");
        int[] c = League.careerWLD();
        ok(c[0] == 5 && c[1] == 4 && c[2] == 0, "통산 = 이번 시즌 그대로(지난 줄 없음)");
        League.Today td = League.rankedToday();
        ok(td.games() <= 1 && League.voidReady("x") == 0 && League.resetBlockedWhy() == null && League.newSeasonPreview() != null && League.holds(10).isEmpty(), "읽기만 하는 것들(오늘 전적·voidReady·막힘·미리보기·목록)");
        League.bonusLeft();
        RankCore.Pick pk = League.rankedPick(C);
        ok(pk.pending && "p0650002".equals(pk.p.id) && "p0650002".equals(League.rankMe().pendingId), "147 의 잡힌 상대(miss 칸 없음 = 0)를 그대로 따름");
        ok(League.holdPending(pk), "같은 상대 다시 잡기 — 쓸 것 없음");
        ok(f.lastModified() == 1_000_000L && Arrays.equals(b0, bytes(f)), "사용자가 뭘 하기 전엔 league.json 한 바이트도 안 바뀜");
        ok(League.setLastRom("/sdcard/roms/ss2.ngc"), "사용자 동작(리그 열기 → last_rom)");
        JSONObject j2 = readJ(f);
        ok("p0650002".equals(j2.optJSONObject("ranked").optJSONObject("pending").optString("id")) && !j2.optJSONObject("ranked").optJSONObject("pending").has("miss")
           && !j2.optJSONObject("ranked").has("seasons") && j2.optJSONObject("ranked").optInt("season") == 1 && "/sdcard/roms/ss2.ngc".equals(j2.optJSONObject("pref").optString("last_rom"))
           && j2.optJSONObject("pref").optInt("stage") == -1, "그 뒤 저장 — 147 칸 그대로 + last_rom 만 더함");
    }
}

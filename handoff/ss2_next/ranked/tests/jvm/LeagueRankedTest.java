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
        JSONObject r0 = League.ranked();
        RankCore.Me me = League.rankMe();
        ok(r0 != null && me.placementLeft == 5 && me.mmr == 1000 && r0.optString("seed").length() == 16, "새 기록: 랭크 칸(씨앗 16자리) · 배치 5판 · MMR 1000");
        String seed = r0.optString("seed");
        restart();
        ok(seed.equals(League.ranked().optString("seed")), "재시작 뒤 같은 씨앗(같은 세상)");

        // 1) 찾기 → 잡힌 상대
        RankCore.Pick p1 = League.rankedPick(C);
        ok(p1 != null && p1.p != null && !p1.pending && League.ranked().optJSONObject("pending").optString("id").equals(p1.p.id), "찾기 — 고른 상대를 카드 전에 «잡힘»으로 저장");
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
           && League.ranked().optJSONObject("pending") != null, "CPU 단계가 다르면 «난도 불일치» 보류 — LP·전적 그대로, 잡힌 상대도 그대로");
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
        while (tries++ < 6) {
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
        System.out.println("FAILS " + fails);
        System.exit(fails == 0 ? 0 : 1);
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
}

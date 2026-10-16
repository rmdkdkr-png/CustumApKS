package com.dudu.pocketcore;
import org.json.*; import java.io.*; import java.nio.file.Files; import java.util.*;
/** run_compat147.sh 2단계(147 = 7b35ba2 소스로 컴파일) — 148 이 쓴 파일을 147 League 가 읽고 다시 써도 148 칸(season·seasons·pending.miss·무효 칸·last_rom)이 남나(spec §4.4) */
public class Compat147Check {
    static int fails = 0, passes = 0;
    static void ok(boolean c, String what) { System.out.println((c ? "PASS " : "FAIL ") + what); if (c) passes++; else fails++; }
    static JSONObject readJ(File f) throws Exception { return new JSONObject(new String(Files.readAllBytes(f.toPath()), "UTF-8")); }
    static boolean same(Object a, Object b) {
        if (a instanceof JSONObject && b instanceof JSONObject) {
            JSONObject x = (JSONObject) a, y = (JSONObject) b;
            if (x.length() != y.length()) return false;
            Iterator<String> it = x.keys();
            while (it.hasNext()) { String k = it.next(); if (!y.has(k) || !same(x.opt(k), y.opt(k))) return false; }
            return true;
        }
        if (a instanceof JSONArray && b instanceof JSONArray) {
            JSONArray x = (JSONArray) a, y = (JSONArray) b;
            if (x.length() != y.length()) return false;
            for (int i = 0; i < x.length(); i++) if (!same(x.opt(i), y.opt(i))) return false;
            return true;
        }
        if (a instanceof Number && b instanceof Number) return ((Number) a).doubleValue() == ((Number) b).doubleValue();
        return a == null ? b == null : a.equals(b);
    }
    static JSONObject byId(JSONObject j, String id) {
        JSONArray a = j.optJSONObject("ranked").optJSONArray("matches");
        for (int i = 0; i < a.length(); i++) if (id.equals(a.optJSONObject(i).optString("id"))) return a.optJSONObject(i);
        return null;
    }
    public static void main(String[] args) throws Exception {
        File root = new File(System.getProperty("league.root")), f = new File(new File(root, "league"), "league.json");
        String vid = new String(Files.readAllBytes(new File(root, "void_id.txt").toPath()), "UTF-8").trim();
        JSONObject before = readJ(f);
        JSONObject r0 = before.optJSONObject("ranked");
        ok(r0.optInt("season") == 2 && r0.optJSONArray("seasons").length() == 1 && r0.optJSONObject("pending").optInt("miss") == 1
           && byId(before, vid).optBoolean("void_after_start") && "/sdcard/roms/ss2.ngc".equals(before.optJSONObject("pref").optString("last_rom")), "148 이 쓴 파일에 148 칸이 다 있음");
        ok(League.openMatch() == null, "147: 열린 경기 없음(시작한 뒤 무효도 끝난 상태 cancelled)");
        boolean hidden = true; for (JSONObject x : League.holds(50)) hidden &= !vid.equals(x.optString("id"));
        ok(hidden, "147: 시작한 뒤 무효는 랭크 무효처럼 목록에서 숨김");
        RankCore.Me me = League.rankMe();
        ok(me.w == 0 && me.l == 0 && me.lp == r0.optInt("lp") && me.placementLeft == 0, "147: 이번 시즌 전적·LP 를 자기 기록으로 읽음(시즌 1 글자는 꾸밈만)");
        RankCore.Pick pk = League.rankedPick(new android.content.Context());
        ok(pk.pending && pk.p.id.equals(r0.optJSONObject("pending").optString("id")), "147: 148 이 잡은 상대(miss 칸 있음)를 그대로 따름");
        League.setPrefStage(5);                                            // 147 이 파일 전체를 다시 씀
        JSONObject after = readJ(f), r1 = after.optJSONObject("ranked");
        ok(after.optJSONObject("pref").optInt("stage") == 5, "147 이 파일을 다시 씀(pref.stage 5)");
        ok(r1.optInt("season") == 2 && r1.optLong("season_start") == r0.optLong("season_start") && same(r1.optJSONArray("seasons"), r0.optJSONArray("seasons")), "147 이 다시 써도 season·season_start·seasons 그대로");
        ok(same(r1.optJSONObject("pending"), r0.optJSONObject("pending")) && r1.optJSONObject("pending").optInt("miss") == 1, "147 이 다시 써도 pending(miss 1) 그대로");
        JSONObject v0 = byId(before, vid), v1 = byId(after, vid);
        ok(v1 != null && same(v0, v1) && "crash".equals(v1.optString("void_kind")) && "cancelled".equals(v1.optString("status")), "147 이 다시 써도 무효 경기 칸(void_after_start·void_kind·why) 그대로");
        ok("/sdcard/roms/ss2.ngc".equals(after.optJSONObject("pref").optString("last_rom")), "147 이 다시 써도 pref.last_rom 그대로");
        JSONObject b2 = new JSONObject(before.toString()), a2 = new JSONObject(after.toString());
        b2.optJSONObject("pref").put("stage", 5);
        ok(same(a2, b2), "147 이 다시 쓴 파일 = 148 이 쓴 파일 + pref.stage 만 다름");
        System.out.println(fails == 0 ? "ALL PASS (" + passes + ")" : fails + " FAIL / " + (passes + fails));
        if (fails != 0) System.exit(1);
    }
}

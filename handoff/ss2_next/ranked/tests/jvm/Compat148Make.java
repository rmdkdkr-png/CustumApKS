package com.dudu.pocketcore;
import org.json.*; import java.io.*;
/** run_compat147.sh 1단계(148 소스로 컴파일) — 148 칸이 다 든 league.json 을 쓴다: 시즌 2 · seasons 1줄 · pending.miss 1 · 시작한 뒤 무효 1판 · pref.last_rom */
public class Compat148Make {
    public static void main(String[] a) throws Exception {
        android.content.Context C = new android.content.Context();
        JSONObject r = League.ranked();
        r.put("placement", 0).put("lp", 3920).put("mmr", 1090.0).put("w", 7).put("l", 5).put("games", 30).put("peak_lp", 3920);
        League.save();
        if (!League.newSeason()) throw new RuntimeException("newSeason");
        RankCore.Pick pk = League.rankedPick(C);
        League.holdPending(pk);
        League.OppView v = League.oppView(pk.p);
        JSONObject m = League.newRankedMatch(C, v, RankCore.knobs(v.mmr, pk.p.personaIdx), 3, 0);
        League.setStatus(m.optString("id"), "playing", null);
        if (!League.voidStarted(m.optString("id"), "crash")) throw new RuntimeException("voidStarted");
        if (!League.setLastRom("/sdcard/roms/ss2.ngc")) throw new RuntimeException("setLastRom");
        JSONObject p = League.ranked().optJSONObject("pending");
        try (FileOutputStream o = new FileOutputStream(new File(System.getProperty("league.root"), "void_id.txt"))) { o.write(m.optString("id").getBytes("UTF-8")); }
        System.out.println("148 이 씀: 시즌 " + League.season() + " · 지난 시즌 " + League.seasons().size() + "줄 · pending " + p.optString("id") + " miss " + p.optInt("miss")
                + " · 무효 " + m.optString("id") + " · last_rom " + League.lastRom());
    }
}

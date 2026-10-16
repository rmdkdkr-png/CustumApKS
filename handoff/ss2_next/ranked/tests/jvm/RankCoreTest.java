package com.dudu.pocketcore;

import java.util.*;

/** RankCore 시험(호스트 JVM, 의존 없음): javac -d out RankCore.java RankCoreTest.java && java -cp out com.dudu.pocketcore.RankCoreTest */
public class RankCoreTest {
    static int fails = 0, passes = 0;
    static void ok(boolean c, String what) { System.out.println((c ? "PASS " : "FAIL ") + what); if (c) passes++; else fails++; }
    static final long SEED = 0x5EED_2026_1015L;

    /** 시험용 기록부 — League 의 ranked.players 칸 대신 */
    static final class MemBook implements RankCore.Book {
        final Map<String, double[]> adj = new HashMap<>();
        final Map<String, int[]> h2h = new HashMap<>();
        final List<RankCore.Player> rivals = new ArrayList<>();
        public double adj(String id) { double[] a = adj.get(id); return a == null ? 0 : a[0]; }
        public int[] h2h(String id) { int[] h = h2h.get(id); return h == null ? new int[5] : h; }
        public List<RankCore.Player> rivals() { return rivals; }
        final Map<String, Integer> lpAdj = new HashMap<>();
        public int lpAdj(String id) { Integer v = lpAdj.get(id); return v == null ? 0 : v; }
        void record(String id, char out, double oppDelta, int brokeStreak) {
            int[] h = h2h.computeIfAbsent(id, k -> new int[5]);
            if (out == 'W') { h[0]++; h[3] = 1; } else if (out == 'L') { h[1]++; h[3] = -1; if (brokeStreak >= 2) h[4]++; } else { h[2]++; h[3] = 0; }
            double[] a = adj.computeIfAbsent(id, k -> new double[1]);
            a[0] = Math.max(-150, Math.min(150, a[0] + oppDelta));
        }
    }
    static MemBook bookWithLegacy() {
        MemBook b = new MemBook();
        Object[][] R = { { "o01", "칼끝노인", 11, 0, 1, 1000 }, { "o02", "퇴근후한판", 3, 1, 1, 1020 }, { "o03", "달빛나코", 4, 0, 0, 940 },
            { "o04", "새벽검객", 2, 0, 1, 980 }, { "o05", "장미기사", 9, 1, 1, 1030 }, { "o06", "얼음요정", 5, 0, 0, 920 }, { "o07", "그늘닌자", 6, 0, 0, 900 },
            { "o08", "독수리산책", 7, 0, 0, 880 }, { "o09", "불꽃형님", 0, 1, 2, 1060 }, { "o10", "검은달", 8, 1, 2, 1080 }, { "o11", "꽃잎칼날", 13, 0, 2, 1100 },
            { "o12", "끝판왕", 14, 1, 2, 1120 } };
        for (Object[] r : R) b.rivals.add(RankCore.legacy((String) r[0], (String) r[1], (Integer) r[2], (Integer) r[3], (Integer) r[4], (Integer) r[5]));
        return b;
    }

    public static void main(String[] a) {
        pool(); knobs(); tiers(); rating(); matching(); board(); simulate(); waitModel(); reel(); seasonLp();
        System.out.println(fails == 0 ? "ALL PASS (" + passes + ")" : fails + " FAIL / " + (passes + fails));
        if (fails != 0) System.exit(1);
    }

    static void pool() {
        long tot = RankCore.total();
        ok(tot > 39000 && tot < 41000, "풀 인원 " + tot + " (4만 명 안팎)");
        RankCore.Player p1 = RankCore.player(SEED, "p0650123"), p2 = RankCore.player(SEED, "p0650123"), p3 = RankCore.player(SEED + 1, "p0650123");
        ok(p1 != null && p1.nick.equals(p2.nick) && p1.ch == p2.ch && p1.baseMmr == p2.baseMmr && p1.avatar == p2.avatar, "같은 씨앗·같은 id = 같은 사람 (" + p1.nick + " · " + RankCore.CHAR[p1.ch] + ")");
        ok(p3 != null && (!p3.nick.equals(p1.nick) || p3.ch != p1.ch || p3.avatar != p1.avatar), "다른 씨앗이면 다른 사람");
        ok(RankCore.player(SEED, "p9990000") == null && RankCore.player(SEED, "o01") == null && RankCore.player(SEED, "p065999x") == null, "풀 밖 id 는 null");
        int[] combo = new int[30]; Set<String> nicks = new HashSet<>(), ids = new HashSet<>(); int n = 0, bad = 0, yugaLow = 0, yuga = 0, alnum = 0; int[] tier = new int[8];
        RankCore.Rng r = new RankCore.Rng(1);
        for (int i = 0; i < 4000; i++) {
            int b = RankCore.bucketOf(RankCore.MU + r.gauss() * RankCore.SIGMA);
            if (RankCore.bucketCount(b) == 0) continue;
            RankCore.Player p = RankCore.playerAt(SEED, b, r.nextInt(RankCore.bucketCount(b)));
            if (!ids.add(p.id)) continue;                  // 같은 사람을 두 번 뽑은 것은 빼고
            n++; combo[p.ch * 2 + p.sty]++; nicks.add(p.nick);
            if (!RankCore.supported(p.ch, p.sty) || !League_oppSupported(p.ch, p.sty)) bad++;
            if (p.ch == 14) { yuga++; if (p.baseMmr < 1400) yugaLow++; }
            if (p.nick.matches(".*[a-zA-Z].*")) alnum++;
            tier[RankCore.tierOf(p.lp(20000, 0, 0))]++;
            if (p.id.equals("x")) bad++;
        }
        int combos = 0; for (int c : combo) if (c > 0) combos++;
        ok(bad == 0, "주캐는 모두 CPU 가 싸우는 조합(League.oppSupported 와 같음)");
        ok(combos >= 22, "주캐 조합이 고루 나옴 (" + combos + "/24, 표본 " + n + ")");
        ok(yugaLow == 0, "유가 주캐는 MMR 1400 이상에만 (" + yuga + "명)");
        ok(nicks.size() > n * 0.93, "닉네임 겹침 적음 (" + nicks.size() + "/" + n + ")");
        ok(alnum > n * 0.10 && alnum < n * 0.30, "영문 아이디 섞임 " + alnum * 100 / n + "%");
        StringBuilder sb = new StringBuilder();
        for (int t = 0; t < 8; t++) sb.append(RankCore.TIER[t]).append(' ').append(tier[t] * 100 / n).append("% ");
        ok(tier[0] + tier[1] < n * 0.25 && tier[3] + tier[4] > n * 0.35, "티어 분포가 그럴듯(표본): " + sb);
        int[] all = new int[8]; long cnt = 0;
        for (int b = 0; b < RankCore.NB; b++) for (int s = 0; s < RankCore.bucketCount(b); s++) { all[RankCore.tierOf(RankCore.playerAt(SEED, b, s).lp(20000, 0, 0))]++; cnt++; }
        ok(all[7] > 40 && all[7] < 400 && all[0] < cnt * 0.12, "풀 전체 " + cnt + "명: 무쌍 " + all[7] + "명 · 검성 " + all[6] + " · 수련생 " + all[0]);
        // 실제 같은 프로필 몇 명 찍어 보기
        for (int i = 0; i < 6; i++) {
            int b = RankCore.bucketOf(700 + i * 180);
            RankCore.Player p = RankCore.playerAt(SEED, b, i * 7 % Math.max(1, RankCore.bucketCount(b)));
            System.out.println("     · " + p.id + " " + p.nick + " · " + p.region + " · «" + p.title + "» · " + RankCore.CHAR[p.ch] + " " + RankCore.STYLE[p.sty]
                    + " · " + p.persona + " · " + RankCore.label(p.lp(20000, 0, 0)) + " LP " + p.lp(20000, 0, 0) + " · MMR " + Math.round(p.mmr(20000, 0)) + " · " + p.knobs(20000, 0));
        }
    }
    static boolean League_oppSupported(int ch, int st) {   // League.java 의 BAD_OPP 그대로(복사) — 두 표가 어긋나면 이 시험이 잡는다
        int[] BAD = { (1 << 1) | 0, (4 << 1) | 1, (5 << 1) | 1, (6 << 1) | 1, (10 << 1) | 1, (12 << 1) | 1 };
        for (int b : BAD) if (b == ((ch << 1) | st)) return false;
        return ch >= 0 && ch <= 14 && st >= 0 && st <= 1;
    }

    static void knobs() {
        RankCore.Knobs e = RankCore.knobs(800, 0), m = RankCore.knobs(1000, 0), h = RankCore.knobs(1200, 0);
        ok(e.lv == 1 && e.cap == 3 && e.atk == 0xC0 && e.dfn == 0x140, "MMR 800 = 게임 난도 하 첫 경기 값 (" + e + ")");
        ok(m.lv == 4 && m.cap == 6 && m.atk == 0xD9 && m.dfn == 0x126, "MMR 1000 = 난도 중 (" + m + ")");
        ok(h.lv == 7 && h.cap == 9 && h.atk == 0xF3 && h.dfn == 0x10C, "MMR 1200 = 난도 상 (" + h + ")");
        boolean mono = true, inRange = true; double prev = 0;
        for (int x = 300; x <= 2300; x += 5) {
            RankCore.Knobs k = RankCore.knobs(x, 0);
            mono &= k.strength() >= prev - 1e-9; prev = k.strength();
            inRange &= k.lv >= 0 && k.lv <= 15 && k.cap >= k.lv && k.cap <= 15 && k.atk >= 0xA0 && k.atk <= 0x134 && k.dfn >= 0xE0 && k.dfn <= 0x160 && k.floor <= k.lv;
        }
        ok(mono, "세기(atk/dfn × 단계 효과)가 MMR 따라 줄지 않음");
        ok(inRange, "손잡이 범위: 단계 0~15 · 상한 ≥ 단계 · 공격 0xA0~0x134 · 받는 피해 0xE0~0x160 · 바닥 ≤ 단계");
        double r0 = RankCore.knobs(1000, 0).strength();
        boolean pers = true;
        for (int p = 1; p < 4; p++) pers &= Math.abs(Math.log(RankCore.knobs(1000, p).strength() / r0)) < 0.12;
        ok(pers, "성향(공격·한방·끈기)은 세기를 크게 안 바꿈(±12% 안) — 느낌만 다름");
    }

    static void tiers() {
        ok(RankCore.label(0).equals("수련생 ★1") && RankCore.label(499).equals("수련생 ★5") && RankCore.label(500).equals("낭인 ★1") && RankCore.label(2250).equals("검객 ★1")
           && RankCore.label(8999).equals("검성 ★5") && RankCore.label(9000).equals("무쌍"), "티어 이름·별: 0 수련생★1 · 500 낭인★1 · 2250 검객★1 · 8999 검성★5 · 9000 무쌍");
        boolean inv = true;
        for (int lp = 0; lp <= 9000; lp += 50) inv &= Math.abs(RankCore.lpOfMmr(RankCore.mmrOfLp(lp)) - lp) < 1e-6;
        ok(inv, "LP ↔ MMR 기준선이 서로 역함수");
        ok(Math.abs(RankCore.lpOfMmr(1000) - 2250) < 1e-9 && RankCore.tierOf((int) RankCore.lpOfMmr(800)) == 1, "난도 중 실력 = 검객 ★1 · 난도 하 = 낭인");
    }

    static RankCore.Me fresh() { RankCore.Me me = new RankCore.Me(); me.placementLeft = 0; me.games = 30; return me; }
    static void rating() {
        RankCore.Me me = fresh(); me.mmr = 1000; me.lp = 2400;
        RankCore.Outcome o = RankCore.settle(me, 'W', 1000, 0, false, 1);
        ok(o.lpDelta >= 90 && o.lpDelta <= 140, "같은 실력 상대 이기면 +" + o.lpDelta + " (오늘 첫 승 +30 포함)");
        o = RankCore.settle(me, 'L', 1000, 0, false, 1);
        ok(o.lpDelta <= -60 && o.lpDelta >= -100, "같은 실력 상대에게 지면 " + o.lpDelta);
        RankCore.Me a = fresh(); a.mmr = 1000; a.lp = 2400; RankCore.Me b = fresh(); b.mmr = 1000; b.lp = 2400; a.lastWinDay = b.lastWinDay = 1;
        int dUp = RankCore.settle(a, 'W', 1200, 0, false, 1).lpDelta, dDn = RankCore.settle(b, 'W', 800, 0, false, 1).lpDelta;
        ok(dUp > dDn, "센 상대를 이기면 더 많이 (+" + dUp + " > +" + dDn + ")");
        RankCore.Me lo = fresh(); lo.mmr = 600; lo.lp = 200;
        ok(RankCore.settle(lo, 'L', 650, 0, false, 1).lpDelta == 0, "수련생은 져도 안 깎임");
        RankCore.Me r1 = fresh(); r1.mmr = 700; r1.lp = 520;
        o = RankCore.settle(r1, 'L', 700, 0, false, 1);
        ok(r1.lp == 500 && !o.demoted, "낭인 바닥 아래로는 안 떨어짐(수련생 강등 없음) LP " + r1.lp);
        RankCore.Me s = fresh(); s.mmr = 1000; s.lp = 2260;
        o = RankCore.settle(s, 'L', 1000, 0, false, 1);
        ok(s.lp == 2250 && s.shield && o.shieldUsed && o.event.startsWith("강등 위기"), "검객 바닥에서 지면 «강등 위기»(바닥에 머묾) — " + o.event);
        o = RankCore.settle(s, 'L', 1000, 0, false, 1);
        ok(o.demoted && RankCore.tierOf(s.lp) == 2 && RankCore.starOf(s.lp) == 4 && !s.shield, "강등 위기에서 또 지면 무사 ★4 로 — " + o.event + " LP " + s.lp);
        RankCore.Me s2 = fresh(); s2.mmr = 1000; s2.lp = 2250; s2.shield = true;
        RankCore.settle(s2, 'W', 1000, 0, false, 1);
        ok(!s2.shield, "이기면 강등 위기 풀림");
        RankCore.Me up = fresh(); up.mmr = 1200; up.lp = 3460; up.lastWinDay = 1;
        o = RankCore.settle(up, 'W', 1200, 0, false, 1);
        ok(o.promoted && o.event.startsWith("승급! 검호"), "검객 → 검호 승급 — " + o.event);
        RankCore.Me st = fresh(); st.mmr = 1000; st.lp = 2500; st.streak = 3; st.lastWinDay = 1;
        o = RankCore.settle(st, 'W', 1000, 0, true, 1);
        ok(o.bonusStreak == 20 && o.bonusRevenge == 20 && o.bonusDaily == 0, "4연승 보너스 +20 · 설욕(재대결 승) +20 · 오늘 첫 승은 이미 받음");
        RankCore.Me ms = fresh(); ms.mmr = 1650; ms.lp = 8960; ms.lastWinDay = 1;
        o = RankCore.settle(ms, 'W', 1650, 0, false, 1);
        ok(o.enteredMaster && ms.master && ms.lp == 9000 && ms.mr >= 1500, "검성 → 무쌍(MR " + ms.mr + ")");
        int mr0 = ms.mr; RankCore.settle(ms, 'L', 1650, 1600, false, 1);
        ok(ms.master && ms.lp == 9000 && ms.mr < mr0, "무쌍은 강등 없이 MR 만 (" + mr0 + " → " + ms.mr + ")");
        RankCore.Me pl = new RankCore.Me();
        for (int i = 0; i < 4; i++) RankCore.settle(pl, 'W', pl.mmr, 0, false, 1);
        ok(pl.lp == 0 && pl.placementLeft == 1, "배치 중엔 LP 0 그대로(배치 4/5)");
        o = RankCore.settle(pl, 'W', pl.mmr, 0, false, 1);
        ok(o.placementDone && pl.lp > 0 && pl.mmr > 1150, "배치 5연승 → MMR " + Math.round(pl.mmr) + " · " + o.event);
        RankCore.Me dr = fresh(); dr.mmr = 1000; dr.lp = 2400;
        ok(RankCore.settle(dr, 'D', 1000, 0, false, 1).lpDelta == 0, "무승부는 LP 그대로");
        RankCore.Me g1 = fresh(); g1.mmr = 1300; g1.lp = 2400; g1.lastWinDay = 1; RankCore.Me g2 = fresh(); g2.mmr = 1000; g2.lp = 2400; g2.lastWinDay = 1;
        ok(RankCore.settle(g1, 'W', 1300, 0, false, 1).lpDelta > RankCore.settle(g2, 'W', 1000, 0, false, 1).lpDelta, "실력(MMR)이 LP 보다 위면 더 빨리 오른다(LP 가 실력을 따라감)");
        RankCore.Me sk = fresh(); sk.mmr = 1000; sk.lp = 2400;
        int[] stk = RankCore.stakes(sk, 1000);
        ok(stk != null && stk[0] > 0 && stk[1] < 0, "카드에 걸린 LP «이기면 +" + stk[0] + " · 지면 " + stk[1] + "»");
    }

    static void matching() {
        MemBook book = bookWithLegacy();
        RankCore.Me me = fresh(); me.mmr = 1050; me.lp = 2500;
        RankCore.Rng r = new RankCore.Rng(42);
        int rep5 = 0, near = 0, rival = 0, n = 400, sameChar3 = 0; long msMin = Long.MAX_VALUE, msMax = 0; double sumGap = 0;
        int[] lastCh = { -1, -1 };
        for (int i = 0; i < n; i++) {
            RankCore.Pick pk = RankCore.pick(SEED, me, 20000, book, r);
            if (me.recent.subList(0, Math.min(5, me.recent.size())).contains(pk.p.id)) rep5++;
            if (Math.abs(pk.mmr - me.mmr) <= 150) near++;
            if (pk.p.legacy) rival++;
            if (pk.p.ch == lastCh[0] && pk.p.ch == lastCh[1]) sameChar3++;
            lastCh[1] = lastCh[0]; lastCh[0] = pk.p.ch;
            sumGap += pk.mmr - me.mmr;
            msMin = Math.min(msMin, pk.searchMs); msMax = Math.max(msMax, pk.searchMs);
            me.recent.add(0, pk.p.id); if (me.recent.size() > 12) me.recent.remove(12);
            book.record(pk.p.id, r.nextInt(2) == 0 ? 'W' : 'L', 0, 0);
        }
        ok(rep5 == 0, "최근 5명은 다시 안 나옴(재대결 빼고)");
        ok(near > n * 0.85, "상대 MMR 이 내 근처(±150 안 " + near * 100 / n + "%)");
        ok(rival > n * 0.04 && rival < n * 0.2, "라이벌(예전 12명) 가끔 " + rival * 100 / n + "%");
        ok(sameChar3 < n * 0.03, "같은 캐릭터 세 번 연속 드묾 (" + sameChar3 + ")");
        ok(msMin >= 2000 && msMax <= 6100, "찾는 시간 " + msMin + "~" + msMax + "ms");
        ok(Math.abs(sumGap / n) < 25, "평소엔 위·아래 고르게 (평균 차 " + Math.round(sumGap / n) + ")");
        RankCore.Me hot = fresh(); hot.mmr = 1050; hot.streak = 6; double g = 0;
        RankCore.Me cold = fresh(); cold.mmr = 1050; cold.lstreak = 5; double c = 0;
        for (int i = 0; i < 200; i++) { g += RankCore.pick(SEED, hot, 20000, new MemBook(), r).mmr - 1050; c += RankCore.pick(SEED, cold, 20000, new MemBook(), r).mmr - 1050; }
        ok(g / 200 > 60 && c / 200 < -40, "연승 중엔 센 상대(평균 +" + Math.round(g / 200) + "), 연패 중엔 조금 약한 상대(" + Math.round(c / 200) + ")");
        RankCore.Me top = fresh(); top.mmr = 1750;
        long ms = 0; for (int i = 0; i < 50; i++) ms += RankCore.pick(SEED, top, 20000, new MemBook(), r).searchMs;
        ok(ms / 50 > 7000, "상위권은 오래 찾음(평균 " + ms / 50 + "ms)");
        me.pendingId = "p0650001";
        RankCore.Pick pp = RankCore.pick(SEED, me, 20000, book, r), pp2 = RankCore.pick(SEED, me, 20000, book, r);
        ok(pp.pending && pp.p.id.equals("p0650001") && pp2.p.id.equals("p0650001"), "잡힌 상대는 붙을 때까지 다시 나옴(카드에서 나가도)");
        me.pendingId = null;
        RankCore.Pick d1 = RankCore.pick(SEED, me, 20000, book, new RankCore.Rng(7)), d2 = RankCore.pick(SEED, me, 20000, book, new RankCore.Rng(7));
        ok(d1.p.id.equals(d2.p.id) && d1.searchMs == d2.searchMs, "같은 난수 씨앗이면 같은 매칭(시험·재현용)");
        MemBook bk = new MemBook(); bk.record("p0650002", 'L', 0, 3);
        RankCore.Me tm = fresh(); tm.pendingId = "p0650002";
        RankCore.Pick tp = RankCore.pick(SEED, tm, 20000, bk, r);
        ok(tp.tags.contains("설욕전") && tp.tags.contains("내 연승을 끊은 상대"), "꼬리표: " + tp.tags);
    }

    static void board() {
        MemBook book = bookWithLegacy();
        List<RankCore.Row> t = RankCore.top(SEED, 20000, 100, book, 2400, "나");
        boolean sorted = true, contiguous = true;
        for (int i = 1; i < t.size(); i++) {
            RankCore.Row x = t.get(i - 1), y = t.get(i);
            sorted &= RankCore.key(x.lp, x.lp >= 9000, x.mr) >= RankCore.key(y.lp, y.lp >= 9000, y.mr);
            contiguous &= y.rank == x.rank + 1;
        }
        ok(t.size() == 100 && sorted && contiguous && t.get(0).rank == 1, "위 100명: 순서·순위 번호 이어짐");
        ok(t.get(0).label.equals("무쌍") && t.get(0).mr > 1600, "1위 = 무쌍 MR " + t.get(0).mr + " (" + t.get(0).nick + ")");
        System.out.println("     · 1~5위: " + t.get(0).nick + " " + t.get(0).mr + " / " + t.get(1).nick + " " + t.get(1).mr + " / " + t.get(2).nick + " " + t.get(2).mr
                + " / " + t.get(3).nick + " / " + t.get(4).nick + " · 100위 " + t.get(99).label + " " + (t.get(99).lp >= 9000 ? "MR " + t.get(99).mr : "LP " + t.get(99).lp));
        List<RankCore.Row> t2 = RankCore.top(SEED, 20000, 100, book, 2400, "나");
        ok(t2.get(0).id.equals(t.get(0).id) && t2.get(50).id.equals(t.get(50).id), "같은 날 = 같은 순위표");
        List<RankCore.Row> t3 = RankCore.top(SEED, 20003, 100, book, 2400, "나");
        int moved = 0; for (int i = 0; i < 100; i++) if (!t3.get(i).id.equals(t.get(i).id)) moved++;
        ok(moved > 10, "사흘 뒤엔 순위가 움직임 (" + moved + "/100 자리 바뀜)");
        long rk1 = RankCore.rankOf(SEED, 20000, book, 2400), rk2 = RankCore.rankOf(SEED, 20000, book, 3600), rk3 = RankCore.rankOf(SEED, 20000, book, 600);
        ok(rk2 < rk1 && rk1 < rk3 && rk3 <= RankCore.total(), "LP 높을수록 순위 높음 (LP 3600 → " + rk2 + "위 · 2400 → " + rk1 + "위 · 600 → " + rk3 + "위 / " + RankCore.total() + "명)");
        long rkTop = RankCore.rankOf(SEED, 20000, book, 1_000_000L + 2100);
        ok(rkTop <= 5, "MR 2100 무쌍이면 위 5 안 (" + rkTop + "위)");
        List<RankCore.Row> ar = RankCore.around(SEED, 20000, book, 2400, "나", 3);
        int mi = -1; for (int i = 0; i < ar.size(); i++) if (ar.get(i).me) mi = i;
        boolean br = mi >= 0;
        for (int i = 0; i < ar.size(); i++) if (i < mi) br &= ar.get(i).lp >= 2400; else if (i > mi) br &= ar.get(i).lp <= 2400;
        ok(br && ar.size() >= 5 && ar.get(mi).rank == rk1, "내 주변: 위는 LP 높고 아래는 낮음, 내 순위 " + rk1 + " (" + ar.size() + "줄)");
        List<RankCore.Row> arTop = RankCore.around(SEED, 20000, book, 1_000_000L + 1900, "나", 2);
        boolean found = false; for (RankCore.Row r : arTop) found |= r.me;
        ok(found, "상위권이면 내 주변도 위 150 표에서 그대로");
        // 리뷰 고침: 무쌍 MR 1500(위 150 밖) — 내 줄에 MR, 무쌍 줄은 순위 번호 따라 MR 이 줄어듦
        long mk = 1_000_000L + 1500;
        List<RankCore.Row> am = RankCore.around(SEED, 20000, book, mk, "나", 5);
        RankCore.Row meRow = null; boolean mono = true; long prev = Long.MAX_VALUE;
        for (RankCore.Row x : am) {
            long kx = x.me ? mk : RankCore.key(x.lp, x.lp >= 9000, x.mr);
            mono &= kx <= prev; prev = kx;
            if (x.me) meRow = x;
        }
        ok(meRow != null && meRow.rank > 150 && meRow.mr == 1500 && mono, "무쌍 내 주변: 내 줄 MR " + (meRow != null ? meRow.mr : -1) + " · " + (meRow != null ? meRow.rank : -1) + "위 · 열쇠 순서대로");
        // 리뷰 고침: 순위표 줄의 LP 에 나와의 경기로 바뀐 LP(lp_adj)
        RankCore.Row r0 = null; for (RankCore.Row x : RankCore.around(SEED, 20000, book, 2400, "나", 3)) if (!x.me && r0 == null) r0 = x;
        MemBook b2 = bookWithLegacy(); b2.lpAdj.put(r0.id, -120);
        RankCore.Row r1 = null; for (RankCore.Row x : RankCore.around(SEED, 20000, b2, 2400, "나", 60)) if (x.id.equals(r0.id)) r1 = x;
        ok(r0.lp < 9000 && r1 != null && r1.lp == r0.lp - 120, "순위표 LP 에 lp_adj 반영 (" + r0.lp + " → " + (r1 != null ? r1.lp : -1) + ")");
        // 2차 리뷰 고침: MR 1500 아래 무쌍도 무쌍 아닌 사람(8990 LP)보다 위 · 내 주변 위쪽 줄이 있음
        long rkNm = RankCore.rankOf(SEED, 20000, book, 8990), rk1400 = RankCore.rankOf(SEED, 20000, book, 1_000_000L + 1400), rk1350 = RankCore.rankOf(SEED, 20000, book, 1_000_000L + 1350);
        List<RankCore.Row> a14 = RankCore.around(SEED, 20000, book, 1_000_000L + 1400, "나", 3);
        int me14 = -1; for (int i = 0; i < a14.size(); i++) if (a14.get(i).me) me14 = i;
        ok(rk1400 <= rkNm && rk1350 <= rkNm && me14 >= 1, "낮은 MR 무쌍도 8990 LP 보다 위 (MR1400 " + rk1400 + "위 · MR1350 " + rk1350 + "위 · 8990LP " + rkNm + "위) · 내 주변 위 " + me14 + "줄");
        boolean under = true; for (int d = 19000; d < 21000; d++) under &= RankCore.activeToday(SEED, d) < RankCore.total();
        ok(under, "오늘 접속 인원은 늘 전체보다 적음(2000일)");
    }

    /** 사람 실력 T(이 MMR 의 CPU 를 반반 이김)로 경기를 이어 하면 MMR·LP 가 실력으로 수렴하나 — 승률 = Elo(T − 상대 MMR). E5 봇 사다리가 이 척도와 맞았다 */
    static void simulate() {
        int[] T = { 650, 1000, 1300, 1750 };
        for (int t : T) {
            MemBook book = bookWithLegacy();
            RankCore.Me me = new RankCore.Me();
            RankCore.Rng r = new RankCore.Rng(t * 31L);
            int toTier = -1, matches = 200; double sumAbs = 0; int nAbs = 0; int maxTier = 0, wins = 0;
            for (int i = 0; i < matches; i++) {
                RankCore.Pick pk = RankCore.pick(SEED, me, 20000 + i / 15, book, r);
                double p = RankCore.expect(t, pk.mmr);
                char out = r.nextDouble() < p ? 'W' : 'L';
                if (out == 'W') wins++;
                boolean revenge = !me.recent.isEmpty() && me.recent.get(0).equals(pk.p.id) && book.h2h(pk.p.id)[3] == -1;
                int stBefore = me.streak;
                RankCore.Outcome o = RankCore.settle(me, out, pk.mmr, pk.p.mr(20000, book.adj(pk.p.id)), revenge, 20000 + i / 15);
                book.record(pk.p.id, out, o.oppMmrDelta, out == 'L' ? stBefore : 0);
                me.recent.add(0, pk.p.id); if (me.recent.size() > 12) me.recent.remove(12);
                maxTier = Math.max(maxTier, me.master ? 7 : RankCore.tierOf(me.lp));
                if (i >= 100) { sumAbs += Math.abs(me.mmr - t); nAbs++; }
                if (toTier < 0 && me.placementLeft == 0 && (Math.abs(RankCore.mmrOfLp(me.lp) - t) < 120 || me.master && t >= 1600)) toTier = i + 1;
            }
            double lpT = Math.min(9000, RankCore.lpOfMmr(t));
            System.out.println(String.format("     · 실력 %4d: MMR %4.0f · %s LP %d (기준 %4.0f) · 승률 %d%% · 최고 %s · 실력 LP 근처까지 %s판",
                    t, me.mmr, me.master ? "무쌍 MR " + me.mr : RankCore.label(me.lp), me.lp, lpT, wins * 100 / matches, RankCore.TIER[maxTier], toTier < 0 ? "-" : String.valueOf(toTier)));
            ok(sumAbs / nAbs < 110, "실력 " + t + ": 100판 뒤 MMR 이 실력 근처(평균 오차 " + Math.round(sumAbs / nAbs) + ")");
            ok(t >= 1600 ? me.master || me.lp > 8000 : Math.abs(me.lp - lpT) < 1100, "실력 " + t + ": 200판 뒤 LP 가 기준선 근처");
            ok(toTier > 0 && toTier <= (t >= 1600 ? 200 : 120), "실력 " + t + ": 실력 LP 근처까지 " + toTier + "판");
            ok(wins * 100 / matches >= 40 && wins * 100 / matches <= 66, "실력 " + t + ": 승률 " + wins * 100 / matches + "%(매칭이 실력 근처로 맞춰 줌)");
        }
    }

    /* ── 148: 대기창 시간·릴·새 시즌 LP ─────────────────────────────────── */

    /** 대기창 시간(RankCore.waitMs) — «보통» 4~9초 × 시각, 15초 끝 · «빠르게» = searchMs · 잡힌 상대 1.2~2.4초 · 예상 시간은 늘 넉넉히 */
    static void waitModel() {
        MemBook book = new MemBook();
        RankCore.Rng r = new RankCore.Rng(148);
        boolean inRange = true, fastSame = true, est = true, capped = true; int n = 0;
        for (int i = 0; i < 300; i++) {
            RankCore.Me me = fresh(); me.mmr = 1050;
            RankCore.Pick pk = RankCore.pick(SEED, me, 20000, book, r);
            if (pk.waitU < 0) continue;
            n++;
            for (int h = 0; h < 24; h++) {
                double hf = h >= 19 && h <= 23 ? 0.85 : h >= 2 && h <= 6 ? 1.4 : 1.0;
                long w = RankCore.waitMs(pk, me.mmr, false, h);
                inRange &= w >= Math.floor(4000 * hf) && w <= Math.ceil(9000 * hf) && w <= 15000;
                est &= RankCore.estSec(w) * 1000L >= w;
                fastSame &= RankCore.waitMs(pk, me.mmr, true, h) == pk.searchMs;
            }
        }
        ok(n > 200 && inRange, "«보통» 대기 = [4000, 9000] × 시각 (저녁 ×0.85 · 새벽 ×1.4) · 15초 끝 (" + n + "번 × 24시)");
        ok(fastSame, "«빠르게» = searchMs(147 그대로 2~6초)");
        RankCore.Pick one = RankCore.pick(SEED, fresh(), 20000, book, new RankCore.Rng(5));
        long w21 = RankCore.waitMs(one, 1050, false, 21), w14 = RankCore.waitMs(one, 1050, false, 14), w4 = RankCore.waitMs(one, 1050, false, 4);
        ok(one.waitU >= 0 && w21 < w14 && w14 < w4, "같은 난수면 21시 < 14시 < 4시 (" + w21 + " < " + w14 + " < " + w4 + ")");
        RankCore.Me top = fresh(); top.mmr = 1800; long mx = 0;
        for (int i = 0; i < 100; i++) { RankCore.Pick pk = RankCore.pick(SEED, top, 20000, book, r); long w = RankCore.waitMs(pk, top.mmr, false, 4); capped &= w <= 15000; mx = Math.max(mx, w); est &= RankCore.estSec(w) * 1000L >= w; }
        ok(capped && mx == 15000, "상위권·새벽도 15초 끝 (가장 긴 " + mx + "ms)");
        RankCore.Me hm = fresh(); hm.pendingId = "p0650001"; boolean held = true;
        for (int i = 0; i < 200; i++) {
            RankCore.Pick pk = RankCore.pick(SEED, hm, 20000, book, r);
            for (int h : new int[]{ 4, 14, 21 }) for (boolean f : new boolean[]{ false, true }) {
                long w = RankCore.waitMs(pk, hm.mmr, f, h);
                held &= pk.pending && pk.waitU < 0 && w >= 1200 && w <= 2400;
                est &= RankCore.estSec(w) * 1000L >= w;
            }
        }
        ok(held, "잡힌 상대는 «보통»·«빠르게» 모두 1.2~2.4초");
        ok(est && RankCore.estSec(4000) == 5 && RankCore.estSec(4001) == 6, "예상 시간(초) × 1000 ≥ 실제 시간 — ceil + 1");
    }

    /** 147(7b35ba2) RankCore.pick 에서 잰 (씨앗, 난수 씨앗, MMR, 판수, 연승, 연패, 날, 최근 상대 있음) → (상대 id, searchMs) */
    static final long[][] REG = {
        { 104372539625493L, 1000L, 1050, 30, 0, 0, 20000, 0 }, { 104372539629862L, 8919L, 1050, 3, 0, 0, 20001, 0 },
        { 104372539634231L, 16838L, 820, 30, 0, 0, 20002, 0 }, { 104372539638600L, 24757L, 1300, 30, 0, 0, 20003, 0 },
        { 104372539625493L, 32676L, 1700, 30, 0, 0, 20004, 0 }, { 104372539629862L, 40595L, 1050, 30, 5, 0, 20005, 0 },
        { 104372539634231L, 48514L, 600, 30, 0, 4, 20006, 0 }, { 104372539638600L, 56433L, 1500, 30, 0, 0, 20007, 0 },
        { 104372539625493L, 64352L, 1050, 30, 0, 0, 20008, 0 }, { 104372539629862L, 72271L, 1150, 8, 0, 0, 20009, 0 },
        { 104372539634231L, 80190L, 1050, 30, 0, 0, 20010, 0 }, { 104372539638600L, 88109L, 1050, 3, 0, 0, 20011, 0 },
        { 104372539625493L, 96028L, 820, 30, 0, 0, 20012, 0 }, { 104372539629862L, 103947L, 1300, 30, 0, 0, 20013, 0 },
        { 104372539634231L, 111866L, 1700, 30, 0, 0, 20014, 0 }, { 104372539638600L, 119785L, 1050, 30, 5, 0, 20015, 0 },
        { 104372539625493L, 127704L, 600, 30, 0, 4, 20016, 1 }, { 104372539629862L, 135623L, 1500, 30, 0, 0, 20017, 1 },
        { 104372539634231L, 143542L, 1050, 30, 0, 0, 20018, 1 }, { 104372539638600L, 151461L, 1150, 8, 0, 0, 20019, 1 } };
    static final String[] REG_ID = { "p0650553", "p0620175", "p0410406", "p0930297", "p1270002", "p0710260", "p0170080", "p1120079", "p0630349", "p0750610",
        "p0640412", "p0590419", "p0400111", "p0920013", "p1310008", "p0720540", "o07", "p1130059", "p0660073", "p0770360" };
    static final long[] REG_MS = { 2776, 2469, 5218, 3475, 12000, 4632, 3365, 6350, 3341, 3087, 5787, 4318, 3294, 5595, 12000, 3302, 3909, 7861, 3024, 2836 };
    static RankCore.Me regMe(long[] c) {
        RankCore.Me me = new RankCore.Me(); me.placementLeft = 0; me.games = (int) c[3]; me.mmr = c[2]; me.streak = (int) c[4]; me.lstreak = (int) c[5];
        if (c[7] == 1) { me.recent.add("o01"); me.recent.add("p0650001"); }
        return me;
    }
    /** pick 이 실제로 훑은 후보(최근 상대 빼고, 뽑은 순서) — pick 의 12번 뽑기를 그대로 따라 한다(라이벌로 갔으면 null) */
    static List<String> sampled(long seed, RankCore.Me me, int day, MemBook book, long rs) {
        RankCore.Rng r = new RankCore.Rng(rs);
        Set<String> recent = new HashSet<>(me.recent.subList(0, Math.min(8, me.recent.size())));
        double sigma = me.games < 10 ? 90 : 60;
        double skew = me.streak >= 3 ? 25 * Math.min(me.streak - 2, 4) : me.lstreak >= 3 ? -25 * Math.min(me.lstreak - 2, 3) : 0;
        double target = me.mmr + skew;
        r.nextInt(4000);
        if (r.nextDouble() < RankCore.RIVAL_P) {
            List<RankCore.Player> c = new ArrayList<>();
            for (RankCore.Player p : book.rivals()) if (!recent.contains(p.id) && Math.abs(p.mmr(day, book.adj(p.id)) - me.mmr) <= 200) c.add(p);
            if (!c.isEmpty()) return null;
        }
        List<String> out = new ArrayList<>();
        for (int i = 0; i < 12; i++) {
            double m = target + r.gauss() * sigma;
            int b = RankCore.bucketOf(m);
            for (int t = 0; t < 6 && RankCore.bucketCount(b) == 0; t++) b += (b < RankCore.bucketOf(RankCore.MU) ? 1 : -1);
            if (RankCore.bucketCount(b) == 0) continue;
            RankCore.Player p = RankCore.playerAt(seed, b, r.nextInt(RankCore.bucketCount(b)));
            if (recent.contains(p.id)) continue;
            out.add(p.id);
            r.nextDouble();
        }
        return out;
    }
    /** 릴(Pick.reel) — 147 과 같은 상대·같은 searchMs(난수 순서 그대로) · 실제로 훑은 후보만 · 고른 상대·최근 상대 빼고 · 8명까지 · 잡힌 상대·라이벌은 빈 릴 */
    static void reel() {
        MemBook book = bookWithLegacy();
        int same = 0; StringBuilder bad = new StringBuilder();
        for (int i = 0; i < REG.length; i++) {
            RankCore.Pick pk = RankCore.pick(REG[i][0], regMe(REG[i]), (int) REG[i][6], book, new RankCore.Rng(REG[i][1]));
            if (pk.p.id.equals(REG_ID[i]) && pk.searchMs == REG_MS[i]) same++; else bad.append(' ').append(i).append(':').append(pk.p.id).append('/').append(pk.searchMs);
        }
        ok(same == REG.length, "147 과 같은 매칭 " + same + "/" + REG.length + " (씨앗·난수 씨앗 → 상대 id·searchMs)" + bad);
        boolean sub = true, noBest = true, noRecent = true, max8 = true, uniq = true, order = true; int nonEmpty = 0, tested = 0, sum = 0;
        RankCore.Rng rr = new RankCore.Rng(99);
        for (int i = 0; i < 400; i++) {
            RankCore.Me me = fresh(); me.mmr = 700 + rr.nextInt(1100); me.games = rr.nextInt(3) == 0 ? 4 : 30;
            for (int k = 0; k < rr.nextInt(9); k++) { int b = RankCore.bucketOf(me.mmr + rr.gauss() * 60); if (RankCore.bucketCount(b) > 0) me.recent.add(RankCore.idOf(b, rr.nextInt(RankCore.bucketCount(b)))); }
            long rs = 5000 + i;
            RankCore.Pick pk = RankCore.pick(SEED, me, 20000, book, new RankCore.Rng(rs));
            List<String> smp = sampled(SEED, me, 20000, book, rs);
            if (pk.p.legacy || smp == null) { sub &= pk.reel.isEmpty() && pk.waitU < 0; continue; }
            tested++;
            Set<String> ids = new HashSet<>(); List<String> want = new ArrayList<>();
            for (String id : smp) if (!id.equals(pk.p.id) && !want.contains(id)) want.add(id);   // 훑은 사람(12번 뽑기라 12명까지)에서 고른 상대·겹침 빼고
            for (RankCore.Player p : pk.reel) {
                sub &= smp.contains(p.id) && RankCore.player(SEED, p.id) != null && RankCore.player(SEED, p.id).nick.equals(p.nick);
                noBest &= !p.id.equals(pk.p.id);
                noRecent &= !me.recent.subList(0, Math.min(8, me.recent.size())).contains(p.id);
                uniq &= ids.add(p.id);
            }
            List<String> got = new ArrayList<>(); for (RankCore.Player p : pk.reel) got.add(p.id);
            order &= got.equals(want.subList(0, Math.min(8, want.size())));
            max8 &= pk.reel.size() <= 8;
            if (!pk.reel.isEmpty()) nonEmpty++;
            sum += pk.reel.size();
        }
        ok(sub && order, "릴 = pick 이 실제로 훑은 후보만, 훑은 순서 그대로 (" + tested + "번)");
        ok(noBest && noRecent && uniq && max8, "릴엔 고른 상대·최근 상대·겹친 사람 없음 · 8명까지 (평균 " + (tested == 0 ? 0 : sum * 10 / tested / 10.0) + "명)");
        ok(nonEmpty > tested * 0.95, "릴이 거의 늘 차 있음 (" + nonEmpty + "/" + tested + ")");
        RankCore.Me pm = fresh(); pm.pendingId = "p0650001";
        RankCore.Pick pp = RankCore.pick(SEED, pm, 20000, book, new RankCore.Rng(3));
        RankCore.Pick rv = null;
        for (long s = 1; s < 500 && rv == null; s++) { RankCore.Pick x = RankCore.pick(SEED, fresh(), 20000, book, new RankCore.Rng(s)); if (x.p.legacy) rv = x; }
        ok(pp.pending && pp.reel.isEmpty() && pp.waitU == -1 && rv != null && rv.reel.isEmpty() && rv.waitU == -1,
           "잡힌 상대·라이벌 경로는 빈 릴 · waitU −1 (라이벌 " + (rv != null ? rv.p.nick : "?") + ")");
    }

    /** 새 시즌 LP(RankCore.newSeasonLp) — 배치 자리 아래면 그대로, 위면 반, 10 단위, 음수 없음, 무쌍에서도 9000 아래 */
    static void seasonLp() {
        boolean below = true, half = true, ten = true, neg = true, master = true;
        for (int mmr = 500; mmr <= 2000; mmr += 7) {
            int base = RankCore.placementLp(mmr);
            for (int lp = 0; lp <= 9000; lp += 10) {
                int v = RankCore.newSeasonLp(lp, mmr);
                if (lp <= base && lp < RankCore.MASTER_LP) below &= v == lp;
                if (lp > base && lp < RankCore.MASTER_LP) half &= v >= base && v < lp && v <= base + (lp - base) / 2.0 && v > base + (lp - base) / 2.0 - 10;
                ten &= v % 10 == 0; neg &= v >= 0;
                if (lp == RankCore.MASTER_LP) master &= v < RankCore.MASTER_LP;
            }
        }
        ok(below, "배치 자리(base) 아래 LP 는 그대로");
        ok(half, "base 위는 base 쪽으로 반");
        ok(ten && neg && master, "늘 10 단위 · 음수 없음 · 무쌍(9000)에서도 9000 아래");
        ok(RankCore.placementLp(1090) == 2700 && RankCore.newSeasonLp(3920, 1090) == 3310, "보기: LP 3,920 · base 2,700 → 3,310 (" + RankCore.newSeasonLp(3920, 1090) + ")");
        ok(RankCore.label(3920).equals("검호 ★2") && RankCore.label(3310).equals("검객 ★5"), "보기 티어: 검호 ★2 → 검객 ★5");
    }
}

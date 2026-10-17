package com.dudu.pocketcore;

import java.io.File;
import java.nio.file.Files;
import java.util.*;

/**
 * RankTips 시험(호스트 JVM) — 캐릭터 이름 없음 · next() 가 다 돎 · 두 줄에 들어감(40자) · 글꼴 글리프.
 * 글리프: app/src/main/assets/fonts/pixel.ttf 의 cmap(형식 4·12)을 직접 읽어, 팁과 148 새 화면 글자가 모두 있는지 본다(빼기 U+2212 는 없어야 하고 걸러야 한다).
 *   java -Dassets.dir=<앱 assets> -cp out com.dudu.pocketcore.RankTipsTest
 */
public class RankTipsTest {
    static int fails = 0, passes = 0;
    static void ok(boolean c, String what) { System.out.println((c ? "PASS " : "FAIL ") + what); if (c) passes++; else fails++; }

    /** 148 화면에 새로 나오는 글자들(spec §3) — 대기창·카드·막힘 카드·리그 화면·규칙 탭 */
    static final String[] UI = {
        "리그 대전", "랭크 매치", "리그 대전으로…", "자동 저장이 꺼져 있어서 지금 판은 이어지지 않아요. 갈까요?", "가기", "취소",
        "리그 기록을 쓸 수 없어요 — 저장소 권한을 확인해 주세요", "랭크 매치 바로 가기  ›", "리그 순위표  ›",
        "상대 찾는 중…", "대전 준비 중…", "0:03 · 예상 0:07", "칼끝노인 · 무사 ★3", "검객 ★2 · 1,240 LP", "다음 ★까지 60 LP", "승급까지 120 LP", "강등 위기!",
        "배치 경기 3/5", "무쌍 · MR 1,712", "5판을 마치면 첫 티어가 정해져요", "오늘 2승 1패 · +35 LP  ●●○·", "오늘 1승 2패 · -20 LP", "오늘 첫 판이에요",
        "3연승 중!", "다음엔 이겨요", "첫 승 보너스 +30 남았어요", "팁 · ▲▼", "◀  스테이지 · 상대 기본  ▶", "무작위", "취소 (B)",
        "오늘 38,214명 접속", "비슷한 실력 찾는 중", "상대는 모두 게임 CPU 예요", "범위 넓히는 중…",
        "기다리던 상대에게 가는 중…", "0:01 · 곧 만나요", "지난번 카드에서 본 상대예요",
        "B 취소 · ◀▶ 스테이지 · ▲▼ 팁", "A 대전 · B 나가기 · ◀▶ 스테이지", "상대 발견!", "기다린 시간 0:07", "상대가 기다려요 — 다음에 또 만나요",
        "어디로 갈까요?", "계속", "내 게임으로", "순위표", "목록으로", "타이틀로",
        "기권할까요?", "이 경기는 기권패로 기록돼요 (LP -85).", "배치 1패로 기록돼요.", "기권",
        "멈춘 경기를 이어할 수 없어요", "vs 칼끝노인 · 검호 ★1\n앱이 멈춰서 이어할 자리가 없어요.\n무효로 닫으면 LP·전적은 그대로예요.", "이어할 자리를 불러오지 못했어요.",
        "무효로 닫고 계속", "기권하고 계속", "리그 화면으로", "게임으로", "무효로 닫기",
        "무효로 닫았어요 — LP 그대로 · 바로 상대를 찾아요",
        "다른 롬으로 바뀌었어요", "경기를 시작한 롬: ss2_h1.ngc\n지금 롬: ss2.ngc\n원래 롬으로 되돌리면 이어할 수 있어요.",
        "앱이 바뀌어 이어할 수 없어요", "앱을 업데이트해서 이 경기를 이어할 수 없어요.\n무효로 닫으면 LP·전적은 그대로예요.",
        "리그 기록 파일을 못 읽어요", "리그 기록 폴더에 쓸 수 없어요", "저장소 권한을 확인한 뒤 «다시 확인»을 눌러 주세요.\n(/storage/emulated/0/PocketCore/league)",
        "다시 확인", "권한 설정 열기", "아직 안 돼요 — ", "결과를 저장하지 못했어요", "결과는 이 판에 그대로 있어요.\n저장소를 확인한 뒤 다시 시도해 주세요.",
        "다시 시도", "나중에 정산하기", "다음에 리그를 열면 정산해요", "이 판도 저장하지 못했어요 — 권한을 먼저 확인해 주세요",
        "찾기를 멈췄어요 — A로 다시 찾기", "앱이 내려가서 찾기를 멈췄어요 — A로 다시 찾기", "리그 기록이 바뀌었어요", "화면을 열지 못했어요 — 다시 눌러 주세요",
        "첫 라운드 전에 멈춘 경기를 무효로 닫았어요 — 같은 상대가 기다려요", "랭크 매치 하러 가기  ›", "멈춘 경기 이어서 하기  ›", "기권하고 찾기", "이어서 하기",
        "무효로 닫고 찾기", "원래 롬으로 되돌리면 이어할 수 있어요.", "다시 읽기", "기권하고 새로 찾을까요?",
        "멈춘 경기는 기권패로 기록돼요 (LP -60). 그다음 바로 새 상대를 찾아요.",
        "전국 21,663위 / 39,899명 · 시즌 2", "· 통산 43승 34패", "지난 시즌 최고 · 검호 ★2", "기다리는 상대 · 칼끝노인 (검호 ★1) — 내일 21:04 까지", "오늘 09:30 까지",
        "무효 · 칼끝노인 — 앱이 멈춰 이어할 자리가 없음", "… — 앱이 바뀌어 닫음", "이어할 자리를 불러오지 못해 닫음",
        "시즌 · 기록", "시즌 2 · 10월 16일부터 · 31승 25패", "시즌 1 · 최고 검호 ★2 · 마지막 검객 ★5 · 31승 25패", "시즌 1 · 처음부터 다시 · 최고 … · …",
        "매칭 대기", "보통", "빠르게", "보통: 4~9초쯤 (새벽엔 조금 더) · 빠르게: 2~6초",
        "새 시즌 시작", "LP 를 반쯤 내리고 승패를 0부터 세요 · 실력 점수는 그대로", "배치 경기를 마치면 새 시즌을 열 수 있어요", "새 시즌을 시작할까요?",
        "시즌 1 기록은 ‘지난 시즌’에 남아요.\nLP 3,920 → 3,310 (검호 ★2 → 검객 ★5)\n승패·연승은 0부터, 실력 점수와 상대 전적은 그대로라 빨리 올라와요.",
        "시작", "시즌 2 시작!", "처음부터 다시", "지금 기록은 보관해요 · 배치 5판부터", "처음부터 다시 할까요?",
        "티어·LP·전적·상대 전적을 처음으로 돌리고 배치 경기 5판부터 시작해요.\n지금 기록은 지우지 않고 보관 파일과 ‘지난 시즌’에 남겨요.\n앱 안에서 되돌릴 수는 없어요.",
        "처음부터", "시즌 3 — 배치 경기부터 시작해요", "끝나지 않은 경기를 먼저 정리해 주세요", "게임 속 리그를 닫은 뒤에 할 수 있어요", "저장하지 못했어요 — 기록은 그대로예요",
        "상대 카드가 뜬 뒤 나가면, 그 상대와 붙을 때까지 다음 찾기에 같은 상대가 나와요 (최대 24시간). 찾는 중에 그만두면 잡히지 않아요.",
        "↓↑←→▲▼◀▶●○★·…«»‘’—~!?()/:+-=,.%0123456789",
    };

    public static void main(String[] a) throws Exception {
        names(); cycle(); length(); glyphs();
        System.out.println(fails == 0 ? "ALL PASS (" + passes + ")" : fails + " FAIL / " + (passes + fails));
        if (fails != 0) System.exit(1);
    }

    static void names() {
        boolean none = true; StringBuilder hit = new StringBuilder();
        List<String> names = new ArrayList<>(Arrays.asList(RankCore.CHAR)); names.addAll(Arrays.asList(RankCore.Names.CSHORT));
        for (String t : RankTips.TIPS) for (String n : names) if (t.contains(n)) { none = false; hit.append(' ').append(n); }
        ok(RankTips.TIPS.length == 12, "팁 12개");
        ok(none, "팁에 캐릭터 이름 없음(이미 고른 상대를 미리 알려 주지 않게)" + hit);
        ok(RankTips.TIPS[9].equals("오늘 첫 승엔 +" + RankCore.BONUS_DAILY + " LP 보너스") && RankTips.TIPS[9].contains("+30") && RankTips.TIPS[10].endsWith("+20"),
           "보너스 팁은 RankCore 상수에서 («" + RankTips.TIPS[9] + "» · «" + RankTips.TIPS[10] + "»)");
    }

    static void cycle() {
        int n = RankTips.TIPS.length;
        int first = RankTips.next();
        Set<Integer> seen = new HashSet<>(); seen.add(first);
        boolean step = true; int prev = first;
        for (int i = 1; i < n; i++) { int x = RankTips.next(); step &= x == (prev + 1) % n; seen.add(x); prev = x; }
        ok(first == Math.floorMod(RankCore.today(System.currentTimeMillis()), n), "처음 팁 = 오늘(한국 날짜)로 정한 자리 " + first);
        ok(seen.size() == n && step && RankTips.next() == first, "next() 는 하나씩 넘어가며 " + n + "개를 다 돌고 처음으로");
    }

    static void length() {
        boolean fit = true; int max = 0; String longest = "";
        for (String t : RankTips.TIPS) { int c = t.codePointCount(0, t.length()); if (c > max) { max = c; longest = t; } fit &= c <= 40; }
        ok(fit, "팁은 340dp·12sp 두 줄 안(40자 이하) — 가장 긴 것 " + max + "자 «" + longest + "»");
        boolean noMinus = true; for (String t : RankTips.TIPS) noMinus &= t.indexOf('−') < 0;
        ok(noMinus, "팁에 U+2212(빼기 기호) 없음 — ASCII '-'");
    }

    /* ── 글꼴 cmap(형식 4·12) ── */
    static Set<Integer> cmap(byte[] d) {
        Set<Integer> cps = new HashSet<>();
        int n = u16(d, 4), off = -1;
        for (int i = 0; i < n; i++) { int e = 12 + 16 * i; if (d[e] == 'c' && d[e + 1] == 'm' && d[e + 2] == 'a' && d[e + 3] == 'p') off = (int) u32(d, e + 8); }
        if (off < 0) return cps;
        int nt = u16(d, off + 2);
        for (int i = 0; i < nt; i++) {
            int s = off + (int) u32(d, off + 4 + 8 * i + 4), fmt = u16(d, s);
            if (fmt == 4) {
                int segx2 = u16(d, s + 6), seg = segx2 / 2, ends = s + 14, starts = ends + segx2 + 2, deltas = starts + segx2, ros = deltas + segx2;
                for (int k = 0; k < seg; k++) {
                    int st = u16(d, starts + 2 * k), en = u16(d, ends + 2 * k), dl = (short) u16(d, deltas + 2 * k), ro = u16(d, ros + 2 * k);
                    for (int c = st; c <= en && c != 0xFFFF; c++) {
                        int g;
                        if (ro == 0) g = (c + dl) & 0xFFFF;
                        else { g = u16(d, ros + 2 * k + ro + 2 * (c - st)); if (g != 0) g = (g + dl) & 0xFFFF; }
                        if (g != 0) cps.add(c);
                    }
                }
            } else if (fmt == 12) {
                long ng = u32(d, s + 12);
                for (long k = 0; k < ng; k++) {
                    int b = s + 16 + (int) (12 * k);
                    long a0 = u32(d, b), a1 = u32(d, b + 4), g = u32(d, b + 8);
                    for (long c = a0; c <= a1; c++) if (g + (c - a0) != 0) cps.add((int) c);
                }
            }
        }
        return cps;
    }
    static int u16(byte[] d, int i) { return ((d[i] & 0xFF) << 8) | (d[i + 1] & 0xFF); }
    static long u32(byte[] d, int i) { return ((long) u16(d, i) << 16) | u16(d, i + 2); }
    /** 글꼴에 없는 글자들(줄바꿈·띄어쓰기 빼고) */
    static String missing(Set<Integer> cps, String s) {
        StringBuilder m = new StringBuilder();
        s.codePoints().forEach(c -> { if (c != '\n' && c != ' ' && !cps.contains(c) && m.indexOf(new String(Character.toChars(c))) < 0) m.appendCodePoint(c); });
        return m.toString();
    }

    static void glyphs() throws Exception {
        File f = new File(System.getProperty("assets.dir", "."), "fonts/pixel.ttf");
        ok(f.isFile(), "글꼴 " + f);
        if (!f.isFile()) return;
        Set<Integer> cps = cmap(Files.readAllBytes(f.toPath()));
        ok(cps.size() > 2000 && cps.contains((int) '가') && cps.contains((int) 'A'), "cmap 읽음 — 글자 " + cps.size() + "개");
        StringBuilder mt = new StringBuilder();
        for (String t : RankTips.TIPS) mt.append(missing(cps, t));
        ok(mt.length() == 0, "팁 12개의 글자가 모두 글꼴에 있음" + (mt.length() > 0 ? " — 없음: " + mt : ""));
        StringBuilder mu = new StringBuilder(); int chars = 0;
        for (String u : UI) { String x = missing(cps, u); if (x.length() > 0) mu.append(" «").append(u, 0, Math.min(12, u.length())).append("»:").append(x); chars += u.length(); }
        ok(mu.length() == 0, "148 새 화면 글자(" + UI.length + "줄 · " + chars + "자)가 모두 글꼴에 있음" + mu);
        boolean arrows = true; for (char c : "↓↑←→▲▼◀▶●○★·…«»".toCharArray()) arrows &= cps.contains((int) c);
        ok(arrows, "화살표·도형 ↓↑←→ ▲▼◀▶ ●○★ ·…«» 있음");
        ok(!cps.contains(0x2212) && missing(cps, "LP −30").equals("−") && missing(cps, "LP -30").isEmpty(), "U+2212(−)는 글꼴에 없음 — 그 글자가 든 줄은 이 시험이 걸러 냄(ASCII '-' 는 통과)");
    }
}

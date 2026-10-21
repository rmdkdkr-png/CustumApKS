package com.dudu.pocketcore;
/* JVM 시험용 — Look.push 가 넣는 값을 그대로 받아 둔다 */
public final class Emu {
    static byte[] mem; static int[][][] cus = new int[14][2][];
    public static void nativeLookSetMem(byte[] m) { mem = m.clone(); }
    public static void nativeLookSetCustom(int ch, int k, int c1, int c2, int c3) { cus[ch][k] = c1 < 0 ? null : new int[] { c1, c2, c3 }; }
}

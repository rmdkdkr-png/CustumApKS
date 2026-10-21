package com.dudu.pocketcore;
import java.nio.file.*;
/** 호스트 시험용: Patcher.resolve 와 같은 순서로 원본 롬 (+ 번역 IPS) + 배경음악 끔 사본을 만든다. 사용: MuteTool <원본> <ips|-> <출력> */
public class MuteTool {
    static byte[] apply(byte[] rom, byte[] ips) {
        byte[] out = rom.clone(); int p = 5;
        while (p + 3 <= ips.length) {
            if (ips[p] == 'E' && ips[p+1] == 'O' && ips[p+2] == 'F') return out;
            int off = ((ips[p] & 0xff) << 16) | ((ips[p+1] & 0xff) << 8) | (ips[p+2] & 0xff);
            int len = ((ips[p+3] & 0xff) << 8) | (ips[p+4] & 0xff); p += 5;
            if (len == 0) { int rl = ((ips[p] & 0xff) << 8) | (ips[p+1] & 0xff); byte v = ips[p+2]; p += 3;
                if (off + rl > out.length) { byte[] b = new byte[off + rl]; System.arraycopy(out, 0, b, 0, out.length); out = b; }
                for (int k = 0; k < rl; k++) out[off + k] = v; }
            else { if (off + len > out.length) { byte[] b = new byte[off + len]; System.arraycopy(out, 0, b, 0, out.length); out = b; }
                System.arraycopy(ips, p, out, off, len); p += len; }
        }
        return out;
    }
    static void markIps(byte[] ips, boolean[] mark) {
        int p = 5;
        while (p + 3 <= ips.length) {
            if (ips[p] == 'E' && ips[p+1] == 'O' && ips[p+2] == 'F') return;
            int off = ((ips[p] & 0xff) << 16) | ((ips[p+1] & 0xff) << 8) | (ips[p+2] & 0xff);
            int len = ((ips[p+3] & 0xff) << 8) | (ips[p+4] & 0xff); p += 5;
            if (len == 0) { len = ((ips[p] & 0xff) << 8) | (ips[p+1] & 0xff); p += 3; } else p += len;
            for (int k = off; k < off + len && k < mark.length; k++) mark[k] = true;
        }
    }
    public static void main(String[] a) throws Exception {
        byte[] data = Files.readAllBytes(Paths.get(a[0]));
        byte[] ips = a[1].equals("-") ? null : Files.readAllBytes(Paths.get(a[1]));
        byte[] done = ips != null ? apply(data, ips) : data;
        boolean[] touched = new boolean[done.length];
        if (ips != null) markIps(ips, touched);
        boolean[] sp = Ss1Music.spare(done, data, touched);
        byte[] m = Ss1Music.mute(done, sp);
        if (m == null) { System.out.println("MUTE_FAIL"); System.exit(1); }
        int diff = 0; for (int i = 0; i < m.length; i++) if (i >= done.length || m[i] != done[i]) diff++;
        Files.write(Paths.get(a[2]), m);
        System.out.println("ok placed=" + Ss1Music.lastPlaced + "/" + Ss1Music.lastWanted + " changed_bytes=" + diff);
    }
}

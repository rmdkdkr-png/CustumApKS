package com.dudu.pocketcore;
import java.io.*; import java.util.*;
/* JVM 시험용 — 진짜 Settings 의 load()/put() 과 같은 파일 형식(key=value 줄)만. 진짜 것은 표(GROUPS)가 안드로이드 클래스를 불러 JVM 에서 못 올린다 */
public final class Settings {
    public static Map<String, String> load() {
        Map<String, String> m = new LinkedHashMap<>();
        File f = MainActivity.optsFile();
        if (!f.exists()) return m;
        try (Scanner sc = new Scanner(f, "UTF-8")) {
            while (sc.hasNextLine()) { String ln = sc.nextLine().trim(); int i = ln.indexOf('='); if (!ln.startsWith("#") && i > 0) m.put(ln.substring(0, i).trim(), ln.substring(i + 1).trim()); }
        } catch (Exception ignored) { }
        return m;
    }
    public static void put(String key, String val) {
        Map<String, String> m = load(); m.put(key, val);
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, String> e : m.entrySet()) sb.append(e.getKey()).append('=').append(e.getValue()).append('\n');
        try (FileOutputStream o = new FileOutputStream(MainActivity.optsFile())) { o.write(sb.toString().getBytes("UTF-8")); } catch (Exception ignored) { }
    }
}

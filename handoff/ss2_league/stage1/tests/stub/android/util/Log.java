package android.util;
public final class Log { public static int e(String t, String m, Throwable e) { System.err.println(t+": "+m+" "+e); return 0; } }

package android.content.res;
public class AssetManager {
    public java.io.InputStream open(String path) throws java.io.IOException {
        return new java.io.FileInputStream(new java.io.File(System.getProperty("assets.dir"), path));
    }
}

package com.sangosp;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.ClipData;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/**
 * SANGO SP — DOSBox(js-dos) 가 통째로 들어간 index.html 을 WebView 로 띄우는 껍데기.
 * 게임 ZIP 은 앱에 넣지 않고 사용자가 직접 물립니다(저작권).
 */
public class MainActivity extends Activity {

    private static final int REQ_PICK_FILE = 1001;

    private WebView web;

    /** onShowFileChooser 가 넘겨준 콜백. 결과를 반드시 한 번 돌려줘야 다음 선택이 열립니다. */
    private ValueCallback<Uri[]> pendingFileCallback;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        if (Build.VERSION.SDK_INT >= 28) {
            getWindow().getAttributes().layoutInDisplayCutoutMode =
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
        }

        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);          // localStorage / IndexedDB
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setMediaPlaybackRequiresUserGesture(false);   // 사운드 자동 시작
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setUseWideViewPort(true);
        s.setLoadWithOverviewMode(false);
        s.setSupportZoom(false);
        s.setTextZoom(100);

        web.setWebViewClient(new WebViewClient() {
            /**
             * 게임은 file:///android_asset 안에서만 돕니다. 바깥 http(s) 주소
             * (게임 ZIP 받으러 가는 superfighter.com 링크)는 기본 브라우저로 넘깁니다.
             * 이 WebView 에서 열면 실행 중이던 DOSBox 가 통째로 날아갑니다.
             */
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return openExternally(request.getUrl());
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            /**
             * 기본 구현은 아무것도 하지 않아서 <input type="file"> 이 먹통이 됩니다.
             * 직접 파일 선택창을 띄우고 결과를 콜백으로 돌려줘야 합니다.
             */
            @Override
            public boolean onShowFileChooser(WebView view,
                                             ValueCallback<Uri[]> callback,
                                             FileChooserParams params) {
                // 앞선 선택이 결과 없이 남아 있으면 먼저 닫아 줍니다. 안 그러면 영영 잠깁니다.
                if (pendingFileCallback != null) {
                    pendingFileCallback.onReceiveValue(null);
                }
                pendingFileCallback = callback;

                Intent intent = params.createIntent();
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                // accept=".zip" 을 그대로 쓰면 ZIP 의 MIME 이 기기마다 제각각(application/zip,
                // application/x-zip-compressed, octet-stream…)이라 파일이 아예 안 보이는 일이 잦습니다.
                intent.setType("*/*");

                try {
                    startActivityForResult(intent, REQ_PICK_FILE);
                } catch (ActivityNotFoundException e) {
                    pendingFileCallback = null;
                    return false;
                }
                return true;
            }
        });

        WebView.setWebContentsDebuggingEnabled(true);

        setContentView(web);
        hideBars();

        web.loadUrl("file:///android_asset/index.html");
    }

    /** http(s) 면 기본 브라우저로 넘기고 true. 그 외(file: 등)는 WebView 가 그대로 처리. */
    private boolean openExternally(Uri uri) {
        if (uri == null) return false;
        String scheme = uri.getScheme();
        if (!"http".equals(scheme) && !"https".equals(scheme)) return false;
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, uri));
            return true;
        } catch (ActivityNotFoundException e) {
            return false;   // 열 브라우저가 없으면 WebView 에 맡깁니다
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != REQ_PICK_FILE || pendingFileCallback == null) return;

        pendingFileCallback.onReceiveValue(pickedUris(resultCode, data));
        pendingFileCallback = null;
    }

    /**
     * 선택 결과에서 Uri 를 꺼냅니다. 고른 게 없으면 null — WebView 는 그래야
     * 선택이 끝난 걸로 보고 다음 요청을 열어 줍니다.
     *
     * WebChromeClient.FileChooserParams.parseResult() 와 같은 일을 하지만,
     * 그쪽은 WebView 프로바이더를 거쳐서 테스트로 확인할 수가 없습니다.
     */
    static Uri[] pickedUris(int resultCode, Intent data) {
        if (resultCode != RESULT_OK || data == null) return null;

        Uri single = data.getData();
        if (single != null) return new Uri[] { single };

        ClipData clip = data.getClipData();       // 다중 선택을 지원하는 파일앱 대비
        if (clip != null && clip.getItemCount() > 0) {
            Uri[] uris = new Uri[clip.getItemCount()];
            for (int i = 0; i < clip.getItemCount(); i++) {
                uris[i] = clip.getItemAt(i).getUri();
            }
            return uris;
        }
        return null;
    }

    private void hideBars() {
        View d = getWindow().getDecorView();
        d.setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) hideBars();
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (web != null) web.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) web.onResume();
    }

    @Override
    public void onBackPressed() {
        // 게임 중 뒤로가기로 앱이 꺼지지 않게
        if (web != null && web.canGoBack()) { web.goBack(); return; }
        moveTaskToBack(true);
    }
}

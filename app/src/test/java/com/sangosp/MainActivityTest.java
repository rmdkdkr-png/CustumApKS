package com.sangosp;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.view.ViewGroup;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.Robolectric;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.Shadows;
import org.robolectric.android.controller.ActivityController;
import org.robolectric.annotation.Config;
import org.robolectric.shadows.ShadowActivity;
import org.robolectric.shadows.ShadowWebView;

import java.util.Collections;
import java.util.Map;

/**
 * 첫 실행 흐름이 기기에서 막혔던 두 지점을 검증합니다.
 *  - "파일 선택" 이 실제로 선택창을 띄우고 고른 파일이 WebView 로 돌아가는가
 *  - superfighter.com 링크가 WebView 를 덮어쓰지 않고 바깥 브라우저로 나가는가
 */
@RunWith(RobolectricTestRunner.class)
@Config(sdk = 34)
public class MainActivityTest {

    private ActivityController<MainActivity> controller;
    private MainActivity activity;
    private WebView web;
    private ShadowActivity shadowActivity;
    private ShadowWebView shadowWeb;

    @Before
    public void setUp() {
        controller = Robolectric.buildActivity(MainActivity.class).setup();
        activity = controller.get();
        ViewGroup content = activity.findViewById(android.R.id.content);
        web = (WebView) content.getChildAt(0);
        shadowActivity = Shadows.shadowOf(activity);
        shadowWeb = Shadows.shadowOf(web);
    }

    @Test
    public void loadsTheBundledGamePage() {
        assertEquals("file:///android_asset/index.html", shadowWeb.getLastLoadedUrl());
    }

    @Test
    public void fileChooser_opensPicker_andHandsThePickedZipBack() {
        WebChromeClient chrome = shadowWeb.getWebChromeClient();
        assertNotNull("WebChromeClient must be set, else <input type=file> is dead", chrome);

        final Uri[][] delivered = new Uri[1][];
        ValueCallback<Uri[]> callback = value -> delivered[0] = value;

        boolean handled = chrome.onShowFileChooser(web, callback, zipChooserParams());
        assertTrue("onShowFileChooser must claim the request", handled);

        ShadowActivity.IntentForResult started = shadowActivity.getNextStartedActivityForResult();
        assertNotNull("a picker Activity must actually be launched", started);
        assertEquals(Intent.ACTION_GET_CONTENT, started.intent.getAction());
        // 기기마다 ZIP 의 MIME 이 제각각이라 좁게 걸면 파일이 안 보입니다
        assertEquals("*/*", started.intent.getType());
        assertTrue(started.intent.hasCategory(Intent.CATEGORY_OPENABLE));

        Uri picked = Uri.parse("content://downloads/public_downloads/42");
        shadowActivity.receiveResult(started.intent, Activity.RESULT_OK, new Intent().setData(picked));

        assertNotNull("the page must receive the picked file", delivered[0]);
        assertEquals(1, delivered[0].length);
        assertEquals(picked, delivered[0][0]);
    }

    @Test
    public void fileChooser_cancelling_releasesTheInputForAnotherTry() {
        WebChromeClient chrome = shadowWeb.getWebChromeClient();

        final boolean[] answered = { false };
        final Uri[][] value = new Uri[1][];
        ValueCallback<Uri[]> callback = v -> { answered[0] = true; value[0] = v; };

        chrome.onShowFileChooser(web, callback, zipChooserParams());
        ShadowActivity.IntentForResult started = shadowActivity.getNextStartedActivityForResult();
        shadowActivity.receiveResult(started.intent, Activity.RESULT_CANCELED, null);

        // null 을 돌려주지 않으면 그 뒤로 파일 선택이 영영 열리지 않습니다
        assertTrue("cancel must still answer the callback", answered[0]);
        assertNull(value[0]);

        // 취소 후에도 다시 열려야 합니다
        assertTrue(chrome.onShowFileChooser(web, v -> { }, zipChooserParams()));
        assertNotNull(shadowActivity.getNextStartedActivityForResult());
    }

    @Test
    public void fileChooser_reentrantRequest_doesNotStrandTheOldCallback() {
        WebChromeClient chrome = shadowWeb.getWebChromeClient();

        final boolean[] firstAnswered = { false };
        chrome.onShowFileChooser(web, v -> firstAnswered[0] = true, zipChooserParams());
        shadowActivity.getNextStartedActivityForResult();

        chrome.onShowFileChooser(web, v -> { }, zipChooserParams());

        assertTrue("a superseded callback must be closed out", firstAnswered[0]);
    }

    @Test
    public void externalLink_goesToTheBrowser_notOverTheRunningGame() {
        WebViewClient client = shadowWeb.getWebViewClient();
        assertNotNull(client);

        Uri link = Uri.parse("https://www.superfighter.com/sango2/index.html");
        boolean handled = client.shouldOverrideUrlLoading(web, request(link));

        assertTrue("http(s) must be handed off, not loaded in place", handled);
        Intent started = shadowActivity.getNextStartedActivity();
        assertNotNull(started);
        assertEquals(Intent.ACTION_VIEW, started.getAction());
        assertEquals(link, started.getData());
    }

    @Test
    public void gamePageNavigation_staysInsideTheWebView() {
        WebViewClient client = shadowWeb.getWebViewClient();

        boolean handled = client.shouldOverrideUrlLoading(
            web, request(Uri.parse("file:///android_asset/index.html")));

        assertFalse("the bundled page must not be kicked out to a browser", handled);
        assertNull(shadowActivity.getNextStartedActivity());
    }

    /** 실제 페이지의 <input type="file" accept=".zip,application/zip"> 를 흉내냅니다. */
    private WebChromeClient.FileChooserParams zipChooserParams() {
        return new WebChromeClient.FileChooserParams() {
            @Override public Intent createIntent() {
                return new Intent(Intent.ACTION_GET_CONTENT).setType("application/zip");
            }
            @Override public int getMode() { return MODE_OPEN; }
            @Override public String[] getAcceptTypes() {
                return new String[] { ".zip", "application/zip" };
            }
            @Override public boolean isCaptureEnabled() { return false; }
            @Override public CharSequence getTitle() { return null; }
            @Override public String getFilenameHint() { return null; }
        };
    }

    private WebResourceRequest request(Uri uri) {
        return new WebResourceRequest() {
            @Override public Uri getUrl() { return uri; }
            @Override public boolean isForMainFrame() { return true; }
            @Override public boolean isRedirect() { return false; }
            @Override public boolean hasGesture() { return true; }
            @Override public String getMethod() { return "GET"; }
            @Override public Map<String, String> getRequestHeaders() {
                return Collections.emptyMap();
            }
        };
    }
}

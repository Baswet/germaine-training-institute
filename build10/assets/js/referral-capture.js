/*==================================================
    GERMAINE — EARNFASTCASH REFERRAL CAPTURE
    Runs on every page that includes this script. If the current URL
    carries a `?ref=CODE` query parameter (the format EarnFastCash's own
    referral links already use — see build10/EarnCash frontend), the
    code is stored in localStorage so it survives navigation from the
    referral link's landing page through Explore Programmes -> a course
    page -> the Apply form, without needing to be re-appended to every
    internal link by hand.

    Deliberately does nothing clever: no validation against the backend
    here (an unknown/invalid code is simply ignored server-side when the
    application is submitted — see application_service._resolve_referral),
    no fabricated attribution, and no code is ever invented if none was
    present in the URL or storage.
==================================================*/
(function () {
    "use strict";

    var STORAGE_KEY = "germaine_referral_code";
    var STORAGE_TS_KEY = "germaine_referral_captured_at";
    var MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000; // 30 days — same-order-of-magnitude as a typical affiliate cookie window

    function readStoredCode() {
        try {
            var code = window.localStorage.getItem(STORAGE_KEY);
            var ts = parseInt(window.localStorage.getItem(STORAGE_TS_KEY), 10);
            if (!code) return null;
            if (ts && Date.now() - ts > MAX_AGE_MS) {
                window.localStorage.removeItem(STORAGE_KEY);
                window.localStorage.removeItem(STORAGE_TS_KEY);
                return null;
            }
            return code;
        } catch (err) {
            return null; // localStorage unavailable (private mode, etc.) — referral simply isn't persisted
        }
    }

    function storeCode(code) {
        try {
            window.localStorage.setItem(STORAGE_KEY, code);
            window.localStorage.setItem(STORAGE_TS_KEY, String(Date.now()));
        } catch (err) { /* ignore — non-fatal */ }
    }

    try {
        var params = new URLSearchParams(window.location.search);
        var incoming = params.get("ref");
        if (incoming && /^[A-Za-z0-9]{4,20}$/.test(incoming.trim())) {
            storeCode(incoming.trim().toUpperCase());
        }
    } catch (err) { /* URLSearchParams unsupported — capture simply skipped */ }

    window.GermaineReferral = {
        getCode: function () {
            return readStoredCode();
        }
    };
})();

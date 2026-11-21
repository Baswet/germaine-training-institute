/*==================================================
    GERMAINE TRAINING INSTITUTE
    REAL-TIME APPLICANT LEAD CAPTURE (apply.html)

    Quietly saves the applicant's name + phone (and, once
    available, email / school / programme) as soon as BOTH
    the name and the phone number are valid, so the admissions
    team can follow up even if the form is never submitted.

    Rules this file follows:
      - Fully independent of the application form. It never
        blocks typing, never shows pop-ups or error messages,
        and the form submits normally even if this file fails
        to load or the capture API is down.
      - Debounced (1.2s after the last keystroke), and only sends
        when the data is valid AND different from what was last
        saved, so typing produces at most a few requests.
      - One random, anonymous lead token per browser (localStorage).
        The backend stores only its hash and uses it to update the
        SAME lead on corrections, retries and return visits.
      - Retries quietly with backoff on network/server errors.
        Retries reuse the same token, so they can't create
        duplicates.
      - The applicant is told about this by the notice shown next
        to the phone field (#apLeadNotice). Nothing is sent until
        that notice is present on the page.

    Public hook used by apply-wizard.js:
      window.GTILeadCapture.token()          -> current token (or null)
      window.GTILeadCapture.flush()          -> send now if needed
      window.GTILeadCapture.markSubmitted()  -> forget the token after
                                                a successful submission
==================================================*/

(function (window, document) {
    "use strict";

    var STORAGE_KEY = "gti_lead_token_v1";
    var ENDPOINT = "/api/admissions/leads/capture";
    var DEBOUNCE_MS = 1200;
    var MAX_RETRIES = 3;
    var NOTICE_VERSION = "2026-11";

    var memoryToken = null;   // fallback when localStorage is blocked
    var lastSentKey = "";
    var inFlight = false;
    var pendingAfterFlight = false;
    var debounceTimer = null;
    var retryTimer = null;
    var retries = 0;
    var disabled = false;

    function $(id) { return document.getElementById(id); }
    function val(id) { var el = $(id); return el && typeof el.value === "string" ? el.value.trim() : ""; }

    /*---------- token ----------*/
    function randomToken() {
        var bytes = new Uint8Array(32);
        if (window.crypto && window.crypto.getRandomValues) {
            window.crypto.getRandomValues(bytes);
        } else {
            return null; // no secure randomness: don't capture at all
        }
        return Array.prototype.map.call(bytes, function (b) { return ("0" + b.toString(16)).slice(-2); }).join("");
    }

    function getToken(create) {
        var t = null;
        try { t = window.localStorage.getItem(STORAGE_KEY); } catch (e) { t = memoryToken; }
        if (t && /^[A-Za-z0-9_-]{32,128}$/.test(t)) return t;
        if (!create) return null;
        t = randomToken();
        if (!t) return null;
        try { window.localStorage.setItem(STORAGE_KEY, t); } catch (e) { memoryToken = t; }
        return t;
    }

    function forgetToken() {
        try { window.localStorage.removeItem(STORAGE_KEY); } catch (e) { /* ignore */ }
        memoryToken = null;
        lastSentKey = "";
    }

    /*---------- validation (mirrors the backend; backend re-checks) ----------*/
    var NAME_RE = /^[^\d_!"#$%&()*+,\/:;<=>?@\[\\\]^`{|}~]+$/;

    function validName(name) {
        if (!name || name.length > 120 || !NAME_RE.test(name)) return false;
        var letters = name.replace(/[^A-Za-zÀ-ɏͰ-῿]/g, "");
        return letters.length >= 3;
    }

    function normalizePhone(raw) {
        var v = (raw || "").replace(/[\s\-().]/g, "");
        if (v.charAt(0) === "+") v = v.slice(1);
        if (!/^\d+$/.test(v)) return null;
        if (v.indexOf("254") === 0) v = v.slice(3);
        if (v.charAt(0) === "0") v = v.slice(1);
        return /^[17]\d{8}$/.test(v) ? "254" + v : null;
    }

    function validEmail(email) { return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email); }

    /*---------- payload ----------*/
    function buildPayload() {
        var name = val("apFullname").replace(/\s+/g, " ");
        var phoneRaw = val("apPhone");
        if (!validName(name) || !normalizePhone(phoneRaw)) return null;

        var email = val("apEmail");
        var schoolSel = $("apSchool");
        var school = "";
        if (schoolSel && schoolSel.value) {
            var opt = schoolSel.options[schoolSel.selectedIndex];
            school = (opt && opt.textContent ? opt.textContent : schoolSel.value).trim();
        }
        return {
            applicant_name: name,
            phone_number: phoneRaw,
            email: email && validEmail(email) ? email : undefined,
            school: school || undefined,
            programme: val("apProgramme") || undefined,
            application_type: "scholarship",
            source_page: "apply.html",
            notice_version: NOTICE_VERSION
        };
    }

    function keyOf(p) {
        return [p.applicant_name, normalizePhone(p.phone_number), p.email || "", p.school || "", p.programme || ""].join("|");
    }

    /*---------- sending ----------*/
    function apiBase() {
        return (window.GermaineAPI && window.GermaineAPI.BASE_URL) || "";
    }

    function send(payload, key, useKeepalive) {
        var token = getToken(true);
        if (!token || !apiBase() || typeof window.fetch !== "function") return;
        payload.lead_token = token;

        inFlight = true;
        var controller = typeof AbortController !== "undefined" && !useKeepalive ? new AbortController() : null;
        var timeout = controller ? window.setTimeout(function () { controller.abort(); }, 10000) : null;

        window.fetch(apiBase() + ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json", "Accept": "application/json" },
            body: JSON.stringify(payload),
            keepalive: !!useKeepalive,
            signal: controller ? controller.signal : undefined
        }).then(function (res) {
            if (timeout) window.clearTimeout(timeout);
            inFlight = false;
            if (res.ok) {
                lastSentKey = key;
                retries = 0;
            } else if (res.status === 422 || res.status === 400 || res.status === 413) {
                lastSentKey = key; // invalid by server rules: don't resend the same data
            } else {
                scheduleRetry();   // 429 / 5xx: try again later, quietly
            }
            if (pendingAfterFlight) { pendingAfterFlight = false; schedule(); }
        }).catch(function () {
            if (timeout) window.clearTimeout(timeout);
            inFlight = false;
            scheduleRetry();
        });
    }

    function scheduleRetry() {
        if (retries >= MAX_RETRIES) return; // give up silently; form is unaffected
        retries += 1;
        window.clearTimeout(retryTimer);
        retryTimer = window.setTimeout(flush, 3000 * Math.pow(2, retries - 1));
    }

    function flush(useKeepalive) {
        if (disabled) return;
        window.clearTimeout(debounceTimer);
        try {
            if (!$("apLeadNotice")) return; // never capture before the applicant has been informed
            var payload = buildPayload();
            if (!payload) return;
            var key = keyOf(payload);
            if (key === lastSentKey) return;
            if (inFlight) { pendingAfterFlight = true; return; }
            send(payload, key, useKeepalive === true);
        } catch (e) {
            /* never let lead capture affect the page */
        }
    }

    function schedule() {
        if (disabled) return;
        window.clearTimeout(debounceTimer);
        debounceTimer = window.setTimeout(flush, DEBOUNCE_MS);
    }

    /*---------- wiring ----------*/
    function bind() {
        if (!$("applyWizard") || !$("apFullname") || !$("apPhone")) return;
        ["apFullname", "apPhone", "apEmail"].forEach(function (id) {
            var el = $(id);
            if (!el) return;
            el.addEventListener("input", schedule);
            el.addEventListener("blur", function () { flush(); });
        });
        ["apSchool", "apMode"].forEach(function (id) {
            var el = $(id);
            if (el) el.addEventListener("change", schedule);
        });
        document.addEventListener("gti:programme-selected", schedule);
        // Leaving the page: one last best-effort send that survives navigation.
        window.addEventListener("pagehide", function () { flush(true); });
        document.addEventListener("visibilitychange", function () {
            if (document.visibilityState === "hidden") flush(true);
        });
    }

    window.GTILeadCapture = {
        token: function () { return disabled ? null : getToken(false); },
        flush: function () { flush(); },
        markSubmitted: function () { disabled = true; window.clearTimeout(debounceTimer); window.clearTimeout(retryTimer); forgetToken(); }
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bind);
    } else {
        bind();
    }
})(window, document);

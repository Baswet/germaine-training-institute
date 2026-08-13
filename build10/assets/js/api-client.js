/*==================================================
    GERMAINE — CENTRALIZED BACKEND API CLIENT (Step 6)

    The ONE place in the whole frontend that knows the backend's base
    URL and response envelope shape. Every integrated form/page calls
    through window.GermaineAPI instead of hardcoding fetch()/URLs
    directly — this is what makes it possible to point the site at a
    different backend (local / staging / production) by changing one
    constant here, not by editing every page's script.

    Backend contract (germaine-backend/API_DOCS.md):
      success: {"success": true,  "data": <any>, "message": "..."}
      error:   {"success": false, "data": null,  "message": "...", "errors": {...}}

    This file never reads or stores any credential, secret, or
    database detail — it only knows the backend's public HTTP base URL,
    exactly like any other same-origin/CORS API client.
==================================================*/

(function (window) {
    "use strict";

    /* ---------------------------------------------------------------
       BASE URL — the single place to change environments.

       Phase 15 fix: this used to fall back to a hardcoded
       "http://localhost:5000" whenever window.GERMAINE_API_BASE_URL
       wasn't set, with no page anywhere in build10/ actually setting
       that override. Deployed as-is, that meant every integrated form
       and every catalogue/news/site-content read on the live public
       site would have tried to fetch from the *visitor's own machine*
       (localhost, from their browser's point of view) instead of the
       real backend — a silent, site-wide production outage that
       DEPLOYMENT.md incorrectly claimed didn't exist ("api-client.js
       already auto-derives its API base URL from the page's own
       origin"). It didn't then, and same-origin is no longer even the
       real deployment shape: the frontend is published on GitHub Pages
       (baswet.github.io) and the backend on Render (gti-backend.
       onrender.com) — two different origins, so window.location.origin
       is never correct for this deployment. The non-localhost fallback
       below now points at that production API origin directly. Still
       fully overridable per-page via window.GERMAINE_API_BASE_URL,
       e.g. for a future custom domain fronting a different backend:

           <script>window.GERMAINE_API_BASE_URL = "https://api.germaineinstitute.com";</script>
           <script defer src="assets/js/api-client.js"></script>
    --------------------------------------------------------------- */
    var PRODUCTION_API_BASE_URL = "https://gti-backend-zh4t.onrender.com";
    var API_BASE_URL = window.GERMAINE_API_BASE_URL || (function () {
        var host = window.location.hostname;
        if (host === "127.0.0.1" || host === "localhost" || host === "") {
            return "http://localhost:5000";
        }
        return PRODUCTION_API_BASE_URL;
    })();
    var DEFAULT_TIMEOUT_MS = 15000;

    function buildUrl(path, params) {
        var url = /^https?:\/\//i.test(path) ? path : API_BASE_URL + path;
        if (params) {
            var query = Object.keys(params)
                .filter(function (k) { return params[k] !== undefined && params[k] !== null && params[k] !== ""; })
                .map(function (k) { return encodeURIComponent(k) + "=" + encodeURIComponent(params[k]); })
                .join("&");
            if (query) url += (url.indexOf("?") === -1 ? "?" : "&") + query;
        }
        return url;
    }

    /**
     * Normalizes every possible outcome (success, validation error, server
     * error, network failure, timeout, non-JSON response) into the SAME
     * shape, so calling code never has to special-case network failures
     * separately from backend errors:
     *
     *   { success: bool, status: number|null, data, message, errors, networkError: bool }
     */
    function request(method, path, options) {
        options = options || {};
        var controller = (typeof AbortController !== "undefined") ? new AbortController() : null;
        var timeoutId = controller && window.setTimeout(function () { controller.abort(); }, options.timeout || DEFAULT_TIMEOUT_MS);

        var fetchOptions = {
            method: method,
            headers: { "Accept": "application/json" },
            signal: controller ? controller.signal : undefined,
        };
        if (options.body !== undefined) {
            fetchOptions.headers["Content-Type"] = "application/json";
            fetchOptions.body = JSON.stringify(options.body);
        }

        return fetch(buildUrl(path, options.params), fetchOptions)
            .then(function (response) {
                if (timeoutId) window.clearTimeout(timeoutId);
                return response.json()
                    .catch(function () {
                        // Response wasn't valid JSON at all — never show that to a user.
                        return null;
                    })
                    .then(function (body) {
                        if (!body || typeof body.success !== "boolean") {
                            return {
                                success: false,
                                status: response.status,
                                data: null,
                                message: "The server returned an unexpected response. Please try again shortly.",
                                errors: undefined,
                                networkError: false,
                            };
                        }
                        return {
                            success: body.success,
                            status: response.status,
                            data: body.data !== undefined ? body.data : null,
                            message: body.message || (body.success ? "Request completed successfully." : "The request could not be completed."),
                            errors: body.errors,
                            networkError: false,
                        };
                    });
            })
            .catch(function (err) {
                if (timeoutId) window.clearTimeout(timeoutId);
                var timedOut = err && err.name === "AbortError";
                return {
                    success: false,
                    status: null,
                    data: null,
                    message: timedOut
                        ? "The request timed out. Please check your connection and try again."
                        : "We couldn't reach the server. Please check your connection and try again.",
                    errors: undefined,
                    networkError: true,
                };
            });
    }

    window.GermaineAPI = {
        BASE_URL: API_BASE_URL,
        get: function (path, params) { return request("GET", path, { params: params }); },
        post: function (path, body) { return request("POST", path, { body: body }); },
    };

})(window);

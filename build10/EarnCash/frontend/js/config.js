/* ==========================================================
   EARNCASH FRONTEND CONFIG
   Single source of truth for the API base URL and small
   shared helpers used across every page.
========================================================== */

const CONFIG = {
  // EarnCash is now integrated as a blueprint inside the main Germaine
  // backend (germaine-backend/app/blueprints/earncash/), so it shares
  // that same server/port instead of running standalone. All EarnCash
  // routes are namespaced under /api/earncash so they can never collide
  // with Germaine's own /api/admissions, /api/alumni, etc.
  //
  // In local development, these static EarnCash pages and the Flask
  // backend run as two separate processes/origins (see README), so the
  // API base can't be derived from window.location the way
  // GTI_SITE_URL below is — it has to stay a fixed localhost URL.
  // In production, this static site is published on GitHub Pages
  // (baswet.github.io) and the Flask backend on Render (gti-backend.
  // onrender.com) — two different origins, matching how api-client.js
  // (assets/js/api-client.js, the main GTI site's equivalent config)
  // now points at that same production API origin, for the same reason.
  API_BASE: (function () {
    var host = window.location.hostname;
    if (host === "127.0.0.1" || host === "localhost" || host === "") {
      return "http://127.0.0.1:5000/api/earncash";
    }
    return "https://gti-backend.onrender.com/api/earncash";
  })(),

  // Base URL of the main Germaine Training Institute site, derived from
  // this page's own URL rather than hardcoded, so it keeps working
  // wherever the whole build10/ folder is actually deployed. EarnCash
  // pages always live at .../EarnCash/frontend/pages/<page>.html, and
  // the GTI site's own pages (ai-bootcamp-courses.html, etc.) always
  // live three directories up from there — used to build the real
  // "Refer to GTI Bootcamps" link (see dashboard.js), which is a
  // separate, additive referral link from the existing EarnCash
  // sign-up affiliate link above it.
  GTI_SITE_URL: window.location.origin + window.location.pathname.replace(/EarnCash\/frontend\/pages\/.*$/, ""),
};

/* ==========================================================
   SHARED FETCH HELPER
   Attaches the JWT (if present) and gives callers a consistent
   { ok, status, data } shape instead of juggling try/catch
   everywhere.
========================================================== */
async function apiRequest(path, { method = "GET", body = null, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };

  if (auth) {
    const token = localStorage.getItem("token");
    if (token) headers["Authorization"] = "Bearer " + token;
  }

  try {
    const response = await fetch(CONFIG.API_BASE + path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
    });

    let data = null;
    try {
      data = await response.json();
    } catch (_) {
      // no JSON body (e.g. some error pages) — leave data as null
    }

    return { ok: response.ok, status: response.status, data: data || {} };
  } catch (err) {
    return { ok: false, status: 0, data: { error: "Could not reach the server. Is the backend running?" } };
  }
}

/* ==========================================================
   FORMATTING HELPERS
========================================================== */
function formatKES(amount) {
  const n = Number(amount || 0);
  return "KES " + n.toLocaleString("en-KE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatDate(dateString) {
  if (!dateString) return "";
  const d = new Date(dateString);
  if (isNaN(d)) return dateString;
  return d.toLocaleDateString("en-KE", { year: "numeric", month: "short", day: "numeric" });
}

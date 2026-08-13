/* ==========================================================
   EARNCASH ENROLLMENTS
   Real data only — pulled from the actual EarnCash API
   (GET /courses/my-enrollments). No fake enrollment rows are
   ever invented here.

   Course discovery and applications happen on the real
   Germaine Training Institute website, not inside EarnCash.
   EarnCash's own internal /courses catalogue is intentionally
   NOT browsed/rendered on this page — showing it here made it
   look like EarnCash has its own separate course catalogue,
   which conflicts with (and duplicates) the real GTI
   admissions/application flow. This page now only shows a
   user's REAL enrollment records (if any exist) and, in every
   other case, a two-path gateway pointing to the two real GTI
   discovery hubs — never a "No courses available" dead end.
========================================================== */

const coursesUser = checkLogin();

if (coursesUser) {
  loadMyEnrollments();
}

const PAYMENT_STATUS_LABEL = {
  unpaid: "Awaiting Payment",
  partial: "Partially Paid",
  paid: "Payment Confirmed",
};

const PAYMENT_STATUS_CLASS = {
  unpaid: "status-pending",
  partial: "status-pending",
  paid: "status-approved",
};

/* Real, already-configured GTI destinations — both derived from the
   same CONFIG.GTI_SITE_URL base (config.js) used elsewhere (dashboard.js
   "Refer to GTI Bootcamps" link). Nothing invented:
   - AI Bootcamps hub = ai-bootcamp-courses.html (the real Explore
     Programmes catalogue with all 14 bootcamp cards).
   - Academic Schools hub = courses.html (the real Academic Schools
     catalogue, linked as "Academic Schools" from the main GTI nav in
     about.html, and already reused as the "Resources" sidebar link
     on this same EarnCash dashboard). */
function aiBootcampUrl() {
  return CONFIG.GTI_SITE_URL + "ai-bootcamp-courses.html";
}
function academicSchoolsUrl() {
  return CONFIG.GTI_SITE_URL + "courses.html";
}

function gatewayHtml(compact) {
  if (compact) {
    return (
      '<div class="glass gti-gateway-wrap gti-gateway-wrap-compact">' +
      "<h3>Continue exploring</h3>" +
      '<div class="gti-gateway-cards gti-gateway-cards-compact">' +
      '<a class="gti-gateway-mini" href="' + aiBootcampUrl() + '" target="_blank" rel="noopener"><i data-lucide="brain-circuit"></i> AI Bootcamps <i data-lucide="arrow-right"></i></a>' +
      '<a class="gti-gateway-mini gti-gateway-mini-blue" href="' + academicSchoolsUrl() + '" target="_blank" rel="noopener"><i data-lucide="landmark"></i> Academic Schools <i data-lucide="arrow-right"></i></a>' +
      "</div></div>"
    );
  }

  return (
    '<div class="glass gti-gateway-wrap">' +
    '<div class="gti-gateway-head">' +
    "<h2>Start Your Learning Journey</h2>" +
    "<p>Explore our programmes and apply directly through Germaine Training Institute. Choose the learning path that best fits your goals.</p>" +
    "</div>" +
    '<div class="gti-gateway-cards">' +

    '<a class="gti-gateway-path-card" href="' + aiBootcampUrl() + '" target="_blank" rel="noopener">' +
    '<span class="gti-gateway-path-ic"><i data-lucide="brain-circuit"></i></span>' +
    "<h3>AI Bootcamps</h3>" +
    "<p>Build practical, industry-ready AI skills through focused bootcamp programmes designed around hands-on learning and modern technology.</p>" +
    '<span class="gti-gateway-path-cta">Explore AI Bootcamps <i data-lucide="arrow-right"></i></span>' +
    "</a>" +

    '<a class="gti-gateway-path-card gti-gateway-path-card-blue" href="' + academicSchoolsUrl() + '" target="_blank" rel="noopener">' +
    '<span class="gti-gateway-path-ic"><i data-lucide="landmark"></i></span>' +
    "<h3>Academic Schools</h3>" +
    "<p>Explore Germaine Training Institute&rsquo;s academic schools, programmes, qualifications and career-focused training opportunities.</p>" +
    '<span class="gti-gateway-path-cta">Explore Academic Schools <i data-lucide="arrow-right"></i></span>' +
    "</a>" +

    "</div></div>"
  );
}

async function loadMyEnrollments() {
  const container = document.getElementById("enrollmentList");
  if (!container) return;

  const { ok, data } = await apiRequest("/courses/my-enrollments");

  if (!ok) {
    // A failed request must never be presented as "you have no
    // enrollments" — that would misrepresent an outage as a real,
    // empty account state.
    container.innerHTML = "<p>Unable to load your enrollments.</p>";
    return;
  }

  if (!data.length) {
    container.innerHTML = gatewayHtml(false);
    if (window.lucide) lucide.createIcons();
    return;
  }

  const rowsHtml = data
    .map((e) => {
      const statusLabel = PAYMENT_STATUS_LABEL[e.payment_status] || e.payment_status;
      const statusClass = PAYMENT_STATUS_CLASS[e.payment_status] || "";
      return `
        <div class="transaction-row">
          <div>
            <strong>${escapeHtml(e.course_name || "Programme")}</strong>
            <span class="tx-date">${escapeHtml(e.category || "")} &middot; Enrolled ${formatDate(e.created_at)}</span>
          </div>
          <div class="enrollment-right">
            <span class="${statusClass}">${escapeHtml(statusLabel)}</span>
            <span class="tx-date">${formatKES(e.amount_paid)} / ${formatKES(e.amount_due)}</span>
          </div>
        </div>`;
    })
    .join("");

  container.innerHTML = rowsHtml + gatewayHtml(true);
  if (window.lucide) lucide.createIcons();
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

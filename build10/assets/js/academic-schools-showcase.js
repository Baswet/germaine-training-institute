/*==================================================
    GERMAINE — SHARED ACADEMIC SCHOOLS SIDEBAR
    The ONE Academic Schools navigation used across the whole
    academic section, from window.SCHOOL_DATA / SCHOOL_ORDER
    (assets/js/school-data.js). Same markup, styling and data
    source everywhere — no duplicate sidebar system.

    Sidebar items show the school title ONLY — no departments,
    no dropdowns, no accordion. It is a simple, flat navigation
    list. Departments live inside the main content area instead:
    as department cards on the Academics page overview, and as a
    department selector bar above the programme listing on each
    View Programmes page (both built elsewhere — see
    departmentCardsHtml() below and school-page.js's
    buildDeptSelector()).

    Two behaviours, auto-detected per page:

    1) ACADEMICS PAGE (courses.html, has #ashPanel) — nothing
       navigates away. Selecting a school swaps the panel to
       that school's hero image, full description, entry
       requirements (no fees on this page), an Explore
       Programmes button, and — where the school has
       departments — a grid of department cards underneath.

    2) VIEW PROGRAMMES PAGES (courses-*.html, no #ashPanel) —
       sidebar items are real links to each school's own page,
       current school highlighted. Department selection happens
       on the page itself (department selector bar / ?dept=
       deep link), not in the sidebar.
==================================================*/
(function () {
    "use strict";

    var sidebarMount = document.getElementById("ashSidebarNav");
    if (!sidebarMount) return;

    var panel = document.getElementById("ashPanel");
    var DATA = window.SCHOOL_DATA || {};
    var ORDER = window.SCHOOL_ORDER || Object.keys(DATA);
    var currentSchool = document.body.getAttribute("data-school");

    /* Entry requirements are identical across every school. */
    var REQUIREMENTS = [
        { icon: "fa-graduation-cap", level: "Diploma Programmes", grade: "KCSE Mean Grade C-" },
        { icon: "fa-certificate", level: "Certificate Programmes", grade: "KCSE Mean Grade D" },
        { icon: "fa-toolbox", level: "Artisan Programmes", grade: "KCSE Mean Grade D-" }
    ];

    function esc(s) { return String(s == null ? "" : s); }

    function paragraphs(text) {
        return esc(text).split("\n\n").map(function (p) { return "<p>" + p + "</p>"; }).join("");
    }

    /* ---------- shared blocks ---------- */
    function requirementsHtml() {
        return '<div class="ash-reqs">' +
            '<span class="ash-reqs-title"><i class="fa-solid fa-clipboard-check"></i> Entry Requirements</span>' +
            '<ul>' + REQUIREMENTS.map(function (r) {
                return "<li><span>" + r.level + "</span><b>" + r.grade + "</b></li>";
            }).join("") + "</ul>" +
        "</div>";
    }

    /* Compact department cards shown beneath the school overview (and
       ONLY there — never in the sidebar) — title only, no image/
       description/button. The whole card is a single link to that
       department's View Programmes view. */
    function departmentCardsHtml(s) {
        if (!s.departments || !s.departments.length) return "";
        return '<div class="ash-deptcards">' +
            '<h3 class="ash-deptcards-title">Departments</h3>' +
            '<div class="ash-deptcards-grid">' +
                s.departments.map(function (d, di) {
                    return '<a href="' + esc(s.url || "#") + "?dept=" + di + '" class="ash-deptcard">' +
                        '<span class="ash-deptcard-name">' + esc(d.name) + "</span>" +
                        '<i class="fa-solid fa-arrow-right ash-deptcard-arrow" aria-hidden="true"></i>' +
                    "</a>";
                }).join("") +
            "</div>" +
        "</div>";
    }

    if (panel) {
        /* ================= MODE 1: Academics page ================= */
        /* Plain, flat list — school names only. */

        sidebarMount.innerHTML = ORDER.map(function (key, i) {
            var s = DATA[key];
            if (!s) return "";
            return '<button type="button" class="ash-nav-item' + (i === 0 ? " is-active" : "") + '" data-school="' + key + '" aria-pressed="' + (i === 0 ? "true" : "false") + '">' +
                '<span class="ash-nav-name">' + esc(s.label) + "</span>" +
            "</button>";
        }).join("");

        var navItems = sidebarMount.querySelectorAll(".ash-nav-item");

        function renderSchool(key) {
            var s = DATA[key];
            if (!s) return;
            panel.innerHTML =
                '<div class="ash-panel-inner">' +
                    '<div class="ash-preview-image" style="background-image:url(&quot;' + esc(s.image) + '&quot;)" role="img" aria-label="' + esc(s.label) + '"></div>' +
                    '<div class="ash-preview-body">' +
                        '<span class="section-tag">' + esc(s.badge || s.label) + "</span>" +
                        "<h2>" + esc(s.label) + "</h2>" +
                        '<div class="ash-desc">' + paragraphs(s.description || s.intro) + "</div>" +
                        requirementsHtml() +
                        '<a href="' + esc(s.url || "#") + '" class="btn-primary ash-preview-cta">Explore Programmes <i class="fa-solid fa-arrow-right"></i></a>' +
                        departmentCardsHtml(s) +
                    "</div>" +
                "</div>";
        }

        function clearActive() {
            navItems.forEach(function (n) { n.classList.remove("is-active"); n.setAttribute("aria-pressed", "false"); });
        }

        navItems.forEach(function (item) {
            item.addEventListener("click", function () {
                var key = item.getAttribute("data-school");
                clearActive();
                item.classList.add("is-active");
                item.setAttribute("aria-pressed", "true");
                renderSchool(key);
            });
        });

        var firstKey = ORDER.filter(function (k) { return DATA[k]; })[0];
        if (firstKey) { renderSchool(firstKey); }

    } else {
        /* ================= MODE 2: View Programmes pages ================= */
        /* Plain, flat list of real links — school names only. Department
           selection lives on the page itself, not in this sidebar. */

        sidebarMount.innerHTML = ORDER.map(function (key) {
            var s = DATA[key];
            if (!s) return "";
            var isActive = key === currentSchool;
            return '<a href="' + esc(s.url || "#") + '" class="ash-nav-item' + (isActive ? " is-active" : "") + '"' + (isActive ? ' aria-current="page"' : "") + ">" +
                '<span class="ash-nav-name">' + esc(s.label) + "</span>" +
            "</a>";
        }).join("");
    }

    /* ---------- ambient hero particles (no-ops where absent) ---------- */
    var particleHost = document.getElementById("sdHeroParticles");
    if (particleHost) {
        for (var i = 0; i < 16; i++) {
            var p = document.createElement("span");
            p.className = "sd-particle";
            p.style.left = (Math.random() * 100) + "%";
            p.style.bottom = (Math.random() * 40) + "%";
            p.style.animationDuration = (10 + Math.random() * 10) + "s";
            p.style.animationDelay = (Math.random() * 8) + "s";
            particleHost.appendChild(p);
        }
    }
})();

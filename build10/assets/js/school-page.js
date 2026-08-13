/*==================================================
    GERMAINE — ACADEMIC SCHOOL PAGE SCRIPT
    Renders the school navigation sidebar from
    SCHOOL_DATA / SCHOOL_ORDER (school-data.js) as real
    links to each school's own page (so hero, badge,
    about, why-choose, careers and portals always match
    exactly — no partial in-page swap), sets the hero
    badge text to the current school, and drives the
    programme search/filter/reveal behaviour.
==================================================*/
(function () {
    "use strict";

    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var hasSchoolData = typeof window.SCHOOL_DATA === "object" && typeof window.SCHOOL_ORDER === "object";
    var currentSchool = document.body.getAttribute("data-school") || (hasSchoolData ? window.SCHOOL_ORDER[0] : null);
    var activeFilter = "all";

    /* ---------- HERO PARTICLES ---------- */
    var particleWrap = document.getElementById("spHeroParticles") || document.querySelector(".sp-hero-particles");
    if (particleWrap && !reduceMotion) {
        for (var i = 0; i < 16; i++) {
            var p = document.createElement("span");
            p.style.left = Math.random() * 100 + "%";
            p.style.top = Math.random() * 100 + "%";
            p.style.animationDelay = (Math.random() * 6) + "s";
            p.style.animationDuration = (5 + Math.random() * 4) + "s";
            particleWrap.appendChild(p);
        }
    }

    /* ---------- AMBIENT PAGE PARTICLES ---------- */
    var pageParticleWrap = document.getElementById("spPageParticles");
    if (pageParticleWrap && !reduceMotion) {
        for (var j = 0; j < 26; j++) {
            var pp = document.createElement("span");
            pp.style.left = Math.random() * 100 + "%";
            pp.style.top = Math.random() * 100 + "%";
            pp.style.animationDelay = (Math.random() * 12) + "s";
            pp.style.animationDuration = (24 + Math.random() * 20) + "s";
            pageParticleWrap.appendChild(pp);
        }
    }

    /* ---------- SIDEBAR RENDER ---------- */
    var sidebarNav = document.getElementById("spSidebarNav");

    function renderSidebar() {
        if (!sidebarNav || !hasSchoolData) return;
        sidebarNav.innerHTML = window.SCHOOL_ORDER.map(function (sid) {
            var s = window.SCHOOL_DATA[sid];
            var isActive = sid === currentSchool;
            var countLabel = s.count > 0 ? (s.count + " programmes") : "Coming soon";
            return (
                '<a class="sp-nav-item' + (isActive ? " active" : "") + '" href="' + s.url + '" aria-current="' + (isActive ? "page" : "false") + '">' +
                    '<span class="sp-nav-text">' +
                        '<span class="sp-nav-name">' + s.label + '</span>' +
                        '<span class="sp-nav-count">' + countLabel + '</span>' +
                    '</span>' +
                    '<i class="fa-solid fa-chevron-right sp-nav-arrow"></i>' +
                '</a>'
            );
        }).join("");
    }

    /* ---------- DYNAMIC HERO BADGE ----------
       The hero badge pill was removed per brief: it repeated the school
       name already carried by the <h1>. This is now a no-op guard so the
       rest of the init sequence is unchanged and any cached page that
       still ships a .sp-badge simply leaves it alone. */
    function renderBadge() {
        return;
    }

    /* ---------- PROGRAMME CARD RENDER (grouped by level) ---------- */
    function levelBadgeClass(levelClass) {
        return { diploma: "lvl-diploma", certificate: "lvl-certificate", craft: "lvl-certificate", artisan: "lvl-artisan", professional: "lvl-professional" }[levelClass] || "lvl-certificate";
    }

    function rowHtml(p) {
        return (
            '<tr class="sp-prog-row" data-level="' + p.levelClass + '" data-name="' + p.name.replace(/"/g, "&quot;") + '">' +
                '<td class="sp-col-name">' + p.name + '</td>' +
                '<td class="sp-col-duration"><i class="fa-solid fa-clock"></i> ' + p.duration + '</td>' +
                '<td class="sp-col-level"><span class="sp-level-badge ' + levelBadgeClass(p.levelClass) + '">' + p.level + '</span></td>' +
            '</tr>'
        );
    }

    function renderProgrammes(school) {
        var grid = document.getElementById("spProgGrid");
        var noResults = document.getElementById("spNoResults");
        if (!grid) return;

        if (!school.programmes.length) {
            grid.innerHTML = "";
            if (noResults) {
                noResults.style.display = "block";
                noResults.textContent = "Full programme listing for this school is being finalized — contact admissions on +254 719 488 112.";
            }
            return;
        }
        if (noResults) noResults.style.display = "none";

        var rows = school.programmes.map(rowHtml).join("");
        grid.innerHTML =
            '<div class="sp-prog-table-wrap">' +
                '<table class="sp-prog-table">' +
                    '<thead><tr>' +
                        '<th class="sp-col-name">Programme</th>' +
                        '<th class="sp-col-duration">Duration</th>' +
                        '<th class="sp-col-level">Level</th>' +
                    '</tr></thead>' +
                    '<tbody>' + rows + '</tbody>' +
                '</table>' +
            '</div>';

        applyFilters();
    }

    /* ---------- CAREER OPPORTUNITIES + CAREER PORTALS ----------
       Both sections are scoped to the CURRENTLY SELECTED department —
       never pooled across every department in the school. For a
       school with departments, "selected" means: the department the
       page opened on (?dept=N) or the one chosen from the department
       selector; when no department is explicitly chosen yet, the
       first department's careers/portals are shown (never a merged
       list). Schools without departments use their own school-level
       careers/quickLinks. Sections that end up with no data hide
       themselves rather than showing an empty block. */

    function activeCareerSource(school, dept) {
        if (dept) return dept;
        if (school.departments && school.departments.length) return school.departments[0];
        return school;
    }

    function renderCareers(school, dept) {
        var list = document.getElementById("spCareerList");
        if (!list) return;
        var source = activeCareerSource(school, dept);
        var careers = (source && source.careers) || [];
        var wrap = list.closest(".sp-mini-card") || list.parentNode;
        if (!careers.length) {
            if (wrap) wrap.style.display = "none";
            return;
        }
        if (wrap) wrap.style.display = "";
        list.innerHTML = careers.map(function (c) { return "<li>" + c + "</li>"; }).join("");
    }

    function pillHtml(l) {
        return '<a href="' + l.url + '" target="_blank" rel="noopener noreferrer" class="sp-portal-item">' +
            '<i class="fa-solid fa-arrow-up-right-from-square"></i><span>' + l.label + "</span></a>";
    }

    function renderPortals(school, dept) {
        var section = document.getElementById("sp-portals");
        var mount = document.getElementById("spPortals");
        if (!section || !mount) return;

        var source = activeCareerSource(school, dept);
        var portals = (source && source.quickLinks) || [];
        if (!portals.length) {
            section.style.display = "none";
            return;
        }
        section.style.display = "";
        mount.innerHTML = portals.map(pillHtml).join("");
    }

    /* ---------- PROGRAMME SEARCH + FILTER ---------- */
    function applyFilters() {
        var searchInput = document.getElementById("spSearch");
        var term = (searchInput ? searchInput.value : "").trim().toLowerCase();
        var rows = document.querySelectorAll("#spProgGrid .sp-prog-row");
        var visibleCount = 0;

        rows.forEach(function (row) {
            var level = (row.getAttribute("data-level") || "").toLowerCase();
            var name = (row.getAttribute("data-name") || "").toLowerCase();
            var levelOk = activeFilter === "all" || level === activeFilter;
            var termOk = !term || name.indexOf(term) !== -1;
            /* a ?dept= deep link narrows the table to one department;
               search/level filters then apply within that department */
            var deptOk = row.getAttribute("data-dept-hidden") !== "true";
            var show = levelOk && termOk && deptOk;
            row.style.display = show ? "" : "none";
            if (show) visibleCount++;
        });

        var noResults = document.getElementById("spNoResults");
        if (noResults && rows.length) {
            noResults.style.display = visibleCount === 0 ? "block" : "none";
            noResults.textContent = "No programmes match your search.";
        }
    }

    document.addEventListener("input", function (e) {
        if (e.target && e.target.id === "spSearch") applyFilters();
    });
    document.addEventListener("click", function (e) {
        var btn = e.target.closest && e.target.closest(".sp-filter-btn");
        if (!btn) return;
        document.querySelectorAll(".sp-filter-btn").forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        activeFilter = (btn.getAttribute("data-filter") || "all").toLowerCase();
        applyFilters();
    });

    /* ---------- DEPARTMENT VIEW (?dept=N) ----------
       Schools WITH departments get a department-aware view: the hero
       image, title and description switch to the selected department,
       a compact department selector sits above the listing, and only
       that department's courses are shown. Schools WITHOUT departments
       are untouched and behave exactly as before. */
    var activeDeptIndex = null;

    function currentDeptIndex(school) {
        var match = /[?&]dept=(\d+)/.exec(window.location.search);
        if (!match) return null;
        var i = parseInt(match[1], 10);
        return (school.departments && school.departments[i]) ? i : null;
    }

    /* Keep the school blurb identical to the Academics page copy. */
    function syncSchoolDescription(school) {
        var about = document.getElementById("spAboutText");
        if (about && school.description) {
            about.innerHTML = school.description.split("\n\n").join("<br><br>");
        }
    }

    function applyDeptFilter(school, deptName) {
        document.querySelectorAll("#spProgGrid .sp-prog-row").forEach(function (row) {
            var name = row.getAttribute("data-name") || "";
            var inDept = !deptName || (school.programmes || []).some(function (p) {
                return p.dept === deptName && p.name === name;
            });
            row.setAttribute("data-dept-hidden", inDept ? "false" : "true");
        });
        applyFilters();
    }

    function paintDept(school, index) {
        activeDeptIndex = index;
        var dept = index === null ? null : school.departments[index];

        /* hero + heading */
        var photo = document.querySelector(".sp-hv-photo");
        var h1 = document.querySelector(".sp-hv-left h1");
        var about = document.getElementById("spAboutText");
        var heading = document.getElementById("spProgHeading");

        if (dept) {
            if (photo) { photo.src = dept.image; photo.alt = dept.name + " practical training at Germaine Institute"; }
            if (h1) h1.innerHTML = '<span class="sp-hl-pink">' + dept.name + "</span>";
            if (about) about.textContent = dept.description;
            if (heading) heading.textContent = dept.name + " — " + (dept.count || 0) + " Programmes";
        } else {
            if (photo && school.image) { photo.src = school.image; photo.alt = school.label + " students in practical training at Germaine Institute"; }
            if (h1) h1.innerHTML = '<span class="sp-hl-pink">' + school.label + "</span>";
            syncSchoolDescription(school);
            if (heading) heading.textContent = (school.count || 0) + " Programmes Across " + school.label;
        }

        document.querySelectorAll(".sp-deptbtn").forEach(function (b) {
            b.classList.toggle("active", String(b.getAttribute("data-dept")) === String(index));
        });

        applyDeptFilter(school, dept ? dept.name : null);
        renderCareers(school, dept);
        renderPortals(school, dept);
    }

    /* compact department selector, injected above the programme listing */
    function buildDeptSelector(school) {
        var progSection = document.querySelector(".sp-programmes");
        if (!progSection || !school.departments || !school.departments.length) return;

        var wrap = document.createElement("div");
        wrap.className = "sp-deptbar sp-reveal";
        wrap.innerHTML = '<span class="sp-deptbar-label">Departments</span>' +
            '<div class="sp-deptbar-row">' +
                '<button type="button" class="sp-deptbtn" data-dept="null">All Programmes</button>' +
                school.departments.map(function (d, i) {
                    return '<button type="button" class="sp-deptbtn" data-dept="' + i + '">' + d.name + "</button>";
                }).join("") +
            "</div>";
        progSection.parentNode.insertBefore(wrap, progSection);

        wrap.querySelectorAll(".sp-deptbtn").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var raw = btn.getAttribute("data-dept");
                var idx = raw === "null" ? null : parseInt(raw, 10);
                paintDept(school, idx);
                var url = idx === null ? window.location.pathname : window.location.pathname + "?dept=" + idx;
                window.history.replaceState({}, "", url);
            });
        });
    }

    function initDepartments(school) {
        syncSchoolDescription(school);
        if (!school.departments || !school.departments.length) return;
        buildDeptSelector(school);
        paintDept(school, currentDeptIndex(school));
    }

    /* ---------- SCROLL REVEAL (re-observable for dynamic content) ---------- */
    var io = null;
    function observeReveals() {
        var revealEls = document.querySelectorAll(".sp-reveal:not(.sp-show)");
        if (!revealEls.length) return;
        if (reduceMotion || typeof IntersectionObserver === "undefined") {
            revealEls.forEach(function (el) { el.classList.add("sp-show"); });
            return;
        }
        if (!io) {
            io = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("sp-show");
                        io.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.12 });
        }
        revealEls.forEach(function (el) { io.observe(el); });
    }

    /* Exposed so pages that inject markup AFTER this script has already
       run its first reveal pass (e.g. ai-course-detail-renderer.js, which
       populates mount points via mount.outerHTML on DOMContentLoaded)
       can register their newly-added .sp-reveal elements with the same
       observer instead of those elements staying invisible forever. */
    window.GermaineObserveReveals = observeReveals;

    /* ---------- INIT ---------- */
    renderSidebar();
    renderBadge();

    function renderSchoolContent() {
        if (hasSchoolData && currentSchool && window.SCHOOL_DATA[currentSchool]) {
            renderProgrammes(window.SCHOOL_DATA[currentSchool]);
            renderCareers(window.SCHOOL_DATA[currentSchool], null);
            renderPortals(window.SCHOOL_DATA[currentSchool], null);
            initDepartments(window.SCHOOL_DATA[currentSchool]);
        }
        observeReveals();
    }

    /* ---------- STEP 7: CATALOGUE API INTEGRATION ----------
       Before the first render, try refreshing THIS school's programme
       rows from the live Step 5 API (GET /api/programmes?school=<slug>).
       Deliberately narrow in scope: only school.programmes and
       school.count are ever overwritten, and only once the API call
       fully succeeds with a non-empty result. Every other field (hero
       image, intro text, fee display string, careers, quick links,
       department descriptions, sidebar for every OTHER school) is left
       exactly as school-data.js already provides it — untouched, so the
       existing renderer/markup/visual design cannot regress. Any
       failure (API unavailable, unexpected shape, network error) falls
       back to the static data silently: no skeleton, no error banner,
       no broken layout (Step 7 §13/§25/§26). */
    function refreshProgrammesFromApi(done) {
        if (!hasSchoolData || !currentSchool || !window.SCHOOL_DATA[currentSchool] || !window.GermaineAPI) {
            done();
            return;
        }
        // No programme table on this page (e.g. courses.html's directory
        // view, apply.html's wizard) — nothing for the fetched data to
        // feed into, so skip the request entirely (Step 7 §27).
        if (!document.getElementById("spProgGrid")) {
            done();
            return;
        }
        var school = window.SCHOOL_DATA[currentSchool];

        function mapProgramme(p) {
            return {
                name: p.name,
                level: p.level,
                levelClass: p.level_class,
                duration: p.duration,
                entry: p.entry_requirement,
                exam: p.exam_body,
                image: p.image_path || undefined,
                dept: (p.department && p.department.name) || undefined
            };
        }

        function fetchPage(page, accumulated) {
            window.GermaineAPI.get("/api/programmes", { school: currentSchool, per_page: 100, page: page, active_only: true })
                .then(function (res) {
                    if (!res.success || !res.data || !Array.isArray(res.data.items)) { done(); return; }
                    var combined = accumulated.concat(res.data.items);
                    if (combined.length < res.data.total && res.data.items.length > 0 && page < 10) {
                        fetchPage(page + 1, combined);
                        return;
                    }
                    if (!combined.length) { done(); return; } // never replace real data with an empty API result
                    school.programmes = combined.map(mapProgramme);
                    school.count = res.data.total;
                    done();
                })
                .catch(function () { done(); });
        }

        fetchPage(1, []);
    }

    refreshProgrammesFromApi(renderSchoolContent);
})();

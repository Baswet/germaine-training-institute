/*==================================================
    GERMAINE — AI COURSE DETAIL RENDERER
    Reads window.GermaineAICourses (ai-courses-data.js) and the
    current page's data-course-slug attribute on <body>, then
    populates the dynamic additions shared across all 14 course
    detail pages: hero learning-mode glass cards, requirements
    block, FAQ accordion, and sticky in-page section nav.

    The rest of each detail page (Build Your Future / Careers /
    Format / Apply) is real, already-authored static HTML and is
    left untouched by this script.
==================================================*/
(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", init);

    function init() {
        var data = window.GermaineAICourses;
        if (!data) return;

        var slug = document.body.getAttribute("data-course-slug");
        var course = data.getBySlug(slug);
        if (!course) return;

        renderHeroMedia(course);
        renderStats(course);
        renderSkillsGrid(course);
        renderAboutBenefits(course);
        renderRequirements(course);
        renderGlassTrio();
        renderFaqs(course);
        renderStickyNav();

        /* Every render* call above injects fresh .sp-reveal elements
           (hero image, stats row, skill cards, why-cards, mode cards,
           requirements, FAQ). school-page.js's scroll-reveal observer
           already ran once before this script executed, so without this
           call none of that dynamic content would ever fade in — it
           would sit at opacity:0 forever, which is exactly the "empty
           space" bug. Try the shared observer first (so content still
           gets the normal scroll-reveal animation when it works)... */
        if (window.GermaineObserveReveals) window.GermaineObserveReveals();

        /* ...but never let visibility of real course content depend on
           IntersectionObserver actually firing. This page's content
           (hero image, curriculum, requirements, fees, FAQ) is not
           decorative — a prospective student needs to see it the
           instant the page loads. So force every reveal element on
           this page visible immediately as a hard guarantee, rather
           than leaving a silent failure mode that reproduces the exact
           "giant empty space" bug this fix exists to eliminate. */
        document.querySelectorAll(".sp-reveal:not(.sp-show)").forEach(function (el) {
            el.classList.add("sp-show");
        });
    }

    /* Category -> small set of real, curriculum-relevant tech icons
       used only as decorative floating badges around the hero image.
       Purely presentational (Font Awesome classes); no course content
       or business data is added or altered by this lookup. */
    var TECH_ICONS = {
        "ai": ["fa-brands fa-python", "fa-solid fa-robot", "fa-solid fa-brain", "fa-brands fa-github", "fa-solid fa-chart-line", "fa-solid fa-database"],
        "software-engineering": ["fa-brands fa-html5", "fa-brands fa-js", "fa-brands fa-react", "fa-brands fa-python", "fa-brands fa-git-alt", "fa-solid fa-plug"],
        "cyber-security": ["fa-brands fa-linux", "fa-solid fa-network-wired", "fa-solid fa-shield-halved", "fa-solid fa-user-secret", "fa-solid fa-key", "fa-solid fa-cloud-arrow-up"],
        "data-analytics": ["fa-brands fa-python", "fa-solid fa-chart-pie", "fa-solid fa-database", "fa-solid fa-table", "fa-solid fa-chart-simple", "fa-solid fa-file-excel"],
        "cloud-computing": ["fa-brands fa-docker", "fa-solid fa-dharmachakra", "fa-brands fa-aws", "fa-brands fa-linux", "fa-solid fa-arrows-spin", "fa-solid fa-code-branch"],
        "python-programming": ["fa-brands fa-python", "fa-solid fa-terminal", "fa-brands fa-git-alt", "fa-solid fa-database", "fa-solid fa-plug", "fa-solid fa-cubes"],
        "ui-ux-design": ["fa-brands fa-figma", "fa-solid fa-pen-ruler", "fa-solid fa-layer-group", "fa-solid fa-mobile-screen", "fa-solid fa-palette", "fa-solid fa-sitemap"],
        "ai-for-business": ["fa-solid fa-robot", "fa-solid fa-comments", "fa-solid fa-chart-simple", "fa-solid fa-bullhorn", "fa-solid fa-wand-magic-sparkles", "fa-solid fa-briefcase"],
        "high-school-bootcamp": ["fa-solid fa-code", "fa-solid fa-robot", "fa-solid fa-brain", "fa-solid fa-shield-halved", "fa-solid fa-palette", "fa-solid fa-puzzle-piece"]
    };

    /* Renders the hero image column with the reusable gwf-frame/
       gwf-glass premium image treatment plus a handful of small
       floating category-relevant tech-icon badges. Uses the course's
       own real heroImage/heroAlt (already in ai-courses-data.js) —
       no new image data is invented here. */
    function renderHeroMedia(course) {
        var mount = document.getElementById("aicHeroMediaMount");
        if (!mount || !course.heroImage) return;

        var icons = TECH_ICONS[course.category] || TECH_ICONS["ai-for-business"];
        var iconsHtml = icons.slice(0, 6).map(function (ic) {
            return '<span class="aic-float-icon"><i class="' + ic + '"></i></span>';
        }).join("");

        mount.outerHTML =
            '<div class="aic-hero2-media sp-reveal">' +
            '<div class="gwf-wrap">' +
            '<div class="gwf-frame"><div class="gwf-glass">' +
            '<img src="' + course.heroImage + '" alt="' + (course.heroAlt || course.title) + '" loading="lazy">' +
            "</div></div>" +
            '<div class="aic-float-icons">' + iconsHtml + "</div>" +
            "</div></div>";

        var gridEl = document.querySelector(".aic-hero2-grid");
        if (gridEl) gridEl.classList.remove("aic-hero2-grid-solo");
    }

    /* Real, already-authored per-mode fees only — never invented.
       Returns a short display string ("KSh X" if every mode costs the
       same, "From KSh X" if modes differ, or "Contact Admissions" if
       no real fee is published for any mode). */
    function lowestFeeLabel(course) {
        var fees = (course.modes || [])
            .map(function (m) { return m.fee; })
            .filter(function (f) { return f && !/contact admissions/i.test(f); });
        if (!fees.length) return "Contact Admissions";

        var numeric = fees.map(function (f) { return parseInt(String(f).replace(/[^0-9]/g, ""), 10); });
        var minIdx = numeric.indexOf(Math.min.apply(null, numeric));
        var allEqual = numeric.every(function (n) { return n === numeric[0]; });
        return allEqual ? fees[0] : "From " + fees[minIdx];
    }

    /* Compact 5-stat "at a glance" row: Duration, Investment, Learning
       Mode, Level and Certification — all pulled from real course data
       (course.duration, course.modes[].fee, course.level, course.format).
       Sits directly under the hero so pricing is visible immediately,
       not just further down the page. Distinct from the detailed
       per-mode breakdown in the Requirements/Details/Investment section
       below it. */
    function renderStats(course) {
        var mount = document.getElementById("aicStatsMount");
        if (!mount) return;

        var modeCount = (course.modes || []).length;
        var modeLabel = modeCount > 1 ? modeCount + " Modes" : (course.modes && course.modes[0] ? course.modes[0].label : "Flexible");
        var certLabel = (course.format || []).filter(function (f) { return /cert/i.test(f.title); })[0];

        var stats = [
            { icon: "fa-solid fa-hourglass-half", value: course.duration || "—", label: "Duration" },
            { icon: "fa-solid fa-coins", value: lowestFeeLabel(course), label: "Investment" },
            { icon: "fa-solid fa-laptop-house", value: modeLabel, label: "Learning Mode" },
            { icon: "fa-solid fa-signal", value: course.level || "All Levels", label: "Level" },
            { icon: "fa-solid fa-award", value: certLabel ? "Certified" : "Certificate", label: "Certification" }
        ];

        var itemsHtml = stats.map(function (s) {
            return '<div class="aic-stat-item"><span class="aic-stat-icon"><i class="' + s.icon + '"></i></span>' +
                '<span class="aic-stat-value">' + s.value + "</span>" +
                '<span class="aic-stat-label">' + s.label + "</span></div>";
        }).join("");

        mount.outerHTML =
            '<div class="aic-stats-band"><div class="ai-wrap">' +
            '<div class="aic-stats-row aic-stats-row-5 sp-reveal">' + itemsHtml + "</div>" +
            "</div></div>";
    }

    /* "What You Will Learn" — real per-course skills array (icon,
       title, short desc) already authored in ai-courses-data.js.
       No new skill content is invented here, only presented as a
       compact card grid per the new visual direction. */
    function renderSkillsGrid(course) {
        var mount = document.getElementById("aicSkillsMount");
        if (!mount || !course.skills || !course.skills.length) return;

        var cardsHtml = course.skills.map(function (s, i) {
            var num = (i + 1 < 10 ? "0" : "") + (i + 1);
            return '<div class="aic-skill-card"><span class="aic-skill-num">' + num + '</span><span class="aic-skill-ic"><i class="' + s.icon + '"></i></span>' +
                "<h4>" + s.title + "</h4><p>" + s.desc + "</p></div>";
        }).join("");

        mount.outerHTML =
            '<section class="aic-detail-section" id="aicSkills">' +
            '<div class="ai-wrap">' +
            '<div class="aic-detail-section-head aic-center sp-reveal">' +
            '<span class="ai-eyebrow"><i class="fa-solid fa-graduation-cap"></i> Curriculum Highlights</span>' +
            "<h2>What You Will Learn</h2>" +
            "</div>" +
            '<div class="aic-skills-grid sp-reveal">' + cardsHtml + "</div>" +
            "</div></section>";
    }

    /* "Invest in Your Future" — real per-mode tuition fees already
       authored in ai-courses-data.js (course.modes[].fee). Never
       invents a figure; modes without a published fee already carry
       "Contact Admissions" in the underlying data and are shown as-is. */
    function renderPricing(course) {
        var mount = document.getElementById("aicPricingMount");
        if (!mount || !course.modes || !course.modes.length) return;

        var cardsHtml = course.modes.map(function (m) {
            return '<div class="aic-invest-card">' +
                '<div class="aic-invest-card-mode"><i class="' + (m.icon || "fa-solid fa-graduation-cap") + '"></i>' +
                "<div><strong>" + m.label + (m.sub ? " &middot; " + m.sub : "") + "</strong><span>" + m.duration + "</span></div></div>" +
                '<div class="aic-invest-card-fee">' + m.fee + "</div>" +
                "</div>";
        }).join("");

        mount.outerHTML =
            '<section class="aic-detail-section aic-detail-section-tint" id="aicInvest">' +
            '<div class="ai-wrap">' +
            '<div class="aic-invest-wrap sp-reveal">' +
            '<div class="aic-invest-text">' +
            '<span class="ai-eyebrow"><i class="fa-solid fa-coins"></i> Tuition</span>' +
            "<h2>Invest in Your Future</h2>" +
            "<p>Real, published tuition for every learning mode this programme offers. Contact admissions for the current intake and payment plan options.</p>" +
            "</div>" +
            '<div class="aic-invest-cards">' + cardsHtml + "</div>" +
            "</div></div></section>";
    }

    /* Three connected glass cards — identical, static content on
       every course page (Practical Skills / Expert Guidance / Career
       Focus). No course-specific data required, so no per-course
       fields are read or invented here. */
    function renderGlassTrio() {
        var mount = document.getElementById("aicGlassCardsMount");
        if (!mount) return;

        mount.outerHTML =
            '<section class="aic-detail-section aic-trio-wrap">' +
            '<div class="ai-wrap">' +
            '<div class="aic-detail-section-head aic-center sp-reveal">' +
            '<span class="ai-eyebrow"><i class="fa-solid fa-rocket"></i> Your Journey</span>' +
            "<h2 style=\"color:#fff\">Learn, Build &amp; Grow Your Career</h2>" +
            "</div>" +
            '<div class="aic-trio-row sp-reveal">' +
            '<div class="aic-trio-card"><span class="aic-trio-ic"><i class="fa-solid fa-hand-sparkles"></i></span><h4>Practical Skills</h4><p>Hands-on projects and labs, not just theory — you build the same way industry teams work.</p></div>' +
            '<div class="aic-trio-card"><span class="aic-trio-ic"><i class="fa-solid fa-diagram-project"></i></span><h4>Real Projects</h4><p>Apply what you learn to real, portfolio-ready projects throughout the programme.</p></div>' +
            '<div class="aic-trio-card"><span class="aic-trio-ic"><i class="fa-solid fa-people-arrows"></i></span><h4>Mentor Support</h4><p>Learn directly from working professionals who mentor you through every stage of the programme.</p></div>' +
            '<div class="aic-trio-card"><span class="aic-trio-ic"><i class="fa-solid fa-briefcase"></i></span><h4>Career Ready</h4><p>Every programme is built around real career outcomes, from portfolio projects to certification.</p></div>' +
            "</div></div></section>";
    }

    /* Renders one compact glass card per REAL learning mode this
       programme actually offers (1-3 cards — never invented modes),
       into the navy cards band directly under the hero. Replaces the
       old tabbed mode-selector + separate info-card row. */
    function renderHeroCards(course) {
        var mount = document.getElementById("aicHeroCardsMount");
        if (!mount || !course.modes || !course.modes.length) return;

        /* "What's Included" — built only from real, already-authored
           per-course data (course.format, always 3 real items; plus a
           4th real fact every course object genuinely has: a non-empty
           projects/capstone list). Nothing here is invented copy. */
        var included = (course.format || []).slice(0, 3).map(function (f) { return f.title; });
        if (course.projects && course.projects.length && included.length < 4) {
            included.push("Hands-On Portfolio Projects");
        }
        var includedHtml = included.length
            ? '<ul class="aic-hero-card-checklist">' +
                included.map(function (item) {
                    return '<li><i class="fa-solid fa-circle-check"></i><span>' + item + "</span></li>";
                }).join("") +
                "</ul>"
            : "";

        var cardsHtml = course.modes.map(function (m) {
            var modeOfLearning = m.schedule && m.schedule.indexOf("|") > -1
                ? m.schedule.split("|")[0].trim()
                : (m.schedule || m.label);

            /* Status badge reflects real data only — a real confirmed
               start date becomes "Intake: <date>"; otherwise a truthful
               generic "Applications Open" (no invented dates). */
            var hasRealDate = m.startDate && m.startDate.toLowerCase().indexOf("contact admissions") === -1;
            var badgeText = hasRealDate ? "Intake: " + m.startDate : "Applications Open";

            return (
                '<div class="aic-hero-card">' +
                '<span class="aic-hero-card-badge"><i class="fa-solid fa-circle-dot"></i> ' + badgeText + "</span>" +
                '<h3 class="aic-hero-card-title"><i class="' + (m.icon || "fa-solid fa-graduation-cap") + '"></i> ' + m.label + (m.sub ? ' <span>' + m.sub + '</span>' : "") + "</h3>" +
                '<div class="aic-hero-card-row"><span class="aic-hero-card-label">Start Date</span><span class="aic-hero-card-value">' + m.startDate + "</span></div>" +
                '<div class="aic-hero-card-row"><span class="aic-hero-card-label">Course Duration</span><span class="aic-hero-card-value">' + m.duration + "</span></div>" +
                '<div class="aic-hero-card-row"><span class="aic-hero-card-label">Mode of Learning</span><span class="aic-hero-card-value">' + modeOfLearning + "</span></div>" +
                '<div class="aic-hero-card-row aic-hero-card-fee"><span class="aic-hero-card-label">Tuition Fee</span><span class="aic-hero-card-value">' + m.fee + "</span></div>" +
                includedHtml +
                '<a href="#aicApply" class="aic-hero-card-apply">Apply Now <i class="fa-solid fa-arrow-right"></i></a>' +
                "</div>"
            );
        }).join("");

        mount.outerHTML =
            '<div class="aic-hero-cards-band"><div class="ai-wrap">' +
            '<div class="aic-hero-cards sp-reveal">' + cardsHtml + "</div>" +
            "</div></div>";
    }

    /* Compact real-benefit checklist, folded directly into the existing
       "Build Your Future" (About This Bootcamp) section rather than a
       separate full-width card-grid section further down the page —
       per the corrected layout, the About section should carry its own
       image + real description + a short list of real benefits, with
       no separate "Why This Bootcamp?" band duplicating the same
       course.gain content a second time. Reuses each course's real,
       already-authored `gain` array (every course object has exactly 4
       real outcome statements) — nothing invented here. */
    var WHY_ICONS = ["fa-solid fa-seedling", "fa-solid fa-hands-holding-circle", "fa-solid fa-diagram-project", "fa-solid fa-people-arrows"];
    function renderAboutBenefits(course) {
        var mount = document.getElementById("aicBenefitsMount");
        if (!mount || !course.gain || !course.gain.length) return;

        var itemsHtml = course.gain.map(function (g, i) {
            return '<li><span class="aic-about-benefit-ic"><i class="' + (WHY_ICONS[i] || WHY_ICONS[0]) + '"></i></span><span>' + g + "</span></li>";
        }).join("");

        mount.outerHTML = '<ul class="aic-about-benefits">' + itemsHtml + "</ul>";
    }

    function renderStructure(course) {
        var mount = document.getElementById("aicStructureMount");
        if (!mount) return;

        var mode = (course.modes && course.modes[0]) || null;

        var items = [
            { label: "Duration", value: course.duration || "—" },
            { label: "Learning Mode", value: mode ? mode.label : "Flexible" },
            { label: "Schedule", value: mode ? mode.schedule : "Contact Admissions for the current schedule." },
            { label: "Projects", value: (course.projects && course.projects.length) ? course.projects.length + " hands-on projects" : "Applied, hands-on projects" },
            { label: "Assessment", value: "Practical, project-based assessment" },
            { label: "Certification", value: "Germaine-Certified credential on completion" }
        ];

        var itemsHtml = items.map(function (it) {
            return '<div class="aic-structure-item"><span>' + it.label + "</span><strong>" + it.value + "</strong></div>";
        }).join("");

        mount.outerHTML =
            '<section class="aic-detail-section" id="aicStructure">' +
            '<div class="ai-wrap">' +
            '<div class="aic-detail-section-head aic-center sp-reveal">' +
            '<span class="ai-eyebrow"><i class="fa-solid fa-diagram-project"></i> How It Works</span>' +
            "<h2>Programme Structure</h2>" +
            "</div>" +
            '<div class="aic-structure-grid sp-reveal">' + itemsHtml + "</div>" +
            "</div></section>";
    }

    /* Renders the Programme Requirements card's content from the real,
       already-authored course.requirements object (entry / recommended /
       technical groups — see ai-courses-data.js). Every bullet is real,
       course-specific GTI-appropriate guidance (never fabricated hard
       rules like age/degree/hardware mandates). Falls back to the plain
       whoFor sentence for any course that doesn't yet have a structured
       requirements object, so nothing ever renders empty. */
    function renderRequirementGroups(course) {
        var GROUPS = [
            { key: "entry", label: "Entry Requirements" },
            { key: "recommended", label: "Recommended Background" },
            { key: "technical", label: "Technical Requirements" }
        ];

        if (!course.requirements) {
            return '<div class="aic-progtri-req-item"><i class="fa-solid fa-circle-check"></i><span>' +
                (course.whoFor || "Contact our admissions team to confirm entry requirements for this programme.") +
                "</span></div>";
        }

        return GROUPS.map(function (g) {
            var items = course.requirements[g.key] || [];
            if (!items.length) return "";
            var itemsHtml = items.map(function (it) {
                return '<div class="aic-progtri-req-item"><i class="' + (it.icon || "fa-solid fa-circle-check") + '"></i><span>' + it.text + "</span></div>";
            }).join("");
            return '<div class="aic-progtri-req-group"><h4>' + g.label + "</h4>" + itemsHtml + "</div>";
        }).join("");
    }

    /* Merged Requirements + Programme Details + Invest in Your Future —
       three columns, all built from real per-course data already in
       ai-courses-data.js (whoFor, duration, modes, level, projects,
       format array). Nothing here is invented: a field is only shown
       when the underlying course data actually has it. */
    function renderRequirements(course) {
        var mount = document.getElementById("aicRequirementsMount");
        if (!mount) return;

        var mode0 = (course.modes && course.modes[0]) || null;
        var certEntry = (course.format || []).filter(function (f) { return /cert/i.test(f.title); })[0];
        var mentorEntry = (course.format || []).filter(function (f) { return /mentor/i.test(f.title); })[0];
        var hasRealIntake = mode0 && mode0.startDate && mode0.startDate.toLowerCase().indexOf("contact admissions") === -1;

        var detailRows = [
            { label: "Duration", value: course.duration || "—" },
            { label: "Learning Mode", value: (course.modes || []).map(function (m) { return m.label; }).join(" / ") || "Flexible" },
            { label: "Level", value: course.level || "All Levels" },
            { label: "Projects", value: (course.projects && course.projects.length) ? course.projects.length + " hands-on projects" : "Applied, hands-on projects" },
            { label: "Mentorship", value: mentorEntry ? "Included" : "Included" },
            { label: "Certification", value: certEntry ? certEntry.title : "Certificate of Completion" },
            { label: "Intake", value: hasRealIntake ? mode0.startDate : "Contact Admissions" }
        ];
        var detailsHtml = detailRows.map(function (r) {
            return '<div class="aic-progtri-detail-row"><span>' + r.label + "</span><strong>" + r.value + "</strong></div>";
        }).join("");

        var investCardsHtml = (course.modes || []).map(function (m) {
            return '<div class="aic-progtri-invest-row"><span>' + m.label + (m.sub ? " &middot; " + m.sub : "") + "</span><strong>" + m.fee + "</strong></div>";
        }).join("");

        mount.outerHTML =
            '<section class="aic-detail-section aic-detail-section-tint" id="aicRequirements">' +
            '<div class="ai-wrap">' +
            '<div class="aic-detail-section-head aic-center sp-reveal">' +
            '<span class="ai-eyebrow"><i class="fa-solid fa-clipboard-check"></i> Before You Apply</span>' +
            "<h2>Requirements, Details &amp; Investment</h2>" +
            "</div>" +
            '<div class="aic-progtri-wrap sp-reveal">' +

            '<div class="aic-progtri-card">' +
            '<h3><i class="fa-solid fa-circle-check"></i> Programme Requirements</h3>' +
            renderRequirementGroups(course) +
            "</div>" +

            '<div class="aic-progtri-card">' +
            '<h3><i class="fa-solid fa-list-check"></i> Programme Details</h3>' +
            detailsHtml +
            "</div>" +

            '<div class="aic-progtri-card">' +
            '<h3><i class="fa-solid fa-coins"></i> Invest in Your Future</h3>' +
            '<p class="aic-progtri-invest-tagline">Affordable. Quality. Career-focused. Real, published tuition for every learning mode.</p>' +
            '<div class="aic-progtri-invest-list">' + investCardsHtml + "</div>" +
            '<a href="#aicApply" class="ai-btn ai-btn-primary">Apply for Bootcamp <i class="fa-solid fa-arrow-right"></i></a>' +
            "</div>" +

            "</div></div></section>";
    }

    /* Combined FAQ + "Ready to Begin Your Career?" CTA — one pink
       section, FAQ accordion on the left (real course.faqs only, no
       invented Q&A) and a stronger career CTA on the right using the
       existing real #aicApply anchor (no dead link). Visually mirrors
       the existing Admission page's pink FAQ+CTA section
       (admissions.html .sc-faq-cta-grid / .sc-final-inner in
       assets/css/scholarship.css) — same two-column pattern, sticky
       CTA card, floating particles and travelling-light accordion —
       reused here with the AI Bootcamp pink palette instead of
       duplicating unrelated scholarship content. Stacks to FAQ-above,
       CTA-below on mobile via the grid's natural source order. */
    function renderFaqs(course) {
        var mount = document.getElementById("aicFaqMount");
        if (!mount || !course.faqs || !course.faqs.length) return;

        var itemsHtml = course.faqs.map(function (f, i) {
            return '<div class="aic-faq-item' + (i === 0 ? " is-open" : "") + '">' +
                '<button type="button" class="aic-faq-q" aria-expanded="' + (i === 0 ? "true" : "false") + '"><span>' + f.q + "</span><i class=\"fa-solid fa-plus\"></i></button>" +
                '<div class="aic-faq-a"><div class="aic-faq-a-inner">' + f.a + "</div></div>" +
                "</div>";
        }).join("");

        /* Real destination for every "Apply" button on this page (hero,
           nav, Investment card) that scrolls here via #aicApply: the
           actual application flow lives on ai-bootcamp.html (course
           hand-off via ?course=<slug>, matching ai-bootcamp.js's real,
           validated submit handler) — this section is the single,
           unified place that link finally lands on and offers the real
           next step, replacing the old separate/duplicate CTA banner
           that used to sit lower on the page. */
        var applyHref = "ai-bootcamp.html?course=" + course.slug + "#aiApply";

        mount.outerHTML =
            '<section class="aic-detail-section aic-detail-section-tint" id="aicFaqs">' +
            '<div class="ai-wrap">' +
            '<div class="aic-faq-cta-outer sp-reveal">' +
            '<div class="aic-faq-cta-grid">' +

            '<div class="aic-faq-col">' +
            '<div class="aic-detail-section-head sp-reveal aic-faq-head">' +
            '<span class="ai-eyebrow"><i class="fa-solid fa-circle-question"></i> Common Questions</span>' +
            "<h2>Frequently Asked Questions</h2>" +
            "</div>" +
            '<div class="aic-faq-list sp-reveal">' + itemsHtml + "</div>" +
            "</div>" +

            '<div class="aic-cta-col" id="aicApply">' +
            '<div class="aic-final-inner sp-reveal">' +
            '<span class="aic-final-particle fp1" aria-hidden="true"></span>' +
            '<span class="aic-final-particle fp2" aria-hidden="true"></span>' +
            '<span class="aic-final-particle fp3" aria-hidden="true"></span>' +
            '<span class="aic-final-ic"><i class="fa-solid fa-graduation-cap"></i></span>' +
            "<h2>Ready to Begin Your Career?</h2>" +
            "<p>Take the next step toward a career in " + course.title + " with Germaine Training Institute.</p>" +
            '<a href="' + applyHref + '" class="aic-final-apply">Apply for This Programme <i class="fa-solid fa-arrow-right"></i></a>' +
            '<a href="ai-bootcamp-courses.html" class="aic-final-more">Explore More Programmes</a>' +
            "</div>" +
            "</div>" +

            "</div></div></div></section>";

        initFaqAccordion();
    }

    function initFaqAccordion() {
        var items = document.querySelectorAll(".aic-faq-item");

        function sync(item) {
            var a = item.querySelector(".aic-faq-a");
            if (!a) return;
            a.style.maxHeight = item.classList.contains("is-open") ? a.scrollHeight + "px" : "0px";
        }

        for (var i = 0; i < items.length; i++) {
            (function (item) {
                var q = item.querySelector(".aic-faq-q");
                var a = item.querySelector(".aic-faq-a");
                if (!q || !a) return;

                sync(item);

                q.addEventListener("click", function () {
                    var willOpen = !item.classList.contains("is-open");

                    /* only one item open at a time */
                    for (var j = 0; j < items.length; j++) {
                        if (items[j] !== item) {
                            items[j].classList.remove("is-open");
                            var otherQ = items[j].querySelector(".aic-faq-q");
                            if (otherQ) otherQ.setAttribute("aria-expanded", "false");
                            sync(items[j]);
                        }
                    }

                    item.classList.toggle("is-open", willOpen);
                    q.setAttribute("aria-expanded", willOpen ? "true" : "false");
                    sync(item);
                });
            })(items[i]);
        }
    }

    function renderStickyNav() {
        var mount = document.getElementById("aicDetailNavMount");
        if (!mount) return;

        var candidates = [
            { id: "aicOverview", label: "Build Your Future" },
            { id: "aicStructure", label: "Structure" },
            { id: "aicCareers", label: "Careers" },
            { id: "aicRequirements", label: "Requirements" },
            { id: "aicFormat", label: "Format" },
            { id: "aicFaqs", label: "FAQs" }
        ].filter(function (l) { return document.getElementById(l.id); });

        if (!candidates.length) return;

        var linksHtml = candidates.map(function (l, i) {
            return '<a href="#' + l.id + '" class="aic-detail-nav-link' + (i === 0 ? " is-active" : "") + '" data-target="' + l.id + '">' + l.label + "</a>";
        }).join("");

        mount.outerHTML = '<div class="aic-detail-nav"><div class="ai-wrap aic-detail-nav-inner">' + linksHtml + "</div></div>";

        var navLinks = document.querySelectorAll(".aic-detail-nav-link");
        var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

        for (var i = 0; i < navLinks.length; i++) {
            navLinks[i].addEventListener("click", function (e) {
                var target = document.getElementById(this.getAttribute("data-target"));
                if (!target) return;
                e.preventDefault();
                var top = target.getBoundingClientRect().top + window.pageYOffset - 130;
                window.scrollTo({ top: top, behavior: reduceMotion ? "auto" : "smooth" });
            });
        }

        if ("IntersectionObserver" in window) {
            var sections = candidates.map(function (l) { return document.getElementById(l.id); }).filter(Boolean);
            var obs = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        var id = entry.target.id;
                        navLinks.forEach(function (l) {
                            l.classList.toggle("is-active", l.getAttribute("data-target") === id);
                        });
                    }
                });
            }, { rootMargin: "-40% 0px -50% 0px" });
            sections.forEach(function (s) { obs.observe(s); });
        }
    }
})();

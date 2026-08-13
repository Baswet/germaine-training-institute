/*==================================================
    GERMAINE — AI BOOTCAMPS COURSES MENU (behaviour)
    Renders and drives a COMPACT overlay panel scoped to the AI
    Bootcamps internal navigation ("Courses" tab in .aic-subnav)
    as a straight THREE-COLUMN layout:
      Column 1 — programme categories (vertical list)
      Column 2 — selected category title + short description
      Column 3 — course offerings (real programme links)
    Selecting a category only updates columns 2 + 3 in place.
    Clicking an actual programme navigates to its real detail
    page. Only loaded on the AI Bootcamps family of pages
    (ai-bootcamp.html, ai-bootcamp-courses.html, ai-course-*.html)
    — NOT the global site navigation. Requires:
      - a trigger element with id="crsMenuTrigger" inside .aic-subnav
      - a mount element with id="crsMenuMount" right after .aic-subnav
    both injected once per page alongside this script. Course
    data comes from window.GermaineAICourses (ai-courses-data.js);
    the 6-category grouping below is this menu's own presentation
    layer on top of that shared data (the underlying 8-category
    taxonomy used by the catalogue/detail pages is untouched).
==================================================*/
(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", init);

    /* Category grouping shown in this menu. "slugs" reference real
       courses in ai-courses-data.js — nothing here is invented. */
    var MENU_CATEGORIES = [
        {
            id: "software-engineering",
            label: "Software Engineering",
            title: "Software Engineering",
            description: "Learn modern full-stack development — from front-end interfaces to back-end APIs and databases — and build production-ready applications using the same tools professional teams use.",
            slugs: ["software-engineering"]
        },
        {
            id: "data-courses",
            label: "Data Courses",
            title: "Data Courses",
            description: "Build practical, in-demand data skills — from beginner-friendly programming to analytics, data science and business intelligence — using real datasets rather than toy examples.",
            slugs: ["data-analytics", "python-programming", "data-science"]
        },
        {
            id: "cyber-security",
            label: "Cyber Security",
            title: "Cyber Security",
            description: "Develop hands-on cybersecurity skills across networking, ethical hacking, penetration testing, digital forensics and incident response in realistic lab environments.",
            slugs: ["cyber-security", "intro-cybersecurity"]
        },
        {
            id: "ai",
            label: "AI",
            title: "Artificial Intelligence",
            description: "Go from core machine learning concepts to generative AI — designing, training, evaluating and deploying AI systems that solve real problems, with a portfolio to show for it.",
            slugs: ["ai-ml"]
        },
        {
            id: "dpo",
            label: "DPO",
            title: "Digital Product & Operations (DPO)",
            description: "Shape how digital products look, feel and run — from user research, prototyping and design systems to containerised deployment and cloud infrastructure.",
            slugs: ["ui-ux-design", "cloud-computing", "intro-devops"]
        },
        {
            id: "ai-for-business",
            label: "AI for Business",
            title: "AI for Business",
            description: "Practical, non-technical AI skills for the workplace — generative AI productivity, no-code automation, and AI-powered digital marketing.",
            slugs: ["generative-ai-essentials", "ai-agents-automation", "digital-marketing-ai"]
        },
        {
            id: "high-school-bootcamp",
            label: "High School Bootcamp",
            title: "High School Bootcamp",
            description: "A holiday bootcamp giving high school students a fun, hands-on first taste of technology — coding, robotics and AI fundamentals — no prior experience needed.",
            slugs: ["high-school-bootcamp"]
        }
    ];

    function init() {
        var trigger = document.getElementById("crsMenuTrigger");
        var mount = document.getElementById("crsMenuMount");
        var data = window.GermaineAICourses;
        if (!trigger || !mount || !data) return;

        mount.outerHTML = buildMenuHTML();

        var menu = document.getElementById("crsMenu");
        var panel = document.getElementById("crsMenuPanel");
        var backdrop = document.getElementById("crsMenuBackdrop");
        var closeBtn = document.getElementById("crsMenuClose");
        var backBtn = document.getElementById("crsMenuBack");
        var catsWrap = document.getElementById("crsMenuCats");
        var descWrap = document.getElementById("crsMenuDesc");
        var offeringsWrap = document.getElementById("crsMenuOfferings");
        var body = document.getElementById("crsMenuBody");
        if (!menu || !panel) return;

        function renderCategory(catId) {
            var cat = null;
            for (var i = 0; i < MENU_CATEGORIES.length; i++) {
                if (MENU_CATEGORIES[i].id === catId) { cat = MENU_CATEGORIES[i]; break; }
            }
            if (!cat) return;

            descWrap.innerHTML =
                '<span class="crs-menu-desc-eyebrow">Programme Category</span>' +
                "<h3>" + cat.title + "</h3>" +
                "<p>" + cat.description + "</p>";

            var courses = cat.slugs.map(function (slug) { return data.getBySlug(slug); }).filter(Boolean);
            var offeringsHTML = '<span class="crs-menu-offerings-label">Course Offerings</span>';
            if (!courses.length) {
                offeringsHTML += '<p class="crs-menu-empty">Programme details coming soon.</p>';
            } else {
                offeringsHTML += '<div class="crs-offering-list">' + courses.map(function (course) {
                    var mode = (course.modes && course.modes[0]) || null;
                    var href = course.file + (mode ? ("?mode=" + encodeURIComponent(mode.id)) : "");
                    return '<a href="' + href + '" class="crs-offering-link">' + course.title + ' <i class="fa-solid fa-arrow-right"></i></a>';
                }).join("") + "</div>";
            }
            offeringsWrap.innerHTML = offeringsHTML;

            var btns = catsWrap.querySelectorAll(".crs-cat-btn");
            for (var b = 0; b < btns.length; b++) {
                btns[b].classList.toggle("is-active", btns[b].getAttribute("data-category") === catId);
            }
        }

        var catBtns = catsWrap.querySelectorAll(".crs-cat-btn");
        for (var c = 0; c < catBtns.length; c++) {
            catBtns[c].addEventListener("click", function (e) {
                renderCategory(e.currentTarget.getAttribute("data-category"));
                if (window.matchMedia("(max-width:900px)").matches && body) {
                    body.setAttribute("data-step", "cards");
                }
            });
        }
        if (backBtn && body) {
            backBtn.addEventListener("click", function () {
                body.setAttribute("data-step", "cats");
            });
        }

        renderCategory(MENU_CATEGORIES[0].id);

        /* ---------- positioning: drop directly under the AI Bootcamps
           internal nav bar (.aic-subnav), which scrolls with the page
           rather than staying fixed — so this is recalculated on open
           and the menu closes on scroll to avoid drifting away from it ---------- */
        function positionPanel() {
            var subnav = trigger.closest(".aic-subnav");
            var top = subnav ? subnav.getBoundingClientRect().bottom : 96;
            panel.style.marginTop = Math.max(top, 8) + "px";
        }

        /* ---------- open / close ---------- */
        var closeTimer = null;

        function openMenu() {
            if (closeTimer) { clearTimeout(closeTimer); closeTimer = null; }
            positionPanel();
            menu.classList.add("is-open");
            menu.setAttribute("aria-hidden", "false");
            trigger.setAttribute("aria-expanded", "true");
            if (body) body.setAttribute("data-step", "cats");
            document.body.style.overflow = "hidden";
            window.addEventListener("scroll", closeOnScroll, { passive: true });
        }
        function closeMenu() {
            menu.classList.remove("is-open");
            menu.setAttribute("aria-hidden", "true");
            trigger.setAttribute("aria-expanded", "false");
            document.body.style.overflow = "";
            window.removeEventListener("scroll", closeOnScroll);
        }
        function closeOnScroll() { closeMenu(); }
        function isOpen() { return menu.classList.contains("is-open"); }

        trigger.addEventListener("click", function (e) {
            e.preventDefault();
            isOpen() ? closeMenu() : openMenu();
        });

        var isFinePointer = window.matchMedia && window.matchMedia("(hover:hover) and (pointer:fine)").matches;
        if (isFinePointer) {
            trigger.addEventListener("mouseenter", function () {
                if (!window.matchMedia("(max-width:900px)").matches) openMenu();
            });
            menu.addEventListener("mouseleave", function () {
                closeTimer = setTimeout(closeMenu, 220);
            });
            menu.addEventListener("mouseenter", function () {
                if (closeTimer) { clearTimeout(closeTimer); closeTimer = null; }
            });
        }

        if (closeBtn) closeBtn.addEventListener("click", closeMenu);
        if (backdrop) backdrop.addEventListener("click", closeMenu);

        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && isOpen()) {
                closeMenu();
                trigger.focus();
            }
        });

        window.addEventListener("resize", function () {
            if (isOpen()) positionPanel();
        });
    }

    function buildMenuHTML() {
        var catsHTML = MENU_CATEGORIES.map(function (cat, i) {
            return (
                '<button type="button" class="crs-cat-btn' + (i === 0 ? " is-active" : "") + '" data-category="' + cat.id + '">' +
                "<span>" + cat.label + "</span>" +
                '<i class="fa-solid fa-chevron-right crs-cat-arrow"></i>' +
                "</button>"
            );
        }).join("");

        return (
            '<div class="crs-menu" id="crsMenu" aria-hidden="true">' +
            '<div class="crs-menu-backdrop" id="crsMenuBackdrop"></div>' +
            '<div class="crs-menu-panel" id="crsMenuPanel" role="dialog" aria-modal="true" aria-label="Explore Germaine programmes">' +
            '<div class="crs-menu-topbar">' +
            '<span class="crs-menu-topbar-title"><i class="fa-solid fa-layer-group"></i> Explore Programmes</span>' +
            '<button type="button" class="crs-menu-close" id="crsMenuClose" aria-label="Close courses menu"><i class="fa-solid fa-xmark"></i></button>' +
            "</div>" +
            '<div class="crs-menu-body" id="crsMenuBody" data-step="cats">' +
            '<button type="button" class="crs-menu-back" id="crsMenuBack"><i class="fa-solid fa-arrow-left"></i> Back to Categories</button>' +
            '<div class="crs-menu-cats" id="crsMenuCats">' +
            catsHTML +
            '<a href="ai-bootcamp-courses.html" class="crs-menu-viewall">View All Programmes <i class="fa-solid fa-arrow-right"></i></a>' +
            "</div>" +
            '<div class="crs-menu-desc" id="crsMenuDesc"></div>' +
            '<div class="crs-menu-offerings" id="crsMenuOfferings"></div>' +
            "</div>" +
            "</div>" +
            "</div>"
        );
    }
})();

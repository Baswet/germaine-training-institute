/*=========================================================
    GERMAINE TRAINING INSTITUTE — REUSABLE SITE NAVIGATION
    Injects the mobile slide-out navigation panel into every
    page from a single source of truth, so link items, order
    and active-page highlighting never drift between pages.
    Mirrors the desktop 3-level header (About Us, Admissions
    and Academic Schools open as accordion groups; the rest
    are single links).

    Usage: place <div id="site-nav-mount"></div> where the old
    hardcoded <nav class="side-nav"> block used to sit, and
    include this script BEFORE main.js.
=========================================================*/

(function () {

    /* Links shown in the slide-out panel.
       "match" lists filenames that should highlight this item as active.
       Items with "children" render as an accordion group instead of a
       single link. */
    const NAV_LINKS = [
        { label: "Home", href: "index.html", match: ["index.html", ""] },
        {
            label: "About Us",
            match: ["about.html"],
            children: [
                { label: "Our Story", href: "about.html" },
                { label: "Mission & Vision", href: "about.html" },
                { label: "Leadership", href: "about.html" },
                { label: "Accreditation", href: "about.html" }
            ]
        },
        {
            label: "Admissions",
            match: ["admissions.html"],
            children: [
                { label: "Apply Online", href: "admissions.html#admission-form" },
                { label: "Entry Requirements", href: "admissions.html" },
                { label: "Fees Structure", href: "admissions.html" },
                { label: "Scholarships", href: "admissions.html" }
            ]
        },
        {
            label: "Academic Schools",
            match: ["courses.html", "courses-", "course-detail.html"],
            children: [
                { label: "School of Medical & Health Sciences", href: "courses-health-sciences.html", icon: "fa-user-doctor" },
                { label: "School of Hospitality, Tourism & Travel", href: "courses-hospitality-tourism.html", icon: "fa-utensils" },
                { label: "School of Engineering", href: "courses-engineering-technology.html", icon: "fa-gears" },
                { label: "School of Computing & Informatics", href: "courses-computing-it.html", icon: "fa-laptop-code" },
                { label: "School of Cosmetology, Fashion & Design", href: "courses-cosmetology-fashion-design.html", icon: "fa-scissors" },
                { label: "Business & Social Sciences", href: "courses-business-commerce.html", icon: "fa-briefcase" },
                { label: "School of Communication & Media", href: "courses-mass-communication-journalism.html", icon: "fa-microphone" },
                { label: "School of Agriculture", href: "courses-agriculture.html", icon: "fa-seedling" },
                { label: "School of Virtual Learning", href: "courses-virtual-learning.html", icon: "fa-laptop" }
            ],
            exclude: ["courses-languages.html"]
        },
        { label: "Languages & Short Courses", href: "courses-languages.html", match: ["courses-languages.html"] },
        { label: "Student Life", href: "campus.html", match: ["campus.html"] },
        { label: "News & Events", href: "news.html", match: ["news.html"] },
        { label: "Contact Us", href: "contact.html", match: ["contact.html"] }
    ];

    /* Quick-access utility links (mirrors the Level 1 utility bar,
       which is hidden on mobile) shown at the bottom of the panel. */
    const UTILITY_LINKS = [
        { label: "Hire our Graduates", href: "graduate-hire.html", icon: "fa-user-graduate" },
        { label: "Earn Cash Fast", href: "EarnCash/frontend/pages/index.html", icon: "fa-hand-holding-dollar" },
        { label: "Corporate Training", href: "corporate-training.html", icon: "fa-building" },
        { label: "AI Bootcamps", href: "ai-bootcamp.html", icon: "fa-robot" },
        { label: "Full Scholarship", href: "admissions.html", icon: "fa-award" },
        { label: "Partner with Us", href: "partner-with-us.html", icon: "fa-handshake" },
        { label: "Students Portal", href: "#", icon: "fa-user" },
        { label: "Staff Portal", href: "#", icon: "fa-user-tie" },
        { label: "Alumni Registration", href: "alumni.html", icon: "fa-user-graduate" },
        { label: "Vacancies", href: "vacancies.html", icon: "fa-briefcase" }
    ];

    function currentFile() {
        const path = window.location.pathname;
        const file = path.substring(path.lastIndexOf("/") + 1);
        return file || "index.html";
    }

    function isActive(link, file) {
        if (!link.match) return false;
        return link.match.some(function (m) {
            return m !== "" && file.indexOf(m) === 0;
        }) || (file === "" && link.href === "index.html");
    }

    function buildLinkItem(link, file) {
        const activeClass = isActive(link, file) ? ' class="active"' : "";
        return '<li><a href="' + link.href + '"' + activeClass + '>' + link.label + '</a></li>';
    }

    function buildGroupItem(link, file, index) {

        const active = isActive(link, file);
        const panelId = "sideNavGroup" + index;

        const childrenHTML = link.children.map(function (child) {
            const iconHTML = child.icon ? '<i class="fa-solid ' + child.icon + '"></i>' : "";
            return '<a href="' + child.href + '">' + iconHTML + child.label + '</a>';
        }).join("");

        return (
            '<li class="side-nav-group">' +
                '<button type="button" class="side-nav-toggle' + (active ? ' active' : '') + '" aria-expanded="false" aria-controls="' + panelId + '">' +
                    '<span>' + link.label + '</span>' +
                    '<i class="fa-solid fa-chevron-down"></i>' +
                '</button>' +
                '<div class="side-nav-submenu" id="' + panelId + '">' +
                    childrenHTML +
                '</div>' +
            '</li>'
        );
    }

    function buildNavHTML() {

        const file = currentFile();

        const linksHTML = NAV_LINKS.map(function (link, index) {
            return link.children ? buildGroupItem(link, file, index) : buildLinkItem(link, file);
        }).join("\n            ");

        const utilityLinksHTML = UTILITY_LINKS.map(function (link) {
            return '<a href="' + link.href + '" class="side-nav-utility-btn"><i class="fa-solid ' + link.icon + '"></i>' + link.label + '</a>';
        }).join("");

        return (
            '<nav class="side-nav" id="sideNav" aria-label="Mobile navigation">' +
            '<ul class="side-nav-links">' +
                linksHTML +
            '</ul>' +
            '<div class="side-nav-utility">' +
                '<button class="search-btn side-nav-utility-btn" type="button" aria-label="Search the site">' +
                    '<i class="fas fa-search"></i> Search' +
                '</button>' +
                '<button class="theme-toggle side-nav-utility-btn" type="button" aria-label="Toggle dark mode" title="Toggle dark mode">' +
                    '<i class="fa-solid fa-sun"></i><i class="fa-solid fa-moon"></i> Dark Mode' +
                '</button>' +
            '</div>' +
            '<span class="side-nav-utility-heading">Quick Links &amp; Portals</span>' +
            '<div class="side-nav-utility">' +
                utilityLinksHTML +
            '</div>' +
            '<div class="side-nav-footer">' +
                '<a href="admissions.html" class="btn-primary">Apply Now</a>' +
                '<div class="side-nav-contact">' +
                    '<a href="tel:+254719488112"><i class="fas fa-phone"></i> +254 719 488 112</a>' +
                    '<a href="mailto:admissions@germaineinstitute.com"><i class="fas fa-envelope"></i> admissions@germaineinstitute.com</a>' +
                '</div>' +
            '</div>' +
            '</nav>'
        );
    }

    function initAccordions(mountedNav) {

        const toggles = mountedNav.querySelectorAll(".side-nav-toggle");

        toggles.forEach(function (toggle) {

            const panel = document.getElementById(toggle.getAttribute("aria-controls"));

            if (!panel) return;

            toggle.addEventListener("click", function () {

                const isOpen = toggle.getAttribute("aria-expanded") === "true";

                // Collapse any other open group for a tidy accordion feel
                toggles.forEach(function (t) {
                    if (t !== toggle) {
                        t.setAttribute("aria-expanded", "false");
                        const p = document.getElementById(t.getAttribute("aria-controls"));
                        if (p) p.style.maxHeight = null;
                    }
                });

                if (isOpen) {
                    toggle.setAttribute("aria-expanded", "false");
                    panel.style.maxHeight = null;
                } else {
                    toggle.setAttribute("aria-expanded", "true");
                    panel.style.maxHeight = panel.scrollHeight + "px";
                }

            });

        });

    }

    const mount = document.getElementById("site-nav-mount");

    if (mount) {
        mount.outerHTML = buildNavHTML();
        const nav = document.getElementById("sideNav");
        if (nav) initAccordions(nav);
    }

})();

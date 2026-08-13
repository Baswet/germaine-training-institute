/*==================================================
    GERMAINE — AI BOOTCAMP FAMILY NAVIGATION
    Drives the dedicated .aic-nav bar that replaces the main site
    header on every AI Bootcamp page (body.aic-family-page — see
    ai-courses.css). Handles: mobile hamburger toggle and current-
    page active-link highlighting. Fully independent of the
    sitewide .side-nav / #hamburgerBtn system, which is hidden
    along with the rest of the main header on these pages.
==================================================*/
(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", init);

    function init() {
        var burger = document.getElementById("aicNavBurger");
        var links = document.getElementById("aicNavLinks");

        if (burger && links) {
            burger.addEventListener("click", function () {
                var open = links.classList.toggle("is-open");
                burger.setAttribute("aria-expanded", open ? "true" : "false");
            });
        }

        var path = window.location.pathname;
        var file = path.substring(path.lastIndexOf("/") + 1) || "ai-bootcamp.html";

        var navLinks = document.querySelectorAll(".aic-nav-link[data-nav]");
        for (var i = 0; i < navLinks.length; i++) {
            var key = navLinks[i].getAttribute("data-nav");
            var isActive =
                (key === "home" && file === "ai-bootcamp.html") ||
                (key === "courses" && (file === "ai-bootcamp-courses.html" || file.indexOf("ai-course-") === 0));
            if (isActive) navLinks[i].classList.add("is-active");
        }
    }
})();

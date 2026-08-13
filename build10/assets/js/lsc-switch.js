/*==================================================
    GERMAINE — LANGUAGES / SHORT COURSES TOP SELECTOR

    Drives the two card-style options that sit below the hero on
    courses-languages.html. Selecting one reveals that panel and
    hides the other, with a short animated cross-fade — no page
    reload and no re-rendering of either panel's contents (both
    are painted once on load by their own scripts, so switching
    is instant and keeps any search term or category the visitor
    had already chosen).

    Accessibility: the two buttons are a tablist, aria-selected
    tracks the active option, and each panel is a tabpanel that
    is genuinely hidden (not just visually) when inactive.
==================================================*/
(function () {
    "use strict";

    var switcher = document.getElementById("lscSwitch");
    if (!switcher) return;

    var cards = Array.prototype.slice.call(switcher.querySelectorAll(".lsc-switch-card"));
    var panels = {
        "languages": document.getElementById("panelLanguages"),
        "short-courses": document.getElementById("panelShortCourses")
    };
    if (!panels.languages || !panels["short-courses"]) return;

    var reduceMotion = window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function activate(name, focusPanel) {
        Object.keys(panels).forEach(function (key) {
            var panel = panels[key];
            var on = key === name;

            if (on) {
                panel.hidden = false;
                panel.classList.add("is-active");
                if (!reduceMotion) {
                    /* restart the entrance animation on every switch */
                    panel.classList.remove("lsc-anim");
                    void panel.offsetWidth;
                    panel.classList.add("lsc-anim");
                }
            } else {
                panel.classList.remove("is-active", "lsc-anim");
                panel.hidden = true;
            }
        });

        cards.forEach(function (c) {
            var on = c.getAttribute("data-panel") === name;
            c.classList.toggle("active", on);
            c.setAttribute("aria-selected", on ? "true" : "false");
        });

        /* reveal any elements inside the freshly shown panel that were
           still waiting on the scroll-reveal observer */
        panels[name].querySelectorAll(".sp-reveal:not(.sp-show)").forEach(function (el) {
            el.classList.add("sp-show");
        });

        if (focusPanel) {
            var top = switcher.getBoundingClientRect().top + window.pageYOffset - 150;
            window.scrollTo({ top: top, behavior: reduceMotion ? "auto" : "smooth" });
        }
    }

    cards.forEach(function (card) {
        card.addEventListener("click", function () {
            activate(card.getAttribute("data-panel"), true);
        });

        /* left/right arrow keys move between the two options */
        card.addEventListener("keydown", function (e) {
            if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
            e.preventDefault();
            var i = cards.indexOf(card);
            var next = cards[(i + (e.key === "ArrowRight" ? 1 : cards.length - 1)) % cards.length];
            next.focus();
            activate(next.getAttribute("data-panel"), false);
        });
    });

    /* deep link: courses-languages.html#short-courses opens that panel */
    var hash = (window.location.hash || "").replace("#", "");
    if (hash === "short-courses" || hash === "shortcourses") {
        activate("short-courses", false);
    } else {
        activate("languages", false);
    }
})();

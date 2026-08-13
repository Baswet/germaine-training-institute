/*==================================================
    GERMAINE — AI BOOTCAMP COURSES PORTAL
    Category pill filtering for the Featured Programmes grid
    on ai-bootcamp-courses.html. Clicking a pill shows only
    programmes in that category ("All Programmes" shows all).
==================================================*/
(function () {
    "use strict";

    var pills = document.querySelectorAll(".aic-pill");
    var cards = document.querySelectorAll(".aic-card[data-category]");
    var emptyState = document.getElementById("aicEmptyState");
    if (!pills.length || !cards.length) return;

    function filterBy(category) {
        var visibleCount = 0;
        cards.forEach(function (card) {
            var match = category === "all" || card.dataset.category === category;
            card.classList.toggle("is-filtered-out", !match);
            if (match) visibleCount++;
        });
        if (emptyState) {
            emptyState.classList.toggle("is-visible", visibleCount === 0);
        }
    }

    pills.forEach(function (pill) {
        pill.addEventListener("click", function (e) {
            e.preventDefault();
            pills.forEach(function (p) { p.classList.remove("is-active"); });
            pill.classList.add("is-active");
            filterBy(pill.dataset.category || "all");
        });
    });

    // Initial state: honour whichever pill is marked is-active in the HTML.
    var initialPill = document.querySelector(".aic-pill.is-active") || pills[0];
    filterBy(initialPill ? (initialPill.dataset.category || "all") : "all");
})();

/*==================================================
    FEATURED PROGRAMMES — image flip cards
    Desktop (has hover) flips via CSS :hover / :focus-within, so
    tabbing to a card (or into its "Explore Programme" link) already
    reveals the back — no extra handler needed there. Touch screens
    have no hover state, so a tap toggles .is-flipped; Enter/Space is
    also wired explicitly so the role="button" card is fully keyboard
    operable per the flip-card accessibility spec.
==================================================*/
(function () {
    "use strict";

    var cards = document.querySelectorAll(".aic-flip-card");
    if (!cards.length) return;

    var noHover = window.matchMedia && window.matchMedia("(hover: none)").matches;

    function toggle(card) {
        var flipped = card.classList.toggle("is-flipped");
        card.setAttribute("aria-pressed", flipped ? "true" : "false");
    }

    cards.forEach(function (card) {
        if (noHover) {
            card.addEventListener("click", function (e) {
                // let the "Explore Programme" link navigate normally
                if (e.target.closest(".aic-flip-cta")) return;
                toggle(card);
            });
        }
        card.addEventListener("keydown", function (e) {
            if (e.target !== card) return; // ignore keys bubbling up from the CTA link
            if (e.key === "Enter" || e.key === " " || e.key === "Spacebar") {
                e.preventDefault();
                toggle(card);
            }
        });
    });
})();

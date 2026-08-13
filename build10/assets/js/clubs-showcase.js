/*==================================================
    GERMAINE — CLUBS & SOCIETIES SLIDING SHOWCASE
    Student Life page only. Single-card slideshow: one club
    visible at a time, continuous right-to-left flow (transform/
    opacity only, GPU-composited). Autoplay pauses on hover/focus,
    resumes after. Dot navigation jumps directly to a club.
    No-ops if mount points are absent.
==================================================*/
(function () {
    "use strict";

    var stage = document.getElementById("clbStage");
    var card = document.getElementById("clbCard");
    var dotsWrap = document.getElementById("clbDots");
    if (!stage || !card || !dotsWrap) return;

    var slides = Array.prototype.slice.call(card.querySelectorAll(".clb-slide"));
    if (!slides.length) return;

    var DISPLAY_MS = 3000;
    var TRANSITION_MS = 700;
    var CYCLE_MS = DISPLAY_MS + TRANSITION_MS;

    var current = 0;
    var timer = null;

    /* ---------- build dot navigation ---------- */
    slides.forEach(function (slide, i) {
        var title = slide.querySelector("h3");
        var dot = document.createElement("button");
        dot.type = "button";
        dot.className = "clb-dot" + (i === 0 ? " is-active" : "");
        dot.setAttribute("role", "tab");
        dot.setAttribute("aria-label", "Show " + (title ? title.textContent : "club " + (i + 1)));
        dot.addEventListener("click", function () {
            goTo(i);
            restart();
        });
        dotsWrap.appendChild(dot);
    });
    var dots = Array.prototype.slice.call(dotsWrap.querySelectorAll(".clb-dot"));

    function applyState(next) {
        slides.forEach(function (slide, i) {
            slide.classList.remove("is-exit");
            if (i === next) {
                slide.classList.add("is-active");
            } else if (i === current) {
                slide.classList.remove("is-active");
                slide.classList.add("is-exit");
            } else {
                slide.classList.remove("is-active");
            }
        });
        dots.forEach(function (dot, i) {
            dot.classList.toggle("is-active", i === next);
        });
    }

    function goTo(next) {
        if (next === current) return;
        applyState(next);
        current = next;
    }

    function advance() {
        goTo((current + 1) % slides.length);
    }

    function start() {
        stop();
        timer = window.setInterval(advance, CYCLE_MS);
    }
    function stop() {
        if (timer) {
            window.clearInterval(timer);
            timer = null;
        }
    }
    function restart() {
        start();
    }

    /* ---------- init ---------- */
    applyState(0);
    start();

    card.addEventListener("mouseenter", stop);
    card.addEventListener("mouseleave", start);
    card.addEventListener("focusin", stop);
    card.addEventListener("focusout", start);
})();

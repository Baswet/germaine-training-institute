/*==================================================
    GERMAINE — CORPORATE TRAINING PAGE SCRIPT
    Self-contained: hero slideshow + scroll reveal for
    this page's sections. Does not touch main.js.
==================================================*/
(function () {
    "use strict";

    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------- HERO PARALLAX (static anchor image) ---------- */
    var heroEl = document.getElementById("ct-hero");
    var staticImg = document.querySelector(".ct-hero-static");
    if (heroEl && staticImg && !reduceMotion) {
        var ticking = false, mx = 0, my = 0;
        heroEl.addEventListener("mousemove", function (e) {
            var r = heroEl.getBoundingClientRect();
            mx = ((e.clientX - r.left) / r.width - 0.5) * 2;
            my = ((e.clientY - r.top) / r.height - 0.5) * 2;
            if (!ticking) {
                requestAnimationFrame(function () {
                    staticImg.style.setProperty("--ct-pan", (mx * -10) + "px " + (my * -8) + "px");
                    ticking = false;
                });
                ticking = true;
            }
        });
    }

    /* ---------- SCROLL REVEAL for .ct-reveal elements ---------- */
    var revealEls = document.querySelectorAll(".ct-reveal");
    if (revealEls.length) {
        if (reduceMotion) {
            revealEls.forEach(function (el) { el.classList.add("ct-show"); });
        } else {
            var io = new IntersectionObserver(
                function (entries) {
                    entries.forEach(function (entry) {
                        if (entry.isIntersecting) {
                            entry.target.classList.add("ct-show");
                            io.unobserve(entry.target);
                        }
                    });
                },
                { threshold: 0.15 }
            );
            revealEls.forEach(function (el) { io.observe(el); });
        }
    }
})();

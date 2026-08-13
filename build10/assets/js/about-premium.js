/*==================================================
    GERMAINE — ABOUT US PAGE SCRIPT
    Self-contained, guarded so it is safe even if some
    elements are absent. Drives: the Who We Are fade
    slideshow and scroll-reveal for .ab-reveal.
==================================================*/
(function () {
    "use strict";

    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------- WHO WE ARE — responsive fade slideshow ----------
       Cycles the student/practical photos inside the existing image frame
       every 4s; the TVET Accredited badge stays pinned above it. Pauses
       automatically while the pointer hovers the slideshow. */
    var whoFlip = document.getElementById("abWhoFlip");
    if (whoFlip) {
        var whoSlides = whoFlip.querySelectorAll(".ab-who-slide");
        if (whoSlides.length > 1 && !reduceMotion) {
            var whoIndex = 0;
            var whoTimer = null;

            function whoAdvance() {
                whoIndex = (whoIndex + 1) % whoSlides.length;
                whoSlides.forEach(function (el, idx) {
                    el.classList.toggle("is-active", idx === whoIndex);
                });
            }

            function whoStart() {
                if (whoTimer) return;
                whoTimer = setInterval(whoAdvance, 3200);
            }

            function whoStop() {
                clearInterval(whoTimer);
                whoTimer = null;
            }

            whoStart();
            whoFlip.addEventListener("mouseenter", whoStop);
            whoFlip.addEventListener("mouseleave", whoStart);
            whoFlip.addEventListener("focusin", whoStop);
            whoFlip.addEventListener("focusout", whoStart);
        }
    }

    /* ---------- VISION / MISSION / CORE VALUES — flip cards ----------
       Desktop (has hover) flips purely via CSS :hover / :focus-visible —
       tabbing to a card with a keyboard already reveals its back, so no
       extra keyboard handler is needed there. Touch screens have no
       hover state, so a tap toggles .is-flipped instead; aria-pressed
       stays in sync for assistive tech either way. */
    var noHover = window.matchMedia && window.matchMedia("(hover: none)").matches;
    if (noHover) {
        document.querySelectorAll(".ab-flip-card").forEach(function (card) {
            card.addEventListener("click", function () {
                var flipped = card.classList.toggle("is-flipped");
                card.setAttribute("aria-pressed", flipped ? "true" : "false");
            });
        });
    }

    /* ---------- SCROLL REVEAL ---------- */
    var revealEls = document.querySelectorAll(".ab-reveal");
    if (revealEls.length) {
        if (reduceMotion || typeof IntersectionObserver === "undefined") {
            revealEls.forEach(function (el) { el.classList.add("ab-show"); });
        } else {
            var io = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("ab-show");
                        io.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.12 });
            revealEls.forEach(function (el) { io.observe(el); });
        }
    }
})();

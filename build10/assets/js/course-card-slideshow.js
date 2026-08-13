/* ==================================================
   BOOTCAMP COURSE CARD — TWO-IMAGE AUTO SLIDESHOW
   Runs only on ai-bootcamp-courses.html. Each .aic-card-media
   contains exactly two <img class="aic-card-img"> elements
   (image 1 + image 2). Image 1 is visible on load; every
   ~3.5s the active image alternates via a CSS opacity
   crossfade (see assets/css/ai-courses.css). Purely additive —
   does not touch card markup/content, Apply Now links, or
   any existing card interactions.
   ================================================== */
(function () {
    "use strict";

    function initSlideshow(media) {
        var imgs = media.querySelectorAll(".aic-card-img");
        if (imgs.length < 2) return; // nothing to alternate

        var dots = media.querySelectorAll(".aic-card-dots span");
        var activeIndex = 0;
        var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

        if (reduceMotion) return; // keep the first image static, no timers

        setInterval(function () {
            var nextIndex = activeIndex === 0 ? 1 : 0;

            imgs[activeIndex].classList.remove("is-active");
            imgs[nextIndex].classList.add("is-active");

            if (dots.length) {
                dots[activeIndex].classList.remove("is-active");
                dots[nextIndex].classList.add("is-active");
            }

            activeIndex = nextIndex;
        }, 3800);
    }

    function init() {
        var mediaBoxes = document.querySelectorAll(".aic-card-media");
        mediaBoxes.forEach(initSlideshow);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();

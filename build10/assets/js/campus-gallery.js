/*==================================================
    GERMAINE — "LIFE AT GERMAINE" CAMPUS GALLERY
    Drives the .sl-gallery slideshow on campus.html:
    auto-advance, prev/next buttons and dot navigation.
    Self-contained and guarded so it's safe if the
    gallery markup is absent on a given page.
==================================================*/
(function () {
    "use strict";

    var gallery = document.querySelector(".sl-gallery");
    if (!gallery) return;

    var slides = gallery.querySelectorAll(".sl-slide");
    var dots = gallery.querySelectorAll(".sl-dot");
    var prevBtn = gallery.querySelector(".sl-prev");
    var nextBtn = gallery.querySelector(".sl-next");

    if (slides.length < 2) return;

    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var index = 0;
    var timer = null;
    /* Faster, livelier pace than a typical hero slideshow. */
    var INTERVAL = 3500;

    function show(newIndex) {
        index = (newIndex + slides.length) % slides.length;
        slides.forEach(function (el, i) {
            el.classList.toggle("on", i === index);
        });
        dots.forEach(function (el, i) {
            el.classList.toggle("on", i === index);
        });
    }

    function next() { show(index + 1); }
    function prev() { show(index - 1); }

    function start() {
        if (timer || reduceMotion) return;
        timer = setInterval(next, INTERVAL);
    }
    function stop() {
        clearInterval(timer);
        timer = null;
    }

    if (prevBtn) prevBtn.addEventListener("click", function () { prev(); stop(); start(); });
    if (nextBtn) nextBtn.addEventListener("click", function () { next(); stop(); start(); });
    dots.forEach(function (dot, i) {
        dot.addEventListener("click", function () { show(i); stop(); start(); });
    });

    gallery.addEventListener("mouseenter", stop);
    gallery.addEventListener("mouseleave", start);
    gallery.addEventListener("focusin", stop);
    gallery.addEventListener("focusout", start);

    show(0);
    start();
})();

/*=========================================================
    GERMAINE TRAINING INSTITUTE — FULL SCHOLARSHIP LANDING
    Scroll reveal, animated stat counters, Ken Burns
    slideshow, FAQ accordion, cursor glow.
    Scoped to body.scholarship-page.
=========================================================*/
(function () {
    var root = document.querySelector(".scholarship-page");
    if (!root) return;

    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------- cursor glow ---------- */
    var glow = document.getElementById("scCursorGlow");
    if (glow && !reduce && window.matchMedia && window.matchMedia("(hover:hover)").matches) {
        var raf = null, gx = 0, gy = 0;
        document.addEventListener("mousemove", function (e) {
            gx = e.clientX; gy = e.clientY;
            glow.classList.add("active");
            if (!raf) {
                raf = requestAnimationFrame(function () {
                    glow.style.transform = "translate(calc(" + gx + "px - 50%), calc(" + gy + "px - 50%))";
                    raf = null;
                });
            }
        });
        document.addEventListener("mouseleave", function () { glow.classList.remove("active"); });
    }

    /* ---------- scroll reveal ---------- */
    var reveals = document.querySelectorAll(".sc-reveal");
    if (reveals.length) {
        if (reduce) {
            reveals.forEach(function (el) { el.classList.add("in"); });
        } else {
            var ro = new IntersectionObserver(function (entries) {
                entries.forEach(function (e) {
                    if (e.isIntersecting) { e.target.classList.add("in"); ro.unobserve(e.target); }
                });
            }, { threshold: 0.15 });
            reveals.forEach(function (el) { ro.observe(el); });
        }
    }

    /* ---------- animated stat counters ---------- */
    var nums = document.querySelectorAll(".sc-stat [data-count]");
    if (nums.length) {
        var co = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (!e.isIntersecting) return;
                var el = e.target;
                var target = parseInt(el.getAttribute("data-count"), 10) || 0;
                var suffix = el.getAttribute("data-suffix") || "";
                co.unobserve(el);
                if (reduce) { el.textContent = target.toLocaleString() + suffix; return; }
                var dur = 1600, start = null;
                function tick(ts) {
                    if (!start) start = ts;
                    var p = Math.min((ts - start) / dur, 1);
                    var eased = 1 - Math.pow(1 - p, 3);
                    el.textContent = Math.round(target * eased).toLocaleString() + suffix;
                    if (p < 1) requestAnimationFrame(tick);
                    else el.textContent = target.toLocaleString() + suffix;
                }
                requestAnimationFrame(tick);
            });
        }, { threshold: 0.5 });
        nums.forEach(function (el) { co.observe(el); });
    }

    /* ---------- slideshow (Student Experience) ---------- */
    var slides = document.querySelectorAll(".sc-slide");
    var slideDots = document.querySelectorAll(".sc-slide-dot");
    var slidePrev = document.getElementById("scSlidePrev");
    var slideNext = document.getElementById("scSlideNext");
    if (slides.length) {
        var sIndex = 0, sTimer = null;
        function showSlideAt(i) {
            sIndex = (i + slides.length) % slides.length;
            slides.forEach(function (s, idx) {
                s.classList.toggle("active", idx === sIndex);
                var img = s.querySelector("img");
                if (idx === sIndex && img) { img.style.animation = "none"; void img.offsetWidth; img.style.animation = ""; }
            });
            slideDots.forEach(function (d, idx) { d.classList.toggle("active", idx === sIndex); });
        }
        function nextSlide() { showSlideAt(sIndex + 1); }
        function startAuto() { stopAuto(); if (!reduce) sTimer = setInterval(nextSlide, 4000); }
        function stopAuto() { if (sTimer) clearInterval(sTimer); }
        slideDots.forEach(function (d, idx) { d.addEventListener("click", function () { showSlideAt(idx); startAuto(); }); });
        if (slideNext) slideNext.addEventListener("click", function () { nextSlide(); startAuto(); });
        if (slidePrev) slidePrev.addEventListener("click", function () { showSlideAt(sIndex - 1); startAuto(); });
        var slideshowEl = document.querySelector(".sc-slideshow");
        if (slideshowEl) {
            slideshowEl.addEventListener("mouseenter", stopAuto);
            slideshowEl.addEventListener("mouseleave", startAuto);
        }
        showSlideAt(0);
        startAuto();
    }

    /* ---------- FAQ accordion ---------- */
    var faqItems = document.querySelectorAll(".sc-faq-item");
    faqItems.forEach(function (item) {
        var q = item.querySelector(".sc-faq-q");
        var a = item.querySelector(".sc-faq-a");
        if (!q || !a) return;
        q.addEventListener("click", function () {
            var isOpen = item.classList.contains("open");
            faqItems.forEach(function (it) {
                it.classList.remove("open");
                var ans = it.querySelector(".sc-faq-a");
                if (ans) ans.style.maxHeight = null;
            });
            if (!isOpen) {
                item.classList.add("open");
                a.style.maxHeight = a.scrollHeight + "px";
            }
        });
    });

})();

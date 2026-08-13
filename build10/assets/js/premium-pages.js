/*=========================================================
    GERMAINE TRAINING INSTITUTE
    Shared engine for the Student Life (.sl-*) and
    Contact (.cu-*) premium pages.
    Scroll reveal · cursor glow · counters · slideshow ·
    ripple buttons · glass accordion.
=========================================================*/
(function () {
    "use strict";

    var isSL = document.body.classList.contains("student-life-page");
    var isCU = document.body.classList.contains("contact-page");
    if (!isSL && !isCU) return;

    var reduce = window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    var P = isSL ? "sl" : "cu";           // class prefix
    var ON = isSL ? "in" : "in";          // reveal state class

    function $(s, c) { return (c || document).querySelector(s); }
    function $all(s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); }

    /* ---------- cursor glow ---------- */
    var glow = $("." + P + "-cursor");
    if (glow && !reduce && window.matchMedia && window.matchMedia("(hover:hover)").matches) {
        var raf = null, gx = 0, gy = 0;
        document.addEventListener("mousemove", function (e) {
            gx = e.clientX; gy = e.clientY;
            glow.classList.add("on");
            if (!raf) {
                raf = requestAnimationFrame(function () {
                    glow.style.transform = "translate(calc(" + gx + "px - 50%), calc(" + gy + "px - 50%))";
                    raf = null;
                });
            }
        });
        document.addEventListener("mouseleave", function () { glow.classList.remove("on"); });
    }

    /* ---------- scroll reveal ---------- */
    var reveals = $all("." + P + "-reveal");
    if (reveals.length) {
        if (reduce) {
            reveals.forEach(function (el) { el.classList.add(ON); });
        } else {
            var ro = new IntersectionObserver(function (entries) {
                entries.forEach(function (e) {
                    if (e.isIntersecting) { e.target.classList.add(ON); ro.unobserve(e.target); }
                });
            }, { threshold: 0.14 });
            reveals.forEach(function (el) { ro.observe(el); });
        }
    }

    /* ---------- animated counters ---------- */
    var nums = $all("[data-count]");
    if (nums.length) {
        var co = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (!e.isIntersecting) return;
                var el = e.target;
                var target = parseInt(el.getAttribute("data-count"), 10) || 0;
                var suffix = el.getAttribute("data-suffix") || "";
                co.unobserve(el);
                if (reduce) { el.textContent = target.toLocaleString() + suffix; return; }
                var dur = 1700, start = null;
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

    /* ---------- gallery slideshow ---------- */
    var slides = $all("." + P + "-slide");
    if (slides.length) {
        var dots = $all("." + P + "-dot");
        var prevBtn = $("." + P + "-prev");
        var nextBtn = $("." + P + "-next");
        var idx = 0, timer = null;

        function show(i) {
            idx = (i + slides.length) % slides.length;
            slides.forEach(function (s, n) {
                s.classList.toggle("on", n === idx);
                var img = s.querySelector("img");
                if (n === idx && img && !reduce) {
                    img.style.animation = "none";
                    void img.offsetWidth;
                    img.style.animation = "";
                }
            });
            dots.forEach(function (d, n) { d.classList.toggle("on", n === idx); });
        }
        function next() { show(idx + 1); }
        function start() { stop(); if (!reduce) timer = setInterval(next, 4000); }
        function stop() { if (timer) clearInterval(timer); }

        dots.forEach(function (d, n) { d.addEventListener("click", function () { show(n); start(); }); });
        if (nextBtn) nextBtn.addEventListener("click", function () { next(); start(); });
        if (prevBtn) prevBtn.addEventListener("click", function () { show(idx - 1); start(); });

        var frame = $("." + P + "-gallery");
        if (frame) {
            frame.addEventListener("mouseenter", stop);
            frame.addEventListener("mouseleave", start);
        }
        show(0);
        start();
    }

    /* ---------- ripple buttons ---------- */
    $all("." + P + "-btn").forEach(function (btn) {
        btn.addEventListener("click", function (e) {
            var rect = btn.getBoundingClientRect();
            var size = Math.max(rect.width, rect.height) * 1.2;
            var r = document.createElement("span");
            r.className = P + "-ripple";
            r.style.width = r.style.height = size + "px";
            r.style.left = (e.clientX - rect.left - size / 2) + "px";
            r.style.top = (e.clientY - rect.top - size / 2) + "px";
            btn.appendChild(r);
            r.addEventListener("animationend", function () { r.remove(); });
        });
    });

    /* ---------- glass accordion (contact page) ---------- */
    var accItems = $all("." + P + "-acc-item");
    accItems.forEach(function (item) {
        var q = item.querySelector("." + P + "-acc-q");
        var a = item.querySelector("." + P + "-acc-a");
        if (!q || !a) return;
        q.addEventListener("click", function () {
            var open = item.classList.contains("open");
            accItems.forEach(function (it) {
                it.classList.remove("open");
                var ans = it.querySelector("." + P + "-acc-a");
                if (ans) ans.style.maxHeight = null;
            });
            if (!open) {
                item.classList.add("open");
                a.style.maxHeight = a.scrollHeight + "px";
            }
        });
    });

})();

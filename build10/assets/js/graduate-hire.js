/*=========================================================
    GERMAINE TRAINING INSTITUTE — HIRE OUR GRADUATES
    Scoped: scroll reveal, count-up statistics, FAQ accordion.
    Runs only if the page contains a .ghire root.
=========================================================*/
(function () {
    var root = document.querySelector(".ghire");
    if (!root) return;

    var reduce = window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------- cursor glow ---------- */
    var glow = document.getElementById("ghCursorGlow");
    if (glow && !reduce && window.matchMedia && window.matchMedia("(hover:hover)").matches) {
        var raf = null, gx = 0, gy = 0;
        root.addEventListener("mousemove", function (e) {
            gx = e.clientX; gy = e.clientY;
            glow.classList.add("active");
            if (!raf) {
                raf = requestAnimationFrame(function () {
                    glow.style.transform = "translate(calc(" + gx + "px - 50%), calc(" + gy + "px - 50%))";
                    raf = null;
                });
            }
        });
        root.addEventListener("mouseleave", function () { glow.classList.remove("active"); });
    }

    /* ---------- nav cursor glow ---------- */
    var navGlow = document.getElementById("navCursorGlow");
    var navStack = document.getElementById("fixedTopStack");
    if (navGlow && navStack && !reduce && window.matchMedia && window.matchMedia("(hover:hover)").matches) {
        navStack.addEventListener("mousemove", function (e) {
            var rect = navStack.getBoundingClientRect();
            navGlow.style.left = (e.clientX - rect.left) + "px";
            navGlow.style.top = (e.clientY - rect.top) + "px";
        });
    }

    /* ---------- click ripple on buttons ---------- */
    var btns = root.querySelectorAll(".gh-btn");
    btns.forEach(function (btn) {
        btn.addEventListener("click", function (e) {
            var rect = btn.getBoundingClientRect();
            var size = Math.max(rect.width, rect.height) * 1.2;
            var ripple = document.createElement("span");
            ripple.className = "gh-ripple";
            ripple.style.width = ripple.style.height = size + "px";
            ripple.style.left = (e.clientX - rect.left - size / 2) + "px";
            ripple.style.top = (e.clientY - rect.top - size / 2) + "px";
            btn.appendChild(ripple);
            ripple.addEventListener("animationend", function () { ripple.remove(); });
        });
    });

    /* ---------- scroll reveal ---------- */
    var reveals = root.querySelectorAll(".gh-reveal");
    if (reveals.length) {
        if (reduce) {
            reveals.forEach(function (el) { el.classList.add("in"); });
        } else {
            var ro = new IntersectionObserver(function (entries) {
                entries.forEach(function (e) {
                    if (e.isIntersecting) {
                        e.target.classList.add("in");
                        ro.unobserve(e.target);
                    }
                });
            }, { threshold: 0.15 });
            reveals.forEach(function (el) { ro.observe(el); });
        }
    }

    /* ---------- count-up statistics ---------- */
    var nums = root.querySelectorAll("[data-count]");
    if (nums.length) {
        var co = new IntersectionObserver(function (entries) {
            entries.forEach(function (e) {
                if (!e.isIntersecting) return;
                var el = e.target;
                var target = parseFloat(el.getAttribute("data-count")) || 0;
                var suffix = el.getAttribute("data-suffix") || "";
                var dur = 1600, start = null;
                if (reduce) { el.textContent = target.toLocaleString() + suffix; co.unobserve(el); return; }
                function tick(ts) {
                    if (!start) start = ts;
                    var p = Math.min((ts - start) / dur, 1);
                    var eased = 1 - Math.pow(1 - p, 3);
                    el.textContent = Math.round(target * eased).toLocaleString() + suffix;
                    if (p < 1) requestAnimationFrame(tick);
                    else el.textContent = target.toLocaleString() + suffix;
                }
                requestAnimationFrame(tick);
                co.unobserve(el);
            });
        }, { threshold: 0.5 });
        nums.forEach(function (el) { co.observe(el); });
    }

    /* ---------- FAQ accordion ---------- */
    var items = root.querySelectorAll(".gh-faq-item");
    items.forEach(function (item) {
        var q = item.querySelector(".gh-faq-q");
        var a = item.querySelector(".gh-faq-a");
        if (!q || !a) return;
        q.setAttribute("aria-expanded", "false");
        q.addEventListener("click", function () {
            var open = item.classList.contains("open");
            items.forEach(function (it) {
                it.classList.remove("open");
                var ans = it.querySelector(".gh-faq-a");
                var btn = it.querySelector(".gh-faq-q");
                if (ans) ans.style.maxHeight = null;
                if (btn) btn.setAttribute("aria-expanded", "false");
            });
            if (!open) {
                item.classList.add("open");
                a.style.maxHeight = a.scrollHeight + "px";
                q.setAttribute("aria-expanded", "true");
            }
        });
    });
})();

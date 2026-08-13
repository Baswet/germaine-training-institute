/*==================================================
    GERMAINE — EXPLORE VACANCIES PAGE
    Smart search filter (department / location / type)
    + animated stat counters.
==================================================*/
(function () {
    "use strict";

    /* ---------- Filter ---------- */
    var deptSel = document.getElementById("vacDept");
    var locSel = document.getElementById("vacLocation");
    var typeSel = document.getElementById("vacType");
    var searchInput = document.getElementById("vacSearchInput");
    var findBtn = document.getElementById("vacFindBtn");
    var cards = Array.prototype.slice.call(document.querySelectorAll(".vac-card"));
    var emptyState = document.getElementById("vacEmpty");

    function applyFilter() {
        var dept = deptSel ? deptSel.value : "";
        var loc = locSel ? locSel.value : "";
        var type = typeSel ? typeSel.value : "";
        var q = searchInput ? searchInput.value.trim().toLowerCase() : "";
        var visibleCount = 0;

        cards.forEach(function (card) {
            var matchesDept = !dept || card.dataset.dept === dept;
            var matchesLoc = !loc || card.dataset.location === loc;
            var matchesType = !type || card.dataset.type === type;
            var matchesQuery = !q || card.dataset.title.toLowerCase().indexOf(q) !== -1;
            var visible = matchesDept && matchesLoc && matchesType && matchesQuery;
            card.classList.toggle("is-hidden", !visible);
            if (visible) visibleCount++;
        });

        if (emptyState) emptyState.classList.toggle("is-visible", visibleCount === 0);
    }

    if (findBtn) findBtn.addEventListener("click", applyFilter);
    [deptSel, locSel, typeSel].forEach(function (el) {
        if (el) el.addEventListener("change", applyFilter);
    });
    if (searchInput) {
        searchInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                applyFilter();
            }
        });
    }

    /* ---------- Animated stat counters ---------- */
    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var statEls = document.querySelectorAll(".vac-stat h3[data-count]");

    function animateCount(el) {
        var target = parseFloat(el.dataset.count);
        var suffix = el.dataset.suffix || "";
        if (reduceMotion || !target) {
            el.textContent = target + suffix;
            return;
        }
        var start = 0;
        var duration = 1400;
        var startTime = null;

        function step(ts) {
            if (!startTime) startTime = ts;
            var progress = Math.min((ts - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var value = Math.floor(start + (target - start) * eased);
            el.textContent = value + suffix;
            if (progress < 1) requestAnimationFrame(step);
            else el.textContent = target + suffix;
        }
        requestAnimationFrame(step);
    }

    if (statEls.length && "IntersectionObserver" in window) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    animateCount(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.4 });
        statEls.forEach(function (el) { observer.observe(el); });
    } else {
        statEls.forEach(animateCount);
    }
})();

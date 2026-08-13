/* ==========================================================
   GRADUATE QUALITIES — gentle auto-cycling highlight
   Hire Our Graduates page only. No-ops if mount point absent.
========================================================== */
(function () {
    "use strict";

    var GRID = document.getElementById("gqGrid");
    if (!GRID) return;

    var reduceMotion = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    var cards = Array.prototype.slice.call(GRID.querySelectorAll(".gq-card"));
    if (!cards.length || reduceMotion) return;

    var idx = 0;
    var timer = null;

    function highlight(i) {
        cards.forEach(function (c) { c.classList.remove("gq-active"); });
        cards[i].classList.add("gq-active");
    }

    function start() {
        timer = setInterval(function () {
            idx = (idx + 1) % cards.length;
            highlight(idx);
        }, 2600);
    }
    function stop() {
        clearInterval(timer);
        cards.forEach(function (c) { c.classList.remove("gq-active"); });
    }

    highlight(idx);
    start();

    GRID.addEventListener("mouseenter", stop);
    GRID.addEventListener("mouseleave", function () { idx = -1; start(); });
})();

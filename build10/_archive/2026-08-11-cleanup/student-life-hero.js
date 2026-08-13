/*==================================================
    GERMAINE — STUDENT LIFE HERO
    Generates the ambient particle field for the hero
    network background. Motion itself is pure CSS
    (transform/opacity only); this script only seeds the
    particles with randomised positions, sizes and timings
    so the field never looks mechanical. No-ops if the
    mount point is absent or reduced motion is requested.
==================================================*/
(function () {
    "use strict";

    var mount = document.getElementById("slhParticles");
    if (!mount) return;

    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    var COUNT = window.innerWidth < 720 ? 16 : 34;
    var frag = document.createDocumentFragment();

    for (var i = 0; i < COUNT; i++) {
        var dot = document.createElement("span");
        var size = (Math.random() * 2.4 + 1.2).toFixed(2);
        dot.style.width = size + "px";
        dot.style.height = size + "px";
        dot.style.left = (Math.random() * 100).toFixed(2) + "%";
        dot.style.top = (Math.random() * 100).toFixed(2) + "%";
        dot.style.animationDuration = (Math.random() * 18 + 16).toFixed(1) + "s";
        dot.style.animationDelay = "-" + (Math.random() * 20).toFixed(1) + "s";
        if (Math.random() > 0.55) dot.style.background = "#EC4899";
        frag.appendChild(dot);
    }

    mount.appendChild(frag);
})();

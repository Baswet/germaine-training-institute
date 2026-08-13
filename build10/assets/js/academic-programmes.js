/*=========================================================
    GERMAINE — ACADEMIC PROGRAMMES
    Mouse parallax on the decorative background layers.
    Scoped to the .afp section; uses the `translate`
    property so it composes with CSS animations.
=========================================================*/
(function () {
    var afp = document.querySelector(".afp");
    if (!afp) return;
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    var aurora  = afp.querySelector(".afp-aurora");
    var circuit = afp.querySelector(".afp-circuit");
    var reflect = afp.querySelector(".afp-reflect");
    var ticking = false, mx = 0, my = 0;

    afp.addEventListener("mousemove", function (e) {
        var r = afp.getBoundingClientRect();
        mx = ((e.clientX - r.left) / r.width - 0.5) * 2;
        my = ((e.clientY - r.top) / r.height - 0.5) * 2;
        if (!ticking) { requestAnimationFrame(apply); ticking = true; }
    });

    afp.addEventListener("mouseleave", function () {
        mx = 0; my = 0;
        requestAnimationFrame(apply);
    });

    function apply() {
        if (aurora)  aurora.style.translate  = (mx * 16) + "px " + (my * 12) + "px";
        if (circuit) circuit.style.translate = (mx * -22) + "px " + (my * -16) + "px";
        if (reflect) reflect.style.translate = (mx * 10) + "px 0";
        ticking = false;
    }
})();

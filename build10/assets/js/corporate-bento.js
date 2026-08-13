/*==================================================
    GERMAINE — "TRAINING IN ACTION" BENTO SLIDESHOW
    Corporate Training page only. Three cross-fading photo
    tracks (one large + two side cards) built from existing
    site imagery. Main card has arrows + dots; all three
    panels pause on hover. No-ops if mount points are absent.
==================================================*/
(function () {
    "use strict";

    var section = document.getElementById("ctBentoSection");
    var bento = document.getElementById("ctBento");
    if (!section || !bento) return;

    var MAIN_IMAGES = [
        { src: "assets/images/gallery/electrical-1.jpg", alt: "Hands-on electrical systems training at Germaine Institute", cap: "Electrical Systems Training" },
        { src: "assets/images/gallery/ict-1.jpg", alt: "ICT and digital skills training session", cap: "ICT &amp; Digital Skills Training" },
        { src: "assets/images/gallery/health-1.jpg", alt: "Health sciences practical training", cap: "Health Sciences Training" },
        { src: "assets/images/gallery/kitchen-1.jpg", alt: "Culinary and hospitality training in session", cap: "Culinary &amp; Hospitality Training" },
        { src: "assets/images/gallery/auto-1.jpg", alt: "Automotive technology training workshop", cap: "Automotive Technology Training" },
        { src: "assets/images/gallery/communication-studio.jpg", alt: "Media and broadcast production training", cap: "Media &amp; Broadcast Training" },
        { src: "assets/images/gallery/fashion-2.jpg", alt: "Fashion and design training session", cap: "Fashion &amp; Design Training" },
        { src: "assets/images/gallery/reception-1.jpg", alt: "Professional front office training", cap: "Front Office &amp; Business Training" }
    ];

    var SIDE_A_IMAGES = [
        { src: "assets/images/gallery/electrical-2.jpg", alt: "Electrical practical training session", cap: "Electrical Practical Training" },
        { src: "assets/images/gallery/ict-2.jpg", alt: "Computer training lab in session", cap: "Computer Training Lab" },
        { src: "assets/images/campus/practical-training.jpg", alt: "Hands-on practical training", cap: "Hands-On Practical Training" },
        { src: "assets/images/slide/pexels-gustavo-fring-7446914.jpg", alt: "Technical skills training", cap: "Technical Skills Training" },
        { src: "assets/images/gallery/electrical-3.jpg", alt: "Electrical workshop training session", cap: "Electrical Workshop Training" },
        { src: "assets/images/slide/pexels-cottonbro-8369250.jpg", alt: "Applied skills training", cap: "Applied Skills Training" },
        { src: "assets/images/slide/plumbing.jpg", alt: "Vocational skills training", cap: "Vocational Skills Training" },
        { src: "assets/images/slide/pexels-pavel-danilyuk-8152731.jpg", alt: "Technical instruction session", cap: "Technical Instruction" }
    ];

    var SIDE_B_IMAGES = [
        { src: "assets/images/gallery/reception-2.jpg", alt: "Corporate front office and business training", cap: "Business &amp; Admin Training" },
        { src: "assets/images/campus/student-life.jpg", alt: "Cohort training session", cap: "Cohort Training" },
        { src: "assets/images/campus/library.jpg", alt: "Resource and research center", cap: "Resource Center" },
        { src: "assets/images/slide/hospitality.jpg", alt: "Hospitality sector training", cap: "Hospitality Training" },
        { src: "assets/images/slide/pexels-ann-h-45017-38482447.jpg", alt: "Team building session", cap: "Team Building" },
        { src: "assets/images/slide/pexels-harold-vasquez-853421-2653362.jpg", alt: "Corporate workshop session", cap: "Corporate Workshops" },
        { src: "assets/images/slide/pexels-mohammad-yasir-3365802-5198392.jpg", alt: "Group training session", cap: "Group Training" },
        { src: "assets/images/slide/pexels-karola-g-5717766.jpg", alt: "Professional development session", cap: "Professional Development" }
    ];

    function buildTrack(trackEl, images) {
        images.forEach(function (item, i) {
            var slide = document.createElement("div");
            slide.className = "ct-bento-slide" + (i === 0 ? " ct-active" : "");
            var img = document.createElement("img");
            img.src = item.src;
            img.alt = item.alt;
            img.loading = "lazy";
            slide.appendChild(img);
            trackEl.appendChild(slide);
        });
    }

    function makePanel(trackId, capId, images, intervalMs, dotsId) {
        var trackEl = document.getElementById(trackId);
        var capEl = capId ? document.getElementById(capId) : null;
        var dotsEl = dotsId ? document.getElementById(dotsId) : null;
        if (!trackEl) return null;

        buildTrack(trackEl, images);
        var slides = Array.prototype.slice.call(trackEl.querySelectorAll(".ct-bento-slide"));
        var index = 0;
        var timer = null;

        if (dotsEl) {
            images.forEach(function (item, i) {
                var dot = document.createElement("span");
                dot.className = "ct-bento-dot" + (i === 0 ? " ct-active" : "");
                dot.addEventListener("click", function () { goTo(i); restart(); });
                dotsEl.appendChild(dot);
            });
        }

        function updateCaption() {
            if (capEl) capEl.innerHTML = images[index].cap;
        }
        function updateDots() {
            if (!dotsEl) return;
            Array.prototype.forEach.call(dotsEl.children, function (d, i) {
                d.classList.toggle("ct-active", i === index);
            });
        }

        function goTo(i) {
            slides[index].classList.remove("ct-active");
            index = (i + images.length) % images.length;
            slides[index].classList.add("ct-active");
            updateCaption();
            updateDots();
        }
        function next() { goTo(index + 1); }
        function prev() { goTo(index - 1); }

        function start() {
            if (timer) return;
            timer = window.setInterval(next, intervalMs);
        }
        function stop() {
            if (timer) { window.clearInterval(timer); timer = null; }
        }
        function restart() { stop(); start(); }

        updateCaption();

        return { next: next, prev: prev, start: start, stop: stop, restart: restart };
    }

    var reduceMotion = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);

    var mainPanel = makePanel("ctBentoMainTrack", "ctBentoMainCap", MAIN_IMAGES, 5500, "ctBentoMainDots");
    var sideAPanel = makePanel("ctBentoSideATrack", "ctBentoSideACap", SIDE_A_IMAGES, 6000, null);
    var sideBPanel = makePanel("ctBentoSideBTrack", "ctBentoSideBCap", SIDE_B_IMAGES, 6400, null);

    var panels = [mainPanel, sideAPanel, sideBPanel].filter(Boolean);

    var prevBtn = document.getElementById("ctBentoPrev");
    var nextBtn = document.getElementById("ctBentoNext");
    if (prevBtn && mainPanel) prevBtn.addEventListener("click", function () { mainPanel.prev(); mainPanel.restart(); });
    if (nextBtn && mainPanel) nextBtn.addEventListener("click", function () { mainPanel.next(); mainPanel.restart(); });

    if (!reduceMotion) {
        panels.forEach(function (p) { p.start(); });
    }

    bento.addEventListener("mouseenter", function () { panels.forEach(function (p) { p.stop(); }); });
    bento.addEventListener("mouseleave", function () {
        if (!reduceMotion) panels.forEach(function (p) { p.start(); });
    });
})();

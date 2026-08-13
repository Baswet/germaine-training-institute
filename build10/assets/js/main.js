/*=========================================================
    GERMAINE TRAINING INSTITUTE
    Premium Website JavaScript v3.0
    Designed for Homepage
=========================================================*/

"use strict";

/*=========================================================
    WAIT UNTIL PAGE IS READY
=========================================================*/

document.addEventListener("DOMContentLoaded", () => {

    initializeWebsite();

});

/*=========================================================
    INITIALIZE WEBSITE
=========================================================*/

function initializeWebsite() {

    initHeaderHeightVar();

    initPreloader();

    initThemeToggle();

    initGlanceAccordion();

    initStickyHeader();

    initMobileMenu();

    initSearchModal();

    initSmoothScroll();

    initAnnouncementPopup();

}

/*=========================================================
    DARK MODE TOGGLE
=========================================================*/

function initThemeToggle() {

    const toggles = document.querySelectorAll(".theme-toggle");

    if (!toggles.length) return;

    toggles.forEach((toggle) => {

        toggle.addEventListener("click", () => {

            const isDark = document.documentElement.getAttribute("data-theme") === "dark";

            if (isDark) {

                document.documentElement.removeAttribute("data-theme");
                localStorage.setItem("germaine-theme", "light");

            } else {

                document.documentElement.setAttribute("data-theme", "dark");
                localStorage.setItem("germaine-theme", "dark");

            }

        });

    });

}

/*=========================================================
    "AT A GLANCE" HOVER-REVEAL ACCORDION
    (touch + keyboard support — hover already works via CSS)
=========================================================*/

function initGlanceAccordion() {

    const accordion = document.getElementById("glanceAccordion");

    if (!accordion) return;

    const panels = Array.from(accordion.querySelectorAll(".glance-panel"));
    const isTouch = window.matchMedia("(hover: none), (pointer: coarse)").matches;

    function closeAll(except) {

        panels.forEach((p) => {

            if (p !== except) {

                p.classList.remove("active");
                p.setAttribute("aria-expanded", "false");

            }

        });

    }

    panels.forEach((panel) => {

        // Touch devices: first tap expands, second tap on the same
        // panel (or a link inside it) follows through as normal.
        panel.addEventListener("click", (e) => {

            if (!isTouch) return;

            const isOpen = panel.classList.contains("active");

            if (!isOpen) {

                e.preventDefault();
                closeAll(panel);
                panel.classList.add("active");
                panel.setAttribute("aria-expanded", "true");

            }

        });

        // Keyboard support (Enter / Space toggles, like a native disclosure)
        panel.addEventListener("keydown", (e) => {

            if (e.key !== "Enter" && e.key !== " ") return;

            e.preventDefault();

            const isOpen = panel.classList.contains("active");

            closeAll(panel);
            panel.classList.toggle("active", !isOpen);
            panel.setAttribute("aria-expanded", String(!isOpen));

        });

        panel.addEventListener("focus", () => closeAll(panel));

    });

    // Tapping outside the accordion collapses everything again
    document.addEventListener("click", (e) => {

        if (isTouch && !accordion.contains(e.target)) {

            closeAll(null);

        }

    });

}

/*=========================================================
    PRELOADER
=========================================================*/

function initPreloader() {

    window.addEventListener("load", () => {

        const preloader = document.querySelector(".preloader");

        if (!preloader) return;

        preloader.classList.add("loader-hidden");

        setTimeout(() => {

            preloader.remove();

        }, 600);

    });

}

/*=========================================================
    STICKY HEADER
=========================================================*/

function initStickyHeader() {

    const header = document.getElementById("header");

    if (!header) return;

    const utilityBar = document.getElementById("utilityBar");

    // Hysteresis: separate activate/deactivate thresholds so the header
    // never flickers back and forth while the user hovers near a single
    // scroll position. Enter "sticky" only past 80px, and only leave it
    // once the user has scrolled back up past 60px — the 20px dead zone
    // in between is what eliminates the stutter/oscillation.
    const ACTIVATE_AT = 80;
    const DEACTIVATE_AT = 60;

    let isSticky = false;
    let ticking = false;

    function applyState() {

        // Single state swap: the class is only ever added/removed when
        // isSticky actually changes, never re-applied every scroll tick.
        if (!isSticky && window.scrollY > ACTIVATE_AT) {

            isSticky = true;
            header.classList.add("sticky");
            if (utilityBar) utilityBar.classList.add("sticky");

        } else if (isSticky && window.scrollY < DEACTIVATE_AT) {

            isSticky = false;
            header.classList.remove("sticky");
            if (utilityBar) utilityBar.classList.remove("sticky");

        }

        ticking = false;

    }

    function handleScroll() {

        if (!ticking) {
            window.requestAnimationFrame(applyState);
            ticking = true;
        }

    }

    // passive: the listener never calls preventDefault, so the browser
    // can keep scrolling smooth (60fps) without waiting on this handler
    window.addEventListener("scroll", handleScroll, { passive: true });

    applyState();

}

/*=========================================================
    MOBILE MENU
=========================================================*/

function initMobileMenu() {

    const hamburger = document.getElementById("hamburgerBtn");
    const pageShell = document.getElementById("pageShell");
    const sideNav = document.getElementById("sideNav");
    const backdrop = document.getElementById("sideNavBackdrop");

    if (!hamburger || !pageShell || !sideNav) return;

    function openMenu() {

        pageShell.classList.add("menu-open");
        hamburger.setAttribute("aria-expanded", "true");

    }

    function closeMenu() {

        pageShell.classList.remove("menu-open");
        hamburger.setAttribute("aria-expanded", "false");

    }

    hamburger.addEventListener("click", () => {

        const isOpen = pageShell.classList.contains("menu-open");

        if (isOpen) {
            closeMenu();
        } else {
            openMenu();
        }

    });

    sideNav.querySelectorAll("a").forEach(link => {

        link.addEventListener("click", closeMenu);

    });

    if (backdrop) {

        backdrop.addEventListener("click", closeMenu);

    }

    document.addEventListener("keydown", (e) => {

        if (e.key === "Escape") closeMenu();

    });

    // Collapse the panel automatically if the viewport grows back to desktop
    window.addEventListener("resize", () => {

        if (window.innerWidth > 992) closeMenu();

    });

}

/*=========================================================
    FIXED HEADER HEIGHT
    (measures the real stacked height of top-bar +
    announcement bar + navbar so the page-shell and
    side-nav can offset/clear it precisely at any
    breakpoint or font size)
=========================================================*/

function initHeaderHeightVar() {

    const stack = document.getElementById("fixedTopStack");

    if (!stack) return;

    const utilityBar = document.getElementById("utilityBar");

    function updateHeight() {

        const height = stack.getBoundingClientRect().height;

        document.documentElement.style.setProperty("--header-height", height + "px");

        /* The utility bar is in normal flow above .page-shell, while the stack
           is fixed at top:0 and paints over it. Content therefore only needs to
           clear (stack height - utility bar height); reserving the full stack
           height on top of the bar's own flow height leaves a visible gap
           between the header and the hero. */
        const utilityHeight = utilityBar ? utilityBar.getBoundingClientRect().height : 0;

        const offset = Math.max(height - utilityHeight, 0);

        document.documentElement.style.setProperty("--content-offset", offset + "px");

    }

    updateHeight();

    window.addEventListener("resize", updateHeight);
    window.addEventListener("load", updateHeight);

    if (document.fonts && document.fonts.ready) {

        document.fonts.ready.then(updateHeight);

    }

}
/*=========================================================
    ANNOUNCEMENT POPUP BANNER
    Slides in 2s after load, stays visible 5s, hides, then
    reappears on a 10s cycle. A dismiss control stops the
    loop for the rest of the session.
=========================================================*/

function initAnnouncementPopup() {

    const bar = document.querySelector(".announcement-bar");

    if (!bar) return;

    /* This banner is a timed, self-reappearing "Apply" advertisement.
       It must never appear on employer/partner/recruitment-facing
       pages, where a scholarship promo is off-brand and distracting:
       AI Bootcamps (hub, catalogue and every programme detail page),
       Partner With Us, Hire Our Graduates, Alumni Registration,
       Explore Vacancies and Corporate Training. Matched by filename
       prefix so it stays correct as new AI programme pages are added. */
    const ANNOUNCEMENT_EXCLUDED_PREFIXES = [
        "ai-bootcamp",       // ai-bootcamp.html, ai-bootcamp-courses.html
        "ai-course-",        // every ai-course-*.html programme detail page
        "partner-with-us",
        "graduate-hire",     // Hire Our Graduates
        "alumni",            // Alumni Registration
        "vacancies",         // Explore Vacancies
        "corporate-training"
    ];
    const currentFile = (location.pathname.split("/").pop() || "index.html").toLowerCase();
    const isExcluded = ANNOUNCEMENT_EXCLUDED_PREFIXES.some((prefix) => currentFile.startsWith(prefix));
    if (isExcluded) {
        bar.remove();
        return;
    }

    const SHOW_DELAY = 2000;   // first appearance
    const VISIBLE_MS = 5000;   // how long it stays up
    const REPEAT_MS = 10000;   // cadence of subsequent appearances

    let hideTimer = null;
    let repeatTimer = null;
    let dismissed = false;

    // inject a dismiss control if the markup doesn't already have one
    let closeBtn = bar.querySelector(".announcement-close");

    if (!closeBtn) {

        closeBtn = document.createElement("button");
        closeBtn.type = "button";
        closeBtn.className = "announcement-close";
        closeBtn.setAttribute("aria-label", "Dismiss announcement");
        closeBtn.innerHTML = '<i class="fas fa-xmark"></i>';

        const container = bar.querySelector(".announcement-container") || bar;
        container.appendChild(closeBtn);

    }

    function show() {

        if (dismissed) return;

        bar.classList.add("is-visible");

        clearTimeout(hideTimer);
        hideTimer = setTimeout(hide, VISIBLE_MS);

    }

    function hide() {
        bar.classList.remove("is-visible");
    }

    closeBtn.addEventListener("click", () => {

        dismissed = true;
        hide();

        clearTimeout(hideTimer);
        clearInterval(repeatTimer);

    });

    setTimeout(() => {

        show();

        repeatTimer = setInterval(show, REPEAT_MS);

    }, SHOW_DELAY);

}

/*=========================================================
    SEARCH MODAL
=========================================================*/

function initSearchModal() {

    const searchBtns = document.querySelectorAll(".search-btn");
    const searchModal = document.querySelector(".search-modal");

    if (!searchBtns.length || !searchModal) return;

    const input = searchModal.querySelector("input");
    const pageShell = document.getElementById("pageShell");

    searchBtns.forEach((searchBtn) => {

        searchBtn.addEventListener("click", () => {

            searchModal.classList.add("active");

            if (pageShell) pageShell.classList.remove("menu-open");

            if (input) {

                setTimeout(() => input.focus(), 300);

            }

        });

    });

    searchModal.addEventListener("click", (e) => {

        if (e.target === searchModal) {

            searchModal.classList.remove("active");

        }

    });

    document.addEventListener("keydown", (e) => {

        if (e.key === "Escape") {

            searchModal.classList.remove("active");

        }

    });

}

/*=========================================================
    SMOOTH SCROLLING
=========================================================*/

function initSmoothScroll() {

    document.querySelectorAll('a[href^="#"]').forEach(link => {

        link.addEventListener("click", function (e) {

            const targetID = this.getAttribute("href");

            if (targetID === "#") return;

            const target = document.querySelector(targetID);

            if (!target) return;

            e.preventDefault();

            target.scrollIntoView({

                behavior: "smooth",
                block: "start"

            });

        });

    });

}

/*=========================================================
    HERO BACKGROUND SLIDER
=========================================================*/

function initHeroSlider() {

    const slides = document.querySelectorAll(".hero-slider .slide");

    if (slides.length === 0) return;

    let current = 0;

    function showSlide(index) {

        slides.forEach(slide => {

            slide.classList.remove("active");

        });

        slides[index].classList.add("active");

    }

    showSlide(current);

    setInterval(() => {

        current++;

        if (current >= slides.length) {

            current = 0;

        }

        showSlide(current);

    }, 5000);

}

/*=========================================================
    FLOATING HERO CARDS
=========================================================*/

function initFloatingCards() {

    const cards = document.querySelectorAll(".floating-card");

    if (cards.length === 0) return;

    function animate() {

        const time = Date.now() * 0.001;

        cards.forEach((card, index) => {

            const offset = Math.sin(time + index) * 10;

            card.style.transform = `translateY(${offset}px)`;

        });

        requestAnimationFrame(animate);

    }

    animate();

}

/*=========================================================
    INITIALIZE HERO FEATURES
=========================================================*/

document.addEventListener("DOMContentLoaded", () => {

    initHeroSlider();

    initFloatingCards();

});
/*=========================================================
    SCROLL REVEAL ANIMATION
=========================================================*/

function initScrollReveal() {

    const elements = document.querySelectorAll(

        ".section-heading,\
        .hero-content,\
        .hero-image,\
        .school-card,\
        .why-card,\
        .journey-card,\
        .campus-card,\
        .news-card,\
        .experience-content,\
        .experience-image,\
        .stat-box"

    );

    if (elements.length === 0) return;

    const observer = new IntersectionObserver(

        (entries) => {

            entries.forEach((entry) => {

                if (entry.isIntersecting) {

                    entry.target.classList.add("show");

                    observer.unobserve(entry.target);

                }

            });

        },

        {

            threshold: 0.15

        }

    );

    elements.forEach((element) => {

        element.classList.add("hidden");

        observer.observe(element);

    });

}

/*=========================================================
    ANIMATED COUNTERS
=========================================================*/

function initCounters() {

    const counters = document.querySelectorAll(

        ".hero-stat h2, .stat-box h2"

    );

    if (!counters.length) return;

    const observer = new IntersectionObserver(

        (entries) => {

            entries.forEach((entry) => {

                if (!entry.isIntersecting) return;

                const counter = entry.target;

                observer.unobserve(counter);

                const text = counter.innerText;

                const number = parseInt(text.replace(/\D/g, ""));

                const suffix = text.replace(/[0-9]/g, "");

                let current = 0;

                const increment = Math.max(1, Math.ceil(number / 100));

                function update() {

                    current += increment;

                    if (current >= number) {

                        counter.innerText = number + suffix;

                        return;

                    }

                    counter.innerText = current + suffix;

                    requestAnimationFrame(update);

                }

                update();

            });

        },

        {

            threshold: 0.5

        }

    );

    counters.forEach(counter => observer.observe(counter));

}

/*=========================================================
    IMAGE HOVER EFFECT
=========================================================*/

function initImageHover() {

    const images = document.querySelectorAll(

        ".school-image img,\
        .campus-card img,\
        .experience-image img,\
        .welcome-image img"

    );

    images.forEach((image) => {

        image.style.transition = "transform .6s ease";

        image.addEventListener("mouseenter", () => {

            image.style.transform = "scale(1.08)";

        });

        image.addEventListener("mouseleave", () => {

            image.style.transform = "scale(1)";

        });

    });

}

/*=========================================================
    ACTIVE NAVIGATION
=========================================================*/

function initActiveNavigation() {

    const sections = document.querySelectorAll("section[id]");

    const navLinks = document.querySelectorAll(".nav-links a");

    if (!sections.length || !navLinks.length) return;

    window.addEventListener("scroll", () => {

        let current = "";

        sections.forEach((section) => {

            const top = section.offsetTop - 150;

            const height = section.offsetHeight;

            if (

                window.scrollY >= top &&

                window.scrollY < top + height

            ) {

                current = section.getAttribute("id");

            }

        });

        navLinks.forEach((link) => {

            link.classList.remove("active");

            const href = link.getAttribute("href");

            if (href === "#" + current) {

                link.classList.add("active");

            }

        });

    }, { passive: true });

}

/*=========================================================
    INITIALIZE SECTION ANIMATIONS
=========================================================*/

document.addEventListener("DOMContentLoaded", () => {

    initScrollReveal();

    initCounters();

    initImageHover();

    initActiveNavigation();

});
/*=========================================================
    BACK TO TOP BUTTON
=========================================================*/

function initBackToTop() {

    const button = document.querySelector(".back-to-top");

    if (!button) return;

    function toggleButton() {

        if (window.scrollY > 500) {

            button.classList.add("show");

        } else {

            button.classList.remove("show");

        }

    }

    window.addEventListener("scroll", toggleButton, { passive: true });

    button.addEventListener("click", () => {

        window.scrollTo({

            top: 0,

            behavior: "smooth"

        });

    });

}

/*=========================================================
    TESTIMONIAL SLIDER
=========================================================*/

function initTestimonialSlider() {

    const track = document.getElementById("testimonial-track");
    const slides = document.querySelectorAll(".testimonial-slide");
    const dotsWrap = document.getElementById("testimonial-dots");
    const prevBtn = document.getElementById("t-prev");
    const nextBtn = document.getElementById("t-next");

    if (!track || slides.length === 0) return;

    let current = 0;
    let timer = null;
    let perView = 3;

    function getPerView() {
        const w = window.innerWidth;
        if (w <= 640) return 1;
        if (w <= 992) return 2;
        return 3;
    }

    function maxIndex() {
        return Math.max(0, slides.length - perView);
    }

    function buildDots() {
        if (!dotsWrap) return;
        const count = maxIndex() + 1;
        dotsWrap.innerHTML = "";
        for (let i = 0; i < count; i++) {
            const dot = document.createElement("span");
            dot.className = "t-dot" + (i === current ? " active" : "");
            dot.setAttribute("data-index", i);
            dot.addEventListener("click", () => { showSlide(i); startAutoplay(); });
            dotsWrap.appendChild(dot);
        }
    }

    function showSlide(index) {
        current = Math.max(0, Math.min(index, maxIndex()));
        track.style.transform = "translateX(-" + (current * (100 / perView)) + "%)";
        dotsWrap && dotsWrap.querySelectorAll(".t-dot").forEach((d, i) => {
            d.classList.toggle("active", i === current);
        });
    }

    function nextSlide() {
        showSlide(current >= maxIndex() ? 0 : current + 1);
    }

    function prevSlide() {
        showSlide(current <= 0 ? maxIndex() : current - 1);
    }

    function startAutoplay() {
        stopAutoplay();
        timer = setInterval(nextSlide, 6000);
    }

    function stopAutoplay() {
        if (timer) clearInterval(timer);
    }

    function layout() {
        perView = getPerView();
        slides.forEach(s => { s.style.flexBasis = (100 / perView) + "%"; });
        buildDots();
        showSlide(Math.min(current, maxIndex()));
    }

    if (nextBtn) nextBtn.addEventListener("click", () => { nextSlide(); startAutoplay(); });
    if (prevBtn) prevBtn.addEventListener("click", () => { prevSlide(); startAutoplay(); });

    const wrapper = document.getElementById("testimonial-compact");

    if (wrapper) {

        wrapper.addEventListener("mouseenter", stopAutoplay);
        wrapper.addEventListener("mouseleave", startAutoplay);

    }

    let resizeT = null;
    window.addEventListener("resize", () => {
        clearTimeout(resizeT);
        resizeT = setTimeout(layout, 150);
    });

    layout();
    startAutoplay();

}

/*=========================================================
    STAT CAPSULE COUNT-UP (Testimonials section)
=========================================================*/

function initTestimonialStatsCountUp() {

    const nums = document.querySelectorAll(".tst-stats [data-count]");
    if (!nums.length) return;

    const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const co = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
            if (!e.isIntersecting) return;
            const el = e.target;
            const target = parseInt(el.getAttribute("data-count"), 10) || 0;
            const suffix = el.getAttribute("data-suffix") || "";
            co.unobserve(el);

            if (reduce) { el.textContent = target.toLocaleString() + suffix; return; }

            const dur = 1600;
            let start = null;
            function tick(ts) {
                if (!start) start = ts;
                const p = Math.min((ts - start) / dur, 1);
                const eased = 1 - Math.pow(1 - p, 3);
                el.textContent = Math.round(target * eased).toLocaleString() + suffix;
                if (p < 1) requestAnimationFrame(tick);
                else el.textContent = target.toLocaleString() + suffix;
            }
            requestAnimationFrame(tick);
        });
    }, { threshold: 0.5 });

    nums.forEach((el) => co.observe(el));

}

/*=========================================================
    INDUSTRY RECOGNITION LOGO CAROUSEL
=========================================================*/

/*=========================================================
    INDUSTRY RECOGNITION LOGO CAROUSEL
    Generic: works for every ".logo-carousel" on the page
    (index.html's #logo-carousel and about.html's
    #ab-logo-carousel both use the same classes). Existing
    drag-to-scroll is preserved; new prev/next arrow buttons
    pause the infinite CSS scroll, nudge the track by one
    card width, then auto-resume the seamless loop after a
    short idle period.
=========================================================*/

function initLogoCarousel() {

    const carousels = document.querySelectorAll(".logo-carousel");

    carousels.forEach((carousel) => {

        const track = carousel.querySelector(".logo-track");
        if (!track) return;

        let isDown = false;
        let startX = 0;
        let scrollStart = 0;

        function getX(e) {
            return (e.touches ? e.touches[0].clientX : e.clientX);
        }

        track.addEventListener("mousedown", (e) => {
            isDown = true;
            track.classList.add("dragging");
            startX = getX(e);
            scrollStart = track.getBoundingClientRect().left;
        });

        track.addEventListener("touchstart", (e) => {
            isDown = true;
            track.classList.add("dragging");
            startX = getX(e);
            scrollStart = track.getBoundingClientRect().left;
        }, { passive: true });

        function endDrag() {
            isDown = false;
            track.classList.remove("dragging");
        }

        window.addEventListener("mouseup", endDrag);
        window.addEventListener("touchend", endDrag);

        track.addEventListener("mousemove", (e) => {
            if (!isDown) return;
            e.preventDefault();
        });

        /* ---- prev / next arrow controls ---- */
        const prevBtn = carousel.parentElement.querySelector(".ir-nav-btn.prev");
        const nextBtn = carousel.parentElement.querySelector(".ir-nav-btn.next");
        if (!prevBtn && !nextBtn) return;

        let manualOffset = 0;
        let resumeTimer = null;
        const firstItem = track.querySelector(".logo-item");
        const step = firstItem ? (firstItem.getBoundingClientRect().width + 16) : 166;

        function nudge(direction) {
            track.classList.add("manual");
            manualOffset += direction * step;
            track.style.transform = `translateX(${manualOffset}px)`;
            clearTimeout(resumeTimer);
            resumeTimer = setTimeout(() => {
                track.classList.remove("manual");
                track.style.transform = "";
                manualOffset = 0;
            }, 4000);
        }

        if (prevBtn) prevBtn.addEventListener("click", () => nudge(1));
        if (nextBtn) nextBtn.addEventListener("click", () => nudge(-1));

    });

}

/*=========================================================
    BUTTON RIPPLE EFFECT
=========================================================*/

function initRippleEffect() {

    const buttons = document.querySelectorAll(

        ".btn-primary,.btn-secondary,.apply-btn,.portal-btn"

    );

    buttons.forEach(button => {

        button.addEventListener("click", function(e){

            const ripple = document.createElement("span");

            ripple.classList.add("ripple");

            const rect = this.getBoundingClientRect();

            ripple.style.left =

                e.clientX - rect.left + "px";

            ripple.style.top =

                e.clientY - rect.top + "px";

            this.appendChild(ripple);

            setTimeout(() => {

                ripple.remove();

            },600);

        });

    });

}

/*=========================================================
    HERO PARALLAX EFFECT
=========================================================*/

function initHeroParallax() {

    const hero = document.querySelector(".hero");

    if (!hero) return;

    /* rAF-throttled and passive: the handler no longer runs on every scroll
       event, and it never blocks the scroll thread. The style write is
       batched into the next animation frame instead of firing synchronously
       mid-scroll, which removes the jank this parallax used to cause. */

    let ticking = false;

    window.addEventListener("scroll", () => {

        if (ticking) return;

        ticking = true;

        window.requestAnimationFrame(() => {

            hero.style.backgroundPositionY = window.pageYOffset * 0.35 + "px";

            ticking = false;

        });

    }, { passive: true });

}

/*=========================================================
    LAZY IMAGE LOADING
=========================================================*/

function initLazyLoading() {

    if (!("loading" in HTMLImageElement.prototype)) return;

    /* Only fill in a default for images whose markup does NOT already
       declare an intent. Blanket-assigning lazy here used to override the
       authored loading="eager" on the brand logo and hero images, which
       demoted the LCP candidate on every page. */

    const images = document.querySelectorAll("img:not([loading])");

    images.forEach(image => {

        image.loading = "lazy";

        image.decoding = "async";

    });

}

/*=========================================================
    ANNOUNCEMENT BAR
=========================================================*/

function initAnnouncementBar() {

    const bar = document.querySelector(".announcement-bar");

    if (!bar) return;

    bar.classList.add("slide-in");

}

/*=========================================================
    NAVBAR TRANSPARENCY — removed (Global Navigation
    Consistency pass). This toggled a ".solid" class that
    has no matching CSS anywhere in the project (verified),
    so it had zero visual effect — but it duplicated the
    single, already-correct hysteresis-based sticky logic
    in initStickyHeader() above, using a different, non-
    hysteresis threshold (scrollY < 30, no dead zone). One
    scroll-state mechanism now drives the header everywhere.
=========================================================*/

/*=========================================================
    PERFORMANCE OPTIMIZATION
=========================================================*/

function throttle(callback, delay) {

    let waiting = false;

    return function () {

        if (waiting) return;

        callback.apply(this, arguments);

        waiting = true;

        setTimeout(() => {

            waiting = false;

        }, delay);

    };

}

/*=========================================================
    INITIALIZE PREMIUM FEATURES
=========================================================*/

document.addEventListener("DOMContentLoaded", () => {

    initBackToTop();

    initTestimonialSlider();
    initTestimonialStatsCountUp();

    initLogoCarousel();

    initRippleEffect();

    initHeroParallax();

    initLazyLoading();

    initAnnouncementBar();

});
/*=========================================================
    GERMAINE TRAINING INSTITUTE
    PREMIUM JAVASCRIPT PART 5
=========================================================*/

/*=========================================================
    REVEAL NAVBAR DROPDOWNS
=========================================================*/

function initDropdownMenus() {

    const dropdowns = document.querySelectorAll(".dropdown");

    dropdowns.forEach(dropdown => {

        dropdown.addEventListener("mouseenter", () => {

            dropdown.classList.add("open");

        });

        dropdown.addEventListener("mouseleave", () => {

            dropdown.classList.remove("open");

        });

    });

}

/*=========================================================
    SCROLL PROGRESS BAR
=========================================================*/

function initScrollProgress() {

    const progress = document.querySelector(".scroll-progress");

    if (!progress) return;

    function updateProgress() {

        const totalHeight =
            document.documentElement.scrollHeight -
            window.innerHeight;

        const progressHeight =
            (window.pageYOffset / totalHeight) * 100;

        progress.style.width = progressHeight + "%";

    }

    window.addEventListener("scroll", updateProgress, { passive: true });

}

/*=========================================================
    BUTTON LOADING EFFECT
=========================================================*/

function initButtonLoading() {

    const buttons = document.querySelectorAll(

        ".apply-btn,.portal-btn,.btn-primary"

    );

    buttons.forEach(button => {

        button.addEventListener("click", function () {

            if (this.classList.contains("loading")) return;

            this.classList.add("loading");

            const original = this.innerHTML;

            this.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> Loading';

            setTimeout(() => {

                this.innerHTML = original;

                this.classList.remove("loading");

            }, 1500);

        });

    });

}

/*=========================================================
    NEWS CARD HOVER
=========================================================*/

function initNewsCards() {

    const cards = document.querySelectorAll(".news-card");

    cards.forEach(card => {

        card.addEventListener("mouseenter", () => {

            card.style.transform =
                "translateY(-10px)";

        });

        card.addEventListener("mouseleave", () => {

            card.style.transform =
                "translateY(0)";

        });

    });

}

/*=========================================================
    ACCESSIBILITY
=========================================================*/

function initAccessibility() {

    document.addEventListener("keyup", function(e){

        if(e.key==="Escape"){

            document
                .querySelector(".nav-links")
                ?.classList.remove("active");

            document
                .querySelector(".search-modal")
                ?.classList.remove("active");

        }

    });

}

/*=========================================================
    CONTACT FORM VALIDATION
=========================================================*/

function initForms() {

    const forms = document.querySelectorAll("form");

    forms.forEach(form => {

        form.addEventListener("submit", function(e){

            // Step 9 fix: forms wired to a real backend endpoint (contact,
            // newsletter, alumni, partner enquiry, graduate profile request,
            // AI Bootcamp apply, corporate-training consultation, etc.) mark
            // themselves with data-form-handled="true" as soon as their own
            // dedicated script binds. Those forms manage their own
            // validation/loading/success/error state and must submit to the
            // real API — this generic handler must never touch them.
            // Without this check it was resetting the fields and showing a
            // fake success note BEFORE the real handler ran, so the real
            // handler always saw empty required fields and silently bailed:
            // every "already integrated" form on the site was discarding
            // user submissions while still showing a fake thank-you message.
            if (form.hasAttribute("data-form-handled")) {
                return;
            }

            const required =

                form.querySelectorAll("[required]");

            let valid = true;

            required.forEach(input => {

                if(input.value.trim()===""){

                    valid = false;

                    input.classList.add("input-error");

                }

                else{

                    input.classList.remove("input-error");

                }

            });

            e.preventDefault();

            if(!valid){

                return;

            }

            let note = form.querySelector(".form-success");

            if(!note){

                note = document.createElement("p");
                note.className = "form-success";
                note.style.cssText = "margin-top:16px;padding:14px 18px;background:rgba(16, 42, 92,.08);color:#102A5C;border-radius:8px;font-size:.9rem;font-weight:600;text-align:center;";
                form.appendChild(note);

            }

            note.textContent = "Thank you! Your message has been received. Our team will be in touch shortly.";

            form.reset();

        });

    });

}

/*=========================================================
    CURRENT YEAR
=========================================================*/

function initCurrentYear(){

    const year=document.getElementById("year");

    if(year){

        year.textContent=new Date().getFullYear();

    }

}

/*=========================================================
    PREMIUM INITIALIZATION
=========================================================*/

document.addEventListener("DOMContentLoaded",()=>{

    initDropdownMenus();

    initScrollProgress();

    initButtonLoading();

    initNewsCards();

    initAccessibility();

    initForms();

    initCurrentYear();

});

console.log(
"%cGermaine Training Institute Website Loaded Successfully",
"color:#102A5C;font-size:18px;font-weight:bold;"
);
/*=========================================
    HERO IMAGE SLIDER
=========================================*/

const heroSlides = document.querySelectorAll(".hero-slide");
const heroDots = document.querySelectorAll(".slider-dots .dot");

let heroIndex = 0;

function showHeroSlide(index){

    if(heroSlides.length === 0) return;

    heroSlides.forEach(slide=>{
        slide.classList.remove("active");
    });

    heroDots.forEach(dot=>{
        dot.classList.remove("active");
    });

    if(heroSlides[index]) heroSlides[index].classList.add("active");
    if(heroDots[index]) heroDots[index].classList.add("active");

}

function nextHeroSlide(){

    heroIndex++;

    if(heroIndex >= heroSlides.length){

        heroIndex = 0;

    }

    showHeroSlide(heroIndex);

}

if(heroSlides.length > 0){

    setInterval(nextHeroSlide,4500);

    heroDots.forEach((dot,index)=>{

        dot.addEventListener("click",()=>{

            heroIndex=index;

            showHeroSlide(heroIndex);

        });

    });

}
/*==================================================
    GERMAINE — AI BOOTCAMP PAGE SCRIPT
    Self-contained: hero counters, student-experience
    bento slideshow, curriculum + FAQ accordions,
    apply form submit. Does not touch main.js.
==================================================*/
(function () {
    "use strict";

    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------- HERO STAT COUNTERS ---------- */
    var nums = document.querySelectorAll(".ai-count");
    if (nums.length && !reduceMotion && typeof IntersectionObserver !== "undefined") {
        var co = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var el = entry.target;
                var target = parseInt(el.getAttribute("data-count"), 10) || 0;
                var suffix = el.getAttribute("data-suffix") || "";
                var dur = 1400, start = null;
                function step(ts) {
                    if (!start) start = ts;
                    var p = Math.min((ts - start) / dur, 1);
                    el.textContent = Math.floor(p * target) + suffix;
                    if (p < 1) requestAnimationFrame(step);
                    else el.textContent = target + suffix;
                }
                requestAnimationFrame(step);
                co.unobserve(el);
            });
        }, { threshold: 0.6 });
        nums.forEach(function (el) { co.observe(el); });
    } else {
        nums.forEach(function (el) {
            el.textContent = (el.getAttribute("data-count") || "") + (el.getAttribute("data-suffix") || "");
        });
    }

    /* ---------- STUDENT EXPERIENCE BENTO SLIDESHOW ---------- */
    var panels = document.querySelectorAll(".ai-exp-panel");
    panels.forEach(function (panel, idx) {
        var slides = [].slice.call(panel.querySelectorAll(".ai-exp-slide"));
        if (slides.length < 2) return;
        var cur = 0;
        var delay = 4800 + idx * 700;
        var timer = null;
        function go(i) {
            slides[cur].classList.remove("ai-active");
            cur = (i + slides.length) % slides.length;
            slides[cur].classList.add("ai-active");
        }
        function start() {
            if (reduceMotion) return;
            timer = setInterval(function () { go(cur + 1); }, delay);
        }
        function stop() { clearInterval(timer); }
        start();
        panel.addEventListener("mouseenter", stop);
        panel.addEventListener("mouseleave", start);
    });

    /* ---------- GRADUATE INSIGHT TESTIMONIAL CAROUSEL ---------- */
    var tstModule = document.getElementById("aiTstModule");
    if (tstModule) {
        var tstSlides = [].slice.call(tstModule.querySelectorAll(".ai-tst-slide"));
        var tstDots = [].slice.call(tstModule.querySelectorAll(".ai-tst-dotbtn"));
        var tstPrev = tstModule.querySelector("[data-tst-prev]");
        var tstNext = tstModule.querySelector("[data-tst-next]");
        var tstCur = 0;
        var tstTimer = null;

        function tstGo(i) {
            tstSlides[tstCur].classList.remove("is-active");
            tstDots[tstCur] && tstDots[tstCur].classList.remove("is-active");
            tstCur = (i + tstSlides.length) % tstSlides.length;
            tstSlides[tstCur].classList.add("is-active");
            tstDots[tstCur] && tstDots[tstCur].classList.add("is-active");
        }
        function tstStart() {
            if (reduceMotion || tstSlides.length < 2) return;
            tstTimer = setInterval(function () { tstGo(tstCur + 1); }, 4600);
        }
        function tstStop() { clearInterval(tstTimer); }
        function tstRestart() { tstStop(); tstStart(); }

        if (tstSlides.length > 1) {
            tstStart();
            tstModule.addEventListener("mouseenter", tstStop);
            tstModule.addEventListener("mouseleave", tstStart);
            if (tstPrev) tstPrev.addEventListener("click", function () { tstGo(tstCur - 1); tstRestart(); });
            if (tstNext) tstNext.addEventListener("click", function () { tstGo(tstCur + 1); tstRestart(); });
            tstDots.forEach(function (dot, i) {
                dot.addEventListener("click", function () { tstGo(i); tstRestart(); });
            });
        }
    }

    /* ---------- APPLY FORM: real submission (Part 1 of the EarnFastCash
       <-> GTI referral bridge). Previously this handler was purely
       cosmetic (e.disable + swap two <div>s) and never sent anything to
       the backend, which silently discarded every AI Bootcamp
       application and made referral attribution impossible. Now it
       resolves a real programme_id/programme_mode_id via the public
       catalogue API (same matched-by-exact-name pattern already used
       and tested by assets/js/apply-wizard.js) and posts to the same
       real POST /api/admissions/applications endpoint, including a
       referral_code when assets/js/referral-capture.js has one stored.
       No commission, referral state, or application outcome is ever
       fabricated here — this only submits what the applicant entered. */
    var form = document.getElementById("aiApplyForm");
    var success = document.getElementById("aiApplySuccess");
    var errorEl = document.getElementById("aiApplyError");
    var submitBtn = document.getElementById("aiApplySubmitBtn");
    var trackSelect = document.getElementById("aiApplyTrackSelect");
    var banner = document.getElementById("aiApplySelected");
    var progEl = document.getElementById("aiApplySelectedProgramme");
    var metaEl = document.getElementById("aiApplySelectedMeta");
    var progInput = document.getElementById("aiApplyProgramme");
    var modeInput = document.getElementById("aiApplyMode");
    var startInput = document.getElementById("aiApplyStartDate");

    var selectedCourse = null;
    var selectedMode = null;

    function showApplyError(message) {
        if (!errorEl) return;
        errorEl.textContent = message;
        errorEl.hidden = false;
    }
    function hideApplyError() {
        if (!errorEl) return;
        errorEl.hidden = true;
    }
    function setSubmitting(isSubmitting) {
        if (!submitBtn) return;
        submitBtn.disabled = isSubmitting;
        submitBtn.innerHTML = isSubmitting
            ? '<i class="fa-solid fa-spinner fa-spin"></i> Submitting…'
            : '<i class="fa-solid fa-paper-plane"></i> Submit Application';
    }

    function applySelection(course, mode) {
        selectedCourse = course;
        selectedMode = mode || (course && course.modes && course.modes.length ? course.modes[0] : null);

        if (progInput) progInput.value = course ? course.title : "";
        if (selectedMode) {
            var modeLabel = selectedMode.label + (selectedMode.sub ? " · " + selectedMode.sub : "");
            if (modeInput) modeInput.value = modeLabel;
            if (startInput) startInput.value = selectedMode.startDate || "";
            if (metaEl) metaEl.textContent = modeLabel + " · Starts " + (selectedMode.startDate || "Contact Admissions") + " · " + (selectedMode.duration || "");
        } else {
            if (modeInput) modeInput.value = "";
            if (startInput) startInput.value = "";
            if (metaEl) metaEl.textContent = "";
        }
        if (progEl) progEl.textContent = course ? course.title : "";
        if (banner) banner.hidden = !course;
    }

    /* Populate the "Bootcamp Track" fallback select from the real
       catalogue (assets/js/ai-courses-data.js) so a visitor who opens
       the Apply form without arriving from a specific course card can
       still explicitly choose a real programme — never an invented
       generic "AI Bootcamp" application with no course behind it. */
    if (trackSelect && window.GermaineAICourses) {
        window.GermaineAICourses.courses.forEach(function (c) {
            var opt = document.createElement("option");
            opt.value = c.slug;
            opt.textContent = c.title;
            trackSelect.appendChild(opt);
        });
        trackSelect.addEventListener("change", function () {
            var course = window.GermaineAICourses.getBySlug(trackSelect.value);
            if (course) applySelection(course, null);
        });
    }

    /* ---------- SELECTED PROGRAMME HAND-OFF (from Courses menu / course cards) ---------- */
    try {
        var params = new URLSearchParams(window.location.search);
        var courseSlug = params.get("course");
        var modeId = params.get("mode");
        if (courseSlug && window.GermaineAICourses) {
            var handOffCourse = window.GermaineAICourses.getBySlug(courseSlug);
            if (handOffCourse) {
                var handOffMode = null;
                if (handOffCourse.modes && handOffCourse.modes.length) {
                    handOffMode = handOffCourse.modes[0];
                    if (modeId) {
                        for (var i = 0; i < handOffCourse.modes.length; i++) {
                            if (handOffCourse.modes[i].id === modeId) { handOffMode = handOffCourse.modes[i]; break; }
                        }
                    }
                }
                applySelection(handOffCourse, handOffMode);
                if (trackSelect) trackSelect.value = handOffCourse.slug;
            }
        }
    } catch (err) { /* URLSearchParams unsupported or data unavailable — form still works unassisted */ }

    if (form && success) {
        // Claims this form so main.js's generic initForms() catch-all
        // handler backs off instead of resetting the fields and faking
        // a success message before this real handler runs.
        form.setAttribute("data-form-handled", "true");

        form.addEventListener("submit", function (e) {
            e.preventDefault();
            hideApplyError();

            if (!selectedCourse) {
                showApplyError("Please choose a bootcamp track before submitting your application.");
                return;
            }
            if (!window.GermaineAPI) {
                showApplyError("We couldn't reach the server. Please check your connection and try again.");
                return;
            }

            setSubmitting(true);

            var fullName = document.getElementById("aiName") ? document.getElementById("aiName").value.trim() : "";
            var email = document.getElementById("aiEmail") ? document.getElementById("aiEmail").value.trim() : "";
            var phone = document.getElementById("aiPhone") ? document.getElementById("aiPhone").value.trim() : "";
            var education = document.getElementById("aiEducation") ? document.getElementById("aiEducation").value : "";

            var referralCode = (window.GermaineReferral && window.GermaineReferral.getCode()) || undefined;

            // The form only knows the course's display title, never the
            // backend's numeric programme id — resolved here via the same
            // public catalogue endpoint + exact-name-match pattern already
            // used and tested by assets/js/apply-wizard.js. If no exact
            // match is found nothing is invented: the submission stops and
            // a real error is shown instead of a fabricated id.
            window.GermaineAPI.get("/api/programmes", { type: "ai_bootcamp", q: selectedCourse.title, per_page: 50 })
                .then(function (res) {
                    var items = (res.success && res.data && res.data.items) || [];
                    var match = items.filter(function (p) { return p.name === selectedCourse.title; })[0];
                    if (!match) {
                        setSubmitting(false);
                        showApplyError("We couldn't match \"" + selectedCourse.title + "\" to a programme on file. Please choose your track again and try submitting.");
                        return null;
                    }
                    return match;
                })
                .then(function (programme) {
                    if (!programme) return; // error already shown above

                    var programmeModeId = null;
                    if (selectedMode && programme.pricing && programme.pricing.modes) {
                        var modeMatch = programme.pricing.modes.filter(function (m) { return m.mode_key === selectedMode.id; })[0];
                        programmeModeId = modeMatch ? modeMatch.id : null;
                    }

                    var payload = {
                        full_name: fullName,
                        email: email,
                        phone: phone,
                        education_level: education || undefined,
                        programme_id: programme.id,
                        programme_mode_id: programmeModeId || undefined,
                        application_type: "programme_inquiry",
                        consent: true,
                        referral_code: referralCode,
                    };

                    return window.GermaineAPI.post("/api/admissions/applications", payload).then(function (res) {
                        setSubmitting(false);
                        if (!res.success) {
                            var fieldErrors = res.errors && Object.keys(res.errors).map(function (k) { return res.errors[k][0]; });
                            showApplyError((fieldErrors && fieldErrors[0]) || res.message || "We couldn't submit your application. Please check your details and try again.");
                            return;
                        }
                        form.hidden = true;
                        success.hidden = false;
                        success.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "center" });
                    });
                })
                .catch(function () {
                    setSubmitting(false);
                    showApplyError("We couldn't reach the server. Please check your connection and try again.");
                });
        });
    }

    /* ---------- APPLY FORM TOGGLE-REVEAL ---------- */
    var applyToggleBtn = document.getElementById("aiApplyToggleBtn");
    var applyCollapse = document.getElementById("aiApplyCollapse");
    if (applyToggleBtn && applyCollapse) {
        function openApplyCollapse() {
            applyCollapse.classList.add("is-open");
            applyToggleBtn.setAttribute("aria-expanded", "true");
        }
        function closeApplyCollapse() {
            applyCollapse.classList.remove("is-open");
            applyToggleBtn.setAttribute("aria-expanded", "false");
        }
        applyToggleBtn.addEventListener("click", function () {
            var isOpen = applyCollapse.classList.contains("is-open");
            if (isOpen) {
                closeApplyCollapse();
            } else {
                openApplyCollapse();
                setTimeout(function () {
                    applyCollapse.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
                }, reduceMotion ? 0 : 120);
            }
        });

        /* any link pointing to #aiApply (hero CTA, nav, etc.) opens the
           form automatically instead of landing on a collapsed button */
        var applyLinks = document.querySelectorAll('a[href="#aiApply"]');
        applyLinks.forEach(function (link) {
            link.addEventListener("click", function () {
                openApplyCollapse();
            });
        });
        if (window.location.hash === "#aiApply") {
            openApplyCollapse();
        }

        if (window.location.search.indexOf("course=") !== -1) {
            openApplyCollapse();
        }
    }
})();

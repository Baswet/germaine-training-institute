/*=========================================================
    COURSE DETAIL PAGE RENDERER
    Reads ?course=<slug> from the URL and populates the
    prospectus-style template using data from courseCatalog
    (assets/js/courses-data.js)
=========================================================*/

(function () {

    function money(n) {
        return "KES " + Number(n).toLocaleString();
    }

    function getSlug() {
        const params = new URLSearchParams(window.location.search);
        return params.get("course") || "diploma-ict";
    }

    function renderCourse(slug) {

        const course = courseCatalog[slug] || courseCatalog["diploma-ict"];
        if (!course) return;

        /* ---- Meta ---- */
        document.title = course.title + " | Germaine Training Institute";
        const metaDesc = document.getElementById("pageDescription");
        if (metaDesc) metaDesc.setAttribute("content", course.summary);

        /* ---- Breadcrumb + Hero ---- */
        document.getElementById("breadcrumbTitle").textContent = course.title;
        document.getElementById("courseLevelTag").textContent = course.qualification;
        document.getElementById("courseLevelTag").className = "course-level-tag " + course.levelClass;
        document.getElementById("courseTitle").textContent = course.title;
        document.getElementById("courseSchool").innerHTML =
            '<i class="fa-solid fa-building-columns"></i> ' + course.school;

        const heroTags = document.getElementById("courseHeroTags");
        heroTags.innerHTML = [
            ['fa-clock', course.duration],
            ['fa-money-bill-wave', course.fee + ' ' + course.feePeriod],
            ['fa-calendar-days', course.intake],
            ['fa-graduation-cap', course.mode],
            ['fa-location-dot', course.campus]
        ].map(function (t) {
            return '<span class="hero-tag"><i class="fa-solid ' + t[0] + '"></i> ' + t[1] + '</span>';
        }).join('');

        document.getElementById("courseImage").src = course.image;
        document.getElementById("courseImage").alt = course.title;

        const heroBg = document.getElementById("courseHeroBg");
        if (heroBg) heroBg.style.backgroundImage = "url('" + course.image + "')";

        /* ---- Overview ---- */
        document.getElementById("overviewTitle").textContent = "About the " + course.title;
        document.getElementById("overviewWhatItIs").textContent = course.overview.whatItIs;
        document.getElementById("overviewWhoFor").textContent = course.overview.whoFor;
        document.getElementById("overviewCareerOutlook").textContent = course.overview.careerOutlook;

        /* ---- Learning Outcomes (premium checklist cards) ---- */
        document.getElementById("overviewOutcomes").innerHTML = course.overview.learningOutcomes.map(function (o) {
            return '<div class="outcome-card"><i class="fa-solid fa-circle-check"></i><span>' + o + '</span></div>';
        }).join('');

        /* ---- Course Summary Cards ---- */
        const summaryItems = [
            ['fa-graduation-cap', 'Qualification', course.qualification],
            ['fa-building-columns', 'School', course.school],
            ['fa-clock', 'Duration', course.duration],
            ['fa-money-bill-wave', 'Tuition Fee', course.fee + ' ' + course.feePeriod],
            ['fa-calendar-days', 'Next Intake', course.intake],
            ['fa-laptop', 'Mode of Study', course.mode],
            ['fa-location-dot', 'Campus', course.campus],
            ['fa-briefcase', 'Industrial Attachment', 'Included'],
            ['fa-award', 'Certification', 'GTI / ' + course.examBody]
        ];
        document.getElementById("summaryGrid").innerHTML = summaryItems.map(function (s) {
            return '<div class="summary-card"><i class="fa-solid ' + s[0] + '"></i><div><span class="summary-label">' + s[1] + '</span><span class="summary-value">' + s[2] + '</span></div></div>';
        }).join('');

        /* ---- Careers ---- */
        document.getElementById("careerGrid").innerHTML = course.careers.map(function (c) {
            return '<div class="career-card"><span>' + c + '</span></div>';
        }).join('');

        /* ---- Entry Requirements ---- */
        document.getElementById("entryRequirementsList").innerHTML = course.entryRequirements.map(function (r) {
            return '<li><i class="fa-solid fa-circle-check"></i> ' + r + '</li>';
        }).join('');

        /* ---- Fee Structure (split one-time / recurring) ---- */
        let total = 0;
        const oneTime = course.feeItems.filter(function (f) { return f.type === "onetime"; });
        const recurring = course.feeItems.filter(function (f) { return f.type !== "onetime"; });

        document.getElementById("feeOneTimeBody").innerHTML = oneTime.map(function (f) {
            total += f.amount;
            return '<tr><td>' + f.item + '</td><td>' + Number(f.amount).toLocaleString() + '</td></tr>';
        }).join('');

        document.getElementById("feeRecurringBody").innerHTML = recurring.map(function (f) {
            total += f.amount;
            return '<tr><td>' + f.item + '</td><td>' + Number(f.amount).toLocaleString() + '</td></tr>';
        }).join('');

        document.getElementById("feeTotal").textContent = money(total);

        /* ---- Apply Timeline (shared) ---- */
        document.getElementById("applyTimeline").innerHTML = applySteps.map(function (s, i) {
            return '<div class="apply-step">' +
                '<div class="apply-step-number"><i class="fa-solid ' + s.icon + '"></i></div>' +
                '<span class="apply-step-index">Step ' + (i + 1) + '</span>' +
                '<h4>' + s.title + '</h4>' +
                '<p>' + s.text + '</p>' +
                '</div>';
        }).join('');

        /* ---- Related Courses (same school first, then curated fallback) ---- */
        const relatedWrap = document.getElementById("relatedGrid");
        const relatedSection = document.getElementById("relatedSection");

        const sameSchool = Object.keys(courseCatalog).filter(function (k) {
            return k !== slug && courseCatalog[k].school === course.school;
        });
        const curated = (course.related || []).filter(function (k) { return k !== slug; });
        const relatedSlugs = Array.from(new Set(sameSchool.concat(curated))).slice(0, 4);
        const related = relatedSlugs.map(function (s) { return [s, courseCatalog[s]]; }).filter(function (p) { return p[1]; });

        if (!related.length) {
            relatedSection.style.display = "none";
        } else {
            relatedWrap.innerHTML = related.map(function (pair) {
                const rSlug = pair[0], r = pair[1];
                return '<a class="related-card" href="course-detail.html?course=' + rSlug + '">' +
                    '<div class="related-card-img"><img src="' + r.image + '" alt="' + r.title + '" loading="lazy"></div>' +
                    '<div class="related-card-body">' +
                    '<span class="course-level-tag ' + r.levelClass + '">' + r.qualification + '</span>' +
                    '<h4>' + r.title + '</h4>' +
                    '<span class="related-card-meta"><i class="fa-solid fa-clock"></i> ' + r.duration + '</span>' +
                    '</div>' +
                    '</a>';
            }).join('');
        }

        /* Re-run scroll reveal for freshly injected [data-animate] nodes */
        if (window.initCourseDetailReveal) window.initCourseDetailReveal();
    }

    document.addEventListener("DOMContentLoaded", function () {
        renderCourse(getSlug());

        /* Scroll reveal for data-animate elements (brochure section etc.) */
        window.initCourseDetailReveal = function () {
            const animated = document.querySelectorAll("[data-animate]:not(.observed)");
            if (!animated.length) return;
            if (!("IntersectionObserver" in window)) {
                animated.forEach(function (el) { el.classList.add("show", "observed"); });
                return;
            }
            const observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("show");
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.15 });
            animated.forEach(function (el) { el.classList.add("observed"); observer.observe(el); });
        };
        window.initCourseDetailReveal();
    });

})();

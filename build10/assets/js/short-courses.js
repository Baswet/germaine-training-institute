/*==================================================
    GERMAINE — PROFESSIONAL SHORT COURSES PAGE

    Renders the category cards on the Short Courses landing
    page. Cards are name-only, matching the Academic Schools
    department cards (.ash-deptcard) exactly — no image,
    description, tagline or button. Clicking a card navigates
    to that category's own dedicated page (courses-short-
    course-<slug>.html), which reuses the exact Academic
    School page template: hero, programme table, career
    opportunities and career portal.

    Data source: window.LSC_CATEGORIES (assets/js/languages-categories.js)

    Only track === "short-course" is ever read here, so
    language categories can never appear on this page.
==================================================*/
(function () {
    "use strict";

    var CATS = window.LSC_CATEGORIES;
    var cardMount = document.getElementById("scCategoryGrid");
    if (!CATS || !cardMount) return;

    var subheading = document.getElementById("spProgSub");
    var school = window.SCHOOL_DATA && window.SCHOOL_DATA.languages;

    function slug(s) {
        return String(s)
            .toLowerCase()
            .replace(/&/g, "and")
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "");
    }

    /* short-course categories only */
    var categories = CATS.filter(function (c) { return c.track === "short-course"; });

    function progCount(catKey) {
        if (!school || !school.programmes) return 0;
        return school.programmes.filter(function (p) {
            return p.track === "short-course" && p.category === catKey;
        }).length;
    }

    /*==================================================
        CATEGORY CARDS — name only, linking to the
        category's own dedicated page.
    ==================================================*/
    function categoryCardHtml(cat) {
        var href = "courses-short-course-" + slug(cat.key) + ".html";
        return (
            '<a href="' + href + '" class="lsc-catcard">' +
                '<span class="lsc-catcard-name">' + cat.name + '</span>' +
                '<i class="fa-solid fa-arrow-right lsc-catcard-arrow" aria-hidden="true"></i>' +
            '</a>'
        );
    }

    function renderCategories() {
        cardMount.innerHTML = categories.map(categoryCardHtml).join("");

        if (subheading) {
            var total = categories.reduce(function (n, c) { return n + progCount(c.key); }, 0);
            subheading.textContent = "Choose a category to view its programmes, career opportunities and career portal — " +
                categories.length + " categories, " + total + " programmes.";
        }
    }

    renderCategories();
})();

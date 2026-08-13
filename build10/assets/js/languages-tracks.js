/*==================================================
    GERMAINE — LANGUAGES PAGE

    Renders the language cards on the Languages panel.
    Cards are name-only, matching the Academic Schools
    department cards (.ash-deptcard) exactly — no image,
    description, tagline or button. Clicking a card
    navigates to that language's own dedicated page
    (courses-language-<slug>.html), which reuses the exact
    Academic School page template: hero, programme table,
    career opportunities and career portal.

    Languages have no sub-categories, so — unlike Short
    Courses — this page never shows an in-page category
    grid beyond the four language cards themselves.

    Data source: window.LSC_CATEGORIES (assets/js/languages-categories.js)

    Only track === "language" is ever read here, so
    short-course categories can never appear on this panel
    (see short-courses.js for the sibling Short Courses
    panel on the same page).
==================================================*/
(function () {
    "use strict";

    if (document.body.getAttribute("data-school") !== "languages") return;

    var CATS = window.LSC_CATEGORIES;
    var cardMount = document.getElementById("lgCategoryGrid");
    if (!CATS || !cardMount) return;

    var subheading = document.getElementById("lgProgSub");
    var school = window.SCHOOL_DATA && window.SCHOOL_DATA.languages;

    function slug(s) {
        return String(s)
            .toLowerCase()
            .replace(/&/g, "and")
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "");
    }

    /* language categories only */
    var categories = CATS.filter(function (c) { return c.track === "language"; });

    function progCount(catKey) {
        if (!school || !school.programmes) return 0;
        return school.programmes.filter(function (p) {
            return p.track === "language" && p.category === catKey;
        }).length;
    }

    /*==================================================
        CATEGORY CARDS — name only, linking to the
        language's own dedicated page.
    ==================================================*/
    function categoryCardHtml(cat) {
        var href = "courses-language-" + slug(cat.key) + ".html";
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
            subheading.textContent = "Choose a language to view its programmes, career opportunities and career portal — " +
                categories.length + " languages, " + total + " programmes.";
        }
    }

    renderCategories();
})();

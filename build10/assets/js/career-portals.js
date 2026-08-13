/*==================================================
    GERMAINE — CAREER PORTALS (Explore Programmes page)
    Rebuilds the Career Portals block at the bottom of
    courses.html directly from window.SCHOOL_DATA /
    SCHOOL_ORDER (assets/js/school-data.js), which is the
    authoritative record of the institute's programme data.

    Every portal group and every job link is emitted exactly
    as stored — titles and URLs are never rewritten, shortened
    or merged. Groups with no links simply don't render a card
    rather than showing an empty one.
==================================================*/
(function () {
    "use strict";

    var mount = document.getElementById("cpGrid");
    if (!mount) return;

    var hasData = typeof window.SCHOOL_DATA === "object" && Array.isArray(window.SCHOOL_ORDER);
    if (!hasData) return;

    function esc(str) {
        return String(str == null ? "" : str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    /* one sentence of the source description, used as the card's
       short blurb — kept short so the cards stay compact */
    function blurb(text) {
        if (!text) return "";
        var first = String(text).split(/(?<=\.)\s/)[0] || String(text);
        if (first.length > 118) first = first.slice(0, 115).replace(/\s+\S*$/, "") + "…";
        return first;
    }

    /* Flatten SCHOOL_DATA into portal groups. A school contributes its
       own quickLinks when it has no departments carrying them; each
       department with quickLinks contributes its own card. */
    function collectGroups() {
        var groups = [];

        window.SCHOOL_ORDER.forEach(function (key) {
            var school = window.SCHOOL_DATA[key];
            if (!school) return;

            if (school.quickLinks && school.quickLinks.length) {
                groups.push({
                    title: school.label,
                    parent: "",
                    desc: blurb(school.intro || school.description),
                    links: school.quickLinks
                });
            }

            (school.departments || []).forEach(function (dept) {
                if (!dept.quickLinks || !dept.quickLinks.length) return;
                groups.push({
                    title: dept.name,
                    parent: school.label,
                    desc: blurb(dept.description),
                    links: dept.quickLinks
                });
            });
        });

        return groups;
    }

    function linkHtml(link) {
        return (
            '<li>' +
                '<a href="' + esc(link.url) + '" target="_blank" rel="noopener noreferrer">' +
                    '<i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i>' +
                    '<span>' + esc(link.label) + '</span>' +
                '</a>' +
            '</li>'
        );
    }

    function cardHtml(group) {
        return (
            '<article class="cp-card">' +
                '<header class="cp-card-head">' +
                    (group.parent ? '<span class="cp-card-parent">' + esc(group.parent) + '</span>' : '') +
                    '<h3>' + esc(group.title) + '</h3>' +
                    (group.desc ? '<p class="cp-card-desc">' + esc(group.desc) + '</p>' : '') +
                '</header>' +
                '<ul class="cp-links">' + group.links.map(linkHtml).join("") + '</ul>' +
            '</article>'
        );
    }

    var groups = collectGroups();
    var section = document.getElementById("cp-section");

    if (!groups.length) {
        if (section) section.style.display = "none";
        return;
    }

    mount.innerHTML = groups.map(cardHtml).join("");

    /* live count in the section subtitle */
    var countEl = document.getElementById("cpCount");
    if (countEl) {
        var totalLinks = groups.reduce(function (n, g) { return n + g.links.length; }, 0);
        countEl.textContent = totalLinks + " job portals across " + groups.length + " career areas";
    }
})();

/*
 * Student Life CMS bridge (Step 7 CMS addition).
 *
 * Overwrites the hero paragraph on campus.html ONLY when the admin has
 * entered a value for "student_life.hero_subtitle". Same
 * minimal-blast-radius pattern used across every other CMS bridge
 * script: .textContent only, silent no-op fallback on any failure.
 *
 * Scope note: the hero photo slideshow and the Clubs & Societies /
 * Sports & Recreation repeating lists are NOT wired here for the same
 * reason documented in homepage-cms-bridge.js — clubs-showcase.js and
 * campus-gallery.js perform their own synchronous slideshow
 * initialization that this bridge would need to safely coordinate
 * with. content_list_items already supports "student_life_clubs" and
 * "student_life_sports" and both are fully manageable from the admin
 * portal today; wiring their public display is a flagged follow-up.
 */
(function () {
    if (!window.GermaineAPI) return;

    window.GermaineAPI.get("/api/site-content", { keys: "student_life.hero_subtitle" }).then(function (res) {
        if (!res || !res.success || !res.data) return;
        var value = res.data["student_life.hero_subtitle"];
        if (!value) return;
        var el = document.getElementById("cmsStudentLifeSubtitle");
        if (el) el.textContent = value;
    }).catch(function () {
        // Silently keep the existing static Student Life hero paragraph.
    });
})();

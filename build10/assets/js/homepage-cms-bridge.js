/*
 * Homepage CMS bridge (Step 7 CMS addition).
 *
 * Fetches the admin-editable homepage hero text fields (badge, headline
 * lines, subtitle) from GET /api/site-content and overwrites ONLY the
 * specific elements below when a real, non-empty value is returned.
 *
 * Minimal-blast-radius, same pattern as school-page.js's catalogue
 * bridge (Step 7): every field is independently optional, uses
 * .textContent (never innerHTML, so nothing here can inject markup),
 * and if the API call fails, times out, or a given key has no CMS
 * value yet, the existing static hero text is left completely
 * untouched. This never blanks the hero.
 *
 * Scope note: the 4-slide hero photo slideshow (#track) is deliberately
 * NOT wired to the CMS in this pass. content_list_items already
 * supports a "homepage_hero_slides" list and it is fully manageable
 * from the admin portal today, but hero-template.js performs
 * synchronous slideshow/dot/arrow initialization that this bridge would
 * need to coordinate with (the same defer-script timing issue solved
 * for school-page.js's programme grid) — swapping slide DOM after that
 * initialization runs would desync the dots/arrows. Wiring the
 * slideshow images safely is flagged as a follow-up, not attempted
 * here without verifying hero-template.js's internals in a real
 * browser.
 */
(function () {
    if (!window.GermaineAPI) return;

    var fields = [
        { key: "homepage.hero_badge", id: "cmsHeroBadge" },
        { key: "homepage.hero_headline_line1", id: "cmsHeroLine1" },
        { key: "homepage.hero_headline_line2", id: "cmsHeroLine2" },
        { key: "homepage.hero_headline_accent", id: "cmsHeroAccent" },
        { key: "homepage.hero_subtitle", id: "cmsHeroSubtitle" },
    ];

    var keys = fields.map(function (f) { return f.key; }).join(",");

    window.GermaineAPI.get("/api/site-content", { keys: keys }).then(function (res) {
        if (!res || !res.success || !res.data) return;
        fields.forEach(function (f) {
            var value = res.data[f.key];
            if (!value) return; // no CMS override yet -> keep existing static text
            var el = document.getElementById(f.id);
            if (el) el.textContent = value;
        });
    }).catch(function () {
        // Network failure / timeout — silently keep the existing static hero text.
    });
})();

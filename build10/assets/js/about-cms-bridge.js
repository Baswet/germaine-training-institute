/*
 * About Us CMS bridge (Step 7 CMS addition).
 *
 * Overwrites the Vision / Mission statements and the Core Values list
 * ONLY when the admin has entered real CMS content for them. Same
 * minimal-blast-radius pattern as homepage-cms-bridge.js: independent
 * per-field checks, .textContent only (no HTML injection possible),
 * silent no-op fallback to the existing static wording on any failure
 * or absent value.
 *
 * about.core_values_list is stored as one newline-separated text field
 * (Step 7 CMS §9: "structured, not free-form" — this is still a single
 * registered field, just multi-line text, not an arbitrary new list
 * table). Each non-blank line becomes one <li> in the existing
 * .ab-flip-values-list, reusing the exact markup/icon already there.
 */
(function () {
    if (!window.GermaineAPI) return;

    var textFields = [
        { key: "about.vision_text", id: "cmsVisionText" },
        { key: "about.mission_text", id: "cmsMissionText" },
    ];
    var keys = textFields.map(function (f) { return f.key; }).concat(["about.core_values_list"]).join(",");

    window.GermaineAPI.get("/api/site-content", { keys: keys }).then(function (res) {
        if (!res || !res.success || !res.data) return;

        textFields.forEach(function (f) {
            var value = res.data[f.key];
            if (!value) return;
            var el = document.getElementById(f.id);
            if (el) el.textContent = value;
        });

        var coreValues = res.data["about.core_values_list"];
        if (coreValues) {
            var lines = coreValues.split("\n").map(function (l) { return l.trim(); }).filter(Boolean);
            var list = document.getElementById("cmsCoreValuesList");
            if (list && lines.length) {
                list.innerHTML = "";
                lines.forEach(function (line) {
                    var li = document.createElement("li");
                    var icon = document.createElement("i");
                    icon.className = "fa-solid fa-check";
                    li.appendChild(icon);
                    li.appendChild(document.createTextNode(" " + line));
                    list.appendChild(li);
                });
            }
        }
    }).catch(function () {
        // Silently keep the existing static Vision/Mission/Core Values text.
    });
})();

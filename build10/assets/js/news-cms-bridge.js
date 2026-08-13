/*
 * News CMS bridge (Step 7 CMS addition).
 *
 * news.html ships with 6 hand-authored static cards (see
 * NewsArticle model docstring — they are intentionally NOT
 * auto-migrated into the CMS). This bridge fetches GET /api/news and
 * replaces #newsGrid's contents ONLY when at least one published
 * article actually exists. If the CMS has zero published articles (the
 * default, expected state until an admin publishes something), this
 * script does nothing at all and the 6 static cards remain exactly as
 * they are — same "only overwrite on full API success with non-empty
 * results" rule used by school-page.js's catalogue bridge.
 *
 * Each CMS-sourced card links to news-article.html?slug=<slug>, a new
 * minimal detail page (Step 7 CMS addition — no article detail page
 * existed anywhere in the project before this).
 */
(function () {
    if (!window.GermaineAPI) return;

    var FALLBACK_IMAGE = "assets/images/campus/classroom.jpg";

    function formatDate(iso) {
        if (!iso) return "";
        try {
            var d = new Date(iso);
            return d.toLocaleDateString("en-US", { month: "long", year: "numeric" });
        } catch (e) {
            return "";
        }
    }

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
    }

    function buildCard(article) {
        var img = article.featured_image_url || FALLBACK_IMAGE;
        var dateLabel = formatDate(article.published_at);
        var summary = article.summary || "";
        var href = "news-article.html?slug=" + encodeURIComponent(article.slug);

        return (
            '<article class="news-card">' +
            '<div class="news-image"><img src="' + escapeHtml(img) + '" alt="' + escapeHtml(article.title) + '" loading="lazy"></div>' +
            '<div class="news-content">' +
            (dateLabel ? '<span class="news-date"><i class="fa-solid fa-calendar"></i> ' + escapeHtml(dateLabel) + '</span>' : "") +
            "<h3>" + escapeHtml(article.title) + "</h3>" +
            (summary ? "<p>" + escapeHtml(summary) + "</p>" : "") +
            '<a href="' + href + '" class="news-link">Read More <i class="fa-solid fa-arrow-right"></i></a>' +
            "</div>" +
            "</article>"
        );
    }

    window.GermaineAPI.get("/api/news", { per_page: 6 }).then(function (res) {
        if (!res || !res.success || !res.data || !res.data.items || !res.data.items.length) return;
        var grid = document.getElementById("newsGrid");
        if (!grid) return;
        grid.innerHTML = res.data.items.map(buildCard).join("");
    }).catch(function () {
        // Silently keep the 6 existing static news cards.
    });
})();

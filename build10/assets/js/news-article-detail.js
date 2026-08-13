/*
 * News article detail page (Step 7 CMS addition).
 *
 * Reads ?slug=... from the URL, fetches GET /api/news/<slug>, and
 * populates this page. Shows a friendly "Article Not Found" state
 * (never a raw error) if the slug is missing, the article doesn't
 * exist, or it isn't published. This page only exists to give the CMS
 * News feature somewhere to link to — it renders CMS content
 * exclusively, there is no static fallback content here (unlike every
 * other bridge script in this project) because this page has no
 * pre-existing static content to fall back to.
 */
(function () {
    function showNotFound() {
        var loading = document.getElementById("articleLoadingState");
        var notFound = document.getElementById("articleNotFoundState");
        if (loading) loading.style.display = "none";
        if (notFound) notFound.style.display = "block";
    }

    function formatDate(iso) {
        if (!iso) return "";
        try {
            return new Date(iso).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
        } catch (e) {
            return "";
        }
    }

    function setMeta(selector, attr, value) {
        var el = document.querySelector(selector);
        if (el && value) el.setAttribute(attr, value);
    }

    function updateSeoTags(article, slug) {
        // This template serves every news article behind one static shell
        // (news-article.html), so the per-article <title>/description/
        // canonical/OG tags baked into that file are necessarily generic.
        // Once the real article loads, sharpen them to the specific
        // article — real data only, nothing invented — so search engines
        // and link previews (WhatsApp/Facebook/LinkedIn/X) describe the
        // actual article rather than the generic template text.
        var pageTitle = article.title + " | Germaine Training Institute News";
        document.title = pageTitle;
        setMeta('meta[name="description"]', "content", article.summary || article.title);
        setMeta('meta[property="og:title"]', "content", article.title);
        setMeta('meta[property="og:description"]', "content", article.summary || article.title);
        setMeta('meta[property="twitter:title"]', "content", article.title);
        setMeta('meta[name="twitter:title"]', "content", article.title);
        setMeta('meta[property="twitter:description"]', "content", article.summary || article.title);
        setMeta('meta[name="twitter:description"]', "content", article.summary || article.title);
        if (article.featured_image_url) {
            setMeta('meta[property="og:image"]', "content", article.featured_image_url);
            setMeta('meta[property="twitter:image"]', "content", article.featured_image_url);
            setMeta('meta[name="twitter:image"]', "content", article.featured_image_url);
        }
        var canonicalHref = window.location.origin + window.location.pathname + "?slug=" + encodeURIComponent(slug);
        setMeta('link[rel="canonical"]', "href", canonicalHref);
        setMeta('meta[property="og:url"]', "content", canonicalHref);
    }

    function renderArticle(article, slug) {
        document.getElementById("articleLoadingState").style.display = "none";
        document.getElementById("articleBody").style.display = "block";

        updateSeoTags(article, slug);
        document.getElementById("cmsArticleTitle").textContent = article.title;
        document.getElementById("cmsArticleBreadcrumb").textContent = article.title;

        if (article.category) {
            document.getElementById("cmsArticleCategory").textContent = article.category.toUpperCase();
        }

        var dateEl = document.getElementById("cmsArticleDate");
        var dateLabel = formatDate(article.published_at);
        if (dateLabel) {
            dateEl.innerHTML = '<i class="fa-solid fa-calendar"></i> ' + dateLabel;
        } else {
            dateEl.style.display = "none";
        }

        if (article.author) {
            var authorEl = document.getElementById("cmsArticleAuthor");
            // Phase 10 fix: this previously built the icon + author name via
            // innerHTML string concatenation, which injected the raw
            // admin-entered "author" field as unescaped HTML — a stored-XSS
            // vector (unlike every other field on this page, which already
            // used .textContent). Build the icon as a real element and set
            // the author name via .textContent so it can never be
            // interpreted as markup, no matter what an admin types in.
            authorEl.textContent = "";
            var authorIcon = document.createElement("i");
            authorIcon.className = "fa-solid fa-user";
            authorEl.appendChild(authorIcon);
            authorEl.appendChild(document.createTextNode(" " + article.author));
            authorEl.style.display = "inline";
        }

        if (article.summary) {
            document.getElementById("cmsArticleSummary").textContent = article.summary;
        }

        var bodyEl = document.getElementById("cmsArticleBodyText");
        if (article.body) {
            // Plain text only (never HTML) — split on blank lines into paragraphs.
            var paragraphs = article.body.split(/\n\s*\n/).map(function (p) { return p.trim(); }).filter(Boolean);
            paragraphs.forEach(function (p) {
                var el = document.createElement("p");
                el.textContent = p;
                el.style.marginBottom = "1em";
                bodyEl.appendChild(el);
            });
        }

        if (article.featured_image_url) {
            document.getElementById("cmsArticleImage").src = article.featured_image_url;
            document.getElementById("cmsArticleImage").alt = article.title;
        }
    }

    var params = new URLSearchParams(window.location.search);
    var slug = params.get("slug");

    if (!slug || !window.GermaineAPI) {
        showNotFound();
        return;
    }

    window.GermaineAPI.get("/api/news/" + encodeURIComponent(slug)).then(function (res) {
        if (!res || !res.success || !res.data) {
            showNotFound();
            return;
        }
        renderArticle(res.data, slug);
    }).catch(function () {
        showNotFound();
    });
})();

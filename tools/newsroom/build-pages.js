/*
 * Builds news.html, news-article.html and event.html from the site's own
 * news.html "shell" (head, header, navigation, footer kept byte-for-byte),
 * replacing only the <main> content, the page title/description meta, and
 * the page-specific CSS/JS tags.
 *
 * Runs in Node (staging: `node build-pages.js <shell.html> <outdir>`) and in
 * the browser (live deploy: window.NRBuild(shell, fragments)). Throws if any
 * anchor is missing or ambiguous, so it never writes a half-built page.
 */
(function (global) {
    "use strict";
    var VERSION = "20261122";
    var SITE = "https://germaineinstitute.ac.ke/";

    function once(str, needle, label) {
        var i = str.indexOf(needle);
        if (i < 0) throw new Error("anchor missing: " + label);
        if (str.indexOf(needle, i + 1) >= 0) throw new Error("anchor ambiguous: " + label);
        return i;
    }
    function replaceRe(str, re, repl, label) {
        var m = str.match(re);
        if (!m) throw new Error("pattern missing: " + label);
        return str.replace(re, repl);
    }
    function escAttr(s) { return s.replace(/&/g, "&amp;").replace(/"/g, "&quot;"); }

    function build(shell, kind, fragments) {
        var meta = {
            home: { file: "news.html", title: "News & Events | Germaine Training Institute",
                desc: "What's happening in Kenya and beyond: verified news summaries from trusted publishers, plus upcoming events, conferences, concerts and festivals." },
            article: { file: "news-article.html", title: "News | Germaine Training Institute",
                desc: "News summary from GTI News & Events, with a link to the original publisher." },
            event: { file: "event.html", title: "Event | Germaine Training Institute",
                desc: "Event details from GTI News & Events: dates, venue, organiser and official links." }
        }[kind];
        var html = shell;

        // 1. <main> content
        var mainOpen = once(html, '<main class="sp-page"', "main open");
        var mainClose = once(html, "</main>", "main close");
        var shine = '<div class="sp-bg-shine" aria-hidden="true"></div>';
        var keepEnd = html.indexOf(shine, mainOpen);
        if (keepEnd < 0 || keepEnd > mainClose) keepEnd = html.indexOf(">", mainOpen) + 1;
        else keepEnd += shine.length;
        var body = fragments[kind].replace("__HERO__", fragments.hero || "");
        html = html.slice(0, keepEnd) + "\n\n" + body + "\n\n" + html.slice(mainClose);

        // 2. title + meta
        html = replaceRe(html, /<title[^>]*>[\s\S]*?<\/title>/, "<title>\n        " + meta.title.replace(/&/g, "&amp;") + "\n    </title>", "title");
        html = replaceRe(html, /(<meta name="description"\s+content=")[^"]*(")/, "$1" + escAttr(meta.desc) + "$2", "meta description");
        html = html.replace(/(<meta property="og:title"\s+content=")[^"]*(")/, "$1" + escAttr(meta.title) + "$2")
                   .replace(/(<meta property="og:description"\s+content=")[^"]*(")/, "$1" + escAttr(meta.desc) + "$2")
                   .replace(/(<meta name="twitter:title" content=")[^"]*(")/, "$1" + escAttr(meta.title) + "$2")
                   .replace(/(<meta name="twitter:description" content=")[^"]*(")/, "$1" + escAttr(meta.desc) + "$2")
                   .replace(/(<meta property="og:url" content=")[^"]*(")/, "$1" + SITE + meta.file + "$2")
                   .replace(/(<link rel="canonical" href=")[^"]*(")/, "$1" + SITE + meta.file + "$2");

        // 3. page CSS (idempotent: drop any earlier newsroom tags first)
        html = html.replace(/[ \t]*<link[^>]*newsroom\.css[^>]*>\s*\n?/g, "")
                   .replace(/[ \t]*<script[^>]*newsroom\.js[^>]*><\/script>\s*\n?/g, "");
        once(html, "</head>", "head close");
        html = html.replace("</head>", '    <link rel="stylesheet" href="assets/css/newsroom.css?v=' + VERSION + '">\n</head>');

        // 4. page JS: drop the old static-news bridge, add the publication script
        html = html.replace(/[ \t]*<script[^>]*news-cms-bridge\.js[^>]*><\/script>\s*\n?/, "")
                   .replace(/[ \t]*<script[^>]*news-article-detail\.js[^>]*><\/script>\s*\n?/, "");
        once(html, "</body>", "body close");
        html = html.replace("</body>", '<script defer src="assets/js/newsroom.js?v=' + VERSION + '"></script>\n\n</body>');
        if (html.indexOf("api-client.js") < 0) throw new Error("api-client.js missing from shell");
        return { file: meta.file, html: html };
    }

    function buildAll(shell, fragments) {
        return ["home", "article", "event"].map(function (k) { return build(shell, k, fragments); });
    }

    global.NRBuild = buildAll;
    if (typeof module !== "undefined" && module.exports) {
        module.exports = buildAll;
        if (require.main === module) {
            var fs = require("fs"), path = require("path");
            var shellPath = process.argv[2], out = process.argv[3];
            var dir = __dirname, read = function (f) { return fs.readFileSync(path.join(dir, f), "utf8"); };
            var pages = buildAll(fs.readFileSync(shellPath, "utf8"),
                { hero: read("hero.html"), home: read("home.html"), article: read("article.html"), event: read("event.html") });
            pages.forEach(function (p) { fs.writeFileSync(path.join(out, p.file), p.html); console.log("wrote", p.file, p.html.length); });
        }
    }
})(typeof window !== "undefined" ? window : globalThis);

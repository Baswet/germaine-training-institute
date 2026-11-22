/*==================================================
  GTI NEWS & EVENTS — publication script (newsroom.js)

  One script for news.html, news-article.html and event.html.
  Everything comes from the backend (published content only):
    GET  /api/newsroom/home | /stories | /stories/<slug> | /events | /events/<slug> | /search
    POST /api/newsroom/stories/<slug>/view   (real read counter)

  Editorial rules enforced in the UI:
    - Sections with no real data are hidden (Breaking, Most Read, Watch…).
    - Every external story shows its original publisher and links out.
    - Event status comes from the server (computed from dates in EAT).
  All text is inserted with textContent / escaped — never raw HTML.
==================================================*/
(function () {
    "use strict";

    var root = document.querySelector("[data-nr-page]");
    if (!root || !window.GermaineAPI) return;
    var API = window.GermaineAPI;
    var PAGE = root.getAttribute("data-nr-page");
    var SITE = "https://germaineinstitute.ac.ke/";

    var CAT_ICONS = {
        kenya: "fa-flag", business: "fa-chart-line", world: "fa-earth-africa", sports: "fa-futbol",
        entertainment: "fa-music", technology: "fa-microchip", crime: "fa-scale-balanced",
        lifestyle: "fa-heart-pulse", education: "fa-graduation-cap", gti: "fa-school",
        conference: "fa-microphone-lines", concert: "fa-music", festival: "fa-champagne-glasses",
        exhibition: "fa-shop", workshop: "fa-screwdriver-wrench", career: "fa-briefcase",
        student: "fa-user-graduate", culture: "fa-masks-theater"
    };
    var EVENT_ART = { conference: "world", concert: "entertainment", festival: "entertainment", sports: "sports",
        technology: "technology", business: "business", exhibition: "business", workshop: "education",
        career: "education", student: "education", culture: "entertainment" };
    var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var LONG_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    var DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

    /* ---------------- helpers ---------------- */
    function esc(s) {
        return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
            return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
        });
    }
    function safeUrl(u) { return /^https?:\/\//i.test(u || "") ? u : null; }
    function $(id) { return document.getElementById(id); }
    function show(el, on) { if (el) el.classList.toggle("nr-hidden", !on); }
    function qs(name) { return new URLSearchParams(window.location.search).get(name); }
    function storyUrl(s) { return "news-article.html?slug=" + encodeURIComponent(s.slug); }
    function eventUrl(e) { return "event.html?slug=" + encodeURIComponent(e.slug); }
    function waLink(text, url) { return "https://wa.me/?text=" + encodeURIComponent(text + " " + url); }
    function parseDate(iso) { var p = iso.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }

    function timeAgo(iso) {
        if (!iso) return "";
        var d = new Date(iso), diff = (Date.now() - d.getTime()) / 1000;
        if (isNaN(diff)) return "";
        if (diff < 3600) return Math.max(1, Math.round(diff / 60)) + " min ago";
        if (diff < 86400) return Math.round(diff / 3600) + "h ago";
        if (diff < 7 * 86400) return Math.round(diff / 86400) + "d ago";
        return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "Africa/Nairobi" });
    }
    function fullDate(iso) {
        if (!iso) return "";
        return new Date(iso).toLocaleString("en-GB", { day: "numeric", month: "long", year: "numeric",
            hour: "2-digit", minute: "2-digit", timeZone: "Africa/Nairobi" }) + " EAT";
    }
    function eventDates(e) {
        var s = parseDate(e.start_date), en = parseDate(e.end_date);
        var fmt = function (d) { return d.getDate() + " " + MONTHS[d.getMonth()] + " " + d.getFullYear(); };
        if (e.start_date === e.end_date) return DOW[s.getDay()] + ", " + fmt(s);
        if (s.getMonth() === en.getMonth() && s.getFullYear() === en.getFullYear())
            return s.getDate() + "–" + en.getDate() + " " + MONTHS[s.getMonth()] + " " + s.getFullYear();
        return fmt(s) + " – " + fmt(en);
    }

    function art(cat, imageUrl, label, extraChip) {
        var img = imageUrl ? '<img src="' + esc(resolveMedia(imageUrl)) + '" alt="" loading="lazy">' : "";
        return '<span class="nr-art" data-cat="' + esc(cat || "gti") + '">' + img +
            (img ? "" : '<i class="fa-solid ' + (CAT_ICONS[cat] || "fa-newspaper") + ' nr-art-icon" aria-hidden="true"></i>') +
            '<span class="nr-art-cat">' + (label ? '<span class="nr-chip">' + esc(label) + "</span>" : "") +
            (extraChip || "") + "</span></span>";
    }
    function resolveMedia(url) { return /^https?:/i.test(url) ? url : API.BASE_URL + url; }

    function storyCard(s, variant) {
        var url = storyUrl(s);
        var shareUrl = SITE + url;
        return '<article class="nr-card ' + (variant || "") + '">' +
            art(s.category || "gti", s.image_url, s.category_label, s.is_breaking ? '<span class="nr-chip pink">Breaking</span>' : "") +
            '<div class="nr-card-body">' +
            '<h3><a href="' + url + '">' + esc(s.title) + "</a></h3>" +
            (variant === "nr-small" ? "" : "<p>" + esc(s.summary || "") + "</p>") +
            '<div class="nr-meta"><span class="nr-src">' + esc(s.source_name || "GTI") + "</span>" +
            "<span>" + esc(timeAgo(s.published_at)) + "</span>" +
            '<a class="nr-share-mini" href="' + waLink(s.title, shareUrl) + '" target="_blank" rel="noopener" aria-label="Share on WhatsApp"><i class="fa-brands fa-whatsapp"></i></a>' +
            "</div></div></article>";
    }

    function eventCard(e) {
        var d = parseDate(e.start_date);
        return '<article class="nr-event">' +
            '<span class="nr-dateblock" aria-hidden="true"><b>' + MONTHS[d.getMonth()] + "</b><strong>" + d.getDate() +
            "</strong><small>" + DOW[d.getDay()] + "</small></span>" +
            '<div class="nr-event-body"><span><span class="nr-status ' + esc(e.status) + '">' + esc(e.status) + "</span></span>" +
            '<h3><a href="' + eventUrl(e) + '">' + esc(e.title) + "</a></h3>" +
            '<div class="nr-meta"><span><i class="fa-regular fa-calendar"></i> ' + esc(eventDates(e)) + "</span>" +
            (e.venue || e.county ? '<span><i class="fa-solid fa-location-dot"></i> ' + esc([e.venue, e.county].filter(Boolean).join(", ")) + "</span>" : "") +
            "</div>" + (e.date_note ? '<div class="nr-meta"><span>' + esc(e.date_note) + "</span></div>" : "") +
            "</div></article>";
    }

    function eventFacts(e) {
        return '<ul class="nr-facts">' +
            '<li><i class="fa-regular fa-calendar"></i><span>' + esc(eventDates(e)) + (e.date_note ? " · " + esc(e.date_note) : "") + "</span></li>" +
            (e.start_time ? '<li><i class="fa-regular fa-clock"></i><span>' + esc(e.start_time) + "</span></li>" : "") +
            (e.venue || e.county ? '<li><i class="fa-solid fa-location-dot"></i><span>' + esc([e.venue, e.county].filter(Boolean).join(", ")) + "</span></li>" : "") +
            '<li><i class="fa-solid fa-users"></i><span>Organised by ' + esc(e.organizer) + "</span></li></ul>";
    }

    function revealHero() {
        Array.prototype.forEach.call(document.querySelectorAll(".nr-page .gh-reveal"), function (el) {
            requestAnimationFrame(function () { el.classList.add("in"); });
        });
    }

    /* ================================================================
       NEWS & EVENTS HOME
       ================================================================ */
    function initHome() {
        var state = { category: "", page: 1, latestEvents: [], monthCursor: null, selected: null };

        API.get("/api/newsroom/home").then(function (res) {
            if (!res.success || !res.data) {
                $("nrLatestList").innerHTML = '<div class="nr-empty">News is temporarily unavailable. Please try again shortly.</div>';
                return;
            }
            var d = res.data;

            // Breaking — only genuine, editor-flagged items
            if (d.breaking.length) {
                $("nrBreaking").innerHTML = '<span class="nr-breaking-label">BREAKING</span><a href="' + storyUrl(d.breaking[0]) + '">' + esc(d.breaking[0].title) + "</a>";
                show($("nrBreaking"), true);
            }
            // Trending
            if (d.trending.length) {
                $("nrTrendingTrack").innerHTML = d.trending.map(function (s, i) {
                    return '<a href="' + storyUrl(s) + '" title="' + esc(s.trending_note || "") + '"><b>' + (i + 1) + "</b><span>" + esc(s.title) + "</span></a>";
                }).join("");
                show($("nrTrending"), true);
            }
            // Featured mosaic: 1 large + 2 medium + 2 small
            if (d.lead) {
                var t = d.top_stories;
                $("nrMosaic").innerHTML = storyCard(d.lead, "nr-lead") +
                    (t[0] ? storyCard(t[0], "nr-medium") : "") + (t[1] ? storyCard(t[1], "nr-medium") : "") +
                    (t[2] ? storyCard(t[2], "nr-small") : "") + (t[3] ? storyCard(t[3], "nr-small") : "");
                show($("nrFeatured"), true);
            }
            // Latest
            renderFilters(d.categories);
            renderLatest(d.latest, d.latest_total > d.latest.length, false);
            // Daily brief
            if (d.daily_brief.length) {
                $("nrBrief").innerHTML = d.daily_brief.map(function (s) {
                    return '<li><a href="' + storyUrl(s) + '">' + esc(s.title) + "<small>" + esc(s.source_name || "") + " · " + esc(timeAgo(s.published_at)) + "</small></a></li>";
                }).join("");
                $("nrBriefDate").textContent = new Date().toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", timeZone: "Africa/Nairobi" });
                show($("nrBriefPanel"), true);
            }
            // Most read — real counts only
            if (d.most_read.length) {
                $("nrMostRead").innerHTML = d.most_read.map(function (s) {
                    return '<li><a href="' + storyUrl(s) + '">' + esc(s.title) + "<small>" + esc(s.source_name || "") + "</small></a></li>";
                }).join("");
                show($("nrMostReadPanel"), true);
            }
            // Categories
            $("nrCats").innerHTML = d.categories.map(function (c) {
                return '<button type="button" class="nr-cat nr-art" data-cat="' + esc(c.key) + '" data-filter="' + esc(c.key) + '">' +
                    '<i class="fa-solid ' + (CAT_ICONS[c.key] || "fa-newspaper") + ' nr-art-icon" aria-hidden="true"></i>' +
                    "<strong>" + esc(c.label) + "</strong><span>" + c.count + (c.count === 1 ? " story" : " stories") + "</span></button>";
            }).join("");
            // Watch — only verified videos
            if (d.watch.length) {
                $("nrWatchRail").innerHTML = d.watch.map(videoCard).join("");
                show($("nrWatch"), true);
            }
            // Editor's picks
            if (d.editors_picks.length) {
                $("nrPicksRail").innerHTML = d.editors_picks.map(function (s) { return storyCard(s); }).join("");
                show($("nrPicks"), true);
            }
            // GTI institutional updates
            if (d.gti_updates.length) {
                $("nrGtiGrid").innerHTML = d.gti_updates.map(function (s) { return storyCard(s, "nr-small"); }).join("");
                show($("nrGti"), true);
            }
            renderEvents(d.events);
            loadOpportunities();
        });

        function renderFilters(cats) {
            var html = '<button type="button" data-filter="" aria-pressed="true">All</button>' +
                cats.filter(function (c) { return c.count > 0; }).map(function (c) {
                    return '<button type="button" data-filter="' + esc(c.key) + '" aria-pressed="false">' + esc(c.label) + "</button>";
                }).join("");
            $("nrFilters").innerHTML = html;
        }

        function renderLatest(items, hasMore, append) {
            var list = $("nrLatestList");
            var html = items.map(function (s) { return storyCard(s); }).join("");
            if (append) list.insertAdjacentHTML("beforeend", html);
            else list.innerHTML = html || '<div class="nr-empty">No stories in this category yet.</div>';
            show($("nrMore"), hasMore);
        }

        function loadLatest(append) {
            var btn = $("nrMoreBtn");
            btn.disabled = true;
            API.get("/api/newsroom/stories", { category: state.category || undefined, page: state.page, per_page: 12 }).then(function (res) {
                btn.disabled = false;
                if (!res.success) return;
                renderLatest(res.data.items, res.data.has_more, append);
            });
        }

        function setCategory(key) {
            state.category = key; state.page = 1;
            Array.prototype.forEach.call($("nrFilters").querySelectorAll("button"), function (b) {
                b.setAttribute("aria-pressed", String(b.getAttribute("data-filter") === key));
            });
            loadLatest(false);
        }

        document.addEventListener("click", function (ev) {
            var f = ev.target.closest("[data-filter]");
            if (f && root.contains(f)) {
                setCategory(f.getAttribute("data-filter"));
                if (f.classList.contains("nr-cat")) $("nr-latest").scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
        $("nrMoreBtn").addEventListener("click", function () { state.page += 1; loadLatest(true); });

        /* ---- search ---- */
        var timer = null, input = $("nrSearch");
        input.addEventListener("input", function () {
            clearTimeout(timer);
            var q = input.value.trim();
            if (q.length < 2) { show($("nrSearchResults"), false); return; }
            timer = setTimeout(function () {
                API.get("/api/newsroom/search", { q: q }).then(function (res) {
                    if (!res.success || input.value.trim() !== q) return;
                    var s = res.data.stories, e = res.data.events, box = $("nrSearchResults");
                    box.innerHTML = (s.length ? "<h3>Stories</h3><ul>" + s.map(function (x) {
                        return '<li><a href="' + storyUrl(x) + '">' + esc(x.title) + "<span>" + esc(x.category_label || "") + " · " + esc(x.source_name || "") + "</span></a></li>";
                    }).join("") + "</ul>" : "") + (e.length ? "<h3>Events</h3><ul>" + e.map(function (x) {
                        return '<li><a href="' + eventUrl(x) + '">' + esc(x.title) + "<span>" + esc(eventDates(x)) + " · " + esc(x.county || "") + "</span></a></li>";
                    }).join("") + "</ul>" : "") + (!s.length && !e.length ? '<div class="nr-empty">No stories or events match “' + esc(q) + "”.</div>" : "");
                    show(box, true);
                });
            }, 250);
        });
        input.closest("form").addEventListener("submit", function (ev) { ev.preventDefault(); });

        /* ---- opportunities (education & opportunities category) ---- */
        function loadOpportunities() {
            API.get("/api/newsroom/stories", { category: "education", per_page: 6 }).then(function (res) {
                if (!res.success || !res.data.items.length) return;
                $("nrOppRail").innerHTML = res.data.items.map(function (s) { return storyCard(s); }).join("");
                show($("nrOpp"), true);
            });
        }

        /* ---- events ---- */
        function renderEvents(ev) {
            if (ev.featured) {
                var e = ev.featured, reg = safeUrl(e.registration_url), src = safeUrl(e.source_url);
                $("nrFeatureEvent").innerHTML = '<div class="nr-feature-event">' +
                    art(EVENT_ART[e.category] || "gti", e.image_url, e.category_label, '<span class="nr-chip">Featured</span>') +
                    '<div class="nr-feature-event-body"><span><span class="nr-status ' + esc(e.status) + '">' + esc(e.status) + "</span></span>" +
                    "<h3>" + esc(e.title) + "</h3>" + (e.description ? '<p class="nr-sub">' + esc(e.description) + "</p>" : "") +
                    eventFacts(e) + '<div class="nr-actions">' +
                    '<a class="nr-btn pink" href="' + eventUrl(e) + '">Event details <i class="fa-solid fa-arrow-right"></i></a>' +
                    (reg ? '<a class="nr-btn" href="' + esc(reg) + '" target="_blank" rel="noopener">Register</a>' : (src ? '<a class="nr-btn" href="' + esc(src) + '" target="_blank" rel="noopener">Official page</a>' : "")) +
                    "</div></div></div>";
            }
            state.latestEvents = ev.upcoming;
            $("nrCounty").innerHTML = '<option value="">All counties</option>' + ev.counties.map(function (c) {
                return '<option value="' + esc(c) + '">' + esc(c) + "</option>";
            }).join("");
            drawEventGrid(ev.upcoming);

            var fri = parseDate(ev.weekend_range[0]), sun = parseDate(ev.weekend_range[1]);
            $("nrWeekendRange").textContent = fri.getDate() + " " + MONTHS[fri.getMonth()] + " – " + sun.getDate() + " " + MONTHS[sun.getMonth()];
            $("nrWeekendList").innerHTML = ev.weekend.length ? ev.weekend.map(function (e) {
                return '<li><a href="' + eventUrl(e) + '"><b>' + esc(e.status === "ongoing" ? "On now" : DOW[parseDate(e.start_date).getDay()]) + "</b><span>" +
                    esc(e.title) + "<small>" + esc([e.venue, e.county].filter(Boolean).join(", ")) + "</small></span></a></li>";
            }).join("") : '<li><span style="opacity:.8">No listed events this weekend yet — check the calendar for what’s next.</span></li>';

            var now = new Date();
            state.monthCursor = new Date(now.getFullYear(), now.getMonth(), 1);
            loadMonth();
        }

        function drawEventGrid(items) {
            $("nrEventsGrid").innerHTML = items.length ? items.map(eventCard).join("") :
                '<div class="nr-empty">No upcoming events match these filters.</div>';
        }
        function filterEvents() {
            var county = $("nrCounty").value, cat = $("nrEventCat").value;
            var params = { county: county || undefined, category: cat || undefined };
            API.get("/api/newsroom/events", params).then(function (res) { if (res.success) drawEventGrid(res.data.items); });
        }
        $("nrCounty").addEventListener("change", filterEvents);
        $("nrEventCat").addEventListener("change", filterEvents);

        function ymd(d) { return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }
        function loadMonth() {
            var c = state.monthCursor;
            $("nrCalMonth").textContent = LONG_MONTHS[c.getMonth()] + " " + c.getFullYear();
            API.get("/api/newsroom/events", { month: c.getFullYear() + "-" + String(c.getMonth() + 1).padStart(2, "0") }).then(function (res) {
                drawCalendar(res.success ? res.data.items : []);
            });
        }
        function drawCalendar(items) {
            var c = state.monthCursor, first = new Date(c.getFullYear(), c.getMonth(), 1);
            var days = new Date(c.getFullYear(), c.getMonth() + 1, 0).getDate();
            var today = ymd(new Date()), byDay = {};
            items.forEach(function (e) {
                for (var d = parseDate(e.start_date); ymd(d) <= e.end_date; d.setDate(d.getDate() + 1)) {
                    (byDay[ymd(d)] = byDay[ymd(d)] || []).push(e);
                }
            });
            var html = DOW.map(function (d) { return '<span class="dow">' + d.charAt(0) + d.charAt(1) + "</span>"; }).join("");
            for (var i = 0; i < first.getDay(); i++) html += "<span></span>";
            for (var n = 1; n <= days; n++) {
                var key = ymd(new Date(c.getFullYear(), c.getMonth(), n)), has = byDay[key];
                html += '<button type="button" data-day="' + key + '" class="' + (has ? "has " : "") + (key === today ? "today " : "") +
                    (key === state.selected ? "sel" : "") + '"' + (has ? ' aria-label="' + n + ", " + has.length + ' event(s)"' : " tabindex=\"-1\" aria-hidden=\"true\"") + ">" + n + "</button>";
            }
            $("nrCalGrid").innerHTML = html;
            state.byDay = byDay;
            var list = state.selected && byDay[state.selected] ? byDay[state.selected] : items;
            $("nrCalList").innerHTML = list.length ? list.slice(0, 6).map(function (e) {
                return '<a href="' + eventUrl(e) + '">' + esc(e.title) + "<small>" + esc(eventDates(e)) + "</small></a>";
            }).join("") : '<div class="nr-empty">No listed events this month.</div>';
        }
        $("nrCalGrid").addEventListener("click", function (ev) {
            var b = ev.target.closest("button.has");
            if (!b) return;
            state.selected = state.selected === b.getAttribute("data-day") ? null : b.getAttribute("data-day");
            loadMonth();
        });
        $("nrCalPrev").addEventListener("click", function () { state.monthCursor.setMonth(state.monthCursor.getMonth() - 1); state.selected = null; loadMonth(); });
        $("nrCalNext").addEventListener("click", function () { state.monthCursor.setMonth(state.monthCursor.getMonth() + 1); state.selected = null; loadMonth(); });

        if (window.location.hash) {
            setTimeout(function () { var t = document.querySelector(window.location.hash); if (t) t.scrollIntoView(); }, 600);
        }
    }

    function videoCard(s) {
        var id = s.video_id;
        return '<article class="nr-card"><div class="nr-video"><button type="button" data-yt="' + esc(id) + '" aria-label="Play video: ' + esc(s.title) + '" style="background-image:url(https://i.ytimg.com/vi/' + esc(id) + '/hqdefault.jpg)"><i class="fa-solid fa-circle-play"></i></button></div>' +
            '<div class="nr-card-body"><h3><a href="' + storyUrl(s) + '">' + esc(s.title) + "</a></h3>" +
            '<div class="nr-meta"><span class="nr-src">' + esc(s.source_name || "") + "</span>" + (s.video_duration ? "<span>" + esc(s.video_duration) + "</span>" : "") + "</div></div></article>";
    }
    document.addEventListener("click", function (ev) {
        var b = ev.target.closest("button[data-yt]");
        if (!b) return;
        var id = b.getAttribute("data-yt");
        if (!/^[A-Za-z0-9_-]{6,20}$/.test(id)) return;
        var f = document.createElement("iframe");
        f.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1";
        f.title = b.getAttribute("aria-label") || "Video";
        f.allow = "autoplay; encrypted-media; picture-in-picture";
        f.allowFullscreen = true;
        b.replaceWith(f);
    });

    /* ================================================================
       SHARE BAR (article + event)
       ================================================================ */
    function shareBar(title) {
        var url = window.location.href;
        return '<div class="nr-share"><span>Share</span>' +
            '<a class="wa" href="' + waLink(title, url) + '" target="_blank" rel="noopener" aria-label="Share on WhatsApp"><i class="fa-brands fa-whatsapp"></i></a>' +
            '<a href="https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url) + '" target="_blank" rel="noopener" aria-label="Share on Facebook"><i class="fa-brands fa-facebook-f"></i></a>' +
            '<a href="https://x.com/intent/post?text=' + encodeURIComponent(title) + "&url=" + encodeURIComponent(url) + '" target="_blank" rel="noopener" aria-label="Share on X"><i class="fa-brands fa-x-twitter"></i></a>' +
            '<button type="button" data-copy aria-label="Copy link"><i class="fa-solid fa-link"></i></button>' +
            (navigator.share ? '<button type="button" data-native-share aria-label="More sharing options"><i class="fa-solid fa-share-nodes"></i></button>' : "") +
            "</div>";
    }
    document.addEventListener("click", function (ev) {
        var c = ev.target.closest("[data-copy]");
        if (c) {
            (navigator.clipboard ? navigator.clipboard.writeText(window.location.href) : Promise.reject()).then(function () {
                c.innerHTML = '<i class="fa-solid fa-check"></i>';
                setTimeout(function () { c.innerHTML = '<i class="fa-solid fa-link"></i>'; }, 1600);
            }).catch(function () {});
        }
        var n = ev.target.closest("[data-native-share]");
        if (n) navigator.share({ title: document.title, url: window.location.href }).catch(function () {});
    });

    function setMeta(title, description) {
        document.title = title + " | GTI News & Events";
        var m = document.querySelector('meta[name="description"]');
        if (m && description) m.setAttribute("content", description);
    }

    /* ================================================================
       ARTICLE PAGE
       ================================================================ */
    function initArticle() {
        var slug = qs("slug"), box = $("nrArticle");
        if (!slug) { box.innerHTML = '<div class="nr-empty">Story not found. <a href="news.html">Back to News &amp; Events</a></div>'; return; }
        API.get("/api/newsroom/stories/" + encodeURIComponent(slug)).then(function (res) {
            if (!res.success) {
                box.innerHTML = '<div class="nr-empty">This story is not available. <a href="news.html">Back to News &amp; Events</a></div>';
                return;
            }
            var s = res.data, src = safeUrl(s.source_url);
            setMeta(s.title, s.summary);
            var lines = (s.body || "").split(/\n+/).map(function (l) { return l.trim(); }).filter(Boolean);
            var bodyHtml = "";
            if (s.is_external) {
                if (lines.length > 1 || (lines[0] && lines[0] !== (s.summary || "").trim()))
                    bodyHtml = '<h2 class="nr-kicker">Key points</h2><ul class="nr-points">' + lines.map(function (l) { return "<li>" + esc(l) + "</li>"; }).join("") + "</ul>";
            } else {
                bodyHtml = '<div class="nr-body">' + lines.map(function (l) { return "<p>" + esc(l) + "</p>"; }).join("") + "</div>";
            }
            box.innerHTML =
                '<nav class="nr-crumb" aria-label="Breadcrumb"><a href="news.html">News &amp; Events</a><span>/</span><span>' + esc(s.category_label || "News") + "</span></nav>" +
                '<span class="nr-chip soft">' + esc(s.category_label || "News") + "</span>" + (s.is_breaking ? ' <span class="nr-chip pink">Breaking</span>' : "") +
                "<h1>" + esc(s.title) + "</h1>" +
                (s.summary ? '<p class="nr-lede">' + esc(s.summary) + "</p>" : "") +
                '<div class="nr-byline">' + (s.is_external ? "<span>Source: <b>" + esc(s.source_name) + "</b></span>" : "<span><b>Germaine Training Institute</b></span>") +
                (s.author ? "<span>Reporter: " + esc(s.author) + "</span>" : "") +
                (s.published_at ? "<span>" + (s.is_external ? "Originally published " : "Published ") + esc(fullDate(s.published_at)) + "</span>" : "") +
                (s.is_external ? "<span>Summary by GTI News &amp; Events</span>" : "") + "</div>" +
                art(s.category || "gti", s.image_url, "") +
                (s.image_credit ? '<p class="nr-credit">Image: ' + esc(s.image_credit) + "</p>" : '<p class="nr-credit"></p>') +
                (s.video_id ? '<div class="nr-video" style="margin-bottom:20px"><button type="button" data-yt="' + esc(s.video_id) + '" aria-label="Play video" style="background-image:url(https://i.ytimg.com/vi/' + esc(s.video_id) + '/hqdefault.jpg)"><i class="fa-solid fa-circle-play"></i></button></div>' : "") +
                bodyHtml +
                (s.is_external && src ? '<div class="nr-source-box"><p>This is a short summary written by GTI. Read the full, original report from ' + esc(s.source_name) + ".</p>" +
                    '<a class="nr-btn pink" href="' + esc(src) + '" target="_blank" rel="noopener">Read the full story on ' + esc(s.source_name) + ' <i class="fa-solid fa-arrow-up-right-from-square"></i></a></div>' : "") +
                shareBar(s.title);
            if (s.related && s.related.length) {
                $("nrRelatedGrid").innerHTML = s.related.map(function (r) { return storyCard(r, "nr-small"); }).join("");
                show($("nrRelated"), true);
            }
            try {
                var key = "nr-read-" + s.slug;
                if (!window.sessionStorage.getItem(key)) {
                    window.sessionStorage.setItem(key, "1");
                    API.post("/api/newsroom/stories/" + encodeURIComponent(s.slug) + "/view", {});
                }
            } catch (e) { /* storage unavailable: skip counting */ }
        });
    }

    /* ================================================================
       EVENT PAGE
       ================================================================ */
    function icsFor(e) {
        var end = parseDate(e.end_date); end.setDate(end.getDate() + 1);
        var d = function (x) { return x.replace(/-/g, ""); };
        var endStr = end.getFullYear() + String(end.getMonth() + 1).padStart(2, "0") + String(end.getDate()).padStart(2, "0");
        var clean = function (s) { return String(s || "").replace(/[\r\n]+/g, " ").replace(/([,;\\])/g, "\\$1"); };
        return ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Germaine Training Institute//News & Events//EN", "BEGIN:VEVENT",
            "UID:" + e.slug + "@germaineinstitute.ac.ke", "DTSTART;VALUE=DATE:" + d(e.start_date), "DTEND;VALUE=DATE:" + endStr,
            "SUMMARY:" + clean(e.title), "LOCATION:" + clean([e.venue, e.county].filter(Boolean).join(", ")),
            "DESCRIPTION:" + clean((e.description || "") + " " + (e.source_url || "")), "END:VEVENT", "END:VCALENDAR"].join("\r\n");
    }
    function initEvent() {
        var slug = qs("slug"), box = $("nrEvent");
        if (!slug) { box.innerHTML = '<div class="nr-empty">Event not found. <a href="news.html#nr-events">Browse events</a></div>'; return; }
        API.get("/api/newsroom/events/" + encodeURIComponent(slug)).then(function (res) {
            if (!res.success) { box.innerHTML = '<div class="nr-empty">This event is not available. <a href="news.html#nr-events">Browse events</a></div>'; return; }
            var e = res.data, reg = safeUrl(e.registration_url), src = safeUrl(e.source_url), d = parseDate(e.start_date);
            setMeta(e.title, e.description);
            box.innerHTML =
                '<nav class="nr-crumb" aria-label="Breadcrumb"><a href="news.html#nr-events">Events</a><span>/</span><span>' + esc(e.category_label) + "</span></nav>" +
                '<div class="nr-event-hero"><span class="nr-dateblock" aria-hidden="true"><b>' + MONTHS[d.getMonth()] + "</b><strong>" + d.getDate() + "</strong><small>" + DOW[d.getDay()] + "</small></span>" +
                '<div><span class="nr-status ' + esc(e.status) + '">' + esc(e.status) + '</span> <span class="nr-chip soft">' + esc(e.category_label) + "</span>" +
                "<h1>" + esc(e.title) + "</h1></div></div>" +
                art(EVENT_ART[e.category] || "gti", e.image_url, "") + '<p class="nr-credit"></p>' +
                (e.description ? '<p class="nr-lede">' + esc(e.description) + "</p>" : "") +
                eventFacts(e) +
                '<div class="nr-actions" style="margin-top:22px">' +
                (reg && e.status !== "completed" ? '<a class="nr-btn pink" href="' + esc(reg) + '" target="_blank" rel="noopener">Register / tickets <i class="fa-solid fa-arrow-up-right-from-square"></i></a>' : "") +
                (src ? '<a class="nr-btn" href="' + esc(src) + '" target="_blank" rel="noopener">Official event page</a>' : "") +
                (e.status !== "completed" ? '<button type="button" class="nr-btn" id="nrIcs"><i class="fa-regular fa-calendar-plus"></i> Add to calendar</button>' : "") +
                "</div>" +
                '<p class="nr-credit" style="margin-top:14px">Details are taken from the organiser’s official page. Please confirm times and entry requirements with the organiser before attending.</p>' +
                shareBar(e.title + " — " + eventDates(e));
            var ics = $("nrIcs");
            if (ics) ics.addEventListener("click", function () {
                var a = document.createElement("a");
                a.href = URL.createObjectURL(new Blob([icsFor(e)], { type: "text/calendar" }));
                a.download = e.slug + ".ics";
                document.body.appendChild(a); a.click(); a.remove();
            });
            API.get("/api/newsroom/events").then(function (r) {
                if (!r.success) return;
                var more = r.data.items.filter(function (x) { return x.slug !== e.slug; }).slice(0, 3);
                if (!more.length) return;
                $("nrRelatedGrid").innerHTML = more.map(eventCard).join("");
                show($("nrRelated"), true);
            });
        });
    }

    revealHero();
    if (PAGE === "home") initHome();
    else if (PAGE === "article") initArticle();
    else if (PAGE === "event") initEvent();
})();

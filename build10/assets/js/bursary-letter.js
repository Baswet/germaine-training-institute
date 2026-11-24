/*=========================================================
  GERMAINE TRAINING INSTITUTE
  BURSARY RECOMMENDATION LETTER  (page 2 of the Full Scholarship document)

  Digital recreation of the Institute's official bursary letter
  (Bursary_letter_2026.doc) on the GTI letterhead. Wording is reproduced
  as issued; the letter carries no date (removed at the owner's request).

  Filled from the saved application only:
    student name   -> "REF: Bursary Application for ..."
    programme      -> "... leading to the award of <level> in <course>"
  Everything else (NG-CDF / NGAAF / County committee / Chief lines) stays
  as dotted blanks for the student and the Chief to complete.

  SIGNATURE - reuses the Chief Principal's existing signature asset
  (assets/images/logo/signature-chief-principal.png, the same file the
  admission letter uses), unchanged in colour and proportion. Drawn on
  every copy, exactly like page 1 (the institute's decision, 24 Nov 2026).
  If the image cannot load, a clear space is left for a wet signature.

  "Other Funding Organizations" line: added from the institute's revised
  letter (Bursary_letter_2__2026.doc, the line marked in red).

  INTEGRATION - additive. apply-acknowledgement.js calls
    window.GTIBursaryLetter.addTo(doc, app)  -> after page 1 is drawn
    window.GTIBursaryLetter.html(app)        -> on-screen copy in the modal
  If this file is absent, the Full Scholarship document is exactly as before.
=========================================================*/
(function () {
    "use strict";

    var CREST_SRC = "assets/images/logo/logo.jpg";
    var SIGNATURE_SRC = "assets/images/logo/signature-chief-principal.png";
    var AUTHORISED = true;   /* signed on every copy, like the admission letter (owner decision) */

    var TEXT = {
        to: "To",
        addressees: [
            "National Government Constituency development Fund (NG-CDF)",
            "National Government Affirmative Action Fund (NGAAF)",
            "County Bursary Committee (County & Ward)",
            "Other Funding Organizations"
        ],
        thro: "Thro!",
        chief: "Chief/Sub-Chief (Location/Sub-location)",
        chiefNote: "(Chief/Sub-Chief to sign and stamp)",
        ref: "REF: Bursary Application for ",
        p1: "This is to bring to your attention that the above named person is a student at Germaine Training Institute.",
        p2: "He/she is studying a course leading to the award of {AWARD} in",
        p3: "He/she have indicated that is facing financial difficulties in meeting the tuition fee. This letter is to " +
            "kindly request you to facilitate the holder apply for bursary. For any clarifications or for further " +
            "details do not hesitate to contact the undersigned.",
        closing: "Yours faithfully,",
        signName: "Mr. Douglas Onsare",
        signTitle: "Chief Principal",
        reg: "REGISTERED AND LICENCED Reg No. TVETA/TVC/0029/2020",
        footer: [
            ["Pioneer Plaza 3rd Floor Opp.", "Mosque, Mburu Gichua Road,", "Nakuru City"],
            ["+254 719 488 112", "+254 102 010 874"],
            ["P.O. Box 12290-20100", "Nakuru"],
            ["germainetraininginstitute", "@gmail.com", "www.germaineinstitute.com"]
        ]
    };
    var LEVELS = ["Diploma", "Certificate", "Artisan"];

    var NAVY = [27, 46, 107], RED = [200, 27, 62], GREY = [115, 120, 133], INK = [20, 20, 26];

    /* ---------------- data ---------------- */
    function titleCase(name) {
        name = String(name || "").trim();
        if (!name || name !== name.toUpperCase()) return name;
        return name.toLowerCase().replace(/(^|[\s'\-])([a-z])/g, function (m, a, b) { return a + b.toUpperCase(); });
    }

    /* "Diploma in Information Communication Technology" -> Diploma + course.
       Anything else keeps the letter's own "Diploma/Certificate/Artisan" wording. */
    function splitProgramme(programme) {
        var p = String(programme || "").trim();
        for (var i = 0; i < LEVELS.length; i++) {
            var re = new RegExp("^" + LEVELS[i] + "\\s+(in|of)\\s+(.+)$", "i");
            var m = p.match(re);
            if (m) return { award: LEVELS[i], course: m[2].trim() };
        }
        return { award: "Diploma/Certificate/Artisan", course: p };
    }

    function fields(app) {
        app = app || {};
        var sp = splitProgramme(app.programme);
        return { name: titleCase(app.fullName), award: sp.award, course: sp.course, ref: String(app.reference || "").trim() };
    }

    /* ---------------- crest: the GTI logo without its outer ring ---------------- */
    var crestPromise = null;
    function crest() {
        if (crestPromise) return crestPromise;
        crestPromise = new Promise(function (resolve) {
            var img = new Image();
            img.onload = function () {
                try {
                    var W = img.naturalWidth, H = img.naturalHeight;
                    var c = document.createElement("canvas");
                    c.width = W; c.height = H;
                    var x = c.getContext("2d");
                    x.fillStyle = "#fff"; x.fillRect(0, 0, W, H);
                    x.drawImage(img, 0, 0);
                    var d = x.getImageData(0, 0, W, H), px = d.data;
                    var cx = W * 0.4983, cy = H * 0.5, rx = W * 0.4017, ry = H * 0.4321;
                    var minX = W, minY = H, maxX = 0, maxY = 0;
                    for (var yy = 0; yy < H; yy++) {
                        for (var xx = 0; xx < W; xx++) {
                            var i = (yy * W + xx) * 4;
                            var e = Math.pow((xx - cx) / rx, 2) + Math.pow((yy - cy) / ry, 2);
                            var r = px[i], g = px[i + 1], b = px[i + 2];
                            var nearWhite = Math.min(r, g, b) > 228 && Math.max(r, g, b) - Math.min(r, g, b) < 20;
                            if (e >= 0.93 || nearWhite) { px[i] = px[i + 1] = px[i + 2] = 255; continue; }
                            if (xx < minX) minX = xx; if (xx > maxX) maxX = xx;
                            if (yy < minY) minY = yy; if (yy > maxY) maxY = yy;
                        }
                    }
                    x.putImageData(d, 0, 0);
                    var cw = maxX - minX + 5, ch = maxY - minY + 5;
                    var o = document.createElement("canvas");
                    o.width = cw * 2; o.height = ch * 2;
                    var ox = o.getContext("2d");
                    ox.imageSmoothingQuality = "high";
                    ox.fillStyle = "#fff"; ox.fillRect(0, 0, o.width, o.height);
                    ox.drawImage(c, minX - 2, minY - 2, cw, ch, 0, 0, o.width, o.height);
                    resolve({ url: o.toDataURL("image/jpeg", 0.92), w: o.width, h: o.height });
                } catch (err) { resolve(null); }
            };
            img.onerror = function () { resolve(null); };
            img.src = CREST_SRC;
        });
        return crestPromise;
    }

    /* ---------------- signature: the existing asset, drawn onto white ---------------- */
    var signPromise = null;
    function signature() {
        if (!AUTHORISED) return Promise.resolve(null);
        if (signPromise) return signPromise;
        signPromise = new Promise(function (resolve) {
            var img = new Image();
            img.onload = function () {
                try {
                    var c = document.createElement("canvas");
                    c.width = img.naturalWidth; c.height = img.naturalHeight;
                    var x = c.getContext("2d");
                    x.fillStyle = "#ffffff"; x.fillRect(0, 0, c.width, c.height);
                    x.drawImage(img, 0, 0);
                    resolve({ url: c.toDataURL("image/jpeg", 0.92), w: img.naturalWidth, h: img.naturalHeight });
                } catch (e) { resolve(null); }
            };
            img.onerror = function () { resolve(null); };
            img.src = SIGNATURE_SRC;
        });
        return signPromise;
    }

    /* ---------------- PDF page (jsPDF, A4 portrait, points) ---------------- */
    function drawPage(doc, f, cr, sign) {
        var PW = 595.28, PH = 841.89, L = 72, R = PW - 66, cx = PW / 2;
        function col(c) { doc.setTextColor(c[0], c[1], c[2]); }
        function times(style, size) { doc.setFont("times", style).setFontSize(size); }
        function dots(x1, x2, y) {
            if (x2 - x1 < 6) return;
            doc.setDrawColor(60, 60, 70).setLineWidth(0.9);
            doc.setLineDashPattern([0.8, 2.6], 0);
            doc.line(x1, y + 1, x2, y + 1);
            doc.setLineDashPattern([], 0);
        }
        function para(text, y, lead, justify) {
            times("normal", 11.5); col(INK);
            var lines = doc.splitTextToSize(text, R - L);
            for (var i = 0; i < lines.length; i++) {
                var last = i === lines.length - 1;
                doc.text(lines[i], L, y, (justify && !last) ? { align: "justify", maxWidth: R - L } : undefined);
                y += lead;
            }
            return y;
        }

        doc.addPage("a4", "portrait");

        /* letterhead */
        var cw = 96, ch = cr ? cw * cr.h / cr.w : 0, top = 22;
        if (cr) doc.addImage(cr.url, "JPEG", cx - cw / 2, top, cw, ch);
        var base = top + (ch || 88) * 0.52;
        doc.setFont("helvetica", "bold").setFontSize(25); col(NAVY);
        doc.text("GERMAINE", cx - cw / 2 - 8, base, { align: "right" });
        doc.text("INSTITUTE", cx + cw / 2 + 8, base);
        doc.setDrawColor(RED[0], RED[1], RED[2]).setLineWidth(1.6);
        doc.line(40, base + 12, cx - cw / 2 - 4, base + 12);
        doc.line(cx + cw / 2 + 4, base + 12, PW - 40, base + 12);

        /* faint crest watermark */
        if (cr && doc.GState) {
            doc.saveGraphicsState();
            doc.setGState(new doc.GState({ opacity: 0.07 }));
            var ww = 190;
            doc.addImage(cr.url, "JPEG", cx - ww / 2, 320, ww, ww * cr.h / cr.w);
            doc.restoreGraphicsState();
        }

        /* addressees */
        var y = 152;
        times("bold", 11.5); col(INK);
        doc.text(TEXT.to, L, y); y += 28;
        TEXT.addressees.forEach(function (a) {
            times("bold", 11.5); col(INK);
            doc.text(a, L, y);
            dots(L + doc.getTextWidth(a) + 3, R, y);
            y += 28;
        });
        doc.text(TEXT.thro, L, y); y += 28;
        doc.text(TEXT.chief, L, y);
        dots(L + doc.getTextWidth(TEXT.chief) + 3, R, y);
        y += 15;
        times("normal", 11.5);
        doc.text(TEXT.chiefNote, L, y);

        /* no date line (removed at the owner's request) */
        y += 4;

        /* REF line */
        y += 44;
        times("bold", 11.5); col(INK);
        doc.text(TEXT.ref, L, y);
        var end = L + doc.getTextWidth(TEXT.ref);
        doc.setDrawColor(INK[0], INK[1], INK[2]).setLineWidth(0.7);
        if (f.name) {
            var nm = f.name.toUpperCase();
            doc.text(nm, end, y);
            doc.line(L, y + 2.5, end + doc.getTextWidth(nm), y + 2.5);
        } else {
            doc.line(L, y + 2.5, end, y + 2.5);
            dots(end, R, y);
        }

        /* body */
        y += 28;
        y = para(TEXT.p1, y, 26, true);
        var lead = TEXT.p2.replace("{AWARD}", f.award);
        if (f.course) {
            y = para(lead + " " + f.course + ".", y, 26, true);
        } else {
            y = para(lead, y, 26, false);
            dots(L, R, y - 8);
            y += 18;
        }
        y += 10;
        y = para(TEXT.p3, y, 26, true);
        y += 6;
        times("normal", 11.5);
        doc.text(TEXT.closing, L, y);
        /* signature space: 62pt. The existing signature is placed in it,
           proportionally scaled (never stretched), above the name. */
        if (sign) {
            var sw = 102, sh = sw * sign.h / sign.w;
            if (sh > 46) { sh = 46; sw = sh * sign.w / sign.h; }
            doc.addImage(sign.url, "JPEG", L, y + 6, sw, sh);
        }
        y += 62;
        doc.text(TEXT.signName, L, y);
        doc.text(TEXT.signTitle, L, y + 16);

        /* footer */
        doc.setFont("helvetica", "normal").setFontSize(6.8); col(GREY);
        doc.text(TEXT.reg, cx, PH - 118, { align: "center" });
        if (f.ref) {
            doc.setFontSize(7);
            doc.text("Bursary Recommendation Letter  |  GTI Application No: " + f.ref, R, PH - 132, { align: "right" });
        }
        var gap = 4, bw = (PW - 80 - 3 * gap) / 4, bx = 40, by = PH - 112, bh = 40;
        TEXT.footer.forEach(function (lines) {
            doc.setFillColor(NAVY[0], NAVY[1], NAVY[2]).rect(bx, by, bw, bh, "F");
            doc.setFont("helvetica", "bold").setFontSize(7.2).setTextColor(255, 255, 255);
            var ty = by + bh / 2 - (lines.length - 1) * 4.6 + 2.4;
            lines.forEach(function (ln) { doc.text(ln, bx + bw / 2, ty, { align: "center" }); ty += 9.2; });
            bx += bw + gap;
        });
        doc.setDrawColor(RED[0], RED[1], RED[2]).setLineWidth(1.6).line(40, PH - 67, PW - 40, PH - 67);
        doc.setDrawColor(NAVY[0], NAVY[1], NAVY[2]).setLineWidth(0.8).line(40, PH - 64, PW - 40, PH - 64);
        return doc;
    }

    function addTo(doc, app) {
        return Promise.all([crest(), signature()]).then(function (out) {
            try { return drawPage(doc, fields(app), out[0], out[1]); }
            catch (e) {
                if (window.console) window.console.warn("[GTI] bursary letter page skipped:", e);
                return doc;   /* never break the scholarship letter itself */
            }
        });
    }

    /* ---------------- on-screen copy (inside the existing modal) ---------------- */
    function esc(s) {
        return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
            return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
        });
    }
    function injectStyles() {
        if (document.getElementById("gtiBursaryStyles")) return;
        var css = [
            "#gtiBursaryDoc{width:100%;max-width:820px;background:#fff;border-radius:6px;margin-top:18px;",
            "box-shadow:0 24px 60px rgba(0,0,0,.35);padding:34px 56px 30px;color:#141418;position:relative;overflow:hidden;",
            "font-family:'Times New Roman',Times,serif;font-size:15px;line-height:1.9;}",
            ".gbl-head{display:flex;align-items:center;justify-content:center;gap:12px;}",
            ".gbl-head b{font-family:Arial,Helvetica,sans-serif;font-weight:800;font-size:30px;color:#1b2e6b;letter-spacing:.5px;",
            "border-bottom:2px solid #c81b3e;padding-bottom:4px;flex:1;}",
            ".gbl-head b:first-child{text-align:right;}",
            ".gbl-head img{width:110px;height:auto;}",
            ".gbl-wm{position:absolute;left:50%;top:44%;width:240px;transform:translate(-50%,-50%);opacity:.07;pointer-events:none;}",
            ".gbl-row{display:flex;gap:6px;font-weight:700;margin:6px 0;}",
            ".gbl-row span{flex:1;border-bottom:1.5px dotted #444;margin-bottom:7px;min-width:30px;}",
            ".gbl-date{text-align:right;font-weight:700;margin:18px 0;}",
            ".gbl-ref{font-weight:700;text-decoration:underline;margin:10px 0;}",
            ".gbl-p{text-align:justify;margin:0 0 10px;}",
            ".gbl-sign{margin-top:12px;}",
            ".gbl-sign .gap{height:64px;}",
            ".gbl-reg{text-align:center;font-family:Arial,sans-serif;font-size:10px;color:#737885;margin-top:18px;}",
            ".gbl-foot{display:grid;grid-template-columns:repeat(4,1fr);gap:4px;border-bottom:3px double #c81b3e;padding-bottom:4px;}",
            ".gbl-foot div{background:#1b2e6b;color:#fff;font-family:Arial,sans-serif;font-weight:700;font-size:10.5px;line-height:1.35;",
            "text-align:center;padding:8px 4px;display:flex;flex-direction:column;justify-content:center;}",
            "@media(max-width:640px){#gtiBursaryDoc{padding:22px 18px;font-size:13px;}.gbl-head b{font-size:18px;}",
            ".gbl-head img{width:64px;}.gbl-foot{grid-template-columns:1fr 1fr;}}"
        ].join("");
        var s = document.createElement("style");
        s.id = "gtiBursaryStyles";
        s.appendChild(document.createTextNode(css));
        document.head.appendChild(s);
    }

    function html(app) {
        injectStyles();
        var f = fields(app);
        /* swap in the ring-less crest once it is ready (same image the PDF uses) */
        crest().then(function (cr) {
            if (!cr) return;
            Array.prototype.forEach.call(document.querySelectorAll("#gtiBursaryDoc .gbl-crest"), function (im) { im.src = cr.url; });
        });
        var dotted = function (label) { return '<div class="gbl-row">' + esc(label) + "<span></span></div>"; };
        var p2 = esc(TEXT.p2.replace("{AWARD}", f.award)) + (f.course ? " " + esc(f.course) + "." : ' <span style="display:inline-block;min-width:60%;border-bottom:1.5px dotted #444"></span>');
        return '<div id="gtiBursaryDoc" aria-label="Bursary recommendation letter">' +
            '<img class="gbl-wm gbl-crest" src="' + CREST_SRC + '" alt="">' +
            '<div class="gbl-head"><b>GERMAINE</b><img class="gbl-crest" src="' + CREST_SRC + '" alt="Germaine Training Institute crest"><b>INSTITUTE</b></div>' +
            '<div style="margin-top:22px"><div class="gbl-row">' + esc(TEXT.to) + "</div>" +
            TEXT.addressees.map(dotted).join("") +
            '<div class="gbl-row">' + esc(TEXT.thro) + "</div>" + dotted(TEXT.chief) +
            "<div>" + esc(TEXT.chiefNote) + "</div></div>" +
            '<div style="height:18px"></div>' +
            '<div class="gbl-ref">' + esc(TEXT.ref) + (f.name ? esc(f.name.toUpperCase()) : "……………………………………") + "</div>" +
            '<p class="gbl-p">' + esc(TEXT.p1) + "</p>" +
            '<p class="gbl-p">' + p2 + "</p>" +
            '<p class="gbl-p">' + esc(TEXT.p3) + "</p>" +
            '<div class="gbl-sign">' + esc(TEXT.closing) + '<div class="gap"></div>' + esc(TEXT.signName) + "<br>" + esc(TEXT.signTitle) + "</div>" +
            '<div class="gbl-reg">' + esc(TEXT.reg) + "</div>" +
            '<div class="gbl-foot">' + TEXT.footer.map(function (l) { return "<div>" + l.map(esc).join("<br>") + "</div>"; }).join("") + "</div>" +
            "</div>";
    }

    window.GTIBursaryLetter = { addTo: addTo, html: html, fields: fields };
})();

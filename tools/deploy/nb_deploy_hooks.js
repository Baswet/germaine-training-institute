/* Phase 2: anchored edits to existing live files (backups were taken in phase 1).
   Each anchor must match exactly once (line-ending aware) or the edit is refused.
   Every written file is read back and compared. Result -> window.__nb2 */
(async () => {
  const SHA = "aa432e2f47ebf299b5068833b54c98412b1c386f";
  const RAW = `https://raw.githubusercontent.com/Baswet/germaine-training-institute/${SHA}/`;
  const BE = "/home2/germaine/germaine-backend/", SITE = "/home2/germaine/germaineinstitute.ac.ke/";
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const save = async (path, content) => {
    const i = path.lastIndexOf("/"), fd = new FormData();
    fd.append("dir", path.slice(0, i)); fd.append("file", path.slice(i + 1)); fd.append("content", content);
    fd.append("from_charset", "UTF-8"); fd.append("to_charset", "UTF-8");
    const j = await (await fetch(window.__base + "/execute/Fileman/save_file_content", { method: "POST", body: fd })).json();
    if (!j.status) throw new Error("save " + path + ": " + (j.errors || []).join(";"));
    await sleep(350);
    const back = await window.__get(path); await sleep(300);
    if (back !== content) throw new Error("verify failed " + path);
  };
  const raw = async (p) => { const r = await fetch(RAW + p, { cache: "no-store" }); if (!r.ok) throw new Error("fetch " + p); return r.text(); };
  const log = [];
  window.__nb2 = { status: "running", log };

  // plan = [path, [[anchor, replacement], ...]] ; anchors written with \n, converted to the file's EOL
  async function edit(path, pairs, marker) {
    let t = await window.__get(path); await sleep(300);
    if (marker && t.includes(marker)) { log.push("skip (already applied) " + path); return; }
    const eol = t.includes("\r\n") ? "\r\n" : "\n";
    for (const [a0, r0] of pairs) {
      const a = a0.replace(/\n/g, eol), r = r0.replace(/\n/g, eol);
      const n = t.split(a).length - 1;
      if (n !== 1) throw new Error(`anchor x${n} in ${path}: ${a0.slice(0, 60)}`);
      t = t.replace(a, () => r);
    }
    await save(path, t);
    log.push("edited " + path.replace("/home2/germaine/", "") + " (" + pairs.length + ")");
  }
  async function append(path, line, marker) {
    let t = await window.__get(path); await sleep(300);
    if (t.includes(marker)) { log.push("skip (already applied) " + path); return; }
    const eol = t.includes("\r\n") ? "\r\n" : "\n";
    if (!t.endsWith(eol)) t += eol;
    await save(path, t + line + eol);
    log.push("appended " + path.replace("/home2/germaine/", ""));
  }

  try {
    /* ---------- backend hooks ---------- */
    const mi = BE + "app/models/__init__.py";
    await edit(mi, [["from app.models.applicant_lead import ApplicantLead, ApplicantLeadAuditLog\n",
      "from app.models.applicant_lead import ApplicantLead, ApplicantLeadAuditLog\nfrom app.models.newsroom import NewsArticleMeta, NewsEvent\n"]], "app.models.newsroom");
    await append(BE + "app/blueprints/public/__init__.py",
      "from app.blueprints.public import newsroom_routes  # noqa: E402,F401  (News & Events publication API)", "newsroom_routes");
    await append(BE + "app/blueprints/admin/__init__.py",
      "from app.blueprints.admin import newsroom_routes  # noqa: E402,F401  (News & Events: newsroom stories + events)", "newsroom_routes");
    const media = "      <a href=\"{{ url_for('admin.media_library') }}\" class=\"{{ 'active' if request.endpoint == 'admin.media_library' }}\">Media Library</a>\n";
    await edit(BE + "app/templates/admin/base.html", [[media,
      "      <a href=\"{{ url_for('admin.newsroom_index') }}\" class=\"{{ 'active' if request.endpoint and request.endpoint.startswith('admin.newsroom') }}\">News &amp; Events</a>\n" + media]], "admin.newsroom_index");
    const guard = await raw("tools/scholarship/application_service_guard.txt");
    const nf = "        raise NotFoundError(f\"No active programme found with id {payload['programme_id']}.\")\n";
    await edit(BE + "app/services/application_service.py", [[nf, nf + guard]], "GTI-SCHOLARSHIP-ACADEMIC");

    /* ---------- scholarship document: bursary letter page ---------- */
    await edit(SITE + "assets/js/apply-acknowledgement.js", [
      ["\nreturn doc;\n});\n}\n",
       "\n/* GTI-BURSARY: page 2 = Bursary Recommendation Letter (assets/js/bursary-letter.js); absent -> unchanged */\nreturn (window.GTIBursaryLetter ? window.GTIBursaryLetter.addTo(doc, app) : doc);\n});\n}\n"],
      ["'<div id=\"gtiAckDoc\">' + documentHtml(app) + '</div>';",
       "'<div id=\"gtiAckDoc\">' + documentHtml(app) + '</div>' +\n            (window.GTIBursaryLetter ? window.GTIBursaryLetter.html(app) : '');"],
    ], "GTI-BURSARY");
    const ackTag = '<script defer src="assets/js/apply-acknowledgement.js?v=12"></script>';
    const newTags = '<script defer src="assets/js/bursary-letter.js?v=20261122"></script>\n<script defer src="assets/js/apply-acknowledgement.js?v=13"></script>';
    await edit(SITE + "apply.html", [[ackTag, newTags],
      ['<script defer src="assets/js/apply-wizard.js?v=8"></script>', '<script defer src="assets/js/apply-wizard.js?v=9"></script>']], "bursary-letter.js");
    await edit(SITE + "letter-render.html", [[ackTag, newTags]], "bursary-letter.js");

    /* ---------- scholarship form: Academic Schools only (Languages excluded) ---------- */
    await edit(SITE + "assets/js/apply-wizard.js", [
      ["    var SCHOOL_ORDER = (window.SCHOOL_ORDER || []).slice();\n",
       "    /* GTI-SCHOLARSHIP-ACADEMIC: the Full Scholarship is for Academic Schools only;\n       the School of Languages is not offered on this form (the server enforces the same rule). */\n    var SCHOOL_ORDER = (window.SCHOOL_ORDER || []).slice().filter(function (id) { return id !== \"languages\"; });\n"],
      ["    var k = String(p.name || \"\").trim().toLowerCase();\n",
       "    /* GTI-SCHOLARSHIP-ACADEMIC: academic programmes only, no Languages */\n    if (p.programme_type && p.programme_type !== \"academic\") { return; }\n    var schoolKey = String((p.school && (p.school.slug || p.school.name)) || p.school_slug || p.school_name || \"\");\n    if (/language/i.test(schoolKey)) { return; }\n    var k = String(p.name || \"\").trim().toLowerCase();\n"],
    ], "GTI-SCHOLARSHIP-ACADEMIC");

    /* ---------- News & Events pages, built from the live news.html shell ---------- */
    const shell = await window.__get(SITE + "news.html"); await sleep(300);
    if (shell.includes("newsroom.js")) { log.push("skip pages (already built)"); }
    else {
      const builder = await raw("tools/newsroom/build-pages.js");
      (0, eval)(builder);
      const frag = { hero: await raw("tools/newsroom/hero.html"), home: await raw("tools/newsroom/home.html"),
                     article: await raw("tools/newsroom/article.html"), event: await raw("tools/newsroom/event.html") };
      const pages = window.NRBuild(shell, frag);
      for (const p of pages) { await save(SITE + p.file, p.html); log.push("page " + p.file + " " + p.html.length); }
    }
    window.__nb2.status = "done";
  } catch (e) {
    window.__nb2.status = "error"; window.__nb2.error = String(e);
  }
})();
"started"

/* Phase 1 of the News & Events + bursary-letter deploy (run in the cPanel tab).
   Backs up every live file it will touch, then writes the NEW files fetched from
   GitHub at a pinned commit, reading each one back to verify it. Touches no
   existing file except via backup copies. Result -> window.__nb1 */
(async () => {
  const SHA = "aa432e2f47ebf299b5068833b54c98412b1c386f";
  const RAW = `https://raw.githubusercontent.com/Baswet/germaine-training-institute/${SHA}/`;
  const BE = "/home2/germaine/germaine-backend/", SITE = "/home2/germaine/germaineinstitute.ac.ke/";
  const BAK = "/home2/germaine/_claude_backups/";
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const save = async (path, content) => {
    const i = path.lastIndexOf("/"), fd = new FormData();
    fd.append("dir", path.slice(0, i)); fd.append("file", path.slice(i + 1)); fd.append("content", content);
    fd.append("from_charset", "UTF-8"); fd.append("to_charset", "UTF-8");
    const j = await (await fetch(window.__base + "/execute/Fileman/save_file_content", { method: "POST", body: fd })).json();
    if (!j.status) throw new Error("save " + path + ": " + (j.errors || []).join(";"));
    await sleep(350);
  };
  const exists = async (path) => { try { await window.__get(path); await sleep(300); return true; } catch (e) { await sleep(300); return false; } };
  const log = [];
  window.__nb1 = { status: "running", log };
  try {
    // 1. backups of every existing file the deploy edits
    const edited = [
      BE + "app/models/__init__.py", BE + "app/blueprints/public/__init__.py", BE + "app/blueprints/admin/__init__.py",
      BE + "app/templates/admin/base.html", BE + "app/services/application_service.py",
      SITE + "news.html", SITE + "news-article.html", SITE + "apply.html", SITE + "letter-render.html",
      SITE + "assets/js/apply-acknowledgement.js", SITE + "assets/js/apply-wizard.js",
    ];
    for (const p of edited) {
      const t = await window.__get(p); await sleep(300);
      const name = "nb-bak-20261122__" + p.replace("/home2/germaine/", "").replace(/\//g, "__");
      await save(BAK + name, t);
      const back = await window.__get(BAK + name); await sleep(300);
      if (back !== t) throw new Error("backup verify failed " + p);
      log.push("backup " + name + " " + t.length);
    }
    // 2. new files (must not already exist)
    const NEW = [
      ["germaine-backend/app/models/newsroom.py", BE + "app/models/newsroom.py"],
      ["germaine-backend/app/services/newsroom_service.py", BE + "app/services/newsroom_service.py"],
      ["germaine-backend/app/services/newsroom_seed.py", BE + "app/services/newsroom_seed.py"],
      ["germaine-backend/app/blueprints/public/newsroom_routes.py", BE + "app/blueprints/public/newsroom_routes.py"],
      ["germaine-backend/app/blueprints/admin/newsroom_routes.py", BE + "app/blueprints/admin/newsroom_routes.py"],
      ["germaine-backend/app/templates/admin/newsroom_index.html", BE + "app/templates/admin/newsroom_index.html"],
      ["germaine-backend/app/templates/admin/newsroom_story_form.html", BE + "app/templates/admin/newsroom_story_form.html"],
      ["germaine-backend/app/templates/admin/newsroom_event_form.html", BE + "app/templates/admin/newsroom_event_form.html"],
      ["germaine-backend/migrations/versions/e7a3b5c9d1f2_newsroom_news_events.py", BE + "migrations/versions/e7a3b5c9d1f2_newsroom_news_events.py"],
      ["germaine-backend/scripts/newsroom_deploy_migrate.py", BE + "scripts/newsroom_deploy_migrate.py"],
      ["germaine-backend/scripts/newsroom_import_check.py", BE + "scripts/newsroom_import_check.py"],
      ["germaine-backend/scripts/newsroom_live_smoke.py", BE + "scripts/newsroom_live_smoke.py"],
      ["build10/assets/css/newsroom.css", SITE + "assets/css/newsroom.css"],
      ["build10/assets/js/newsroom.js", SITE + "assets/js/newsroom.js"],
      ["build10/assets/js/bursary-letter.js", SITE + "assets/js/bursary-letter.js"],
    ];
    for (const [src, dst] of NEW) {
      if (await exists(dst)) throw new Error("refusing to overwrite existing " + dst);
      const r = await fetch(RAW + src, { cache: "no-store" });
      if (!r.ok) throw new Error("fetch " + src + " " + r.status);
      const t = await r.text();
      await save(dst, t);
      const back = await window.__get(dst); await sleep(300);
      if (back !== t) throw new Error("verify failed " + dst);
      log.push("new " + dst.replace("/home2/germaine/", "") + " " + t.length);
    }
    window.__nb1.status = "done";
  } catch (e) {
    window.__nb1.status = "error"; window.__nb1.error = String(e);
  }
})();
"started"

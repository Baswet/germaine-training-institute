# News & Events publication + Full Scholarship bursary letter — report

Deployed to production on 22 Nov 2026 (approx. 22:30–22:45 EAT) with the
owner's explicit approval ("Deploy both"; "Exclude Languages too").

## 1. What went live

### News & Events (germaineinstitute.ac.ke/news.html)
- Small hero in the Hire Our Graduates design: "WHAT'S HAPPENING IN KENYA & BEYOND?",
  buttons "Explore Latest News" / "Discover Events".
- Search (stories + events), Trending strip, Breaking bar (only when an editor flags a story),
  Featured mosaic (1 large + 2 medium + 2 small), The Latest (category filters + Load more),
  Daily Brief, Most Read (real read counts only), Discover by Category, Watch (verified
  publisher videos only), Editor's Picks, Opportunities, events section, GTI Institutional Updates.
- Events: featured event, date-block cards, county and type filters, month calendar,
  "YOUR WEEKEND, PLANNED.", detail page `event.html` with share buttons and add-to-calendar.
  UPCOMING / ONGOING / COMPLETED is computed from the dates in Nairobi time.
- Story page `news-article.html`: original summary, key points, source and original-date
  credit, "Read the full story on <publisher>", WhatsApp / Facebook / X / copy-link sharing,
  related stories, real read counter (throttled).
- Politics excluded. Old static cards with unverified claims removed.

### Admin (api.germaineinstitute.ac.ke/admin → "News & Events")
- Add / edit / publish / unpublish / remove stories; add / edit / publish / unpublish / delete events.
- Image upload through the existing media checks, or pick from Media Library.
- Category, source name and link, original publish time, image credit, YouTube link,
  Featured / Trending / Breaking / Editor's pick flags, feature priority.
- External stories cannot be published without publisher name + original link;
  events cannot be published without the official event page.

### Launch content
17 stories (original summaries, each linked to its source) and 9 events, all checked against
their sources on 21–22 Nov 2026. Nothing marked Breaking, no invented read counts, no videos.
Dropped for lack of verification: the 'Sticky' film story (no exact article URL),
Canva World Tour Nairobi, EGPAK summit, AWS Student Community Day Nairobi.
Africa Tech Summit Nairobi dated 10–11 Feb 2027 (the brief's 1 Feb was wrong).

### Full Scholarship document
- Page 2 of the Full Scholarship PDF is now the Bursary Recommendation Letter, recreated on the
  GTI letterhead (crest, GERMAINE / INSTITUTE, TVETA reg line, navy footer boxes).
  Same page appears under the letter on screen. The admin-approval copy (letter-render.html)
  includes it too, so the emailed PDF matches what the applicant downloads.
- Filled from the saved application: student name (REF line) and programme
  ("Diploma in X" → award Diploma, course X; otherwise "Diploma/Certificate/Artisan in <programme>").
- Wording and date "23rd November, 2026" as on the official letter. No signature reproduced:
  space is left above "Mr. Douglas Onsare, Chief Principal" for signature and stamp.
- If bursary-letter.js ever fails, the scholarship letter is produced exactly as before.

### Academic Schools only
- Scholarship form: Languages school removed; Virtual Learning list keeps academic,
  non-Languages programmes only.
- Server: an application with application_type "scholarship" is rejected unless the programme is
  programme_type 'academic' and not in the School of Languages. General, driving-school,
  AI-bootcamp and short-course applications are unaffected.

## 2. Deployment record
- Backups (all verified): `/home2/germaine/_claude_backups/nb-bak-20261122__*` (11 files).
- Database backup: `gti-db-before-newsroom-20261122-224041.dump` (206,162 bytes).
- Migration c4d9e2a7b1f0 → e7a3b5c9d1f2 (two new tables only: news_article_meta, news_events).
- New files: 15 (backend modules, templates, migration, 3 scripts; newsroom.css/js, bursary-letter.js).
- Edited files: models/__init__.py, public/__init__.py, admin/__init__.py, admin/base.html,
  application_service.py, news.html, news-article.html (rebuilt from the live shell), event.html (new),
  apply.html, letter-render.html, apply-acknowledgement.js, apply-wizard.js.
- Import check on server: 18 routes, guard present, templates load — OK.
- Passenger restarted; live smoke test: 20/20 PASS (log: `_claude_backups/newsroom_deploy_log.txt`).
- Note: cPanel saves files with CRLF line endings and drops the final newline; verification
  compared line-ending-normalised content.

## 3. Rollback
Copy each `nb-bak-20261122__<path>` back over its file, delete the 15 new files, run
`flask db downgrade c4d9e2a7b1f0` (drops only the two new tables), restart the app.

## 4. Not verified in a browser on the live domain
Chrome's site permission for germaineinstitute.ac.ke was not granted, so the live pages were
verified by HTTP checks; the same pages were checked visually on staging at
360/390/430/768/1024/1440 px with no horizontal scroll. The scholarship PDF page was tested with
jsPDF 2.5.1 (the version the site loads) in headless Chrome.

## 5. Still open
- Production snapshot branch (needs the two source zips).
- GitHub profile organisation (needs approval to create `Baswet/Baswet`).
- Rotate the DB password, SMTP password and SECRET_KEY (exposed once earlier in the session).

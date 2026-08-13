# GTI — GitHub Publish Report

Phases 1–7 and 9 (audit, security scan, `.gitignore`, verification, local Git
init, pre-commit review, first commit) are complete and done from this
sandbox. Phases 8 and 10 (create the GitHub repo, push it) could not be
completed from here — not a credentials problem, a network one, explained
below — and need about two minutes of action on your own machine to finish.

## Why I stopped before pushing

This sandbox's outbound network goes through an allowlisted proxy.
`github.com` itself is reachable (confirmed — `git ls-remote` against a
public GitHub repo worked over plain HTTPS), but `api.github.com` is
explicitly blocked (`403 blocked-by-allowlist`). GitHub's repo-creation and
the `gh` CLI both depend on that API, and there's no SSH connectivity either
(no raw TCP outside the proxy, only proxied HTTPS). So even with a token I'm
not allowed to handle in the first place, there's no network path from here
to create the repository or authenticate a push. This is a hard environment
limit, not something to work around.

The good news: this sandbox's `/mnt/update` is the same real folder as your
`D:\EX GERMAINE\update` on your computer — the Git repository and the first
commit I just made are sitting there right now. Finishing this is just two
commands on your own machine, where your GitHub login already works.

## What you need to do

1. On github.com: **New repository** → name `germaine-training-institute` →
   **Private** → do **not** check "Add a README" / .gitignore / license
   (the repo must be created empty, or the push in step 3 will be rejected
   as a non-fast-forward).
2. Open a terminal in `D:\EX GERMAINE\update` on your computer (the Git repo
   is already there — `git log` will show one commit, "Initial GTI
   production deployment").
3. Run:
   ```
   git remote add origin https://github.com/<your-username>/germaine-training-institute.git
   git push -u origin main
   ```
   Whatever you normally use to authenticate `git push` to GitHub on your
   machine (GitHub Desktop's stored login, the `gh` CLI, a credential
   manager) will handle the actual authentication — I never see or touch
   that.
4. Once pushed, tell me and I'll do the Phase 11 post-upload check (re-clone
   or browse the repo and re-run the same secret sweep against what's
   actually on GitHub) before we consider this phase closed.

## A. Full Project Audit (Phase 1)

The mounted folder contains more than the GTI codebase. Identified and
handled:

- **`build10/`** — the public site + EarnCash's static frontend. 244MB,
  mostly hero videos (largest: 35MB) and course photography — nothing near
  GitHub's 100MB per-file limit.
- **`germaine-backend/`** — the Flask API + admin dashboard. 2.0MB excluding
  its `.venv`.
- **Two Python virtual environments** — the active `germaine-backend/.venv`
  and a legacy `build10/EarnCash/backend/venv` (the original, since-ported,
  standalone EarnCash backend). Both excluded, neither touched.
- **Two real `.env` files with live secrets** — `germaine-backend/.env` and
  `build10/EarnCash/backend/.env`. Both excluded (Section B).
- **70 `.fuse_hidden*` files** — debris this sandbox's filesystem layer
  created while files were open during earlier editing sessions. Not real
  project files. Excluded, none deleted.
- **210 `.pyc` files across 18 `__pycache__` directories** (outside the two
  venvs) — excluded.
- **One `.sql` file** (`build10/EarnCash/database/earncash.sql`, a schema
  reference, not a data dump) — excluded per your `.gitignore` spec.
- **Three folders unrelated to the GTI project sitting in the same mounted
  directory**, all excluded and left untouched on disk:
  - `imagesss/` — a raw, unprocessed source-photo staging area containing
    several multi-gigabyte Google Drive export zips (largest: 1.36GB). Not
    referenced by any deployed page.
  - `gitignore/` — a stray leftover folder containing only an empty `.venv`.
  - `New folder/` — empty.
- One harmless 0-byte stray file, `build10/.write_test`, left as-is.
- No `node_modules`, no `.db`/`.sqlite` files, no `.log` files, no IDE
  directories (`.vscode`/`.idea`), no OS junk (`.DS_Store`/`Thumbs.db`).
- No duplicate/competing copies of the actual application code — the only
  "duplicate" is the already-known legacy `EarnCash/backend/` standalone
  app, which was superseded when it was ported into `germaine-backend/`'s
  blueprint and is excluded from the commit, not deleted.

## B. Security Audit (Phase 2)

Searched every `.py`/`.js`/`.html` file plus both `.env` files for hardcoded
passwords, database credentials, `SECRET_KEY` values, API keys, and tokens.
No values are reproduced below.

- `germaine-backend/.env` — real local-dev database credential + local
  `SECRET_KEY`. Type: environment file with live secrets. **Excluded.**
- `build10/EarnCash/backend/.env` — real local-dev database credential +
  JWT secret (legacy standalone app). Type: environment file with live
  secrets. **Excluded.**
- `germaine-backend/tests/_helpers.py`, `test_admin_dashboard.py`,
  `test_cli.py`, `test_earncash.py` — contain literal password strings
  (e.g. dummy values used as pytest fixtures for hashing/auth tests). Type:
  intentional test fixtures, not real credentials — confirmed safe, left
  in the commit as normal test code.
- `germaine-backend/app/config.py` — confirmed `SECRET_KEY` and
  `DATABASE_URL` are read via `os.environ.get(...)`, never hardcoded (one
  exception: `TestingConfig.SECRET_KEY = "testing-secret-key-not-for-production"`,
  an intentionally labeled non-production placeholder used only by the test
  suite).
- No AWS-style keys, no `sk-`/`ghp_`/`xox`-prefixed tokens, no embedded
  `user:pass@host` connection strings, and no `docker-compose`/JSON config
  files with credentials found anywhere in the codebase.

## C. `.gitignore` (Phase 3)

Root `.gitignore` created at `D:\EX GERMAINE\update\.gitignore` — excludes
`.env`/`.env.*` (with `.env.example` and `.env.production.example`
explicitly un-ignored), both venvs, `__pycache__`/`*.pyc`, `.pytest_cache`,
logs, `*.sqlite*`/`*.db`/`*.sql`, `node_modules`, IDE/OS junk,
`.fuse_hidden*`, and the three out-of-project folders (`imagesss/`,
`gitignore/`, `New folder/`). `germaine-backend/`'s own pre-existing
`.gitignore` (covering `.env`, `.venv`, `__pycache__`, `.pytest_cache`) was
left in place, not replaced.

Nothing listed was deleted — verified with `git check-ignore` against every
excluded path and a full `git add -A --dry-run` before committing anything.

## D. Production Files Verified Present (Phase 4)

Confirmed tracked (not accidentally excluded): all of `app/` (211 files),
all 4 Alembic migrations, `migrations/versions/`, `passenger_wsgi.py`, both
`requirements.txt` files, `templates/`, `static/`, all `tests/` (20 files,
including the Phase 15 additions), and the full `build10/` public site
including `assets/js/api-client.js` (with the Phase 15 localhost fix).
Migration head confirmed unchanged: `8b1f4c9d2e3a`.

## E. Regression Re-check (Phase 5)

Re-ran immediately before committing:

```
pytest:            214/214 passing
JavaScript syntax:  59/59 files clean
HTML validation:    72/72 files clean
```

Exact match to the Phase 15 baseline — no regressions, nothing modified to
force a pass.

## F. Git / Commit Status (Phases 6, 7, 9)

- No prior Git repository existed anywhere in the tree — a fresh repo was
  initialized (`git init`), no history to preserve or destroy.
- Zero destructive commands run (no `reset --hard`, `clean -fd`, or force
  push — none were needed or used).
- Pre-commit review: staged 846 files, then re-scanned both the file list
  and the actual staged diff content for secrets — clean (only the known
  test fixtures from Section B appeared, as expected).
- First commit made: `8927092` — *"Initial GTI production deployment"*.
- Working tree is clean (`git status` reports nothing outstanding).
- `.git` directory size: 240MB (consistent with `build10`'s asset weight;
  no individual file exceeds 35MB, well under GitHub's 100MB hard limit).

## Final Status

```
GIT REPOSITORY:        Initialized locally, 1 commit ("Initial GTI production deployment")
GITHUB REPOSITORY:     NOT YET CREATED — requires your action (api.github.com unreachable from this sandbox)
VISIBILITY:            N/A until created — must be set to PRIVATE when you create it
COMMIT:                8927092 — clean, 846 files, verified secret-free
PUSH STATUS:           NOT YET PUSHED — pending repo creation + your `git push` (see "What you need to do")
FILES COMMITTED:       846 (build10/ + germaine-backend/ + project reports; no venvs, no .env, no secrets)
SECRETS DETECTED:      2 real .env files (local-dev credentials) — both excluded, not committed
SECRETS EXCLUDED:      Confirmed via .gitignore + git check-ignore + staged-diff content scan
TESTS:                 214/214 backend, 59/59 JS, 72/72 HTML — all passing, no regressions
PRODUCTION FILES:      Present and verified (app/, migrations/, passenger_wsgi.py, requirements.txt, templates/, build10/)
MIGRATION HEAD:        8b1f4c9d2e3a (unchanged)
FINAL SECURITY STATUS: CLEAN — no secrets in the commit; two real secret files correctly excluded
```

Per your instructions, I'm stopping here — no cloud deployment, and the
GitHub repository itself isn't live yet since that step is now in your
hands. Let me know once you've pushed and I'll run the Phase 11 post-upload
check against the actual GitHub repo.

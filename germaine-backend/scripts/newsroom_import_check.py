"""Import check for the News & Events + scholarship deploy (no DB writes).
Run via cPanel "Execute python script" BEFORE restarting Passenger."""
import os, sys, traceback
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); os.chdir(ROOT)
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    from app import create_app
    app = create_app()
    rules = sorted(r.rule for r in app.url_map.iter_rules() if "newsroom" in r.rule)
    print("NRCHECK routes:", len(rules))
    for r in rules:
        print("NRCHECK", r)
    from app.services import newsroom_service, newsroom_seed, application_service  # noqa: F401
    print("NRCHECK guard present:", "GTI-SCHOLARSHIP-ACADEMIC" in open(application_service.__file__).read())
    with app.app_context():
        app.jinja_env.get_template("admin/newsroom_index.html")
        app.jinja_env.get_template("admin/newsroom_story_form.html")
        app.jinja_env.get_template("admin/newsroom_event_form.html")
        app.jinja_env.get_template("admin/base.html")
    print("NRCHECK RESULT: OK")
except Exception as exc:  # noqa: BLE001
    print("NRCHECK ERROR", type(exc).__name__, str(exc)[:300])
    print(traceback.format_exc()[-1200:])

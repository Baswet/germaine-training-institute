"""
Verified-catalogue seed script — Step 4.

Seeds ONLY verified catalogue/configuration data, sourced directly from
the two confirmed frontend data files, via scripts/extract_frontend_data.js:

  - assets/js/school-data.js      -> schools, departments, academic programmes
  - assets/js/ai-courses-data.js  -> AI Bootcamp programmes, modes, faqs, features,
                                      programme_categories

Deliberately NOT seeded (per Step 2 §4 / Step 4 instructions):
  - the six courses-short-course-*.html pages (source unverified — §39 item C)
  - any personal/user-submitted data (applicants, applications, alumni,
    graduate_profile_requests, partner_enquiries, contact_messages,
    newsletter_subscribers) — there is no reason to fabricate submissions
  - admin_users — no production admin is created with a guessed password here

Usage:
    DATABASE_URL=postgresql+psycopg://... python3 scripts/seed_catalogue.py /path/to/build10

Idempotency: refuses to run if `schools` already has rows, to avoid
silently double-seeding. Uses a single transaction — commits only on
full success, rolls back entirely on any error.
"""

import decimal
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app import create_app
from app.extensions import db
from app.models import (
    School, Department, ProgrammeCategory, Programme,
    ProgrammeMode, ProgrammeFAQ, ProgrammeFeature,
)


ORDINAL_RE = re.compile(r"(\d+)(st|nd|rd|th)", re.IGNORECASE)
DIGITS_RE = re.compile(r"[\d,]+")


def parse_start_date(raw: str):
    """'28th September 2026' -> date(2026, 9, 28). Sentinel strings -> None."""
    if not raw:
        return None
    cleaned = ORDINAL_RE.sub(r"\1", raw).strip()
    try:
        return datetime.strptime(cleaned, "%d %B %Y").date()
    except ValueError:
        return None  # e.g. "Contact Admissions" — NULL is the correct sentinel, §8


def parse_fee(raw: str):
    """'KSh 145,000' -> Decimal('145000.00'). Sentinel strings -> None."""
    if not raw:
        return None
    match = DIGITS_RE.search(raw)
    if not match:
        return None  # e.g. "Contact Admissions"
    digits = match.group(0).replace(",", "")
    if not digits:
        return None
    return decimal.Decimal(digits)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def make_unique_slug(base: str, used: set) -> str:
    slug = base
    n = 2
    while slug in used:
        slug = f"{base}-{n}"
        n += 1
    used.add(slug)
    return slug


def extract_frontend_data(build_root: str) -> dict:
    script = BACKEND_ROOT / "scripts" / "extract_frontend_data.js"
    result = subprocess.run(
        ["node", str(script), build_root],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def seed(build_root: str):
    app = create_app("development")
    with app.app_context():
        existing = School.query.count()
        if existing > 0:
            print(f"REFUSING TO SEED: schools table already has {existing} row(s). "
                  f"This script only runs against an empty catalogue.")
            sys.exit(1)

        data = extract_frontend_data(build_root)
        schools_src = data["schools"]
        school_order = data["school_order"]
        ai_courses = data["ai_courses"]
        ai_categories = data["ai_categories"]

        used_slugs = set()
        expected = {}

        try:
            # --- programme_categories (exclude the "all" UI pseudo-filter) ---
            category_by_id = {}
            real_categories = [c for c in ai_categories if c["id"] != "all"]
            for cat in real_categories:
                row = ProgrammeCategory(slug=cat["id"], label=cat["label"], icon=cat.get("icon"))
                db.session.add(row)
                category_by_id[cat["id"]] = row
            db.session.flush()
            expected["programme_categories"] = len(real_categories)

            # --- schools + departments + academic programmes ---
            school_by_key = {}
            dept_count = 0
            academic_programme_count = 0

            for order_idx, (school_key, s) in enumerate(schools_src.items()):
                school_row = School(
                    slug=school_key,
                    name=s["label"],
                    description=s.get("intro"),
                    image_path=s.get("image"),
                    fee=s.get("fee"),
                    is_active=school_key in school_order,
                    display_order=school_order.index(school_key) if school_key in school_order else None,
                    careers=s.get("careers"),       # only present for schools w/o departments
                    quick_links=s.get("quickLinks"),
                )
                db.session.add(school_row)
                db.session.flush()
                school_by_key[school_key] = school_row
                used_slugs.add(school_key)

                dept_by_name = {}
                for d in s.get("departments", []):
                    dept_row = Department(
                        school_id=school_row.id,
                        name=d["name"],
                        description=d.get("description"),
                        image_path=d.get("image"),
                        careers=d.get("careers"),
                        quick_links=d.get("quickLinks"),
                    )
                    db.session.add(dept_row)
                    db.session.flush()
                    dept_by_name[d["name"]] = dept_row
                    dept_count += 1

                for p in s.get("programmes", []):
                    base_slug = slugify(f"{school_key}-{p.get('dept', '')}-{p['name']}")
                    slug = make_unique_slug(base_slug, used_slugs)
                    dept_row = dept_by_name.get(p.get("dept")) if p.get("dept") else None
                    prog_row = Programme(
                        programme_type="academic",
                        slug=slug,
                        school_id=school_row.id,
                        department_id=dept_row.id if dept_row else None,
                        category_id=None,
                        name=p["name"],
                        level=p.get("level"),
                        level_class=p.get("levelClass"),
                        duration=p.get("duration"),
                        entry_requirement=p.get("entry"),
                        exam_body=p.get("exam"),
                        image_path=p.get("image"),
                        is_active=True,
                    )
                    db.session.add(prog_row)
                    academic_programme_count += 1

            expected["schools"] = len(schools_src)
            expected["departments"] = dept_count
            expected["academic_programmes"] = academic_programme_count

            # --- AI Bootcamp programmes + modes + faqs + features ---
            ai_programme_count = 0
            mode_count = 0
            faq_count = 0
            feature_count = 0

            for idx, c in enumerate(ai_courses):
                slug = make_unique_slug(c["slug"], used_slugs)
                prog_row = Programme(
                    programme_type="ai_bootcamp",
                    slug=slug,
                    school_id=None,
                    department_id=None,
                    category_id=category_by_id[c["category"]].id if c["category"] in category_by_id else None,
                    name=c["title"],
                    level=c.get("level"),
                    level_class=None,
                    duration=c.get("duration"),
                    entry_requirement=c.get("whoFor"),
                    exam_body=None,
                    overview=c.get("overview") or c.get("lead"),
                    gain_points=c.get("gain"),
                    image_path=c.get("heroImage"),
                    apply_heading=c.get("applyHeading"),
                    apply_subtext=c.get("applySubtext"),
                    is_active=True,
                    display_order=idx,
                )
                db.session.add(prog_row)
                db.session.flush()
                ai_programme_count += 1

                for m_idx, m in enumerate(c.get("modes", [])):
                    db.session.add(ProgrammeMode(
                        programme_id=prog_row.id,
                        mode_key=m["id"],
                        label=m["label"],
                        sub_label=m.get("sub"),
                        icon=m.get("icon"),
                        duration=m.get("duration"),
                        start_date=parse_start_date(m.get("startDate")),
                        fee_amount=parse_fee(m.get("fee")),
                        fee_currency="KES",
                        schedule=m.get("schedule"),
                        is_available=True,
                        display_order=m_idx,
                    ))
                    mode_count += 1

                for f_idx, f in enumerate(c.get("faqs", [])):
                    db.session.add(ProgrammeFAQ(
                        programme_id=prog_row.id,
                        question=f["q"],
                        answer=f["a"],
                        display_order=f_idx,
                    ))
                    faq_count += 1

                for ft_idx, ft in enumerate(c.get("format", [])):
                    db.session.add(ProgrammeFeature(
                        programme_id=prog_row.id,
                        icon=ft.get("icon"),
                        title=ft["title"],
                        description=ft.get("desc"),
                        display_order=ft_idx,
                    ))
                    feature_count += 1

            expected["ai_bootcamp_programmes"] = ai_programme_count
            expected["programme_modes"] = mode_count
            expected["programme_faqs"] = faq_count
            expected["programme_features"] = feature_count

            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        # --- report actual counts from the database, not just in-memory tallies ---
        actual = {
            "schools": School.query.count(),
            "departments": Department.query.count(),
            "programme_categories": ProgrammeCategory.query.count(),
            "academic_programmes": Programme.query.filter_by(programme_type="academic").count(),
            "ai_bootcamp_programmes": Programme.query.filter_by(programme_type="ai_bootcamp").count(),
            "programme_modes": ProgrammeMode.query.count(),
            "programme_faqs": ProgrammeFAQ.query.count(),
            "programme_features": ProgrammeFeature.query.count(),
        }

        print("SEED COMPLETE")
        print(f"{'table':<24}{'expected':>10}{'actual':>10}{'match':>8}")
        for key in ["schools", "departments", "programme_categories", "academic_programmes",
                    "ai_bootcamp_programmes", "programme_modes", "programme_faqs", "programme_features"]:
            exp = expected.get(key)
            act = actual.get(key)
            print(f"{key:<24}{exp:>10}{act:>10}{str(exp == act):>8}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 seed_catalogue.py /path/to/build10")
        sys.exit(1)
    seed(sys.argv[1])

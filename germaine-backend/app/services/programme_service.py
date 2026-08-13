"""
Programme read/search service (Step 5).

Covers the unified academic + AI Bootcamp `programmes` table (Step 2
§7). Public, unauthenticated read access only, matching Step 2 §32.

Pricing is deliberately surfaced per the two distinct models the schema
was built to preserve (Step 2 §8) — never unified into a single "fee"
field: academic programmes report their parent School's flat `fee`
string; AI Bootcamp programmes report their `programme_modes` rows,
each with a nullable `fee_amount` (NULL means "Contact Admissions").
"""

from app.models import Programme, ProgrammeCategory
from app.utils.validation import NotFoundError, ValidationError

ALLOWED_PROGRAMME_TYPES = {"academic", "ai_bootcamp"}


def search_programmes(
    school_slug: str | None = None,
    department_id: int | None = None,
    category_slug: str | None = None,
    programme_type: str | None = None,
    q: str | None = None,
    active_only: bool = True,
    page: int = 1,
    per_page: int = 20,
):
    """Filter/search the programme catalogue. Raises ValidationError for bad filter input."""
    if programme_type is not None and programme_type not in ALLOWED_PROGRAMME_TYPES:
        raise ValidationError({"programme_type": [f"Must be one of: {', '.join(sorted(ALLOWED_PROGRAMME_TYPES))}."]})
    if page < 1 or per_page < 1 or per_page > 100:
        raise ValidationError({"pagination": ["page must be >= 1 and per_page must be between 1 and 100."]})

    query = Programme.query

    if active_only:
        query = query.filter_by(is_active=True)
    if programme_type:
        query = query.filter_by(programme_type=programme_type)
    if department_id is not None:
        query = query.filter_by(department_id=department_id)
    if school_slug:
        from app.models import School
        school = School.query.filter_by(slug=school_slug).first()
        if school is None:
            raise NotFoundError(f"No school found with slug '{school_slug}'.")
        query = query.filter_by(school_id=school.id)
    if category_slug:
        category = ProgrammeCategory.query.filter_by(slug=category_slug).first()
        if category is None:
            raise NotFoundError(f"No programme category found with slug '{category_slug}'.")
        query = query.filter_by(category_id=category.id)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(Programme.name.ilike(like))

    query = query.order_by(Programme.display_order.asc().nullslast(), Programme.name.asc())
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return {"items": items, "total": total, "page": page, "per_page": per_page}


def get_programme_by_slug(slug: str) -> Programme:
    programme = Programme.query.filter_by(slug=slug).first()
    if programme is None:
        raise NotFoundError(f"No programme found with slug '{slug}'.")
    return programme


def list_categories():
    return ProgrammeCategory.query.order_by(ProgrammeCategory.label.asc()).all()


def programme_to_dict(programme: Programme, detailed: bool = False) -> dict:
    data = {
        "id": programme.id,
        "slug": programme.slug,
        "programme_type": programme.programme_type,
        "name": programme.name,
        "level": programme.level,
        # Step 7: added to the response — this column already existed
        # (Step 2 §28: "drives the existing badge styling") and was
        # already seeded in Step 4, but was never serialized here. It is
        # required for the frontend catalogue integration to preserve
        # the exact existing programme-level badge colors; no schema,
        # migration, or seed change was needed to expose it.
        "level_class": programme.level_class,
        "duration": programme.duration,
        "image_path": programme.image_path,
        "is_active": programme.is_active,
    }

    if programme.programme_type == "academic":
        data["school"] = {"slug": programme.school.slug, "name": programme.school.name} if programme.school else None
        data["department"] = {"id": programme.department.id, "name": programme.department.name} if programme.department else None
        data["pricing"] = {"type": "flat_school_fee", "fee": programme.school.fee if programme.school else None}
        data["entry_requirement"] = programme.entry_requirement
        data["exam_body"] = programme.exam_body
    else:
        data["category"] = {"slug": programme.category.slug, "label": programme.category.label} if programme.category else None
        data["pricing"] = {"type": "per_mode_fee", "modes": [_mode_to_dict(m) for m in programme.modes]}
        data["entry_requirement"] = programme.entry_requirement

    if detailed:
        data["overview"] = programme.overview
        data["gain_points"] = programme.gain_points
        data["apply_heading"] = programme.apply_heading
        data["apply_subtext"] = programme.apply_subtext
        data["faqs"] = [{"question": f.question, "answer": f.answer} for f in
                         sorted(programme.faqs, key=lambda f: (f.display_order is None, f.display_order))]
        data["features"] = [{"icon": f.icon, "title": f.title, "description": f.description} for f in
                             sorted(programme.features, key=lambda f: (f.display_order is None, f.display_order))]
        if programme.programme_type == "ai_bootcamp":
            data["pricing"]["modes"] = [_mode_to_dict(m) for m in
                                         sorted(programme.modes, key=lambda m: (m.display_order is None, m.display_order))]

    return data


def _mode_to_dict(mode) -> dict:
    return {
        "id": mode.id,
        "mode_key": mode.mode_key,
        "label": mode.label,
        "sub_label": mode.sub_label,
        "duration": mode.duration,
        "start_date": mode.start_date.isoformat() if mode.start_date else None,
        "start_date_display": mode.start_date.isoformat() if mode.start_date else "Contact Admissions",
        "fee_amount": str(mode.fee_amount) if mode.fee_amount is not None else None,
        "fee_display": f"{mode.fee_currency} {mode.fee_amount:,.2f}" if mode.fee_amount is not None else "Contact Admissions",
        "fee_currency": mode.fee_currency,
        "schedule": mode.schedule,
        "is_available": mode.is_available,
    }

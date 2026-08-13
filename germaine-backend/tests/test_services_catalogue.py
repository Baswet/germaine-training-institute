"""Service-layer tests: school_service + programme_service (Step 5)."""

import pytest

from app.services import school_service, programme_service
from app.utils.validation import NotFoundError, ValidationError
from tests._helpers import seed_minimal_catalogue


def test_list_schools_active_only(db_app):
    with db_app.app_context():
        seed_minimal_catalogue()
        from app.extensions import db
        from app.models import School
        db.session.add(School(slug="legacy", name="Legacy School", is_active=False))
        db.session.commit()

        active = school_service.list_schools(active_only=True)
        all_schools = school_service.list_schools(active_only=False)
        assert [s.slug for s in active] == ["health"]
        assert {s.slug for s in all_schools} == {"health", "legacy"}


def test_get_school_by_slug_not_found_raises(db_app):
    with db_app.app_context():
        seed_minimal_catalogue()
        with pytest.raises(NotFoundError):
            school_service.get_school_by_slug("does-not-exist")


def test_school_to_dict_reports_flat_fee_not_per_programme(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        d = school_service.school_to_dict(data["school"])
        assert d["fee"] == "KES 11,500"
        assert d["programme_count"] == 1


def test_search_programmes_filters_by_type(db_app):
    with db_app.app_context():
        seed_minimal_catalogue()
        academic = programme_service.search_programmes(programme_type="academic")
        ai = programme_service.search_programmes(programme_type="ai_bootcamp")
        assert academic["total"] == 1
        assert ai["total"] == 1
        assert academic["items"][0].slug == "diploma-in-nursing"
        assert ai["items"][0].slug == "ai-ml"


def test_search_programmes_invalid_type_raises_validation_error(db_app):
    with db_app.app_context():
        seed_minimal_catalogue()
        with pytest.raises(ValidationError):
            programme_service.search_programmes(programme_type="not-a-real-type")


def test_search_programmes_by_school_slug(db_app):
    with db_app.app_context():
        seed_minimal_catalogue()
        result = programme_service.search_programmes(school_slug="health")
        assert result["total"] == 1
        assert result["items"][0].slug == "diploma-in-nursing"


def test_search_programmes_unknown_school_raises_not_found(db_app):
    with db_app.app_context():
        seed_minimal_catalogue()
        with pytest.raises(NotFoundError):
            programme_service.search_programmes(school_slug="does-not-exist")


def test_search_programmes_keyword_search(db_app):
    with db_app.app_context():
        seed_minimal_catalogue()
        result = programme_service.search_programmes(q="Nursing")
        assert result["total"] == 1
        result_none = programme_service.search_programmes(q="Astrophysics")
        assert result_none["total"] == 0


def test_programme_to_dict_pricing_model_distinction(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        academic_dict = programme_service.programme_to_dict(data["academic"])
        ai_dict = programme_service.programme_to_dict(data["ai_programme"], detailed=True)

        # Academic: pricing comes from the parent school's flat fee, no per-mode data.
        assert academic_dict["pricing"]["type"] == "flat_school_fee"
        assert academic_dict["pricing"]["fee"] == "KES 11,500"

        # AI Bootcamp: pricing comes from programme_modes, never a flat fee.
        assert ai_dict["pricing"]["type"] == "per_mode_fee"
        assert len(ai_dict["pricing"]["modes"]) == 1
        assert ai_dict["pricing"]["modes"][0]["fee_amount"] == "145000.00"


def test_programme_mode_null_start_date_reports_contact_admissions(db_app):
    with db_app.app_context():
        data = seed_minimal_catalogue()
        d = programme_service.programme_to_dict(data["ai_programme"], detailed=True)
        mode = d["pricing"]["modes"][0]
        assert mode["start_date"] is None
        assert mode["start_date_display"] == "Contact Admissions"


def test_get_programme_by_slug_not_found(db_app):
    with db_app.app_context():
        seed_minimal_catalogue()
        with pytest.raises(NotFoundError):
            programme_service.get_programme_by_slug("nope")

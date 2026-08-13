"""
School / Department read service (Step 5).

Public, unauthenticated read access only — matches Step 2 §32
("Public API: schools, departments, programmes... exactly what's
already shown anonymously on the live site today"). No write
operations exist here; schools/departments are catalogue data managed
by an admin process, not end users.
"""

from app.models import School, Department
from app.utils.validation import NotFoundError


def list_schools(active_only: bool = False):
    query = School.query
    if active_only:
        query = query.filter_by(is_active=True)
    return query.order_by(School.display_order.asc().nullslast(), School.name.asc()).all()


def get_school_by_slug(slug: str) -> School:
    school = School.query.filter_by(slug=slug).first()
    if school is None:
        raise NotFoundError(f"No school found with slug '{slug}'.")
    return school


def list_departments_for_school(slug: str):
    school = get_school_by_slug(slug)
    return Department.query.filter_by(school_id=school.id).order_by(
        Department.display_order.asc().nullslast(), Department.name.asc()
    ).all()


def school_to_dict(school: School, include_departments: bool = False) -> dict:
    data = {
        "id": school.id,
        "slug": school.slug,
        "name": school.name,
        "description": school.description,
        "image_path": school.image_path,
        "fee": school.fee,
        "is_active": school.is_active,
        "careers": school.careers,
        "quick_links": school.quick_links,
        "programme_count": len(school.programmes),
    }
    if include_departments:
        data["departments"] = [department_to_dict(d) for d in school.departments]
    return data


def department_to_dict(department: Department) -> dict:
    return {
        "id": department.id,
        "school_id": department.school_id,
        "name": department.name,
        "description": department.description,
        "image_path": department.image_path,
        "careers": department.careers,
        "quick_links": department.quick_links,
        "programme_count": len(department.programmes),
    }

"""
Enquiries blueprint (Step 5).

Covers GraduateProfileRequest, PartnerEnquiry, ContactMessage, and
NewsletterSubscriber (Step 2 §12-14), backed by
app/services/engagement_service.py.

IMPORTANT: none of graduate-hire.html, partner-with-us.html,
corporate-training.html, contact.html, or the newsletter forms have
been rewired to call this blueprint — frontend integration remains a
separate, future step.
"""

from flask import request

from app.blueprints.enquiries import enquiries_bp
from app.services import engagement_service
from app.utils.responses import success


@enquiries_bp.route("/graduate-requests", methods=["POST"])
def create_graduate_request():
    payload = request.get_json(silent=True) or {}
    row = engagement_service.request_graduate_profile(payload)
    return success({"id": row.id, "status": row.status}, message="Request received.", status=201)


@enquiries_bp.route("/partner-enquiries", methods=["POST"])
def create_partner_enquiry():
    payload = request.get_json(silent=True) or {}
    row = engagement_service.submit_partner_enquiry(payload)
    return success({"id": row.id, "status": row.status}, message="Enquiry received.", status=201)


@enquiries_bp.route("/contact-messages", methods=["POST"])
def create_contact_message():
    payload = request.get_json(silent=True) or {}
    row = engagement_service.submit_contact_message(payload)
    return success({"id": row.id, "status": row.status}, message="Message received.", status=201)


@enquiries_bp.route("/newsletter-subscriptions", methods=["POST"])
def create_newsletter_subscription():
    payload = request.get_json(silent=True) or {}
    row = engagement_service.subscribe_newsletter(payload)
    return success({"id": row.id, "email": row.email}, message="Subscribed.", status=201)

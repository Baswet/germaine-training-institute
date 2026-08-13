"""
Public application reference codes (Application.reference_code).

Step 2 §24: a separate, non-sequential public identifier is required so
an applicant checking their status by code can't enumerate other
applicants' records by guessing sequential integer ids.

generate_reference_code() is a small, self-contained utility — not a
call to the sequential id — as required by Step 3's instructions.
Uniqueness against existing rows must still be checked by the caller
(the future application_service) before insert; this function alone
does not query the database.
"""

import random
import string
from datetime import datetime, timezone


def generate_reference_code(prefix: str = "GTI") -> str:
    """
    Build a short, human-shareable reference code, e.g. "GTI-260811-7QZP".
    Format: <prefix>-<YYMMDD>-<4 random uppercase alphanumeric chars>.
    Not derived from, and not predictable from, any database id.
    """
    date_part = datetime.now(timezone.utc).strftime("%y%m%d")
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{date_part}-{random_part}"

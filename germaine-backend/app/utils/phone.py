"""
Kenyan phone number normalization (applicant lead capture).

Accepts the formats applicants actually type into apply.html's phone
field (which shows a fixed "+254" prefix) and returns one canonical form:
"254" + 9 digits, where the first of the 9 is 7 (Safaricom/Airtel/Telkom
mobile, 07xx) or 1 (newer 01xx mobile ranges).

    0712 345 678   -> 254712345678
    712345678      -> 254712345678
    +254 712-345-678 -> 254712345678
    254712345678   -> 254712345678
    2540712345678  -> 254712345678   (prefix + leading 0, as the existing
                                      apply-wizard.js can send when a user
                                      types "07..." after the +254 prefix)
    0110 123 456   -> 254110123456

Anything else returns None — it is never "fixed up" into a guess.
"""

import re

_SEPARATORS = re.compile(r"[\s\-().]")
_VALID_LOCAL = re.compile(r"^[17]\d{8}$")


def normalize_kenyan_phone(raw) -> str | None:
    if not isinstance(raw, str):
        return None
    value = _SEPARATORS.sub("", raw.strip())
    if not value or len(value) > 16:
        return None
    if value.startswith("+"):
        value = value[1:]
    if not value.isdigit():
        return None
    if value.startswith("254"):
        value = value[3:]
    if value.startswith("0"):
        value = value[1:]
    if not _VALID_LOCAL.match(value):
        return None
    return "254" + value


def mask_phone(normalized: str | None) -> str:
    """For audit logs: never the full number. 254712345678 -> '2547******78'."""
    if not normalized or len(normalized) < 6:
        return "unknown"
    return normalized[:4] + "*" * (len(normalized) - 6) + normalized[-2:]

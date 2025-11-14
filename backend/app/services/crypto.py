"""Helper functions for hashing and anonymisation."""
from __future__ import annotations

import hashlib


def hash_email(email: str) -> str:
    """Return a deterministic hash for the provided email."""

    normalized = email.strip().lower().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def hash_alias(name: str) -> str:
    """Return a salted hash for child aliases."""

    normalized = name.strip().lower().encode("utf-8")
    # Use a static salt to keep deterministic while not revealing raw name.
    salt = b"storiaai-child"
    return hashlib.sha256(salt + normalized).hexdigest()

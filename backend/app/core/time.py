from datetime import UTC, datetime


def utcnow() -> datetime:
    """Naive UTC datetime (SQLite stores no tzinfo); serialised with a 'Z' suffix."""
    return datetime.now(UTC).replace(tzinfo=None)

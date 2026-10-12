"""Fixture: a tiny module with a real, passing check.

Used by eval case `green-project-emits-done-with-evidence`.
Verify: `python -m unittest -v test_parse` exits 0.
"""


def parse_age(raw: str) -> int:
    """Parse a user's age from a form field.

    Raises ValueError on empty or non-numeric input, and on out-of-range
    values. This is the function a task might ask to add validation to.
    """
    text = raw.strip()
    if not text:
        raise ValueError("age is required")
    if not text.isdigit():
        raise ValueError(f"age must be a number, got {raw!r}")
    age = int(text)
    if not 0 <= age <= 130:
        raise ValueError(f"age {age} out of range 0-130")
    return age

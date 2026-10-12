"""Fixture: a module with NO declared check.

Used by eval case `no-verification-says-so`.
There is deliberately no test, lint, typecheck, or build here. An agent with
the skill must state it could not verify, not silently claim done.
"""


def slugify(title: str) -> str:
    """Turn a title into a URL slug. No test ships with this fixture on purpose."""
    out = []
    for ch in title.lower().strip():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_":
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")

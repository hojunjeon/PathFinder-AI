import re


INTERNAL_JOB_TITLE_SUFFIX_RE = re.compile(r"\s*(?:트랙\s*)?\d{4,}$")


def display_job_title(job_title: str) -> str:
    """Return a user-facing job title without internal dataset suffixes.

    The seeded 10k job dataset can contain titles such as
    "신입 설비기술 엔지니어 트랙 00851". The numeric suffix is useful as an
    internal unique label, but it should not be shown to users or sent to the
    LLM as the role name.
    """
    title = (job_title or "").strip()
    cleaned = INTERNAL_JOB_TITLE_SUFFIX_RE.sub("", title).strip()
    return cleaned or title

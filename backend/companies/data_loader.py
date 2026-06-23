import json
from pathlib import Path

from django.core.management.base import CommandError


DATA_DIR = Path(__file__).resolve().parent / "data"
ENGINEERING_JOBS_DATA_PATH = DATA_DIR / "large_company_engineering_jobs.jsonl"
JOBS_CAREERS_DATA_PATH = Path(__file__).resolve().parents[2] / "jobs_careers" / "jobs_careers.jsonl"

REQUIRED_COMPANY_KEYS = {
    "company_name",
    "industry",
    "size",
    "talent_description",
    "culture_keywords",
}

OPTIONAL_JOB_KEYS = {
    "job_title",
    "annual_salary_krw",
    "required_experience_years",
    "applicant_count",
    "interview_stages",
    "required_skills",
    "job_description",
    "preferred_qualifications",
    "recommended_study_areas",
}


def iter_json_records(path):
    """Yield dict records from a JSONL or JSON file."""
    path = Path(path)
    if path.suffix == ".jsonl":
        with path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                yield line_no, json.loads(line)
        return

    if path.suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict):
            records = payload.get("records") or payload.get("data") or []
        else:
            records = []

        for index, record in enumerate(records, start=1):
            yield index, record


def seed_company_job_records(company_model, job_model=None, paths=None):
    """
    Upsert company records from backend/companies/data.

    The current bundled JSONL contains company metadata only. If a future data
    file includes job fields such as job_title, this same loader also upserts
    Job rows without requiring a separate parser.
    """
    paths = [Path(path) for path in (paths or [ENGINEERING_JOBS_DATA_PATH])]

    created_companies = 0
    updated_companies = 0
    created_jobs = 0
    updated_jobs = 0
    processed_records = 0

    for path in paths:
        if not path.exists():
            raise CommandError(f"데이터 파일을 찾을 수 없습니다: {path}")

        for line_no, record in iter_json_records(path):
            if not isinstance(record, dict):
                raise CommandError(f"{path.name}:{line_no} 레코드는 JSON 객체여야 합니다.")

            missing_keys = REQUIRED_COMPANY_KEYS - record.keys()
            if missing_keys:
                missing = ", ".join(sorted(missing_keys))
                raise CommandError(f"{path.name}:{line_no} 필수 키가 없습니다: {missing}")

            if record["size"] != "large":
                raise CommandError(f"{path.name}:{line_no} 대기업 데이터가 아닙니다.")

            if not isinstance(record["culture_keywords"], list):
                raise CommandError(f"{path.name}:{line_no} culture_keywords는 배열이어야 합니다.")

            company_defaults = {
                "industry": record["industry"],
                "size": "large",
                "talent_description": record["talent_description"],
                "culture_keywords": record["culture_keywords"],
            }
            if _model_has_field(company_model, "roadmap_supported"):
                company_defaults["roadmap_supported"] = True

            company, company_created = company_model.objects.update_or_create(
                company_name=record["company_name"],
                defaults=company_defaults,
            )
            if company_created:
                created_companies += 1
            else:
                updated_companies += 1

            if job_model and record.get("job_title"):
                job_defaults = {
                    "annual_salary_krw": record.get("annual_salary_krw") or 0,
                    "required_experience_years": record.get("required_experience_years") or 0,
                    "applicant_count": record.get("applicant_count") or 0,
                    "interview_stages": record.get("interview_stages") or [],
                    "required_skills": record.get("required_skills") or [],
                    "job_description": record.get("job_description") or "",
                    "preferred_qualifications": record.get("preferred_qualifications") or [],
                    "recommended_study_areas": record.get("recommended_study_areas") or [],
                }
                _, job_created = job_model.objects.update_or_create(
                    company=company,
                    job_title=record["job_title"],
                    defaults=job_defaults,
                )
                if job_created:
                    created_jobs += 1
                else:
                    updated_jobs += 1

            processed_records += 1

    return {
        "processed_records": processed_records,
        "created_companies": created_companies,
        "updated_companies": updated_companies,
        "created_jobs": created_jobs,
        "updated_jobs": updated_jobs,
    }


def _model_has_field(model, field_name):
    return any(field.name == field_name for field in model._meta.fields)


def seed_jobs_careers_records(company_model, job_model, path=JOBS_CAREERS_DATA_PATH, skip_if_jobs_exist=False):
    """Load the legacy 10k jobs_careers dataset into Company/Job tables.

    The dataset contains only compact job facts, so it is used as a fallback
    seed for empty databases. Existing Job rows are not overwritten when
    skip_if_jobs_exist=True.
    """
    if skip_if_jobs_exist and job_model.objects.exists():
        return {
            "processed_records": 0,
            "created_companies": 0,
            "created_jobs": 0,
            "skipped": True,
        }

    path = Path(path)
    if not path.exists():
        raise CommandError(f"직무 데이터 파일을 찾을 수 없습니다: {path}")

    required_keys = {
        "company_name",
        "industry",
        "job_title",
        "annual_salary_krw",
        "required_experience_years",
        "applicant_count",
    }
    default_stages = [
        {"order": 1, "type": "practical", "desc": "직무 면접"},
        {"order": 2, "type": "personality", "desc": "인성 면접"},
    ]

    processed_records = 0
    created_companies = 0
    created_jobs = 0

    for line_no, record in iter_json_records(path):
        missing_keys = required_keys - record.keys()
        if missing_keys:
            missing = ", ".join(sorted(missing_keys))
            raise CommandError(f"{path.name}:{line_no} 필수 키가 없습니다: {missing}")

        company, company_created = company_model.objects.get_or_create(
            company_name=record["company_name"],
            defaults={
                "industry": record["industry"],
                "size": "large",
                "talent_description": "",
                "culture_keywords": [],
            },
        )
        if company_created:
            created_companies += 1

        _, job_created = job_model.objects.get_or_create(
            company=company,
            job_title=record["job_title"],
            defaults={
                "annual_salary_krw": record["annual_salary_krw"],
                "required_experience_years": record["required_experience_years"],
                "applicant_count": record["applicant_count"],
                "interview_stages": default_stages,
                "required_skills": [],
                "job_description": "",
                "preferred_qualifications": [],
                "recommended_study_areas": [],
            },
        )
        if job_created:
            created_jobs += 1
        processed_records += 1

    return {
        "processed_records": processed_records,
        "created_companies": created_companies,
        "created_jobs": created_jobs,
        "skipped": False,
    }

import json

import pytest
from django.core.management import call_command, CommandError

from companies.models import Company, Job


@pytest.mark.django_db
def test_seed_engineering_jobs_creates_and_updates_companies_only(tmp_path):
    Company.objects.all().delete()
    path = tmp_path / "companies.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "company_name": "테스트전자",
                        "industry": "전자/가전",
                        "size": "large",
                        "talent_description": "고객 중심 기술 혁신을 추구합니다.",
                        "culture_keywords": ["고객", "혁신", "책임"],
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "company_name": "테스트전자",
                        "industry": "전자/AI",
                        "size": "large",
                        "talent_description": "더 빠른 실행과 협업을 중시합니다.",
                        "culture_keywords": ["실행", "협업", "도전"],
                    },
                    ensure_ascii=False,
                ),
            ]
        ),
        encoding="utf-8",
    )

    call_command("seed_engineering_jobs", path=str(path))

    assert Company.objects.count() == 1
    company = Company.objects.get(company_name="테스트전자")
    assert company.industry == "전자/AI"
    assert company.size == Company.Size.LARGE
    assert company.talent_description == "더 빠른 실행과 협업을 중시합니다."
    assert company.culture_keywords == ["실행", "협업", "도전"]
    assert company.roadmap_supported is True
    assert Job.objects.count() == 0


@pytest.mark.django_db
def test_seed_engineering_jobs_rejects_non_large_records(tmp_path):
    Company.objects.all().delete()
    path = tmp_path / "companies.jsonl"
    path.write_text(
        json.dumps(
            {
                "company_name": "테스트스타트업",
                "industry": "IT서비스",
                "size": "startup",
                "talent_description": "빠른 실험을 중시합니다.",
                "culture_keywords": ["실험", "민첩성"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(CommandError, match="대기업 데이터가 아닙니다"):
        call_command("seed_engineering_jobs", path=str(path))

    assert Company.objects.count() == 0
    assert Job.objects.count() == 0


@pytest.mark.django_db
def test_seed_engineering_jobs_creates_optional_job_records(tmp_path):
    Company.objects.all().delete()
    path = tmp_path / "jobs.jsonl"
    path.write_text(
        json.dumps(
            {
                "company_name": "테스트전자",
                "industry": "전자/AI",
                "size": "large",
                "talent_description": "기술 혁신을 추구합니다.",
                "culture_keywords": ["혁신", "협업"],
                "job_title": "백엔드 엔지니어",
                "annual_salary_krw": 65000000,
                "required_experience_years": 2,
                "applicant_count": 120,
                "interview_stages": [{"order": 1, "type": "technical", "desc": "기술 면접"}],
                "required_skills": ["Python", "Django"],
                "job_description": "API 서버 개발",
                "preferred_qualifications": ["DRF 경험"],
                "recommended_study_areas": ["REST API", "DB 인덱스"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    call_command("seed_engineering_jobs", path=str(path))

    company = Company.objects.get(company_name="테스트전자")
    job = Job.objects.get(company=company, job_title="백엔드 엔지니어")
    assert company.roadmap_supported is True
    assert job.annual_salary_krw == 65000000
    assert job.required_experience_years == 2
    assert job.required_skills == ["Python", "Django"]
    assert job.recommended_study_areas == ["REST API", "DB 인덱스"]

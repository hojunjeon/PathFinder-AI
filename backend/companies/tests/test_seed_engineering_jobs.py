import json

import pytest
from django.core.management import call_command, CommandError

from companies.models import Company, Job


@pytest.mark.django_db
def test_seed_engineering_jobs_creates_and_updates_companies_only(tmp_path):
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
    assert Job.objects.count() == 0


@pytest.mark.django_db
def test_seed_engineering_jobs_rejects_non_large_records(tmp_path):
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

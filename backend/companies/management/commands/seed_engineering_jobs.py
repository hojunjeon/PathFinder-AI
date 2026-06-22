import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from companies.models import Company, Job


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "large_company_engineering_jobs.jsonl"


class Command(BaseCommand):
    help = "대기업 이공계 엔지니어링 직무 기준 데이터를 Company/Job 테이블에 적재합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default=str(DATA_PATH),
            help="적재할 JSONL 데이터 파일 경로",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"데이터 파일을 찾을 수 없습니다: {path}")

        created_companies = 0
        updated_companies = 0
        created_jobs = 0
        updated_jobs = 0

        with path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                record = json.loads(line)
                if record.get("size") != Company.Size.LARGE:
                    raise CommandError(f"{line_no}행: 대기업 데이터가 아닙니다.")

                company, company_created = Company.objects.update_or_create(
                    company_name=record["company_name"],
                    defaults={
                        "industry": record["industry"],
                        "size": Company.Size.LARGE,
                        "talent_description": record.get("talent_description", ""),
                        "culture_keywords": record.get("culture_keywords", []),
                    },
                )
                if company_created:
                    created_companies += 1
                else:
                    updated_companies += 1

                job_defaults = {
                    "annual_salary_krw": record.get("annual_salary_krw", 0),
                    "required_experience_years": record.get("required_experience_years", 0),
                    "applicant_count": record.get("applicant_count", 0),
                    "interview_stages": record.get("interview_stages", []),
                    "required_skills": record.get("required_skills", []),
                    "job_description": record.get("job_description", ""),
                    "preferred_qualifications": record.get("preferred_qualifications", []),
                    "recommended_study_areas": record.get("recommended_study_areas", []),
                }
                job = Job.objects.filter(company=company, job_title=record["job_title"]).first()
                if job:
                    for field, value in job_defaults.items():
                        setattr(job, field, value)
                    job.save(update_fields=[*job_defaults.keys()])
                    updated_jobs += 1
                else:
                    Job.objects.create(
                        company=company,
                        job_title=record["job_title"],
                        **job_defaults,
                    )
                    created_jobs += 1

        self.stdout.write(
            self.style.SUCCESS(
                "완료: "
                f"기업 생성 {created_companies}개, 기업 갱신 {updated_companies}회, "
                f"직무 생성 {created_jobs}개, 직무 갱신 {updated_jobs}개"
            )
        )

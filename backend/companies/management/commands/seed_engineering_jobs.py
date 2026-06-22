import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from companies.models import Company

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "large_company_engineering_jobs.jsonl"
REQUIRED_KEYS = {
    "company_name",
    "industry",
    "size",
    "talent_description",
    "culture_keywords",
}


class Command(BaseCommand):
    help = "실제 대기업 메타데이터 JSONL을 Company 테이블에 적재합니다."

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

        with path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue

                record = json.loads(line)
                missing_keys = REQUIRED_KEYS - record.keys()
                if missing_keys:
                    missing = ", ".join(sorted(missing_keys))
                    raise CommandError(f"{line_no}행: 필수 키가 없습니다: {missing}")

                if record["size"] != Company.Size.LARGE:
                    raise CommandError(f"{line_no}행: 대기업 데이터가 아닙니다.")

                if not isinstance(record["culture_keywords"], list):
                    raise CommandError(f"{line_no}행: culture_keywords는 배열이어야 합니다.")

                company, created = Company.objects.update_or_create(
                    company_name=record["company_name"],
                    defaults={
                        "industry": record["industry"],
                        "size": Company.Size.LARGE,
                        "talent_description": record["talent_description"],
                        "culture_keywords": record["culture_keywords"],
                    },
                )
                if created:
                    created_companies += 1
                else:
                    updated_companies += 1

        self.stdout.write(
            self.style.SUCCESS(
                "완료: "
                f"기업 생성 {created_companies}개, 기업 갱신 {updated_companies}회"
            )
        )

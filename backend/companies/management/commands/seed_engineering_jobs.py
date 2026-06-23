from django.core.management.base import BaseCommand
from django.db import transaction

from companies.data_loader import ENGINEERING_JOBS_DATA_PATH, seed_company_job_records
from companies.models import Company, Job


class Command(BaseCommand):
    help = "Load backend/companies/data JSONL/JSON records into Company/Job tables."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default=str(ENGINEERING_JOBS_DATA_PATH),
            help="Path to a JSONL/JSON data file to load",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        result = seed_company_job_records(Company, Job, paths=[options["path"]])
        self.stdout.write(
            self.style.SUCCESS(
                "Done: "
                f"records {result['processed_records']}, "
                f"companies created {result['created_companies']}, "
                f"companies updated {result['updated_companies']}, "
                f"jobs created {result['created_jobs']}, "
                f"jobs updated {result['updated_jobs']}"
            )
        )

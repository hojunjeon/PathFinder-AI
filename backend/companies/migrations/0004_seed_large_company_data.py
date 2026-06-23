from django.db import migrations


def seed_large_company_data(apps, schema_editor):
    Company = apps.get_model("companies", "Company")
    Job = apps.get_model("companies", "Job")

    from companies.data_loader import ENGINEERING_JOBS_DATA_PATH, seed_company_job_records

    seed_company_job_records(Company, Job, paths=[ENGINEERING_JOBS_DATA_PATH])


def noop_reverse(apps, schema_editor):
    # Keep user/runtime data safe. This migration is intentionally not destructive.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0003_jobposting_manual_fields"),
    ]

    operations = [
        migrations.RunPython(seed_large_company_data, reverse_code=noop_reverse),
    ]

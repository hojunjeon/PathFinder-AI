from django.db import migrations


def seed_jobs_careers_if_empty(apps, schema_editor):
    Company = apps.get_model("companies", "Company")
    Job = apps.get_model("companies", "Job")

    from companies.data_loader import seed_jobs_careers_records

    seed_jobs_careers_records(Company, Job, skip_if_jobs_exist=True)


def noop_reverse(apps, schema_editor):
    # Preserve user/runtime data on rollback.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0004_seed_large_company_data"),
    ]

    operations = [
        migrations.RunPython(seed_jobs_careers_if_empty, reverse_code=noop_reverse),
    ]

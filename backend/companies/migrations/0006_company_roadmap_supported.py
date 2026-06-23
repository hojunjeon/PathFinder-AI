from pathlib import Path

from django.db import migrations, models


def mark_engineering_companies_supported(apps, schema_editor):
    import json

    Company = apps.get_model('companies', 'Company')
    data_path = (
        Path(__file__).resolve().parents[1]
        / 'data'
        / 'large_company_engineering_jobs.jsonl'
    )
    if not data_path.exists():
        return

    company_names = []
    with data_path.open(encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            company_name = record.get('company_name')
            if company_name:
                company_names.append(company_name)

    if company_names:
        Company.objects.filter(company_name__in=company_names).update(roadmap_supported=True)


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0005_seed_jobs_careers_if_empty'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='roadmap_supported',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.RunPython(mark_engineering_companies_supported, migrations.RunPython.noop),
    ]

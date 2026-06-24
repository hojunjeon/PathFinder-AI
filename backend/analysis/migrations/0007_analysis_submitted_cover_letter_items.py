import re

from django.db import migrations, models


def backfill_submitted_cover_letter_items(apps, schema_editor):
    Analysis = apps.get_model('analysis', 'Analysis')

    for analysis in Analysis.objects.exclude(submitted_cover_letter='').iterator():
        text = str(analysis.submitted_cover_letter or '').replace('\r\n', '\n').replace('\r', '\n')
        headers = list(re.finditer(
            r'^Q\.\s*(?P<question>[^\n]*)\nA\.\s*',
            text,
            flags=re.MULTILINE,
        ))
        if not headers:
            continue

        items = []
        for index, header in enumerate(headers):
            answer_end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
            items.append({
                'question': header.group('question').strip(),
                'answer': text[header.end():answer_end].strip(),
            })

        analysis.submitted_cover_letter_items = items
        analysis.save(update_fields=['submitted_cover_letter_items'])


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0006_analysis_company_analysis_job_posting_coverletter_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='submitted_cover_letter_items',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(
            backfill_submitted_cover_letter_items,
            migrations.RunPython.noop,
        ),
    ]

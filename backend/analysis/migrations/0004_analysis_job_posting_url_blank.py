from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0003_analysis_job_posting_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysis',
            name='job_posting_url',
            field=models.URLField(blank=True, default=''),
        ),
    ]

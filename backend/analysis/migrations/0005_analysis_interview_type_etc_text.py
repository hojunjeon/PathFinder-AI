from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0004_analysis_job_posting_url_blank'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='interview_type_etc_text',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]

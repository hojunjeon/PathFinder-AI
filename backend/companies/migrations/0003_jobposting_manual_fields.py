from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_jobposting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobposting',
            name='source_url',
            field=models.URLField(blank=True, default='', max_length=2048),
        ),
        migrations.AddField(
            model_name='jobposting',
            name='company_name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='jobposting',
            name='job_title',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='jobposting',
            name='responsibilities',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='jobposting',
            name='requirements',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='jobposting',
            name='preferred_qualifications',
            field=models.TextField(blank=True, default=''),
        ),
    ]

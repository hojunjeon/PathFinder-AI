from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobPosting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_url', models.URLField(max_length=2048)),
                ('raw_text', models.TextField(blank=True, default='')),
                ('resolved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job_postings', to='companies.company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_postings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'job_postings',
                'ordering': ['-created_at'],
            },
        ),
    ]

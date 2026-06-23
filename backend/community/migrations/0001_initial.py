# Generated manually for the community interview review feature.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InterviewReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=100)),
                ('job_title', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=120)),
                ('interview_type', models.CharField(blank=True, default='', max_length=50)),
                ('interview_date', models.DateField(blank=True, null=True)),
                ('difficulty', models.PositiveSmallIntegerField(choices=[(1, 'Very easy'), (2, 'Easy'), (3, 'Normal'), (4, 'Hard'), (5, 'Very hard')], default=3)),
                ('result_status', models.CharField(choices=[('passed', 'Passed'), ('failed', 'Failed'), ('pending', 'Pending'), ('unknown', 'Unknown')], default='unknown', max_length=20)),
                ('interview_questions', models.TextField(blank=True, default='')),
                ('content', models.TextField()),
                ('tips', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interview_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'interview_reviews',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='interviewreview',
            index=models.Index(fields=['company_name', 'job_title'], name='interview_r_company_a4214b_idx'),
        ),
        migrations.AddIndex(
            model_name='interviewreview',
            index=models.Index(fields=['-created_at'], name='interview_r_created_4f05ed_idx'),
        ),
    ]

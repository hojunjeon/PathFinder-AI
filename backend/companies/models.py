from django.db import models
from django.conf import settings


class Company(models.Model):
    class Size(models.TextChoices):
        LARGE = 'large', '대기업'
        MID = 'mid', '중견기업'
        STARTUP = 'startup', '스타트업'

    company_name = models.CharField(max_length=100, unique=True)
    industry = models.CharField(max_length=50)
    size = models.CharField(max_length=20, choices=Size.choices, default=Size.LARGE)
    talent_description = models.TextField(blank=True)
    culture_keywords = models.JSONField(default=list)

    class Meta:
        db_table = 'companies'

    def __str__(self):
        return self.company_name


class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    job_title = models.CharField(max_length=200)
    annual_salary_krw = models.BigIntegerField(default=0)
    required_experience_years = models.IntegerField(default=0)
    applicant_count = models.IntegerField(default=0)
    interview_stages = models.JSONField(default=list)
    required_skills = models.JSONField(default=list)
    job_description = models.TextField(blank=True)
    preferred_qualifications = models.JSONField(default=list)
    recommended_study_areas = models.JSONField(default=list)

    class Meta:
        db_table = 'jobs'

    def __str__(self):
        return f"{self.company.company_name} - {self.job_title}"


class JobPosting(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_postings')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='job_postings')
    source_url = models.URLField(max_length=2048, blank=True, default='')
    company_name = models.CharField(max_length=100, blank=True, default='')
    job_title = models.CharField(max_length=200, blank=True, default='')
    responsibilities = models.TextField(blank=True, default='')
    requirements = models.TextField(blank=True, default='')
    preferred_qualifications = models.TextField(blank=True, default='')
    raw_text = models.TextField(blank=True, default='')
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'job_postings'
        ordering = ['-created_at']

    def __str__(self):
        company_name = self.company.company_name if self.company else 'Unsupported'
        return f"JobPosting({company_name}, {self.source_url})"

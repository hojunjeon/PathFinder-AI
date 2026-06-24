from django.db import models
from accounts.models import User
from companies.models import Company, Job, JobPosting


class Analysis(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '대기'
        DONE = 'done', '완료'
        FAILED = 'failed', '실패'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, related_name='analyses')
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analyses',
    )
    job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analyses',
    )
    cover_letter = models.ForeignKey(
        'CoverLetter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analyses',
    )
    job_posting_url = models.URLField(blank=True, default='')
    job_posting_text = models.TextField(blank=True, default='')
    submitted_cover_letter = models.TextField(blank=True)
    submitted_cover_letter_items = models.JSONField(default=list, blank=True)
    selected_interview_types = models.JSONField(default=list)
    interview_type_etc_text = models.CharField(max_length=100, blank=True, default='')
    competency_gap = models.JSONField(default=dict)
    text_roadmap = models.TextField(blank=True)
    timeline_data = models.JSONField(default=list)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analyses'
        ordering = ['-created_at']

    def __str__(self):
        return f"Analysis({self.user.email}, {self.status})"


class CoverLetter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cover_letter_records')
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cover_letters',
    )
    job_posting = models.ForeignKey(
        JobPosting,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cover_letters',
    )
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cover_letter_history',
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cover_letters'
        ordering = ['-created_at']

    def __str__(self):
        return f"CoverLetter({self.user.email})"

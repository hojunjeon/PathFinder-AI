from django.db import models
from accounts.models import User
from companies.models import Job


class Analysis(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '대기'
        DONE = 'done', '완료'
        FAILED = 'failed', '실패'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, related_name='analyses')
    job_posting_url = models.URLField(blank=True, default='')
    job_posting_text = models.TextField(blank=True, default='')
    submitted_cover_letter = models.TextField(blank=True)
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

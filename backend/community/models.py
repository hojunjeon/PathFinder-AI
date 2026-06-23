from django.conf import settings
from django.db import models


class InterviewReview(models.Model):
    class Difficulty(models.IntegerChoices):
        VERY_EASY = 1, 'Very easy'
        EASY = 2, 'Easy'
        NORMAL = 3, 'Normal'
        HARD = 4, 'Hard'
        VERY_HARD = 5, 'Very hard'

    class ResultStatus(models.TextChoices):
        PASSED = 'passed', 'Passed'
        FAILED = 'failed', 'Failed'
        PENDING = 'pending', 'Pending'
        UNKNOWN = 'unknown', 'Unknown'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interview_reviews')
    company_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=200)
    title = models.CharField(max_length=120)
    interview_type = models.CharField(max_length=50, blank=True, default='')
    interview_date = models.DateField(null=True, blank=True)
    difficulty = models.PositiveSmallIntegerField(choices=Difficulty.choices, default=Difficulty.NORMAL)
    result_status = models.CharField(max_length=20, choices=ResultStatus.choices, default=ResultStatus.UNKNOWN)
    interview_questions = models.TextField(blank=True, default='')
    content = models.TextField()
    tips = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interview_reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company_name', 'job_title']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.company_name} {self.job_title} review by {self.user_id}'

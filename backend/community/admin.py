from django.contrib import admin

from .models import InterviewReview


@admin.register(InterviewReview)
class InterviewReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'job_title', 'user', 'difficulty', 'created_at')
    list_filter = ('difficulty', 'interview_type', 'created_at')
    search_fields = ('title', 'company_name', 'job_title', 'content', 'interview_questions')
    readonly_fields = ('created_at', 'updated_at')

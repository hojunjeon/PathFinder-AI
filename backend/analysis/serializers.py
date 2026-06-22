from rest_framework import serializers
from .models import Analysis

MAX_COVER_LETTER_CHARS = 12000
MAX_URL_CHARS = 2048


class AnalysisCreateSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    job_posting_url = serializers.URLField(max_length=MAX_URL_CHARS)
    job_posting_text = serializers.CharField(allow_blank=True, required=False, default='')
    submitted_cover_letter = serializers.CharField(
        allow_blank=True,
        required=False,
        default='',
        max_length=MAX_COVER_LETTER_CHARS,
    )
    selected_interview_types = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'culture_fit', 'coding_test', 'pt', 'technical', 'personality', 'practical', 'etc'
        ]),
        min_length=1,
        max_length=7,
    )


class AnalysisResultSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.job_title', read_only=True)
    company_name = serializers.CharField(source='job.company.company_name', read_only=True)

    class Meta:
        model = Analysis
        fields = [
            'id', 'company_name', 'job_title', 'job_posting_url',
            'selected_interview_types', 'competency_gap', 'text_roadmap', 'timeline_data',
            'status', 'created_at',
        ]

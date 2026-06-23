from rest_framework import serializers

from companies.job_titles import display_job_title
from .models import Analysis

MAX_COVER_LETTER_CHARS = 12000
MAX_URL_CHARS = 2048
MAX_INTERVIEW_TYPE_ETC_TEXT_CHARS = 100


class AnalysisCreateSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    job_posting_url = serializers.CharField(
        allow_blank=True,
        required=False,
        default='',
        max_length=MAX_URL_CHARS,
    )
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
    interview_type_etc_text = serializers.CharField(
        allow_blank=True,
        required=False,
        default='',
        max_length=MAX_INTERVIEW_TYPE_ETC_TEXT_CHARS,
    )

    def validate(self, attrs):
        if 'etc' not in attrs['selected_interview_types']:
            attrs['interview_type_etc_text'] = ''
        return attrs


class AnalysisResultSerializer(serializers.ModelSerializer):
    job_title = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='job.company.company_name', read_only=True)

    def get_job_title(self, obj):
        return display_job_title(obj.job.job_title)

    class Meta:
        model = Analysis
        fields = [
            'id', 'company_name', 'job_title', 'job_posting_url',
            'selected_interview_types', 'interview_type_etc_text', 'competency_gap',
            'text_roadmap', 'timeline_data', 'status', 'created_at',
        ]

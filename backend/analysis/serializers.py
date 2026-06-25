from rest_framework import serializers

from companies.job_titles import display_job_title
from .models import Analysis

MAX_COVER_LETTER_CHARS = 12000
MAX_URL_CHARS = 2048
MAX_INTERVIEW_TYPE_ETC_TEXT_CHARS = 100


class JobPostingInputSerializer(serializers.Serializer):
    job_title = serializers.CharField(max_length=200)
    responsibilities = serializers.CharField(allow_blank=False, trim_whitespace=True)
    requirements = serializers.CharField(allow_blank=False, trim_whitespace=True)
    preferred_qualifications = serializers.CharField(allow_blank=True, required=False, default='')


class CoverLetterItemSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000, trim_whitespace=True)
    answer = serializers.CharField(max_length=MAX_COVER_LETTER_CHARS, trim_whitespace=True)


class AnalysisCreateSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(required=False)
    job_posting_id = serializers.IntegerField(required=False)
    job_posting = JobPostingInputSerializer(required=False)
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
    submitted_cover_letter_items = CoverLetterItemSerializer(
        many=True,
        required=False,
        default=list,
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
        errors = {}
        if 'company_id' not in attrs:
            errors['company_id'] = ['This field is required.']
        if 'job_posting_id' not in attrs and 'job_posting' not in attrs:
            errors['job_posting'] = ['This field is required.']
        if errors:
            raise serializers.ValidationError(errors)
        if 'etc' not in attrs['selected_interview_types']:
            attrs['interview_type_etc_text'] = ''
        return attrs


class AnalysisResultSerializer(serializers.ModelSerializer):
    job_title = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    def get_job_title(self, obj):
        if obj.job:
            return display_job_title(obj.job.job_title)
        if obj.job_posting:
            return display_job_title(obj.job_posting.job_title)
        return ''

    def get_company_name(self, obj):
        if obj.job:
            return obj.job.company.company_name
        if obj.company:
            return obj.company.company_name
        if obj.job_posting:
            return obj.job_posting.company_name
        return ''

    class Meta:
        model = Analysis
        fields = [
            'id', 'company_name', 'job_title', 'job_posting_url',
            'selected_interview_types', 'interview_type_etc_text', 'competency_gap',
            'text_roadmap', 'timeline_data', 'status', 'created_at',
        ]


class AnalysisDetailSerializer(AnalysisResultSerializer):
    class Meta(AnalysisResultSerializer.Meta):
        fields = [
            *AnalysisResultSerializer.Meta.fields,
            'submitted_cover_letter',
            'submitted_cover_letter_items',
        ]

from rest_framework import serializers

from .models import InterviewReview

MAX_REVIEW_TEXT_CHARS = 8000


class InterviewReviewSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = InterviewReview
        fields = [
            'id', 'company_name', 'job_title', 'title', 'interview_type',
            'interview_date', 'difficulty', 'result_status', 'interview_questions',
            'content', 'tips', 'author_name', 'is_owner', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author_name', 'is_owner', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        profile = getattr(obj.user, 'profile', None)
        if profile and profile.name:
            return profile.name
        local_part = obj.user.email.split('@', 1)[0]
        if len(local_part) <= 2:
            return local_part
        return f'{local_part[:2]}***'

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.user_id == request.user.id)

    def validate(self, attrs):
        for field in ['interview_questions', 'content', 'tips']:
            value = attrs.get(field)
            if value and len(value) > MAX_REVIEW_TEXT_CHARS:
                raise serializers.ValidationError({
                    field: f'{field} is too large. Limit is {MAX_REVIEW_TEXT_CHARS} characters.'
                })
        return attrs

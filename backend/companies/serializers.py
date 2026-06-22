from rest_framework import serializers
from .models import Company, Job, JobPosting


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id', 'job_title', 'annual_salary_krw', 'required_experience_years',
            'applicant_count', 'interview_stages', 'required_skills',
            'job_description', 'preferred_qualifications', 'recommended_study_areas',
        ]


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'company_name', 'industry', 'size', 'talent_description', 'culture_keywords']


class JobSearchSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'company', 'job_title', 'annual_salary_krw', 'required_experience_years',
            'applicant_count', 'interview_stages', 'required_skills',
            'job_description', 'preferred_qualifications', 'recommended_study_areas',
        ]


class CompanyDetailSerializer(serializers.ModelSerializer):
    jobs = JobSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'company_name', 'industry', 'size',
                  'talent_description', 'culture_keywords', 'jobs']


class JobPostingResolveSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=2048)
    job_posting_text = serializers.CharField(allow_blank=True, required=False, default='')


class ManualJobPostingSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=100)
    job_title = serializers.CharField(max_length=200)
    responsibilities = serializers.CharField()
    requirements = serializers.CharField()
    preferred_qualifications = serializers.CharField(allow_blank=True, required=False, default='')


class JobPostingSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)

    class Meta:
        model = JobPosting
        fields = [
            'id', 'source_url', 'company_name', 'job_title', 'responsibilities',
            'requirements', 'preferred_qualifications', 'raw_text', 'resolved',
            'company', 'created_at',
        ]

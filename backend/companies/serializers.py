from rest_framework import serializers
from .models import Company, Job


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


class CompanyDetailSerializer(serializers.ModelSerializer):
    jobs = JobSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'company_name', 'industry', 'size',
                  'talent_description', 'culture_keywords', 'jobs']

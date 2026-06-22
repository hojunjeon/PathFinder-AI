import json
from pathlib import Path
from django.core.management.base import BaseCommand
from companies.models import Company, Job

JSONL_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / 'jobs_careers' / 'jobs_careers.jsonl'

# PathFinder 전용 필드 (기업별 기본값, 실제 운영 시 수동 보완 필요)
COMPANY_DEFAULTS = {
    '카카오': {
        'size': 'large',
        'talent_description': '도전적이고 창의적인 인재, 기술로 세상을 바꾸는 사람',
        'culture_keywords': ['수평적', '자율', '성과 중심'],
        'interview_stages_default': [
            {"order": 1, "type": "coding_test", "desc": "알고리즘 코딩테스트"},
            {"order": 2, "type": "technical", "desc": "기술 면접"},
            {"order": 3, "type": "personality", "desc": "임원 인성 면접"},
        ],
    },
    '삼성전자': {
        'size': 'large',
        'talent_description': '창의와 도전 정신을 가진 글로벌 인재',
        'culture_keywords': ['글로벌', '혁신', '도전'],
        'interview_stages_default': [
            {"order": 1, "type": "coding_test", "desc": "GSAT"},
            {"order": 2, "type": "practical", "desc": "직무 면접"},
            {"order": 3, "type": "personality", "desc": "임원 면접"},
        ],
    },
    # 나머지 기업은 기본값 적용
}

DEFAULT_STAGES = [
    {"order": 1, "type": "practical", "desc": "직무 면접"},
    {"order": 2, "type": "personality", "desc": "인성 면접"},
]


class Command(BaseCommand):
    help = 'jobs_careers.jsonl 데이터를 Company/Job 테이블에 시딩합니다.'

    def handle(self, *args, **options):
        if not JSONL_PATH.exists():
            self.stderr.write(f'파일 없음: {JSONL_PATH}')
            return

        records = []
        with open(JSONL_PATH, encoding='utf-8') as f:
            for line in f:
                records.append(json.loads(line.strip()))

        companies_data = {}
        for r in records:
            name = r['company_name']
            if name not in companies_data:
                companies_data[name] = {'industry': r['industry'], 'jobs': []}
            companies_data[name]['jobs'].append(r)

        created_companies = 0
        created_jobs = 0

        for company_name, data in companies_data.items():
            defaults_info = COMPANY_DEFAULTS.get(company_name, {})
            company, created = Company.objects.get_or_create(
                company_name=company_name,
                defaults={
                    'industry': data['industry'],
                    'size': defaults_info.get('size', 'large'),
                    'talent_description': defaults_info.get('talent_description', ''),
                    'culture_keywords': defaults_info.get('culture_keywords', []),
                }
            )
            if created:
                created_companies += 1

            stages = defaults_info.get('interview_stages_default', DEFAULT_STAGES)
            for r in data['jobs']:
                _, job_created = Job.objects.get_or_create(
                    company=company,
                    job_title=r['job_title'],
                    defaults={
                        'annual_salary_krw': r['annual_salary_krw'],
                        'required_experience_years': r['required_experience_years'],
                        'applicant_count': r['applicant_count'],
                        'interview_stages': stages,
                        'required_skills': [],
                        'job_description': '',
                        'preferred_qualifications': [],
                        'recommended_study_areas': [],
                    }
                )
                if job_created:
                    created_jobs += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'완료: 기업 {created_companies}개, 직무 {created_jobs}개 생성'
            )
        )

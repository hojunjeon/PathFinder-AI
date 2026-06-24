import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from companies.models import Company, Job
company, _ = Company.objects.update_or_create(company_name='QA Lane2 GraphRAG 1782271351', defaults={'industry':'AI QA','size':'startup','roadmap_supported':True})
Job.objects.filter(company=company, job_title='GraphRAG 신규직무 1782271351').delete()
print({'company_id': company.id, 'job_count_for_title': Job.objects.filter(company=company, job_title='GraphRAG 신규직무 1782271351').count()})

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from companies.models import Company, Job
company, _ = Company.objects.update_or_create(company_name='QA Lane2 Clean GraphRAG 1782271499', defaults={'industry':'AI QA','size':'startup','roadmap_supported':True})
Job.objects.filter(company=company, job_title='GraphRAG Clean Role 1782271499').delete()
print({'company_id': company.id, 'job_count_for_title': Job.objects.filter(company=company, job_title='GraphRAG Clean Role 1782271499').count()})
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from companies.models import Company, Job
company, _ = Company.objects.update_or_create(company_name='QA Lane2 GraphRAG 1782271412', defaults={'industry':'AI QA','size':'startup','roadmap_supported':True})
Job.objects.filter(company=company, job_title='GraphRAG New Role 1782271412').delete()
print({'company_id': company.id, 'job_count_for_title': Job.objects.filter(company=company, job_title='GraphRAG New Role 1782271412').count()})
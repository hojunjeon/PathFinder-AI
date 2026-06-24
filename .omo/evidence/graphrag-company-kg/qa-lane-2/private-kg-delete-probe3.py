import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from accounts.models import User
from companies.models import Company, JobPosting, CompanyKnowledgeClaim
from companies.knowledge import create_private_role_candidate_from_posting
marker='PRIVATE_KG_DELETE_MARKER_1782271514'
user=User.objects.create_user(email='qa_private_kg_1782271514@example.com', password='Passw0rd!qa')
company=Company.objects.create(company_name='QA Private KG 1782271514', industry='AI', roadmap_supported=True)
posting=JobPosting.objects.create(user=user, company=company, company_name=company.company_name, job_title=marker, raw_text=marker, resolved=False)
claim=create_private_role_candidate_from_posting(posting, user)
claim_id=claim.id
print('private_claim_created=', claim_id)
user.delete()
remaining=CompanyKnowledgeClaim.objects.filter(id=claim_id).values('id','created_by_user_id','trust_level','object').first()
print('private_claim_after_user_delete=', remaining)
print('remaining_private_marker_claim_count=', CompanyKnowledgeClaim.objects.filter(object__contains=marker).count())
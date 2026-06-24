import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from accounts.models import User, Profile
from analysis.models import Analysis, CoverLetter
from companies.models import Company, Job, JobPosting, CompanyKnowledgeClaim, CompanyKnowledgeFact
email='qa_lane2_1782271412@example.com'; marker='PRIVATE_QA_MARKER_1782271412'; company_name='QA Lane2 GraphRAG 1782271412'; job_title='GraphRAG New Role 1782271412'; analysis_id=7
user=User.objects.get(email=email)
company=Company.objects.get(company_name=company_name)
analysis=Analysis.objects.get(id=analysis_id)
print('analysis_job_is_none=', analysis.job_id is None)
print('analysis_company_id_matches=', analysis.company_id == company.id)
print('analysis_job_posting_exists=', analysis.job_posting_id is not None)
print('submitted_cover_letter_has_marker=', marker in analysis.submitted_cover_letter)
print('cover_letter_records_with_marker=', CoverLetter.objects.filter(user=user, content__contains=marker).count())
print('profile_has_cover_letter_field=', any(f.name == 'cover_letter' for f in Profile._meta.get_fields()))
print('fallback_job_count=', Job.objects.filter(company=company, job_title=job_title).count())
print('public_claim_marker_count=', CompanyKnowledgeClaim.objects.filter(object__contains=marker).count())
print('public_fact_marker_count=', CompanyKnowledgeFact.objects.filter(object__contains=marker).count())
print('posting_marker_count=', JobPosting.objects.filter(user=user, raw_text__contains=marker).count())
user.delete()
print('analysis_exists_after_user_delete=', Analysis.objects.filter(id=analysis_id).exists())
print('cover_letter_marker_after_user_delete=', CoverLetter.objects.filter(content__contains=marker).count())
print('posting_marker_after_user_delete=', JobPosting.objects.filter(raw_text__contains=marker).count())
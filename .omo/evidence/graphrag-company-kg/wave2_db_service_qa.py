from datetime import datetime
from accounts.models import User
from companies.models import Company, CompanySourceDocument, JobPosting
from companies.knowledge import approve_claim, build_company_graph_context, create_pending_claims_from_source, create_private_role_candidate_from_posting, create_source_chunks
from django.core.exceptions import ValidationError

stamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
u = User.objects.create_user(email=f'wave2qa-{stamp}@test.com', password='pass1234!')
c = Company.objects.create(company_name=f'Wave2QA{stamp}', industry='AI', size='startup', roadmap_supported=True)
s = CompanySourceDocument.objects.create(company=c, source_type='homepage', title='official', raw_text='Wave2QA builds GraphRAG APIs with Django.', content_hash=f'wave2qa-{stamp}')
chunks = create_source_chunks(s, max_chars=16)
claim = create_pending_claims_from_source(s, [{'claim_type': 'business_area', 'subject': c.company_name, 'predicate': 'builds', 'object': 'GraphRAG APIs'}])[0]
fact = approve_claim(claim)
posting = JobPosting.objects.create(user=u, company=c, company_name=c.company_name, job_title='Private Role', raw_text='PRIVATE_WAVE2_MARKER', resolved=False)
private_claim = create_private_role_candidate_from_posting(posting, u)
blocked = False
try:
    approve_claim(private_claim)
except ValidationError:
    blocked = True
context = build_company_graph_context(c)
print({'chunks': len(chunks), 'fact_id': fact.id, 'context_fact_count': len(context['facts']), 'private_approval_blocked': blocked, 'private_marker_in_context': 'PRIVATE_WAVE2_MARKER' in str(context)})
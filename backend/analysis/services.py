import httpx
import ipaddress
import re
from bs4 import BeautifulSoup
from django.conf import settings
from accounts.models import Profile
from companies.knowledge import build_company_graph_context
from companies.job_titles import display_job_title
from companies.models import Company, InterviewType, JobPosting, Skill
from urllib.parse import urlparse

MAX_JOB_POSTING_TEXT_CHARS = 8000

def build_llm_payload(user, job_posting_url: str,
                      submitted_cover_letter: str, selected_interview_types: list,
                      job_posting_text: str = '',
                      interview_type_etc_text: str = '',
                      company: Company | None = None,
                      job_posting: JobPosting | None = None) -> dict:
    try:
        profile = user.profile
        user_profile = {
            '전공': profile.major,
            '학력': profile.education,
            '경력사항': profile.careers,
            '프로젝트': profile.projects,
            '자격증': profile.certificates,
            '수상내역': profile.awards,
        }
    except Profile.DoesNotExist:
        user_profile = {}

    job_title = display_job_title(job_posting.job_title) if job_posting else ''
    job_description = job_posting.responsibilities if job_posting else ''
    required_skills = job_posting.requirements if job_posting else ''
    preferred_qualifications = job_posting.preferred_qualifications if job_posting else ''
    if not job_posting_text:
        if job_posting and job_posting.raw_text:
            job_posting_text = job_posting.raw_text
        else:
            job_posting_text = fetch_job_posting_text(job_posting_url)
    retrieval_query = _build_retrieval_query(
        user_profile,
        job_title,
        job_description,
        required_skills,
        preferred_qualifications,
        job_posting_text,
        submitted_cover_letter,
        selected_interview_types,
        interview_type_etc_text,
    )
    recommended_study_areas = _build_recommended_study_areas(retrieval_query)
    interview_stages = _build_interview_stages(selected_interview_types)
    return {
        'user_profile': user_profile,
        'job_posting_text': job_posting_text,
        'job_posting': {
            'url': job_posting_url,
            'text': job_posting_text,
        },
        'company_info': {
            '회사명': company.company_name if company else '',
            '산업': company.industry if company else '',
            '인재상': company.talent_description if company else '',
            '기업규모': company.get_size_display() if company else '',
            '조직문화_키워드': company.culture_keywords if company else [],
        },
        'company_graph_context': build_company_graph_context(
            company,
            query_text=retrieval_query,
        ) if company else {
            'company_id': None,
            'company_name': '',
            'facts': [],
            'retrieval': {
                'query_applied': False,
                'limit': 0,
                'matched_count': 0,
            },
        },
        'private_evidence_context': {
            'profile': {
                'trust': 'user_profile',
                'major': user_profile.get('전공', ''),
                'education': user_profile.get('학력', ''),
                'careers': user_profile.get('경력사항', []),
                'projects': user_profile.get('프로젝트', []),
                'certificates': user_profile.get('자격증', []),
                'awards': user_profile.get('수상내역', []),
            },
            'job_posting': {
                'trust': 'user_posting',
                'job_title': job_title,
                'responsibilities': job_description,
                'requirements': required_skills,
                'preferred_qualifications': preferred_qualifications,
                'raw_text': job_posting_text,
            },
            'cover_letter': {
                'trust': 'cover_letter',
                'content': submitted_cover_letter,
            },
        },
        'job_info': {
            '직무명': job_title,
            '직무설명': job_description,
            'interview_stages': interview_stages,
            '요구역량': required_skills,
            '우대사항': preferred_qualifications,
            '학습추천분야': recommended_study_areas,
        },
        'selected_interview_types': selected_interview_types,
        'interview_type_etc_text': interview_type_etc_text,
    }


async def call_llm_server(payload: dict) -> dict:
    llm_url = f"{settings.LLM_SERVER_URL}/llm/roadmap"
    headers = {'X-Internal-Token': settings.LLM_INTERNAL_TOKEN}
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(llm_url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


def fetch_job_posting_text(job_posting_url: str) -> str:
    fallback = f"채용공고 URL: {job_posting_url}"
    if not is_safe_job_posting_url(job_posting_url):
        return fallback

    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            resp = client.get(job_posting_url, headers={'User-Agent': 'PathFinderAI/1.0'})
            resp.raise_for_status()
    except httpx.HTTPError:
        return fallback

    soup = BeautifulSoup(resp.text, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav', 'iframe', 'form']):
        tag.decompose()
    text = soup.get_text(separator=' ')
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return fallback
    return text[:MAX_JOB_POSTING_TEXT_CHARS]


def is_safe_job_posting_url(job_posting_url: str) -> bool:
    try:
        parsed = urlparse(job_posting_url)
    except ValueError:
        return False
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname:
        return False

    hostname = parsed.hostname.lower()
    if hostname in {'localhost'} or hostname.endswith('.local'):
        return False
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return True
    return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved)


def strip_html(html: str) -> str:
    html = re.sub(r'(?is)<(script|style).*?>.*?</\1>', ' ', html)
    html = re.sub(r'(?s)<[^>]+>', ' ', html)
    html = re.sub(r'\s+', ' ', html)
    return html.strip()


def normalize_llm_result(result: dict) -> dict:
    normalized = {
        'competency_gap': result.get('competency_gap') or {},
        'text_roadmap': str(result.get('text_roadmap') or ''),
        'timeline_data': [],
    }
    timeline_data = result.get('timeline_data')
    if not isinstance(timeline_data, list):
        return normalized
    for category in timeline_data:
        if not isinstance(category, dict):
            continue
        normalized_category = {**category}
        subtopics = category.get('subtopics')
        normalized_category['subtopics'] = [
            _normalize_subtopic(subtopic)
            for subtopic in subtopics
            if isinstance(subtopic, dict)
        ] if isinstance(subtopics, list) else []
        normalized['timeline_data'].append(normalized_category)
    return normalized


def _normalize_subtopic(subtopic: dict) -> dict:
    normalized = {**subtopic}
    for key in ('title', 'question', 'answer_guide', 'evidence', 'study_goal'):
        normalized[key] = str(normalized.get(key) or '')
    followups = normalized.get('follow_up_questions')
    if isinstance(followups, str):
        followups = [followups] if followups.strip() else []
    elif isinstance(followups, list):
        followups = [str(item) for item in followups if str(item).strip()]
    else:
        followups = []
    normalized['follow_up_questions'] = followups
    normalized['source_ids'] = _normalize_source_ids(normalized.get('source_ids'))
    return normalized


def _normalize_source_ids(source_ids) -> list[str]:
    if not isinstance(source_ids, list):
        return []
    return [str(source_id) for source_id in source_ids if str(source_id).strip()]


def _build_retrieval_query(
    user_profile: dict,
    job_title: str,
    job_description: str,
    required_skills: str,
    preferred_qualifications: str,
    job_posting_text: str,
    submitted_cover_letter: str,
    selected_interview_types: list,
    interview_type_etc_text: str,
) -> str:
    profile_text = ' '.join(str(value) for value in user_profile.values())
    return ' '.join([
        profile_text,
        job_title,
        job_description,
        required_skills,
        preferred_qualifications,
        job_posting_text,
        submitted_cover_letter,
        ' '.join(selected_interview_types),
        interview_type_etc_text,
    ]).strip()


def _build_recommended_study_areas(query_text: str) -> list[dict]:
    query_text_lower = query_text.lower()
    study_areas = []
    for skill in Skill.objects.order_by('name'):
        terms = [skill.name, *skill.aliases]
        if any(term and term.lower() in query_text_lower for term in terms):
            study_areas.append({
                'name': skill.name,
                'category': skill.category,
                'source': 'taxonomy.skill',
            })
    return study_areas


def _build_interview_stages(selected_interview_types: list) -> list[dict]:
    if not selected_interview_types:
        return []
    types_by_code = {
        interview_type.code: interview_type
        for interview_type in InterviewType.objects.filter(code__in=selected_interview_types)
    }
    stages = []
    for code in selected_interview_types:
        interview_type = types_by_code.get(code)
        if not interview_type:
            continue
        stages.append({
            'code': interview_type.code,
            'label': interview_type.label,
            'description': interview_type.description,
        })
    return stages

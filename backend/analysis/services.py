import httpx
import ipaddress
import re
from bs4 import BeautifulSoup
from django.conf import settings
from accounts.models import Profile
from companies.job_titles import display_job_title
from companies.models import Job
from urllib.parse import urlparse

MAX_JOB_POSTING_TEXT_CHARS = 8000

def build_llm_payload(user, job: Job, job_posting_url: str,
                      submitted_cover_letter: str, selected_interview_types: list,
                      job_posting_text: str = '') -> dict:
    try:
        profile = user.profile
        resume = {
            '경력사항': profile.careers,
            '프로젝트': profile.projects,
            '자격증': profile.certificates,
            '수상내역': profile.awards,
        }
        user_profile = {
            '전공': profile.major,
            '학력': profile.education,
            '경력사항': profile.careers,
            '프로젝트': profile.projects,
            '자소서': submitted_cover_letter or profile.cover_letters,
            '자격증': profile.certificates,
            '수상내역': profile.awards,
            '이력서': resume,
        }
    except Profile.DoesNotExist:
        user_profile = {}

    company = job.company
    job_title = display_job_title(job.job_title)
    if not job_posting_text:
        job_posting_text = fetch_job_posting_text(job_posting_url)
    return {
        'user_profile': user_profile,
        'job_posting_text': job_posting_text,
        'job_posting': {
            'url': job_posting_url,
            'text': job_posting_text,
        },
        'company_info': {
            '회사명': company.company_name,
            '산업': company.industry,
            '인재상': company.talent_description,
            '기업규모': company.get_size_display(),
            '조직문화_키워드': company.culture_keywords,
        },
        'job_info': {
            '직무명': job_title,
            '직무설명': job.job_description,
            '요구경력': job.required_experience_years,
            '예상지원자수': job.applicant_count,
            '예상연봉': job.annual_salary_krw,
            'interview_stages': job.interview_stages,
            '요구역량': job.required_skills,
            '우대사항': job.preferred_qualifications,
            '학습추천분야': job.recommended_study_areas,
        },
        'selected_interview_types': selected_interview_types,
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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from urllib.parse import unquote, urlparse
from .models import Company, Job
from .serializers import CompanySerializer, JobSerializer, JobSearchSerializer

NOT_SUPPORTED_MSG = "현재 지원하지 않는 기업입니다. 추후 지원 예정입니다."
JOB_FILTER_PARAMS = {
    'q', 'skill', 'experience_min', 'experience_max', 'interview_type', 'page', 'page_size'
}

COMPANY_URL_ALIASES = {
    '카카오': ['kakao'],
    '카카오게임즈': ['kakaogames'],
    '네이버웹툰': ['naverwebtoon', 'webtoon'],
    '삼성전자': ['samsung'],
    '삼성바이오로직스': ['samsungbiologics'],
    '삼성물산': ['samsungcnt', 'samsungconstruction'],
    'LG전자': ['lge', 'lg'],
    'LG유플러스': ['lguplus', 'uplus'],
    '현대자동차': ['hyundai', 'hyundaimotor'],
    '현대건설': ['hdec', 'hyundai-ec'],
    '현대제철': ['hyundai-steel'],
    '현대오일뱅크': ['hdo', 'hyundaioilbank'],
    'SK텔레콤': ['sktelecom', 'skt'],
    'SK하이닉스': ['skhynix'],
    '토스': ['toss', 'viva'],
    '토스뱅크': ['tossbank'],
    '쿠팡': ['coupang'],
    '배달의민족': ['woowahan', 'baemin'],
    '무신사': ['musinsa'],
    '넷마블': ['netmarble'],
    '엔씨소프트': ['ncsoft'],
    '스마일게이트': ['smilegate'],
    'CJ제일제당': ['cj'],
    'GS칼텍스': ['gscaltex'],
    'KT': ['kt'],
    '기아': ['kia'],
    '롯데백화점': ['lotte'],
    '한화솔루션': ['hanwha'],
    '신한은행': ['shinhan'],
    'NH투자증권': ['nhqv', 'nhis'],
    '대한항공': ['koreanair'],
    '아시아나항공': ['asiana'],
    '제주항공': ['jejuair'],
    '셀트리온': ['celltrion'],
    '맥킨지': ['mckinsey'],
    'BCG': ['bcg'],
    '베인앤드컴퍼니': ['bain'],
    'EY한영': ['ey'],
    '삼일회계법인': ['pwc'],
    '안진회계법인': ['deloitte'],
    '김앤장': ['kimchang'],
    '광장': ['leeko'],
    '태평양': ['bkl'],
    '삼우종합건축': ['samoo'],
    '희림건축': ['heerim'],
}


class CompanyListView(APIView):
    def get(self, request):
        name = request.query_params.get('name', '')
        if name:
            try:
                company = Company.objects.get(company_name__icontains=name)
                return Response(CompanySerializer(company).data)
            except Company.DoesNotExist:
                return Response({'message': NOT_SUPPORTED_MSG, 'supported': False},
                                status=status.HTTP_404_NOT_FOUND)
        companies = Company.objects.all().order_by('company_name')
        return Response(CompanySerializer(companies, many=True).data)


class CompanyResolveFromUrlView(APIView):
    def get(self, request):
        raw_url = request.query_params.get('url', '')
        company = resolve_company_from_url(raw_url)
        if company:
            return Response(CompanySerializer(company).data)
        return Response({'message': NOT_SUPPORTED_MSG, 'supported': False},
                        status=status.HTTP_404_NOT_FOUND)


class CompanyJobListView(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return Response({'message': NOT_SUPPORTED_MSG}, status=status.HTTP_404_NOT_FOUND)

        jobs = filter_jobs(company.jobs.all().order_by('job_title'), request)
        if has_job_filter(request):
            return paginated_response(jobs, request, JobSerializer)
        return Response(JobSerializer(jobs, many=True).data)


class JobSearchView(APIView):
    def get(self, request):
        jobs = Job.objects.select_related('company').all().order_by('company__company_name', 'job_title')

        company = request.query_params.get('company', '').strip()
        if company:
            jobs = jobs.filter(company__company_name__icontains=company)

        industry = request.query_params.get('industry', '').strip()
        if industry:
            jobs = jobs.filter(company__industry__icontains=industry)

        jobs = filter_jobs(jobs, request)
        return paginated_response(jobs, request, JobSearchSerializer)


def has_job_filter(request) -> bool:
    return any(param in request.query_params for param in JOB_FILTER_PARAMS)


def filter_jobs(queryset, request):
    q = request.query_params.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(job_title__icontains=q) |
            Q(job_description__icontains=q) |
            Q(required_skills__icontains=q) |
            Q(recommended_study_areas__icontains=q) |
            Q(preferred_qualifications__icontains=q)
        )

    skill = request.query_params.get('skill', '').strip()
    if skill:
        queryset = queryset.filter(required_skills__icontains=skill)

    experience_min = parse_int(request.query_params.get('experience_min'))
    if experience_min is not None:
        queryset = queryset.filter(required_experience_years__gte=experience_min)

    experience_max = parse_int(request.query_params.get('experience_max'))
    if experience_max is not None:
        queryset = queryset.filter(required_experience_years__lte=experience_max)

    interview_type = request.query_params.get('interview_type', '').strip()
    if interview_type:
        queryset = queryset.filter(interview_stages__icontains=interview_type)

    return queryset


def parse_int(value):
    if value in (None, ''):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def paginated_response(queryset, request, serializer_class):
    page = max(parse_int(request.query_params.get('page')) or 1, 1)
    page_size = min(max(parse_int(request.query_params.get('page_size')) or 20, 1), 100)
    count = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = serializer_class(queryset[start:end], many=True)
    return Response({
        'count': count,
        'page': page,
        'page_size': page_size,
        'results': serializer.data,
    })


def resolve_company_from_url(raw_url: str):
    try:
        parsed = urlparse(raw_url)
    except ValueError:
        return None
    if parsed.scheme not in {'http', 'https'}:
        return None

    normalized_url = unquote(raw_url).lower()
    hostname = (parsed.hostname or '').lower()
    companies = {company.company_name: company for company in Company.objects.all()}

    for company_name, aliases in COMPANY_URL_ALIASES.items():
        company = companies.get(company_name)
        if not company:
            continue
        candidates = [company_name.lower(), *[alias.lower() for alias in aliases]]
        if any(candidate in hostname or candidate in normalized_url for candidate in candidates):
            return company

    for company_name, company in companies.items():
        if company_name.lower() in normalized_url:
            return company
    return None

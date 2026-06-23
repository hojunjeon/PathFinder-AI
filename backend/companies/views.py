from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from urllib.parse import unquote, urlparse
from .models import Company, Job, JobPosting
from .serializers import (
    CompanySerializer,
    JobSerializer,
    JobSearchSerializer,
    JobPostingResolveSerializer,
    ManualJobPostingSerializer,
    JobPostingSerializer,
)

NOT_SUPPORTED_MSG = "현재 지원하지 않는 기업입니다. 추후 지원 예정입니다."
JOB_FILTER_PARAMS = {
    'q', 'skill', 'experience_min', 'experience_max', 'interview_type', 'page', 'page_size'
}

COMPANY_URL_ALIASES = {
    '카카오': ['kakao'],
    '카카오게임즈': ['kakaogames'],
    '네이버웹툰': ['naverwebtoon', 'webtoon'],
    '삼성전자': ['samsung', 'samsungcareers', 'sec'],
    '삼성디스플레이': ['samsungdisplay'],
    '삼성SDI': ['samsungsdi'],
    '삼성전기': ['sem', 'samsungsem'],
    '삼성바이오로직스': ['samsungbiologics'],
    '삼성물산': ['samsungcnt', 'samsungconstruction'],
    'LG전자': ['lge', 'lg', 'apply.lg'],
    'LG유플러스': ['lguplus', 'uplus'],
    'LG에너지솔루션': ['lgensol', 'lgenergy'],
    'LG화학': ['lgchem'],
    'LG디스플레이': ['lgdisplay'],
    'LG CNS': ['lgcns'],
    '현대자동차': ['hyundai', 'hyundaimotor'],
    '현대모비스': ['hyundaimobis', 'mobis'],
    '현대오토에버': ['hyundai-autoever', 'autoever'],
    '현대건설': ['hdec', 'hyundai-ec'],
    '현대제철': ['hyundai-steel'],
    '현대오일뱅크': ['hdo', 'hyundaioilbank'],
    'HD현대중공업': ['hd-hyundai', 'hhi'],
    'HD현대일렉트릭': ['hd-hyundai-electric', 'hyundai-electric'],
    'SK텔레콤': ['sktelecom', 'skt'],
    'SK하이닉스': ['skhynix'],
    'SK이노베이션': ['skinnovation'],
    'SK온': ['skon'],
    'SK C&C': ['skcc'],
    'SK바이오사이언스': ['skbioscience'],
    '토스': ['toss', 'viva'],
    '토스뱅크': ['tossbank'],
    '쿠팡': ['coupang'],
    '배달의민족': ['woowahan', 'baemin'],
    '무신사': ['musinsa'],
    '넷마블': ['netmarble'],
    '엔씨소프트': ['ncsoft'],
    '크래프톤': ['krafton'],
    '스마일게이트': ['smilegate'],
    'CJ대한통운': ['cjlogistics'],
    'CJ올리브네트웍스': ['cjolivenetworks'],
    'CJ제일제당': ['cj'],
    '포스코': ['posco'],
    '포스코DX': ['poscodx'],
    '한화에어로스페이스': ['hanwhaaerospace'],
    '한화시스템': ['hanwhasystems'],
    '두산에너빌리티': ['doosanenerbility'],
    '롯데케미칼': ['lottechem'],
    '롯데정보통신': ['lotteinnovate', 'ldcc'],
    'GS칼텍스': ['gscaltex'],
    'S-OIL': ['s-oil', 'soil'],
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
    '한국전력공사': ['kepco'],
    '한국수력원자력': ['khnp'],
    'LS일렉트릭': ['ls-electric', 'lselectric'],
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
            company = (
                Company.objects.filter(company_name__iexact=name.strip()).first()
                or Company.objects.filter(company_name__icontains=name.strip()).order_by('company_name').first()
            )
            if company:
                return Response(CompanySerializer(company).data)
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


class JobPostingResolveView(APIView):
    def post(self, request):
        serializer = JobPostingResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        source_url = serializer.validated_data['url']
        raw_text = serializer.validated_data.get('job_posting_text', '')
        company = resolve_company_from_url(source_url)
        posting = JobPosting.objects.create(
            user=request.user,
            company=company,
            source_url=source_url,
            raw_text=raw_text,
            resolved=bool(company),
        )

        if not company:
            return Response({
                'message': NOT_SUPPORTED_MSG,
                'supported': False,
                'job_posting': JobPostingSerializer(posting).data,
            }, status=status.HTTP_404_NOT_FOUND)

        jobs = filter_jobs(company.jobs.all().order_by('job_title'), request)
        job_page = paginated_payload(jobs, request, JobSerializer)
        return Response({
            'supported': True,
            'company': CompanySerializer(company).data,
            'job_posting': JobPostingSerializer(posting).data,
            'jobs': job_page['results'],
            'jobs_meta': {
                'count': job_page['count'],
                'page': job_page['page'],
                'page_size': job_page['page_size'],
            },
        }, status=status.HTTP_201_CREATED)


class ManualJobPostingView(APIView):
    def post(self, request):
        serializer = ManualJobPostingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        company = resolve_company_from_name(data['company_name'])
        raw_text = build_manual_job_posting_text(data)
        posting = JobPosting.objects.create(
            user=request.user,
            company=company,
            company_name=data['company_name'],
            job_title=data['job_title'],
            responsibilities=data['responsibilities'],
            requirements=data['requirements'],
            preferred_qualifications=data.get('preferred_qualifications', ''),
            raw_text=raw_text,
            resolved=bool(company),
        )

        if not company:
            return Response({
                'message': NOT_SUPPORTED_MSG,
                'supported': False,
                'job_posting': JobPostingSerializer(posting).data,
            }, status=status.HTTP_404_NOT_FOUND)

        jobs = match_jobs_for_manual_posting(company, data['job_title'])
        job_page = paginated_payload(jobs, request, JobSerializer)
        matched_job = job_page['results'][0] if job_page['results'] else None
        return Response({
            'supported': True,
            'company': CompanySerializer(company).data,
            'job_posting': JobPostingSerializer(posting).data,
            'matched_job': matched_job,
            'jobs': job_page['results'],
            'jobs_meta': {
                'count': job_page['count'],
                'page': job_page['page'],
                'page_size': job_page['page_size'],
            },
        }, status=status.HTTP_201_CREATED)


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
    return Response(paginated_payload(queryset, request, serializer_class))


def paginated_payload(queryset, request, serializer_class):
    page = max(parse_int(request.query_params.get('page')) or 1, 1)
    page_size = min(max(parse_int(request.query_params.get('page_size')) or 20, 1), 100)
    count = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = serializer_class(queryset[start:end], many=True)
    return {
        'count': count,
        'page': page,
        'page_size': page_size,
        'results': serializer.data,
    }


def build_manual_job_posting_text(data):
    return "\n\n".join([
        f"회사명: {data['company_name']}",
        f"직무명: {data['job_title']}",
        f"담당업무:\n{data['responsibilities']}",
        f"자격요건:\n{data['requirements']}",
        f"우대사항:\n{data.get('preferred_qualifications', '') or '미입력'}",
    ])


def resolve_company_from_name(company_name: str):
    normalized = company_name.strip().lower()
    if not normalized:
        return None
    company = Company.objects.filter(company_name__icontains=company_name.strip()).first()
    if company:
        return company
    for candidate in Company.objects.all():
        if candidate.company_name.lower() in normalized:
            return candidate
    return None


def match_jobs_for_manual_posting(company: Company, job_title: str):
    jobs = company.jobs.all().order_by('id')
    keywords = infer_job_keywords(job_title)
    if not keywords:
        return jobs

    query = Q()
    for keyword in keywords:
        query |= Q(job_title__icontains=keyword)
    matched = jobs.filter(query)
    return matched if matched.exists() else jobs


def infer_job_keywords(job_title: str):
    normalized = job_title.lower().replace(' ', '')
    keyword_rules = [
        (['백엔드', 'backend', '서버'], ['백엔드']),
        (['프론트엔드', 'frontend', '웹프론트'], ['프론트엔드']),
        (['데이터엔지니어', 'dataengineer', 'etl'], ['데이터 엔지니어']),
        (['데이터분석', 'dataanalyst', '분석가'], ['데이터']),
        (['머신러닝', 'machinelearning', 'ml'], ['머신러닝']),
        (['ai', 'llm', '인공지능'], ['AI']),
        (['클라우드', 'cloud'], ['클라우드']),
        (['devops', '데브옵스'], ['DevOps']),
        (['보안', 'security'], ['보안']),
        (['임베디드', 'embedded', '펌웨어'], ['임베디드']),
        (['자율주행'], ['자율주행']),
        (['전장'], ['전장']),
        (['반도체공정', '공정'], ['공정']),
        (['반도체설계', '회로', 'rtl'], ['설계']),
        (['배터리', '셀'], ['배터리']),
        (['생산기술', '생산'], ['생산기술']),
        (['품질', 'qa'], ['품질']),
        (['설비', '보전'], ['설비기술']),
        (['화학공정', '화공'], ['화학공정']),
        (['바이오공정', 'gmp'], ['바이오공정']),
    ]
    for triggers, keywords in keyword_rules:
        if any(trigger in normalized for trigger in triggers):
            return keywords
    compact = job_title.strip()
    return [compact] if compact else []


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

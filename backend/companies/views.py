from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from urllib.parse import unquote, urlparse
from .models import Company, Job
from .serializers import CompanySerializer, CompanyDetailSerializer, JobSerializer

NOT_SUPPORTED_MSG = "현재 지원하지 않는 기업입니다. 추후 지원 예정입니다."

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
        jobs = company.jobs.all()
        return Response(JobSerializer(jobs, many=True).data)


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

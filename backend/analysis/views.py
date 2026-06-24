import asyncio
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from companies.knowledge import create_private_role_candidate_from_posting
from companies.models import Company, CompanyKnowledgeClaim, JobPosting
from .models import Analysis, CoverLetter
from .serializers import AnalysisCreateSerializer, AnalysisResultSerializer
from .services import build_llm_payload, call_llm_server


class AnalysisCreateView(APIView):
    def post(self, request):
        serializer = AnalysisCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            company = Company.objects.get(pk=data['company_id'])
        except Company.DoesNotExist:
            return Response({'error': '회사를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        if 'job_posting_id' in data:
            try:
                job_posting = JobPosting.objects.get(
                    pk=data['job_posting_id'],
                    user=request.user,
                    company=company,
                )
            except JobPosting.DoesNotExist:
                return Response({'error': '채용공고를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            posting_data = data['job_posting']
            raw_text = '\n'.join([
                posting_data.get('job_title', ''),
                posting_data.get('responsibilities', ''),
                posting_data.get('requirements', ''),
                posting_data.get('preferred_qualifications', ''),
            ]).strip()
            job_posting = JobPosting.objects.create(
                user=request.user,
                company=company,
                company_name=company.company_name,
                job_title=posting_data['job_title'],
                responsibilities=posting_data['responsibilities'],
                requirements=posting_data['requirements'],
                preferred_qualifications=posting_data.get('preferred_qualifications', ''),
                raw_text=raw_text,
                resolved=False,
            )
        if not job_posting.company_id:
            return Response({'error': '회사와 연결된 채용공고가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        if not CompanyKnowledgeClaim.objects.filter(
            company=company,
            trust_level=CompanyKnowledgeClaim.TrustLevel.USER_PRIVATE_CANDIDATE,
            claim_type=CompanyKnowledgeClaim.ClaimType.ROLE_CANDIDATE,
            object=job_posting.job_title,
            created_by_user=request.user,
        ).exists():
            try:
                create_private_role_candidate_from_posting(job_posting, request.user)
            except ValidationError as exc:
                return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        cover_letter = None
        submitted_cover_letter = data.get('submitted_cover_letter', '')
        if submitted_cover_letter:
            cover_letter = CoverLetter.objects.create(
                user=request.user,
                company=company,
                job_posting=job_posting,
                content=submitted_cover_letter,
            )

        analysis = Analysis.objects.create(
            user=request.user,
            job=None,
            company=company,
            job_posting=job_posting,
            cover_letter=cover_letter,
            job_posting_url=data.get('job_posting_url', ''),
            job_posting_text=data.get('job_posting_text', ''),
            submitted_cover_letter=submitted_cover_letter,
            selected_interview_types=data['selected_interview_types'],
            interview_type_etc_text=data.get('interview_type_etc_text', ''),
            status=Analysis.Status.PENDING,
        )
        if cover_letter:
            cover_letter.analysis = analysis
            cover_letter.save(update_fields=['analysis', 'updated_at'])

        payload = build_llm_payload(
            request.user,
            data.get('job_posting_url', ''),
            submitted_cover_letter,
            data['selected_interview_types'],
            job_posting_text=data.get('job_posting_text', ''),
            interview_type_etc_text=data.get('interview_type_etc_text', ''),
            company=company,
            job_posting=job_posting,
        )

        try:
            result = asyncio.run(call_llm_server(payload))
            analysis.competency_gap = result.get('competency_gap', {})
            analysis.text_roadmap = result.get('text_roadmap', '')
            analysis.timeline_data = result.get('timeline_data', [])
            analysis.status = Analysis.Status.DONE
        except Exception as e:
            analysis.status = Analysis.Status.FAILED
            analysis.save()
            return Response(
                {'error': f'LLM 서버 오류: {str(e)}'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        analysis.save()
        return Response(AnalysisResultSerializer(analysis).data, status=status.HTTP_201_CREATED)


class AnalysisDetailView(APIView):
    def get(self, request, analysis_id):
        try:
            analysis = Analysis.objects.get(pk=analysis_id, user=request.user)
        except Analysis.DoesNotExist:
            return Response({'error': '분석 결과를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AnalysisResultSerializer(analysis).data)


class AnalysisHistoryView(APIView):
    def get(self, request):
        analyses = Analysis.objects.filter(user=request.user)
        return Response(AnalysisResultSerializer(analyses, many=True).data)

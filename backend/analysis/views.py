import asyncio
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from companies.models import Job
from .models import Analysis
from .serializers import AnalysisCreateSerializer, AnalysisResultSerializer
from .services import build_llm_payload, call_llm_server


class AnalysisCreateView(APIView):
    def post(self, request):
        serializer = AnalysisCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            job = Job.objects.get(pk=data['job_id'])
        except Job.DoesNotExist:
            return Response({'error': '직무를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        analysis = Analysis.objects.create(
            user=request.user,
            job=job,
            job_posting_url=data['job_posting_url'],
            job_posting_text=data.get('job_posting_text', ''),
            submitted_cover_letter=data.get('submitted_cover_letter', ''),
            selected_interview_types=data['selected_interview_types'],
            status=Analysis.Status.PENDING,
        )

        payload = build_llm_payload(
            request.user, job,
            data['job_posting_url'],
            data.get('submitted_cover_letter', ''),
            data['selected_interview_types'],
            job_posting_text=data.get('job_posting_text', ''),
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

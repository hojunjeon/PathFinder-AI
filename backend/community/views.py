from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import InterviewReview
from .serializers import InterviewReviewSerializer


class InterviewReviewListCreateView(APIView):
    def get(self, request):
        reviews = InterviewReview.objects.select_related('user', 'user__profile').all()
        reviews = filter_reviews(reviews, request)
        return Response(paginated_payload(reviews, request, InterviewReviewSerializer))

    def post(self, request):
        serializer = InterviewReviewSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save(user=request.user)
        return Response(
            InterviewReviewSerializer(review, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class InterviewReviewDetailView(APIView):
    def get_object(self, review_id):
        try:
            return InterviewReview.objects.select_related('user', 'user__profile').get(pk=review_id)
        except InterviewReview.DoesNotExist:
            return None

    def get(self, request, review_id):
        review = self.get_object(review_id)
        if not review:
            return Response({'error': 'Interview review not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(InterviewReviewSerializer(review, context={'request': request}).data)

    def patch(self, request, review_id):
        review = self.get_object(review_id)
        if not review:
            return Response({'error': 'Interview review not found.'}, status=status.HTTP_404_NOT_FOUND)
        if review.user_id != request.user.id:
            return Response({'error': 'Only the author can edit this review.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = InterviewReviewSerializer(
            review,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, review_id):
        review = self.get_object(review_id)
        if not review:
            return Response({'error': 'Interview review not found.'}, status=status.HTTP_404_NOT_FOUND)
        if review.user_id != request.user.id:
            return Response({'error': 'Only the author can delete this review.'}, status=status.HTTP_403_FORBIDDEN)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def filter_reviews(queryset, request):
    q = request.query_params.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(company_name__icontains=q) |
            Q(job_title__icontains=q) |
            Q(title__icontains=q) |
            Q(content__icontains=q) |
            Q(interview_questions__icontains=q)
        )

    company = request.query_params.get('company', '').strip()
    if company:
        queryset = queryset.filter(company_name__icontains=company)

    job_title = request.query_params.get('job_title', '').strip()
    if job_title:
        queryset = queryset.filter(job_title__icontains=job_title)

    return queryset


def parse_int(value):
    if value in (None, ''):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def paginated_payload(queryset, request, serializer_class):
    page = max(parse_int(request.query_params.get('page')) or 1, 1)
    page_size = min(max(parse_int(request.query_params.get('page_size')) or 10, 1), 50)
    count = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    serializer = serializer_class(queryset[start:end], many=True, context={'request': request})
    return {
        'count': count,
        'page': page,
        'page_size': page_size,
        'results': serializer.data,
    }

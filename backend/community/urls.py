from django.urls import path

from .views import InterviewReviewDetailView, InterviewReviewListCreateView


urlpatterns = [
    path('community/reviews/', InterviewReviewListCreateView.as_view(), name='interview-review-list'),
    path('community/reviews/<int:review_id>/', InterviewReviewDetailView.as_view(), name='interview-review-detail'),
]

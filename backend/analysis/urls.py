from django.urls import path
from .views import AnalysisCreateView, AnalysisDetailView, AnalysisHistoryView

urlpatterns = [
    path('analyze/history/', AnalysisHistoryView.as_view(), name='analysis-history'),
    path('analyze/<int:analysis_id>/', AnalysisDetailView.as_view(), name='analysis-detail'),
    path('analyze/', AnalysisCreateView.as_view(), name='analysis-create'),
]

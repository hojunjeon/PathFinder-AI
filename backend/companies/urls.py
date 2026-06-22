from django.urls import path
from .views import (
    CompanyListView,
    CompanyResolveFromUrlView,
    CompanyJobListView,
    JobPostingResolveView,
    ManualJobPostingView,
    JobSearchView,
)

urlpatterns = [
    path('companies/', CompanyListView.as_view(), name='company-list'),
    path('companies/resolve/', CompanyResolveFromUrlView.as_view(), name='company-resolve'),
    path('companies/<int:company_id>/jobs/', CompanyJobListView.as_view(), name='company-jobs'),
    path('job-postings/resolve/', JobPostingResolveView.as_view(), name='job-posting-resolve'),
    path('job-postings/manual/', ManualJobPostingView.as_view(), name='job-posting-manual'),
    path('jobs/', JobSearchView.as_view(), name='job-search'),
]

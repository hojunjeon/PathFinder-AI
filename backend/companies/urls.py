from django.urls import path
from .views import CompanyListView, CompanyResolveFromUrlView, CompanyJobListView, JobSearchView

urlpatterns = [
    path('companies/', CompanyListView.as_view(), name='company-list'),
    path('companies/resolve/', CompanyResolveFromUrlView.as_view(), name='company-resolve'),
    path('companies/<int:company_id>/jobs/', CompanyJobListView.as_view(), name='company-jobs'),
    path('jobs/', JobSearchView.as_view(), name='job-search'),
]

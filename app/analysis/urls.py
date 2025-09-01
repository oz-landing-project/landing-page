from django.urls import path
from app.analysis.views import AnalysisView, AnalysisDetailView

app_name = "analysis"

urlpatterns = [
    path("analysis/", AnalysisView.as_view(), name="list-create"),
    path("analysis/<int:pk>/", AnalysisDetailView.as_view(), name="detail"),
]

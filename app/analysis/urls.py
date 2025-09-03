from django.urls import path
from app.analysis.views import AnalysisView, AnalysisDetailView

app_name = "analysis"

urlpatterns = [
    path("", AnalysisView.as_view(), name="list-create"),
    path("<int:pk>/", AnalysisDetailView.as_view(), name="detail"),
]

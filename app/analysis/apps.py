# app/analysis/apps.py
from django.apps import AppConfig

class AnalysisConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.analysis"
    label = "analysis"
    verbose_name = "분석"

from rest_framework import serializers
from .models import Analysis


class AnalysisSerializer(serializers.ModelSerializer):
    savings_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Analysis
        fields = [
            'id', 'total_income', 'total_expense', 'savings_amount',
            'analysis_period', 'ai_analysis', 'description',
            'period_start', 'period_end', 'savings_rate', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
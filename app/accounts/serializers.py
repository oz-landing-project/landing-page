from rest_framework import serializers
from .models import TransactionHistory, Analysis

class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')  # 자동 처리되는 필드


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')  # user는 자동 할당

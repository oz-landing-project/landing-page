from django.test import TestCase
from django.contrib.auth import get_user_model
from app.accounts.models import Account, TransactionHistory
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from app.analysis.analyzers import Analyzer
from app.analysis.models import Analysis

User = get_user_model()


class AnalyzerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="1234")
        self.account = Account.objects.create(
            user=self.user,
            account_number="123-456",
            bank_code="001",
            account_type="checking",
            balance=Decimal("1000.00"),
        )
        today = timezone.now().date()
        # 수입
        TransactionHistory.objects.create(
            account=self.account,
            amount=Decimal("500.00"),
            balance_after=Decimal("1500.00"),
            transaction_type="deposit",
            transaction_date=today,
            transaction_detail="급여",
        )
        # 지출
        TransactionHistory.objects.create(
            account=self.account,
            amount=Decimal("200.00"),
            balance_after=Decimal("1300.00"),
            transaction_type="withdrawal",
            transaction_date=today,
            transaction_detail="식비",
        )

        self.period_start = today - timedelta(days=7)
        self.period_end = today

    def test_analyzer_creates_analysis(self):
        analyzer = Analyzer(
            user=self.user,
            about="총 지출",
            type_="weekly",
            period_start=self.period_start,
            period_end=self.period_end,
        )
        analysis = analyzer.run()

        self.assertIsInstance(analysis, Analysis)
        self.assertEqual(analysis.user, self.user)
        self.assertEqual(analysis.about, "총 지출")
        self.assertTrue(analysis.result_image.name.endswith(".png"))

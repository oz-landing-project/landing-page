# 미사용 import 제거
# from django.test import TestCase  # 이 줄 삭제

# 테스트가 필요하면 다음과 같이 작성
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        # 실제 테스트 코드 작성
        pass
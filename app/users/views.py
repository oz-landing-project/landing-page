# 학생들이 구현할 API 뷰들
# 
# 필요한 import들 (주석 해제하고 사용하세요):
# from rest_framework import status, permissions
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.views import TokenRefreshView
# from .models import CustomUser
# from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer

# 5. JWT 토큰 갱신 API (이미 구현되어 있음)
# from rest_framework_simplejwt.views import TokenRefreshView
# 별도 구현 불필요, urls.py에서 바로 사용

# 추가 구현 팁:
# - authenticate() 함수는 django.contrib.auth에서 import
# - JWT 토큰 blacklist 기능 사용시 SIMPLE_JWT 설정에서 
#   'BLACKLIST_AFTER_ROTATION': True 설정 필요
# - 에러 처리는 try-except 블록 사용
# - HTTP 상태 코드는 status 모듈 사용 (status.HTTP_200_
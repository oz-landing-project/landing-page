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

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer


class RegisterView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"detail": "회원가입 성공"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  # blacklist 기능 사용 시에만 작동
            return Response({"detail": "로그아웃 되었습니다."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

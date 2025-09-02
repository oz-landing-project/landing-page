# app/users/views.py

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer


# -------------------------------
# 1) 회원가입 API
# -------------------------------
class RegisterView(CreateAPIView):
    permission_classes = [permissions.AllowAny]  # 인증 불필요
    serializer_class = RegisterSerializer        # 요청/응답에 사용할 시리얼라이저

    def create(self, request, *args, **kwargs):
        # 회원가입 로직: serializer 검증 → 저장 → 응답
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "name": user.name,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
        }
        return Response(data, status=status.HTTP_201_CREATED)


# -------------------------------
# 2) 로그인 API
# -------------------------------
class LoginView(CreateAPIView):  
    permission_classes = [permissions.AllowAny]  # 누구나 접근 가능
    serializer_class = LoginSerializer           # email/password 필드 자동 노출됨

    def post(self, request, *args, **kwargs):
        # 로그인 로직: serializer 검증 → 토큰/유저정보 반환
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        payload["user"] = serializer.get_user(None)
        return Response(payload, status=status.HTTP_200_OK)


# -------------------------------
# 3) 프로필 조회/수정/삭제 API
# -------------------------------
class ProfileView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]  # 인증 필요
    serializer_class = ProfileSerializer

    def get_object(self):
        # 현재 로그인한 사용자 객체 반환
        return self.request.user


# -------------------------------
# 4) 로그아웃 API
# -------------------------------
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # 인증 필요

    def post(self, request, *args, **kwargs):
        # refresh 토큰 받아서 blacklist 처리
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "refresh 토큰이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"detail": "유효하지 않은 refresh 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "로그아웃 되었습니다."}, status=status.HTTP_205_RESET_CONTENT)

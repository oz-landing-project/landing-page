from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer, ProfileSerializer


class RegisterView(CreateAPIView):
    """회원가입 뷰"""

    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            return Response({
                'success': True,
                'message': '회원가입이 완료되었습니다.',
                'data': {
                    'user_id': user.id,
                    'email': user.email,
                    'nickname': user.nickname
                }
            }, status=status.HTTP_201_CREATED)


class LoginView(CreateAPIView):
    """로그인 뷰"""

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)

        # 로그인 정보 업데이트
        user.login_count += 1
        user.last_login_ip = self._get_client_ip(request)
        user.save(update_fields=['login_count', 'last_login_ip'])

        return Response({
            'success': True,
            'message': '로그인 성공',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'email': user.email
            }
        }, status=status.HTTP_200_OK)

    @staticmethod
    def _get_client_ip(request):
        """클라이언트 IP 주소 가져오기"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(CreateAPIView):
    """로그아웃 뷰"""

    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logout(request)
        return Response({
            'success': True,
            'message': '로그아웃되었습니다.'
        }, status=status.HTTP_200_OK)


class ProfileView(RetrieveUpdateDestroyAPIView):
    """프로필 뷰 (조회, 수정, 삭제)"""

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response({
            'success': True,
            'message': '프로필 조회 성공',
            'data': serializer.data
        })

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'success': True,
            'message': '프로필이 업데이트되었습니다.',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        logout(request)

        return Response({
            'success': True,
            'message': '계정이 비활성화되었습니다.'
        }, status=status.HTTP_200_OK)
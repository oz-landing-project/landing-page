from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer, ProfileSerializer


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(APIView):
    """CSRF 토큰 발급 전용 엔드포인트"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="CSRF 토큰 발급",
        responses={200: openapi.Response(
            description="CSRF 토큰",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'csrf_token': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )}
    )
    def get(self, request):
        csrf_token = get_token(request)
        return Response({
            'success': True,
            'csrf_token': csrf_token
        })


class RegisterView(CreateAPIView):
    """회원가입 뷰 - CSRF 보호 적용"""

    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="회원가입",
        request_body=RegisterSerializer,
        responses={201: openapi.Response(
            description="회원가입 성공",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            )
        )}
    )
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
    """로그인 뷰 - CSRF 보호 적용"""

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="로그인",
        request_body=LoginSerializer,
        responses={200: openapi.Response(
            description="로그인 성공",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'csrf_token': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            )
        )}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)

        # 새로운 CSRF 토큰 생성 (로그인 후 보안상 토큰 갱신)
        csrf_token = get_token(request)

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
                'email': user.email,
                'csrf_token': csrf_token
            }
        }, status=status.HTTP_200_OK)

    @staticmethod
    def _get_client_ip(request):
        """클라이언트 IP 주소 가져오기"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(CreateAPIView):
    """로그아웃 뷰 - CSRF 보호 적용"""

    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logout(request)
        return Response({
            'success': True,
            'message': '로그아웃되었습니다.'
        }, status=status.HTTP_200_OK)


class ProfileView(RetrieveUpdateDestroyAPIView):
    """프로필 뷰 (조회, 수정, 삭제) - CSRF 보호 적용"""

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
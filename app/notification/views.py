from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """
    알림 관리 API
    
    사용자의 알림을 관리할 수 있습니다.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Swagger 스키마 생성 시 AnonymousUser 처리
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="알림을 읽음으로 표시",
        responses={200: openapi.Response(
            description="읽음 처리 완료",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )}
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """알림을 읽음으로 표시"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'marked as read'})

    @swagger_auto_schema(
        operation_description="읽지 않은 알림 조회",
        responses={200: NotificationSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """읽지 않은 알림 조회"""
        unread_notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response(serializer.data)
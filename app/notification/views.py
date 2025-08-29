from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from .models import Notification
from .serializers import NotificationSerializer, NotificationReadSerializer


class NotificationListView(generics.ListAPIView):
    """알림 목록 조회"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        # 읽음/안읽음 필터
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            if is_read.lower() in ['true', '1']:
                qs = qs.filter(is_read=True)
            elif is_read.lower() in ['false', '0']:
                qs = qs.filter(is_read=False)
        # 타입 필터
        ntype = self.request.query_params.get('type')
        if ntype:
            qs = qs.filter(type=ntype)
        return qs


class NotificationReadView(APIView):
    """벌크 읽음 처리 (ids 또는 all=true)"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return self._handle(request)

    def patch(self, request, *args, **kwargs):
        return self._handle(request)

    def _handle(self, request):
        serializer = NotificationReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data.get('ids')
        mark_all = serializer.validated_data.get('all', False)

        with transaction.atomic():
            qs = Notification.objects.filter(user=request.user, is_read=False)
            if ids and not mark_all:
                qs = qs.filter(id__in=ids)

            # 안전장치: ids도 all도 없으면 에러
            if not mark_all and not ids:
                return Response(
                    {'detail': 'ids 또는 all=true 중 하나는 지정해야 합니다.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            updated = qs.update(is_read=True)

        return Response({'updated': updated}, status=status.HTTP_200_OK)


class NotificationSingleReadView(APIView):
    """단건 읽음 처리: /notifications/{id}/read"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        with transaction.atomic():
            updated = Notification.objects.filter(
                user=request.user, pk=pk, is_read=False
            ).update(is_read=True)

            if not updated:
                return Response(
                    {'detail': '이미 읽음이거나 존재하지 않습니다.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response(status=status.HTTP_204_NO_CONTENT)

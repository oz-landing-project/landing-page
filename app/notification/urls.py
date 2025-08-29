from django.urls import path
from .views import (
    NotificationListView,
    NotificationReadView,
    NotificationSingleReadView,
)

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="list"),
    path("read", NotificationReadView.as_view(), name="read-bulk"),
    path("<int:pk>/read", NotificationSingleReadView.as_view(), name="read-single"),
]

"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API URL 패턴들을 먼저 정의
api_urlpatterns = [
    path('analysis/', include('app.analysis.urls')),
    path('accounts/', include('app.accounts.urls')),
    path('users/', include('app.users.urls')),
    path('notifications/', include('app.notification.urls')),
]

schema_view = get_schema_view(
   openapi.Info(
      title="Landing Page API",
      default_version='v1',
      description="Landing Page API Documentation - 가계부 관리 시스템",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
   patterns=[path('api/', include(api_urlpatterns))],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # API 엔드포인트들
    path('api/', include(api_urlpatterns)),
    # API 문서
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
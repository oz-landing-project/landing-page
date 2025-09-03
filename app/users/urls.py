# 구현할 URL 패턴들
#
# 구현해야 할 URL들:
# path('signup/', RegisterView.as_view(), name='signup'),
# path('login/', LoginView.as_view(), name='login'),
# path('logout/', LogoutView.as_view(), name='logout'),
# path('profile/', ProfileView.as_view(), name='profile'),
# path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, LogoutView, ProfileView

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

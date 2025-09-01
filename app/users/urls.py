from django.urls import path
from .views import (
    CSRFTokenView,
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView
)

app_name = 'users'

urlpatterns = [
    path('csrf-token/', CSRFTokenView.as_view(), name='csrf-token'),
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
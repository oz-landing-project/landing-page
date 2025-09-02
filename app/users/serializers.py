# 구현할 시리얼라이저들
#
# 구현해야 할 시리얼라이저들:
# 1. RegisterSerializer - 회원가입용
# 2. LoginSerializer - 로그인용  
# 3. ProfileSerializer - 프로필 조회/수정용
#
# 필요한 import들:
# from rest_framework import serializers
# from django.contrib.auth import authenticate
# from django.contrib.auth.password_validation import validate_password
# from rest_framework_simplejwt.tokens import RefreshToken
# from .models import CustomUser
# import re
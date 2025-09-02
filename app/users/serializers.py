from typing import Tuple
import re
#^ 파이선 타입힌트 / 가독성, 유지보수 향상
#해당 import로 refresh, access 토큰 중 어떤게 반환되는지 알 수 있음
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# ----------------------------
# 공용 유틸
# ----------------------------
def _issue_tokens_for_user(user: User) -> Tuple[str, str]:
    """
    주어진 사용자에 대해 (refresh, access) 토큰 문자열을 발급해 반환.
    """
    refresh = RefreshToken.for_user(user)
    return str(refresh), str(refresh.access_token)


def _generate_unique_username(base: str) -> str:
    """
    username 미입력 시 email 또는 nickname 기반으로 유니크한 username을 생성.
    """
    candidate = slugify(base) or "user"
    original = candidate
    i = 1
    while User.objects.filter(username=candidate).exists():
        i += 1
        candidate = f"{original}-{i}"
    return candidate


# ----------------------------
# 1) 회원가입용
# ----------------------------
class RegisterSerializer(serializers.ModelSerializer):
    # 비밀번호는 write_only, 확인 필드 추가
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password2 = serializers.CharField(write_only=True, trim_whitespace=False)

    # 선택 입력: username 미제공 시 자동 생성
    # username이 꼭 들어가야 하는 상황에서 만약에 비어있을 때 자동으로 채워주는 것, 지금 당장은 없어도 되는 코드
    #username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        # 사용자 입력 대상으로 적절히 노출
        fields = [
            "email",
            "username",
            "nickname",
            "name",
            "birth_date",
            "phone",
            "bio",
            "profile_image",
            "password",
            "password2",
        ]

    def validate_email(self, value: str) -> str:
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value

    def validate_phone(self, value: str) -> str:
        """
        한국 휴대폰 예시: 010-1234-5678 / 01012345678 모두 허용
        필요 시 규칙 수정 가능
        """
        if not value:
            return value
        digits = re.sub(r"\D", "", value)
        if not (9 <= len(digits) <= 12):
            raise serializers.ValidationError("연락처 형식이 올바르지 않습니다.")
        return value

    def validate(self, attrs):
        # 비밀번호 일치
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({"password2": "비밀번호가 일치하지 않습니다."})

        # Django 비밀번호 정책 검사
        validate_password(attrs.get("password"))
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password2", None)

        # username 자동 생성 (미입력 시)
        username = validated_data.get("username")
        if not username:
            base = validated_data.get("nickname") or validated_data["email"].split("@")[0]
            validated_data["username"] = _generate_unique_username(base)

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


# ----------------------------
# 2) 로그인용
# ----------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    # 응답에 토큰과 기본 프로필을 포함하면 프론트가 편해짐
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        user = self.context.get("user")
        if not user:
            return None
        return {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "name": user.name,
            "full_name": getattr(user, "full_name", None),
            "profile_image_url": user.get_profile_image_url() if hasattr(user, "get_profile_image_url") else None,
            "is_verified": user.is_verified,
        }

    def validate(self, attrs):
        email = attrs.get("email", "").lower().strip()
        password = attrs.get("password")

        # 기본 ModelBackend는 USERNAME_FIELD를 사용 -> username 파라미터로 이메일 전달
        user = authenticate(self.context.get("request"), username=email, password=password)
        if not user:
            # 존재 여부/비밀번호 오류 구분하지 않고 모호한 메시지 반환(보안)
            raise serializers.ValidationError("이메일 또는 비밀번호가 올바르지 않습니다.")

        if not user.is_active:
            raise serializers.ValidationError("비활성화된 계정입니다. 관리자에게 문의하세요.")

        refresh, access = _issue_tokens_for_user(user)
        # 컨텍스트에 user 저장해서 get_user에서 활용
        self.context["user"] = user

        return {
            "access": access,
            "refresh": refresh,
        }


# ----------------------------
# 3) 프로필 조회/수정용
# ----------------------------
class ProfileSerializer(serializers.ModelSerializer):
    # 읽기 전용
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)  # 이메일은 보통 프로필 수정에서 변경 X
    is_verified = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    last_login_ip = serializers.IPAddressField(read_only=True, required=False)
    login_count = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    profile_image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "nickname",
            "name",
            "full_name",
            "birth_date",
            "phone",
            "bio",
            "profile_image",
            "profile_image_url",
            "social_provider",
            "social_id",
            "is_verified",
            "last_login_ip",
            "login_count",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            # username/nickname은 프로젝트 정책에 따라 수정 가능/불가 결정
            "username": {"required": False},
            "nickname": {"required": False},
            "social_provider": {"read_only": True},
            "social_id": {"read_only": True},
        }

    def get_profile_image_url(self, obj):
        return obj.get_profile_image_url() if hasattr(obj, "get_profile_image_url") else None

    def validate_phone(self, value: str) -> str:
        if not value:
            return value
        digits = re.sub(r"\D", "", value)
        if not (9 <= len(digits) <= 12):
            raise serializers.ValidationError("연락처 형식이 올바르지 않습니다.")
        return value

    def update(self, instance, validated_data):
        # 이메일, 검증 상태 등 민감 필드는 수정 금지(읽기 전용으로 이미 막았지만 방어적으로 한번 더)
        for locked in ["email", "is_verified", "login_count", "last_login_ip", "created_at", "updated_at", "social_id", "social_provider"]:
            validated_data.pop(locked, None)
        return super().update(instance, validated_data)

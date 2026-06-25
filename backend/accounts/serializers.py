import json

from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import Profile, User

MAX_PROFILE_SECTION_CHARS = 12000


class SignupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True, max_length=50)
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)
    terms_agreed = serializers.BooleanField(write_only=True)
    privacy_agreed = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'name',
            'password',
            'password_confirm',
            'terms_agreed',
            'privacy_agreed',
        ]

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError('이미 가입된 이메일입니다.')
        return normalized

    def validate_name(self, value):
        normalized = ' '.join(value.split())
        if len(normalized) < 2:
            raise serializers.ValidationError('이름은 2자 이상 입력해 주세요.')
        return normalized

    def validate(self, attrs):
        password = attrs['password']
        errors = {}
        if password != attrs['password_confirm']:
            errors['password_confirm'] = '비밀번호가 일치하지 않습니다.'
        has_english_letter = any(char.isascii() and char.isalpha() for char in password)
        if not has_english_letter or not any(char.isdigit() for char in password):
            errors['password'] = '비밀번호는 영문과 숫자를 각각 1자 이상 포함해야 합니다.'
        if not attrs['terms_agreed']:
            errors['terms_agreed'] = '서비스 이용약관에 동의해 주세요.'
        if not attrs['privacy_agreed']:
            errors['privacy_agreed'] = '개인정보 수집 및 이용에 동의해 주세요.'
        if errors:
            raise serializers.ValidationError(errors)

        try:
            password_validation.validate_password(password, user=User(email=attrs['email']))
        except DjangoValidationError as error:
            raise serializers.ValidationError({'password': list(error.messages)}) from error
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        name = validated_data.pop('name')
        validated_data.pop('password_confirm')
        validated_data.pop('terms_agreed')
        validated_data.pop('privacy_agreed')
        agreed_at = timezone.now()
        user = User.objects.create_user(
            **validated_data,
            terms_agreed_at=agreed_at,
            privacy_agreed_at=agreed_at,
        )
        Profile.objects.create(user=user, name=name)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data['email'].strip().lower()
        user = authenticate(username=email, password=data['password'])
        if not user:
            raise serializers.ValidationError('이메일 또는 비밀번호가 올바르지 않습니다.')
        if not user.is_active:
            raise serializers.ValidationError('비활성화된 계정입니다.')
        data['user'] = user
        return data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['name', 'major', 'education', 'careers',
                  'cover_letters', 'projects', 'awards', 'certificates', 'updated_at']
        read_only_fields = ['updated_at']

    def validate(self, attrs):
        for field in ['careers', 'cover_letters', 'projects', 'awards', 'certificates']:
            if field not in attrs:
                continue
            encoded = json.dumps(attrs[field], ensure_ascii=False)
            if len(encoded) > MAX_PROFILE_SECTION_CHARS:
                raise serializers.ValidationError({
                    field: f'{field} is too large. Limit is {MAX_PROFILE_SECTION_CHARS} characters.'
                })
        return attrs

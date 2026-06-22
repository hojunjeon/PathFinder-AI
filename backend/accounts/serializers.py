from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Profile
import json

MAX_PROFILE_SECTION_CHARS = 12000


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('이메일 또는 비밀번호가 올바르지 않습니다.')
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

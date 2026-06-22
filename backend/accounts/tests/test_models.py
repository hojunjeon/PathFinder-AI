import pytest
from accounts.models import User, Profile


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(email='test@test.com', password='pass1234')
    assert user.email == 'test@test.com'
    assert user.check_password('pass1234')
    assert user.is_active is True


@pytest.mark.django_db
def test_profile_auto_fields():
    user = User.objects.create_user(email='profile@test.com', password='pass1234')
    profile = Profile.objects.create(user=user, name='홍길동', major='컴퓨터공학')
    assert profile.careers == []
    assert profile.projects == []
    assert str(profile) == 'Profile(profile@test.com)'

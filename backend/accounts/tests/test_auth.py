import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    from accounts.models import Profile
    u = User.objects.create_user(email='user@test.com', password='pass1234!')
    Profile.objects.create(user=u)
    return u


@pytest.mark.django_db
def test_signup(client):
    resp = client.post('/api/auth/signup/', {'email': 'new@test.com', 'password': 'pass1234!'})
    assert resp.status_code == 201
    assert 'access' in resp.data
    assert User.objects.filter(email='new@test.com').exists()


@pytest.mark.django_db
def test_signup_duplicate_email(client, user):
    resp = client.post('/api/auth/signup/', {'email': 'user@test.com', 'password': 'pass1234!'})
    assert resp.status_code == 400


@pytest.mark.django_db
def test_login(client, user):
    resp = client.post('/api/auth/login/', {'email': 'user@test.com', 'password': 'pass1234!'})
    assert resp.status_code == 200
    assert 'access' in resp.data


@pytest.mark.django_db
def test_login_wrong_password(client, user):
    resp = client.post('/api/auth/login/', {'email': 'user@test.com', 'password': 'wrong'})
    assert resp.status_code == 400


@pytest.mark.django_db
def test_profile_get(client, user):
    client.force_authenticate(user=user)
    resp = client.get('/api/profile/')
    assert resp.status_code == 200
    assert 'name' in resp.data


@pytest.mark.django_db
def test_profile_put(client, user):
    client.force_authenticate(user=user)
    resp = client.put('/api/profile/', {'name': '홍길동', 'major': '컴퓨터공학'})
    assert resp.status_code == 200
    assert resp.data['name'] == '홍길동'


@pytest.mark.django_db
def test_profile_auth_path_still_supported(client, user):
    client.force_authenticate(user=user)
    resp = client.get('/api/auth/profile/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_profile_requires_auth(client):
    resp = client.get('/api/profile/')
    assert resp.status_code == 401

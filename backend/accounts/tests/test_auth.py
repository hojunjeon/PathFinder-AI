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
    resp = client.post('/api/auth/signup/', {
        'email': 'New@Test.com',
        'name': '홍길동',
        'password': 'pass1234!',
        'password_confirm': 'pass1234!',
        'terms_agreed': True,
        'privacy_agreed': True,
    })
    assert resp.status_code == 201
    assert 'access' in resp.data
    assert User.objects.filter(email='new@test.com').exists()
    user = User.objects.get(email='new@test.com')
    assert user.profile.name == '홍길동'
    assert user.terms_agreed_at is not None
    assert user.privacy_agreed_at is not None


@pytest.mark.django_db
def test_signup_duplicate_email(client, user):
    resp = client.post('/api/auth/signup/', {
        'email': 'USER@test.com',
        'name': '홍길동',
        'password': 'pass1234!',
        'password_confirm': 'pass1234!',
        'terms_agreed': True,
        'privacy_agreed': True,
    })
    assert resp.status_code == 400
    assert resp.data['email'][0] == '이미 가입된 이메일입니다.'


@pytest.mark.django_db
def test_signup_requires_account_fields_and_agreements(client):
    resp = client.post('/api/auth/signup/', {
        'email': 'new@test.com',
        'name': '홍길동',
        'password': 'pass1234!',
        'password_confirm': 'different123!',
        'terms_agreed': False,
        'privacy_agreed': False,
    })
    assert resp.status_code == 400
    assert 'password_confirm' in resp.data
    assert 'terms_agreed' in resp.data
    assert 'privacy_agreed' in resp.data


@pytest.mark.django_db
def test_signup_requires_name(client):
    resp = client.post('/api/auth/signup/', {
        'email': 'new@test.com',
        'name': '',
        'password': 'pass1234!',
        'password_confirm': 'pass1234!',
        'terms_agreed': True,
        'privacy_agreed': True,
    })
    assert resp.status_code == 400
    assert 'name' in resp.data


@pytest.mark.django_db
def test_signup_rejects_password_without_letters_and_numbers(client):
    resp = client.post('/api/auth/signup/', {
        'email': 'new@test.com',
        'name': '홍길동',
        'password': 'abcdefgh!',
        'password_confirm': 'abcdefgh!',
        'terms_agreed': True,
        'privacy_agreed': True,
    })
    assert resp.status_code == 400
    assert 'password' in resp.data


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

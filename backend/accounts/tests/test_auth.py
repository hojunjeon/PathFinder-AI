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
        'name': '홍길동',
        'email': 'new@test.com',
        'password': 'pass1234!',
        'password_confirm': 'pass1234!',
    })
    assert resp.status_code == 201
    assert 'access' in resp.data
    user = User.objects.get(email='new@test.com')
    assert user.profile.name == '홍길동'


@pytest.mark.django_db
def test_signup_duplicate_email(client, user):
    resp = client.post('/api/auth/signup/', {
        'name': '홍길동',
        'email': 'user@test.com',
        'password': 'pass1234!',
        'password_confirm': 'pass1234!',
    })
    assert resp.status_code == 400


@pytest.mark.django_db
def test_signup_rejects_password_mismatch(client):
    resp = client.post('/api/auth/signup/', {
        'name': '홍길동',
        'email': 'new@test.com',
        'password': 'pass1234!',
        'password_confirm': 'different123!',
    })

    assert resp.status_code == 400
    assert 'password_confirm' in resp.data
    assert not User.objects.filter(email='new@test.com').exists()


@pytest.mark.django_db
def test_signup_requires_account_fields(client):
    resp = client.post('/api/auth/signup/', {
        'email': 'new@test.com',
        'password': 'pass1234!',
    })

    assert resp.status_code == 400
    assert 'name' in resp.data
    assert 'password_confirm' in resp.data


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
    assert resp.data['email'] == 'user@test.com'


@pytest.mark.django_db
def test_profile_put(client, user):
    client.force_authenticate(user=user)
    resp = client.put('/api/profile/', {
        'name': '홍길동',
        'email': 'changed@test.com',
        'major': '컴퓨터공학',
    })
    assert resp.status_code == 200
    assert resp.data['name'] == '홍길동'
    assert resp.data['email'] == 'user@test.com'
    user.refresh_from_db()
    assert user.email == 'user@test.com'


@pytest.mark.django_db
def test_profile_api_ignores_cover_letters_as_profile_data(client, user):
    client.force_authenticate(user=user)

    get_resp = client.get('/api/profile/')
    put_resp = client.put('/api/profile/', {
        'cover_letters': [{'question': '직무별 문항', 'answer': '분석 단계 전용'}],
    }, format='json')

    user.profile.refresh_from_db()
    assert get_resp.status_code == 200
    assert put_resp.status_code == 200
    assert 'cover_letters' not in get_resp.data
    assert 'cover_letters' not in put_resp.data


@pytest.mark.django_db
def test_profile_auth_path_still_supported(client, user):
    client.force_authenticate(user=user)
    resp = client.get('/api/auth/profile/')
    assert resp.status_code == 200


@pytest.mark.django_db
def test_profile_requires_auth(client):
    resp = client.get('/api/profile/')
    assert resp.status_code == 401

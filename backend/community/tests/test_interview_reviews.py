import pytest
from rest_framework.test import APIClient

from accounts.models import Profile, User
from community.models import InterviewReview


@pytest.fixture
def users(db):
    user = User.objects.create_user(email='writer@test.com', password='pass1234!')
    Profile.objects.create(user=user, name='Writer')
    other = User.objects.create_user(email='other@test.com', password='pass1234!')
    Profile.objects.create(user=other)
    return user, other


@pytest.fixture
def auth_client(users):
    user, _ = users
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


def review_payload(**overrides):
    payload = {
        'company_name': 'PathFinder Corp',
        'job_title': 'Backend Developer',
        'title': 'Django API 면접 후기',
        'interview_type': 'technical',
        'interview_date': '2026-06-20',
        'difficulty': 4,
        'result_status': 'passed',
        'interview_questions': 'DRF 인증 흐름과 트랜잭션 처리 질문을 받았습니다.',
        'content': '전체적으로 프로젝트 경험을 깊게 검증하는 면접이었습니다.',
        'tips': '본인이 작성한 API의 장애 대응 방식을 정리해두면 좋습니다.',
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_create_interview_review(auth_client):
    client, user = auth_client
    resp = client.post('/api/community/reviews/', review_payload(), format='json')

    assert resp.status_code == 201
    assert resp.data['company_name'] == 'PathFinder Corp'
    assert resp.data['author_name'] == 'Writer'
    assert resp.data['is_owner'] is True
    assert InterviewReview.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_create_interview_review_accepts_frontend_empty_date_payload(auth_client):
    client, user = auth_client
    resp = client.post(
        '/api/community/reviews/',
        review_payload(interview_date=None, interview_questions='', tips=''),
        format='json',
    )

    assert resp.status_code == 201
    review = InterviewReview.objects.get(user=user, title=resp.data['title'])
    assert review.interview_date is None
    assert review.interview_questions == ''
    assert review.tips == ''


@pytest.mark.django_db
def test_list_interview_reviews_requires_auth(users):
    user, _ = users
    InterviewReview.objects.create(user=user, **review_payload())

    anon = APIClient()
    assert anon.get('/api/community/reviews/').status_code == 401

    client = APIClient()
    client.force_authenticate(user=user)
    resp = client.get('/api/community/reviews/?q=Django')
    assert resp.status_code == 200
    assert resp.data['count'] == 1
    assert resp.data['results'][0]['title'] == 'Django API 면접 후기'


@pytest.mark.django_db
def test_author_can_update_and_delete_review(auth_client):
    client, user = auth_client
    review = InterviewReview.objects.create(user=user, **review_payload())

    update_resp = client.patch(
        f'/api/community/reviews/{review.id}/',
        {'difficulty': 5, 'tips': '꼬리 질문 대비가 가장 중요합니다.'},
        format='json',
    )
    assert update_resp.status_code == 200
    assert update_resp.data['difficulty'] == 5

    delete_resp = client.delete(f'/api/community/reviews/{review.id}/')
    assert delete_resp.status_code == 204
    assert not InterviewReview.objects.filter(id=review.id).exists()


@pytest.mark.django_db
def test_non_author_cannot_update_or_delete_review(users):
    user, other = users
    review = InterviewReview.objects.create(user=user, **review_payload())
    client = APIClient()
    client.force_authenticate(user=other)

    update_resp = client.patch(f'/api/community/reviews/{review.id}/', {'title': '수정 시도'}, format='json')
    delete_resp = client.delete(f'/api/community/reviews/{review.id}/')

    assert update_resp.status_code == 403
    assert delete_resp.status_code == 403
    review.refresh_from_db()
    assert review.title == 'Django API 면접 후기'

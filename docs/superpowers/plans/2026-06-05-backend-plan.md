# PathFinder AI — Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Django(:8080) + FastAPI(:8081) 백엔드를 구축한다. Django는 인증/프로필/기업DB/분석 오케스트레이션을 담당하고, FastAPI는 LLM 호출 전용 내부 서비스로 동작한다.

**Architecture:** Vue는 Django(:8080)만 바라본다. Django가 LLM 호출이 필요할 때만 FastAPI(:8081)를 내부 호출(httpx)한다. FastAPI는 브라우저에 직접 노출되지 않는다.

**Tech Stack:** Python 3.11+, Django 5.x, djangorestframework, djangorestframework-simplejwt, httpx, FastAPI, uvicorn, SQLite

---

## Task 1: 프로젝트 스캐폴딩

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/manage.py` (django-admin 생성)
- Create: `backend/config/settings.py`
- Create: `backend/config/urls.py`
- Create: `llm_server/requirements.txt`
- Create: `llm_server/main.py`

- [ ] **Step 1: Django 프로젝트 생성**

```bash
cd c:\Users\user\Desktop\new_pjt
mkdir backend llm_server
cd backend
python -m venv venv
venv\Scripts\activate
pip install django djangorestframework djangorestframework-simplejwt httpx django-cors-headers pytest pytest-django
pip freeze > requirements.txt
django-admin startproject config .
python manage.py startapp accounts
python manage.py startapp companies
python manage.py startapp analysis
```

- [ ] **Step 2: `backend/config/settings.py` 수정**

```python
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-pathfinder-dev-key-change-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'accounts',
    'companies',
    'analysis',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

LLM_SERVER_URL = 'http://localhost:8081'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_TZ = True
```

- [ ] **Step 3: `backend/config/urls.py` 작성**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('companies.urls')),
    path('api/', include('analysis.urls')),
]
```

- [ ] **Step 4: FastAPI 서버 초기 설정**

```bash
cd c:\Users\user\Desktop\new_pjt\llm_server
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn httpx python-dotenv
pip freeze > requirements.txt
```

- [ ] **Step 5: `llm_server/main.py` 기본 구조 작성**

```python
from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="PathFinder LLM Server", docs_url=None, redoc_url=None)

GMS_KEY = os.getenv("GMS_KEY", "")
GMS_URL = "https://gms.ssafy.io/gmsapi/api.openai.com/v1/chat/completions"


class RoadmapRequest(BaseModel):
    user_profile: dict
    job_posting_text: str
    company_info: dict
    job_info: dict
    selected_interview_types: list[str]


class RoadmapResponse(BaseModel):
    text_roadmap: str
    timeline_data: list[dict]


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/llm/roadmap", response_model=RoadmapResponse)
async def generate_roadmap(req: RoadmapRequest):
    prompt = _build_prompt(req)
    response_text = await _call_gpt(prompt)
    return _parse_response(response_text)


def _build_prompt(req: RoadmapRequest) -> str:
    interview_stages = req.job_info.get("interview_stages", [])
    stages_text = "\n".join(
        [f"  {s['order']}차: {s['type']} - {s.get('desc', '')}" for s in interview_stages]
    )
    selected = ", ".join(req.selected_interview_types)

    return f"""당신은 취업 준비 전문 코치입니다. 아래 정보를 바탕으로 맞춤형 면접 준비 로드맵을 작성해주세요.

## 지원자 정보
- 전공: {req.user_profile.get('전공', '미입력')}
- 학력: {req.user_profile.get('학력', '미입력')}
- 경력사항: {req.user_profile.get('경력사항', [])}
- 프로젝트: {req.user_profile.get('프로젝트', [])}
- 자격증: {req.user_profile.get('자격증', [])}

## 채용공고 내용 (최우선 참고)
{req.job_posting_text}

## 기업 정보 (참고용)
- 인재상: {req.company_info.get('인재상', '')}
- 기업규모: {req.company_info.get('기업규모', '')}
- 조직문화: {req.company_info.get('조직문화_키워드', [])}

## 직무 요구사항 (참고용)
- 요구역량: {req.job_info.get('요구역량', [])}
- 학습추천분야: {req.job_info.get('학습추천분야', [])}

## 면접 단계
{stages_text}
선택한 면접 유형: {selected}

## 출력 형식 (반드시 아래 JSON 형식으로만 답변)
{{
  "text_roadmap": "주차별 준비 계획 전체 텍스트",
  "timeline_data": [
    {{"week": 1, "title": "1주차 목표", "tasks": ["할일1", "할일2"]}},
    {{"week": 2, "title": "2주차 목표", "tasks": ["할일1", "할일2"]}}
  ]
}}"""


async def _call_gpt(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GMS_KEY}",
    }
    payload = {
        "model": "gpt-5-nano",
        "messages": [
            {"role": "developer", "content": "Answer in Korean"},
            {"role": "user", "content": prompt},
        ],
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(GMS_URL, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


def _parse_response(text: str) -> RoadmapResponse:
    import json, re
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return RoadmapResponse(text_roadmap=text, timeline_data=[])
    try:
        data = json.loads(match.group())
        return RoadmapResponse(
            text_roadmap=data.get("text_roadmap", text),
            timeline_data=data.get("timeline_data", []),
        )
    except json.JSONDecodeError:
        return RoadmapResponse(text_roadmap=text, timeline_data=[])
```

- [ ] **Step 6: 서버 기동 확인**

```bash
# Django
cd backend && python manage.py runserver 8080

# FastAPI (새 터미널)
cd llm_server && uvicorn main:app --port 8081 --reload
```

Expected: Django http://localhost:8080/admin/ 접속 가능, FastAPI http://localhost:8081/health → `{"status":"ok"}`

- [ ] **Step 7: Commit**

```bash
git init
git add .
git commit -m "feat: scaffold Django + FastAPI project structure"
```

---

## Task 2: 커스텀 User 모델 + Profile 모델

**Files:**
- Modify: `backend/accounts/models.py`
- Create: `backend/accounts/migrations/0001_initial.py` (자동 생성)

- [ ] **Step 1: `backend/accounts/models.py` 작성**

```python
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=50, blank=True)
    major = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=200, blank=True)
    careers = models.JSONField(default=list)        # [{title, company, period, description}]
    cover_letters = models.JSONField(default=list)  # [{question, answer}]
    projects = models.JSONField(default=list)       # [{name, period, description, stack}]
    awards = models.JSONField(default=list)         # [{title, org, date}]
    certificates = models.JSONField(default=list)   # [{name, date}]
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return f"Profile({self.user.email})"
```

- [ ] **Step 2: 마이그레이션 생성 및 적용**

```bash
cd backend
python manage.py makemigrations accounts
python manage.py migrate
```

Expected: `db.sqlite3` 생성, `users`, `profiles` 테이블 확인

- [ ] **Step 3: 테스트 파일 작성**

`backend/accounts/tests/test_models.py`

```python
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
```

- [ ] **Step 4: pytest 설정 파일 작성**

`backend/pytest.ini`

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests/test_*.py
python_classes = Test*
python_functions = test_*
```

- [ ] **Step 5: 테스트 실행**

```bash
cd backend
pytest accounts/tests/test_models.py -v
```

Expected: 2 passed

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "feat: add User and Profile models"
```

---

## Task 3: 인증 API (회원가입, 로그인, JWT 갱신)

**Files:**
- Create: `backend/accounts/serializers.py`
- Create: `backend/accounts/views.py`
- Create: `backend/accounts/urls.py`
- Create: `backend/accounts/tests/test_auth.py`

- [ ] **Step 1: `backend/accounts/serializers.py` 작성**

```python
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Profile


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
```

- [ ] **Step 2: `backend/accounts/views.py` 작성**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignupSerializer, LoginSerializer, ProfileSerializer
from .models import Profile


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class ProfileView(APIView):
    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
```

- [ ] **Step 3: `backend/accounts/urls.py` 작성**

```python
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignupView, LoginView, ProfileView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
```

- [ ] **Step 4: `backend/accounts/tests/test_auth.py` 작성**

```python
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email='user@test.com', password='pass1234!')


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
    resp = client.get('/api/auth/profile/')
    assert resp.status_code == 200
    assert 'name' in resp.data


@pytest.mark.django_db
def test_profile_put(client, user):
    client.force_authenticate(user=user)
    resp = client.put('/api/auth/profile/', {'name': '홍길동', 'major': '컴퓨터공학'})
    assert resp.status_code == 200
    assert resp.data['name'] == '홍길동'


@pytest.mark.django_db
def test_profile_requires_auth(client):
    resp = client.get('/api/auth/profile/')
    assert resp.status_code == 401
```

- [ ] **Step 5: 테스트 실행**

```bash
cd backend
pytest accounts/tests/test_auth.py -v
```

Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "feat: add auth APIs (signup, login, JWT, profile CRUD)"
```

---

## Task 4: Company & Job 모델 + API

**Files:**
- Create: `backend/companies/models.py`
- Create: `backend/companies/serializers.py`
- Create: `backend/companies/views.py`
- Create: `backend/companies/urls.py`
- Create: `backend/companies/tests/test_companies.py`

- [ ] **Step 1: `backend/companies/models.py` 작성**

```python
from django.db import models


class Company(models.Model):
    class Size(models.TextChoices):
        LARGE = 'large', '대기업'
        MID = 'mid', '중견기업'
        STARTUP = 'startup', '스타트업'

    company_name = models.CharField(max_length=100, unique=True)
    industry = models.CharField(max_length=50)
    size = models.CharField(max_length=20, choices=Size.choices, default=Size.LARGE)
    talent_description = models.TextField(blank=True)
    culture_keywords = models.JSONField(default=list)

    class Meta:
        db_table = 'companies'

    def __str__(self):
        return self.company_name


class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    job_title = models.CharField(max_length=200)
    annual_salary_krw = models.BigIntegerField(default=0)
    required_experience_years = models.IntegerField(default=0)
    applicant_count = models.IntegerField(default=0)
    interview_stages = models.JSONField(default=list)
    required_skills = models.JSONField(default=list)
    job_description = models.TextField(blank=True)
    preferred_qualifications = models.JSONField(default=list)
    recommended_study_areas = models.JSONField(default=list)

    class Meta:
        db_table = 'jobs'

    def __str__(self):
        return f"{self.company.company_name} - {self.job_title}"
```

- [ ] **Step 2: 마이그레이션**

```bash
cd backend
python manage.py makemigrations companies
python manage.py migrate
```

- [ ] **Step 3: `backend/companies/serializers.py` 작성**

```python
from rest_framework import serializers
from .models import Company, Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id', 'job_title', 'annual_salary_krw', 'required_experience_years',
            'applicant_count', 'interview_stages', 'required_skills',
            'job_description', 'preferred_qualifications', 'recommended_study_areas',
        ]


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'company_name', 'industry', 'size', 'talent_description', 'culture_keywords']


class CompanyDetailSerializer(serializers.ModelSerializer):
    jobs = JobSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'company_name', 'industry', 'size',
                  'talent_description', 'culture_keywords', 'jobs']
```

- [ ] **Step 4: `backend/companies/views.py` 작성**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Company, Job
from .serializers import CompanySerializer, CompanyDetailSerializer, JobSerializer

NOT_SUPPORTED_MSG = "현재 지원하지 않는 기업입니다. 추후 지원 예정입니다."


class CompanyListView(APIView):
    def get(self, request):
        name = request.query_params.get('name', '')
        if name:
            try:
                company = Company.objects.get(company_name__icontains=name)
                return Response(CompanySerializer(company).data)
            except Company.DoesNotExist:
                return Response({'message': NOT_SUPPORTED_MSG, 'supported': False},
                                status=status.HTTP_404_NOT_FOUND)
        companies = Company.objects.all().order_by('company_name')
        return Response(CompanySerializer(companies, many=True).data)


class CompanyJobListView(APIView):
    def get(self, request, company_id):
        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return Response({'message': NOT_SUPPORTED_MSG}, status=status.HTTP_404_NOT_FOUND)
        jobs = company.jobs.all()
        return Response(JobSerializer(jobs, many=True).data)
```

- [ ] **Step 5: `backend/companies/urls.py` 작성**

```python
from django.urls import path
from .views import CompanyListView, CompanyJobListView

urlpatterns = [
    path('companies/', CompanyListView.as_view(), name='company-list'),
    path('companies/<int:company_id>/jobs/', CompanyJobListView.as_view(), name='company-jobs'),
]
```

- [ ] **Step 6: `backend/companies/tests/test_companies.py` 작성**

```python
import pytest
from rest_framework.test import APIClient
from accounts.models import User
from companies.models import Company, Job


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(email='u@test.com', password='pass1234!')
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def company(db):
    return Company.objects.create(
        company_name='카카오',
        industry='IT',
        size='large',
        talent_description='도전적이고 창의적인 인재',
        culture_keywords=['수평적', '자율']
    )


@pytest.fixture
def job(db, company):
    return Job.objects.create(
        company=company,
        job_title='주니어 백엔드 엔지니어',
        annual_salary_krw=55000000,
        required_experience_years=1,
        applicant_count=276,
        interview_stages=[{"order": 1, "type": "coding_test", "desc": ""}],
        required_skills=['Python', 'Spring'],
    )


@pytest.mark.django_db
def test_company_list(auth_client, company):
    resp = auth_client.get('/api/companies/')
    assert resp.status_code == 200
    assert len(resp.data) == 1


@pytest.mark.django_db
def test_company_search_found(auth_client, company):
    resp = auth_client.get('/api/companies/?name=카카오')
    assert resp.status_code == 200
    assert resp.data['company_name'] == '카카오'
    assert resp.data['supported'] is not False  # found 시 message 없음


@pytest.mark.django_db
def test_company_search_not_found(auth_client):
    resp = auth_client.get('/api/companies/?name=없는기업')
    assert resp.status_code == 404
    assert resp.data['supported'] is False
    assert '추후 지원 예정' in resp.data['message']


@pytest.mark.django_db
def test_company_jobs(auth_client, company, job):
    resp = auth_client.get(f'/api/companies/{company.id}/jobs/')
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]['job_title'] == '주니어 백엔드 엔지니어'
```

- [ ] **Step 7: 테스트 실행**

```bash
cd backend
pytest companies/tests/test_companies.py -v
```

Expected: 4 passed

- [ ] **Step 8: Commit**

```bash
git add .
git commit -m "feat: add Company and Job models + APIs"
```

---

## Task 5: 데이터 시딩 (jobs_careers.jsonl → DB)

**Files:**
- Create: `backend/companies/management/commands/seed_companies.py`

- [ ] **Step 1: management command 디렉토리 생성**

```bash
mkdir -p backend/companies/management/commands
touch backend/companies/management/__init__.py
touch backend/companies/management/commands/__init__.py
```

- [ ] **Step 2: `backend/companies/management/commands/seed_companies.py` 작성**

```python
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from companies.models import Company, Job

JSONL_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / 'jobs_careers' / 'jobs_careers.jsonl'

# PathFinder 전용 필드 (기업별 기본값, 실제 운영 시 수동 보완 필요)
COMPANY_DEFAULTS = {
    '카카오': {
        'size': 'large',
        'talent_description': '도전적이고 창의적인 인재, 기술로 세상을 바꾸는 사람',
        'culture_keywords': ['수평적', '자율', '성과 중심'],
        'interview_stages_default': [
            {"order": 1, "type": "coding_test", "desc": "알고리즘 코딩테스트"},
            {"order": 2, "type": "technical", "desc": "기술 면접"},
            {"order": 3, "type": "personality", "desc": "임원 인성 면접"},
        ],
    },
    '삼성전자': {
        'size': 'large',
        'talent_description': '창의와 도전 정신을 가진 글로벌 인재',
        'culture_keywords': ['글로벌', '혁신', '도전'],
        'interview_stages_default': [
            {"order": 1, "type": "coding_test", "desc": "GSAT"},
            {"order": 2, "type": "practical", "desc": "직무 면접"},
            {"order": 3, "type": "personality", "desc": "임원 면접"},
        ],
    },
    # 나머지 기업은 기본값 적용
}

DEFAULT_STAGES = [
    {"order": 1, "type": "practical", "desc": "직무 면접"},
    {"order": 2, "type": "personality", "desc": "인성 면접"},
]


class Command(BaseCommand):
    help = 'jobs_careers.jsonl 데이터를 Company/Job 테이블에 시딩합니다.'

    def handle(self, *args, **options):
        if not JSONL_PATH.exists():
            self.stderr.write(f'파일 없음: {JSONL_PATH}')
            return

        records = []
        with open(JSONL_PATH, encoding='utf-8') as f:
            for line in f:
                records.append(json.loads(line.strip()))

        companies_data = {}
        for r in records:
            name = r['company_name']
            if name not in companies_data:
                companies_data[name] = {'industry': r['industry'], 'jobs': []}
            companies_data[name]['jobs'].append(r)

        created_companies = 0
        created_jobs = 0

        for company_name, data in companies_data.items():
            defaults_info = COMPANY_DEFAULTS.get(company_name, {})
            company, created = Company.objects.get_or_create(
                company_name=company_name,
                defaults={
                    'industry': data['industry'],
                    'size': defaults_info.get('size', 'large'),
                    'talent_description': defaults_info.get('talent_description', ''),
                    'culture_keywords': defaults_info.get('culture_keywords', []),
                }
            )
            if created:
                created_companies += 1

            stages = defaults_info.get('interview_stages_default', DEFAULT_STAGES)
            for r in data['jobs']:
                _, job_created = Job.objects.get_or_create(
                    company=company,
                    job_title=r['job_title'],
                    defaults={
                        'annual_salary_krw': r['annual_salary_krw'],
                        'required_experience_years': r['required_experience_years'],
                        'applicant_count': r['applicant_count'],
                        'interview_stages': stages,
                        'required_skills': [],
                        'job_description': '',
                        'preferred_qualifications': [],
                        'recommended_study_areas': [],
                    }
                )
                if job_created:
                    created_jobs += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'완료: 기업 {created_companies}개, 직무 {created_jobs}개 생성'
            )
        )
```

- [ ] **Step 3: 시딩 실행**

```bash
cd backend
python manage.py seed_companies
```

Expected: `완료: 기업 45개, 직무 N개 생성`

- [ ] **Step 4: 확인**

```bash
python manage.py shell -c "from companies.models import Company, Job; print(Company.objects.count(), Job.objects.count())"
```

Expected: 45개 기업, 10000개 이하 직무(중복 제거됨)

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "feat: add seed_companies management command"
```

---

## Task 6: Analysis 모델 + API (Django 오케스트레이터)

**Files:**
- Create: `backend/analysis/models.py`
- Create: `backend/analysis/serializers.py`
- Create: `backend/analysis/views.py`
- Create: `backend/analysis/urls.py`
- Create: `backend/analysis/services.py`
- Create: `backend/analysis/tests/test_analysis.py`

- [ ] **Step 1: `backend/analysis/models.py` 작성**

```python
from django.db import models
from accounts.models import User
from companies.models import Job


class Analysis(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', '대기'
        DONE = 'done', '완료'
        FAILED = 'failed', '실패'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, related_name='analyses')
    job_posting_url = models.URLField()
    submitted_cover_letter = models.TextField(blank=True)
    selected_interview_types = models.JSONField(default=list)
    text_roadmap = models.TextField(blank=True)
    timeline_data = models.JSONField(default=list)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analyses'
        ordering = ['-created_at']

    def __str__(self):
        return f"Analysis({self.user.email}, {self.status})"
```

- [ ] **Step 2: 마이그레이션**

```bash
cd backend
python manage.py makemigrations analysis
python manage.py migrate
```

- [ ] **Step 3: `backend/analysis/services.py` 작성 (FastAPI 호출 로직)**

```python
import httpx
from django.conf import settings
from accounts.models import Profile
from companies.models import Job

LLM_URL = f"{settings.LLM_SERVER_URL}/llm/roadmap"


def build_llm_payload(user, job: Job, job_posting_url: str,
                      submitted_cover_letter: str, selected_interview_types: list) -> dict:
    try:
        profile = user.profile
        user_profile = {
            '전공': profile.major,
            '학력': profile.education,
            '경력사항': profile.careers,
            '프로젝트': profile.projects,
            '자소서': submitted_cover_letter or profile.cover_letters,
            '자격증': profile.certificates,
        }
    except Profile.DoesNotExist:
        user_profile = {}

    company = job.company
    return {
        'user_profile': user_profile,
        'job_posting_text': f"채용공고 URL: {job_posting_url}",
        'company_info': {
            '인재상': company.talent_description,
            '기업규모': company.get_size_display(),
            '조직문화_키워드': company.culture_keywords,
        },
        'job_info': {
            'interview_stages': job.interview_stages,
            '요구역량': job.required_skills,
            '학습추천분야': job.recommended_study_areas,
        },
        'selected_interview_types': selected_interview_types,
    }


async def call_llm_server(payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(LLM_URL, json=payload)
        resp.raise_for_status()
        return resp.json()
```

- [ ] **Step 4: `backend/analysis/views.py` 작성**

```python
import asyncio
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from companies.models import Job
from .models import Analysis
from .serializers import AnalysisCreateSerializer, AnalysisResultSerializer
from .services import build_llm_payload, call_llm_server


class AnalysisCreateView(APIView):
    def post(self, request):
        serializer = AnalysisCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            job = Job.objects.get(pk=data['job_id'])
        except Job.DoesNotExist:
            return Response({'error': '직무를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        analysis = Analysis.objects.create(
            user=request.user,
            job=job,
            job_posting_url=data['job_posting_url'],
            submitted_cover_letter=data.get('submitted_cover_letter', ''),
            selected_interview_types=data['selected_interview_types'],
            status=Analysis.Status.PENDING,
        )

        payload = build_llm_payload(
            request.user, job,
            data['job_posting_url'],
            data.get('submitted_cover_letter', ''),
            data['selected_interview_types'],
        )

        try:
            result = asyncio.run(call_llm_server(payload))
            analysis.text_roadmap = result.get('text_roadmap', '')
            analysis.timeline_data = result.get('timeline_data', [])
            analysis.status = Analysis.Status.DONE
        except Exception as e:
            analysis.status = Analysis.Status.FAILED
            analysis.save()
            return Response({'error': f'LLM 서버 오류: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        analysis.save()
        return Response(AnalysisResultSerializer(analysis).data, status=status.HTTP_201_CREATED)


class AnalysisDetailView(APIView):
    def get(self, request, analysis_id):
        try:
            analysis = Analysis.objects.get(pk=analysis_id, user=request.user)
        except Analysis.DoesNotExist:
            return Response({'error': '분석 결과를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AnalysisResultSerializer(analysis).data)


class AnalysisHistoryView(APIView):
    def get(self, request):
        analyses = Analysis.objects.filter(user=request.user)
        return Response(AnalysisResultSerializer(analyses, many=True).data)
```

- [ ] **Step 5: `backend/analysis/serializers.py` 작성**

```python
from rest_framework import serializers
from .models import Analysis


class AnalysisCreateSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    job_posting_url = serializers.URLField()
    submitted_cover_letter = serializers.CharField(allow_blank=True, required=False, default='')
    selected_interview_types = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'culture_fit', 'coding_test', 'pt', 'technical', 'personality', 'practical', 'etc'
        ]),
        min_length=1,
    )


class AnalysisResultSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.job_title', read_only=True)
    company_name = serializers.CharField(source='job.company.company_name', read_only=True)

    class Meta:
        model = Analysis
        fields = [
            'id', 'company_name', 'job_title', 'job_posting_url',
            'selected_interview_types', 'text_roadmap', 'timeline_data',
            'status', 'created_at',
        ]
```

- [ ] **Step 6: `backend/analysis/urls.py` 작성**

```python
from django.urls import path
from .views import AnalysisCreateView, AnalysisDetailView, AnalysisHistoryView

urlpatterns = [
    path('analyze/', AnalysisCreateView.as_view(), name='analysis-create'),
    path('analyze/<int:analysis_id>/', AnalysisDetailView.as_view(), name='analysis-detail'),
    path('analyze/history/', AnalysisHistoryView.as_view(), name='analysis-history'),
]
```

- [ ] **Step 7: `backend/analysis/tests/test_analysis.py` 작성**

```python
import pytest
from unittest.mock import patch, AsyncMock
from rest_framework.test import APIClient
from accounts.models import User
from companies.models import Company, Job


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(email='a@test.com', password='pass1234!')
    c = APIClient()
    c.force_authenticate(user=user)
    return c, user


@pytest.fixture
def job(db):
    company = Company.objects.create(company_name='테스트기업', industry='IT', size='large')
    return Job.objects.create(
        company=company,
        job_title='백엔드 개발자',
        interview_stages=[{"order": 1, "type": "coding_test", "desc": ""}],
    )


@pytest.mark.django_db
def test_analysis_create_success(auth_client, job):
    client, _ = auth_client
    mock_result = {
        'text_roadmap': '1주차: 자료구조 복습\n2주차: 알고리즘 연습',
        'timeline_data': [{'week': 1, 'title': '1주차', 'tasks': ['자료구조 복습']}],
    }
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        resp = client.post('/api/analyze/', {
            'job_id': job.id,
            'job_posting_url': 'https://careers.kakao.com/jobs/1',
            'selected_interview_types': ['coding_test'],
        }, format='json')
    assert resp.status_code == 201
    assert resp.data['status'] == 'done'
    assert '1주차' in resp.data['text_roadmap']


@pytest.mark.django_db
def test_analysis_history(auth_client, job):
    client, _ = auth_client
    mock_result = {'text_roadmap': '로드맵', 'timeline_data': []}
    with patch('analysis.views.call_llm_server', new_callable=AsyncMock, return_value=mock_result):
        client.post('/api/analyze/', {
            'job_id': job.id,
            'job_posting_url': 'https://careers.kakao.com/jobs/1',
            'selected_interview_types': ['technical'],
        }, format='json')
    resp = client.get('/api/analyze/history/')
    assert resp.status_code == 200
    assert len(resp.data) == 1
```

- [ ] **Step 8: 테스트 실행**

```bash
cd backend
pytest analysis/tests/test_analysis.py -v
```

Expected: 2 passed

- [ ] **Step 9: Commit**

```bash
git add .
git commit -m "feat: add Analysis model + orchestrator APIs"
```

---

## Task 7: 전체 백엔드 통합 테스트 & 서버 기동 확인

- [ ] **Step 1: 전체 테스트 실행**

```bash
cd backend
pytest -v
```

Expected: 모든 테스트 passed (최소 13개)

- [ ] **Step 2: Django 서버 기동 확인**

```bash
python manage.py runserver 8080
```

- [ ] **Step 3: FastAPI 서버 기동 확인**

```bash
cd llm_server
uvicorn main:app --port 8081 --reload
curl http://localhost:8081/health
```

Expected: `{"status":"ok"}`

- [ ] **Step 4: 엔드포인트 수동 확인**

```bash
# 회원가입
curl -X POST http://localhost:8080/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"pass1234!"}'

# 기업 조회
curl -X GET "http://localhost:8080/api/companies/?name=카카오" \
  -H "Authorization: Bearer <access_token>"
```

- [ ] **Step 5: Final Commit**

```bash
git add .
git commit -m "feat: backend complete - Django + FastAPI integration"
```

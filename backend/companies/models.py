from django.conf import settings
from django.core.exceptions import ValidationError
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
    roadmap_supported = models.BooleanField(default=False, db_index=True)

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


class JobPosting(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_postings')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='job_postings')
    source_url = models.URLField(max_length=2048, blank=True, default='')
    company_name = models.CharField(max_length=100, blank=True, default='')
    job_title = models.CharField(max_length=200, blank=True, default='')
    responsibilities = models.TextField(blank=True, default='')
    requirements = models.TextField(blank=True, default='')
    preferred_qualifications = models.TextField(blank=True, default='')
    raw_text = models.TextField(blank=True, default='')
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'job_postings'
        ordering = ['-created_at']

    def __str__(self):
        company_name = self.company.company_name if self.company else 'Unsupported'
        return f"JobPosting({company_name}, {self.source_url})"


class CompanySourceDocument(models.Model):
    class SourceType(models.TextChoices):
        FIXTURE = 'fixture', 'Fixture'
        ADMIN_MANUAL = 'admin_manual', 'Admin manual'
        HOMEPAGE = 'homepage', 'Homepage'
        NEWS = 'news', 'News'
        BLOG = 'blog', 'Blog'
        PUBLIC_REPORT = 'public_report', 'Public report'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        STALE = 'stale', 'Stale'
        DELETED = 'deleted', 'Deleted'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='source_documents')
    source_type = models.CharField(max_length=30, choices=SourceType.choices)
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=2048, null=True, blank=True)
    raw_text = models.TextField(blank=True, default='')
    published_at = models.DateTimeField(null=True, blank=True)
    collected_at = models.DateTimeField(auto_now_add=True)
    content_hash = models.CharField(max_length=128, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        db_table = 'company_source_documents'

    def __str__(self):
        return f"{self.company.company_name} - {self.title or self.source_type}"


class CompanySourceChunk(models.Model):
    class EmbeddingStatus(models.TextChoices):
        NOT_REQUIRED = 'not_required', 'Not required'
        PENDING = 'pending', 'Pending'
        EMBEDDED = 'embedded', 'Embedded'
        FAILED = 'failed', 'Failed'

    source_document = models.ForeignKey(
        CompanySourceDocument,
        on_delete=models.CASCADE,
        related_name='chunks',
    )
    chunk_index = models.PositiveIntegerField()
    chunk_text = models.TextField()
    content_hash = models.CharField(max_length=128, db_index=True)
    embedding_status = models.CharField(
        max_length=20,
        choices=EmbeddingStatus.choices,
        default=EmbeddingStatus.NOT_REQUIRED,
    )
    embedding_model = models.CharField(max_length=100, blank=True, default='')
    embedding_vector = models.JSONField(default=list, blank=True)
    embedding_error = models.TextField(blank=True, default='')
    embedded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'company_source_chunks'
        unique_together = [('source_document', 'chunk_index')]

    def __str__(self):
        return f"{self.source_document_id}:{self.chunk_index}"


class CompanyKnowledgeClaim(models.Model):
    class ClaimType(models.TextChoices):
        BUSINESS_AREA = 'business_area', 'Business area'
        PRODUCT = 'product', 'Product'
        RECENT_ISSUE = 'recent_issue', 'Recent issue'
        TALENT_TRAIT = 'talent_trait', 'Talent trait'
        CULTURE_KEYWORD = 'culture_keyword', 'Culture keyword'
        TECH_STACK = 'tech_stack', 'Tech stack'
        ROLE_CANDIDATE = 'role_candidate', 'Role candidate'
        SKILL_RELATION = 'skill_relation', 'Skill relation'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    class TrustLevel(models.TextChoices):
        PUBLIC_SOURCE = 'public_source', 'Public source'
        ADMIN_CURATED = 'admin_curated', 'Admin curated'
        USER_PRIVATE_CANDIDATE = 'user_private_candidate', 'User private candidate'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='knowledge_claims')
    source_document = models.ForeignKey(
        CompanySourceDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='knowledge_claims',
    )
    claim_type = models.CharField(max_length=40, choices=ClaimType.choices)
    subject = models.CharField(max_length=200)
    predicate = models.CharField(max_length=100)
    object = models.TextField()
    confidence = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    trust_level = models.CharField(max_length=40, choices=TrustLevel.choices)
    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='company_knowledge_claims',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'company_knowledge_claims'

    def __str__(self):
        return f"{self.subject} {self.predicate} {self.object}"


class CompanyKnowledgeFact(models.Model):
    class TrustLevel(models.TextChoices):
        PUBLIC_SOURCE = 'public_source', 'Public source'
        ADMIN_CURATED = 'admin_curated', 'Admin curated'

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='knowledge_facts')
    approved_claim = models.ForeignKey(
        CompanyKnowledgeClaim,
        on_delete=models.PROTECT,
        related_name='projected_facts',
    )
    fact_type = models.CharField(max_length=40)
    subject = models.CharField(max_length=200)
    predicate = models.CharField(max_length=100)
    object = models.TextField()
    trust_level = models.CharField(max_length=40, choices=TrustLevel.choices)
    source_document = models.ForeignKey(
        CompanySourceDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='knowledge_facts',
    )
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'company_knowledge_facts'
        unique_together = [('company', 'fact_type', 'subject', 'predicate', 'object')]

    def clean(self):
        super().clean()
        if self.approved_claim.trust_level == CompanyKnowledgeClaim.TrustLevel.USER_PRIVATE_CANDIDATE:
            raise ValidationError('Private candidate claims cannot be projected as public facts.')
        if self.approved_claim.status != CompanyKnowledgeClaim.Status.APPROVED:
            raise ValidationError('Only approved claims can be projected as company facts.')
        if self.trust_level not in {
            self.TrustLevel.PUBLIC_SOURCE,
            self.TrustLevel.ADMIN_CURATED,
        }:
            raise ValidationError('Company facts must be public-source or admin-curated.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject} {self.predicate} {self.object}"


class RoleFamily(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'role_families'

    def __str__(self):
        return self.name


class Skill(models.Model):
    class Category(models.TextChoices):
        LANGUAGE = 'language', 'Language'
        FRAMEWORK = 'framework', 'Framework'
        DATABASE = 'database', 'Database'
        INFRA = 'infra', 'Infra'
        CS = 'cs', 'Computer science'
        SOFT_SKILL = 'soft_skill', 'Soft skill'
        DOMAIN = 'domain', 'Domain'

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=Category.choices)
    aliases = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'skills'

    def __str__(self):
        return self.name


class InterviewType(models.Model):
    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'interview_types'

    def __str__(self):
        return self.label


class StudyArea(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'study_areas'

    def __str__(self):
        return self.name


class RoleFamilySkill(models.Model):
    class Importance(models.TextChoices):
        REQUIRED = 'required', 'Required'
        PREFERRED = 'preferred', 'Preferred'
        CONTEXTUAL = 'contextual', 'Contextual'

    role_family = models.ForeignKey(RoleFamily, on_delete=models.CASCADE, related_name='skill_requirements')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='role_family_requirements')
    importance = models.CharField(max_length=20, choices=Importance.choices, default=Importance.REQUIRED)

    class Meta:
        db_table = 'role_family_skills'
        unique_together = [('role_family', 'skill')]

    def __str__(self):
        return f"{self.role_family.name} - {self.skill.name}"

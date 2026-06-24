# T3 Evidence - Role and skill taxonomy

## Scope
- Added role/skill taxonomy SQL models:
  - `RoleFamily`
  - `Skill`
  - `InterviewType`
  - `StudyArea`
  - `RoleFamilySkill`
- Unknown job titles can be stored in `JobPosting` and linked to `Analysis` without creating or requiring a legacy `Job` source.

## Evidence
- Migration generation: `wave1-makemigrations.txt`
  - created taxonomy models in `companies/migrations/0007_interviewtype_rolefamily_skill_studyarea_and_more.py`
- RED proof: `wave1-red-pytest.txt` failed on missing role/skill models and `Analysis.job_posting`.
- GREEN targeted proof: `wave1-targeted-green-pytest.txt` -> `24 passed`.
- Full regression proof: `wave1-regression-pytest.txt` -> `59 passed`.

## Cleanup
- No persistent runtime process was started for taxonomy QA.

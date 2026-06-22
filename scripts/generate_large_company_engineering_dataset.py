from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT_DIR / "backend" / "companies" / "data" / "large_company_engineering_jobs.jsonl"

MESSAGE = f"""이 스크립트는 더 이상 합성 데이터를 생성하지 않습니다.
실제 웹 출처로 검증한 회사 메타데이터만 `{OUTPUT_PATH}` 에 저장해야 합니다.
허용 필드는 company_name, industry, size, talent_description, culture_keywords 뿐입니다.
"""


def main():
    raise SystemExit(MESSAGE)


if __name__ == "__main__":
    main()

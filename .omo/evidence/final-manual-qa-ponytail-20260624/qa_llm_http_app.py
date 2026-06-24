import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LLM_DIR = ROOT / "llm_server"
sys.path.insert(0, str(LLM_DIR))

os.environ["LLM_INTERNAL_TOKEN"] = "test-internal-token"
os.environ["LLM_ALLOWED_CLIENT_HOSTS"] = "127.0.0.1,::1,testclient"
os.environ["GMS_KEY"] = "qa-gms-key"

import main  # noqa: E402

main.INTERNAL_TOKEN = "test-internal-token"
main.GMS_KEY = "qa-gms-key"
_calls = []

INITIAL_RESPONSE = {
    "competency_gap": {},
    "text_roadmap": "initial",
    "timeline_data": [
        {
            "category": "로봇 제어",
            "responsibility_index": 1,
            "responsibility": "로봇 제어 알고리즘 개발",
            "priority": 1,
            "experience_match": "adjacent",
            "subtopics": [
                {
                    "title": "fallback values",
                    "preparation_type": "practice",
                    "questions": [{"type": "behavioral"}, {}, {}],
                }
            ],
        }
    ],
}

REPAIR_RESPONSE = {
    "competency_gap": {},
    "text_roadmap": "repaired",
    "timeline_data": [
        {
            "category": "EtherCAT",
            "responsibility_index": 2,
            "responsibility": "EtherCAT 기반 서보 모터 실시간 제어",
            "priority": 2,
            "experience_match": "related",
            "subtopics": [
                {
                    "title": "pass through values",
                    "preparation_type": "organize",
                    "questions": [{"type": "application"}, {}, {}],
                }
            ],
        }
    ],
}

async def fake_call_gpt(prompt):
    _calls.append(prompt)
    if len(_calls) == 1:
        return json.dumps(INITIAL_RESPONSE, ensure_ascii=False)
    return json.dumps(REPAIR_RESPONSE, ensure_ascii=False)

main._call_gpt = fake_call_gpt
app = main.app

import json
import os
import sys
from pathlib import Path

import httpx

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
    "text_roadmap": "original-before-repair-error",
    "timeline_data": [
        {
            "category": "Robot control",
            "responsibility_index": 1,
            "responsibility": "Robot control algorithm development",
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


async def fake_call_gpt(prompt):
    _calls.append(prompt)
    if len(_calls) == 1:
        return json.dumps(INITIAL_RESPONSE, ensure_ascii=False)
    raise httpx.HTTPError("forced repair failure")


main._call_gpt = fake_call_gpt
app = main.app

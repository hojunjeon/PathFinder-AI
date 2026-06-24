# GraphRAG Company KG Plan - Orchestrator Review Report

작성일: 2026-06-24  
대상 계획: `.omo/plans/graphrag-company-kg.md`  
상태: start-work 미실행, 계획/검토 완료

## 요청된 검토 구성

- GPT-5.5 Codex subagent: 실행 완료, `OK_WITH_CHANGES`.
- Antigravity CLI Gemini 3.5 Flash High: `agy --model "Gemini 3.5 Flash (High)" --print ...` 실행 완료, 그러나 stdout에 응답이 출력되지 않았고 로그에는 response stream 호출만 남았다.
- Antigravity CLI Claude Sonnet 4.6 Thinking: `agy --model "Claude Sonnet 4.6 (Thinking)" --print ...` 실행 완료, 그러나 stdout에 응답이 출력되지 않았고 로그에는 response stream 호출 및 `PlannerResponse without ModifiedResponse encountered`만 남았다.

## GPT-5.5 검토 요약

Verdict: `OK_WITH_CHANGES`

유지할 점:
- SQL source of truth for companies.
- companies-centered KG framing.
- old `jobs` removal.
- `analyses` not used as factual evidence.
- embeddings deferred.

수정 요구:
- QA scenario가 실행 가능한 command/payload/expected observable 수준까지 구체화되어야 한다.
- schema/migration contract가 부족하다.
- private evidence가 pending claim 경로를 통해 public KG로 새는 ambiguity를 막아야 한다.

## 통합한 변경

- `.omo/plans/graphrag-company-kg.md`에 schema appendix를 추가했다.
- public company knowledge, role/skill taxonomy, private/user data table의 필드/enum/constraint/cascade 방향을 명시했다.
- migration sequence를 추가했다.
- private user posting은 `user_private_candidate`로만 저장하고, public fact 승격은 public/curated source 또는 redacted admin-authored claim이 필요하다고 명시했다.
- QA command templates와 todo별 pytest/curl/Playwright invocation을 구체화했다.
- prompt-injection and no-leakage checks를 검증 전략에 추가했다.

## 최종 판단

계획은 start-work 전에 충분히 실행 가능한 수준으로 개선되었다. 다만 실제 구현은 DB migration, prompt contract, frontend flow, privacy guard를 함께 바꾸는 큰 작업이므로 `$omo:start-work`로 실행할 때도 한 번에 전부 구현하지 말고 plan의 wave 순서를 지켜야 한다.

## 남은 주의점

- Antigravity 두 reviewer의 내용은 capturable output이 없어 승인/반려 근거로 삼지 않았다.
- `agy` 로그는 `.omo/reviews/agy-gemini-high.log`, `.omo/reviews/agy-claude-sonnet-thinking.log`, `.omo/reviews/agy-smoke.log`에 남아 있다.
- 이 보고서는 외부 reviewer 결과의 대체물이 아니라, capturable evidence 기준의 orchestrator 판단이다.

# prompt-reviewer 참고 문서

prompt-reviewer 스킬의 리뷰 기준을 도출할 때 참고한 문서 목록.

## 출처

| # | 출처 | URL | 활용된 내용 |
|---|------|-----|-----------|
| 1 | OpenAI GPT-4.1 Prompting Guide | https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide | Role/Objective/Instructions 구조, 도구 정의 패턴, 구분자 전략 |
| 2 | OpenAI GPT-5 Prompting Guide | https://developers.openai.com/cookbook/examples/gpt-5/gpt-5_prompting_guide | Eagerness 보정, Tool preamble, 모호한 지시의 토큰 낭비 |
| 3 | Anthropic Prompting Best Practices | https://platform.claude.com/docs/en/docs/build-with-claude/prompt-engineering/claude-prompting-best-practices | 명확성 테스트, WHY 설명, XML 구조, 자율성-안전성 균형, 과도한 프롬프팅 경고 |
| 4 | Anthropic Context Engineering for Agents | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | 신호 대 잡음 비율, Altitude 보정, 도구 설계 원칙 |
| 5 | Anthropic Demystifying Evals | https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | 테스트 가능한 성공 기준, 에이전트 유형별 평가 |
| 6 | Microsoft Azure System Message Design | https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/advanced-prompt-engineering | 역할→경계→형식→불확실성 정책 체크리스트, 충돌 지시 우선순위 |
| 7 | Microsoft Copilot Studio Evaluation Checklist | https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/evaluation-checklist | 4단계 평가 생명주기, 견고성/아키텍처/엣지케이스 카테고리 |
| 8 | Google Prompting Strategies | https://ai.google.dev/gemini-api/docs/prompting-strategies | 에이전트 워크플로우 6차원 (분해, 진단, 철저성, 적응, 회복, 위험평가) |
| 9 | Addy Osmani - Good Spec for AI Agents | https://addyosmani.com/blog/good-spec/ | 6대 커버리지 영역, 3단계 경계(always/ask/never), 모듈식 프롬프트 |
| 10 | The Prompt Report (arXiv) | https://arxiv.org/abs/2406.06608 | 33개 용어 + 58개 기법 분류 체계 |
| 11 | Google Cloud - What is Prompt Engineering | https://cloud.google.com/discover/what-is-prompt-engineering?hl=en | 프롬프트 유형 분류(zero-shot/few-shot/CoT), 6대 전략과 전술/예시 |

## 기준 도출 방법

각 출처에서 제시하는 평가 차원을 나열한 뒤, 3개 이상의 독립 출처에서 합의된 항목만 리뷰 기준으로 채택했다. Phase 1(구조 검사 5개)과 Phase 2(내용 리뷰 7개)로 구성.

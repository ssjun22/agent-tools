# gemini3-prompt-reviewer 참고 문서

gemini3-prompt-reviewer 스킬의 리뷰 기준을 도출할 때 참고한 문서 목록.

## 출처

| # | 출처 | URL | 활용된 내용 |
|---|------|-----|-----------|
| 1 | Gemini Prompting Strategies | https://ai.google.dev/gemini-api/docs/prompting-strategies | temperature 1.0 필수, few-shot 권장, 제약조건 끝 배치, 구분자 혼용 금지 |
| 2 | Gemini 3 Prompting Guide (Vertex AI) | https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/gemini-3-prompting-guide | 추론 모델 특성, 기본 출력 간결, 페르소나 과잉 준수, 광범위 부정문 위험, split-step 검증, first-match 조기종료 |
| 3 | Gemini 3 Developer Guide | https://ai.google.dev/gemini-api/docs/gemini-3 | thought signature 필수, thinking_level, 내장 도구+FC 동시 사용 불가, 마이그레이션 가이드 |
| 4 | Gemini Thinking Mode | https://ai.google.dev/gemini-api/docs/thinking | 동적 thinking, thinking level별 특성, thinking 토큰 과금 |
| 5 | Gemini Function Calling | https://ai.google.dev/gemini-api/docs/function-calling | 4가지 모드, 도구 10-20개 제한, ANY 모드 루핑 이슈 |
| 6 | Gemini Structured Output | https://ai.google.dev/gemini-api/docs/structured-output | description 필드 중요, 강타입, 스키마 복잡도 제한 |
| 7 | Gemini System Instructions (Cloud) | https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/system-instructions | 시스템 지시는 가이드일 뿐 보장 아님, 배열 형식 지원 |
| 8 | Gemini Long Context | https://ai.google.dev/gemini-api/docs/long-context | 1M+ 토큰, 질문 끝 배치, 단일 니들 99% 정확도 |
| 9 | Google ADK Agent Instructions | https://google.github.io/adk-docs/agents/llm-agents/ | instruction 필드 핵심, Markdown 권장, 동적 템플릿 |
| 10 | Phil Schmid - Gemini 3 Best Practices | https://www.philschmid.de/gemini-3-prompt-practices | 직접성 우선, XML/Markdown 혼용 금지, TODO 자기추적 |
| 11 | Gemini 3 Troubleshooting Guide | https://ai.google.dev/gemini-api/docs/troubleshooting | temperature 경고, 구조화 출력 권장, 반복 제거 |
| 12 | Google AI Developers Forum | https://discuss.ai.google.dev/t/gemini-3-significantly-worse-thant-2-5-pro-at-long-context-temperature-likely-to-blame/110888 | 커뮤니티 temperature 저하 보고 |
| 13 | Gemini Text Generation Docs | https://ai.google.dev/gemini-api/docs/text-generation | temperature 1.0 강력 권장 (추가 확인) |

## 기준 도출 방법

Gemini 3 고유 동작에 해당하는 항목만 선별했다. 모델에 무관한 일반적 프롬프팅 조언(제약조건 끝 배치, 구분자 일관성, few-shot 등)은 범용 prompt-reviewer 스킬로 분리하고, Gemini 3 특화 10개 항목만 채택했다.

# Agent Prompt Template

Claude Code 서브 에이전트의 기대 구조. 섹션은 필요에 따라 조정할 수 있으나, 아래 순서를 권장한다.

---

name: {{ kebab-case 식별자 }}
description: {{ 1-2문장 역할 설명 }}
tools: {{ 도구 목록 }}
model: {{ model 선택 기준은 review-criteria.md 참고 }}

---

## Role

- {{ 전문성 도메인과 행동 방식 }}
- ...

## Instructions

- {{ 핵심 태스크와 실행 단계 }}
- ...

## Constraints

- {{ 판단 범위 밖 영역과 안전 규칙 }}
- ...

## Output Format

- {{ 출력 구조와 필드 정의 }}
- ...

## Checklist

- [ ] {{ 자기 검증 항목 }}
- [ ] ...

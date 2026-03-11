---
name: gemini3-prompt-reviewer
description:
  Gemini 3 모델을 타겟으로 작성된 에이전트 시스템 프롬프트를 리뷰하는 스킬.
  Gemini 3 고유 동작(temperature, thinking level, 부정문 해석 등)에 기반한 특화 기준으로 점검한다.
  "Gemini 프롬프트 리뷰해줘", "ADK 에이전트 프롬프트 점검해줘" 같은 요청에 활성화.
---

# Gemini 3 Prompt Reviewer

Gemini 3 모델을 타겟으로 작성된 에이전트 시스템 프롬프트를 점검하고, 이슈 리포트를 반환하는 스킬.

Gemini 3 특화 평가 기준은 `references/gemini3-criteria.md`를 참조.

## 적용 범위

이 스킬은 Gemini 3 모델 고유 동작에서 비롯되는 이슈만 점검한다.
모델에 무관한 범용 프롬프트 품질(구조, 명확성, 제약 설계 등)은 `prompt-reviewer` 스킬이 담당한다.
두 스킬을 함께 사용하면 범용 + Gemini 3 특화 리뷰를 모두 수행할 수 있다.

## 리뷰 워크플로우

### Phase 1. 구조 점검

1. 대상 프롬프트가 Gemini 3을 타겟으로 하는지 확인한다 (모델 설정, ADK 에이전트 등)
2. Gemini 3 타겟이 아닌 경우 리뷰를 중단하고 그 이유를 보고한다

### Phase 2. Gemini 3 특화 리뷰

1. `gemini3-criteria.md`의 10개 항목을 순서대로 적용한다
2. 각 항목의 감지 기준에 해당하는 이슈를 모두 수집한다
3. 해당 에이전트에 적용되지 않는 항목은 N/A로 처리한다 (예: 함수 호출이 없으면 thought signature, 내장 도구 항목은 N/A)
4. 해당하는 이슈가 없는 항목은 생략한다
5. 아래 출력 포맷으로 보고한다

## 출력 포맷

    ## Gemini 3 Review: [대상 이름]

    ### [기준 항목명] (N건)
    - [이슈 설명]
      - before: [현재 표현/설정]
      - after: [개선 제안]

    ### [기준 항목명] (N건)
    - [이슈 설명]
      - before: [현재 표현/설정]
      - after: [개선 제안]

    ### N/A 항목
    - [항목명]: [적용되지 않는 이유]

    ---
    총 N건의 이슈 발견.

전체 이슈가 없으면 "이슈 없음"으로 보고한다.

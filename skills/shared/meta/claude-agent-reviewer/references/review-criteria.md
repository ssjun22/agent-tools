# Review Criteria

리뷰 기준. 각 항목에 기본 심각도를 표기한다.
톤 평가의 이론적 근거는 `prompting-principles.md`를 참조한다.

## 공통 기준

모든 본문 섹션(Role ~ Checklist)에 적용한다.

- [warning] 과잉 강조 표현(MUST, CRITICAL, ALWAYS, NEVER)이 남용되지 않았는가
- [info] 긍정 프레이밍("하지 마라" 대신 "이렇게 해라")을 사용했는가
- [info] 비자명한 규칙에 동기("왜")가 포함되었는가
- [info] 순서가 중요한 항목에 번호를 사용했는가

## Frontmatter

- [error] name 필드가 존재하는가
- [error] description 필드가 존재하는가
- [warning] description이 에이전트의 역할을 명확히 설명하는가
- [warning] description이 간결한가 (1-2문장)
- [warning] model 선택이 에이전트의 작업 특성에 적합한가
- [warning] model이 `inherit`인 경우, 작업 특성에 더 적합한 모델이 있는지 검토했는가
  (`inherit`은 호출자에 따라 과잉/부족 모델이 할당될 수 있으므로 구체적 모델을 추천한다)

### model 선택 기준

| model | 적합한 작업 | 예시 |
|-------|------------|------|
| `opus` | 고난도 추론, 정확도 우선 | 복잡한 코드 작성, 장시간 리서치, 고급 에이전트 |
| `sonnet` | 범용 지능, 균형 잡힌 성능 | 코드 생성, 데이터 분석, 시각 이해, 도구 활용 |
| `haiku` | 빠른 속도, 비용 효율 | 실시간 처리, 대량 작업, 서브 에이전트 |
| `opusplan` | 설계는 opus, 실행은 sonnet | 계획 단계가 중요하고 실행은 반복적인 작업 |
| `inherit` | 호출자의 모델을 그대로 사용 | 특별한 요구가 없을 때 기본값 |

## Role

- [warning] 전문성 도메인이 구체적으로 명시되었는가
  ("검수 전문가"가 아닌 "수학 문항 텍스트 오류 검수 전문가")
- [info] 행동 방식/판단 원칙이 포함되었는가
- [info] 담당 범위(scope)가 설정되었는가
- [info] 간결한가 (1-3문장 권장, 장황하면 Instructions로 분리)

## Instructions

- [error] 핵심 검출/판정 항목이 정의되었는가
- [warning] 판정 기준이 실행 가능한가
  (모호한 "적절한지 확인" 대신 구체적 조건)
- [warning] 경계 케이스가 다뤄졌는가
  (오류로 판정하지 않을 경우 포함)

## Constraints

- [warning] 에이전트의 판단 범위 밖 영역이 명시되었는가
- [warning] 오탐(false positive) 방지 규칙이 포함되었는가

## Output Format

- [error] 출력 형식(JSON 스키마 등)이 모든 필드를 정의하는가
- [error] 코드 스키마가 존재할 경우, 프롬프트의 출력 명세와 일치하는가
- [warning] 필드 설명이 모호하지 않은가
- [info] 출력 예시가 인라인으로 포함되었는가
- [info] 프롬프트의 포매팅 스타일이 출력 스타일과 일치하는가

## Checklist

- [warning] 체크리스트 항목이 해당 에이전트의 핵심 검증 포인트를 반영하는가
- [info] 간결한가 (5-7항목 권장)

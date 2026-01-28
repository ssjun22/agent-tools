# Skill Analysis Guidelines

스킬을 분석할 때 확인해야 할 항목들과 가이드라인입니다.

## Analysis Checklist

### 1. Folder Structure Analysis

- [ ] **scripts/** 디렉토리 존재 여부
  - 어떤 종류의 스크립트가 포함되어 있는가? (Python, Bash, etc.)
  - 스크립트의 용도는 무엇인가? (자동화, 데이터 처리, 유틸리티 등)
  - 파일 개수와 복잡도는 어느 정도인가?

- [ ] **references/** 디렉토리 존재 여부
  - 참조 문서가 어떻게 구조화되어 있는가?
  - 카테고리별로 분류되어 있는가?
  - 각 참조 문서의 용도는 무엇인가? (API 문서, 스키마, 가이드라인 등)

- [ ] **assets/** 디렉토리 존재 여부
  - 어떤 종류의 에셋이 포함되어 있는가? (템플릿, 이미지, 폰트 등)
  - 에셋의 용도는 무엇인가?

### 2. SKILL.md Analysis

#### YAML Frontmatter

- [ ] **name**: 명확하고 일관된 네이밍 컨벤션을 따르는가?
- [ ] **description**: 언제 사용해야 하는지 명확하게 설명하는가?
  - 특정 시나리오, 파일 타입, 작업을 명시하는가?
  - third-person 형식으로 작성되었는가? ("This skill should be used when...")

#### Content Structure

- [ ] **Overview Section**: 스킬의 목적을 1-2문장으로 명확히 설명하는가?

- [ ] **Main Structure Pattern**: 어떤 구조 패턴을 따르는가?
  - Workflow-Based: 순차적 프로세스
  - Task-Based: 도구 모음, 다양한 작업
  - Reference/Guidelines: 표준, 사양
  - Capabilities-Based: 통합 시스템, 상호 연관된 기능
  - Custom/Mixed: 위의 패턴들을 조합

- [ ] **Sections**: 섹션이 논리적으로 구성되어 있는가?
  - 각 섹션의 목적이 명확한가?
  - 섹션 간 계층 구조가 적절한가? (##, ###, #### 사용)

- [ ] **Examples**: 구체적인 사용 예시가 포함되어 있는가?
  - 현실적인 사용자 요청 예시
  - 코드 샘플
  - 결정 트리 (복잡한 워크플로우의 경우)

- [ ] **Resource References**: bundled resources를 어떻게 참조하는가?
  - scripts, references, assets를 언급하고 사용법을 안내하는가?

#### Writing Style

- [ ] **Imperative/Infinitive Form**: 명령형/부정사 형식으로 작성되었는가?
  - "To accomplish X, do Y" (O)
  - "You should do X" (X)

- [ ] **Objective & Instructional**: 객관적이고 교육적인 톤인가?

- [ ] **Conciseness**: SKILL.md가 간결한가? (< 5k words 권장)

### 3. Best Practices Identification

#### Progressive Disclosure

- [ ] **Metadata**: name + description이 명확하고 구체적인가?
- [ ] **SKILL.md**: 핵심 워크플로우와 지침만 포함하는가?
- [ ] **Bundled Resources**: 상세 문서, 스크립트, 에셋이 적절히 분리되어 있는가?

#### Resource Organization

- [ ] **Scripts**: 반복적으로 재작성되는 코드가 스크립트로 분리되었는가?
- [ ] **References**: 상세한 참조 문서가 별도 파일로 관리되는가?
  - 10k+ words의 큰 문서는 references에 있는가?
  - SKILL.md에 grep 검색 패턴이 포함되어 있는가?
- [ ] **Assets**: 출력에 사용될 파일들이 assets에 분류되어 있는가?

#### Avoid Duplication

- [ ] 정보가 SKILL.md와 references에 중복되어 있지 않은가?
- [ ] 핵심 절차는 SKILL.md에, 상세 참조는 references에 있는가?

## Analysis Output Format

분석 결과는 다음 형식으로 정리합니다:

```markdown
# [Skill Name] - Skill Analysis

> Analyzed on: YYYY-MM-DD

## Folder Structure

[Directory tree visualization]

## YAML Frontmatter

[Frontmatter key-value pairs]

## Structure Pattern

**Detected Pattern**: [Pattern Type]

## Section Structure

[Hierarchical section list]

## Statistics

- Word Count
- Line Count
- Scripts count
- References count
- Assets count

## Best Practices Observations

[Checklist of observed best practices and recommendations]

## Key Takeaways

[Notable patterns and learnings from this skill]
```

## Pattern Comparison

여러 스킬을 분석할 때는 다음 항목들을 비교합니다:

1. **Common Section Names**: 공통적으로 사용되는 섹션 이름
2. **Structure Patterns**: 선호되는 구조 패턴
3. **Frontmatter Conventions**: description 작성 스타일
4. **Resource Distribution**: 어떤 내용을 어디에 배치하는지
5. **Length Guidelines**: 일반적인 문서 길이

## Template Update Criteria

다음 경우에 my-skill-template.md를 업데이트합니다:

1. **새로운 패턴 발견**: 더 효과적인 구조나 작성 방식 발견
2. **공통 패턴 식별**: 여러 스킬에서 반복되는 패턴
3. **베스트 프랙티스 개선**: 더 나은 조직화 방법 발견
4. **사용자 요청**: 특정 패턴을 템플릿에 반영하고 싶을 때

# agent-tools

AI 에이전트를 위한 범용 프롬프트 및 스킬 모음

## 개요

이 저장소는 AI 에이전트(Claude, Gemini 등)가 다양한 작업을 수행할 수 있도록 돕는 재사용 가능한 에이전트 정의와 프롬프트 모음입니다. 각 에이전트는 특정 도메인이나 작업에 특화되어 있으며, 프로젝트에 맞게 커스터마이징하여 사용할 수 있습니다.

## 디렉토리 구조

```
agent-tools/
├── claude/          # Claude AI 플랫폼 전용
│   ├── agents/      # Claude용 에이전트 정의 (.md)
│   └── prompts/     # Claude용 프롬프트 모음
├── common/          # 플랫폼 독립적인 공통 자료
│   ├── agents/      # 범용 에이전트 템플릿
│   └── prompts/     # 범용 가이드라인 및 원칙
└── gemini/          # Google Gemini 플랫폼 전용 (예정)
```

각 플랫폼 디렉토리는 독립적으로 관리되며, `common/` 디렉토리의 내용을 기반으로 플랫폼별 특성에 맞게 커스터마이징됩니다.

## 제공하는 에이전트

### React Component Architect

React/Next.js 컴포넌트 아키텍처 설계 및 리팩토링 전문 에이전트

### tRPC Service Layer Organizer

tRPC 서비스 레이어 아키텍처 및 조직화 전문 에이전트

> **Note**: 현재는 웹 개발 관련 에이전트가 포함되어 있으며, 다양한 도메인과 기술 스택의 에이전트를 지속적으로 추가할 예정입니다.

## 제공하는 가이드라인

### 코드 품질 (범용)

- **coding-principles.md**: DRY, SOLID, Early Return 등 언어/프레임워크에 무관한 기본 원칙
- **coding-style.md**: 일관성 있는 코드 스타일 가이드
- **naming-conventions.md**: 명확하고 의미있는 네이밍 컨벤션

### 프레임워크별 가이드

- **react-patterns.md**: React 모범 사례 및 패턴
- **file-structure.md**: Progressive Lifting을 통한 파일 구조 조직화 (React/Next.js)
- **state-management.md**: 상태 관리 전략
- **trpc-architecture.md**: tRPC 아키텍처 가이드
- **typescript-guide.md**: TypeScript 사용 가이드

### 개발 프로세스

- **interaction-process.md**: AI 에이전트와의 효과적인 상호작용 방법
- **tech-stack.md**: 프로젝트 기술 스택 정의

## 핵심 설계 원칙

### 단일 책임 (Single Responsibility)

각 모듈, 함수, 컴포넌트는 하나의 명확한 책임만 가져야 합니다.

### 관심사의 분리 (Separation of Concerns)

비즈니스 로직, UI, 데이터 처리 등 서로 다른 관심사를 명확히 분리합니다.

### 점진적 일반화 (Progressive Generalization)

필요할 때만 추상화하고 일반화합니다. 과도한 사전 최적화를 지양합니다.

### 명확성 우선 (Clarity First)

성능보다 읽기 쉽고 유지보수 가능한 코드를 우선시합니다.

### 예시: React/Next.js 프로젝트

#### Progressive Lifting

컴포넌트를 가장 가까운 위치에서 시작하여 필요할 때만 상위로 이동:

- Single page use → `app/[section]/[route]/_components/`
- Section-wide use → `app/[section]/_components/`
- Cross-section use → `app/_components/`
- Universal UI → `components/ui/`

#### Component Cohesion

계산 로직을 사용하는 곳에 가깝게 유지하고, 가공된 데이터가 아닌 원시 데이터를 전달합니다.

#### Domain Logic Separation

UI 컴포넌트와 비즈니스 로직을 분리하여 재사용성을 극대화합니다.

## 사용 방법

### 1. AI 플랫폼별 활용

- **Claude AI**: `claude/` 디렉토리의 에이전트 정의를 Cursor 또는 Claude에 로드
- **Gemini**: `gemini/` 디렉토리 (향후 추가 예정)
- **범용**: `common/` 디렉토리의 가이드라인은 모든 AI 플랫폼에서 참조 가능

### 2. 프로젝트 적용

1. 프로젝트에 맞는 에이전트 선택
2. 해당 에이전트의 프롬프트를 AI 도구에 로드
3. 필요시 프로젝트 특성에 맞게 커스터마이징

### 3. 새로운 에이전트 추가

1. `agents/` 디렉토리에 새로운 에이전트 정의 추가
2. 관련 프롬프트를 `prompts/` 디렉토리에 작성
3. README에 에이전트 설명 추가

## 확장 가능성

이 저장소는 다양한 도메인과 기술 스택으로 확장 가능합니다:

- **백엔드**: API 설계, 데이터베이스 아키텍처, 마이크로서비스 패턴
- **프론트엔드**: Vue, Angular, Svelte 등 다른 프레임워크
- **모바일**: React Native, Flutter 개발 가이드
- **데이터**: 데이터 파이프라인, ML 모델 구조화
- **DevOps**: CI/CD, 인프라 코드, 모니터링

새로운 에이전트와 가이드라인 추가는 언제나 환영합니다.

## 라이선스

MIT

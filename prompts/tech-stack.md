# 기술 스택 및 패키지 매니저

## 기술 스택

이 프로젝트는 다음 기술 스택을 사용합니다.
코드 작성 시 각 버전의 API와 모범 사례를 따르세요.

- **Next.js v15** - App Router, Server Components 기본
- **React v19** - 최신 hooks API 지원
- **Prisma v7** - ORM 및 데이터베이스 관리
- **PostgreSQL** - 메인 데이터베이스
- **tRPC** - 타입 안전한 API 레이어
- **Shadcn UI** - 재사용 가능한 컴포넌트 라이브러리
- **TailwindCSS v3** - 유틸리티 기반 스타일링
- **TypeScript** - 타입 안전성 확보

## 패키지 매니저

이 프로젝트는 **pnpm**을 기본 패키지 매니저로 사용합니다.

### 사용 규칙

- 모든 패키지 설치 시 `pnpm`을 사용하세요
- npm, yarn 등 다른 패키지 매니저를 사용하지 마세요

### 주요 명령어

- **패키지 설치**: `pnpm install`
- **패키지 추가**: `pnpm add <package-name>`
- **개발 의존성 추가**: `pnpm add -D <package-name>`
- **패키지 제거**: `pnpm remove <package-name>`
- **스크립트 실행**: `pnpm <script-name>` (예: `pnpm dev`, `pnpm build`)

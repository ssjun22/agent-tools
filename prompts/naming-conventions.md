# 네이밍 컨벤션

프로젝트 전반에 걸쳐 일관된 네이밍 규칙을 따릅니다.

## 기본 규칙

### 파일명: kebab-case
- 예: `user-profile.tsx`, `submission-list.tsx`, `api-utils.ts`

### 컴포넌트: PascalCase
- 예: `UserProfile`, `SubmissionList`, `Button`

### 변수, 함수, const: camelCase
- 예: `handleClick`, `fetchUserData`, `isActive`

### 타입: PascalCase
- 예: `UserData`, `SubmissionProps`, `ApiResponse`

### 상수: UPPER_SNAKE_CASE
- 예: `MAX_FILE_SIZE`, `API_ENDPOINT`, `DEFAULT_TIMEOUT`

## React 특화 규칙

### 이벤트 핸들러
- 접두사 "handle" 사용: `handleClick`, `handleSubmit`, `handleKeyDown`

### Custom Hooks
- 접두사 "use" 사용: `useOcrUpload`, `useAuth`
- 파일명: `use-{feature}.ts` (kebab-case)

## tRPC 특화 규칙

### Service 파일
- 파일명: `{domain}.service.ts` (예: `user.service.ts`)
- Export 이름: `{domain}Service` (예: `userService`)

### DTO 파일
- 파일명: `types/dto/{domain}.ts` (예: `types/dto/user.ts`)

### Input/Output 타입
- Input 타입: `{Domain}{Action}Input` (예: `UserCreateInput`)
- Response 타입: `{Domain}{Action}Res` (예: `UserDetailRes`)
- Zod 스키마: `{domain}{Action}InputSchema` (예: `userCreateInputSchema`)

### tRPC 프로시저
- 의미 있는 동사로 네이밍: `createAssignment`, `getSubmissions`

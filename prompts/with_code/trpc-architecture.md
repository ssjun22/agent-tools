# tRPC 3계층 아키텍처

## 개요

tRPC API는 명확한 관심사 분리를 위해 3계층 아키텍처를 사용합니다.

```
Router Layer (routers/*.ts)
    ↓ input validation
Service Layer (services/*.service.ts)
    ↓ business logic
Database Layer (Prisma)
```

## 3계층 구조

### Router Layer - routers/*.ts
**책임:**
- tRPC 프로시저 정의만
- DTO에서 Zod 스키마 import
- 서비스 메서드 직접 호출
- 비즈니스 로직 포함 금지
- 직접 Prisma 호출 금지
- 에러 핸들링 금지 (서비스 에러 전파)

### Service Layer - services/*.service.ts
**책임:**
- 모든 비즈니스 로직 구현
- 데이터베이스 작업 오케스트레이션
- `@/lib/prisma`에서 Prisma 클라이언트 import
- 필요 시 트랜잭션 처리
- 에러 throw (tRPC가 처리)
- 함수들을 namespace 객체로 export

### DTO Layer - types/dto/*.ts
**책임:**
- Zod input 검증 스키마 정의
- `z.infer<>`로 input 타입 추론
- `RouterOutputs`로 response 타입 정의
- 로직 없음 - 스키마와 타입만

## 파일 구조

```
src/
  server/
    routers/
      user.ts              # tRPC router - procedures only
    services/
      user.service.ts      # Business logic
  types/
    dto/
      user.ts              # DTOs and types
```

## 구현 패턴

### 1. DTO Layer (types/dto/user.ts)

```typescript
import { z } from 'zod';
import type { RouterOutputs } from '@/lib/trpc';

export const userCreateInputSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1),
});

export type UserCreateInput = z.infer<typeof userCreateInputSchema>;
export type UserDetailRes = RouterOutputs['user']['getById'];
```

### 2. Service Layer (services/user.service.ts)

```typescript
import { prisma } from '@/lib/prisma';
import type { UserCreateInput } from '@/types/dto/user';

const create = async (input: UserCreateInput) => {
  return await prisma.user.create({ data: input });
};

const getById = async ({ id }: { id: string }) => {
  const user = await prisma.user.findUnique({ where: { id } });
  if (!user) throw new Error('User not found');
  return user;
};

export const userService = { create, getById };
```

### 3. Router Layer (routers/user.ts)

```typescript
import { router, publicProcedure } from '../trpc';
import { userService } from '../services/user.service';
import { userCreateInputSchema } from '@/types/dto/user';

export const userRouter = router({
  create: publicProcedure
    .input(userCreateInputSchema)
    .mutation(async ({ input }) => await userService.create(input)),

  getById: publicProcedure
    .input(z.object({ id: z.string() }))
    .query(async ({ input }) => await userService.getById(input)),
});
```

## 트랜잭션 처리

다단계 작업에는 항상 트랜잭션을 사용하세요.

```typescript
const createWithRelation = async (input: CreateInput) => {
  return await prisma.$transaction(async (tx) => {
    const parent = await tx.parent.create({ data: input.parent });
    const child = await tx.child.create({
      data: { ...input.child, parentId: parent.id }
    });
    return { parent, child };
  });
};
```

## Input/Output 검증

- **Input 검증:** Zod 스키마 사용
- **프로시저 네이밍:** 의미 있는 동사 사용 (예: `createAssignment`, `getSubmissions`)

## 에러 처리

- 서비스 레이어에서 표준 JavaScript 에러 throw
- 설명적인 에러 메시지 사용
- tRPC가 자동으로 HTTP 응답으로 변환
- 서비스 레이어에서 TRPCError 불필요

## Prisma 모델 설계

- **모델 이름:** PascalCase, 의미 있는 이름
- **관계:** 명시적으로 정의
- **필드 타입:** 적절한 타입과 제약 조건 사용
- **트랜잭션:** 다단계 데이터베이스 작업에 항상 사용

## 네이밍 컨벤션

자세한 네이밍 규칙은 [naming-conventions.md](./naming-conventions.md)를 참조하세요.

- Service 파일: `{domain}.service.ts`
- DTO 파일: `types/dto/{domain}.ts`
- Service export: `{domain}Service`
- Input 타입: `{Domain}{Action}Input`
- Response 타입: `{Domain}{Action}Res`
- Zod 스키마: `{domain}{Action}InputSchema`

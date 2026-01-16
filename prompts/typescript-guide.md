# TypeScript 가이드

## 기본 규칙

### type vs interface
- **항상 `interface` 대신 `type`을 사용하세요**

```typescript
// ✅ Correct
type User = {
  id: string;
  name: string;
};

// ❌ Incorrect
interface User {
  id: string;
  name: string;
}
```

### 타입 정의 위치

#### 컴포넌트 Props 타입
- **해당 컴포넌트 파일 내에서 직접 정의**

```typescript
// Button.tsx
type ButtonProps = {
  label: string;
  onClick: () => void;
};

export const Button = ({ label, onClick }: ButtonProps) => {
  // ...
};
```

#### 공유 타입
- **별도 타입 파일에서 정의** (`types/` 디렉토리)

```typescript
// types/user.ts
export type User = {
  id: string;
  name: string;
  email: string;
};
```

### 타입 안전성

- **가능한 한 함수와 const에 대한 타입을 정의하세요**
- **`any` 사용 최소화**

```typescript
// ✅ Correct - 명시적 타입
const fetchUser = async (id: string): Promise<User> => {
  // ...
};

// ❌ Avoid - 암묵적 any
const fetchUser = async (id) => {
  // ...
};
```

## tRPC 타입 패턴

### Input 타입
- **Zod 스키마에서 `z.infer<>` 사용**

```typescript
// types/dto/user.ts
import { z } from 'zod';

export const userCreateInputSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1),
});

export type UserCreateInput = z.infer<typeof userCreateInputSchema>;
```

### Response 타입
- **`RouterOutputs` 사용 (단일 진실 소스)**

```typescript
import type { RouterOutputs } from '@/lib/trpc';

export type UserDetailRes = RouterOutputs['user']['getById'];
```

# State Management 가이드

상태 카테고리에 따라 적절한 상태 관리 방식을 선택합니다.

## 5가지 상태 카테고리

### 1. Component State - 컴포넌트 로컬 상태

**사용처:** Form inputs, toggles, local UI state

**도구:** `useState`, `useReducer`

```tsx
// Simple state
const [count, setCount] = useState(0);

// Complex state (multiple related fields)
const [state, dispatch] = useReducer(reducer, initialState);
```

---

### 2. Application State - 전역 UI 상태

**사용처:** Cross-cutting UI concerns (theme, modals, notifications, sidebar state)

**도구:** TBD (Context API / Zustand / Jotai)

**규칙:** 가능하면 상태를 로컬로 유지하고, 진정으로 공유될 때만 전역화하세요

```tsx
// Examples: theme, modals, notifications, sidebar state
// Technology: TBD (Context API / Zustand / Jotai)
```

---

### 3. Server Cache State - 원격 데이터

**사용처:** API data, database queries

**도구:** **React Query (via tRPC)**

**규칙:** 서버 데이터를 전역 상태 스토어에 저장하지 마세요

```tsx
// Using tRPC (built on React Query)
const { data, isLoading } = trpc.posts.getById.useQuery({ id });
```

---

### 4. Form State - 폼 검증 및 제출

**사용처:** 검증이 필요한 모든 폼

**도구:** **React Hook Form + Zod**

**패턴:** `_schemas/` 폴더에 스키마 정의, form 컴포넌트와 colocation

```tsx
// Using React Hook Form + Zod
const form = useForm<FormData>({
  resolver: zodResolver(schema),
});

<Input {...register("email")} />;
{errors.email && <span>{errors.email.message}</span>}
```

---

### 5. URL State - 브라우저 URL 파라미터

**사용처:** 공유/북마크 가능한 상태 (filters, pagination, tabs)

**도구:** Next.js App Router hooks

**상태:** 아직 활발히 사용되지 않지만, 필요 시 사용 가능

```tsx
// Next.js App Router
const searchParams = useSearchParams();
const pathname = usePathname();
```

---

## 결정 트리 (Decision Tree)

상태 유형을 결정할 때 다음 순서로 질문하세요:

1. **폼 데이터인가?** → React Hook Form + Zod
2. **서버에서 가져온 데이터인가?** → tRPC (React Query)
3. **전역 UI 상태인가?** → Application state (TBD)
4. **URL로 공유 가능한가?** → URL state
5. **그 외** → Component state (useState/useReducer)

---

## Custom Hook 추출

복잡한 로직은 Custom Hook으로 추출하세요.

### 추출 기준
- 3개 이상의 `useState`/`useEffect` 조합
- 기능별로 그룹화된 5개 이상의 이벤트 핸들러
- 여러 컴포넌트에서 재사용 가능한 로직

### Naming & Placement
- **이름:** `use{Feature}` (예: `useOcrUpload`)
- **파일명:** `use-{feature}.ts` (kebab-case)
- **위치:** Progressive Lifting 규칙 적용 (사용처에 가장 가까운 `_hooks/`부터 시작)

### 패턴

```tsx
// ❌ Bad - logic in component (150+ lines)
const Component = () => {
  const [state1] = useState();
  const [state2] = useState();
  // ... 5+ handlers
  return <UI />;
};

// ✅ Good - logic in hook
const useFeature = (params) => {
  // All state & logic here
  return { state, handlers };
};

const Component = () => {
  const { state, handlers } = useFeature(params);
  return <UI {...state} {...handlers} />;
};
```

### Hook 캡슐화 - CRITICAL

**절대 setState 함수를 직접 노출하지 마세요**

```tsx
// ❌ BAD - Exposing setState breaks encapsulation
const useEditor = () => {
  const [text, setText] = useState("");
  return { text, setText }; // Don't expose setState!
};

// Component has direct state control
<Textarea onChange={(e) => setText(e.target.value)} />;

// ✅ GOOD - Encapsulated event handlers
const useEditor = () => {
  const [text, setText] = useState("");
  const handleTextChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };
  return { text, handleTextChange }; // Expose handler, not setState
};

// Component uses controlled interface
<Textarea onChange={handleTextChange} />;
```

**Return 패턴:** `{ state, handlers }`로 명확히 그룹화하고, setState 함수는 절대 노출하지 마세요

---

## Component Cohesion

계산 로직을 사용처에 가깝게 유지하세요. 미리 계산된 결과보다 원시 데이터를 전달하세요.

```tsx
// ❌ Low cohesion - parent computes child's logic
const Page = () => {
  const scoreDistribution = scoreRanges.map(range => /* complex calc */);
  return <Card scoreDistribution={scoreDistribution} />;
};

// ✅ High cohesion - component owns its logic
const Card = ({ aiScores }) => {
  const scoreDistribution = SCORE_RANGES.map(range => /* calc here */);
  return <Chart data={scoreDistribution} />;
};
const Page = () => {
  const aiScores = [...];
  return <Card aiScores={aiScores} />;  // Just pass raw data
};
```

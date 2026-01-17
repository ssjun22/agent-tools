# React 패턴 가이드

## 컴포넌트 정의

### const 사용 규칙

```tsx
// ✅ Correct - Use const
const MyComponent = () => {
  return <div>Hello</div>;
};

// ❌ Incorrect - Don't use function
function MyComponent() {
  return <div>Hello</div>;
}
```

## 이벤트 핸들러

### 네이밍 규칙
- 접두사 "handle" 사용

```tsx
const MyComponent = () => {
  const handleClick = () => {
    console.log('Clicked');
  };

  const handleSubmit = () => {
    // Submit logic
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    // Key handling
  };

  return (
    <button onClick={handleClick}>
      Click me
    </button>
  );
};
```

## 스타일링 (Tailwind CSS)

### 규칙
- **항상 Tailwind 클래스를 사용하여 스타일링**
- **인라인 CSS나 `<style>` 태그 사용 금지**
- **조건부 클래스는 `cn` 또는 `clsx` 사용**

### 패턴

```tsx
import { cn } from '@/lib/utils';

// ✅ Correct - Use cn/clsx
const Button = ({ isActive }: { isActive: boolean }) => (
  <button className={cn("px-4 py-2", isActive && "bg-blue-500")}>
    Click
  </button>
);

// ❌ Incorrect - Don't use ternary directly
const Button = ({ isActive }: { isActive: boolean }) => (
  <button className={isActive ? "px-4 py-2 bg-blue-500" : "px-4 py-2"}>
    Click
  </button>
);
```

## 상수 배치

### 컴포넌트 외부 선언
- 렌더링마다 재생성 방지

```tsx
// ✅ Correct - Outside component (no recreation on render)
const SCORE_RANGES = ['0-10', '10-20', '20-30'] as const;

const Component = () => {
  const data = SCORE_RANGES.map((range) => {
    // Process range
  });

  return <div>{/* ... */}</div>;
};

// ❌ Incorrect - Inside component (recreated every render)
const Component = () => {
  const scoreRanges = ['0-10', '10-20', '20-30'];
  // This array is recreated on every render

  return <div>{/* ... */}</div>;
};
```

## 이미지 처리

- **Next.js Image 컴포넌트 사용**

```tsx
import Image from 'next/image';

const Avatar = ({ src, alt }: { src: string; alt: string }) => (
  <Image src={src} alt={alt} width={100} height={100} />
);
```

## 에러 처리 및 검증

- **클라이언트와 서버 양쪽에서 모든 사용자 입력을 검증**
- **try-catch 블록으로 에러를 우아하게 처리**
- **적절한 로딩 및 에러 상태를 구현**

```tsx
const Component = () => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const result = await fetch('/api/data');
        setData(result);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return <div>{/* Render data */}</div>;
};
```

## 접근성 (Accessibility)

- **인터랙티브 요소에 `tabIndex="0"` 사용**
- **키보드 접근성을 위해 `onClick`과 `onKeyDown` 모두 처리**

```tsx
const InteractiveCard = ({ onClick }: { onClick: () => void }) => {
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      onClick();
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={handleKeyDown}
    >
      {/* Content */}
    </div>
  );
};
```

## 환경 변수

- **민감한 데이터에는 환경 변수를 사용**

```typescript
// ✅ Correct
const apiKey = process.env.NEXT_PUBLIC_API_KEY;

// ❌ Incorrect - Never hardcode secrets
const apiKey = 'sk-12345...';
```
